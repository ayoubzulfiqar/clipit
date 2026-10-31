import json
import math
import os
import string

from . import utils
from . import typography
from . import helpers as _helpers
from . import ffmpeg_utils as _ffmpeg_utils

FIREFOX_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0"

format_seconds = _helpers.format_seconds
escape_ffmpeg_filter_value = _helpers.escape_ffmpeg_filter_value
detect_video_encoder = _ffmpeg_utils.detect_video_encoder
get_ts_encode_args = _ffmpeg_utils.get_ts_encode_args
get_mp4_encode_args = _ffmpeg_utils.get_mp4_encode_args
open_ffmpeg_video_writer = _ffmpeg_utils.open_ffmpeg_video_writer
build_ffmpeg_progress_cmd = _ffmpeg_utils.build_ffmpeg_progress_cmd
run_ffmpeg_with_progress = _ffmpeg_utils.run_ffmpeg_with_progress

_resize_frame = utils._resize_frame
_get_cv2_interpolation = utils._get_cv2_interpolation
_get_render_dims = utils._get_render_dims
_is_vertical_ratio = utils._is_vertical_ratio

download_google_font = typography.download_google_font
register_fonts_for_libass = typography.register_fonts_for_libass
siapkan_font_tipografi = typography.siapkan_font_tipografi

from clipping.emoji_engine import get_palette_color, lookup_semantic_emoji

