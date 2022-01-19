from pydantic import BaseModel


class MobileProfilePhotoUploadResult(BaseModel):
    status: str
    url: str
