import pygame
from ..settings import WIDTH, HEIGHT, TEXT_COLOR, PARTICLE_TYPES, DETECTORS_CONFIG

class TutorialScreen:
    def __init__(self, sound_manager=None):
        # --- VARIABLES DE ENTRADA ---
        self.sound = sound_manager
        self.pages = [
            {
                "title": "MISION: OPERADOR DE RADIACION ISS (1/3)",
                "subtitle": "Protege los modulos Columbus, US Lab y SM",
                "items": [
                    ("OBJETIVO:", "Sobrevive 15s de orbita manteniendo la dosis bajo 100 mSv.", TEXT_COLOR),
                    ("PARTICULAS:", "Vuelan desde el espacio hacia los modulos de la estacion.", TEXT_COLOR),
                    ("IMPACTO:", "Si tocan un modulo, la dosis acumulada sube.", (255, 90, 110)),
                    ("CONTROLES:", "Usa [1], [2], [3] o clic abajo para cambiar detector.", (0, 220, 255)),
                ],
                "show_particles": True
            },
            {
                "title": "INSTRUMENTOS CIENTIFICOS (2/3)",
                "subtitle": "Cada detector tiene una especialidad tactica",
                "items": [
                    ("[1] LIULIN:", "Barrido en AREA. Ideal para Electrones (Cian) y baja dosis.", DETECTORS_CONFIG["LIULIN"]["color"]),
                    ("[2] TIMEPIX:", "Muestra TRACKS completos y ralentiza cerca del cursor.", DETECTORS_CONFIG["TIMEPIX"]["color"]),
                    ("[3] ALTEA:", "Precision x3 PUNTOS en Iones Pesados (Rojo) e identifica ion.", DETECTORS_CONFIG["ALTEA"]["color"]),
                    ("CONSEJO:", "Combina instrumentos segun el color de la oleada.", TEXT_COLOR),
                ],
                "show_particles": False
            },
            {
                "title": "ANOMALIA DEL ATLANTICO SUR - SAA (3/3)",
                "subtitle": "Peligro maximo entre los segundos 40s y 65s",
                "items": [
                    ("ZONA ROJA:", "Observa la marca roja en la barra superior de orbita.", (255, 90, 110)),
                    ("TORMENTA:", "En la SAA la pantalla se tine de rojo y caen mas iones.", (255, 200, 0)),
                    ("ESTRATEGIA:", "Usa Timepix para ver rutas y ALTEA para frenar iones pesados.", (0, 220, 255)),
                    ("AYUDA:", "Puedes abrir este tutorial en partida con la tecla [H].", (150, 180, 220)),
                ],
                "show_particles": False
            }
        ]

        # --- VARIABLES DE SALIDA (Estado del tutorial) ---
        self.active = True
        self.current_page = 0
        self.btn_next = pygame.Rect(WIDTH // 2 + 40, HEIGHT - 110, 220, 44)
        self.btn_prev = pygame.Rect(WIDTH // 2 - 260, HEIGHT - 110, 220, 44)

    def open(self):
        self.active = True
        self.current_page = 0

    def handle_event(self, event):
        # --- LÓGICA DE NAVEGACIÓN ---
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RIGHT, pygame.K_SPACE, pygame.K_RETURN):
                self._next_page()
            elif event.key == pygame.K_LEFT:
                self._prev_page()
            elif event.key == pygame.K_ESCAPE:
                self.active = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.btn_next.collidepoint(pos):
                self._next_page()
            elif self.btn_prev.collidepoint(pos) and self.current_page > 0:
                self._prev_page()

    def _next_page(self):
        if self.current_page < len(self.pages) - 1:
            if self.sound:
                self.sound.play("ui_page")
            self.current_page += 1
        else:
            if self.sound:
                self.sound.play("ui_page")
            self.active = False

    def _prev_page(self):
        if self.current_page > 0:
            if self.sound:
                self.sound.play("ui_page")
            self.current_page -= 1

    def draw(self, surface, font, small_font):
        # --- SALIDA VISUAL ---
        if not self.active:
            return

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 12, 22, 235))
        surface.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(70, 55, WIDTH - 140, HEIGHT - 110)
        pygame.draw.rect(surface, (18, 26, 44), panel_rect, border_radius=12)
        pygame.draw.rect(surface, (0, 220, 255), panel_rect, width=2, border_radius=12)

        page_data = self.pages[self.current_page]

        title_surf = font.render(page_data["title"], True, (0, 220, 255))
        sub_surf = small_font.render(page_data["subtitle"], True, (255, 220, 80))
        surface.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 105)))
        surface.blit(sub_surf, sub_surf.get_rect(center=(WIDTH // 2, 140)))

        pygame.draw.line(surface, (50, 75, 110), (110, 165), (WIDTH - 110, 165), 2)

        start_y = 195
        for tag, desc, color in page_data["items"]:
            tag_surf = small_font.render(tag, True, color)
            desc_surf = small_font.render(desc, True, TEXT_COLOR)
            surface.blit(tag_surf, (115, start_y))
            surface.blit(desc_surf, (265, start_y))
            start_y += 48

        if page_data["show_particles"]:
            demo_y = 415
            demos = [
                ("ELECTRON (+5 mSv)", PARTICLE_TYPES["electron"], 230),
                ("PROTON (+12 mSv)", PARTICLE_TYPES["proton"], 512),
                ("ION PESADO (+25 mSv)", PARTICLE_TYPES["heavy_ion"], 790),
            ]
            for label, pdata, cx in demos:
                pygame.draw.circle(surface, pdata["color"], (cx, demo_y), pdata["radius"] + 3)
                pygame.draw.circle(surface, (255, 255, 255), (cx, demo_y), max(2, pdata["radius"] // 3))
                lbl = small_font.render(label, True, pdata["color"])
                surface.blit(lbl, lbl.get_rect(center=(cx, demo_y + 30)))

        if self.current_page > 0:
            pygame.draw.rect(surface, (30, 42, 65), self.btn_prev, border_radius=6)
            pygame.draw.rect(surface, (120, 150, 190), self.btn_prev, width=2, border_radius=6)
            prev_lbl = small_font.render("< ANTERIOR", True, TEXT_COLOR)
            surface.blit(prev_lbl, prev_lbl.get_rect(center=self.btn_prev.center))

        is_last = (self.current_page == len(self.pages) - 1)
        next_color = (50, 230, 140) if is_last else (0, 220, 255)
        next_text = "COMENZAR MISION >" if is_last else "SIGUIENTE >"

        pygame.draw.rect(surface, (25, 45, 65), self.btn_next, border_radius=6)
        pygame.draw.rect(surface, next_color, self.btn_next, width=2, border_radius=6)
        next_lbl = small_font.render(next_text, True, next_color)
        surface.blit(next_lbl, next_lbl.get_rect(center=self.btn_next.center))

        