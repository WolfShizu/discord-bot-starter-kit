from datetime import datetime
from typing import TYPE_CHECKING
import random

from rich.layout import Layout
from rich.panel import Panel
from rich.console import Group
from rich.text import Text

if TYPE_CHECKING:
    from app.core.telemetry import SystemStatistics

class TerminalDashboard:
    def __init__(self):
        self.layout = Layout()

        self.log_buffer = []
        self.max_logs = 20

        self._setup_layout()

    def _setup_layout(self):
        self.layout.split_row(
            Layout(name= "column_1"),
            Layout(name= "column_2")
        )

        self.layout["column_1"].split_column(
            Layout(name= "system_data_panel", size= 16),
            Layout(name= "commands_info_line")
        )

        self.layout["column_1"]["system_data_panel"].split_row(
            Layout(name= "system_data_line"),
            Layout(name= "empty_space")
        )

        self.layout["column_1"]["system_data_panel"]["system_data_line"].split_column(
            Layout(name= "system", size= 7),
            Layout(name= "info", size= 9),
        )

        self.layout["column_1"]["commands_info_line"].split_row(
            Layout(name= "most_used_commands"),
            Layout(name= "slowest_commands")
        )

        self.layout["column_2"].split_column(
            Layout(name= "exceptions"),
            Layout(name= "logs"),
            Layout(name= "empty1"),
            Layout(name= "empty2")
        )

        self.layout["column_1"]["system_data_panel"]["empty_space"].update(
            Panel(
                self._get_starfield_background(),
                title="[bold purple] ◈ WOLFSHIZU // UNIT-01 ◈ [/]",
                border_style="purple",
            )
        )

    def add_log(self, message: str, style: str = "white"):
            # TODO Melhorar a aba de logs. Deve buscar o tamanho do layout para exibir a quantidade corretas de linhas
            # E as mensagens rolarem de cima para baixo
            timestamp = datetime.now().strftime("%H:%M:%S")

            log_line = Text.assemble(
                (f"[{timestamp}] ", "cyan"),
                (message, style)
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
        )

        self.layout["column_1"]["system_data_line"]["system"].update(
            Panel(system_data, title= "SYSTEM", border_style= "green")
        )

        self.layout["column_1"]["system_data_line"]["info"].update(
            Panel(info_data, title= "INFO", border_style= "cyan")
        )


    def update_command_info(self):
        ...

    def add_exception(self):
        ...

    def update_empty_panel(self):
        ...

    def _get_starfield_background(self):
        lines = 100
        lenght = 200

        characters = [".", ".", "·", "+", "*", "°"]
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
