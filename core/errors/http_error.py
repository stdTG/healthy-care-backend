class HttpError(Exception):
    def __init__(self, message, code, details=None):
        if details is None:
            details = {}

        self.message = message
        self.code = code
        self.details = details
