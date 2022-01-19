from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from web.core.results import CamelModel


class MetricData(CamelModel):
    date: datetime
    value: int


class Metric(CamelModel):
    name: str
    values: List[MetricData]


class Metrics(BaseModel):
    metrics: Optional[List[Metric]]
