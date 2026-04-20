# src/droneplan_viz/core/entity.py

from typing import Tuple

class Entity:
    """
    Clase base para todos los objetos físicos dentro de la simulación.
    Define las propiedades espaciales lógicas independientemente de su renderizado.
    """
    
    def __init__(self, entity_id: str, x: float, y: float):
        """
        Inicializa una nueva entidad.
        
        :param entity_id: Identificador único lógico (ej. 'dron1', 'paqueteA').
        :param x: Coordenada lógica X en la cuadrícula.
        :param y: Coordenada lógica Y en la cuadrícula.
        """
        self.id = entity_id
        
        # Coordenadas lógicas (pueden ser flotantes durante la interpolación del movimiento)
        self.x = float(x)
        self.y = float(y)
        
        # Estado de visibilidad o existencia lógica (False si el objeto es destruido o consumido)
        self.is_active = True

    def get_position(self) -> Tuple[float, float]:
        """Devuelve la posición lógica actual de la entidad."""
        return self.x, self.y

    def set_position(self, x: float, y: float) -> None:
        """Actualiza las coordenadas lógicas de la entidad."""
        self.x = float(x)
        self.y = float(y)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} pos=({self.x:.2f}, {self.y:.2f})>"