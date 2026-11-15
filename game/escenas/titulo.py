from pathlib import Path
import json

import pygame

from ..data import datos_nasa as N
from ..assets import sonido, textos
from ..assets.textos import t, n
from ..assets.texto_mate import componer, fuente, fuente_pixel, pixel
from ..assets.constantes import *

SEG_POR_IMAGEN = 6
SEG_FUNDIDO = 1.5      
FPS_MENU = 60      


def _carpeta_fondos():
    return Path(__file__).resolve().parents[1] / "assets" / "imagenes_fondo" / "titulo"

class MenuInicial:
    def _titulo(self):
        # fondo: imágenes reales de la NASA cambiando; si no hay, el dibujo de siempre
        if not self._fondo_rotativo():
            self.cielo()
            pygame.draw.circle(self.lienzo, (40, 90, 170), (1080, 150), 60)
            pygame.draw.circle(self.lienzo, (60, 150, 90), (1062, 136), 22)
            pygame.draw.ellipse(self.lienzo, (120, 122, 132), (-200, 520, W + 400, 520))
            for cx, cy, rx in ((220, 600, 70), (640, 640, 110), (1000, 610, 60)):
                pygame.draw.ellipse(self.lienzo, (96, 98, 108), (cx - rx, cy - rx // 4, rx * 2, rx // 2))

        # encabezado: nombre y subtítulos
        self._typewriter(t("tit.nombre", "Base Lunar"), "oro", 48, W // 2, 116)
        self._texto(t("tit.sub", "Simulador de misión para astronautas junior"), "texto", 16, W // 2, 180, centro=True)
        self._texto(t("tit.sub2", "La misión depende de ti... Toma decisiones que importan."), "gris", 12, W // 2, 220, centro=True)

        # botones
        self._dibujar_botones_titulo()

        # «?»: de dónde vienen las imágenes de fondo (la imagen del día de la NASA)
        if hasattr(self, "boton_ayuda"):
            self.boton_ayuda(40, 40, "apod", r=16, etiqueta=t("tit.q", "¿De dónde son estas imágenes?"))

        # ── pie: crédito de la imagen, aviso y equipo ────────────────────────────────
        credito = self._fondo_credito()
        if credito:
            self._texto(credito, "gris", 16, W // 2, H - 76, pixelada=False, centro=True)
        self._texto(t("tit.aviso", "Demo para el NASA Space Apps Challenge 2026."), "gris_oscuro", 10, W // 2, H - 52, centro=True)
        self._texto(t("tit.equipo", "Equipo Vanguard Dreamers"), "gris_oscuro", 10, W // 2, H - 30, centro=True)





    #funcion de texto reutilizable
    def _texto(self, texto, color, tamanno, x, y, pixelada=True, centro=False):
        if pixelada:
            self.pix(texto, tamanno, color, x, y, centro=centro)
        else:
            self.txt(texto, tamanno, color, x, y, centro=centro)



    def _typewriter(self, texto, color, tamanno, x, y, centro=True, clave="titulo"):
        """Esta funcion se encarga de poner el estilo typewriter"""
        inicio = f"_typewriter_{clave}_inicio"
        visto = f"_typewriter_{clave}_visto"
        if self.cuadro - getattr(self, visto, -99) > 1:
            setattr(self, inicio, self.cuadro)
        setattr(self, visto, self.cuadro)
        letras = (self.cuadro - getattr(self, inicio, self.cuadro)) // 4
        cursor = "_" if (self.cuadro // 20) % 2 == 0 else " "
        self._texto(texto[:letras] + cursor, color, tamanno, x, y, pixelada=True, centro=centro)


    def _boton_simple(self, rect, texto, accion, color="panel", tamanno=16, color_texto="texto", tecla=None):
        self.boton(rect, "", accion, color, tecla=tecla)
        r = pygame.Rect(rect)
        self._texto(texto, color_texto, tamanno, r.centerx, r.centery, centro=True)


    def _boton_doble(self, rect, titulo, detalle, accion, color="panel", tam_titulo=16, tam_detalle=17,
                    color_titulo="texto", color_detalle="texto", tecla=None, activo=True):
        r = pygame.Rect(rect)
        if activo:
            self.boton(rect, "", accion, color, tecla=tecla)
        else:
            pygame.draw.rect(self.lienzo, C["gris2"], r, border_radius=8)
        if not activo:
            color_titulo = "gris"
            color_detalle = "gris"
        self._texto(titulo, color_titulo, tam_titulo, r.centerx, r.y + 28, centro=True)
        self._texto(detalle, color_detalle, tam_detalle, r.centerx, r.y + 58, pixelada=False, centro=True)


    def _salir(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _dibujar_botones_titulo(self):
        y = 262
        if self.m and not self.m.fin:
            r = pygame.Rect(W // 2 - 190, y, 380, 76)
            self.boton(r, "", lambda: setattr(self, "fase", "manana"), "panel2")
            self._texto(t("tit.seguir", "Seguir la misión"),
                        "texto", 16, r.centerx, r.centery - 10, centro=True)
            self._texto(t("tit.seguir_d", "Día {d} de {t}",
                        d=self.m.e.dia, t=self.m.total),
                        "texto", 14, r.centerx, r.centery + 13, centro=True)
            y += 86
            y += 62
        # dos misiones, una al lado de la otra
        # dos misiones, una al lado de la otra
        for i, (modo, titulo, detalle, color) in enumerate((
                ("corta", t("tit.corta", "Demo"), t("tit.corta_d", "14 días · Misión corta"), "panel"),
                ("completa", t("tit.completa", "Mission Survival"),
                t("tit.completa_d", "28 días · Un día lunar entero"), "panel2"))):
            self._boton_doble((W // 2 - 300 + i * 310, y, 290, 84), titulo, detalle,
                            lambda mm=modo: self.nueva_mision(modo=mm), color,
                            tecla=pygame.K_RETURN if modo == "corta" else None,
                            activo=modo == "corta")
        y += 98
        self._boton_simple((W // 2 - 190, y, 380, 52), t("tit.como", "Cómo se juega"),
                        lambda: self._abrir("como"))
        y += 64
        self._boton_simple((W // 2 - 190, y, 380, 52), t("tit.datos", "Sobre el proyecto"),
                        lambda: self._abrir("datos"))
        y += 64


        self._boton_simple((W - 150, 20, 130, 45), t("tit.salir", "Salir"),
                    self._salir, "panel")
        y += 64
        # if textos.EN:
        #     otro = "en" if textos.IDIOMA == "es" else "es"
        #     self._boton_simple((W // 2 - 190, y, 380, 52),
        #                     "English" if otro == "en" else "Español",
        #                     lambda: textos.poner_idioma(otro))










    # ── fondo rotativo con imágenes de la NASA ───────────────────────────────────
    def _cargar_fondos(self):
        """Carga una sola vez todas las imágenes de la carpeta, ya recortadas al tamaño del lienzo."""
        if hasattr(self, "_fondos"):
            return self._fondos
        self._fondos, self._fondos_fichas = [], []
        carpeta = _carpeta_fondos()
        if carpeta:
            for ruta in sorted(list(carpeta.glob("*.jpg")) + list(carpeta.glob("*.png"))):
                try:
                    img = pygame.image.load(str(ruta)).convert()
                    iw, ih = img.get_size()
                    k = max(W / iw, H / ih)                      # escala para cubrir todo sin deformar
                    img = pygame.transform.smoothscale(img, (int(iw * k), int(ih * k)))
                    img = img.subsurface(((img.get_width() - W) // 2,
                                          (img.get_height() - H) // 2, W, H)).copy()
                except pygame.error:
                    continue
                ficha = {}
                try:
                    ficha = json.loads(ruta.with_suffix(".json").read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    pass
                self._fondos.append(img)
                self._fondos_fichas.append(ficha)
        # velo oscuro para que los botones y el texto se lean sobre cualquier foto
        self._fondo_velo = pygame.Surface((W, H))
        self._fondo_velo.fill((0, 0, 0))
        self._fondo_velo.set_alpha(110)
        return self._fondos

    def _fondo_indice(self):
        por = SEG_POR_IMAGEN * FPS_MENU
        return (self.cuadro // por) % len(self._fondos)

    def _fondo_rotativo(self):
        """Dibuja la imagen actual con fundido a la siguiente. Devuelve False si no hay imágenes."""
        fondos = self._cargar_fondos()
        if not fondos:
            return False
        por, fundido = SEG_POR_IMAGEN * FPS_MENU, SEG_FUNDIDO * FPS_MENU
        i, dentro = self._fondo_indice(), self.cuadro % por
        self.lienzo.blit(fondos[i], (0, 0))
        if len(fondos) > 1 and dentro > por - fundido:
            sig = fondos[(i + 1) % len(fondos)]
            sig.set_alpha(int(255 * (dentro - (por - fundido)) / fundido))
            self.lienzo.blit(sig, (0, 0))
            sig.set_alpha(255)
        self.lienzo.blit(self._fondo_velo, (0, 0))
        return True

    def _fondo_credito(self):
        """Texto de crédito de la imagen que se está viendo (APOD pide dar crédito)."""
        if not getattr(self, "_fondos", None):
            return ""
        f = self._fondos_fichas[self._fondo_indice()]
        if not f:
            return ""
        return f"{f.get('titulo', '')} · {f.get('credito', '')} · NASA APOD"[:150]

    #imagenes de fondo usando los datos de la nasa
    def _fondo_imagen(self, ruta):
        """Carga la imagen y la recorta para llenar el lienzo sin deformarla."""
        if getattr(self, "_fondo_ruta", "sin cargar") != ruta:
            self._fondo_ruta, self._fondo_img = ruta, None
            if ruta and Path(ruta).exists():
                try:
                    img = pygame.image.load(str(ruta)).convert()
                    iw, ih = img.get_size()
                    k = max(W / iw, H / ih)                      # escala para cubrir todo
                    img = pygame.transform.smoothscale(img, (int(iw * k), int(ih * k)))
                    self._fondo_img = img.subsurface(((img.get_width() - W) // 2,
                                                      (img.get_height() - H) // 2, W, H)).copy()
                except pygame.error:
                    pass
        return self._fondo_img