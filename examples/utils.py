"""
Small utility functions.
"""


import traceback
# if we don't have log.py, don't crash
try:
#    from . import log
    import log
    log = log.Log('pyslipqt.log')
except AttributeError:
    # means log already set up
    pass
except ImportError as e:
    # if we don't have log.py, don't crash
    # fake all log(), log.debug(), ... calls
    def logit(*args, **kwargs):
        pass
    log = logit
    log.debug = logit
    log.info = logit
    log.warn = logit
    log.error = logit
    log.critical = logit


def str_trace(msg=None):
    """Get a traceback string.

    This is useful if we need at any point in code to find out how
    we got to that point.
    """

    result = []

    if msg:
        result.append(msg+'\n')

    result.extend(traceback.format_stack())

    return ''.join(result)


def log_trace(msg=None):
    """Log a traceback string."""

    log.debug(str_trace(msg))
