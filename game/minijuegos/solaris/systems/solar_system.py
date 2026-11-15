import math
import pygame
from .. import settings as S
from ..entities.solar_panel import SolarPanel


class SolarSystem:
    def __init__(self):
        self.center = (S.WIDTH // 2, 330)
        self.orbit_time = 0.0
        self.phase = 0.0
        self.panels = [
            SolarPanel("ALFA", 365, 190, 35),
            SolarPanel("BETA", 660, 190, 145),
            SolarPanel("GAMMA", 365, 465, 220),
            SolarPanel("DELTA", 660, 465, 310),
        ]
        self.selected = 0
        self.panels[0].selected = True
        self.sun_x = 850.0
        self.sun_y = 180.0

    def update(self, dt, elapsed):
        self.orbit_time += dt
        self.phase += dt * (0.16 + 0.03 * elapsed)
        self.sun_x = self.center[0] + math.cos(self.phase) * 405
        self.sun_y = self.center[1] + math.sin(self.phase) * 235
        for panel in self.panels:
            panel.get_efficiency(self.sun_x, self.sun_y)

    def select_at(self, point):
        for index, panel in enumerate(self.panels):
            if panel.contains(point):
                self.selected = index
                for item in self.panels:
                    item.selected = False
                panel.selected = True
                return True
        return False

    def rotate_selected(self, amount):
        self.panels[self.selected].rotate(amount)

    def production_kw(self):
        return sum(panel.max_output * panel.efficiency for panel in self.panels)

    def draw(self, surface, font, small_font):
        # Trayectoria orbital del Sol
        pygame.draw.ellipse(surface, (26, 48, 75), (self.center[0] - 405, self.center[1] - 235, 810, 470), 1)
        sun_glow = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.circle(sun_glow, (255, 190, 70, 25), (50, 50), 48)
        pygame.draw.circle(sun_glow, (255, 205, 95, 55), (50, 50), 34)
        surface.blit(sun_glow, (int(self.sun_x - 50), int(self.sun_y - 50)))
        pygame.draw.circle(surface, (255, 190, 72), (int(self.sun_x), int(self.sun_y)), 19)
        pygame.draw.circle(surface, (255, 231, 145), (int(self.sun_x), int(self.sun_y)), 12)
        pygame.draw.circle(surface, (255, 245, 190), (int(self.sun_x - 4), int(self.sun_y - 4)), 4)
        # Rayos solares
        for offset in range(0, 360, 45):
            a = math.radians(offset + self.orbit_time * 25)
            p1 = (self.sun_x + math.cos(a) * 25, self.sun_y + math.sin(a) * 25)
            p2 = (self.sun_x + math.cos(a) * 32, self.sun_y + math.sin(a) * 32)
            pygame.draw.line(surface, S.YELLOW, p1, p2, 2)

        # Estación central
        cx, cy = self.center
        pygame.draw.circle(surface, (18, 40, 65), (cx, cy), 54)
        pygame.draw.circle(surface, S.CYAN, (cx, cy), 54, 2)
        pygame.draw.circle(surface, (43, 76, 105), (cx, cy), 30)
        pygame.draw.rect(surface, (165, 190, 205), (cx - 38, cy - 12, 76, 24), border_radius=5)
        pygame.draw.rect(surface, S.CYAN, (cx - 10, cy - 28, 20, 56), border_radius=4)
        pygame.draw.circle(surface, S.WHITE, (cx, cy), 5)
        for panel in self.panels:
            pygame.draw.line(surface, (108, 139, 163), self.center, (panel.x, panel.y), 3)
        for panel in self.panels:
            panel.draw(surface, small_font)

