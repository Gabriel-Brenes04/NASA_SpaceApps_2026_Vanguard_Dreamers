import math
import pygame
from ..settings import PARTICLE_TYPES, CLICK_MARGIN, TRAIL_MAX_LENGTH

class Particle:
    def __init__(self, x, y, p_type_key, target_module):
        # --- VARIABLES DE ENTRADA ---
        self.start_x = float(x)
        self.start_y = float(y)
        self.type_key = p_type_key
        self.target = target_module
        
        data = PARTICLE_TYPES[p_type_key]
        self.color = data["color"]
        self.base_speed = data["speed"]
        self.radius = data["radius"]
        self.dose = data["dose"]
        self.points = data["points"]
        self.ideal_detector = data["ideal"]

        # --- VARIABLES DE SALIDA (Estado dinámico) ---
        self.x = self.start_x
        self.y = self.start_y
        self.dir_x = -1.0
        self.dir_y = 0.0
        self.trail = []
        self.revealed_track = False
        self.slowed = False
        self.has_collided = False

        # --- LÓGICA DE INICIALIZACIÓN ---
        self._calculate_trajectory()

    def _calculate_trajectory(self):
        tx, ty = self.target.rect.center
        dx = tx - self.x
        dy = ty - self.y
        distance = math.hypot(dx, dy)
        if distance > 0:
            self.dir_x = dx / distance
            self.dir_y = dy / distance

    def update(self, dt):
        # --- LÓGICA DE MOVIMIENTO ---
        speed_multiplier = 0.65 if self.slowed else 1.0
        current_speed = self.base_speed * speed_multiplier

        self.x += self.dir_x * current_speed * dt
        self.y += self.dir_y * current_speed * dt

        self.trail.append((self.x, self.y))
        if len(self.trail) > TRAIL_MAX_LENGTH:
            self.trail.pop(0)

        self.has_collided = self.target.rect.collidepoint(int(self.x), int(self.y))

    def is_clicked(self, mouse_pos):
        # --- LÓGICA DE INTERACCIÓN ---
        mx, my = mouse_pos
        dist = math.hypot(self.x - mx, self.y - my)
        return dist <= (self.radius + CLICK_MARGIN)

    def draw(self, surface):
        # --- SALIDA VISUAL ---
        if self.revealed_track:
            pygame.draw.line(surface, (90, 130, 160), (int(self.x), int(self.y)), self.target.rect.center, 1)

        if len(self.trail) > 1:
            pygame.draw.lines(surface, self.color, False, self.trail, width=2)

        glow_radius = self.radius * 2
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, 70), (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surf, (int(self.x - glow_radius), int(self.y - glow_radius)))

        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), max(2, self.radius // 3))