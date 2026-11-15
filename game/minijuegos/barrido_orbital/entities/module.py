import math
import os
import random
import pygame
from ..settings import (
    MODULE_BASE_COLOR, MODULE_BORDER_COLOR,
    MODULE_HIT_FILL, MODULE_HIT_BORDER, TEXT_COLOR,
    FLOAT_AMPLITUDE_Y, FLOAT_AMPLITUDE_X, FLOAT_SPEED, FLOAT_TILT_ANGLE
)

class StationModule:
    def __init__(self, name, x, y, width, height, image_path=None):
        # --- VARIABLES DE ENTRADA ---
        self.name = name
        self.base_x = float(x)
        self.base_y = float(y)
        self.width = width
        self.height = height
        self.image_path = image_path
        self.hit_flash_duration = 0.25

        # --- VARIABLES DE SALIDA (Estado interno y movimiento orbital) ---
        self.rect = pygame.Rect(int(self.base_x), int(self.base_y), self.width, self.height)
        self.hit_timer = 0.0
        self.hits = 0
        self.current_fill = MODULE_BASE_COLOR
        self.current_border = MODULE_BORDER_COLOR
        self.sprite = None
        self.hit_sprite = None

        # Variables de gravedad cero
        self.float_time = random.uniform(0.0, math.tau)  # Fase inicial distinta para cada módulo
        self.current_angle = 0.0
        self.recoil_x = 0.0

        # --- LÓGICA DE CARGA DE SPRITE ---
        self._load_sprite()

    def _load_sprite(self):
        if self.image_path and os.path.exists(self.image_path):
            raw_img = pygame.image.load(self.image_path).convert_alpha()
            self.sprite = pygame.transform.scale(raw_img, (self.width, self.height))

            self.hit_sprite = self.sprite.copy()
            red_tint = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            red_tint.fill((255, 70, 90, 160))
            self.hit_sprite.blit(red_tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def take_hit(self):
        # --- LÓGICA DE IMPACTO ---
        self.hit_timer = self.hit_flash_duration
        self.hits += 1
        self.recoil_x = -8.0  # Empuje hacia atrás por el impacto de la partícula

    def update(self, dt):
        # --- LÓGICA DE FLOTACIÓN (GRAVEDAD CERO) ---
        self.float_time += dt * FLOAT_SPEED

        # Desplazamiento suave en X e Y usando ondas senoidales desfasadas
        offset_y = math.sin(self.float_time) * FLOAT_AMPLITUDE_Y
        offset_x = math.cos(self.float_time * 0.7) * FLOAT_AMPLITUDE_X

        # Recuperación gradual del retroceso por impacto
        self.recoil_x *= 0.88

        # Aplicar nueva posición al rectángulo de colisión y dibujado
        self.rect.x = int(self.base_x + offset_x + self.recoil_x)
        self.rect.y = int(self.base_y + offset_y)

        # Oscilación angular sutil (cabeceo orbital)
        self.current_angle = math.sin(self.float_time * 0.85) * FLOAT_TILT_ANGLE

        # Control de parpadeo rojo
        if self.hit_timer > 0:
            self.hit_timer -= dt
            self.current_fill = MODULE_HIT_FILL
            self.current_border = MODULE_HIT_BORDER
        else:
            self.current_fill = MODULE_BASE_COLOR
            self.current_border = MODULE_BORDER_COLOR

    def draw(self, surface, font):
        # --- SALIDA VISUAL ---
        if self.sprite is not None:
            base_img = self.hit_sprite if self.hit_timer > 0 else self.sprite

            # Rotar suavemente manteniendo el centro del módulo fijo
            rotated_img = pygame.transform.rotate(base_img, self.current_angle)
            rotated_rect = rotated_img.get_rect(center=self.rect.center)
            surface.blit(rotated_img, rotated_rect.topleft)

            # Etiqueta debajo del módulo
            lbl_surf = font.render(self.name, True, TEXT_COLOR)
            lbl_rect = lbl_surf.get_rect(midtop=(self.rect.centerx, self.rect.bottom + 6))
            surface.blit(lbl_surf, lbl_rect)
        else:
            pygame.draw.rect(surface, self.current_fill, self.rect, border_radius=8)
            pygame.draw.rect(surface, self.current_border, self.rect, width=2, border_radius=8)

            text_surf = font.render(self.name, True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)