def buat_file_ass(
    data_segmen,
    start_clip,
    end_clip,
    nama_file_ass,
    rasio,
    cfg,
    typography_plan=None,
    gunakan_advanced=True,
    get_x_func=None,
    source_dim=None,
):
    """
    Build and write an Advanced SubStation Alpha (ASS) subtitle file for a video clip.

    Args:
        data_segmen (list): A list of dictionaries containing transcript segments and their timing.
        start_clip (float): The starting timestamp of the clip in the original video (in seconds).
        end_clip (float): The ending timestamp of the clip in the original video (in seconds).
        nama_file_ass (str): The destination file path to save the generated ASS file.
        rasio (str): The target aspect ratio ('9:16' or '16:9').
        cfg: Runtime configuration object specifying styling, fonts, and render settings.
        typography_plan (list, optional): A list of dictionaries specifying emphasis and animation for specific words. Defaults to None.
        gunakan_advanced (bool, optional): Whether to use advanced positioning and animations. Defaults to True.
        get_x_func (callable, optional): A function taking a timestamp and returning the X-coordinate for dynamic tracking.
        source_dim (tuple, optional): Source video dimension tuple `(width, height)`.

    Returns:
        None

    Side Effects:
        Writes formatting and subtitle event data to the local file specified by `nama_file_ass`.

    Raises:
        FileNotFoundError: If advanced mode is used and the configured font files are missing from the font directory.
    """
    if typography_plan is None:
        typography_plan = []

    typo_dict = {}
    for plan in typography_plan:
        clean_word = plan.get("kata_utama", "").lower().strip(string.punctuation)
        typo_dict[clean_word] = plan

    pakai_advanced = cfg.use_advanced_text and gunakan_advanced
    pakai_karaoke = cfg.use_karaoke_effect

    outline_val = 3 if pakai_karaoke else 0.2
    shadow_val = 2.5 if pakai_karaoke else 0.2

    daftar_font = cfg.daftar_font
    gaya = cfg.gaya_font_aktif
    font_dir = cfg.font_dir

    font_utama_dict = daftar_font[gaya]["utama"]
    font_khusus_dict = daftar_font[gaya]["khusus"]

    font_utama = font_utama_dict["nama"]
    font_khusus = font_khusus_dict["nama"]

    enable_emojis = getattr(cfg, "semantic_emojis", False)
    palette_name = getattr(cfg, "keyword_palette", "modern")

    scale_base_khusus = (
        cfg.scale_kata_khusus_916 if _is_vertical_ratio(rasio) else cfg.scale_kata_khusus_169
    )
    warna_khusus = cfg.warna_kata_khusus

    def get_scale_value(level):
        if level == 3:
            return scale_base_khusus
        elif level == 2:
            return int((scale_base_khusus + 100) / 2)
        else:
            return 110

    def fmt_time(d):
        return f"{int(d // 3600)}:{int((d % 3600) // 60):02d}:{int(d % 60):02d}.{int((d - int(d)) * 100):02d}"

    play_res_x, play_res_y = _get_render_dims(cfg, rasio, source_h=source_dim[1] if source_dim else 1080)
    
    # Calculate scale relative to standard 1080p vertical (1920 height)
    # This ensures typography looks consistent across different render resolutions
    scale_factor = play_res_y / (1920 if _is_vertical_ratio(rasio) else 1080)
    if rasio == "split":
        align = 5
        margin_v = 0
    else:
        align = cfg.ass_align_916 if _is_vertical_ratio(rasio) else cfg.ass_align_169
        margin_v = int((cfg.ass_margin_916 if _is_vertical_ratio(rasio) else cfg.ass_margin_169) * scale_factor)
    font_sz = int((cfg.ass_font_916 if _is_vertical_ratio(rasio) else cfg.ass_font_169) * scale_factor)
    margin_lr = int((60 if _is_vertical_ratio(rasio) else 40) * scale_factor)

    header = (
        f"[Script Info]\n"
        f"PlayResX: {play_res_x}\n"
        f"PlayResY: {play_res_y}\n"
        f"WrapStyle: 1\n"
        f"ScriptType: v4.00+\n"
        f"ScaledBorderAndShadow: yes\n\n"
        f"[V4+ Styles]\n"
        f"Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{font_utama},{font_sz},&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,{outline_val},{shadow_val},{align},{margin_lr},{margin_lr},{margin_v},1\n\n"
        f"[Events]\n"
        f"Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )

    def cek_font_di_folder(nama_file, min_valid_size=1000):
        path = os.path.join(font_dir, nama_file)
        return os.path.exists(path) and os.path.getsize(path) > min_valid_size

    if not pakai_advanced:
        with open(nama_file_ass, "w", encoding="utf-8") as f:
            f.write(header)
            for seg in data_segmen:
                seg_s = max(0, seg["start"] - start_clip)
                seg_e = min(end_clip - start_clip, seg["end"] - start_clip)
                if seg_s >= seg_e:
                    continue

                for i, w in enumerate(seg["words"]):
                    w_s = max(0, w["start"] - start_clip)
                    if i < len(seg["words"]) - 1:
                        w_e = min(
                            end_clip - start_clip,
                            seg["words"][i + 1]["start"] - start_clip,
                        )
                    else:
                        w_e = min(end_clip - start_clip, w["end"] - start_clip)

                    if w_s < w_e:
                        text_parts = []
                        for j, x in enumerate(seg["words"]):
                            if pakai_karaoke:
                                if j == i:
                                    text_parts.append(
                                        f"{{\\c&H00FFFF&}}{x['word']}{{\\c&HFFFFFF&}}"
                                    )
                                else:
                                    text_parts.append(x["word"])
                            else:
                                if j <= i:
                                    text_parts.append(x["word"])
                                else:
                                    text_parts.append(
                                        f"{{\\alpha&HFF&}}{x['word']}{{\\alpha&H00&}}"
                                    )

                        f.write(
                            f"Dialogue: 0,{fmt_time(w_s)},{fmt_time(w_e)},Default,,0,0,0,,{' '.join(text_parts)}\n"
                        )
        return

    # Advanced typography mode
    font_cache = {}

    def get_cached_font(is_khusus, scale_val):
        key = f"{is_khusus}_{scale_val}"
        if key not in font_cache:
            f_info = font_khusus_dict if is_khusus else font_utama_dict
            f_file = f_info["file"]
            f_path = os.path.join(font_dir, f_file)

            if not cek_font_di_folder(f_file):
                raise FileNotFoundError(f"Font tidak ditemukan: {f_path}")

            font_cache[key] = ImageFont.truetype(
                f_path,
                int(font_sz * (scale_val / 100.0)),
            )
        return font_cache[key]

    def build_font_tag(font_info):
        nama = str(font_info["nama"]).replace("{", "").replace("}", "").strip()
        bold = 1 if int(font_info.get("bold", 0)) else 0
        return f"\\fn{nama}\\b{bold}"

    max_line_width = play_res_x - (margin_lr * 2)
    space_width = font_sz * 0.25
    TIGHTNESS = 0.95

    with open(nama_file_ass, "w", encoding="utf-8") as f:
        f.write(header)

        for seg in data_segmen:
            seg_s = max(0, seg["start"] - start_clip)
            seg_e = min(end_clip - start_clip, seg["end"] - start_clip)
            if seg_s >= seg_e:
                continue

            lines = []
            current_line = []
            current_w = 0
            max_line_h = 0

            for w_dict in seg["words"]:
                word_clean = w_dict["word"].lower().strip(string.punctuation)
                plan = typo_dict.get(word_clean)

                display_word = w_dict["word"]
                if enable_emojis:
                    em = lookup_semantic_emoji(word_clean)
                    if em:
                        display_word = f"{display_word} {em}"

                if plan:
                    w_style = plan.get("style", "khusus")
                    w_scale = get_scale_value(plan.get("scale_level", 2))
                    is_khusus = w_style == "khusus"

                    pil_font = get_cached_font(is_khusus, w_scale)
                    raw_w = (
                        pil_font.getlength(display_word)
                        if hasattr(pil_font, "getlength")
                        else len(display_word) * 20
                    )
                    w_len = raw_w * TIGHTNESS
                    h_len = font_sz * (w_scale / 100.0)
                else:
                    w_scale = 100
                    pil_font = get_cached_font(False, w_scale)
                    raw_w = (
                        pil_font.getlength(display_word)
                        if hasattr(pil_font, "getlength")
                        else len(display_word) * 15
                    )
                    w_len = raw_w * TIGHTNESS
                    h_len = font_sz

                if current_line and (current_w + space_width + w_len > max_line_width):
                    lines.append(
                        {
                            "words": current_line,
                            "width": current_w,
                            "height": max_line_h,
                        }
                    )
                    current_line = []
                    current_w = 0
                    max_line_h = 0

                x_offset = current_w if not current_line else current_w + space_width
                current_line.append(
                    {
                        "text": display_word,
                        "word_clean": word_clean,
                        "plan": plan,
                        "w": w_len,
                        "h": h_len,
                        "x_offset": x_offset,
                        "start": max(0, w_dict["start"] - start_clip),
                        "end": min(end_clip - start_clip, w_dict["end"] - start_clip),
                    }
                )

                current_w = x_offset + w_len
                max_line_h = max(max_line_h, h_len)

            if current_line:
                lines.append(
                    {"words": current_line, "width": current_w, "height": max_line_h}
                )

            line_spacing = 15
            total_stack_h = (
                sum(l["height"] for l in lines) + (len(lines) - 1) * line_spacing
            )
            if rasio == "split":
                current_y = (play_res_y - total_stack_h) / 2
            else:
                current_y = play_res_y - margin_v - total_stack_h

            for line in lines:
                start_x = (play_res_x - line["width"]) / 2
                
                if get_x_func and cfg.dev_mode and source_dim:
                    sw, sh = source_dim
                    # Reference time: midpoint of the current segment/line
                    t_ref = line["words"][0]["start"] + start_clip
                    center_x_src = get_x_func(t_ref)
                    # Target center in PlayResX (1920)
                    target_center_x = center_x_src * (play_res_x / sw)
                    start_x = target_center_x - (line["width"] / 2)

                line_y = current_y + line["height"]

                for w_data in line["words"]:
                    word_x = start_x + w_data["x_offset"] + (w_data["w"] / 2)
                    w_appear_ms = int((w_data["start"] - seg_s) * 1000)
                    w_end_ms = int((w_data["end"] - seg_s) * 1000)

                    w_clean = w_data.get("word_clean", "")
                    highlight_color = get_palette_color(palette_name, w_clean)

                    if w_data["plan"]:
                        w_style = w_data["plan"].get("style", "khusus")
                        w_anim = w_data["plan"].get("animasi", "bounce_pop")
                        target_scale = get_scale_value(
                            w_data["plan"].get("scale_level", 2)
                        )
                        font_info = (
                            font_khusus_dict if w_style == "khusus" else font_utama_dict
                        )
                        f_tag = build_font_tag(font_info)
                        c_tag = f"\\c{highlight_color}" if palette_name != "modern" or w_clean else f"\\c{warna_khusus}"
                    else:
                        w_anim = "none"
                        target_scale = 100
                        f_tag = build_font_tag(font_utama_dict)
                        c_tag = "\\c&HFFFFFF&"

                    t_start = w_appear_ms
                    t_pop = w_appear_ms + 80
                    t_settle = w_appear_ms + 150

                    if pakai_karaoke:
                        pos_tag = f"\\pos({int(word_x)},{int(line_y)})"
                        c_tag = "\\c&HFFFFFF&"
                        anim_tag = f"\\fscx{target_scale}\\fscy{target_scale}\\t({t_start},{t_start},\\c{highlight_color})\\t({w_end_ms},{w_end_ms},\\c&HFFFFFF&)"
                    else:
                        if w_anim == "stagger_up":
                            y_start = int(line_y + 30)
                            pos_tag = f"\\move({int(word_x)},{y_start},{int(word_x)},{int(line_y)},{t_start},{t_settle})"
                            anim_tag = f"\\alpha&HFF&\\fscx{target_scale}\\fscy{target_scale}\\t({t_start},{t_start},\\alpha&H00&)"
                        elif w_anim == "bounce_pop":
                            init_scale = int(target_scale * 0.7)
                            overshoot = int(target_scale * 1.15)
                            pos_tag = f"\\pos({int(word_x)},{int(line_y)})"
                            anim_tag = (
                                f"\\alpha&HFF&\\fscx{init_scale}\\fscy{init_scale}"
                                f"\\t({t_start},{t_start},\\alpha&H00&)"
                                f"\\t({t_start},{t_pop},\\fscx{overshoot}\\fscy{overshoot})"
                                f"\\t({t_pop},{t_settle},\\fscx{target_scale}\\fscy{target_scale})"
                            )
                        else:
                            pos_tag = f"\\pos({int(word_x)},{int(line_y)})"
                            anim_tag = f"\\alpha&HFF&\\fscx{target_scale}\\fscy{target_scale}\\t({t_start},{t_start},\\alpha&H00&)"

                    event_text = (
                        f"{{\\an2{pos_tag}{f_tag}{c_tag}{anim_tag}}}{w_data['text']}"
                    )
                    f.write(
                        f"Dialogue: 0,{fmt_time(seg_s)},{fmt_time(seg_e)},Default,,0,0,0,,{event_text}\n"
                    )

                current_y += line["height"] + line_spacing


# ==============================================================================
# SIDECAR SUBTITLES (SRT & WebVTT) & MULTI-LANGUAGE TRANSLATION
# ==============================================================================

def format_srt_timestamp(seconds: float) -> str:
    """Format floating seconds into standard SRT timestamp HH:MM:SS,mmm."""
    secs = max(0.0, float(seconds))
    hrs = int(secs // 3600)
    mins = int((secs % 3600) // 60)
    s = int(secs % 60)
    ms = int(round((secs - int(secs)) * 1000))
    if ms >= 1000:
        s += 1
        ms -= 1000
    return f"{hrs:02d}:{mins:02d}:{s:02d},{ms:03d}"


def format_vtt_timestamp(seconds: float) -> str:
    """Format floating seconds into standard WebVTT timestamp HH:MM:SS.mmm."""
    secs = max(0.0, float(seconds))
    hrs = int(secs // 3600)
    mins = int((secs % 3600) // 60)
    s = int(secs % 60)
    ms = int(round((secs - int(secs)) * 1000))
    if ms >= 1000:
        s += 1
        ms -= 1000
    return f"{hrs:02d}:{mins:02d}:{s:02d}.{ms:03d}"


def build_clip_cues(data_segmen: list[dict], clip_start: float, clip_end: float) -> list[dict]:
    """
    Extract and re-timestamp subtitle segments relative to clip start (t=0.0).
    """
    cues = []
    for seg in data_segmen:
        s_start = float(seg.get("start", 0.0))
        s_end = float(seg.get("end", 0.0))
        text = str(seg.get("text", "")).strip()

        if s_end <= clip_start or s_start >= clip_end or not text:
            continue

        rel_start = max(0.0, s_start - clip_start)
        rel_end = max(0.0, min(clip_end, s_end) - clip_start)

        if rel_end > rel_start:
            cues.append({
                "start": round(rel_start, 3),
                "end": round(rel_end, 3),
                "text": text,
            })
    return cues


def generate_srt(cues: list[dict]) -> str:
    """Render list of cues as standard SubRip (.srt) text."""
    lines = []
    for idx, cue in enumerate(cues, start=1):
        lines.append(str(idx))
        lines.append(f"{format_srt_timestamp(cue['start'])} --> {format_srt_timestamp(cue['end'])}")
        lines.append(cue["text"])
        lines.append("")
    return "\n".join(lines)


def generate_vtt(cues: list[dict]) -> str:
    """Render list of cues as standard WebVTT (.vtt) text."""
    lines = ["WEBVTT", ""]
    for idx, cue in enumerate(cues, start=1):
        lines.append(str(idx))
        lines.append(f"{format_vtt_timestamp(cue['start'])} --> {format_vtt_timestamp(cue['end'])}")
        lines.append(cue["text"])
        lines.append("")
    return "\n".join(lines)


def translate_subtitle_cues(cues: list[dict], target_lang: str, ai_provider=None) -> list[dict]:
    """
    Translate cue texts into target_lang while strictly preserving timing intervals.
    """
    if not cues or not target_lang:
        return cues

    if ai_provider is not None:
        try:
            texts = [c["text"] for c in cues]
            prompt = (
                f"You are a professional subtitle translator. Translate the following subtitle lines into natural {target_lang}. "
                "Keep translations concise and punchy for video subtitles. "
                "Output ONLY a valid JSON array of strings corresponding 1:1 with each item in the input array:\n"
                + json.dumps(texts, ensure_ascii=False)
            )
            if hasattr(ai_provider, "generate_text"):
                resp = ai_provider.generate_text(prompt)
            elif hasattr(ai_provider, "complete"):
                resp = ai_provider.complete(prompt)
            else:
                resp = None

            if resp:
                clean_json = resp.strip()
                if clean_json.startswith("```"):
                    clean_json = clean_json.split("\n", 1)[1].rsplit("\n```", 1)[0].strip()
                translated = json.loads(clean_json)
                if isinstance(translated, list) and len(translated) == len(cues):
                    new_cues = []
                    for c, trans_t in zip(cues, translated):
                        nc = dict(c)
                        nc["text"] = str(trans_t).strip()
                        new_cues.append(nc)
                    return new_cues
        except Exception:
            pass

    return cues


def export_sidecar_subtitles(
    data_segmen: list[dict],
    clip_start: float,
    clip_end: float,
    base_video_path: str,
    formats: tuple[str, ...] | list[str] = ("srt", "vtt"),
    languages: list[str] | None = None,
    ai_provider=None,
) -> dict[str, str]:
    """
    Generate and save sidecar subtitle files (.srt and/or .vtt) alongside rendered video.

    Returns:
        Dict mapping format tags to written absolute file paths.
    """
    if not formats or "none" in formats:
        return {}

    cues = build_clip_cues(data_segmen, clip_start, clip_end)
    if not cues:
        return {}

    base_no_ext = os.path.splitext(base_video_path)[0]
    out_files: dict[str, str] = {}

    want_all = "all" in formats
    want_srt = want_all or "srt" in formats
    want_vtt = want_all or "vtt" in formats

    # 1. Primary video subtitle
    if want_srt:
        srt_path = f"{base_no_ext}.srt"
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(generate_srt(cues))
        out_files["srt"] = srt_path

    if want_vtt:
        vtt_path = f"{base_no_ext}.vtt"
        with open(vtt_path, "w", encoding="utf-8") as f:
            f.write(generate_vtt(cues))
        out_files["vtt"] = vtt_path

    # 2. Translated subtitle sidecars
    if languages:
        for lang in languages:
            lang = lang.strip().lower()
            if not lang:
                continue
            translated_cues = translate_subtitle_cues(cues, target_lang=lang, ai_provider=ai_provider)
            if want_srt:
                trans_srt_path = f"{base_no_ext}_{lang}.srt"
                with open(trans_srt_path, "w", encoding="utf-8") as f:
                    f.write(generate_srt(translated_cues))
                out_files[f"srt_{lang}"] = trans_srt_path
            if want_vtt:
                trans_vtt_path = f"{base_no_ext}_{lang}.vtt"
                with open(trans_vtt_path, "w", encoding="utf-8") as f:
                    f.write(generate_vtt(translated_cues))
                out_files[f"vtt_{lang}"] = trans_vtt_path

    return out_files


