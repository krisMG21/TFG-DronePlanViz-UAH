# src/droneplan_viz/__init__.py

"""
droneplan_viz
Un framework de simulación gráfica y validación lógica para dominios PDDL de drones.
"""

# Exponemos públicamente solo la API, ocultando la complejidad interna
from .api.client import SimulationAPI

__version__ = "0.1.0"
__all__ = ["SimulationAPI"]