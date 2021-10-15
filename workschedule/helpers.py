from pathlib import Path


def get_top_directory() -> Path:
    tmp_path = Path(__file__).absolute().parent.parent
    if not (tmp_path / "workschedule/__init__.py").exists():
        raise ValueError(f"coud not find top directory, found {tmp_path}")
    return tmp_path
