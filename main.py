"""Pétalos de Luna: juego Pygame de recolección y evasión."""
import random
import pygame

# Tamaño de la ventana y reglas principales del juego.
ANCHO, ALTO = 800, 520
FPS = 60
META_PÉTALOS = 10
VIDAS_INICIALES = 3
TIEMPO_INICIAL = 60.0
VELOCIDAD_JUGADORA = 330.0
DT_MAXIMO = 0.05
PISO_Y = ALTO - 52

# Colores pastel para el cielo, el jardín y los elementos del juego.
LILA_CIELO = (247, 239, 255)
ROSA_NUBE = (255, 250, 254)
MORADO = (91, 67, 121)
ROSA = (244, 136, 183)
ROSA_CLARO = (255, 190, 218)
LILA = (184, 157, 236)
MENTA = (136, 202, 168)
VERDE = (116, 180, 132)
AMARILLO = (255, 218, 123)
AZUL_GOTA = (127, 165, 203)
BLANCO = (255, 255, 255)


def nuevo_estado(en_juego=False):
    """Crea todos los datos iniciales de una partida."""
    return {
        "pantalla": "juego" if en_juego else "inicio",
        "jugadora_x": ANCHO // 2,
        "petalos": 0,
        "vidas": VIDAS_INICIALES,
        "tiempo": TIEMPO_INICIAL,
        "pausado": False,
        "objetos": [],
        "tiempo_aparicion": 0.0,
    }


def rect_canasta(estado):
    """Define la zona de colisión de la canasta."""
    return pygame.Rect(int(estado["jugadora_x"] - 43), ALTO - 98, 86, 48)


def rect_objeto(objeto):
    """Define una caja de colisión para una flor o una gota."""
    if objeto["tipo"] == "flor":
        return pygame.Rect(int(objeto["x"] - 13), int(objeto["y"] - 13), 26, 26)
    return pygame.Rect(int(objeto["x"] - 11), int(objeto["y"] - 10), 22, 28)


def manejar_eventos(estado, eventos=None):
    """Atiende el teclado, el inicio, la pausa, el reinicio y el cierre."""
    seguir = True
    if eventos is None:
        eventos = pygame.event.get()

    for evento in eventos:
        if evento.type == pygame.QUIT:
            seguir = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                seguir = False
            elif estado["pantalla"] == "inicio" and evento.key in (
                pygame.K_RETURN, pygame.K_SPACE
            ):
                estado["pantalla"] = "juego"
            elif estado["pantalla"] == "juego" and evento.key == pygame.K_SPACE:
                estado["pausado"] = not estado["pausado"]
            elif evento.key == pygame.K_r:
                estado.clear()
                estado.update(nuevo_estado(en_juego=True))
    return seguir


def tecla_activa(teclas, codigo):
    """Consulta una tecla del teclado de Pygame."""
    if isinstance(teclas, dict):
        return bool(teclas.get(codigo, False))
    try:
        return bool(teclas[codigo])
    except (IndexError, KeyError, TypeError):
        return False


def crear_objeto(tipo=None, azar=None):
    """Genera una flor para recolectar o una gota para esquivar."""
    azar = azar or random
    if tipo is None:
        tipo = "flor" if azar.random() < 0.72 else "gota"
    return {
        "tipo": tipo,
        "x": azar.randint(28, ANCHO - 28),
        "y": -24.0,
        "velocidad": azar.uniform(125.0, 205.0),
    }


def actualizar(estado, dt, teclas=None, azar=None):
    """Mueve la canasta y objetos, detecta choques y revisa el final."""
    if estado["pantalla"] != "juego" or estado["pausado"]:
        return

    dt = min(max(dt, 0.0), DT_MAXIMO)
    if teclas is None:
        teclas = pygame.key.get_pressed()

    # Movimiento horizontal con límites para mantener la canasta en pantalla.
    if tecla_activa(teclas, pygame.K_LEFT):
        estado["jugadora_x"] -= VELOCIDAD_JUGADORA * dt
    if tecla_activa(teclas, pygame.K_RIGHT):
        estado["jugadora_x"] += VELOCIDAD_JUGADORA * dt
    estado["jugadora_x"] = max(45, min(ANCHO - 45, estado["jugadora_x"]))

    # El temporizador genera objetos en intervalos regulares.
    estado["tiempo"] -= dt
    estado["tiempo_aparicion"] += dt
    if estado["tiempo_aparicion"] >= 0.82:
        estado["tiempo_aparicion"] -= 0.82
        estado["objetos"].append(crear_objeto(azar=azar))

    zona_canasta = rect_canasta(estado)
    restantes = []
    for objeto in estado["objetos"]:
        objeto["y"] += objeto["velocidad"] * dt
        if rect_objeto(objeto).colliderect(zona_canasta):
            if objeto["tipo"] == "flor":
                estado["petalos"] += 1
            else:
                estado["vidas"] -= 1
        elif objeto["y"] < ALTO + 30:
            restantes.append(objeto)
    estado["objetos"] = restantes

    if estado["petalos"] >= META_PÉTALOS:
        estado["pantalla"] = "victoria"
    elif estado["vidas"] <= 0 or estado["tiempo"] <= 0:
        estado["pantalla"] = "fin"


