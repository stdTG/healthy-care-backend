from core.logic import BaseUpdate
from .mapper import Mapper
from ..model_db import DbHost
from ..model_web import DbHost as WebDbHost


class Update(BaseUpdate):

    def __init__(self):
        super().__init__(DbHost, WebDbHost, Mapper())
