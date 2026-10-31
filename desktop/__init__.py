"""
desktop — Clipit Studio Desktop Application Packaging & Launcher
"""

from .launcher import launch_desktop, find_free_port, check_ffmpeg_available

__all__ = ["launch_desktop", "find_free_port", "check_ffmpeg_available"]