def texto_centrado(pantalla, fuente, texto, color, y):
    """Dibuja una línea de texto centrada en la ventana."""
    superficie = fuente.render(texto, True, color)
    pantalla.blit(superficie, superficie.get_rect(center=(ANCHO // 2, y)))


def dibujar_flor(pantalla, x, y, escala=1.0, color=ROSA):
    """Dibuja una flor usando figuras geometricas sencillas."""
    x, y = int(x), int(y)
    radio = max(3, int(6 * escala))
    for dx, dy in ((0, -8), (8, 0), (0, 8), (-8, 0), (6, -6), (-6, -6)):
        pygame.draw.circle(
            pantalla, color,
            (x + int(dx * escala), y + int(dy * escala)), radio
        )
    pygame.draw.circle(pantalla, AMARILLO, (x, y), max(2, int(4 * escala)))


def dibujar_corazon(pantalla, x, y, color=ROSA):
    """Dibuja un corazon pequeño para indicar las vidas."""
    pygame.draw.circle(pantalla, color, (x - 5, y - 3), 6)
    pygame.draw.circle(pantalla, color, (x + 5, y - 3), 6)
    pygame.draw.polygon(pantalla, color, ((x - 11, y - 1), (x + 11, y - 1), (x, y + 12)))


def dibujar_nube(pantalla, x, y):
    """Dibuja una nube decorativa."""
    pygame.draw.circle(pantalla, ROSA_NUBE, (x, y), 19)
    pygame.draw.circle(pantalla, ROSA_NUBE, (x + 20, y - 7), 24)
    pygame.draw.circle(pantalla, ROSA_NUBE, (x + 45, y), 18)
    pygame.draw.rect(pantalla, ROSA_NUBE, (x - 4, y - 1, 54, 18), border_radius=8)


def dibujar_canasta(pantalla, centro_x):
    """Dibuja la canasta, su asa, carita y un pequeño moñito."""
    y = ALTO - 83
    rect = pygame.Rect(int(centro_x - 38), y - 5, 76, 43)
    pygame.draw.arc(pantalla, LILA, (rect.x + 8, y - 25, 60, 42), 0.1, 3.05, 4)
    pygame.draw.rect(pantalla, ROSA_CLARO, rect, border_radius=12)
    pygame.draw.rect(
        pantalla, ROSA,
        (rect.x - 3, y - 8, rect.width + 6, 11), border_radius=5
    )
    # Cara amigable y mejillas.
    pygame.draw.circle(pantalla, MORADO, (int(centro_x - 11), y + 13), 2)
    pygame.draw.circle(pantalla, MORADO, (int(centro_x + 11), y + 13), 2)
    pygame.draw.circle(pantalla, (255, 151, 183), (int(centro_x - 20), y + 20), 4)
    pygame.draw.circle(pantalla, (255, 151, 183), (int(centro_x + 20), y + 20), 4)
    pygame.draw.arc(pantalla, MORADO, (int(centro_x - 7), y + 14, 14, 10), 3.3, 6.1, 2)
    # Monito de dos petalos en una esquina de la canasta.
    pygame.draw.circle(pantalla, LILA, (rect.x + 8, y - 8), 6)
    pygame.draw.circle(pantalla, ROSA, (rect.x + 17, y - 8), 6)
    pygame.draw.circle(pantalla, AMARILLO, (rect.x + 12, y - 8), 3)


def dibujar_objeto(pantalla, objeto):
    """Dibuja la flor recolectable o la gota que se debe esquivar."""
    if objeto["tipo"] == "flor":
        color = ROSA if int(objeto["x"]) % 2 else LILA
        dibujar_flor(pantalla, objeto["x"], objeto["y"], 0.9, color=color)
    else:
        x, y = int(objeto["x"]), int(objeto["y"])
        pygame.draw.circle(pantalla, AZUL_GOTA, (x, y + 5), 9)
        pygame.draw.polygon(pantalla, AZUL_GOTA, ((x - 8, y + 5), (x, y - 11), (x + 8, y + 5)))
        pygame.draw.circle(pantalla, (220, 237, 255), (x - 3, y + 2), 2)


def dibujar(pantalla, fuente_titulo, fuente_texto, estado):
    """Dibuja el jardín, la interfaz y la pantalla actual."""
    pantalla.fill(LILA_CIELO)
    dibujar_nube(pantalla, 70, 93)
    dibujar_nube(pantalla, 570, 128)

    # Pequeñas estrellas decorativas en el cielo.
    for x, y in ((210, 70), (430, 88), (735, 63), (500, 190), (130, 210)):
        pygame.draw.circle(pantalla, BLANCO, (x, y), 3)

    pygame.draw.rect(pantalla, (223, 244, 224), (0, PISO_Y, ANCHO, ALTO - PISO_Y))
    pygame.draw.line(pantalla, MENTA, (0, PISO_Y), (ANCHO, PISO_Y), 4)
    for x in (42, 140, 245, 560, 670, 770):
        pygame.draw.line(pantalla, VERDE, (x, PISO_Y + 10), (x, PISO_Y + 27), 2)
        dibujar_flor(pantalla, x, PISO_Y + 9, 0.55, color=ROSA)

    if estado["pantalla"] == "inicio":
        pygame.draw.rect(pantalla, (255, 252, 255), (145, 157, 510, 235), border_radius=24)
        texto_centrado(pantalla, fuente_titulo, "PÉTALOS DE LUNA", MORADO, 205)
        texto_centrado(pantalla, fuente_texto, "Atrapa 10 flores y esquiva las gotas", MORADO, 256)
        texto_centrado(pantalla, fuente_texto, "Usa las flechas para mover | Espacio para comenzar", MORADO, 300)
        texto_centrado(pantalla, fuente_texto, "Presiona Enter para jugar", ROSA, 348)
    else:
        # Panel superior con objetivo, tiempo y vidas.
        pygame.draw.rect(pantalla, (255, 252, 255), (18, 16, ANCHO - 36, 55), border_radius=16)
        pantalla.blit(fuente_titulo.render("PÉTALOS DE LUNA", True, MORADO), (31, 27))
        pantalla.blit(
            fuente_texto.render(f"Flores: {estado['petalos']}/{META_PÉTALOS}", True, MORADO),
            (350, 34),
        )
        pantalla.blit(
            fuente_texto.render(f"{max(0, int(estado['tiempo']))} s", True, MORADO),
            (532, 34),
        )
        for i in range(estado["vidas"]):
            dibujar_corazon(pantalla, 685 + i * 30, 39)

        for objeto in estado["objetos"]:
            dibujar_objeto(pantalla, objeto)
        dibujar_canasta(pantalla, estado["jugadora_x"])
        pygame.draw.rect(pantalla, (255, 252, 255), (200, ALTO - 37, 400, 25), border_radius=10)
        texto_centrado(
            pantalla, fuente_texto,
            "Flechas mover | Espacio pausar | R reiniciar", MORADO, ALTO - 25,
        )

        if estado["pausado"]:
            texto_centrado(pantalla, fuente_titulo, "PAUSA", MORADO, ALTO // 2)
        elif estado["pantalla"] in ("victoria", "fin"):
            mensaje = (
                "JARDÍN COMPLETO!"
                if estado["pantalla"] == "victoria"
                else "INTÉNTALO OTRA VEZ!"
            )
            capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            capa.fill((255, 245, 252, 185))
            pantalla.blit(capa, (0, 0))
            texto_centrado(pantalla, fuente_titulo, mensaje, MORADO, ALTO // 2 - 16)
            texto_centrado(
                pantalla, fuente_texto,
                "Presiona R para jugar otra vez", MORADO, ALTO // 2 + 28,
            )

    pygame.display.flip()


def main(max_frames=None):
    """Prepara Pygame y coordina eventos, actualización y renderizado."""
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Pétalos de Luna - Jardin mágico")
    reloj = pygame.time.Clock()
    fuente_titulo = pygame.font.SysFont("arial", 26, bold=True)
    fuente_texto = pygame.font.SysFont("arial", 18)
    estado = nuevo_estado()
    seguir = True
    cuadros = 0

    try:
        while seguir:
            dt = min(reloj.tick(FPS) / 1000.0, DT_MAXIMO)
            seguir = manejar_eventos(estado)
            actualizar(estado, dt)
            dibujar(pantalla, fuente_titulo, fuente_texto, estado)
            cuadros += 1
            # Limite opcional para una comprobación breve del ciclo principal.
            if max_frames is not None and cuadros >= max_frames:
                seguir = False
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
