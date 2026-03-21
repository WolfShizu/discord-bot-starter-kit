# TODO as features devem retornar para o dispatcher um payload com dados de telemetria customizados
# E o Telemetry deve ser capaz de tratar esses dados corretamente
# Os dados que serão recebidos devem ser registrados e configurados (se devem aparecer no terminal, se deve ser contado, etc)
# Também terá um aviso caso algum dado não esteja registrado
from typing import Any
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
class FeatureStatistics:
    """Guarda informações sobre execução das features. Usado para criar os top 5 e outras métricas"""
    feature_name: str
    execution_count: int = 0
    average_execution_time: float = 0
    slowest_execution_time: float = 0
    last_executed: datetime = field(default_factory= datetime.now)

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

    # Mapeamento de Features
    commands_statistics_map: dict[str, FeatureStatistics] = field(default_factory= dict)
    listener_statistics_map: dict[str, FeatureStatistics] = field(default_factory= dict)

class Telemetry:
    def __init__(self, dashboard: TerminalDashboard, statistics: SystemStatistics) -> None:
        self.dashboard = dashboard
        self.statistics = statistics
        self.total_data_recorded = 0

        # Mapeamento de Features
        self.commands_map: dict[str, FeatureStatistics] = {}
        self.listeners_map: dict[str, FeatureStatistics] = {}

    async def record_batch(self, telemetry_batch: TelemetryBatchFeaturePayload) -> None:
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

            target_map = None
            match telemetry_data.feature_type:
                case FeatureType.COMMAND:
                    target_map = self.statistics.commands_statistics_map

                case FeatureType.LISTENER:
                    target_map = self.statistics.listener_statistics_map

                case _:
                    # TODO Tratar corretamente o erro
                    ...

            if target_map is not None:
                if telemetry_data.feature_name not in target_map:
                    target_map[telemetry_data.feature_name] = FeatureStatistics(feature_name= telemetry_data.feature_name)

                feature_stats = target_map[telemetry_data.feature_name]
                feature_stats.execution_count += 1
                feature_stats.last_executed = telemetry_data.timestamp

                feature_execution_time = telemetry_data.execution_time

                # Define o tempo de execução mais lento
                if feature_stats.slowest_execution_time < feature_execution_time:
                    feature_stats.slowest_execution_time = feature_execution_time

                # Define a média de tempo de execução
                if feature_stats.execution_count == 1:
                    feature_stats.average_execution_time = feature_execution_time

                else:
                    average_execution_time = ((feature_stats.average_execution_time * (feature_stats.execution_count - 1)) + feature_execution_time) / feature_stats.execution_count
                    feature_stats.average_execution_time = average_execution_time

        self.dashboard.add_log(log_message)

    def get_most_used_commands_data(self) -> list[dict[str, Any]]:
        """Retorna os 5 comandos mais executados junto da quantidade de execuções"""
        most_used_commands = sorted(
            self.statistics.commands_statistics_map.items(),
            key= lambda data: data[1].execution_count,
            reverse= True
        )[:5]

        response = [
            {
                "command_name": most_used_command[1].feature_name,
                "execution_count": most_used_command[1].execution_count,
                "average_execution_time": most_used_command[1].average_execution_time
            }
            for most_used_command in most_used_commands
        ]

        return response

    def get_slowest_commands_data(self) -> list[dict[str, Any]]:
        """Retorna os 5 comandos mais lentos junto do tempo de execução total e médio deles"""
        slowest_commands = sorted(
            self.statistics.commands_statistics_map.items(),
            key= lambda data: data[1].slowest_execution_time,
            reverse= True
        )[:5]

        response = [
            {
                "command_name": slowest_command[1].feature_name,
                "slowest_execution_time": slowest_command[1].slowest_execution_time,
                "average_execution_time": slowest_command[1].average_execution_time
            }
            for slowest_command in slowest_commands
        ]

        return response

    async def record_sent_message(self, response_payload: BotResponsePayload) -> None:
        self.statistics.messages_sent += 1

    async def record_exception(self, exception_payload: TelemetryExceptionPayload) -> None:
        self.statistics.total_exceptions += 1

        exception_log = [
            f"name: {exception_payload.name}",
            f"severity: {exception_payload.severity}",
            f"message: {exception_payload.message}",
            f"discord event: {exception_payload.discord_event}",
            f"arguments: {exception_payload.arguments}",
            f"trimmed traceback: {exception_payload.trimmed_traceback}"
        ]

        self.dashboard.add_exception(exception_log, default_style= "red")

    def record_basic_exception(self, exception_message: str):
        self.statistics.total_exceptions += 1
        self.dashboard.add_exception([exception_message], default_style= "red")
