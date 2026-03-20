from datetime import datetime
from typing import TYPE_CHECKING, Sequence, Any
import random

from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.console import Group
from rich.text import Text
from rich import box

if TYPE_CHECKING:
    from app.core.telemetry import SystemStatistics, Telemetry

class TerminalDashboard:
    def __init__(self):
        self.layout = Layout()

        self.log_buffer = []
        self.exception_log_buffer = []
        self.max_logs = 20

        self.telemetry: "Telemetry"

        self._setup_layout()

    def get_telemetry(self, telemetry: "Telemetry"):
        self.telemetry = telemetry

    def _setup_layout(self):
        self.layout.split_row(
            Layout(name= "column_1"),
            Layout(name= "column_2"),
        )

        self.layout["column_1"].split_column(
            Layout(name= "system_data_panel", size= 17),
            Layout(name= "commands_info_line")
        )

        self.layout["column_1"]["system_data_panel"].split_row(
            Layout(name= "system_data_line"),
            Layout(name= "empty_space")
        )

        self.layout["column_1"]["system_data_panel"]["system_data_line"].split_column(
            Layout(name= "system", size= 7),
            Layout(name= "info", size= 10),
        )

        self.layout["column_1"]["commands_info_line"].split_row(
            Layout(name= "most_used_commands"),
            Layout(name= "slowest_commands")
        )

        self.layout["column_2"].split_column(
            Layout(name= "exceptions"),
            Layout(name= "logs"),
            Layout(name= "empty_panel"),
        )

        self.layout["column_2"]["empty_panel"].split_row(
            Layout(name= "empty_1"),
            Layout(name= "empty_2")
        )

        self.layout["column_1"]["system_data_panel"]["empty_space"].update(
            Panel(
                self._get_starfield_background(),
                title="[bold purple] ◈ WOLFSHIZU // UNIT-01 ◈ [/]",
                border_style="purple",
                box= box.SQUARE,

            )
        )

    def add_log(self, message: Sequence[str | tuple[str, str]], default_style: str = "white"):
            # TODO Melhorar a aba de logs. Deve buscar o tamanho do layout para exibir a quantidade corretas de linhas
            # E as mensagens rolarem de cima para baixo
            timestamp = datetime.now().strftime("%H:%M:%S")

            parsed_message = []

            for message_chunk in message:
                if isinstance(message_chunk, str):
                    parsed_message.append((message_chunk, default_style))
                else:
                    parsed_message.append(message_chunk)

            log_line = Text.assemble(
                (f"[{timestamp}] ", "cyan"),
                *parsed_message
            )

            # Insere como primeiro da lista
            self.log_buffer.insert(0, log_line)

            if len(self.log_buffer) > self.max_logs:
                self.log_buffer.pop()

            self.layout["column_2"]["logs"].update(
                Panel(Group(*self.log_buffer), title="Live Logs", border_style="blue")
            )

    def update_statistics(self, statistics: "SystemStatistics"):
        system_data = (
            f"[bold white]Status:[/] [green]{statistics.system_status}[/]\n"
            f"[bold white]connect As:[/] [yellow]{statistics.connected_as}[/]\n"
            f"[bold white]ID:[/] [dim]{statistics.bot_id}[/]\n"
            f"[bold white]CPU usage:[/] [medium_purple1]{statistics.cpu_usage}[/]\n"
            f"[bold white]RAM usage:[/] [medium_purple1]{statistics.ram_usage}[/]\n"
        )

        info_data = (
            f"[bold white]uptime:[/] [medium_purple1]{statistics.uptime}\n[/]"
            f"[bold white]guilds:[/] [blue]{statistics.guilds}\n[/]"
            f"[bold white]Processed Messages:[/] [blue]{statistics.processed_messages}\n[/]"
            f"[bold white]messages Sent:[/] [blue]{statistics.messages_sent}\n[/]"
            f"[bold white]features Executed:[/] [blue]{statistics.features_executed}\n[/]"
            f"[bold white]listeners Executed:[/] [blue]{statistics.listeners_executed}\n[/]"
            f"[bold white]commands Executeds:[/] [blue]{statistics.commands_executed}\n[/]"
            f"[bold white]exceptions:[/] [red]{statistics.total_exceptions}[/]"
        )

        self.layout["column_1"]["system_data_line"]["system"].update(
            Panel(system_data, title= "SYSTEM", border_style= "green")
        )

        self.layout["column_1"]["system_data_line"]["info"].update(
            Panel(info_data, title= "INFO", border_style= "cyan")
        )

        most_used_commands = self.telemetry.get_most_used_commands_data()
        slowest_commands = self.telemetry.get_slowest_commands_data()

        most_used_commands_table = self._create_most_used_commands_table(most_used_commands)
        slowest_commands_table = self._create_slowest_commands_table(slowest_commands)

        self.layout["column_1"]["commands_info_line"]["most_used_commands"].update(
            Panel(most_used_commands_table, title= "Most Used Commands", border_style= "blue")
        )

        self.layout["column_1"]["commands_info_line"]["slowest_commands"].update(
            Panel(slowest_commands_table, title= "Slowest Commands", border_style= "blue")
        )

    def _create_most_used_commands_table(self, most_used_commands: list[dict[str, Any]]) -> Table:
        most_used_commands_data = []
        for command in most_used_commands:
            most_used_commands_data.append(
                [
                    command["command_name"],
                    str(command["execution_count"]),
                    f"{command["average_execution_time"]:.2f}ms"
                ]
            )

        columns = [
            {"header": "Comando"},
            {"header": "Execuções"},
            {"header": "Tempo Médio"},
        ]

        most_used_commands_table = self._create_table(columns= columns, rows= most_used_commands_data)
        return most_used_commands_table

    def _create_slowest_commands_table(self, slowest_commands: list[dict[str, Any]]) -> Table:
        slowest_commands_data = []
        for command in slowest_commands:
            slowest_commands_data.append(
                [
                    command["command_name"],
                    f"{command["slowest_execution_time"]:.2f}ms",
                    f"{command["average_execution_time"]:.2f}ms"
                ]
            )

        columns = [
            {"header": "Comando"},
            {"header": "Execução mais lenta"},
            {"header": "Tempo Médio"},
        ]

        slowest_commands_table = self._create_table(columns= columns, rows= slowest_commands_data)
        return slowest_commands_table

    def _create_table(
            self,
            columns: list[dict[str, Any]],
            rows: list[dict[str, Any]],
            header_style: str = "blue"
        ) -> Table:
        table = Table(
            expand= True,
            box= box.ROUNDED,
            header_style= header_style
        )

        for column in columns:
            table.add_column(**column)

        for row in rows:
            table.add_row(*row)

        return table

    def update_command_info(self):
        ...

    def add_exception(self, exception_log, default_style: str = "white"):
        # TODO Mover essa lógica para uma função auxiliar que é chamada pelo exception e log
        # TODO Melhorar a aba de logs. Deve buscar o tamanho do layout para exibir a quantidade corretas de linhas
        # E as mensagens rolarem de cima para baixo
        timestamp = datetime.now().strftime("%H:%M:%S")
        parsed_message = []

        for log_chunk in exception_log:
            if isinstance(log_chunk, str):
                parsed_message.append((log_chunk, default_style))
            else:
                parsed_message.append(log_chunk)

        log_line = Text.assemble(
            (f"[{timestamp}] ", "cyan"),
            *parsed_message
        )

        # Insere como primeiro da lista
        self.exception_log_buffer.insert(0, log_line)

        if len(self.exception_log_buffer) > self.max_logs:
            self.exception_log_buffer.pop()

        self.layout["column_2"]["exceptions"].update(
            Panel(Group(*self.exception_log_buffer), title="Live Logs", border_style="blue")
        )

    def update_empty_panel(self):
        ...

    def _get_starfield_background(self):
        lines = 100
        lenght = 200

        characters = [".", ".", "·", "+", "*"]
        colors = ["dim white", "purple", "magenta", "bold white", "deep_pink3", "yellow", "blue"]

        star_lines = []

        for _ in range(lines):
            current_line = ""

            current_line += " " * random.randint(0, 5)

            while len(current_line) < lenght:
                character = random.choice(characters)
                color = random.choice(colors)
                current_line += f"[{color}]{character}[/]"
                current_line += " " * random.randint(4, 9)

            star_lines.append(current_line)

        full_markup = "\n".join(star_lines)

        starfield = Text.from_markup(full_markup)

        starfield.no_wrap = True
        starfield.overflow = "crop"
        return starfield
