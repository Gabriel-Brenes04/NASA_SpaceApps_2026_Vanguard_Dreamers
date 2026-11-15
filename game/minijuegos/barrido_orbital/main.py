import os
import random
import pygame
from .settings import (
    WIDTH, HEIGHT, FPS, MODULES_CONFIG, SAMPLE_RATE,
    MAIN_FONT_SIZE, SMALL_FONT_SIZE, TINY_FONT_SIZE,FONT_PATH)
from .entities.module import StationModule
from .entities.particle import Particle
from .systems.detector import DetectorSystem
from .systems.orbit_manager import OrbitManager
from .systems.tutorial import TutorialScreen
from .systems.sound_manager import SoundManager

def reset_game(sound_manager):
    """Inicializa o reinicia todas las variables de estado de la partida."""
    modules = [StationModule(name, x, y, w, h, img_path) for name, x, y, w, h, img_path in MODULES_CONFIG]
    detector_system = DetectorSystem(sound_manager)
    orbit_manager = OrbitManager()
    sound_manager.reset()
    particles = []
    current_dose = 0.0
    score = 0
    return modules, detector_system, orbit_manager, particles, current_dose, score

def main(screen=None, cerrar_pygame=True):
    if screen is None:
        pygame.mixer.pre_init(SAMPLE_RATE, -16, 2, 512)
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Barrido de Radiación - Operador ISS")
    clock = pygame.time.Clock()

    # Cargar una única fuente en 3 tamaños sin abrir ventanas extra
    load_font = (lambda s: pygame.font.Font(FONT_PATH, s)) if os.path.exists(FONT_PATH) else (lambda s: pygame.font.SysFont("consolas", s + 4, bold=True))
    font = load_font(MAIN_FONT_SIZE)
    small_font = load_font(SMALL_FONT_SIZE)
    tiny_font = load_font(TINY_FONT_SIZE)

    # ==========================================
    # 2. VARIABLES DE SALIDA / ESTADO DEL JUEGO
    # ==========================================
    running = True
    sound_manager = SoundManager()
    tutorial = TutorialScreen(sound_manager)
    modules, detector_system, orbit_manager, particles, current_dose, score = reset_game(sound_manager)

    while running:
        # Captura de entradas del frame
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        click_pos = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif tutorial.active:
                tutorial.handle_event(event)
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_h:
                        tutorial.open()
                    elif event.key == pygame.K_r and orbit_manager.game_state != "PLAYING":
                        modules, detector_system, orbit_manager, particles, current_dose, score = reset_game(sound_manager)
                    else:
                        detector_system.handle_key(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click_pos = mouse_pos

        # ==========================================
        # 3. LÓGICA DEL CÓDIGO (Procesamiento)
        # ==========================================
        if not tutorial.active:
            orbit_manager.update(dt, current_dose)

            # Alarma sonora una vez al entrar a la Anomalía del Atlántico Sur
            if orbit_manager.in_saa and not sound_manager.saa_alarm_played:
                sound_manager.play("saa_alarm")
                sound_manager.saa_alarm_played = True

            if orbit_manager.game_state == "PLAYING":
                # A. Procesar detectores y clics
                detector_system.update(dt, mouse_pos, particles)
                if click_pos is not None:
                    pts, dose_saved = detector_system.process_click(click_pos, particles)
                    score += pts
                    current_dose = max(0.0, current_dose - dose_saved)

                # B. Generar nueva partícula según el estado de la órbita
                if orbit_manager.should_spawn:
                    chosen_target = random.choice(modules)
                    spawn_y = random.randint(95, HEIGHT - 110)
                    particles.append(Particle(WIDTH + 20, spawn_y, orbit_manager.next_particle_type, chosen_target))

                # C. Actualizar módulos y partículas
                for mod in modules:
                    mod.update(dt)

                for p in particles[:]:
                    p.update(dt)
                    if p.has_collided:
                        current_dose += p.dose
                        p.target.take_hit()
                        detector_system.spawn_explosion(p.x, p.y, (255, 70, 90), count=18)
                        sound_manager.play("hit")
                        particles.remove(p)

        # ==========================================
        # 4. SALIDA VISUAL (Renderizado)
        # ==========================================
        screen.fill(orbit_manager.current_bg_color)

        for mod in modules:
            mod.draw(screen, small_font)

        for p in particles:
            p.draw(screen)

        detector_system.draw(screen, font, small_font, mouse_pos)
        orbit_manager.draw_hud(screen, font, small_font, current_dose, score)
        orbit_manager.draw_end_screen(screen, font, small_font, current_dose, score)
        tutorial.draw(screen, font, small_font)

        pygame.display.flip()


    if cerrar_pygame:
        pygame.quit()

if __name__ == "__main__":
    main()