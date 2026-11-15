# -*- coding: utf-8 -*-
"""Las pantallas del simulador (pygame). Las reglas viven en simulador.py y decisiones.py.

Fases: titulo → como → (misión: manana → decision → resultado → tarea → tarea_hecha → cierre)
       → fin · datos (fuentes de la NASA)
Lienzo lógico de 1280×720 que se agranda a la ventana sin deformarse.
"""
import math
import os
import random
import sys

import pygame

from ..data import datos_nasa as N
from . import simulador as S        
from .. import minijuegos
from ..assets import sonido
from ..assets.textos import t, n
from ..assets.texto_mate import componer, fuente, fuente_pixel, pixel
from ..assets.constantes import *


#minijuegos
from ..minijuegos.barrido_orbital.main import main as iniciar_barrido
from ..minijuegos.solaris.main import main as iniciar_solaris



#pantallas
from ..escenas.titulo import MenuInicial


#acciones


# clave, máximo, color, «alto es malo»
INDICADORES = [("o2", 60, "cian", False), ("agua", 160, "azul", False), ("energia", 500, "amarillo", False),
               ("comida", 160, "verde", False), ("dosis", 250, "violeta", True), ("animo", 100, "rosa", False)]


def nombre_ind(k):
    return {"o2": t("ind.o2", "Oxígeno"), "agua": t("ind.agua", "Agua"), "energia": t("ind.energia", "Energía"),
            "comida": t("ind.comida", "Comida"), "dosis": t("ind.dosis", "Radiación recibida"),
            "animo": t("ind.animo", "Ánimo de la tripulación")}[k]


def valor_ind(k, v):
    return {"o2": f"{n(v)} kg", "agua": f"{n(v)} L", "energia": f"{n(v, 0)} kWh", "comida": f"{n(v)} kg",
            "dosis": f"{n(v)} mSv", "animo": f"{n(v, 0)} %"}[k]


def nombre_sis(k):
    return {"generador": t("sis.generador", "generador de O₂"), "reciclador": t("sis.reciclador", "reciclador de agua"),
            "invernadero": t("sis.invernadero", "invernadero")}[k]


class Boton:
    def __init__(self, rect, texto, accion, color="panel2", activo=True, tam=22, negrita=True, tecla=None):
        self.rect = pygame.Rect(rect)
        self.texto, self.accion, self.color = texto, accion, color
        self.activo, self.tam, self.negrita, self.tecla = activo, tam, negrita, tecla


