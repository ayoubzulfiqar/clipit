"""
clipping.marketplace — Template & Community Preset Pack Distribution

Provides packaging, validation, export, and import of portable '.clipit-pack'
distribution bundles containing custom presets, fonts, audio assets, and brand overlays.
"""

from __future__ import annotations

import json
import os
import shutil
import time
import zipfile
from typing import Any, Dict, List, Optional, Tuple


class MarketplacePackError(Exception):
    """Raised when pack validation, export, or extraction fails."""
    pass


def export_pack(
    pack_name: str,
    preset_data: Dict[str, Any],
    output_path: str,
    author: str = "Anonymous",
    description: str = "",
    version: str = "1.0.0",
    tags: Optional[List[str]] = None,
    asset_files: Optional[Dict[str, str]] = None,
) -> str:
    """
    Export a preset and associated asset files into a portable .clipit-pack (zip) archive.
    
    asset_files: dict mapping archive relative destination ('fonts/cool.ttf') to local path.
    """
    if not pack_name or not preset_data:
        raise MarketplacePackError("pack_name and preset_data are required for export.")

    manifest = {
        "manifest_version": "1.0",
        "pack_name": pack_name,
        "author": author,
        "description": description,
        "version": version,
        "tags": tags or [],
        "created_at": time.time(),
        "preset": preset_data,
        "assets": list((asset_files or {}).keys()),
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Write manifest
        zf.writestr("pack.json", json.dumps(manifest, indent=2, ensure_ascii=False))

        # Write asset files
        if asset_files:
            for arcname, local_path in asset_files.items():
                # Prevent path traversal in arcname
                clean_arcname = os.path.normpath(arcname).lstrip("/\\")
                if ".." in clean_arcname:
                    raise MarketplacePackError(f"Invalid asset archive path: {arcname}")
                if os.path.isfile(local_path):
                    zf.write(local_path, clean_arcname)

    return output_path


def inspect_pack(pack_path: str) -> Dict[str, Any]:
    """Inspect and return metadata from a .clipit-pack archive without extracting."""
    if not os.path.isfile(pack_path):
        raise MarketplacePackError(f"Pack file does not exist: {pack_path}")

    try:
        with zipfile.ZipFile(pack_path, "r") as zf:
            if "pack.json" not in zf.namelist():
                raise MarketplacePackError("Invalid pack: missing pack.json manifest.")
            content = zf.read("pack.json").decode("utf-8")
            data = json.loads(content)
            data["file_size_bytes"] = os.path.getsize(pack_path)
            data["files"] = zf.namelist()
            return data
    except (zipfile.BadZipFile, json.JSONDecodeError) as e:
        raise MarketplacePackError(f"Failed to read pack {pack_path}: {e}")


def import_pack(
    pack_path: str,
    install_dir: str,
    allowed_dirs: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Safely extract and install a .clipit-pack into the application install directory.
    Prevents directory traversal (Zip Slip vulnerability).
    
    Returns the loaded pack manifest.
    """
    manifest_data = inspect_pack(pack_path)
    os.makedirs(install_dir, exist_ok=True)
    real_install_dir = os.path.realpath(install_dir)

    with zipfile.ZipFile(pack_path, "r") as zf:
        for member in zf.infolist():
            if member.filename == "pack.json":
                continue
            # Security: ensure member does not escape install_dir
            target_path = os.path.realpath(os.path.join(real_install_dir, member.filename))
            if not target_path.startswith(real_install_dir + os.sep) and target_path != real_install_dir:
                raise MarketplacePackError(f"Malicious path detected in archive: {member.filename}")

            zf.extract(member, real_install_dir)

    # Save installed preset descriptor
    preset_dir = os.path.join(real_install_dir, "presets")
    os.makedirs(preset_dir, exist_ok=True)
    safe_name = "".join(c for c in manifest_data["pack_name"] if c.isalnum() or c in ("-", "_")).lower()
    preset_file = os.path.join(preset_dir, f"{safe_name}.json")
    with open(preset_file, "w", encoding="utf-8") as f:
        json.dump(manifest_data["preset"], f, indent=2, ensure_ascii=False)

    manifest_data["installed_preset_path"] = preset_file
    return manifest_data
