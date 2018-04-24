"""
BackupPC Clone
"""


def sizeof_fmt(num, suffix='B'):
    """
    Returns the size in bytes in human readable format.

    :param int num: The number of bytes.
    :param str suffix: The suffix.

    :rtype: str
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0

    return "%.1f%s%s" % (num, 'Yi', suffix)
