""" Utility string procedures and classes.

@author Provotorov A. <merqcio11@gmail.com>
"""


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
