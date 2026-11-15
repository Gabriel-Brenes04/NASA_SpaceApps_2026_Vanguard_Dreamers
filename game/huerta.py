# -*- coding: utf-8 -*-
# Microjuego: La Huerta (tarea: cosecha -> comida)
# Hecho por Juan David para Base Lunar.
#
# Como se juega (40 s):
#   - Se hace clic en el tanque y se arrastra una gota hasta una planta con sed.
#   - El tanque tiene pocas gotas: el agua se recicla y sale una nueva cada poco.
#   - Con agua las plantas crecen y dan tomates (eso es la cosecha).
#   - A veces llega una alerta solar (fulguracion real de NASA DONKI). Hay que
#     prender el ESCUDO o las plantas se secan mucho mas rapido.
#
# Datos reales:
#   - Fulguraciones: NASA DONKI (assets/datos/donki.json)
#   - Agua reciclada: Agencia Espacial Canadiense (la Estacion recicla orina, sudor y aliento)
#   - Veggie: en 2015 los astronautas comieron lechuga cultivada en la Estacion (NASA)

import math

import pygame

from .base import ZONA, COLORES
from ._kit import Partida
from ..assets import clima
from ..assets import sonido
from ..assets.textos import t

# ---------- cosas para ajustar ----------
GOTAS_INICIO = 6
GOTAS_MAX = 8
TIEMPO_RECICLAR = 1.5      # segundos para hacer una gota nueva
AGUA_POR_GOTA = 40
SECADO = 2.0               # agua que pierde cada planta por segundo (en el nivel 1)
DANO_SOL = 3.0             # sin escudo, en la tormenta se secan 3 veces mas rapido
TIEMPO_ESCUDO = 5.0
TIEMPO_RECARGA = 5.0
AVISO = 3.0                # segundos de aviso antes de la tormenta
TORMENTA = 5.0             # segundos que dura la tormenta

# ---------- donde va cada cosa ----------
SUELO = ZONA.bottom - 120
TANQUE = pygame.Rect(ZONA.x + 30, ZONA.bottom - 200, 150, 120)
BOTON_ESCUDO = pygame.Rect(ZONA.x + 30, ZONA.y + 150, 150, 80)
CENTROS = [370, 520, 670, 820, 970, 1120]

VERDE = (70, 190, 90)
AMARILLO = (220, 200, 70)
CAFE = (120, 90, 55)
AZUL = (70, 160, 250)
CELESTE = (150, 210, 255)
CIAN = (90, 230, 230)
ROJO = (225, 70, 60)
MACETA = (170, 95, 60)


class Planta:
    def __init__(self, x, agua):
        self.x = x
        self.agua = agua
        self.tamano = 0.2
        self.viva = True
        self.brillo = 0.0

    def zona(self):
        return pygame.Rect(self.x - 60, SUELO - 200, 120, 250)

    def color(self):
        if self.agua > 50:
            return VERDE
        elif self.agua > 25:
            return AMARILLO
        return CAFE


