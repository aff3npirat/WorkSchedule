from pathlib import Path


def get_top_directory() -> Path:
    tmp_path = Path(__file__).absolute().parent.parent
    if not (tmp_path / "workschedule/__init__.py").exists():
        raise ValueError(f"coud not find top directory, found {tmp_path}")
    return tmp_path


def split_lines(string: str, line_length: int) -> str:
    """Places newlines so that no words are cut."""
    string = list(string)
    split_idx = line_length
    for idx, val in enumerate(string):
        if val == " ":
            split_idx = idx
        if idx - 1 == line_length - 1:
            if string[split_idx] == " ":
                string[split_idx] = "\n"
            else:
                string = string[:split_idx] + ["\n"] \
                         + string[split_idx:]
    return "".join(string)


def cutoff(string: str, line_length: int) -> str:
    if len(string) <= line_length:
        return string

    cut_idx = line_length - 4
    for idx, val in enumerate(string):
        if val == " ":
            cut_idx = idx
        if idx == line_length - 3:
            return string[:cut_idx] + "..."
