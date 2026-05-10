#!/usr/bin/env python3
"""
Update .bundled_manifest with new/updated skill hashes.
Safely handles keys that may not exist in the manifest yet.

Usage:
    python3 update_manifest.py [--dry-run]

    Called via: sudo -u openclaw python3 /tmp/update_manifest.py
"""
import hashlib
import os
import re
import sys
from pathlib import Path

def hash_dir(path: Path) -> str:
    """Compute a git-style hash of a directory's contents."""
    h = hashlib.sha256()
    for root, dirs, files in os.walk(path):
        dirs.sort()
        for f in sorted(files):
            fp = os.path.join(root, f)
            h.update(fp.encode())
            with open(fp, 'rb') as file:
                h.update(file.read())
    return h.hexdigest()[:40]

def load_manifest(manifest_path: Path) -> dict:
    """Load manifest as dict from existing file."""
    manifest = {}
    if manifest_path.exists():
        content = manifest_path.read_text()
        for line in content.strip().split('\n'):
            line = line.strip()
            if ':' in line:
                key, val = line.split(':', 1)
                manifest[key.strip()] = val.strip()
    return manifest

def save_manifest(manifest_path: Path, manifest: dict):
    """Save manifest dict to file, sorted alphabetically."""
    lines = []
    for key in sorted(manifest.keys()):
        lines.append(f"{key}:{manifest[key]}")
    manifest_path.write_text('\n'.join(lines) + '\n')

def update_skills(skills_to_hash: list[str], manifest_path: Path, skills_base: Path, dry_run: bool = False):
    """
    Compute hashes for listed skills and update manifest.
    
    Args:
        skills_to_hash: List of skill directory names to hash and update
        manifest_path: Path to .bundled_manifest
        skills_base: Base path containing skill directories
        dry_run: If True, print what would change without modifying files
    """
    manifest = load_manifest(manifest_path)
    changes = []
    
    for skill in sorted(skills_to_hash):
        skill_path = skills_base / skill
        if not skill_path.is_dir():
            print(f"WARNING: {skill} is not a directory, skipping", file=sys.stderr)
            continue
        
        h = hash_dir(skill_path)
        old_hash = manifest.get(skill)
        if old_hash != h:
            changes.append((skill, old_hash, h))
            manifest[skill] = h
    
    if dry_run:
        print("DRY RUN - would make these changes:")
        for skill, old, new in changes:
            print(f"  {skill}: {old} -> {new}")
        print(f"\nTotal: {len(changes)} changes")
        return
    
    if changes:
        save_manifest(manifest_path, manifest)
        print(f"Updated {len(changes)} skills in manifest:")
        for skill, old, new in changes:
            print(f"  {skill}: {old} -> {new}")
    else:
        print("No changes needed - all hashes match")

if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    
    # Default paths - override via sys.path insertion when called as module
    skills_base = Path.home() / '.hermes' / 'skills'
    manifest_path = skills_base / '.bundled_manifest'
    
    # Skills to update (empty by default - populate when called)
    skills_to_hash = []
    
    if skills_to_hash:
        update_skills(skills_to_hash, manifest_path, skills_base, dry_run)
    else:
        print("Usage: update_manifest.py [--dry-run]")
        print(f"  skills_base: {skills_base}")
        print(f"  manifest: {manifest_path}")