from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import stat
import tempfile
import zipfile


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _safe_member(root: Path, name: str) -> Path:
    target = (root / name).resolve()
    if root not in target.parents and target != root:
        raise ValueError(f"unsafe capsule path: {name}")
    return target


def pack(case_dir, out):
    root = Path(case_dir).resolve()
    manifest = json.loads((root / "manifest.json").read_text())
    files = sorted(set(manifest.get("files", []) + ["manifest.json"]))
    hashes = {}
    for name in files:
        path = _safe_member(root, name)
        if not path.is_file():
            raise ValueError(f"missing capsule file: {name}")
        hashes[name] = sha(path)
    manifest["_hashes"] = hashes
    manifest.setdefault("_format", 1)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, sort_keys=True, indent=2))
        for name in files:
            if name != "manifest.json":
                archive.write(root / name, name)


def safe_extract(archive, dst):
    root = Path(dst).resolve()
    for member in archive.infolist():
        _safe_member(root, member.filename)
        mode = member.external_attr >> 16
        if stat.S_ISLNK(mode):
            raise ValueError(f"symlink entries are not allowed: {member.filename}")
    archive.extractall(root)


def verify(directory):
    root = Path(directory).resolve()
    manifest = json.loads((root / "manifest.json").read_text())
    bad = []
    for name, expected in manifest.get("_hashes", {}).items():
        if name == "manifest.json":
            continue
        path = _safe_member(root, name)
        if not path.exists() or sha(path) != expected:
            bad.append(name)
    return manifest, bad


def _pointer(data, pointer: str):
    if pointer == "":
        return data
    if not pointer.startswith("/"):
        raise KeyError("JSON pointer must start with /")
    value = data
    for raw in pointer[1:].split("/"):
        part = raw.replace("~1", "/").replace("~0", "~")
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def evaluate_assertion(data, assertion):
    pointer = assertion.get("path", "")
    try:
        actual = _pointer(data, pointer)
        exists = True
    except (KeyError, IndexError, TypeError, ValueError):
        actual = None
        exists = False
    if "exists" in assertion:
        passed = exists is bool(assertion["exists"])
        return {"assertion": assertion, "passed": passed, "actual": actual}
    if not exists:
        return {"assertion": assertion, "passed": False, "actual": None, "error": "path does not exist"}
    checks = []
    if "equals" in assertion:
        checks.append(actual == assertion["equals"])
    if "contains" in assertion:
        try:
            checks.append(assertion["contains"] in actual)
        except TypeError:
            checks.append(False)
    if "matches" in assertion:
        checks.append(isinstance(actual, str) and re.search(assertion["matches"], actual) is not None)
    if "gte" in assertion:
        checks.append(isinstance(actual, (int, float)) and actual >= assertion["gte"])
    if "lte" in assertion:
        checks.append(isinstance(actual, (int, float)) and actual <= assertion["lte"])
    if "length" in assertion:
        try:
            checks.append(len(actual) == assertion["length"])
        except TypeError:
            checks.append(False)
    if not checks:
        return {"assertion": assertion, "passed": False, "actual": actual, "error": "no supported assertion operator"}
    return {"assertion": assertion, "passed": all(checks), "actual": actual}


def run(capsule):
    with tempfile.TemporaryDirectory() as directory:
        with zipfile.ZipFile(capsule) as archive:
            safe_extract(archive, directory)
        manifest, bad = verify(directory)
        if bad:
            return {"passed": False, "hash_failures": bad, "assertions": []}
        data = json.loads((Path(directory) / manifest["actual"]).read_text())
        results = [evaluate_assertion(data, assertion) for assertion in manifest.get("assertions", [])]
        return {"passed": all(item["passed"] for item in results), "hash_failures": [], "assertions": results}
