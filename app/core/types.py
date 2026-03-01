from enum import Enum, auto

class FeatureType(Enum):
    COMMAND = auto()
    LISTENER = auto()

class ExceptionSeverity(Enum):
    LOW = auto()
    """Notifica apenas no terminal. Erro aceitável e esperado."""

    MEDIUM = auto()
    """Notifica e guarda o erro. Funcionalidade afetada, exige correção."""

    CRITICAL = auto()
    """Notifica, guarda o erro e encerra o processo para evitar corrupção de dados."""
