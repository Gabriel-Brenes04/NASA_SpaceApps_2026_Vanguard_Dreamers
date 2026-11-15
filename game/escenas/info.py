import pygame
from ..data import datos_nasa as N
from ..assets.textos import t
from ..assets.constantes import *

class PantallasInformacion:
    #Como se juega
    def _como(self):
        self.cielo(brillo=0.5)
        self.caja((140, 40, 1000, 640), "panel")
        self.pix(t("como.tit", "Cómo se juega"), 24, "oro", W // 2, 82, centro=True)
        pasos = [
            (t("como.1t", "1 · Mañana"), t("como.1", "Mirá los 6 indicadores de la base y el reporte. Podés "
                                                        "encender o apagar los sistemas con un clic.")),
            (t("como.2t", "2 · Una decisión"), t("como.2", "Cada día llega un problema con números reales. "
                                                            "Hacé la cuenta: la mejor opción sale de la matemática.")),
            (t("como.3t", "3 · Una tarea"), t("como.3", "Hay 7 tareas: cosechar, hacer oxígeno, medir la "
                                                        "radiación, traer hielo, descansar, guardar la carga y "
                                                        "alinear los paneles. Escogé una por día.")),
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
                                    "o la comida, si la radiación pasa el límite de la misión (250 mSv) o si el ánimo llega "
                                    "a cero."), 20, "oro", 200, y, 880)
        self.boton_ayuda(W - 190, 82, "recursos", etiqueta=t("como.q", ""))
        self.boton((W // 2 - 120, 600, 240, 52), t("volver", "Volver"), lambda: setattr(self, "fase", self.volver_a),
                    tecla=[pygame.K_RETURN, pygame.K_ESCAPE])



    #informacion sobre el proyecto
    def _datos(self):
        """Los datos reales del juego: solo los recursos del reto (NASA y CSA), en dos columnas."""
        self.caja((40, 16, 1200, 688), "panel")
        self.pix(t("dat.tit", "Los datos reales del juego"), 24, "oro", W // 2, 52, centro=True)
        colores = {"NASA": C["azul"], "CSA": C["verde"]}
        ancho_col, x0, y0 = 560, 70, 92
        ys = [y0, y0]
        for i, (dato, fuente_txt, _url, origen) in enumerate(N.FUENTES):
            col = 0 if i < (len(N.FUENTES) + 1) // 2 else 1
            x, y = x0 + col * (ancho_col + 20), ys[col]
            chip = pygame.Rect(x, y + 2, 56, 22)
            pygame.draw.rect(self.lienzo, colores.get(origen, C["gris2"]), chip, border_radius=7)
            self.txt(origen, 15, "texto", chip.centerx, chip.centery, True, centro=True)
            alto = self.rico(t(f"fuente.{i}", dato), 17, "texto", x + 68, y, ancho_col - 80, True)
            self.txt(t(f"fuente.{i}.f", fuente_txt), 14, "gris", x + 68, y + alto + 1)
            ys[col] = y + alto + 24
        y = max(ys) + 4
        self.boton((W // 2 - 120, 650, 240, 44), t("volver", "Volver"), lambda: setattr(self, "fase", self.volver_a),
                    tecla=[pygame.K_RETURN, pygame.K_ESCAPE], tam=20)


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
                    color_titulo="texto", color_detalle="texto", tecla=None):
        self.boton(rect, "", accion, color, tecla=tecla)
        r = pygame.Rect(rect)
        self._texto(titulo, color_titulo, tam_titulo, r.centerx, r.y + 28, centro=True)
        self._texto(detalle, color_detalle, tam_detalle, r.centerx, r.y + 58, pixelada=False, centro=True)
    