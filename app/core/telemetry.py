# TODO as features devem retornar para o dispatcher um payload com dados de telemetria customizados
# E o Telemetry deve ser capaz de tratar esses dados corretamente
# Os dados que serão recebidos devem ser registrados e configurados (se devem aparecer no terminal, se deve ser contado, etc)
# Também terá um aviso caso algum dado não esteja registrado
from types import TracebackType
from dataclasses import dataclass, field
from datetime import datetime

from app.core.types import FeatureType, ExceptionSeverity
from app.core.dashboard import TerminalDashboard

from app.models.message_payload import BotResponsePayload

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
class TelemetryExceptionPayload:
    severity: ExceptionSeverity
    name: str
    message: str
    discord_event: str
    arguments: tuple
    trimmed_traceback: str
    full_traceback: str

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
    total_exceptions: int

class Telemetry:
    def __init__(self, dashboard: TerminalDashboard, statistics: SystemStatistics):
        self.dashboard = dashboard
        self.statistics = statistics
        self.total_data_recorded = 0

    async def record_batch(self, telemetry_batch: TelemetryBatchFeaturePayload):
        self.total_data_recorded += 1

        message_id = telemetry_batch.message_id
        total_execution_time = telemetry_batch.total_execution_time
        features_executed = len(telemetry_batch.features_executed)

        execution_time_color = ""

        if total_execution_time:
            if total_execution_time < 100:
                execution_time_color = "green"
            elif total_execution_time < 500:
                execution_time_color = "yellow"
            else:
                execution_time_color = "red"

        log_message = [
            f"Data N° {self.total_data_recorded} | ",
            f"Message ID: {message_id} | ",
            (f"Execution Time: {total_execution_time:.2f}ms", execution_time_color),
            f" | Features: {features_executed}",
        ]

        for telemetry_data in telemetry_batch.features_executed:
            self.statistics.features_executed +=1
            match telemetry_data.feature_type:
                case FeatureType.COMMAND:
                    self.statistics.commands_executed += 1

                case FeatureType.LISTENER:
                    self.statistics.listeners_executed += 1

                case _:
                    # TODO Tratar corretamente o erro
                    ...

        self.dashboard.add_log(log_message)

    async def record_sent_message(self, response_payload: BotResponsePayload):
        self.statistics.messages_sent += 1

    async def record_exception(self, exception_payload: TelemetryExceptionPayload):
        self.statistics.total_exceptions += 1

        exception_log = [
            f"name: {exception_payload.name}",
            f"severity: {exception_payload.severity}",
            f"message: {exception_payload.message}",
            f"discord event: {exception_payload.discord_event}",
            f"arguments: {exception_payload.arguments}",
            f"trimmed traceback: {exception_payload.trimmed_traceback}"
        ]

        self.dashboard.add_exception(exception_log)

    def record_basic_exception(self, exception_message: str):
        self.statistics.total_exceptions += 1
        self.dashboard.add_exception([exception_message])
