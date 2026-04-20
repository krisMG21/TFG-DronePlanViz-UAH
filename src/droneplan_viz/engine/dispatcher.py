# src/droneplan_viz/engine/dispatcher.py

from typing import Callable, List, Dict
from droneplan_viz.core.agents import Drone, DroneState
from droneplan_viz.core.world import World

class ActionInstance:
    """
    Estructura de datos que representa una acción encolada en el tiempo.
    """
    def __init__(self, agent_id: str, t_start: float, duration: float, 
                 update_func: Callable[[float], None], 
                 finish_func: Callable[[], None]):
        self.agent_id = agent_id
        self.t_start = t_start
        self.duration = duration
        self.t_end = t_start + duration
        
        # Funciones callback inyectadas por la API
        self.update_func = update_func   # Se llama en cada frame para interpolar
        self.finish_func = finish_func   # Se llama una vez al terminar (t >= t_end)
        self.completed = False

class Dispatcher:
    """
    Motor temporal. Lee la cola de acciones y avanza el estado lógico del mundo
    en función del Delta Time provisto por el bucle gráfico.
    """
    def __init__(self, world: World):
        self.world = world
        self.action_queue: List[ActionInstance] = []
        self.speed_multiplier: float = 1.0

    def enqueue_action(self, action: ActionInstance) -> None:
        """Añade una nueva acción a la cola de procesamiento continuo."""
        self.action_queue.append(action)
        # Se ordena la cola por tiempo de inicio para procesar cronológicamente
        self.action_queue.sort(key=lambda a: a.t_start)

    def tick(self, delta_time_seconds: float) -> None:
        """
        Avanza el reloj global y procesa las acciones activas.
        Se invoca desde el Game Loop (Capa Gráfica).
        """
        if not self.action_queue:
            return # Si no hay acciones, el tiempo fluye pero no se procesa lógica
            
        # Avanzar el tiempo lógico del mundo
        step = delta_time_seconds * self.speed_multiplier
        self.world.current_time += step
        
        current_t = self.world.current_time
        
        for action in self.action_queue:
            if action.completed:
                action.finish_func()
                self.world.take_snapshot()      
                
            # Si la acción aún no ha empezado, la ignoramos
            if current_t < action.t_start:
                continue
                
            # Calcular porcentaje de progreso (0.0 a 1.0)
            if action.duration <= 0:
                progress = 1.0
            else:
                progress = (current_t - action.t_start) / action.duration
                progress = min(max(progress, 0.0), 1.0) # Clamp entre 0 y 1
            
            # Ejecutar interpolación
            action.update_func(progress)
            
            # Si ha terminado, ejecutar estado final y marcar como completada
            if current_t >= action.t_end:
                action.finish_func()
                action.completed = True
                
                # Liberar al agente de su estado bloqueante
                agent = self.world.get_entity(action.agent_id)
                if isinstance(agent, Drone) and agent.state != DroneState.ERROR:
                    agent.state = DroneState.IDLE
                    
        # Limpiar acciones completadas de la memoria
        self.action_queue = [a for a in self.action_queue if not a.completed]