
__all__ = ['file_linescount']


def file_linescount(filepath):
    with open(filepath) as f:
        for line_no, unused_line in enumerate(f):
            pass
    return line_no + 1
