"""
Biblioteca común usada por las variantes PFSP y TSP.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TipoProblema(str, Enum):
    """Tipos conocidos; TEXTO permite representar un dataset no clasificado."""

    PFSP = "PFSP"
    TSP = "TSP"
    TEXTO = "TEXTO"


@dataclass
class Instancia:
    """Dataset flexible: cada lector determina sus datos y metadatos."""

    nombre: str
    tipo: TipoProblema | str
    datos: Any
    metadatos: dict[str, Any] = field(default_factory=dict)


from src.pfsp import (
    calcular_makespan,
    calcular_makespan_parcial,
    leer_instancia_taillard,
    validar_permutacion,
)

__all__ = [
    "Instancia", "TipoProblema", "calcular_makespan", "calcular_makespan_parcial",
    "leer_instancia_taillard", "validar_permutacion",
]
