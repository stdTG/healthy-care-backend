from core.logic import BaseDelete
from .mapper import Mapper
from ..model_db import DbHost
from ..model_web import DbHost as WebDbHost


class Delete(BaseDelete):

    def __init__(self):
        super().__init__(DbHost, WebDbHost, Mapper())
