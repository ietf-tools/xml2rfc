def justify_inline(left_str, center_str, right_str, width=72):
    """ Takes three string arguments and outputs a single string with the
        arguments left-justified, centered, and right-justified respectively.

        Throws an exception if the combined length of the three strings is
        greater than the width.
    """

    if (len(left_str) + len(center_str) + len(right_str)) > width:
        raise Exception("The given strings are greater than a width of: "\
                                                            + str(width))
    else:
        center_str_pos = width / 2 - len(center_str) / 2
        str = left_str + ' ' * (center_str_pos - len(left_str)) \
            + center_str + ' ' * (center_str_pos - len(right_str)) \
            + right_str
        return str
