import os
import random
import pygame

from . import settings as S
from .systems.solar_system import SolarSystem
from .systems.energy_manager import EnergyManager
from ...assets import sonido


INSTRUCCION = "Rota los paneles con la rueda del mouse o las flechas de tu teclado!"
FIN_ESPERA = 2.5      # segundos que se ve la cajita final antes de volver a Mission Survival
BATERIA_BAJA = 20.0   # por debajo de este % suena la alarma


def suena(nombre, vol=1.0):
    if sonido is not None:
        sonido.play(nombre, vol)


class SolarisGame:
    def __init__(self, screen=None):
        if screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((S.WIDTH, S.HEIGHT))
        else:
            self.screen = screen
        pygame.display.set_caption("SOLARIS - Operacion Helios")
        self.clock = pygame.time.Clock()
        self.big = self.load_font(18)
        self.font = self.load_font(13)
        self.small = self.load_font(10)
        self.tiny = self.load_font(8)
        if sonido is not None and not sonido.ACTIVO:
            sonido.iniciar()
        self.running = True
        pygame.key.set_repeat(200, 40)
        self.reset()

    def load_font(self, size):
        if os.path.exists(S.FONT_PATH):
            return pygame.font.Font(S.FONT_PATH, size)
        return pygame.font.SysFont("consolas", size, bold=True)

    def reset(self):
        self.solar = SolarSystem()
        self.energy = EnergyManager()
        self.elapsed = 0.0
        self.score = 0.0
        self.state = "PLAYING"            # PLAYING, WON o LOST
        self.fin_timer = 0.0
        self.alarma_timer = 0.0
        self.ultimo_segundo = int(S.GAME_DURATION)
        self.stars = [(random.randrange(S.WIDTH), random.randrange(S.HEIGHT), random.choice((1, 1, 2))) for _ in range(100)]
        suena("ya", 0.8)

    # ── controles ────────────────────────────────────────────────────────────────
    def rotar(self, grados):
        panel = self.solar.panels[self.solar.selected]
        antes = panel.efficiency
        self.solar.rotate_selected(grados)
        despues = panel.get_efficiency(self.solar.sun_x, self.solar.sun_y)
        suena("click", 0.6)
        if antes < 0.8 <= despues:
            suena("bien", 0.7)            # el panel quedó bien apuntado al sol (pasa a verde)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if self.state != "PLAYING":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    self.running = False      # salir sin esperar
            elif event.key == pygame.K_ESCAPE:
                self.running = False          # ESC: volver al juego principal
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.rotar(-2)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.rotar(2)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.state == "PLAYING":
            if event.button == 1:
                if self.solar.select_at(event.pos):
                    suena("clac", 0.6)
            elif event.button == 4:
                self.rotar(2)
            elif event.button == 5:
                self.rotar(-2)

    # ── lógica ───────────────────────────────────────────────────────────────────
    def update(self, dt):
        if self.state != "PLAYING":
            self.fin_timer += dt
            if self.fin_timer >= FIN_ESPERA:
                self.running = False          # vuelve solo al juego principal
            return
        self.elapsed += dt
        self.solar.update(dt, self.elapsed)
        produccion = self.solar.production_kw()
        self.energy.update(dt, produccion)
        self.score += produccion * dt

        # alarma mientras la batería está baja
        if self.energy.battery < BATERIA_BAJA:
            self.alarma_timer -= dt
            if self.alarma_timer <= 0:
                suena("alarma", 0.6)
                self.alarma_timer = 1.0
        else:
            self.alarma_timer = 0.0

        # cuenta regresiva de los últimos 3 segundos
        quedan = int(S.GAME_DURATION - self.elapsed)
        if quedan != self.ultimo_segundo:
            self.ultimo_segundo = quedan
            if 0 <= quedan < 3:
                suena("cuenta", 0.7)

        if self.energy.blackout:
            self.state = "LOST"
            suena("derrota")
        elif self.elapsed >= S.GAME_DURATION:
            self.state = "WON"
            suena("victoria")
        if self.state != "PLAYING" and sonido is not None:
            sonido.parar_bucles()

    # ── dibujo ───────────────────────────────────────────────────────────────────
    def draw_background(self):
        self.screen.fill(S.BG)
        for x in range(0, S.WIDTH, 40):
            pygame.draw.line(self.screen, S.BG_GRID, (x, 0), (x, S.HEIGHT), 1)
        for y in range(0, S.HEIGHT, 40):
            pygame.draw.line(self.screen, S.BG_GRID, (0, y), (S.WIDTH, y), 1)
        for x, y, radius in self.stars:
            self.screen.set_at((x, y), (75, 105, 140) if radius == 1 else (115, 145, 175))

    def text(self, value, y, color, font):
        image = font.render(str(value), True, color)
        self.screen.blit(image, image.get_rect(center=(S.WIDTH // 2, y)))

    def draw_battery(self):
        bateria = self.energy.battery
        color = S.GREEN if bateria > 35 else S.YELLOW if bateria > BATERIA_BAJA else S.RED
        self.text(f"BATERIA {bateria:3.0f}%", S.HEIGHT - 50, color, self.small)
        barra = pygame.Rect(0, 0, 260, 14)
        barra.center = (S.WIDTH // 2, S.HEIGHT - 28)
        pygame.draw.rect(self.screen, (35, 49, 68), barra, border_radius=5)
        lleno = max(0, int(barra.width * bateria / S.BATTERY_CAPACITY))
        pygame.draw.rect(self.screen, color, (barra.x, barra.y, lleno, barra.height), border_radius=5)
        pygame.draw.rect(self.screen, (110, 135, 160), barra, 1, border_radius=5)

    def draw_end(self):
        gano = self.state == "WON"
        caja = pygame.Rect(0, 0, 480, 170)
        caja.center = (S.WIDTH // 2, S.HEIGHT // 2)
        pygame.draw.rect(self.screen, (9, 20, 37), caja, border_radius=10)
        pygame.draw.rect(self.screen, S.CYAN if gano else S.RED, caja, 2, border_radius=10)
        self.text("OPERACION COMPLETADA" if gano else "FALLO ENERGETICO", caja.top + 55,
                  S.GREEN if gano else S.RED, self.big)
        self.text(f"PUNTUACION: {int(self.score)}", caja.top + 115, S.WHITE, self.font)

    def draw(self):
        self.draw_background()
        self.solar.draw(self.screen, self.small, self.font)
        image = self.font.render(INSTRUCCION, True, S.WHITE)
        self.screen.blit(image, image.get_rect(midtop=(S.WIDTH // 2, 20)))
        self.draw_battery()
        quedan = max(0, int(S.GAME_DURATION - self.elapsed + 0.999))
        self.text(f"TIEMPO {quedan // 60:02}:{quedan % 60:02}", 62, S.RED if quedan <= 5 else S.YELLOW, self.big)
        if self.state != "PLAYING":
            self.draw_end()
        pygame.display.flip()

    def run(self, cerrar_pygame=True):
        while self.running:
            dt = min(self.clock.tick(S.FPS) / 1000.0, 0.05)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()
        if sonido is not None:
            sonido.parar_bucles()
        if cerrar_pygame:
            pygame.quit()


def main(screen=None, cerrar_pygame=True):
    juego = SolarisGame(screen)
    juego.run(cerrar_pygame)


if __name__ == "__main__":
    main()
