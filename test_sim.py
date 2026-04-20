# test_sim.py

from droneplan_viz import SimulationAPI

def main():
    # 1. Instanciamos la API
    sim = SimulationAPI()

    # 2. Configuramos el mundo lógico (Grid de 10x10)
    sim.setup_grid(10, 10)

    # 3. Añadimos entidades iniciales
    # Dron: en (1, 1), 100% batería, 2 brazos
    sim.add_drone(drone_id="drone1", x=1, y=1, battery=100.0, arms=2)
    
    # Paquete: en (5, 5), contiene "Medicinas"
    sim.add_package(package_id="pkg_med", x=5, y=5, content="Medicinas")

    # 4. Inyectamos el Plan PDDL (Secuencia lógica)
    print("Encolando acciones...")
    
    # El dron vuela hacia el paquete
    sim.move(drone_id="drone1", target_x=5, target_y=5, duration=3.0)
    
    # El dron coge el paquete (solo tendrá éxito si llegó correctamente)
    sim.pickup(drone_id="drone1", package_id="pkg_med", duration=1.0)
    
    # El dron vuela hacia la base con el paquete a cuestas
    sim.move(drone_id="drone1", target_x=8, target_y=2, duration=4.0)

    # 5. Arrancamos el renderizado gráfico
    print("Iniciando simulación...")
    
    # En este momento se abre la ventana de PyGame. 
    # El bucle principal leerá las acciones encoladas y las animará.
    sim.dispatcher.world = sim.world # Sincronización final
    
    from droneplan_viz.graphics.renderer import Renderer
    renderer = Renderer(world=sim.world, dispatcher=sim.dispatcher)
    renderer.start()

if __name__ == "__main__":
    main()