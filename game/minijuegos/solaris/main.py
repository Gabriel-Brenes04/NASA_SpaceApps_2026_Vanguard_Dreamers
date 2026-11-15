import math
import os
import random
import pygame

from . import settings as S
from .systems.solar_system import SolarSystem
from .systems.energy_manager import EnergyManager


FIN_ESPERA = 4.0      # segundos que se ve la pantalla final antes de volver a Mission Survival


class SolarisGame:
    def __init__(self, screen=None):
        if screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((S.WIDTH, S.HEIGHT))
        else:
            self.screen = screen
        pygame.display.set_caption("SOLARIS - Operacion Helios")
        self.clock = pygame.time.Clock()
        self.font = self.load_font(14)
        self.small = self.load_font(10)
        self.tiny = self.load_font(8)
        self.state = "PLAYING"        # sin pantalla de inicio: se juega de una vez
        self.running = True
        self.reset()

    def load_font(self, size):
        if os.path.exists(S.FONT_PATH):
            return pygame.font.Font(S.FONT_PATH, size)
        return pygame.font.SysFont("consolas", size, bold=True)

    def reset(self):
        self.solar = SolarSystem()
        self.energy = EnergyManager()
        self.elapsed = 0.0
        self.fin_timer = 0.0
        self.score = 0
        self.message_timer = 0.0
        self.message = ""
        self.stars = [(random.randrange(S.WIDTH), random.randrange(S.HEIGHT), random.choice((1, 1, 2))) for _ in range(100)]

    def text(self, value, x, y, color=S.WHITE, font=None, center=False):
        font = font or self.small
        image = font.render(str(value), True, color)
        rect = image.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(image, rect)

    def panel(self, rect, fill=(12, 24, 43), border=(42, 76, 108)):
        pygame.draw.rect(self.screen, fill, rect, border_radius=8)
        pygame.draw.rect(self.screen, border, rect, 1, border_radius=8)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if self.state == "PLAYING":
                if event.key == pygame.K_ESCAPE:
                    self.running = False          # ESC: volver al juego principal
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.solar.rotate_selected(-4)
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.solar.rotate_selected(4)
                elif event.key == pygame.K_q:
                    self.solar.rotate_selected(-15)
                elif event.key == pygame.K_e:
                    self.solar.rotate_selected(15)
                elif event.key == pygame.K_TAB:
                    self.solar.select_at((self.solar.panels[(self.solar.selected + 1) % len(self.solar.panels)].x,
                                          self.solar.panels[(self.solar.selected + 1) % len(self.solar.panels)].y))
            elif self.state in ("WON", "LOST"):
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    self.running = False          # salir sin esperar
        elif event.type == pygame.MOUSEBUTTONDOWN and self.state == "PLAYING":
            if event.button == 1:
                self.solar.select_at(event.pos)
            elif event.button == 4:
                self.solar.rotate_selected(4)
            elif event.button == 5:
                self.solar.rotate_selected(-4)

    def update(self, dt):
        if self.state in ("WON", "LOST"):
            self.fin_timer += dt
            if self.fin_timer >= FIN_ESPERA:
                self.running = False              # sale solo, sin necesidad de ESC
            return
        if self.state != "PLAYING":
            return
        self.elapsed += dt
        self.solar.update(dt, self.elapsed)
        self.energy.update(dt, self.solar.production_kw())
        self.score += int(self.solar.production_kw() * dt)
        if self.energy.blackout:
            self.state = "LOST"
        elif self.elapsed >= S.GAME_DURATION:
            self.state = "WON"
        if self.message_timer > 0:
            self.message_timer -= dt

    def draw_background(self):
        self.screen.fill(S.BG)
        for x in range(0, S.WIDTH, 40):
            pygame.draw.line(self.screen, S.BG_GRID, (x, 0), (x, S.HEIGHT), 1)
        for y in range(0, S.HEIGHT, 40):
            pygame.draw.line(self.screen, S.BG_GRID, (0, y), (S.WIDTH, y), 1)
        for x, y, radius in self.stars:
            self.screen.set_at((x, y), (75, 105, 140) if radius == 1 else (115, 145, 175))

    def draw_hud(self):
        self.panel((18, 14, 988, 78))
        self.text("SOLARIS / OPERACION HELIOS", 34, 25, S.CYAN, self.small)
        remaining = max(0, int(S.GAME_DURATION - self.elapsed))
        self.text(f"TIEMPO  {remaining // 60:02}:{remaining % 60:02}", 34, 49, S.WHITE, self.small)
        self.text(f"PUNTOS  {self.score:06}", 280, 49, S.YELLOW, self.small)
        self.text(f"GENERACION  {self.energy.production:5.1f} kW", 520, 25, S.GREEN, self.small)
        self.text(f"CONSUMO  {self.energy.consumption:.0f} kW", 520, 49, S.MUTED, self.small)
        self.text(f"BATERIA  {self.energy.battery:4.0f}%", 790, 25, S.WHITE, self.small)
        bar = pygame.Rect(790, 48, 190, 13)
        pygame.draw.rect(self.screen, (35, 49, 68), bar, border_radius=5)
        fill = max(0, int(bar.width * self.energy.battery / S.BATTERY_CAPACITY))
        color = S.GREEN if self.energy.battery > 35 else S.YELLOW if self.energy.battery > 15 else S.RED
        pygame.draw.rect(self.screen, color, (bar.x, bar.y, fill, bar.height), border_radius=5)
        pygame.draw.rect(self.screen, (110, 135, 160), bar, 1, border_radius=5)

    def draw_controls(self):
        self.panel((18, 574, 988, 48))
        self.text("CLIC: SELECCIONAR PANEL", 32, 591, S.WHITE, self.tiny)
        self.text("A / D o FLECHAS: ROTAR", 315, 591, S.WHITE, self.tiny)
        self.text("Q / E: GIRO RAPIDO", 585, 591, S.WHITE, self.tiny)
        self.text("ESC: SALIR", 830, 591, S.MUTED, self.tiny)

    def draw_playing(self):
        self.solar.draw(self.screen, self.small, self.tiny)
        self.draw_hud()
        self.draw_controls()
        selected = self.solar.panels[self.solar.selected]
        self.text(f"PANEL ACTIVO: {selected.name}  |  ORIENTACION: {selected.angle:05.1f} grados",
                  S.WIDTH // 2, 548, S.CYAN, self.tiny, center=True)
        if self.solar.in_shadow:
            self.text("La estacion esta en sombra: utiliza la energia almacenada.", S.WIDTH // 2, 135, S.ORANGE, self.tiny, center=True)
        elif self.solar.storm_active:
            self.text("La tormenta solar reduce temporalmente la eficiencia de los paneles.", S.WIDTH // 2, 135, S.YELLOW, self.tiny, center=True)

    def draw_end(self):
        self.panel((190, 190, 644, 250), (9, 20, 37), S.CYAN if self.state == "WON" else S.RED)
        title = "OPERACION COMPLETADA" if self.state == "WON" else "FALLO ENERGETICO"
        color = S.GREEN if self.state == "WON" else S.RED
        self.text(title, S.WIDTH // 2, 235, color, self.small, center=True)
        self.text(f"PUNTUACION: {self.score}", S.WIDTH // 2, 290, S.WHITE, self.small, center=True)
        self.text(f"ENERGIA FINAL: {self.energy.battery:.1f}%", S.WIDTH // 2, 325, S.WHITE, self.small, center=True)
        faltan = max(0, int(FIN_ESPERA - self.fin_timer) + 1)
        self.text(f"VOLVIENDO A MISSION SURVIVAL EN {faltan} s", S.WIDTH // 2, 375, S.GREEN, self.tiny, center=True)
        self.text("ENTER: SALIR YA", S.WIDTH // 2, 405, S.MUTED, self.tiny, center=True)

    def draw(self):
        self.draw_background()
        if self.state == "PLAYING":
            self.draw_playing()
        else:
            self.solar.draw(self.screen, self.small, self.tiny)
            self.draw_hud()
            self.draw_end()
        pygame.display.flip()

    def run(self, cerrar_pygame=True):
        while self.running:
            dt = min(self.clock.tick(S.FPS) / 1000.0, 0.05)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()
        if cerrar_pygame:
            pygame.quit()


def main(screen=None, cerrar_pygame=True):
    juego = SolarisGame(screen)
    juego.run(cerrar_pygame)


if __name__ == "__main__":
    main()