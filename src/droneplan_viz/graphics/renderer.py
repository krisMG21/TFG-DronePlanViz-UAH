# src/droneplan_viz/graphics/renderer.py

import pygame
import pygame_gui
import sys
from droneplan_viz.core.world import World
from droneplan_viz.core.agents import Drone, Package, Carrier, DroneState
from droneplan_viz.engine.dispatcher import Dispatcher

class Renderer:
    def __init__(self, world: World, dispatcher: Dispatcher, tile_size: int = 64):
        pygame.init()
        self.world = world
        self.dispatcher = dispatcher
        self.tile_size = tile_size
        
        self.screen_width = world.width * tile_size
        self.screen_height = (world.height * tile_size) + 120  # Más espacio para la UI
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("droneplan_viz - Simulador de Planificación")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 16)
        
        # --- NUEVO: Configuración de la Interfaz (UI) ---
        self.ui_manager = pygame_gui.UIManager((self.screen_width, self.screen_height))
        
        # Crear un slider (barra de tiempo) en la parte inferior
        slider_rect = pygame.Rect((20, self.screen_height - 50), (self.screen_width - 40, 30))
        self.time_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=slider_rect,
            start_value=0,
            value_range=(0, 0), # Se actualizará dinámicamente según haya más snapshots
            manager=self.ui_manager
        )
        
        self.running = True
        self.is_paused = False # Estado de reproducción

    def _logical_to_pixel(self, x: float, y: float):
        return int(x * self.tile_size), int(y * self.tile_size)

    def _draw_grid(self):
        for x in range(0, self.screen_width, self.tile_size):
            for y in range(0, self.screen_height - 120, self.tile_size):
                rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

    def _draw_entities(self):
        for entity in self.world.entities.values():
            if not entity.is_active: continue
            
            px, py = self._logical_to_pixel(entity.x, entity.y)
            center = (px + self.tile_size // 2, py + self.tile_size // 2)

            if isinstance(entity, Drone):
                color = (0, 120, 255) # IDLE
                if entity.state == DroneState.MOVING: color = (255, 165, 0) # Naranja
                if entity.state == DroneState.ERROR: color = (255, 0, 0) # Rojo
                
                pygame.draw.circle(self.screen, color, center, self.tile_size // 3)
                label = self.font.render(entity.id, True, (0, 0, 0))
                self.screen.blit(label, (px + 5, py + 5))

            elif isinstance(entity, Package):
                rect = pygame.Rect(px + 16, py + 16, 32, 32)
                pygame.draw.rect(self.screen, (139, 69, 19), rect)
                # Cambiado a color negro para que no se camufle con el fondo blanco
                label = self.font.render(entity.content_id, True, (0, 0, 0))
                self.screen.blit(label, (px + 20, py + 20))

    def _draw_hud(self):
        hud_rect = pygame.Rect(0, self.screen_height - 120, self.screen_width, 120)
        pygame.draw.rect(self.screen, (50, 50, 50), hud_rect)
        
        # Muestra el total de snapshots en memoria
        total_snaps = len(self.world.history)
        current_snap = self.world.current_snapshot_index
        
        stats_text = f"Tiempo Lógico: {self.world.current_time:.2f}s | Batería Plan: {self.world.total_cost:.1f} | Snapshots: {current_snap}/{total_snaps - 1}"
        img = self.font.render(stats_text, True, (255, 255, 255))
        self.screen.blit(img, (20, self.screen_height - 100))

    def start(self):
        # Toma una primera foto estática nada más arrancar
        self.world.take_snapshot()

        while self.running:
            dt_ms = self.clock.tick(60)
            dt_sec = dt_ms / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # --- NUEVO: Captura de eventos de la UI ---
                if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element == self.time_slider:
                        # Si el usuario mueve la barra, pausamos el motor y viajamos en el tiempo
                        self.is_paused = True 
                        target_index = int(event.value)
                        self.world.restore_snapshot(target_index)

                self.ui_manager.process_events(event)

            # --- NUEVO: Lógica condicional de actualización ---
            # Solo avanzamos el tiempo si no estamos pausados viajando por el historial
            if not self.is_paused:
                self.dispatcher.tick(dt_sec)
                
                # Actualizar el rango máximo del slider si el dispatcher genera nuevas fotos
                if len(self.world.history) > 1:
                    max_val = len(self.world.history) - 1
                    self.time_slider.value_range = (0, max_val)
                    self.time_slider.set_current_value(self.world.current_snapshot_index)

            self.ui_manager.update(dt_sec)

            # Renderizado
            self.screen.fill((255, 255, 255))
            self._draw_grid()
            self._draw_entities()
            self._draw_hud()
            self.ui_manager.draw_ui(self.screen) # Dibujar la interfaz por encima de todo
            
            pygame.display.flip()

        pygame.quit()
        sys.exit()