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
    from app.core.telemetry import SystemStatistics

class TerminalDashboard:
    def __init__(self) -> None:
        self.layout = Layout()

        self.log_buffer = []
        self.exception_log_buffer = []
        self.buffer_size = 20

        self._setup_layout()

    def _setup_layout(self) -> None:
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

        self.layout["column_2"]["exceptions"].update(
            Panel(
                Group(
                    Text("Nenhuma exceção registrada no momento.", style= "green")
                ),
                title= "Exceptions",
                border_style= "blue"
            )
        )

    def add_log(self, message: Sequence[str | tuple[str, str]], default_style: str = "white") -> None:
        self._update_log_panel(message, self.log_buffer, "logs", "System Logs", default_style)

    def add_exception(self, exception_log: Sequence[tuple[str, str] | str], default_style: str = "red") -> None:

        self._update_log_panel(exception_log, self.exception_log_buffer, "exceptions", "Exceptions", default_style)

    def update_statistics(self, statistics: "SystemStatistics") -> None:
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

        most_used_commands = statistics.get_most_used_commands_data()
        slowest_commands = statistics.get_slowest_commands_data()

        most_used_commands_table = self._create_most_used_commands_table(most_used_commands)
        slowest_commands_table = self._create_slowest_commands_table(slowest_commands)

        self.layout["column_1"]["commands_info_line"]["most_used_commands"].update(
            Panel(most_used_commands_table, title= "Most Used Commands", border_style= "blue")
        )

        self.layout["column_1"]["commands_info_line"]["slowest_commands"].update(
            Panel(slowest_commands_table, title= "Slowest Commands", border_style= "blue")
        )

    def _update_log_panel(
            self,
            log_chunks: Sequence[tuple[str, str] | str],
            buffer: list[Text],
            panel_name: str,
            panel_title: str,
            default_style: str = "white"
        ):
        # TODO Melhorar a aba de logs. Deve buscar o tamanho do layout para exibir a quantidade corretas de linhas
        # E as mensagens rolarem de cima para baixo
        timestamp = datetime.now().strftime("%H:%M:%S")
        parsed_message = []

        for log_chunk in log_chunks:
            if isinstance(log_chunk, str):
                parsed_message.append((log_chunk, default_style))
            else:
                parsed_message.append(log_chunk)

        log_line = Text.assemble(
            (f"[{timestamp}] ", "cyan"),
            *parsed_message
        )

        # Insere como primeiro da lista
        buffer.insert(0, log_line)

        if len(buffer) > self.buffer_size:
            _ = buffer.pop()

        self.layout["column_2"][panel_name].update(
            Panel(Group(*buffer), title= panel_title, border_style= "blue")
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

    def _get_starfield_background(self) -> Text:
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
