import math
import random
import pygame
from ..settings import (
    DETECTORS_CONFIG, HEAVY_ION_NAMES, WIDTH, HEIGHT,
    EXPLOSION_PARTICLE_COUNT, EXPLOSION_SPEED_MIN,
    EXPLOSION_SPEED_MAX, EXPLOSION_LIFETIME
)

class DetectorSystem:
    def __init__(self, sound_manager=None):
        # --- VARIABLES DE ENTRADA ---
        self.config = DETECTORS_CONFIG
        self.detector_names = list(self.config.keys())
        self.sound = sound_manager

        # --- VARIABLES DE SALIDA (Estado del sistema) ---
        self.active_detector = "LIULIN"
        self.cooldown_timer = 0.0
        self.floating_texts = []  # {text, x, y, color, timer}
        self.pulse_effects = []   # {x, y, radius, color, timer}
        self.sparks = []          # Chispas de explosión: {x, y, vx, vy, color, radius, timer, max_timer}
        self.buttons = self._create_ui_buttons()

    def _create_ui_buttons(self):
        buttons = {}
        btn_width, btn_height = 290, 44
        spacing = 25
        total_w = (btn_width * 3) + (spacing * 2)
        start_x = (WIDTH - total_w) // 2
        y = HEIGHT - 58

        for i, name in enumerate(self.detector_names):
            rect = pygame.Rect(start_x + i * (btn_width + spacing), y, btn_width, btn_height)
            buttons[name] = rect
        return buttons

    def spawn_explosion(self, x, y, color, count=EXPLOSION_PARTICLE_COUNT):
        """Genera una explosión radial de chispas en (x, y)."""
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(EXPLOSION_SPEED_MIN, EXPLOSION_SPEED_MAX)
            life = random.uniform(EXPLOSION_LIFETIME * 0.6, EXPLOSION_LIFETIME)
            self.sparks.append({
                "x": float(x),
                "y": float(y),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "color": color,
                "radius": random.randint(2, 5),
                "timer": life,
                "max_timer": life
            })

    def select_detector(self, detector_name):
        if detector_name in self.config and self.active_detector != detector_name:
            self.active_detector = detector_name
            if self.sound:
                self.sound.play("switch")

    def handle_key(self, key):
        # --- LÓGICA DE TECLADO ---
        if key == pygame.K_1:
            self.select_detector("LIULIN")
        elif key == pygame.K_2:
            self.select_detector("TIMEPIX")
        elif key == pygame.K_3:
            self.select_detector("ALTEA")

    def update(self, dt, mouse_pos, particles):
        # --- LÓGICA PASIVA (Por cada frame) ---
        if self.cooldown_timer > 0:
            self.cooldown_timer = max(0.0, self.cooldown_timer - dt)

        is_timepix = (self.active_detector == "TIMEPIX")
        slow_radius = self.config["TIMEPIX"]["slow_radius"]
        mx, my = mouse_pos

        for p in particles:
            p.revealed_track = is_timepix
            if is_timepix and math.hypot(p.x - mx, p.y - my) <= slow_radius:
                p.slowed = True
            else:
                p.slowed = False

        # Actualizar textos flotantes
        for ft in self.floating_texts[:]:
            ft["y"] -= 35 * dt
            ft["timer"] -= dt
            if ft["timer"] <= 0:
                self.floating_texts.remove(ft)

        # Actualizar ondas de pulso
        for pe in self.pulse_effects[:]:
            pe["timer"] -= dt
            if pe["timer"] <= 0:
                self.pulse_effects.remove(pe)

        # Actualizar chispas de explosión (con fricción suave)
        for sp in self.sparks[:]:
            sp["x"] += sp["vx"] * dt
            sp["y"] += sp["vy"] * dt
            sp["vx"] *= 0.94
            sp["vy"] *= 0.94
            sp["timer"] -= dt
            if sp["timer"] <= 0:
                self.sparks.remove(sp)

    def process_click(self, click_pos, particles):
        # --- ENTRADAS DE CLIC ---
        points_earned = 0
        dose_reduced = 0.0

        for name, rect in self.buttons.items():
            if rect.collidepoint(click_pos):
                self.select_detector(name)
                return points_earned, dose_reduced

        if self.cooldown_timer > 0:
            return points_earned, dose_reduced

        # --- LÓGICA DE DETECCIÓN SEGÚN INSTRUMENTO ---
        det_data = self.config[self.active_detector]
        cx, cy = click_pos

        if self.active_detector == "LIULIN":
            aoe = det_data["aoe_radius"]
            self.pulse_effects.append({"x": cx, "y": cy, "radius": aoe, "color": det_data["color"], "timer": 0.2})
            hit_any = False

            for p in reversed(particles):
                if math.hypot(p.x - cx, p.y - cy) <= (aoe + p.radius):
                    hit_any = True
                    pts = p.points * 2 if p.ideal_detector == "LIULIN" else p.points
                    points_earned += pts
                    if p.ideal_detector == "LIULIN":
                        dose_reduced += det_data["dose_reduction"]
                    # Explosión al detectar
                    self.spawn_explosion(p.x, p.y, p.color)
                    particles.remove(p)

            if hit_any:
                if self.sound:
                    self.sound.play("liulin")
                self.cooldown_timer = det_data["cooldown"]
                msg = f"+{points_earned} PTS" + (f" (-{dose_reduced:.1f} mSv)" if dose_reduced > 0 else "")
                self.floating_texts.append({"text": msg, "x": cx, "y": cy, "color": det_data["color"], "timer": 0.8})

        elif self.active_detector == "TIMEPIX":
            for p in reversed(particles):
                if p.is_clicked(click_pos):
                    pts = p.points * 2 if p.ideal_detector == "TIMEPIX" else p.points
                    points_earned += pts
                    self.cooldown_timer = det_data["cooldown"]
                    self.floating_texts.append({"text": f"+{pts} PTS", "x": p.x, "y": p.y, "color": det_data["color"], "timer": 0.8})
                    # Explosión al detectar
                    self.spawn_explosion(p.x, p.y, p.color)
                    if self.sound:
                        self.sound.play("timepix")
                    particles.remove(p)
                    break

        elif self.active_detector == "ALTEA":
            for p in reversed(particles):
                if p.is_clicked(click_pos):
                    if p.ideal_detector == "ALTEA":
                        pts = p.points * det_data["ion_multiplier"]
                        ion_name = random.choice(HEAVY_ION_NAMES)
                        label = f"{ion_name} +{pts}!"
                        # Explosión extra grande para iones pesados
                        self.spawn_explosion(p.x, p.y, p.color, count=EXPLOSION_PARTICLE_COUNT * 2)
                    else:
                        pts = p.points
                        label = f"+{pts} PTS"
                        self.spawn_explosion(p.x, p.y, p.color)

                    points_earned += pts
                    self.cooldown_timer = det_data["cooldown"]
                    self.floating_texts.append({"text": label, "x": p.x, "y": p.y, "color": det_data["color"], "timer": 1.0})
                    if self.sound:
                        self.sound.play("altea" if p.ideal_detector == "ALTEA" else "timepix")
                    particles.remove(p)
                    break

        # --- SALIDAS ---
        return points_earned, dose_reduced

    def draw(self, surface, font, small_font, mouse_pos):
        # --- SALIDA VISUAL ---
        det_data = self.config[self.active_detector]
        mx, my = mouse_pos

        # 1. Chispas de explosión (se encogen y desvanecen al morir)
        for sp in self.sparks:
            life_ratio = max(0.0, sp["timer"] / sp["max_timer"])
            current_radius = max(1, int(sp["radius"] * life_ratio))
            pos = (int(sp["x"]), int(sp["y"]))
            pygame.draw.circle(surface, sp["color"], pos, current_radius)
            if current_radius >= 2:
                pygame.draw.circle(surface, (255, 255, 255), pos, max(1, current_radius // 2))

        # 2. Retícula del detector activo
        if self.active_detector == "LIULIN":
            pygame.draw.circle(surface, det_data["color"], (mx, my), det_data["aoe_radius"], width=1)
        elif self.active_detector == "TIMEPIX":
            pygame.draw.circle(surface, det_data["color"], (mx, my), det_data["slow_radius"], width=1)
        elif self.active_detector == "ALTEA":
            pygame.draw.line(surface, det_data["color"], (mx - 15, my), (mx + 15, my), 2)
            pygame.draw.line(surface, det_data["color"], (mx, my - 15), (mx, my + 15), 2)

        # 3. Ondas de pulso de Liulin
        for pe in self.pulse_effects:
            pygame.draw.circle(surface, pe["color"], (pe["x"], pe["y"]), pe["radius"], width=2)

        # 4. Textos flotantes
        for ft in self.floating_texts:
            txt_surf = small_font.render(ft["text"], True, ft["color"])
            surface.blit(txt_surf, (int(ft["x"] - txt_surf.get_width() // 2), int(ft["y"])))

        # 5. Barra inferior de botones
        for name, rect in self.buttons.items():
            cfg = self.config[name]
            is_selected = (name == self.active_detector)
            bg = (35, 50, 75) if is_selected else (18, 24, 38)
            border_w = 3 if is_selected else 1

            pygame.draw.rect(surface, bg, rect, border_radius=6)
            pygame.draw.rect(surface, cfg["color"], rect, width=border_w, border_radius=6)

            lbl = small_font.render(cfg["label"], True, cfg["color"] if is_selected else (160, 175, 195))
            surface.blit(lbl, lbl.get_rect(center=rect.center))
            