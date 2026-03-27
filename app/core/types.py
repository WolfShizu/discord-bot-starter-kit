from enum import Enum

class FeatureType(Enum):
    COMMAND = "command"
    LISTENER = "listeners"

class ExceptionSeverity(Enum):
    UNKNOWN = "unknown"
    """Usado para definir a severidade de exceções padrões"""

    LOW = "low"
    """Notifica apenas no terminal. Erro aceitável e esperado."""

    MEDIUM = "medium"
    """Notifica e guarda o erro. Funcionalidade afetada, exige correção."""

    CRITICAL = "critical"
    """Notifica, guarda o erro e encerra o processo para evitar corrupção de dados."""
