import random
import pygame
from ..settings import WIDTH, HEIGHT, STAR_COUNT, STAR_SPEED_MIN, STAR_SPEED_MAX

class Starfield:
    def __init__(self):
        # --- VARIABLES DE ENTRADA ---
        self.count = STAR_COUNT
        self.min_speed = STAR_SPEED_MIN
        self.max_speed = STAR_SPEED_MAX
        self.colors = [
            (180, 200, 230),  # Azul tenue (lejanas)
            (230, 240, 255),  # Blanco estelar (medias)
            (255, 235, 190),  # Blanco cálido (cercanas)
        ]

        # --- VARIABLES DE SALIDA (Lista de estrellas: [x, y, speed, size, color]) ---
        self.stars = []
        self._init_stars()

    def _init_stars(self):
        for _ in range(self.count):
            depth = random.random()  # 0.0 (lejos) a 1.0 (cerca)
            x = random.uniform(0, WIDTH)
            y = random.uniform(60, HEIGHT - 70)  # Evita saturar detrás del HUD superior/inferior
            speed = self.min_speed + depth * (self.max_speed - self.min_speed)
            size = 1 if depth < 0.55 else (2 if depth < 0.88 else 3)
            color = self.colors[0] if size == 1 else (self.colors[1] if size == 2 else self.colors[2])
            self.stars.append([x, y, speed, size, color])

    def update(self, dt, in_saa=False):
        # --- LÓGICA DE DESPLAZAMIENTO ORBITAL ---
        # En la Anomalía del Atlántico Sur (SAA) el desplazamiento visual se acelera ligeramente
        speed_mult = 1.6 if in_saa else 1.0

        for star in self.stars:
            star[0] -= star[2] * speed_mult * dt
            if star[0] < 0:
                star[0] = WIDTH
                star[1] = random.uniform(60, HEIGHT - 70)

    def draw(self, surface):
        # --- SALIDA VISUAL ---
        for x, y, _, size, color in self.stars:
            pygame.draw.rect(surface, color, (int(x), int(y), size, size))