# src/droneplan_viz/api/client.py

from typing import Optional
from droneplan_viz.core.world import World
from droneplan_viz.core.agents import Drone, Package, Carrier, DroneState
from droneplan_viz.engine.dispatcher import Dispatcher, ActionInstance

class SimulationAPI:
    """
    Punto de entrada principal para los scripts de los alumnos.
    Encapsula la complejidad del motor temporal y el estado global.
    """
    def __init__(self):
        # Al ser Singleton, siempre obtenemos la misma instancia del mundo
        self.world = World()
        self.dispatcher = Dispatcher(self.world)
        
        # Reloj interno para dominios puramente secuenciales (STRIPS)
        self._sequential_time = 0.0

    # ==========================================
    # CONFIGURACIÓN DEL ENTORNO (Setup)
    # ==========================================

    def setup_grid(self, width: int, height: int) -> None:
        """Inicializa las dimensiones del mundo."""
        self.world.configure(width, height)

    def add_drone(self, drone_id: str, x: int, y: int, battery: float, arms: int) -> None:
        """Instancia y registra un nuevo dron en el mapa."""
        drone = Drone(drone_id, float(x), float(y), battery, arms)
        self.world.add_entity(drone)

    def add_package(self, package_id: str, x: int, y: int, content: str) -> None:
        """Instancia y registra una caja."""
        package = Package(package_id, float(x), float(y), content)
        self.world.add_entity(package)

    # ==========================================
    # TRATAMIENTO DEL TIEMPO
    # ==========================================

    def _resolve_time(self, start_time: Optional[float], duration: float) -> float:
        """
        Si no se provee tiempo, asume ejecución secuencial.
        Si se provee, asume planificación temporal y permite concurrencia.
        """
        if start_time is None:
            t = self._sequential_time
            self._sequential_time += duration
            return t
        return start_time

    # ==========================================
    # PRIMITIVAS DE ACCIÓN (El Plan)
    # ==========================================

    def move(self, drone_id: str, target_x: int, target_y: int, 
             start_time: Optional[float] = None, duration: float = 2.0) -> None:
        """
        Encola una acción de movimiento.
        No ejecuta el movimiento instantáneamente, lo delega al Dispatcher.
        """
        drone = self.world.get_entity(drone_id)
        if not isinstance(drone, Drone):
            raise ValueError(f"Entidad '{drone_id}' no encontrada o no es un Dron.")

        t_start = self._resolve_time(start_time, duration)

        # Variables de estado para la interpolación
        state = {'start_x': None, 'start_y': None, 'initialized': False}

        def update(progress: float):
            # Capturar el origen exacto en el frame 0 de la animación
            if not state['initialized']:
                state['start_x'] = drone.x
                state['start_y'] = drone.y
                state['initialized'] = True
                drone.state = DroneState.MOVING

            # Interpolación lineal (Lerp)
            current_x = state['start_x'] + (target_x - state['start_x']) * progress
            current_y = state['start_y'] + (target_y - state['start_y']) * progress
            drone.set_position(current_x, current_y)

        def finish():
            # Asegurar la posición exacta al finalizar y consumir recursos
            drone.set_position(target_x, target_y)
            drone.consume_battery(duration * 1.5) # Ejemplo: 1.5 uds de batería por segundo

        # Crear y encolar la acción en el motor temporal
        action = ActionInstance(drone_id, t_start, duration, update, finish)
        self.dispatcher.enqueue_action(action)

    def pickup(self, drone_id: str, package_id: str, 
               start_time: Optional[float] = None, duration: float = 1.0) -> None:
        """
        Encola una acción de manipulación (coger paquete).
        """
        drone = self.world.get_entity(drone_id)
        package = self.world.get_entity(package_id)
        
        if not isinstance(drone, Drone) or not isinstance(package, Package):
            raise ValueError("IDs inválidos para Dron o Paquete.")

        t_start = self._resolve_time(start_time, duration)

        def update(progress: float):
            # Visulamente el dron no se mueve, pero está ocupado
            drone.state = DroneState.INTERACTING

        def finish():
            # Realizar la comprobación lógica estricta al momento de ejecutarse
            if (drone.x, drone.y) != (package.x, package.y):
                drone.state = DroneState.ERROR
                raise RuntimeError(f"Colisión lógica: El dron {drone.id} intentó coger {package.id} desde otra casilla.")
            
            # Delega la mutación de estado a la Capa Lógica
            drone.pickup_package(package)
            drone.consume_battery(duration * 0.5)

        action = ActionInstance(drone_id, t_start, duration, update, finish)
        self.dispatcher.enqueue_action(action)