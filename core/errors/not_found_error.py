from fastapi import HTTPException, status


class HTTPNotFoundError(HTTPException):
    def __init__(self, message: str = "Item not found"):
        super().__init__(status.HTTP_404_NOT_FOUND, message)


class HTTPNotAllowedError(HTTPException):
    def __init__(self, message: str = "You don't have permission"):
        super().__init__(status.HTTP_404_NOT_FOUND, message)