class Huerta(Partida):
    titulo = "Huerta: regá las plantas"
    instruccion = "Arrastrá gotas del tanque a las plantas con sed"
    tarea = "cosecha"
    duracion = 40.0
    META = 12000
    ESCALA = 400
    COLOR = VERDE

    def preparar(self):
        self.titulo = t("mj.huerta.titulo", "Huerta: regá las plantas")
        self.instruccion = t("mj.huerta.instr", "Arrastrá gotas del tanque a las plantas con sed")
        self.consejos = (
            t("mj.huerta.c1", "El tanque tiene pocas gotas: el agua se recicla y sale una nueva cada poco."),
            t("mj.huerta.c2", "Si llega una alerta solar, prendé el ESCUDO para proteger las plantas."),
            t("mj.huerta.c3", "Las plantas bien regadas crecen y dan tomates."),
        )
        self.plantas = [Planta(x, self.rng.randint(55, 90)) for x in CENTROS]
        for p in self.plantas:
            p.tamano = self.rng.uniform(0.0, 0.6)    # para que no den tomates todas juntas
        self.gotas = GOTAS_INICIO
        self.reciclado = 0.0
        self.con_gota = False
        self.antes_apretado = False
        self.escudo = 0.0
        self.recarga = 0.0
        self.proxima_alerta = 9.0
        self.aviso = 0.0
        self.tormenta = 0.0
        self.protegida = False
        self.fulguracion = None
        self.cosechas = 0

    # ---------- reglas que cambian con el nivel ----------
    def secado(self):
        return SECADO * (1 + 0.08 * (self.nv - 1))

    def cada_alerta(self):
        return max(7.0, 13.0 - 0.8 * (self.nv - 1))

    # ---------- la logica ----------
    def jugar(self, dt):
        mx, my = self.raton

        # el reciclador hace gotas nuevas
        if self.gotas < GOTAS_MAX:
            self.reciclado += dt / TIEMPO_RECICLAR
            if self.reciclado >= 1:
                self.reciclado = 0.0
                self.gotas += 1
        else:
            self.reciclado = 0.0

        # clics: tomar una gota o prender el escudo
        for x, y in self.clics:
            if TANQUE.collidepoint(x, y):
                if self.gotas > 0:
                    self.gotas -= 1
                    self.con_gota = True
                    sonido.play("click", 0.6)
                else:
                    self.fx.texto(x, y - 20, t("mj.huerta.vacio", "¡Tanque vacío! Esperá el reciclador"),
                                  COLORES["naranja"], 20)
            elif BOTON_ESCUDO.collidepoint(x, y):
                self.prender_escudo()
            else:
                encima = any(p.zona().collidepoint(x, y) for p in self.plantas)
                if not encima and not self.con_gota:
                    self.errar(x, y)

        # soltar la gota
        if self.con_gota and self.antes_apretado and not self.apretado:
            self.soltar(mx, my)
        self.antes_apretado = self.apretado

        # escudo
        if self.escudo > 0:
            self.escudo -= dt
            if self.escudo <= 0:
                self.escudo = 0.0
                self.recarga = TIEMPO_RECARGA
        elif self.recarga > 0:
            self.recarga = max(0.0, self.recarga - dt)

        # alertas solares
        if self.tormenta > 0:
            self.tormenta -= dt
            if self.tormenta <= 0:
                self.tormenta = 0.0
                self.proxima_alerta = self.cada_alerta()
        elif self.aviso > 0:
            self.aviso -= dt
            if self.aviso <= 0:
                self.empieza_tormenta()
        else:
            self.proxima_alerta -= dt
            if self.proxima_alerta <= 0:
                self.empieza_aviso()

        # las plantas
        velocidad = self.secado()
        if self.tormenta > 0 and self.escudo <= 0:
            velocidad *= DANO_SOL
        for p in self.plantas:
            if not p.viva:
                continue
            p.agua -= velocidad * dt
            if p.agua > 60:
                p.tamano += dt / 9.0
                if p.tamano >= 1.0:
                    p.tamano = 0.45
                    self.cosechas += 1
                    self.ganar(120, p.x, SUELO - 150, t("mj.huerta.tomates", "¡Tomates!"), ROJO,
                               subir=0.25, combo=False)
            if p.agua <= 0:
                p.agua = 0
                p.viva = False
                self.perder(p.x, SUELO - 80, t("mj.huerta.seco", "¡Se secó!"), castigo=150)

    def soltar(self, x, y):
        self.con_gota = False
        if TANQUE.collidepoint(x, y):
            self.gotas += 1            # la devolvio al tanque
            return
        for p in self.plantas:
            if p.viva and p.zona().collidepoint(x, y):
                sed = 1 - p.agua / 100
                if p.agua > 85:
                    self.fx.texto(p.x, SUELO - 190, t("mj.huerta.llena", "Ya tenía agua"), COLORES["gris"], 20)
                    self.combo = 0
                else:
                    msj = t("mj.huerta.salvada", "¡Salvada!") if p.agua < 25 else None
                    self.ganar(int(20 + 60 * sed), p.x, SUELO - 170, msj, CELESTE)
                p.agua = min(100, p.agua + AGUA_POR_GOTA)
                p.brillo = 0.4
                self.fx.chispas(p.x, SUELO - 30, CELESTE, 12, grav=500)
                return
        # cayo afuera: se desperdicia
        self.fx.chispas(x, y, CELESTE, 8, grav=500)
        self.errar(x, y)

    def prender_escudo(self):
        if self.escudo > 0 or self.recarga > 0:
            return
        self.escudo = TIEMPO_ESCUDO
        sonido.play("nivel", 0.5)
        if self.aviso > 0 or self.tormenta > 0:
            self.ganar(60, BOTON_ESCUDO.centerx, BOTON_ESCUDO.top - 10,
                       t("mj.huerta.protegidas", "¡Protegidas!"), CIAN, combo=False)

    def empieza_aviso(self):
        self.aviso = AVISO
        self.fulguracion = clima.evento_real(self.rng, "fuerte" if self.nv >= 4 else "moderada")
        self.fx.cartel(t("mj.huerta.alerta", "¡Alerta solar!"), COLORES["naranja"], 40, 1.4, self.Y_CARTEL)
        sonido.play("alerta", 0.6)

    def empieza_tormenta(self):
        self.tormenta = TORMENTA
        if self.escudo > 0:
            self.fx.texto(BOTON_ESCUDO.centerx + 60, BOTON_ESCUDO.bottom + 55, t("mj.huerta.bien", "¡El escudo aguanta!"), CIAN, 22)

    def animar(self, dt):
        for p in self.plantas:
            p.brillo = max(0.0, p.brillo - dt)

    # ---------- el dibujo ----------
    def escena(self, lienzo):
        # fondo: domo del invernadero en la Luna
        lienzo.fill((14, 18, 36), ZONA)
        pygame.draw.ellipse(lienzo, (22, 30, 56), (ZONA.x + 220, ZONA.y + 10, ZONA.w - 260, 760))
        pygame.draw.ellipse(lienzo, (60, 80, 130), (ZONA.x + 220, ZONA.y + 10, ZONA.w - 260, 760), 3)
        pygame.draw.rect(lienzo, (70, 70, 80), (ZONA.x, SUELO + 45, ZONA.w, ZONA.bottom - SUELO - 45))

        # sol de la tormenta
        if self.aviso > 0 or self.tormenta > 0:
            rojo = self.tormenta > 0 and self.escudo <= 0
            if rojo and int(self.t * 4) % 2 == 0:
                pygame.draw.rect(lienzo, ROJO, ZONA, 8)
            pygame.draw.circle(lienzo, COLORES["amarillo"], (ZONA.right - 60, ZONA.y + 125), 26)
            self.letrero_alerta(lienzo)

        for p in self.plantas:
            self.dibujar_planta(lienzo, p)

        # escudo encima de las plantas
        if self.escudo > 0:
            pygame.draw.ellipse(lienzo, CIAN, (ZONA.x + 240, ZONA.y + 40, ZONA.w - 300, 700), 5)

        self.dibujar_tanque(lienzo)
        self.dibujar_boton(lienzo)

        # la gota que se lleva
        if self.con_gota:
            self.dibujar_gota(lienzo, self.raton[0], self.raton[1], 16)

    def letrero_alerta(self, lienzo):
        from ..assets.texto_mate import fuente
        if self.fulguracion:
            msj = t("mj.huerta.real", "Fulguración real {c} del {f} (NASA DONKI)",
                    c=self.fulguracion.get("clase", ""), f=clima.fecha(self.fulguracion.get("pico", "")))
        else:
            msj = t("mj.huerta.alerta", "¡Alerta solar!")
        img = fuente(18, True).render(msj, True, COLORES["amarillo"])
        lienzo.blit(img, img.get_rect(midright=(ZONA.right - 100, ZONA.y + 125)))

    def dibujar_planta(self, lienzo, p):
        x = p.x
        pygame.draw.polygon(lienzo, MACETA, [(x - 45, SUELO), (x + 45, SUELO), (x + 34, SUELO + 50), (x - 34, SUELO + 50)])
        pygame.draw.rect(lienzo, (140, 75, 45), (x - 50, SUELO - 6, 100, 10))

        if not p.viva:
            pygame.draw.line(lienzo, CAFE, (x, SUELO - 4), (x + 38, SUELO - 16), 5)
            return

        # tallo: si tiene poca agua se dobla
        alto = 80 + 80 * p.tamano
        doblado = 0
        if p.agua < 50:
            doblado = (50 - p.agua) / 50
        punta_x = x + 55 * doblado
        punta_y = SUELO - alto + alto * 0.6 * doblado
        pygame.draw.line(lienzo, p.color(), (x, SUELO - 4), (punta_x, punta_y), 6)
        for i in range(1, 4):
            hx = x + (punta_x - x) * i / 4
            hy = SUELO + (punta_y - SUELO) * i / 4
            if i % 2 == 0:
                pygame.draw.ellipse(lienzo, p.color(), (hx, hy - 8, 34, 16))
            else:
                pygame.draw.ellipse(lienzo, p.color(), (hx - 34, hy - 8, 34, 16))
        pygame.draw.circle(lienzo, p.color(), (int(punta_x), int(punta_y)), 11)
        if p.tamano > 0.7:
            pygame.draw.circle(lienzo, ROJO, (int(punta_x) + 16, int(punta_y) + 28), 10)
        if p.brillo > 0:
            pygame.draw.circle(lienzo, CELESTE, (x, SUELO - 80), int(90 - 100 * p.brillo), 3)

        # barra de agua
        pygame.draw.rect(lienzo, (50, 50, 65), (x - 45, SUELO + 58, 90, 10))
        color = AZUL if p.agua > 30 else ROJO
        pygame.draw.rect(lienzo, color, (x - 45, SUELO + 58, int(90 * p.agua / 100), 10))

    def dibujar_tanque(self, lienzo):
        from ..assets.texto_mate import fuente
        pygame.draw.rect(lienzo, (40, 70, 120), TANQUE, border_radius=10)
        pygame.draw.rect(lienzo, COLORES["texto"], TANQUE, 2, border_radius=10)
        img = fuente(16, True).render(t("mj.huerta.tanque", "AGUA RECICLADA"), True, COLORES["texto"])
        lienzo.blit(img, img.get_rect(midbottom=(TANQUE.centerx, TANQUE.top - 6)))
        for i in range(self.gotas):
            self.dibujar_gota(lienzo, TANQUE.x + 22 + (i % 4) * 35, TANQUE.y + 45 + (i // 4) * 45, 9)
        pygame.draw.rect(lienzo, (50, 50, 65), (TANQUE.x, TANQUE.bottom + 8, TANQUE.w, 8))
        pygame.draw.rect(lienzo, CIAN, (TANQUE.x, TANQUE.bottom + 8, int(TANQUE.w * self.reciclado), 8))
        img = fuente(14, False).render(t("mj.huerta.reciclador", "reciclador"), True, COLORES["gris"])
        lienzo.blit(img, img.get_rect(midtop=(TANQUE.centerx, TANQUE.bottom + 20)))

    def dibujar_boton(self, lienzo):
        from ..assets.texto_mate import fuente
        if self.escudo > 0:
            color, msj = CIAN, t("mj.huerta.activo", "activo")
        elif self.recarga > 0:
            color, msj = (90, 95, 115), t("mj.huerta.cargando", "cargando...")
        else:
            color, msj = (60, 160, 160), t("mj.huerta.listo", "listo")
        pygame.draw.rect(lienzo, color, BOTON_ESCUDO, border_radius=12)
        pygame.draw.rect(lienzo, COLORES["texto"], BOTON_ESCUDO, 2, border_radius=12)
        img = fuente(22, True).render(t("mj.huerta.escudo", "ESCUDO"), True, (10, 15, 25))
        lienzo.blit(img, img.get_rect(center=(BOTON_ESCUDO.centerx, BOTON_ESCUDO.centery - 12)))
        img = fuente(15, False).render(msj, True, (10, 15, 25))
        lienzo.blit(img, img.get_rect(center=(BOTON_ESCUDO.centerx, BOTON_ESCUDO.centery + 16)))

    def dibujar_gota(self, lienzo, x, y, tam):
        x, y = int(x), int(y)
        pygame.draw.polygon(lienzo, AZUL, [(x - tam, y), (x + tam, y), (x, y - tam * 2)])
        pygame.draw.circle(lienzo, AZUL, (x, y), tam)
        pygame.draw.circle(lienzo, CELESTE, (x - tam // 3, y - tam // 3), max(2, tam // 4))
