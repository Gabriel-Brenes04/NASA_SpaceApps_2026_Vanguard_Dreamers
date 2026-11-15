import math
import pygame

from .. import settings as S


class SolarPanel:
    def __init__(self, name, x, y, angle):
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.angle = float(angle) % 360
        self.selected = False
        self.max_output = S.PANEL_MAX_KW
        self.efficiency = 0.0

    def rotate(self, amount):
        self.angle = (self.angle + amount) % 360

    def get_efficiency(self, sun_x, sun_y):
        target = math.degrees(math.atan2(sun_y - self.y, sun_x - self.x))
        difference = abs((target - self.angle + 180) % 360 - 180)
        self.efficiency = max(0.0, math.cos(math.radians(difference)))
        return self.efficiency

    def contains(self, point):
        dx = point[0] - self.x
        dy = point[1] - self.y
        tangent = math.radians(self.angle + 90)
        along = dx * math.cos(tangent) + dy * math.sin(tangent)
        across = -dx * math.sin(tangent) + dy * math.cos(tangent)
        return abs(along) <= 58 and abs(across) <= 22

    def draw(self, surface, font):
        angle = math.radians(self.angle + 90)
        ux, uy = math.cos(angle), math.sin(angle)
        vx, vy = -uy, ux
        corners = []
        for a, b in [(-58, -21), (58, -21), (58, 21), (-58, 21)]:
            corners.append((self.x + ux * a + vx * b, self.y + uy * a + vy * b))
        pygame.draw.polygon(surface, S.PANEL_DARK, corners)
        pygame.draw.polygon(surface, S.CYAN if self.selected else S.PANEL_LIGHT, corners, 3 if self.selected else 2)
        for offset in (-38, -13, 13, 38):
            p1 = (self.x + ux * offset - vx * 18, self.y + uy * offset - vy * 18)
            p2 = (self.x + ux * offset + vx * 18, self.y + uy * offset + vy * 18)
            pygame.draw.line(surface, (48, 139, 190), p1, p2, 1)
        nx, ny = math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))
        start = (self.x, self.y)
        end = (self.x + nx * 34, self.y + ny * 34)
        pygame.draw.line(surface, S.YELLOW, start, end, 3)
        pygame.draw.circle(surface, S.YELLOW, (int(end[0]), int(end[1])), 4)
        pct = int(self.efficiency * 100)
        color = S.GREEN if pct >= 80 else S.YELLOW if pct >= 45 else S.RED
        value = font.render(f"{pct}%", True, color)
        surface.blit(value, value.get_rect(center=(self.x, self.y + 72)))
