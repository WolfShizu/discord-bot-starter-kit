# TODO as features devem retornar para o dispatcher um payload com dados de telemetria customizados
# E o Telemetry deve ser capaz de tratar esses dados corretamente
# Os dados que serão recebidos devem ser registrados e configurados (se devem aparecer no terminal, se deve ser contado, etc)
# Também terá um aviso caso algum dado não esteja registrado

from dataclasses import dataclass, field
from datetime import datetime

from app.core.types import FeatureType
from app.core.dashboard import TerminalDashboard

@dataclass
class TelemetryFeaturePayload:
    feature_type: FeatureType
    feature_name: str
    execution_time: float
    success: bool
    user_id: int
    guild_id: int | None
    error_type: str | None = None # TODO Adicionar exceções personalizadas
    timestamp: datetime = field(default_factory= datetime.now)

@dataclass
class TelemetryBatchFeaturePayload:
    message_id: int
    user_id: int
    guild_id: int | None
    total_execution_time: float | None = None
    features_executed: list[TelemetryFeaturePayload] = field(default_factory= list)
    timestamp: datetime = field(default_factory= datetime.now)

@dataclass
class SystemStatistics:
    system_status: str
    connected_as: str
    bot_id: int
    cpu_usage: str
    ram_usage: str
    uptime: str
    guilds: int
    processed_messages: int
    messages_sent: int
    features_executed: int
    commands_executed: int
    listeners_executed: int

class Telemetry:
    def __init__(self, dashboard: TerminalDashboard):
        self.dashboard = dashboard
        self.total_data_recorded = 0

    async def record_batch(self, telemetry_data: TelemetryBatchFeaturePayload):
        self.total_data_recorded += 1
        data = {
            "message_id": telemetry_data.message_id,
            "total_execution_time": telemetry_data.total_execution_time,
            "features_executed": len(telemetry_data.features_executed),
            "timestamp": telemetry_data.timestamp
        }

        log_message = (
            f"Data N° {self.total_data_recorded}\n"
            f"Message ID: {data['message_id']}\n"
            f"Execution Time: {data['total_execution_time']:.4f}ms\n"
            f"Features: {data['features_executed']}"
        )

        self.dashboard.add_log(log_message)
