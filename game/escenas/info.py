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



    #informacion sobre el proyecto
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
    