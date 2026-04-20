# src/droneplan_viz/graphics/renderer.py

import pygame
import sys
from droneplan_viz.core.world import World
from droneplan_viz.core.agents import Drone, Package, Carrier, DroneState
from droneplan_viz.engine.dispatcher import Dispatcher

class Renderer:
    """
    Motor de renderizado basado en PyGame.
    Maneja la ventana, el bucle principal y el dibujado de entidades.
    """
    def __init__(self, world: World, dispatcher: Dispatcher, tile_size: int = 64):
        pygame.init()
        self.world = world
        self.dispatcher = dispatcher
        self.tile_size = tile_size
        
        # Configuración de la ventana
        self.screen_width = world.width * tile_size
        self.screen_height = (world.height * tile_size) + 100  # Espacio extra para el HUD
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("droneplan_viz - Simulador de Planificación")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 16)
        self.running = True

    def _logical_to_pixel(self, x: float, y: float):
        """Transforma coordenadas del grid a píxeles de pantalla."""
        return int(x * self.tile_size), int(y * self.tile_size)

    def _draw_grid(self):
        """Dibuja la cuadrícula de fondo."""
        for x in range(0, self.screen_width, self.tile_size):
            for y in range(0, self.screen_height - 100, self.tile_size):
                rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

    def _draw_entities(self):
        """Renderiza cada entidad según su tipo y estado actual."""
        for entity in self.world.entities.values():
            if not entity.is_active: continue
            
            px, py = self._logical_to_pixel(entity.x, entity.y)
            center = (px + self.tile_size // 2, py + self.tile_size // 2)

            if isinstance(entity, Drone):
                # Color según estado
                color = (0, 120, 255) # Azul IDLE
                if entity.state == DroneState.MOVING: color = (255, 165, 0) # Naranja
                if entity.state == DroneState.ERROR: color = (255, 0, 0) # Rojo
                
                pygame.draw.circle(self.screen, color, center, self.tile_size // 3)
                # Dibujar ID del dron
                label = self.font.render(entity.id, True, (0, 0, 0))
                self.screen.blit(label, (px + 5, py + 5))

            elif isinstance(entity, Package):
                # Representación simple de una caja
                rect = pygame.Rect(px + 16, py + 16, 32, 32)
                pygame.draw.rect(self.screen, (139, 69, 19), rect) # Marrón
                label = self.font.render(entity.content_id, True, (255, 255, 255))
                self.screen.blit(label, (px + 20, py + 20))

    def _draw_hud(self):
        """Dibuja el panel inferior con métricas (Requisito RF-07)."""
        hud_rect = pygame.Rect(0, self.screen_height - 100, self.screen_width, 100)
        pygame.draw.rect(self.screen, (50, 50, 50), hud_rect)
        
        stats_text = f"Tiempo: {self.world.current_time:.2f}s | Entidades: {len(self.world.entities)}"
        img = self.font.render(stats_text, True, (255, 255, 255))
        self.screen.blit(img, (20, self.screen_height - 80))

    def start(self):
        """Ejecuta el Game Loop principal."""
        while self.running:
            # 1. Gestión de eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # 2. Actualización de la lógica (Dispatcher)
            dt = self.clock.tick(60) / 1000.0  # Delta time en segundos
            self.dispatcher.tick(dt)

            # 3. Renderizado
            self.screen.fill((255, 255, 255))
            self._draw_grid()
            self._draw_entities()
            self._draw_hud()
            
            pygame.display.flip()

        pygame.quit()
        sys.exit()