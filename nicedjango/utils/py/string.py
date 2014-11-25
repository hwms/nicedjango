from nicedjango._compat import basestring

__all__ = ['divide_string']


def divide_string(s, char):
    """
    Divide string *s* by first occurence of *char* and return tuple of two strings
    or raise ValueErrors, when *s* is no string, empty or starts with *char*.
    """
    if not isinstance(s, basestring):
        raise ValueError('must be a string: %s' % s)
    if not s:
        raise ValueError('can\'t be empty')
    if s.startswith(char):
        raise ValueError('can\'t start with %s: %s' % (char, s))
    divided = s.split(char, 1)
    if len(divided) == 1:
        return s, ''
    return divided
