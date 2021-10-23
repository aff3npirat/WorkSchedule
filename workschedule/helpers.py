from pathlib import Path


def get_top_directory() -> Path:
    tmp_path = Path(__file__).absolute().parent.parent
    if not (tmp_path / "workschedule/__init__.py").exists():
        raise ValueError(f"coud not find top directory, found {tmp_path}")
    return tmp_path


def split_lines(text: str, line_length: int) -> str:
    """Places newlines so that no words are cut."""
    text = list(text)
    split_idx = line_length
    for idx, val in enumerate(text):
        if val == " ":
            split_idx = idx
        if idx - 1 == line_length - 1:
            if text[split_idx] == " ":
                text[split_idx] = "\n"
            else:
                text = text[:split_idx] + ["\n"] \
                       + text[split_idx:]
    return "".join(text)


def cutoff(text: str, line_length: int) -> str:
    if len(text) <= line_length:
        return text

    cut_idx = line_length - 4
    for idx, val in enumerate(text):
        if val == " ":
            cut_idx = idx
        if idx == line_length - 3:
            return text[:cut_idx] + "..."
