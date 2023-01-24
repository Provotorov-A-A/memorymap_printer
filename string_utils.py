""" Utility string procedures and classes.

@author Provotorov A. <merqcio11@gmail.com>
"""


import sys


def hex_digits(value):
    """Returns minimal number of hex digits that represent specified value.
    """
    ret = 1
    hex_base = 16
    border = 1
    while border <= 2 ** 64:
        border = border * hex_base
        if value < border:
            return ret
        ret += 1
    return ret


def max_strlen_in_list(str_list):
    """Finds string with a maximum length and returns that length.
    """
    ret = 0
    for item in str_list:
        ret = max(ret, len(item))
    return ret


def split_by_len(string: str, part_size):
    """Splits string to parts each of specified size.
    """
    if string:
        str_len = len(string)
        return [string[i:i + part_size] for i in range(0, str_len, part_size)]
    else:
        return []


def list_from_multiline(self, string: str, max_substring_len=sys.maxsize):
    """Splits string by newline and specified length, returns list with at least 'minimal_lines_count' number
    of substrings.
    """
    ret = []
    if string:
        substrings = string.split('\n')
    else:
        substrings = []
    for s in substrings:
        ret.extend(self.split_by_len(s, max_substring_len))
    return ret
