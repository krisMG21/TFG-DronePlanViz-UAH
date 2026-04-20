# src/droneplan_viz/core/agents.py

from enum import Enum
from typing import List, Optional
from .entity import Entity

class DroneState(Enum):
    """Enumeración de los estados válidos para la máquina de estados del Dron."""
    IDLE = "IDLE"               # En reposo, listo para recibir órdenes
    MOVING = "MOVING"           # En tránsito, bloqueado para nuevas acciones
    INTERACTING = "INTERACTING" # Manipulando objetos (coger, soltar, cargar)
    ERROR = "ERROR"             # Fallo crítico (ej. sin batería)

class Package(Entity):
    """
    Representa una caja o paquete lógico en la simulación.
    """
    def __init__(self, entity_id: str, x: float, y: float, content_id: str):
        super().__init__(entity_id, x, y)
        self.content_id = content_id
        # Referencia a la entidad que lo transporta (puede ser un Drone o un Carrier)
        self.carried_by: Optional[Entity] = None

    def __repr__(self) -> str:
        return f"<Package {self.id} content='{self.content_id}' pos=({self.x}, {self.y})>"

class Carrier(Entity):
    """
    Representa un contenedor logístico (Carguero).
    Implementa un patrón Composite para gestionar las cajas en su interior.
    """
    def __init__(self, entity_id: str, x: float, y: float, capacity: int):
        super().__init__(entity_id, x, y)
        self.capacity = capacity
        self.content_list: List[Package] = []
        # Un carguero puede ser acoplado a un dron
        self.attached_to: Optional['Drone'] = None

    def load_package(self, package: Package) -> None:
        """Añade un paquete al carguero si hay capacidad física."""
        if len(self.content_list) >= self.capacity:
            raise ValueError(f"Fallo lógico: El carguero '{self.id}' ha superado su capacidad ({self.capacity}).")
        
        self.content_list.append(package)
        package.carried_by = self
        # Sincronizar posición de la caja con el carguero
        package.set_position(self.x, self.y)

    def set_position(self, x: float, y: float) -> None:
        """Sobrescribe el movimiento base para desplazar también su contenido (Cascada)."""
        super().set_position(x, y)
        for package in self.content_list:
            package.set_position(x, y)

class Drone(Entity):
    """
    Agente principal de la simulación. 
    Maneja sus recursos (batería, brazos) y su máquina de estados.
    """
    def __init__(self, entity_id: str, x: float, y: float, battery: float, max_arms: int):
        super().__init__(entity_id, x, y)
        self.battery = float(battery)
        self.max_arms = int(max_arms)
        self.used_arms = 0
        
        # Máquina de estados inicial
        self.state: DroneState = DroneState.IDLE
        
        # Inventario
        self.carried_packages: List[Package] = []
        self.attached_carrier: Optional[Carrier] = None

    def consume_battery(self, amount: float) -> None:
        """Reduce la batería y transita a ERROR si se agota."""
        self.battery -= amount
        if self.battery <= 0:
            self.battery = 0
            self.state = DroneState.ERROR

    def pickup_package(self, package: Package) -> None:
        """Coge una caja usando los brazos manipuladores."""
        if self.used_arms >= self.max_arms:
            raise ValueError(f"Fallo lógico: El dron '{self.id}' no tiene brazos libres.")
        
        self.carried_packages.append(package)
        self.used_arms += 1
        package.carried_by = self

    def set_position(self, x: float, y: float) -> None:
        """Sobrescribe el movimiento base para mover en solidaridad todo su inventario."""
        super().set_position(x, y)
        
        # Mover paquetes sujetados directamente por los brazos
        for package in self.carried_packages:
            package.set_position(x, y)
            
        # Mover el carguero acoplado (que a su vez moverá su contenido en cascada)
        if self.attached_carrier:
            self.attached_carrier.set_position(x, y)