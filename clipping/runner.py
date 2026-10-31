"""
clipping.runner — Pipeline Orchestrator

Maps to Cell 4 (Execute) of the notebook.
Orchestrates the full clip generation pipeline.
"""

import json
import os

from . import diarization as diarization_mod
from . import engine, metadata, studio, hook_manager, voiceover
from .dedup import filter_duplicate_candidates
from .scene_detect import batch_snap_clips


def run_pipeline(cfg, whisper_model_instance=None) -> list[dict]:
    """
    Run the full clipping pipeline:
      1. Download YouTube video
      2. Transcribe with Whisper
      3. Analyse with Gemini AI
      4. Normalize metadata
      5. Prepare glitch transition
      6. Render each clip
      7. Save render_manifest.json

    Parameters
    ----------
    cfg : SimpleNamespace
        Configuration object from ``config.build_config()``.
    whisper_model_instance : WhisperModel or None
        Optional pre-loaded WhisperModel to reuse across batch runs.

    Returns
    -------
    list[dict]
        Render manifest (one dict per clip).
    """

    # Step 1 — Download
    source_platform = getattr(cfg, "source_platform", "youtube")
    resume_enabled = getattr(cfg, "resume", True)

    if resume_enabled and os.path.exists(cfg.file_video_asli) and os.path.getsize(cfg.file_video_asli) > 1024:
        print(f"🔄 [1/7] Source video ditemukan di disk ({cfg.file_video_asli}), melewati proses download.")
    else:
        engine.download_video(
            cfg.url_youtube,
            cfg.file_video_asli,
            getattr(cfg, "use_dlp_subs", False),
            getattr(cfg, "download_source_height", "max"),
            source_platform=source_platform,
            yt_cookies=getattr(cfg, "yt_cookies", None),
        )

    # Step 2 — Transcribe
    transkrip_lengkap = ""
    data_segmen = []
    transcription_cache_path = os.path.join(cfg.outputs_dir, "transcription_cache.json")

    # Checkpoint: load cached transcription if available
    if resume_enabled and os.path.exists(transcription_cache_path):
        try:
            with open(transcription_cache_path, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                transkrip_lengkap = cached_data.get("transkrip_lengkap", "")
                data_segmen = cached_data.get("data_segmen", [])
            if transkrip_lengkap and data_segmen:
                print(f"🔄 [2/7] Memuat transkripsi dari cache ({transcription_cache_path}), melewati proses Whisper.")
        except Exception as e:
            print(f"⚠️ Gagal membaca transcription_cache.json ({e}), melanjutkan transkripsi normal.")

    import glob

    # Mencari file json3 apapun (karena bahasanya bisa .id.json3 atau .en.json3)
    json3_files = glob.glob(cfg.file_video_asli.replace(".mp4", ".*.json3"))
    file_json3 = json3_files[0] if json3_files else None

    # Only run YouTube JSON3 subtitle search for YouTube sources
    if not transkrip_lengkap or not data_segmen:
        if source_platform == "youtube":
            if (
                getattr(cfg, "use_dlp_subs", False)
                and file_json3
                and os.path.exists(file_json3)
            ):
                transkrip_lengkap, data_segmen = engine.parse_youtube_json3_subs(
                    file_json3, max_words_per_subtitle=cfg.max_kata_per_subtitle
                )
                if transkrip_lengkap and data_segmen:
                    print(
                        f"✅ Berhasil memparsing subtitle dari YouTube ({os.path.basename(file_json3)}), melewati proses Whisper."
                    )

    if not transkrip_lengkap or not data_segmen:
        transkrip_lengkap, data_segmen = engine.transcribe_video(
            cfg.file_video_asli,
            max_words_per_subtitle=getattr(cfg, "max_kata_per_subtitle", 4),
            model_size=getattr(cfg, "whisper_model", "large-v3"),
            device=getattr(cfg, "whisper_device", "cuda"),
            compute_type=getattr(cfg, "whisper_compute_type", "float16"),
            whisper_model_instance=whisper_model_instance,
        )
        # Checkpoint: save transcription cache
        try:
            with open(transcription_cache_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"transkrip_lengkap": transkrip_lengkap, "data_segmen": data_segmen},
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception as e:
            print(f"⚠️ Gagal menyimpan transcription_cache.json: {e}")

    # Step 3 — Gemini AI analysis
    gemini_output_path = os.path.join(cfg.outputs_dir, "gemini_response.json")
    
    if (resume_enabled or getattr(cfg, "load_gemini_json", False)) and os.path.exists(gemini_output_path):
        print(f"\n🔄 [3/7] Memuat data AI ({cfg.ai_provider}) dari file lokal: {gemini_output_path}")
        with open(gemini_output_path, "r", encoding="utf-8") as f:
            hasil_json = json.load(f)
    else:
        hasil_json = engine.analyze_with_ai(transkrip_lengkap, cfg)
        
        # Save raw gemini json for future loading/reproduction
        with open(gemini_output_path, "w", encoding="utf-8") as f:
            json.dump(hasil_json, f, indent=4, ensure_ascii=False)
        print(f"💾 Raw AI response tersimpan di: {gemini_output_path}")

    # Deduplication pass (if enabled)
    if getattr(cfg, "dedup", False):
        iou_thresh = getattr(cfg, "dedup_iou_threshold", 0.6)
        text_thresh = getattr(cfg, "dedup_text_sim_threshold", 0.75)
        hasil_json = filter_duplicate_candidates(hasil_json, iou_threshold=iou_thresh, text_sim_threshold=text_thresh)

    # Natural camera scene-cut snapping pass (if enabled)
    if getattr(cfg, "snap_scene_cuts", False) and os.path.exists(cfg.file_video_asli):
        threshold = getattr(cfg, "scene_cut_detector_threshold", 0.35)
        max_dist = getattr(cfg, "scene_snap_distance", 1.0)
        hasil_json = batch_snap_clips(hasil_json, cfg.file_video_asli, threshold=threshold, max_distance=max_dist)

    # Step 4 — Metadata normalisation
    hasil_json = metadata.normalize_and_validate(hasil_json)
    metadata.print_preview(hasil_json)

    metadata_path = os.path.join(cfg.outputs_dir, "metadata_preview.json")
    metadata.save_metadata_preview(hasil_json, path=metadata_path)

    # Step 5 — Diarization (split-screen / camera-switch)
    diarization_data = None
    if (
        (getattr(cfg, "use_split_screen", False) and cfg.split_trigger == "diarization")
        or getattr(cfg, "use_camera_switch", False)
    ) and studio._is_vertical_ratio(cfg.pilihan_rasio):
        try:
            mode_label = (
                "Split-Screen"
                if getattr(cfg, "use_split_screen", False)
                else "Camera-Switch"
            )
            print(f"\n🎙️ [{mode_label}] Menjalankan speaker diarization...")
            audio_path = cfg.file_video_asli.replace(".mp4", "_audio.wav")
            diarization_mod.extract_audio(cfg.file_video_asli, audio_path)
            num_speakers_arg = getattr(cfg, "diarization_num_speakers", 2)
            min_spk = None
            max_spk = None

            if str(num_speakers_arg).lower() == "auto":
                max_faces = studio.estimate_speaker_count_from_video(
                    cfg.file_video_asli, cfg
                )
                num_speakers_arg = "auto"
                min_spk = max(1, max_faces)
                max_spk = min_spk + 2
                print(f"   ℹ️ Instruksi Pyannote: {min_spk} hingga {max_spk} speaker.")

            diarization_data = diarization_mod.run_diarization(
                audio_path,
                hf_token=cfg.hf_token,
                num_speakers=num_speakers_arg,
                min_speakers=min_spk,
                max_speakers=max_spk,
            )
            # Clean up temp audio
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception as e:
            print(f"⚠️ Diarization gagal: {e}")
            print("   Fallback ke mode render biasa (tanpa split-screen).")
            diarization_data = None

    # Step 6 — Video encoder & glitch
    os.environ["CLIPIT_VIDEO_SCALE_ALGO"] = str(
        getattr(cfg, "video_scale_algo", "lanczos")
    )
    
    # Get target dimensions for auto-bitrate calculation
    try:
        import cv2
        cap_e = cv2.VideoCapture(cfg.file_video_asli)
        src_h_e = int(cap_e.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1080)
        cap_e.release()
    except (ImportError, Exception):
        src_h_e = 1080
    
    target_w_e, target_h_e = studio._get_render_dims(cfg, cfg.pilihan_rasio, source_h=src_h_e)
    video_encoder = studio.detect_video_encoder(cfg, target_h=target_h_e)

    file_glitch_ts = None
    if cfg.use_hook_glitch:
        print("⚙️ Menyiapkan Video Glitch Transisi...")
        
        # Get source dimensions for proper glitch scaling
        try:
            import cv2
            cap_g = cv2.VideoCapture(cfg.file_video_asli)
            source_h_g = int(cap_g.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1080)
            cap_g.release()
        except (ImportError, Exception):
            source_h_g = 1080

        file_glitch_ts = studio.siapkan_glitch_video(
            cfg.pilihan_rasio, cfg, video_encoder, source_h=source_h_g
        )

    # Step 6 — Render each clip
    render_manifest: list[dict] = []

    custom_hook_path = None
    if getattr(cfg, "hook_source", None):
        print("\n🎣 Mengunduh sumber klip Hook kustom...")
        custom_hook_path = hook_manager.download_custom_hook(cfg)

    # Step 5.5 — Generate Voice-Over (if enabled)
    if getattr(cfg, "voiceover", False):
        print(f"\n🎙️ Meng-generate Voice-Over untuk {len(hasil_json)} klip...")
        for klip in hasil_json:
            try:
                # 1. Generate commentary script from snippet
                start = float(klip["start_time"])
                end = float(klip["end_time"])
                # Extract transcript snippet for this time range
                snippet_lines = []
                for seg in data_segmen:
                    if float(seg["end"]) > start and float(seg["start"]) < end:
                        # Support both Whisper format (has 'text') and YouTube JSON3 (only 'words')
                        seg_text = seg.get("text") or " ".join(w["word"] for w in seg.get("words", []))
                        if seg_text:
                            snippet_lines.append(seg_text)
                snippet_text = " ".join(snippet_lines)

                script = voiceover.generate_commentary_script(
                    snippet_text,
                    cfg,
                    style=cfg.voiceover_style,
                    language=cfg.voiceover_lang,
                    length=cfg.voiceover_length,
                )

                if script:
                    # 2. Synthesize TTS
                    audio_path, vo_segments = voiceover.synthesize_voice(
                        script,
                        cfg.voiceover_voice,
                        cfg.outputs_dir,
                        str(klip["rank"])
                    )
                    
                    if os.path.exists(audio_path):
                        klip["voiceover"] = {
                            "script": script,
                            "audio_path": audio_path,
                            "segments": vo_segments,
                            "voice": cfg.voiceover_voice
                        }

            except Exception as e:
                print(f"   ⚠️ Gagal generate voice-over untuk Rank {klip['rank']}: {e}")

    manifest_path = os.path.join(cfg.outputs_dir, "render_manifest.json")
    old_manifest_map = {}
    if resume_enabled and os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                for entry in json.load(f):
                    if isinstance(entry, dict) and "rank" in entry:
                        old_manifest_map[entry["rank"]] = entry
        except Exception:
            pass

    for klip in sorted(hasil_json, key=lambda x: x["rank"]):
        rank = klip["rank"]
        # Checkpoint: reuse existing clip if already rendered
        if resume_enabled and rank in old_manifest_map:
            cached_clip = old_manifest_map[rank]
            clip_file = cached_clip.get("output_file") or cached_clip.get("video_path")
            if clip_file and os.path.exists(clip_file) and os.path.getsize(clip_file) > 1024:
                print(f"🔄 [6/7] Klip Rank {rank} sudah ada di disk ({clip_file}), melewati render.")
                render_manifest.append(cached_clip)
                continue

        if custom_hook_path:
            klip["custom_hook_info"] = {"file_path": custom_hook_path}

        hasil_render = studio.proses_klip(
            klip["rank"],
            klip,
            cfg.pilihan_rasio,
            file_glitch_ts,
            data_segmen,
            cfg,
            video_encoder,
            diarization_data=diarization_data,
        )
        if hasil_render:
            render_manifest.append(hasil_render)

    # Step 7 — Inject source metadata for attribution & safety tracking
    for row in render_manifest:
        # Attach source URL so metadata.py can auto-add source credit
        if not row.get("source_url"):
            row["source_url"] = getattr(cfg, "url_youtube", None)

    # Step 8 — Save manifest
    manifest_path = os.path.join(cfg.outputs_dir, "render_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(render_manifest, f, ensure_ascii=False, indent=2)

    print(
        f"\n💾 Render manifest disimpan ke {manifest_path} ({len(render_manifest)} item)"
    )


    return render_manifest

