# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

""" Module Singleton which handles output of warnings and errors to
    stdout/stderr, or alternatively to specified file paths.

    If warn_error is set, then any warnings submitted will raise a
    python exception.
"""

import sys
import parser

quiet = False
write_out = sys.stdout
write_err = sys.stderr


def write_on_line(*args):
    """ Writes a message without ending the line, i.e. in a loading bar """
    write_out.write(' '.join(args))
    write_out.flush()


def write(*args):
    """ Prints a message to write_out """
    write_out.write(' '.join(args))
    write_out.write('\n')


def warn(*args):
    """ Prints a warning message nuless quiet """
    if not quiet:
        write_err.write('WARNING: ' + ' '.join(args))
        write_err.write('\n')


def error(*args):
    """ This is typically called after an exception was already raised. """
    write_err.write('ERROR: ' + ' '.join(args))
    write_err.write('\n')
