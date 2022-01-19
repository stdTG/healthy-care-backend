import sys
from collections import deque, namedtuple

from .random import Random

__all__ = ["Transaction"]


class Transaction(object):
    """
    A context manager for recording and playing rollback.
    The first exception will be remembered and re-raised after rollback

    Sample usage:
    with Transaction() as rollback:
        rollback.push(lambda: undo step1)
        def undoStep2(arg): pass
        step2()
        rollback.push(undoStep2, someArg)

    When rollback exits, it runs the undo functions in reverse order.
    Firstly it runs undoStep2(), then the lambda to undo step1.

    More examples see tests/test_rollbackcontext.py .
    """

    class Undo(namedtuple('Undo', ['undo', 'autoCommit', 'args', 'kwargs'])):
        def setAutoCommit(self):
            self.autoCommit[0] = True

    def __init__(self, title: str = "Unnamed", *args):
        self._title = title
        self._finally = deque()
        self._lastUndo = None

        data = Random().get()
        self._id = data.uuid
        self._short_id = data.short_code

    def __enter__(self):
        print("[TRX-{short_id}] Starting transaction [{title}]...".format(title=self._title,
                                                                          short_id=self._short_id))
        print("[TRX-{short_id}] ID: [{id}]".format(id=self._id, short_id=self._short_id))
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        According to Python official doc. This function should only re-raise
        the exception from undo functions. Python automatically re-raises the
        original exception when this function does not return True.
        http://docs.python.org/2/library/stdtypes.html#contextmanager.__exit__
        """

        if exc_type:
            print(self.format(f"Transaction [{self._title}] failed."))
            print(self.format(f"Rollback started..."))

        undoExcInfo = None
        for func, autoCommit, args, kwargs in self._finally:
            if (exc_type is None) and autoCommit[0]:
                # The "with" statement exits without exception,
                # so skip the auto-committing undos.
                continue

            try:
                func(*args, **kwargs)
            except Exception as err:
                print(self.format(f"Rollback {func.__name__} failed."))
                print(err)
                # keep the earliest exception info
                if undoExcInfo is None:
                    undoExcInfo = sys.exc_info()

        if exc_type is None and undoExcInfo is not None:
            raise undoExcInfo[0](undoExcInfo[1], undoExcInfo[2])
        else:
            print(self.format(f"Transaction [{self._title}] complete"))

    def _push(self, func, toTop, args, kwargs):
        undo = self.Undo(func, [False], args, kwargs)
        if toTop:
            self._finally.appendleft(undo)
        else:
            self._finally.append(undo)
        return undo

    def push(self, func, *args, **kwargs):
        return self._push(func, True, args, kwargs)

    def pushBottom(self, func, *args, **kwargs):
        return self._push(func, False, args, kwargs)

    def commitAll(self):
        self._finally.clear()
        return self.format("All committed.")

    def format(self, message: str):
        return f"[TRX-{self._short_id}] {message}"
