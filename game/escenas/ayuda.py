# -*- coding: utf-8 -*-
"""Los botones circulares «?» y la ventana con datos curiosos.

    self.boton_ayuda(x, y, "radiacion")      dibuja el círculo con «?» y lo vuelve un botón
    self.abrir_ayuda("apod")                 abre la ventana (también la abre el clic)

El contenido sale de data/curiosidades.py. La ventana se dibuja al final de `dibujar()`: mientras está
abierta, el resto de la pantalla no recibe clics ni teclas. ESC o ENTER la cierran; → o ESPACIO pasan
al siguiente dato.
"""
import pygame

from ..data import curiosidades
from ..logica import clima
from ..assets.textos import t
from ..assets.texto_mate import componer, fuente
from ..assets.constantes import *


class AyudaMixin:
    ayuda = None          # None o {"clave", "idx", "extra"}

    # ── el botón «?» ────────────────────────────────────────────────────────────────────
    def boton_ayuda(self, cx, cy, clave, r=14, etiqueta=None):
        """Círculo con «?» centrado en (cx, cy). Con `etiqueta`, la escribe al lado (en gris)."""
        from ..logica.juego import Boton
        rect = pygame.Rect(cx - r, cy - r, 2 * r, 2 * r)
        self.botones.append(Boton(rect, "", lambda c=clave: self.abrir_ayuda(c)))
        encima = rect.collidepoint(self.mouse)
        pygame.draw.circle(self.lienzo, C["oro"] if encima else C["cian"], (cx, cy), r)
        pygame.draw.circle(self.lienzo, C["texto"], (cx, cy), r, 2)
        img = fuente(int(r * 1.5), True).render("?", True, C["fondo"])
        self.lienzo.blit(img, img.get_rect(center=(cx, cy + 1)))
        if etiqueta:
            self.txt(etiqueta, 15, "texto" if encima else "gris", cx + r + 8, cy - 9)

    # ── abrir y cerrar ──────────────────────────────────────────────────────────────────
    def abrir_ayuda(self, clave):
        extra = self._apod_actual() if clave == "apod" else None
        self.ayuda = {"clave": clave, "idx": 0, "extra": [extra] if extra else None}

    def cerrar_ayuda(self):
        self.ayuda = None

    def _siguiente_dato(self):
        if self.ayuda:
            self.ayuda["idx"] += 1

    def _apod_actual(self):
        """La imagen del día que se ve ahora de fondo, como un dato más (si hay imágenes guardadas)."""
        try:
            self._cargar_fondos()
            ficha = self._fondos_fichas[self._fondo_indice()] if self._fondos else None
        except (AttributeError, IndexError, ZeroDivisionError):
            ficha = None
        if not ficha:
            return None
        return {"tipo": "dato", "fuente": "NASA APOD", "url": ficha.get("pagina", ""),
                "texto": t("ayu.apod.ahora", "Ahora se ve «{ti}», la imagen del {f}. Crédito: {cr}.",
                           ti=ficha.get("titulo", "—"), f=clima.fecha(ficha.get("fecha_imagen", "")),
                           cr=ficha.get("credito") or "NASA")}

    # ── la ventana ──────────────────────────────────────────────────────────────────────
    def _dibujar_ayuda(self):
        from ..logica.juego import Boton
        a = self.ayuda
        info = curiosidades.ayuda(a["clave"], a["extra"])
        items = info["items"]
        if not items:
            self.ayuda = None
            return
        self.botones, self.atajos = [], {}              # lo de atrás deja de recibir clics y teclas
        self.oscurecer(205)
        # el alto se ajusta al dato más largo, para que la ventana no cambie de tamaño al pasar de dato
        ancho_txt = 940 - 88
        mayor = 0
        for x in items:
            h = componer(x["texto"], 24, C["texto"], ancho_txt).get_height()
            h += 22 + componer(t("ayu.fuente", "Fuente: {f}", f=x["fuente"]), 17, C["gris"], ancho_txt).get_height() \
                if x["fuente"] else 0
            mayor = max(mayor, h)
        alto_p = max(330, min(600, 140 + mayor + 130))
        p = pygame.Rect(170, (H - alto_p) // 2, 940, alto_p)
        self.botones.append(Boton((0, 0, W, H), "", self.cerrar_ayuda))      # clic afuera: cerrar
        self.botones.append(Boton(p, "", lambda: None))                      # clic adentro: nada
        self.caja(p, "panel")
        # encabezado
        pygame.draw.circle(self.lienzo, C["cian"], (p.x + 44, p.y + 46), 20)
        img = fuente(30, True).render("?", True, C["fondo"])
        self.lienzo.blit(img, img.get_rect(center=(p.x + 44, p.y + 47)))
        self.pix(info["titulo"], 16, "oro", p.x + 82, p.y + 38, ancho=p.w - 120)
        # el dato de hoy
        n = len(items)
        i = a["idx"] % n
        it = items[i]
        es_juego = it["tipo"] == "juego"
        etiqueta = (t("ayu.juego", "Cómo funciona en el juego") if es_juego
                    else t("ayu.dato", "Dato curioso"))
        self.txt(etiqueta, 20, "verde" if es_juego else "cian", p.x + 44, p.y + 96, True)
        if n > 1:
            self.txt(f"{i + 1} / {n}", 18, "gris", p.right - 44, p.y + 98, derecha=True)
        alto = self.rico(it["texto"], 24, "texto", p.x + 44, p.y + 140, p.w - 88)
        if it["fuente"]:
            self.rico(t("ayu.fuente", "Fuente: {f}", f=it["fuente"]), 17, "gris", p.x + 44,
                      p.y + 140 + alto + 22, p.w - 88)
        # puntitos de página
        for k in range(n):
            pygame.draw.circle(self.lienzo, C["oro"] if k == i else C["borde"],
                               (p.centerx - (n - 1) * 9 + k * 18, p.bottom - 92), 5)
        # botones
        y = p.bottom - 70
        if n > 1:
            self.boton((p.x + 44, y, 300, 50), t("ayu.otro", "Otro dato  →"), self._siguiente_dato,
                       "panel2", tecla=[pygame.K_RIGHT, pygame.K_SPACE], tam=21)
        self.boton((p.right - 44 - 220, y, 220, 50), t("ayu.cerrar", "Cerrar"), self.cerrar_ayuda,
                   "verde" if n == 1 else "panel2", tecla=[pygame.K_RETURN, pygame.K_ESCAPE], tam=21)
