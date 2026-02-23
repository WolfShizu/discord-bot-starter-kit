from dataclasses import dataclass, field
from datetime import datetime

from app.core.types import FeatureType

@dataclass
class TelemetryFeaturePayload:
    feature_type: FeatureType
    feature_name: str
    execution_time: float
    success: bool
    user_id: int
    guild_id: int | None
    error_type: str | None = None # TODO Adicionar exceções personalizadas
    timestamp: datetime = field(default_factory=datetime.now)