class Juego(MenuInicial):
    def __init__(self, ventana=True):
        if ventana and sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass
        pygame.init()
        self.con_ventana = ventana
        if ventana:
            pygame.display.set_caption("Mission Survival")
            info = pygame.display.Info()
            esc = min(1.0, (info.current_w - 80) / W, (info.current_h - 120) / H) if info.current_w > 0 else 1.0
            self.ventana = pygame.display.set_mode((int(W * esc), int(H * esc)), pygame.RESIZABLE)
            sonido.iniciar()
        self.lienzo = pygame.Surface((W, H))
        self.reloj = pygame.time.Clock()
        rng = random.Random(3)
        self.estrellas = [(rng.random(), rng.random(), rng.randint(80, 255)) for _ in range(160)]
        self.m = None
        self.fase = "titulo"
        self.volver_a = "titulo"
        self.botones, self.atajos = [], {}
        self.mouse = (0, 0)
        self.reporte, self.res, self.res_tarea, self.res_cierre = [], None, None, None
        self.foto_manana = None
        self.dia_cerrado = 0
        self.cuadro = 0
        self.pantalla_completa = False
        self.jugar_micro = True        # se puede apagar en la pantalla de la tarea
        self.mj, self.mj_tid = None, None
        self._dt = 1 / 60

    # ══ acciones ════════════════════════════════════════════════════════════════════════
    SIN_JUGAR = 0.9                    # rendimiento si se salta un microjuego que sí existe

    def elegir_tarea(self, tid):
        if tid == "paneles":
            if self.jugar_micro:
                tamano = self.ventana.get_size()
                try:
                    iniciar_solaris(cerrar_pygame=False)
                finally:
                    if self.pantalla_completa:
                        self.ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        self.ventana = pygame.display.set_mode(tamano, pygame.RESIZABLE)
                    pygame.display.set_caption("Mission Survival")
                    sonido.parar_bucles()
            self.hacer_tarea(tid, 1.0)
            return
        if tid == "radiacion":
            if self.jugar_micro:
                tamano = self.ventana.get_size()
                try:
                    iniciar_barrido(cerrar_pygame=False)
                finally:
                    if self.pantalla_completa:
                        self.ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        self.ventana = pygame.display.set_mode(tamano, pygame.RESIZABLE)
                    pygame.display.set_caption("Mission Survival")
                    sonido.parar_bucles()
            self.hacer_tarea(tid, 1.0)
            return
        clase = minijuegos.para_tarea(tid)
        if clase and self.jugar_micro:
            semilla = self.m.semilla * 100 + self.m.e.dia
            self.mj, self.mj_tid = clase(self.m.e, random.Random(semilla)), tid
            self.fase = "micro"
        else:
            self.hacer_tarea(tid, self.SIN_JUGAR if clase else 1.0)

    def terminar_micro(self, saltado=False):
        sonido.parar_bucles()
        if saltado and getattr(self.mj, "etapa", None) == "final":
            saltado = False                # ESC en la tarjeta final: vale lo que ya se jugó
        r = self.SIN_JUGAR if saltado else self.mj.rendimiento_seguro()
        tid = self.mj_tid
        self.mj, self.mj_tid = None, None
        self.hacer_tarea(tid, r)
        nota = (t("mic.saltado", "Saltaste el microjuego: la tarea rindió el {p} %.", p=n(r * 100, 0)) if saltado
                else t("mic.rend", "Microjuego: rendiste el {p} %.", p=n(r * 100, 0)))
        self.res_tarea = (tid, [nota] + self.res_tarea[1])

    def paso_micro(self, eventos):
        """Un cuadro del microjuego: los clics ya van en coordenadas del lienzo."""
        convertidos = []
        for ev in eventos:
            if hasattr(ev, "pos"):
                d = dict(ev.dict)
                d["pos"] = self._a_lienzo(ev.pos)
                convertidos.append(pygame.event.Event(ev.type, d))
            else:
                convertidos.append(ev)
        apretado = pygame.mouse.get_pressed()[0] if self.con_ventana else False
        if self.mj.paso(convertidos, min(0.05, self._dt), self.mouse, apretado):
            self.terminar_micro()

    def nueva_mision(self, semilla=None, modo=None):
        """modo: «corta» (14 días) o «completa» (28). Sin modo, repite el de la última misión."""
        self.modo = modo or getattr(self, "modo", "corta")
        self.m = S.Mision(semilla, self.modo)
        self.empezar_dia()

    def empezar_dia(self):
        self.foto_manana = self.m.e.foto()
        self.reporte = self.m.empezar_dia()
        self.fase = "manana"
        if self.m.decision and self.m.decision.evento:
            sonido.play("alerta")
        else:
            sonido.play("dia")

    def ir_decision(self):
        self.fase = "decision" if self.m.decision else "tarea"

    def elegir(self, i):
        self.res = self.m.elegir(i)
        sonido.play("bien" if self.res["correcta"] else "mal")
        self.fase = "resultado"

    def hacer_tarea(self, tid, r=1.0):
        self.res_tarea = (tid, self.m.hacer_tarea(tid, r))
        sonido.play("bien")
        self.fase = "tarea_hecha"

    def cerrar(self):
        self.dia_cerrado = self.m.e.dia
        self.res_cierre = self.m.cerrar_dia()
        self.fase = "cierre"

    def siguiente(self):
        if self.m.fin:
            self.fase = "fin"
            sonido.play("victoria" if self.m.fin == "victoria" else "derrota")
        else:
            self.empezar_dia()

    def alternar_sistema(self, k):
        e = self.m.e
        if k == "reciclador" and e.reciclador_roto:
            return
        e.sistemas[k] = not e.sistemas[k]

    # ══ bucle ═══════════════════════════════════════════════════════════════════════════
    def _guion_autoprueba(self):
        """MISION_AUTOPRUEBA=<carpeta>: el juego se maneja SOLO, en su ventana real (se manda sus propias
        teclas y clics), guarda fotos en esa carpeta y se cierra. Nunca toca otras ventanas."""
        K = pygame.KEYDOWN
        return [(90, ("foto", "1_titulo")), (5, (K, pygame.K_RETURN)), (60, ("foto", "2_tablero")),
                (5, (K, pygame.K_RETURN)), (30, (K, pygame.K_1)), (30, ("foto", "3_resultado")),
                (5, (K, pygame.K_RETURN)), (30, ("foto", "4_tarea")), (5, (K, pygame.K_1)),
                (30, (K, pygame.K_RETURN)), (30, ("foto", "5_cierre")), (5, (K, pygame.K_RETURN)),
                (60, ("clic", (533, 485))), (20, ("foto", "6_clic_generador")), (5, ("clic", (533, 485))),
                (20, ("foto", "7_tablero_dia2")), (5, ("salir", None))]

    def _paso_autoprueba(self, guion):
        if not guion:
            return True
        espera, (tipo, dato) = guion[0]
        if espera > 0:
            guion[0] = (espera - 1, (tipo, dato))
            return True
        guion.pop(0)
        carpeta = os.environ["MISION_AUTOPRUEBA"]
        if tipo == "foto":
            os.makedirs(carpeta, exist_ok=True)
            pygame.image.save(self.lienzo, os.path.join(carpeta, dato + ".png"))
        elif tipo == "clic":
            esc, ox, oy = self._geom()
            pos = (int(ox + dato[0] * esc), int(oy + dato[1] * esc))
            pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
        elif tipo == "salir":
            return False
        else:
            pygame.event.post(pygame.event.Event(tipo, key=dato, mod=0, unicode="", scancode=0))
        return True

    def correr(self):
        guion = self._guion_autoprueba() if os.environ.get("MISION_AUTOPRUEBA") else None
        while True:
            if guion is not None and not self._paso_autoprueba(guion):
                return
            eventos = pygame.event.get()
            for ev in eventos:
                if ev.type == pygame.QUIT:
                    return
                if ev.type == pygame.VIDEORESIZE and not self.pantalla_completa:
                    self.ventana = pygame.display.set_mode(ev.size, pygame.RESIZABLE)
                if ev.type == pygame.KEYDOWN:
                    if os.environ.get("MISION_REGISTRO"):
                        self._registrar(f"tecla {pygame.key.name(ev.key)} en {self.fase}")
                    if ev.key == pygame.K_F11:
                        self._alternar_completa()
                    elif ev.key == pygame.K_F12:
                        self.guardar_foto()
                    elif ev.key == pygame.K_ESCAPE:
                        if self.pantalla_completa:
                            self._alternar_completa()
                        elif self.fase == "titulo":
                            return
                        elif self.fase in ("datos", "como"):
                            self.fase = self.volver_a
                        elif self.fase == "micro":
                            self.terminar_micro(saltado=True)
                    elif ev.key in self.atajos:
                        sonido.play("click")
                        self.atajos[ev.key]()
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    p = self._a_lienzo(ev.pos)
                    for b in reversed(self.botones):
                        if b.activo and b.rect.collidepoint(p):
                            sonido.play("click")
                            b.accion()
                            break
            self.mouse = self._a_lienzo(pygame.mouse.get_pos())
            if self.fase == "micro" and self.mj:
                self.paso_micro(eventos)
            self.dibujar()
            self._presentar()
            self._dt = self.reloj.tick(60) / 1000

    def _registrar(self, linea):
        """Solo para pruebas (variable MISION_REGISTRO=1): anota lo que pasa en ~/.mision_lunar/registro.txt."""
        try:
            carpeta = os.path.join(os.path.expanduser("~"), ".mision_lunar")
            os.makedirs(carpeta, exist_ok=True)
            with open(os.path.join(carpeta, "registro.txt"), "a", encoding="utf-8") as f:
                f.write(linea + chr(10))
        except OSError:
            pass

    def guardar_foto(self):
        """F12: guarda una foto del juego (solo el juego, no la pantalla) en ~/.mision_lunar/capturas."""
        carpeta = os.path.join(os.path.expanduser("~"), ".mision_lunar", "capturas")
        os.makedirs(carpeta, exist_ok=True)
        k = len(os.listdir(carpeta)) + 1
        ruta = os.path.join(carpeta, f"captura_{k:03d}.png")
        pygame.image.save(self.lienzo, ruta)
        if os.environ.get("MISION_REGISTRO"):
            self._registrar("foto " + ruta)
        return ruta

    def _alternar_completa(self):
        self.pantalla_completa = not self.pantalla_completa
        if self.pantalla_completa:
            self.ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.ventana = pygame.display.set_mode((W, H), pygame.RESIZABLE)

    def _geom(self):
        vw, vh = self.ventana.get_size()
        esc = min(vw / W, vh / H)
        return esc, (vw - int(W * esc)) // 2, (vh - int(H * esc)) // 2

    def _a_lienzo(self, pos):
        if not self.con_ventana:
            return pos
        esc, ox, oy = self._geom()
        return (int((pos[0] - ox) / esc), int((pos[1] - oy) / esc))

    def _presentar(self):
        esc, ox, oy = self._geom()
        if abs(esc - 1) < 1e-3:
            self.ventana.blit(self.lienzo, (ox, oy))
        else:
            self.ventana.fill((0, 0, 0))
            self.ventana.blit(pygame.transform.smoothscale(self.lienzo, (int(W * esc), int(H * esc))), (ox, oy))
        pygame.display.flip()

    # ══ ayudas de dibujo ════════════════════════════════════════════════════════════════
    def txt(self, s, tam, color, x, y, negrita=False, centro=False, derecha=False):
        img = fuente(tam, negrita).render(s, True, C.get(color, color) if isinstance(color, str) else color)
        r = img.get_rect()
        if centro:
            r.center = (x, y)
        elif derecha:
            r.topright = (x, y)
        else:
            r.topleft = (x, y)
        self.lienzo.blit(img, r)
        return r

    def pix(self, s, tam, color, x, y, centro=False, derecha=False, ancho=None):
        """Texto con la letra de píxeles (Press Start 2P). Con `ancho`, se achica a 16 si no cabe."""
        s = pixel(s)
        f = fuente_pixel(tam)
        if ancho and f.size(s)[0] > ancho and tam > 16:
            f = fuente_pixel(16)
        img = f.render(s, False, C.get(color, color) if isinstance(color, str) else color)
        r = img.get_rect()
        if centro:
            r.center = (x, y)
        elif derecha:
            r.topright = (x, y)
        else:
            r.topleft = (x, y)
        self.lienzo.blit(img, r)
        return r

    def rico(self, s, tam, color, x, y, ancho, negrita=False, centro=False):
        img = componer(s, tam, C.get(color, color) if isinstance(color, str) else color, ancho, negrita,
                       "centro" if centro else "izq")
        self.lienzo.blit(img, (x, y))
        return img.get_height()

    def caja(self, rect, color="panel", borde="borde", radio=14, alfa=None):
        r = pygame.Rect(rect)
        if alfa is not None:
            s = pygame.Surface(r.size, pygame.SRCALPHA)
            pygame.draw.rect(s, (*C[color], alfa), s.get_rect(), border_radius=radio)
            self.lienzo.blit(s, r)
        else:
            pygame.draw.rect(self.lienzo, C[color], r, border_radius=radio)
        if borde:
            pygame.draw.rect(self.lienzo, C[borde], r, 2, border_radius=radio)
        return r

    def boton(self, rect, texto, accion, color="panel2", activo=True, tam=22, tecla=None, negrita=True, pixel_=False):
        b = Boton(rect, texto, accion, color, activo, tam, negrita, tecla)
        self.botones.append(b)
        if tecla is not None and activo:
            for k in (tecla if isinstance(tecla, (list, tuple)) else [tecla]):
                self.atajos[k] = accion
        encima = b.rect.collidepoint(self.mouse) and activo
        base = C[color]
        fondo = tuple(min(255, v + 28) for v in base) if encima else base
        if not activo:
            fondo = (40, 44, 60)
        pygame.draw.rect(self.lienzo, fondo, b.rect, border_radius=12)
        pygame.draw.rect(self.lienzo, C["oro"] if encima else C["borde"], b.rect, 2, border_radius=12)
        color_txt = C["texto"] if activo else C["gris2"]
        if pixel_ and texto and fuente_pixel(16).size(pixel(texto))[0] <= b.rect.w - 28:
            img = fuente_pixel(16).render(pixel(texto), False, color_txt)
            self.lienzo.blit(img, img.get_rect(center=b.rect.center))
            return b
        img = componer(texto, tam, color_txt, b.rect.w - 24, negrita, "centro")
        self.lienzo.blit(img, (b.rect.x + 12, b.rect.centery - img.get_height() // 2))
        return b

    def oscurecer(self, alfa=175):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((0, 0, 0, alfa))
        self.lienzo.blit(s, (0, 0))

    def cielo(self, rect=None, brillo=1.0):
        r = pygame.Rect(rect or (0, 0, W, H))
        for x, y, b in self.estrellas:
            px, py = r.x + int(x * r.w), r.y + int(y * r.h)
            tw = 0.75 + 0.25 * math.sin(self.cuadro * 0.03 + x * 40)
            v = int(b * tw * brillo)
            self.lienzo.set_at((px, py), (v, v, min(255, v + 20)))

    # ══ dibujo general ══════════════════════════════════════════════════════════════════
    def dibujar(self):
        self.cuadro += 1
        self.botones, self.atajos = [], {}
        self.lienzo.fill(C["fondo"])
        f = self.fase
        if f == "titulo":
            self._titulo()
        elif f == "como":
            self._como()
        elif f == "datos":
            self._datos()
        elif f == "fin":
            self._fin()
        elif f == "micro":
            self.mj.dibujar_todo(self.lienzo, fuente)
            self.txt(t("mic.esc", "ESC para saltar (rinde el 90 %)"), 15, "gris2", W - 40, H - 30, derecha=True)
        else:
            self._tablero(interactivo=(f == "manana"))
            if f != "manana":
                self.oscurecer()
                {"decision": self._decision, "resultado": self._resultado, "tarea": self._tarea,
                 "tarea_hecha": self._tarea_hecha, "cierre": self._cierre}[f]()

    def _abrir(self, fase):
        self.volver_a = self.fase
        self.fase = fase

    # ── cómo se juega ───────────────────────────────────────────────────────────────────
    def _como(self):
        self.cielo(brillo=0.5)
        self.caja((140, 40, 1000, 640), "panel")
        self.pix(t("como.tit", "Cómo se juega"), 24, "oro", W // 2, 82, centro=True)
        pasos = [
            (t("como.1t", "1 · Mañana"), t("como.1", "Mirá los 6 indicadores de la base y el reporte. Podés "
                                                      "encender o apagar los sistemas con un clic.")),
            (t("como.2t", "2 · Una decisión"), t("como.2", "Cada día llega un problema con números reales. "
                                                           "Hacé la cuenta: la mejor opción sale de la matemática.")),
            (t("como.3t", "3 · Una tarea"), t("como.3", "Escogé en qué trabaja la tripulación: cosechar, hacer "
                                                        "oxígeno, traer hielo, cubrir el hábitat o descansar.")),
            (t("como.4t", "4 · Fin del día"), t("como.4", "La base consume y produce. Mirá qué subió y qué bajó.")),
        ]
        y = 130
        for tit, desc in pasos:
            self.txt(tit, 24, "cian", 200, y, True)
            y += 34 + self.rico(desc, 21, "texto", 200, y + 32, 880)
        y += 10
        self.rico(t("como.gana", "Se gana llegando al último día con la tripulación bien. La misión completa dura "
                                 "28 días: un día lunar entero, 14 de sol y 14 de noche. La corta dura 14: los últimos "
                                 "7 días de sol y los primeros 7 de la noche. Se pierde si se acaba el oxígeno, el agua "
                                 "o la comida, si la radiación pasa el límite de la NASA (250 mSv) o si el ánimo llega "
                                 "a cero."), 20, "oro", 200, y, 880)
        self.boton((W // 2 - 120, 600, 240, 52), t("volver", "Volver"), lambda: setattr(self, "fase", self.volver_a),
                   tecla=[pygame.K_RETURN, pygame.K_ESCAPE])

    # ── datos de la NASA ────────────────────────────────────────────────────────────────
    def _datos(self):
        self.caja((60, 24, 1160, 672), "panel")
        self.pix(t("dat.tit", "Los datos reales del juego"), 24, "oro", W // 2, 60, centro=True)
        y = 92
        for dato, fuente_txt, _url, es_nasa in N.FUENTES:
            chip = pygame.Rect(90, y + 2, 92, 26)
            pygame.draw.rect(self.lienzo, C["azul"] if es_nasa else C["gris2"], chip, border_radius=8)
            self.txt("NASA" if es_nasa else t("dat.otra", "otra"), 16, "texto", chip.centerx, chip.centery, True,
                     centro=True)
            self.txt(dato, 19, "texto", 198, y, True)
            self.txt(fuente_txt, 16, "gris", 198, y + 23)
            y += 39
        self.rico(t("dat.nota", "Los números de diseño (tamaño de la batería, potencia de cada aparato, lo que "
                                "rinde el invernadero) son simplificaciones del juego, no datos de la NASA. Este "
                                "juego no está afiliado a la NASA ni respaldado por ella, y no usa su logo."),
                  16, "gris", 90, y + 4, 1100)
        self.boton((W // 2 - 120, 640, 240, 44), t("volver", "Volver"), lambda: setattr(self, "fase", self.volver_a),
                   tecla=[pygame.K_RETURN, pygame.K_ESCAPE], tam=20)

    # ── el tablero de la base ───────────────────────────────────────────────────────────
    def _tablero(self, interactivo):
        m, e = self.m, self.m.e
        de_dia = e.de_dia()
        # barra de arriba con el mapa de los días de la misión (una constelación de nodos)
        self.caja((0, -14, W, 70), "panel", radio=0)
        self.pix(t("tab.dia", "Día {d} de {t}", d=e.dia, t=e.total), 16, "oro", 18, 9)
        self.txt(t("tab.luz", "Día lunar: hay sol") if de_dia else t("tab.noche", "Noche lunar: sin sol, −173 °C"),
                 15, "amarillo" if de_dia else "cian", 18, 33)
        x0, x1, yy = 330, 1010, 28
        paso = (x1 - x0) / (e.total - 1)
        pygame.draw.line(self.lienzo, C["borde"], (x0, yy), (x1, yy), 2)
        for d in range(1, e.total + 1):
            x = int(x0 + (d - 1) * paso)
            noche = d > e.luz
            if d < e.dia:
                pygame.draw.circle(self.lienzo, (90, 110, 160) if noche else (170, 160, 110), (x, yy), 6)
            elif d == e.dia:
                pygame.draw.circle(self.lienzo, C["oro"], (x, yy), 10)
                pygame.draw.circle(self.lienzo, C["texto"], (x, yy), 10, 2)
            else:
                pygame.draw.circle(self.lienzo, (30, 36, 70) if noche else (60, 60, 50), (x, yy), 6)
                pygame.draw.circle(self.lienzo, C["borde"], (x, yy), 6, 1)
            if d == e.dia + 1 and m.pronostico:
                pygame.draw.circle(self.lienzo, C["naranja"], (x, yy), 11, 2)
        self.txt(t("tab.sol", "sol"), 13, "gris", x0 - 6, yy + 12)
        self.txt(t("tab.noc", "noche"), 13, "gris", int(x0 + e.luz * paso) - 4, yy + 12)
        if interactivo:
            self.boton((W - 150, 8, 136, 40), t("tab.menu", "Menú"), lambda: setattr(self, "fase", "titulo"), tam=18)
        # indicadores
        self.caja((16, 66, 420, 520), "panel")
        self.pix(t("tab.ind", "Indicadores"), 16, "oro", 34, 82)
        y = 108
        for k, mx, col, alto_malo in INDICADORES:
            v = getattr(e, k)
            frac = max(0.0, min(1.0, v / mx))
            critico = False
            if k in ("o2", "agua", "comida"):
                d = e.dias_que_alcanza(k)
                sub = (t("ind.sube", "no baja hoy") if d is None else t("ind.mucho", "alcanza más de 99 días") if d > 99
                       else t("ind.alcanza", "alcanza {d} días", d=n(d)))
                critico = d is not None and d < 4
            elif k == "energia":
                kwh = (e.kw_fuente() - e.kw_carga()) * 24
                sub = t("ind.energia_d", "{s}{k} kWh por día", s="+" if kwh >= 0 else "−", k=n(abs(kwh), 0))
                critico = v < 80
            elif k == "dosis":
                sub = t("ind.dosis_d", "límite de la NASA: 250 · +{d} por día", d=n(e.dosis_diaria(), 2))
                critico = v > 190
            else:
                sub = (t("ind.animo_bien", "con ganas") if v >= 60 else t("ind.animo_med", "cansada") if v >= 30
                       else t("ind.animo_mal", "agotada: rinde menos"))
                critico = v < 30
            self.txt(nombre_ind(k), 19, "texto", 34, y, True)
            self.pix(valor_ind(k, v), 16, "rojo" if critico else "texto", 418, y + 3, derecha=True)
            barra = pygame.Rect(34, y + 28, 384, 14)
            pygame.draw.rect(self.lienzo, (36, 42, 72), barra, border_radius=7)
            if frac > 0:
                pygame.draw.rect(self.lienzo, C["rojo"] if critico else C[col],
                                 (barra.x, barra.y, max(8, int(barra.w * frac)), barra.h), border_radius=7)
            self.txt(sub, 15, "rojo" if critico else "gris", 34, y + 46)
            y += 79
        # la base dibujada
        self._escena(pygame.Rect(452, 66, 440, 330))
        # sistemas
        self.caja((452, 406, 440, 180), "panel")
        r_sis = self.pix(t("tab.sis", "Sistemas"), 16, "oro", 468, 418)
        if interactivo:
            self.txt(t("tab.sis_clic", "clic para encender o apagar"), 15, "gris", r_sis.right + 14, 415)
        for i, k in enumerate(("generador", "reciclador", "invernadero")):
            r = pygame.Rect(468 + i * 140, 444, 130, 82)
            on = e.sistemas[k] and not (k == "reciclador" and e.reciclador_roto)
            roto = k == "reciclador" and e.reciclador_roto
            col = "verde" if on else ("rojo" if roto else "gris2")
            if interactivo:
                self.botones.append(Boton(r, "", (lambda kk=k: self.alternar_sistema(kk))))
            encima = interactivo and r.collidepoint(self.mouse)
            pygame.draw.rect(self.lienzo, (34, 44, 80) if encima else (26, 32, 60), r, border_radius=10)
            pygame.draw.rect(self.lienzo, C[col], r, 2, border_radius=10)
            nom = {"generador": t("sis.c.gen", "Generador O₂"), "reciclador": t("sis.c.rec", "Reciclador"),
                   "invernadero": t("sis.c.inv", "Invernadero")}[k]
            self.txt(nom, 16, "texto", r.centerx, r.y + 16, True, centro=True)
            self.txt(f"{n(S.CARGAS_KW[k])} kW", 15, "gris", r.centerx, r.y + 38, centro=True)
            estado = (t("sis.roto", "AVERIADO") if roto else t("sis.on", "ENCENDIDO") if on else t("sis.off", "APAGADO"))
            self.txt(estado, 15, col, r.centerx, r.y + 60, True, centro=True)
        entra, sale = e.kw_fuente(), e.kw_carga()
        fuente_txt = t("tab.panel", "panel solar") if de_dia else t("tab.reactor", "reactor")
        self.rico(t("tab.balance", "Entra {a} kW ({f}) · sale {b} kW · batería {s}{c} kWh por día",
                    a=n(entra), f=fuente_txt, b=n(sale), s="+" if entra >= sale else "−",
                    c=n(abs(entra - sale) * 24, 0)), 15, "rojo" if sale > entra else "texto", 468, 534, 416)
        # reporte
        self.caja((908, 66, 356, 520), "panel")
        self.pix(t("tab.rep", "Reporte de hoy"), 16, "oro", 926, 82)
        yy = 110
        lineas = list(self.reporte) or [t("tab.sin", "Sin novedades. Todo en orden en la base.")]
        if m.pronostico:
            lineas.append(m.pronostico)
        for fr in lineas:
            yy += self.rico("• " + fr, 17, "naranja" if fr == m.pronostico else "texto", 926, yy, 322) + 8
        refugio = {0.3: t("ref.agua", "tanques de agua"), 0.6: t("ref.plantas", "invernadero"),
                   1.0: t("ref.nada", "sin refugio")}.get(e.refugio, "")
        info = [t("tab.reg", "Regolito encima: {m} m", m=n(e.regolito)),
                t("tab.ref", "Refugio del dormitorio: {r}", r=refugio)]
        if e.racion < 1:
            info.append(t("tab.racion", "Comida racionada al 75 %"))
        if e.enfermo:
            info.append(t("tab.enfermo", "Un tripulante está enfermo"))
        yy = 470
        for s in info:
            self.txt(s, 16, "gris", 926, yy)
            yy += 24
        self.txt(t("tab.aciertos", "Buenas decisiones: {a} de {t}", a=e.aciertos, t=e.aciertos + e.errores),
                 16, "verde", 926, yy)
        # acción principal
        if interactivo:
            if m.decision:
                txt = t("tab.ir_dec", "Ver la decisión del día  →")
                if m.decision.evento:
                    txt = t("tab.ir_evento", "¡Atención! {e}  →", e=m.decision.titulo)
            else:
                txt = t("tab.ir_tarea", "Día tranquilo: ir a la tarea  →")
            self.boton((W // 2 - 260, 604, 520, 60), txt, self.ir_decision,
                       "rojo" if (m.decision and m.decision.evento) else "panel2",
                       tecla=[pygame.K_RETURN, pygame.K_SPACE], tam=24, pixel_=True)
            self.txt(t("tab.ayuda", "ENTER para seguir · F11 pantalla completa"), 15, "gris2", W // 2, 684, centro=True)

    # ── la base dibujada ────────────────────────────────────────────────────────────────
    def _escena(self, r):
        e = self.m.e
        s = self.lienzo
        de_dia = e.de_dia()
        pygame.draw.rect(s, (3, 4, 12), r, border_radius=12)
        s.set_clip(r.inflate(-4, -4))
        self.cielo(r, 1.0 if not de_dia else 0.6)
        if de_dia:
            for rad, a in ((46, 30), (36, 60), (28, 255)):
                g = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
                pygame.draw.circle(g, (255, 236, 150, a), (rad, rad), rad)
                s.blit(g, (r.x + 70 - rad, r.y + 58 - rad))
        tx, ty = r.right - 70, r.y + 56
        pygame.draw.circle(s, (40, 100, 200), (tx, ty), 22)
        pygame.draw.circle(s, (70, 160, 90), (tx - 6, ty - 5), 9)
        pygame.draw.circle(s, (230, 235, 245), (tx + 8, ty + 6), 6)
        self.txt(t("esc.tierra", "la Tierra"), 12, "gris", tx, ty + 30, centro=True)
        suelo = (126, 126, 134) if de_dia else (42, 44, 56)
        pts = [(r.x, r.y + 214)] + [(r.x + i * 20, r.y + 210 + int(6 * math.sin(i * 0.9))) for i in range(r.w // 20 + 2)]
        pts += [(r.right, r.bottom), (r.x, r.bottom)]
        pygame.draw.polygon(s, suelo, pts)
        for cx, cy, rx in ((r.x + 60, r.y + 300, 36), (r.x + 330, r.y + 296, 28), (r.x + 200, r.y + 312, 18)):
            pygame.draw.ellipse(s, tuple(max(0, c - 22) for c in suelo), (cx - rx, cy - rx // 4, rx * 2, rx // 2))
        # panel solar
        px, py = r.x + 58, r.y + 250
        pygame.draw.line(s, (170, 170, 180), (px, py), (px, py - 46), 3)
        ang = math.radians(35 if e.panel_factor <= 0.5 else 0)
        wv, hv = 80, 34
        cx, cy = px, py - 58
        esquinas = [(-wv / 2, -hv / 2), (wv / 2, -hv / 2), (wv / 2, hv / 2), (-wv / 2, hv / 2)]
        poli = [(cx + x * math.cos(ang) - y * math.sin(ang), cy + x * math.sin(ang) + y * math.cos(ang))
                for x, y in esquinas]
        pygame.draw.polygon(s, (50, 90, 190) if de_dia else (24, 34, 70), poli)
        pygame.draw.polygon(s, (170, 190, 240), poli, 2)
        if e.panel_factor < 1 and e.panel_factor != 0.5:
            pygame.draw.line(s, (255, 255, 255), (cx - 10, cy - 8), (cx + 6, cy + 9), 2)
        self.txt(t("esc.panel", "panel solar"), 12, "gris", px, py + 4, centro=True)
        # hábitat con el regolito encima
        hx, hy = r.centerx - 24, r.y + 236
        if e.regolito > 0:
            grosor = int(6 * e.regolito)
            pygame.draw.ellipse(s, (124, 104, 82), (hx - 86 - grosor, hy - 46 - grosor, 172 + 2 * grosor, 110 + 2 * grosor))
        pygame.draw.ellipse(s, (215, 218, 226), (hx - 80, hy - 40, 160, 96))
        pygame.draw.rect(s, (215, 218, 226), (hx - 80, hy + 4, 160, 30))
        for i in range(3):
            ventana_col = (255, 220, 120) if not de_dia else (60, 80, 120)
            pygame.draw.circle(s, ventana_col, (hx - 40 + i * 40, hy + 6), 8)
        cols = {0.3: (80, 150, 255), 0.6: (80, 200, 110), 1.0: (230, 200, 70)}
        col = cols.get(e.refugio)
        if col and e.refugio_elegido:
            for dx in (-70, -35, 35, 70):
                pygame.draw.rect(s, col, (hx + dx - 9, hy + 30, 18, 22), border_radius=4)
        self.txt(t("esc.habitat", "hábitat ({m} m de regolito)", m=n(e.regolito)), 12, "gris", hx, hy + 64, centro=True)
        # invernadero
        gx, gy = r.right - 104, r.y + 262
        on = e.sistemas["invernadero"]
        if on:
            g = pygame.Surface((110, 70), pygame.SRCALPHA)
            pygame.draw.ellipse(g, (80, 230, 120, 70), g.get_rect())
            s.blit(g, (gx - 55, gy - 52))
        pygame.draw.ellipse(s, (120, 220, 150) if on else (90, 100, 110), (gx - 40, gy - 40, 80, 80), 3)
        if on:
            for i in range(4):
                pygame.draw.line(s, (60, 200, 90), (gx - 24 + i * 16, gy), (gx - 24 + i * 16, gy - 18), 3)
        pygame.draw.line(s, suelo, (gx - 44, gy + 1), (gx + 44, gy + 1), 3)
        self.txt(t("esc.inv", "invernadero"), 12, "gris", gx, gy + 12, centro=True)
        # reactor (se enciende de noche)
        rx, ry = r.right - 26, r.y + 196
        pygame.draw.rect(s, (150, 150, 160), (rx - 8, ry, 16, 40))
        for i in range(3):
            pygame.draw.line(s, (190, 190, 200), (rx + 8, ry + 6 + i * 12), (rx + 22, ry + i * 12), 2)
        if not de_dia:
            g = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(g, (255, 140, 40, 90 + int(40 * math.sin(self.cuadro * 0.08))), (20, 20), 18)
            s.blit(g, (rx - 20, ry - 2))
        self.txt(t("esc.reactor", "reactor"), 12, "gris", rx, ry + 46, centro=True)
        s.set_clip(None)
        pygame.draw.rect(s, C["borde"], r, 2, border_radius=12)

    # ── decisión del día ────────────────────────────────────────────────────────────────
    def _panel_central(self):
        return self.caja((140, 34, 1000, 652), "panel")

    def _decision(self):
        d = self.m.decision
        p = self._panel_central()
        y = p.y + 22
        if d.evento:
            chip = pygame.Rect(p.x + 40, y + 4, 110, 30)
            pygame.draw.rect(self.lienzo, C["rojo"], chip, border_radius=8)
            self.txt(t("dec.evento", "EVENTO"), 17, "texto", chip.centerx, chip.centery, True, centro=True)
            self.pix(d.titulo, 24, "oro", p.x + 166, y + 8, ancho=790)
        else:
            self.pix(d.titulo, 24, "oro", p.x + 40, y + 8, ancho=920)
        y += 56
        y += self.rico(d.enunciado, 22, "texto", p.x + 40, y, 920) + 12
        x = p.x + 40
        for dato in d.datos:
            img = fuente(17, True).render(dato, True, C["cian"])
            chip = pygame.Rect(x, y, img.get_width() + 24, 32)
            if chip.right > p.right - 40:
                x = p.x + 40
                y += 40
                chip.topleft = (x, y)
            pygame.draw.rect(self.lienzo, (26, 50, 80), chip, border_radius=10)
            self.lienzo.blit(img, (chip.x + 12, chip.y + 6))
            x = chip.right + 10
        y += 44 if d.datos else 4
        alto = 56
        y = max(y, p.bottom - 24 - len(d.opciones) * (alto + 10))
        teclas = [(pygame.K_1, pygame.K_KP1, pygame.K_a), (pygame.K_2, pygame.K_KP2, pygame.K_b),
                  (pygame.K_3, pygame.K_KP3, pygame.K_c), (pygame.K_4, pygame.K_KP4, pygame.K_d)]
        for i, op in enumerate(d.opciones):
            r = pygame.Rect(p.x + 40, y, 920, alto)
            self.boton(r, "", (lambda ii=i: self.elegir(ii)), tecla=teclas[i])
            letra = "ABCD"[i]
            pygame.draw.circle(self.lienzo, C["oro"], (r.x + 30, r.centery), 17)
            self.txt(letra, 20, "fondo", r.x + 30, r.centery, True, centro=True)
            img = componer(op.texto, 21, C["texto"], r.w - 80, False)
            self.lienzo.blit(img, (r.x + 60, r.centery - img.get_height() // 2))
            y += alto + 10

    def _resultado(self):
        res, d = self.res, self.m.decision
        p = self._panel_central()
        y = p.y + 24
        ok = res["correcta"]
        cx, cy = p.x + 64, y + 22
        pygame.draw.circle(self.lienzo, C["verde"] if ok else C["naranja"], (cx, cy), 22)
        if ok:
            pygame.draw.lines(self.lienzo, C["fondo"], False, [(cx - 11, cy), (cx - 3, cy + 9), (cx + 12, cy - 9)], 5)
        else:
            self.txt("!", 30, "fondo", cx, cy, True, centro=True)
        self.pix(t("res.bien", "¡Buena decisión!") if ok else t("res.mal", "No era la mejor opción"),
                 24, "verde" if ok else "naranja", p.x + 100, y + 10)
        y += 64
        for fr in res["frases"]:
            y += self.rico("• " + fr, 21, "texto", p.x + 40, y, 920) + 6
        y += 10
        self.txt(t("res.cuentas", "Las cuentas:"), 22, "cian", p.x + 40, y, True)
        y += 34
        caja_y = y
        alto = componer(res["explicacion"], 21, C["texto"], 880).get_height()
        self.caja((p.x + 30, caja_y - 8, 940, alto + 24), "panel2", borde=None, radio=12)
        self.rico(res["explicacion"], 21, "texto", p.x + 50, caja_y + 4, 880)
        y = caja_y + alto + 30
        if not ok and res["mejores"]:
            self.rico(t("res.mejor", "La mejor era: {x}", x=" / ".join(res["mejores"])), 20, "verde", p.x + 40, y, 920)
        self.boton((p.right - 300, p.bottom - 76, 260, 54), t("res.seguir", "Continuar  →"),
                   lambda: setattr(self, "fase", "tarea"), tecla=[pygame.K_RETURN, pygame.K_SPACE], pixel_=True)

    # ── tarea del día ───────────────────────────────────────────────────────────────────
    def _tarea(self):
        p = self._panel_central()
        self.pix(t("tar.tit", "Tarea del día"), 24, "oro", p.x + 40, p.y + 30)
        ts = self.m.tareas_disponibles()
        if not ts:
            self.rico(t("tar.ninguna", "Hoy el trabajo de la tripulación se fue en la reparación. No hay tarea."),
                      22, "texto", p.x + 40, p.y + 90, 920)
            self.boton((p.right - 300, p.bottom - 76, 260, 54), t("tar.cerrar", "Terminar el día  →"), self.cerrar,
                       tecla=[pygame.K_RETURN, pygame.K_SPACE], pixel_=True)
            return
        self.rico(t("tar.sub", "Escogé en qué trabaja hoy la tripulación. Las tareas marcadas «se juega» abren un "
                               "microjuego de pocos segundos: tu puntaje cambia cuánto rinde."),
                  19, "gris", p.x + 40, p.y + 70, 640)
        self.boton((p.right - 300, p.y + 66, 260, 44),
                   t("tar.micro_si", "minijuegos: SÍ") if self.jugar_micro else t("tar.micro_no", "minijuegos: NO"),
                   lambda: setattr(self, "jugar_micro", not self.jugar_micro),
                   "verde" if self.jugar_micro else "panel2", tam=18)
        colores = {"cosecha": "verde", "oxigeno": "cian", "radiacion": "naranja", "hielo": "azul",
                   "recreo": "rosa", "estiba": "amarillo", "paneles": "amarillo"}
        for i, tid in enumerate(ts):
            fila, col = divmod(i, 3)
            r = pygame.Rect(p.x + 40 + col * 312, p.y + 140 + fila * 150, 296, 136)
            self.boton(r, "", (lambda tt=tid: self.elegir_tarea(tt)), tecla=getattr(pygame, f"K_{i + 1}"))
            pygame.draw.rect(self.lienzo, C[colores[tid]], (r.x + 2, r.y + 2, 10, r.h - 4), border_radius=6)
            self.rico(f"{i + 1} · " + S.tarea_titulo(tid), 20, "texto", r.x + 26, r.y + 16, r.w - 40, True)
            self.rico(S.tarea_detalle(tid), 17, "gris", r.x + 26, r.y + 76, r.w - 40)
            if (tid in ("paneles", "radiacion") or minijuegos.para_tarea(tid)) and self.jugar_micro:
                chip = pygame.Rect(r.right - 104, r.bottom - 34, 92, 24)
                pygame.draw.rect(self.lienzo, C["oro"], chip, border_radius=7)
                self.txt(t("tar.sejuega", "se juega"), 15, "fondo", chip.centerx, chip.centery, True, centro=True)

    def _tarea_hecha(self):
        tid, frases = self.res_tarea
        p = self._panel_central()
        self.pix(S.tarea_titulo(tid), 24, "oro", p.x + 40, p.y + 30, ancho=920)
        y = p.y + 90
        for fr in frases:
            y += self.rico("• " + fr, 22, "texto", p.x + 40, y, 920) + 8
        self.boton((p.right - 300, p.bottom - 76, 260, 54), t("tar.cerrar", "Terminar el día  →"), self.cerrar,
                   tecla=[pygame.K_RETURN, pygame.K_SPACE], pixel_=True)

    # ── cierre del día ──────────────────────────────────────────────────────────────────
    def _cierre(self):
        e = self.m.e
        p = self._panel_central()
        self.pix(t("cie.tit", "Fin del día {d}", d=self.dia_cerrado), 24, "oro", p.x + 40, p.y + 30)
        y = p.y + 84
        antes = self.foto_manana
        for k, mx, col, alto_malo in INDICADORES:
            dv = getattr(e, k) - antes[k]
            bueno = (dv <= 0) if alto_malo else (dv >= 0)
            self.txt(nombre_ind(k), 21, "texto", p.x + 60, y, True)
            signo = "+" if dv >= 0 else "−"
            self.txt(f"{signo}{n(abs(dv), 0 if k in ('energia', 'animo') else 1)}", 21,
                     "verde" if bueno else "rojo", p.x + 470, y, True, derecha=True)
            self.txt(t("cie.queda", "queda {v}", v=valor_ind(k, getattr(e, k))), 19, "gris", p.x + 500, y + 2)
            y += 40
        y += 6
        for fr in self.res_cierre["frases"]:
            y += self.rico("• " + fr, 20, "naranja", p.x + 60, y, 880) + 6
        if self.m.fin:
            txt = t("cie.fin", "Ver cómo terminó la misión  →")
        else:
            txt = t("cie.sig", "Empezar el día {d}  →", d=e.dia)
        self.boton((p.right - 380, p.bottom - 76, 340, 54), txt, self.siguiente, "rojo" if self.m.fin == "derrota"
                   else "panel2", tecla=[pygame.K_RETURN, pygame.K_SPACE], pixel_=True)

    # ── fin de la misión ────────────────────────────────────────────────────────────────
    def _fin(self):
        m, e = self.m, self.m.e
        self.cielo(brillo=0.6)
        gano = m.fin == "victoria"
        self.pix(t("fin.gano", "¡Misión cumplida!") if gano else t("fin.perdio", "Misión fallida"), 32,
                 "verde" if gano else "rojo", W // 2, 64, centro=True)
        self.rico(m.causa, 24, "texto", W // 2 - 460, 104, 920, centro=True)
        for i in range(3):
            cx, cy = W // 2 - 70 + i * 70, 172
            lleno = i < m.estrellas()
            pts = [(cx + (26 if k % 2 == 0 else 11) * math.sin(k * math.pi / 5),
                    cy - (26 if k % 2 == 0 else 11) * math.cos(k * math.pi / 5)) for k in range(10)]
            pygame.draw.polygon(self.lienzo, C["oro"] if lleno else (50, 54, 80), pts)
        datos = [t("fin.puntos", "Puntaje: {p}", p=n(m.puntaje(), 0)),
                 t("fin.dias", "Días en la Luna: {d} de {t}", d=min(e.dia, e.total), t=e.total),
                 t("fin.aciertos", "Buenas decisiones: {a} de {t}", a=e.aciertos, t=e.aciertos + e.errores),
                 t("fin.dosis", "Radiación: {d} mSv (límite 250)", d=n(e.dosis))]
        for i, s in enumerate(datos):
            self.txt(s, 20, "texto", 160 + i * 250, 214)
        # gráfico de los recursos día por día
        g = pygame.Rect(150, 262, 980, 300)
        self.caja(pygame.Rect(g.x - 15, g.y - 20, g.w + 30, g.h + 58), "panel")
        hist = m.historial
        pygame.draw.line(self.lienzo, C["gris2"], (g.x, g.bottom), (g.right, g.bottom), 1)
        noche_x = g.x + g.w * e.luz / e.total
        pygame.draw.rect(self.lienzo, (14, 18, 40), (noche_x, g.y, g.right - noche_x, g.h))
        self.txt(t("fin.noche", "noche lunar"), 14, "gris", int(noche_x) + 8, g.y + 4)
        series = [("o2", 60, "cian"), ("agua", 160, "azul"), ("comida", 160, "verde"), ("energia", 500, "amarillo"),
                  ("dosis", 250, "violeta")]
        for k, mx, col in series:
            pts = [(g.x + g.w * i / e.total, g.bottom - g.h * max(0, min(1, h[k] / mx))) for i, h in enumerate(hist)]
            if len(pts) > 1:
                pygame.draw.lines(self.lienzo, C[col], False, pts, 3)
        for i, (k, mx, col) in enumerate(series):
            x = g.x + 10 + i * 190
            pygame.draw.rect(self.lienzo, C[col], (x, g.bottom + 14, 22, 6))
            self.txt(nombre_ind(k), 14, "gris", x + 28, g.bottom + 8)
        self.boton((W // 2 - 400, 628, 250, 54), t("fin.otra", "Jugar otra vez"), lambda: self.nueva_mision(),
                   "verde", tecla=pygame.K_RETURN)
        self.boton((W // 2 - 125, 628, 250, 54), t("fin.datos", "Los datos de la NASA"), lambda: self._abrir("datos"))
        self.boton((W // 2 + 150, 628, 250, 54), t("fin.menu", "Menú"), lambda: setattr(self, "fase", "titulo"))


def main():
    juego = Juego()
    juego.correr()
    pygame.quit()
