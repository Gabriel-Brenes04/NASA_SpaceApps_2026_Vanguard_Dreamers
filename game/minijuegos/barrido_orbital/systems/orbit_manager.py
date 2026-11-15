import random
import pygame
from ..settings import (
    WIDTH, HEIGHT, BG_COLOR, SAA_BG_COLOR, TEXT_COLOR,
    ORBIT_DURATION, SAA_START, SAA_END, MAX_DOSE,
    NORMAL_SPAWN_INTERVAL, SAA_SPAWN_INTERVAL,
    NORMAL_WEIGHTS, SAA_WEIGHTS, PARTICLE_TYPES
)

class OrbitManager:
    def __init__(self):
        # --- VARIABLES DE ENTRADA ---
        self.duration = ORBIT_DURATION
        self.saa_start = SAA_START
        self.saa_end = SAA_END
        self.max_dose = MAX_DOSE
        self.particle_keys = list(PARTICLE_TYPES.keys())

        # --- VARIABLES DE SALIDA (Estado de la partida) ---
        self.elapsed_time = 0.0
        self.in_saa = False
        self.game_state = "PLAYING"  # Estados: "PLAYING", "VICTORY", "GAME_OVER"
        self.current_bg_color = BG_COLOR
        self.spawn_timer = 0.0
        self.should_spawn = False
        self.next_particle_type = "electron"
        self.final_rank = "C"

    def update(self, dt, current_dose):
        # --- LÓGICA DEL CICLO DE ÓRBITA ---
        self.should_spawn = False

        if self.game_state != "PLAYING":
            return

        # 1. Verificar condición de derrota
        if current_dose >= self.max_dose:
            self.game_state = "GAME_OVER"
            return

        # 2. Avanzar reloj de órbita y verificar victoria
        self.elapsed_time += dt
        if self.elapsed_time >= self.duration:
            self.elapsed_time = self.duration
            self.final_rank = self._calculate_rank(current_dose)
            self.game_state = "VICTORY"
            return

        # 3. Verificar si estamos dentro de la Anomalía del Atlántico Sur (SAA)
        self.in_saa = (self.saa_start <= self.elapsed_time <= self.saa_end)
        self.current_bg_color = SAA_BG_COLOR if self.in_saa else BG_COLOR

        # 4. Controlar temporizador de generación de partículas
        interval = SAA_SPAWN_INTERVAL if self.in_saa else NORMAL_SPAWN_INTERVAL
        weights = SAA_WEIGHTS if self.in_saa else NORMAL_WEIGHTS

        self.spawn_timer += dt
        if self.spawn_timer >= interval:
            self.spawn_timer = 0.0
            self.should_spawn = True
            self.next_particle_type = random.choices(self.particle_keys, weights=weights, k=1)[0]

    def _calculate_rank(self, current_dose):
        if current_dose <= 15.0:
            return "S (OPERADOR ÉLITE)"
        elif current_dose <= 40.0:
            return "A (ÓRBITA SEGURA)"
        elif current_dose <= 70.0:
            return "B (DOSIS MODERADA)"
        else:
            return "C (LÍMITE CRÍTICO)"

    def draw_hud(self, surface, font, small_font, current_dose, score):
        # --- SALIDA VISUAL: HUD SUPERIOR ---
        # Barra superior oscura de fondo
        pygame.draw.rect(surface, (15, 20, 35), (0, 0, WIDTH, 68))
        pygame.draw.line(surface, (50, 75, 110), (0, 68), (WIDTH, 68), 2)

        # 1. Izquierda: Barra de Dosis Acumulada
        dose_ratio = min(1.0, current_dose / self.max_dose)
        bar_x, bar_y, bar_w, bar_h = 20, 34, 240, 20

        if dose_ratio < 0.4:
            bar_color = (50, 220, 130)
        elif dose_ratio < 0.75:
            bar_color = (255, 200, 0)
        else:
            bar_color = (255, 50, 80)

        lbl_dose = small_font.render(f"DOSIS ACUMULADA: {current_dose:.1f} / {int(self.max_dose)} mSv", True, TEXT_COLOR)
        surface.blit(lbl_dose, (bar_x, 12))
        pygame.draw.rect(surface, (30, 38, 55), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        pygame.draw.rect(surface, bar_color, (bar_x, bar_y, int(bar_w * dose_ratio), bar_h), border_radius=4)
        pygame.draw.rect(surface, (120, 140, 170), (bar_x, bar_y, bar_w, bar_h), width=1, border_radius=4)

        # 2. Centro: Progreso de Órbita con marcador de SAA
        orb_x, orb_y, orb_w, orb_h = 340, 34, 340, 20
        orb_ratio = self.elapsed_time / self.duration

        lbl_orb = small_font.render(f"PROGRESO DE ÓRBITA: {int(self.elapsed_time)}s / {int(self.duration)}s", True, TEXT_COLOR)
        surface.blit(lbl_orb, (orb_x, 12))
        pygame.draw.rect(surface, (30, 38, 55), (orb_x, orb_y, orb_w, orb_h), border_radius=4)

        # Zona roja señalando la Anomalía del Atlántico Sur en la barra
        saa_x_start = orb_x + int(orb_w * (self.saa_start / self.duration))
        saa_width = int(orb_w * ((self.saa_end - self.saa_start) / self.duration))
        pygame.draw.rect(surface, (140, 35, 60), (saa_x_start, orb_y, saa_width, orb_h))

        # Indicador actual de la ISS
        cursor_x = orb_x + int(orb_w * orb_ratio)
        pygame.draw.line(surface, (0, 240, 255), (cursor_x, orb_y - 3), (cursor_x, orb_y + orb_h + 3), 3)
        pygame.draw.rect(surface, (120, 140, 170), (orb_x, orb_y, orb_w, orb_h), width=1, border_radius=4)

        # Alerta parpadeante durante la SAA
        if self.in_saa and int(self.elapsed_time * 4) % 2 == 0:
            warn_surf = small_font.render("[!] ALERTA: ANOMALIA DEL ATLANTICO SUR (SAA) [!]", True, (255, 90, 110))
            surface.blit(warn_surf, (WIDTH // 2 - warn_surf.get_width() // 2, 78))

        # 3. Derecha: Puntuación
        score_surf = font.render(f"SCORE: {score}", True, (255, 220, 80))
        surface.blit(score_surf, (WIDTH - score_surf.get_width() - 25, 24))

    def draw_end_screen(self, surface, font, small_font, current_dose, score):
        # --- SALIDA VISUAL: PANTALLA FINAL ---
        if self.game_state == "PLAYING":
            return

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 12, 22, 215))
        surface.blit(overlay, (0, 0))

        if self.game_state == "VICTORY":
            title = font.render("¡ÓRBITA COMPLETADA CON ÉXITO!", True, (50, 230, 140))
            sub1 = font.render(f"RANGO FINAL: {self.final_rank}", True, (255, 220, 80))
            sub2 = small_font.render(f"Dosis Final: {current_dose:.1f} mSv   |   Puntuación: {score}", True, TEXT_COLOR)
        else:
            title = font.render("MISIÓN ABORTADA: DOSIS CRÍTICA ALCANZADA", True, (255, 60, 80))
            sub1 = font.render("Los módulos excedieron el límite seguro de radiación.", True, TEXT_COLOR)
            sub2 = small_font.render(f"Tiempo sobrevivido: {int(self.elapsed_time)}s   |   Puntuación: {score}", True, TEXT_COLOR)

        restart_msg = small_font.render("Presiona [R] para iniciar una nueva órbita o [ESC] para salir", True, (150, 180, 220))

        surface.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
        surface.blit(sub1, sub1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10)))
        surface.blit(sub2, sub2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))
        surface.blit(restart_msg, restart_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 90)))