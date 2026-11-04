import importlib.util
import struct
import sys
from pathlib import Path

import pytest

PT_GNU_STACK = 0x6474E551
PF_X = 0x1


def needs_exec_stack(so_path: Path) -> bool:
    """True if a 64-bit little-endian ELF file asks for an executable stack."""
    with open(so_path, "rb") as f:
        header = f.read(64)
        assert header[:6] == b"\x7fELF\x02\x01", (
            f"{so_path} is not a 64-bit little-endian ELF"
        )
        phoff = struct.unpack_from("<Q", header, 0x20)[0]
        phentsize, phnum = struct.unpack_from("<HH", header, 0x36)
        f.seek(phoff)
        table = f.read(phentsize * phnum)
    for i in range(phnum):
        p_type, p_flags = struct.unpack_from("<II", table, i * phentsize)
        if p_type == PT_GNU_STACK:
            return bool(p_flags & PF_X)
    return True  # no PT_GNU_STACK header: the loader defaults to an executable stack


def test_onnxruntime_imports():
    # chromadb imports onnxruntime at import time, so the whole agent depends on this.
    import onnxruntime  # noqa: F401


# Newer glibc (e.g. ubuntu-26.04) refuses to load libraries that need an executable stack.
@pytest.mark.skipif(
    not sys.platform.startswith("linux"), reason="ELF check, Linux only"
)
def test_onnxruntime_native_lib_does_not_need_exec_stack():
    package_dir = Path(importlib.util.find_spec("onnxruntime").origin).parent
    libs = list((package_dir / "capi").glob("onnxruntime_pybind11_state*.so"))
    assert libs
    assert not [lib.name for lib in libs if needs_exec_stack(lib)]
