import hashlib
import sys
import uuid
from collections import deque, namedtuple


class TransactionAsync(object):
    class Undo(namedtuple('Undo', ['undo', 'autoCommit', 'args', 'kwargs'])):
        def setAutoCommit(self):
            self.autoCommit[0] = True

    def __init__(self, title: str = "Unnamed", *args):
        self._title = title
        self._finally = deque()
        self._lastUndo = None

        self._id = uuid.uuid1()
        hasher = hashlib.sha1(self._id.bytes)
        self._short_id = hasher.hexdigest()[:9]

    async def __aenter__(self):
        print("[TRX-{short_id}] Starting transaction [{title}]...".format(title=self._title,
                                                                          short_id=self._short_id))
        print("[TRX-{short_id}] ID: [{id}]".format(id=self._id, short_id=self._short_id))
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):

        if exc_type:
            print("[TRX-{short_id}] Transaction [{title}] failed.".format(title=self._title,
                                                                          short_id=self._short_id))
            print("[TRX-{short_id}] Rollback started...".format(short_id=self._short_id))

        undoExcInfo = None
        for func, autoCommit, args, kwargs in self._finally:
            if (exc_type is None) and autoCommit[0]:
                # The "with" statement exits without exception,
                # so skip the auto-committing undos.
                continue

            try:
                await func(*args, **kwargs)
            except Exception:
                # keep the earliest exception info
                if undoExcInfo is None:
                    undoExcInfo = sys.exc_info()

        if exc_type is None and undoExcInfo is not None:
            raise undoExcInfo[0](undoExcInfo[1], undoExcInfo[2])
        else:
            print("[TRX-{short_id}] Transaction [{title}] complete.".format(title=self._title,
                                                                            short_id=self._short_id))

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
        return "[TRX-{short_id}] All committed.".format(short_id=self._short_id)

    def format(self, message: str):
        return "[TRX-{short_id}] {message}".format(message=message, short_id=self._short_id)
