# src/droneplan_viz/core/world.py

from typing import Dict, List, Optional
from .entity import Entity

class World:
    """
    Gestor centralizado del estado lógico de la simulación (Singleton).
    Almacena las dimensiones del mapa y el registro de todas las entidades activas.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(World, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.width: int = 0
        self.height: int = 0
        self.entities: Dict[str, Entity] = {}
        
        # Métricas globales del plan
        self.current_time: float = 0.0
        self.total_cost: float = 0.0
        
        self._initialized = True

    def configure(self, width: int, height: int) -> None:
        """
        Define las dimensiones del entorno lógico (grid).
        """
        self.width = width
        self.height = height

    def add_entity(self, entity: Entity) -> None:
        """
        Registra una nueva entidad en el mundo.
        Lanza un error si el ID ya existe, garantizando la unicidad.
        """
        if entity.id in self.entities:
            raise ValueError(f"Inconsistencia lógica: La entidad con ID '{entity.id}' ya existe.")
        self.entities[entity.id] = entity

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Recupera una entidad por su identificador único.
        """
        return self.entities.get(entity_id)

    def get_entities_by_type(self, entity_type: type) -> List[Entity]:
        """
        Devuelve una lista de entidades filtradas por su clase (ej. todos los Drones).
        """
        return [e for e in self.entities.values() if isinstance(e, entity_type) and e.is_active]

    def remove_entity(self, entity_id: str) -> None:
        """
        Elimina (o desactiva) una entidad del registro lógico.
        """
        if entity_id in self.entities:
            self.entities[entity_id].is_active = False
            del self.entities[entity_id]

    def reset(self) -> None:
        """
        Limpia el estado del mundo. Útil para reiniciar la simulación.
        """
        self.entities.clear()
        self.current_time = 0.0
        self.total_cost = 0.0