"""Hash only explicitly selected regular files contained in a chosen root."""
from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath


def _file(root: Path, name: str) -> Path:
    if not isinstance(name, str) or "\\" in name:
        raise ValueError("manifest paths must be relative POSIX paths")
    relative = PurePosixPath(name)
    if relative.is_absolute() or ".." in relative.parts or relative.as_posix() != name or not relative.parts:
        raise ValueError("manifest paths must be normalized and relative")
    path = root
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("symlinks are not accepted")
    path.resolve().relative_to(root.resolve())
    if not path.is_file():
        raise ValueError("manifest entry is not a regular file")
    return path


def _digest(path: Path) -> dict:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        before = path.stat()
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
        after = path.stat()
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
        raise ValueError("file changed during hashing")
    return {"bytes": after.st_size, "sha256": digest.hexdigest()}


def create_manifest(root: Path, files: list[str]) -> dict:
    if not files or len(set(files)) != len(files):
        raise ValueError("select at least one file, without duplicates")
    return {"schema_version": 1, "algorithm": "sha256",
            "files": {name: _digest(_file(root, name)) for name in sorted(files)}}


def verify_manifest(root: Path, manifest: dict) -> dict:
    if (manifest.get("schema_version") != 1 or manifest.get("algorithm") != "sha256"
            or not isinstance(manifest.get("files"), dict) or not manifest["files"]):
        raise ValueError("invalid manifest schema")
    findings = []
    for name, expected in manifest["files"].items():
        if (not isinstance(expected, dict) or set(expected) != {"bytes", "sha256"}
                or type(expected["bytes"]) is not int or expected["bytes"] < 0
                or not isinstance(expected["sha256"], str) or len(expected["sha256"]) != 64
                or any(c not in "0123456789abcdef" for c in expected["sha256"])):
            raise ValueError("invalid manifest file record")
        path = _file(root, name)
        if _digest(path) != expected:
            findings.append({"file": name, "code": "CONTENT_CHANGED"})
    return {"status": "invalid" if findings else "ok", "files_checked": len(manifest["files"]), "findings": findings}
