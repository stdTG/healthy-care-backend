from core.logic import BaseRead
from .mapper import Mapper
from ..model_db import DbHost
from ..model_web import DbHost as WebDbHost


class Read(BaseRead):

    def __init__(self):
        super().__init__(DbHost, WebDbHost, Mapper())
