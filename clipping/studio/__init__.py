"""
clipping.studio — Video Rendering Engine Package

Exports the public Studio rendering API and utilities.
"""

from .helpers import (
    format_seconds,
    escape_ffmpeg_filter_value,
)
from .ffmpeg_utils import (
    detect_video_encoder,
    get_ts_encode_args,
    get_mp4_encode_args,
    open_ffmpeg_video_writer,
    build_ffmpeg_progress_cmd,
    run_ffmpeg_with_progress,
)
from .utils import (
    _get_render_dims,
    _is_vertical_ratio,
    _get_cv2_interpolation,
    _resize_frame,
    RATIO_MAP,
)
from .face_detection import (
    get_face_detector,
    estimate_speaker_count_from_video,
)
from .typography import (
    download_google_font,
    register_fonts_for_libass,
    siapkan_font_tipografi,
)
from .audio_bgm import (
    get_local_bgm_file,
    build_bgm_filter,
)
from .broll import (
    download_pexels_broll,
    crop_center_broll,
)
from .subtitles import (
    buat_file_ass,
)
from .effects import (
    siapkan_glitch_video,
)
from .transitions import (
    download_transition_raw,
    download_all_transitions,
    get_random_transition,
    prepare_transition_clip,
    TMP_TRANSITION_POOL,
)
from .thumbnail import (
    buat_thumbnail,
)
from .render_hybrid import (
    buat_video_hybrid,
)
from .render_split_screen import (
    buat_video_split_screen,
)
from .render_camera_switch import (
    buat_video_camera_switch,
)
from .core import (
    proses_klip,
)
from .watermark import (
    apply_watermark,
)

__all__ = [
    "format_seconds",
    "escape_ffmpeg_filter_value",
    "detect_video_encoder",
    "get_ts_encode_args",
    "get_mp4_encode_args",
    "open_ffmpeg_video_writer",
    "build_ffmpeg_progress_cmd",
    "run_ffmpeg_with_progress",
    "_get_render_dims",
    "_is_vertical_ratio",
    "_get_cv2_interpolation",
    "_resize_frame",
    "RATIO_MAP",
    "get_face_detector",
    "estimate_speaker_count_from_video",
    "download_google_font",
    "register_fonts_for_libass",
    "siapkan_font_tipografi",
    "get_local_bgm_file",
    "build_bgm_filter",
    "download_pexels_broll",
    "crop_center_broll",
    "buat_file_ass",
    "siapkan_glitch_video",
    "download_transition_raw",
    "download_all_transitions",
    "get_random_transition",
    "prepare_transition_clip",
    "TMP_TRANSITION_POOL",
    "buat_thumbnail",
    "buat_video_hybrid",
    "buat_video_split_screen",
    "buat_video_camera_switch",
    "proses_klip",
    "apply_watermark",
]
