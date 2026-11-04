"""Escena interactiva de Pygame: Luna llega a una estrella en el jardín."""
import math
import pygame

# Tamaño de ventana y valores que controlan el movimiento.
ANCHO, ALTO = 800, 520
FPS = 60
VELOCIDAD = 230.0
DT_MAXIMO = 0.05
AREA_JUEGO = pygame.Rect(0, 72, ANCHO, ALTO - 126)
PUNTOS_ESTRELLA = tuple(
    (math.cos(-math.pi / 2 + i * math.pi / 5),
     math.sin(-math.pi / 2 + i * math.pi / 5), i % 2 == 0)
    for i in range(10)
)

# Colores pastel para el fondo y los dibujos.
CIELO = (250, 242, 250)
VERDE = (205, 231, 205)
VERDE_OSCURO = (125, 179, 132)
BLANCO = (255, 255, 255)
TEXTO = (72, 54, 78)
ROSA = (244, 151, 190)
ROSA_CLARO = (255, 218, 232)
AMARILLO = (255, 205, 92)
MORADO = (158, 119, 179)
NEGRO = (68, 54, 70)


def crear_estado():
    """Prepara la posición inicial de Luna, la meta y el mensaje."""
    return {
        "jugadora": pygame.Rect(58, 300, 44, 44),
        "meta": pygame.Rect(690, 298, 58, 58),
        "ganaste": False,
    }


def manejar_eventos(estado):
    """Lee los eventos de la ventana y las teclas para reiniciar o salir."""
    continuar = True
    reiniciar = False
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            continuar = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                continuar = False
            elif evento.key == pygame.K_r:
                reiniciar = True
    return continuar, reiniciar


def tecla_presionada(teclas, opciones):
    """Permite revisar tanto el teclado real como teclas simuladas en pruebas."""
    if isinstance(teclas, dict):
        return any(teclas.get(tecla, False) for tecla in opciones)
    return any(teclas[tecla] for tecla in opciones)


def actualizar(estado, dt, teclas=None):
    """Mueve a Luna, la mantiene dentro de la ventana y revisa la colisión."""
    if estado["ganaste"]:
        return
    if teclas is None:
        teclas = pygame.key.get_pressed()

    # El tiempo máximo evita saltos grandes si el juego se pausa un momento.
    dt = min(max(dt, 0.0), DT_MAXIMO)
    izquierda = tecla_presionada(teclas, (pygame.K_LEFT, pygame.K_a))
    derecha = tecla_presionada(teclas, (pygame.K_RIGHT, pygame.K_d))
    arriba = tecla_presionada(teclas, (pygame.K_UP, pygame.K_w))
    abajo = tecla_presionada(teclas, (pygame.K_DOWN, pygame.K_s))
    dx = int(derecha) - int(izquierda)
    dy = int(abajo) - int(arriba)

    # Normalizar el movimiento para que avanzar en diagonal no sea más rápido.
    largo = math.hypot(dx, dy)
    if largo:
        estado["jugadora"].x += round(dx / largo * VELOCIDAD * dt)
        estado["jugadora"].y += round(dy / largo * VELOCIDAD * dt)
    estado["jugadora"].clamp_ip(AREA_JUEGO)

    # Rect.colliderect comprueba si Luna alcanza la estrella.
    if estado["jugadora"].colliderect(estado["meta"]):
        estado["ganaste"] = True


def dibujar_estrella(superficie, centro, radio_exterior=25, radio_interior=11):
    """Dibuja la estrella con sus ángulos calculados una sola vez."""
    puntos = [
        (round(centro[0] + x * (radio_exterior if exterior else radio_interior)),
         round(centro[1] + y * (radio_exterior if exterior else radio_interior)))
        for x, y, exterior in PUNTOS_ESTRELLA
    ]
    pygame.draw.polygon(superficie, AMARILLO, puntos)
    pygame.draw.polygon(superficie, (228, 166, 54), puntos, 2)


def dibujar_personaje(superficie, rect):
    """Dibuja a Luna con figuras simples, sin necesitar imágenes externas."""
    x, y = rect.x, rect.y
    # Orejas y cara de la conejita.
    pygame.draw.ellipse(superficie, ROSA, (x + 7, y - 14, 12, 27))
    pygame.draw.ellipse(superficie, ROSA, (x + 25, y - 14, 12, 27))
    pygame.draw.ellipse(superficie, ROSA_CLARO, (x + 10, y - 10, 6, 17))
    pygame.draw.ellipse(superficie, ROSA_CLARO, (x + 28, y - 10, 6, 17))
    pygame.draw.circle(superficie, ROSA, rect.center, 22)
    pygame.draw.circle(superficie, NEGRO, (x + 15, y + 20), 2)
    pygame.draw.circle(superficie, NEGRO, (x + 29, y + 20), 2)
    pygame.draw.circle(superficie, ROSA_CLARO, (x + 11, y + 27), 4)
    pygame.draw.circle(superficie, ROSA_CLARO, (x + 33, y + 27), 4)
    pygame.draw.circle(superficie, BLANCO, (x + 22, y + 26), 3)
    # Un pequeño moño completa el personaje.
    pygame.draw.circle(superficie, MORADO, (x + 22, y - 8), 4)
    pygame.draw.circle(superficie, MORADO, (x + 17, y - 8), 3)
    pygame.draw.circle(superficie, MORADO, (x + 27, y - 8), 3)


def crear_fondo(fuente_titulo, fuente_ui):
    """Dibuja una vez el fondo y las etiquetas que no cambian."""
    fondo = pygame.Surface((ANCHO, ALTO))
    fondo.fill(CIELO)
    # Nubes, jardín y flores decorativas estáticas.
    pygame.draw.circle(fondo, BLANCO, (130, 150), 24)
    pygame.draw.circle(fondo, BLANCO, (157, 140), 30)
    pygame.draw.circle(fondo, BLANCO, (185, 151), 22)
    pygame.draw.rect(fondo, VERDE, (0, 260, ANCHO, ALTO - 260))
    pygame.draw.ellipse(fondo, (222, 240, 213), (-90, 230, 430, 150))
    pygame.draw.ellipse(fondo, (219, 238, 212), (430, 245, 500, 145))
    for fx, fy in ((120, 405), (228, 365), (330, 430), (505, 390), (610, 440)):
        pygame.draw.line(fondo, VERDE_OSCURO, (fx, fy), (fx, fy + 20), 3)
        pygame.draw.circle(fondo, ROSA, (fx, fy), 6)
        pygame.draw.circle(fondo, AMARILLO, (fx, fy), 2)

    # Panel con el nombre y una instrucción corta.
    pygame.draw.rect(fondo, BLANCO, (22, 18, ANCHO - 44, 48), border_radius=12)
    fondo.blit(fuente_titulo.render("Luna y la estrella", True, TEXTO), (38, 25))
    texto_meta = fuente_ui.render("Llega a la estrella amarilla", True, TEXTO)
    fondo.blit(texto_meta, (ANCHO - texto_meta.get_width() - 38, 33))
    pygame.draw.rect(fondo, BLANCO, (22, ALTO - 48, ANCHO - 44, 30), border_radius=9)
    controles = fuente_ui.render("Flechas o WASD: mover     R: empezar de nuevo     ESC: salir", True, TEXTO)
    fondo.blit(controles, (34, ALTO - 41))
    return fondo


def dibujar_escena(superficie, estado, fondo, mensaje_victoria):
    """Dibuja el fondo guardado, los elementos móviles y el resultado."""
    superficie.blit(fondo, (0, 0))
    # La meta se dibuja detrás de Luna para que la colisión sea visible.
    pygame.draw.circle(superficie, (255, 237, 184), estado["meta"].center, 34)
    dibujar_estrella(superficie, estado["meta"].center)
    dibujar_personaje(superficie, estado["jugadora"])

    # Solo se dibuja el mensaje extra cuando se completa el objetivo.
    if estado["ganaste"]:
        panel = pygame.Rect(180, 205, 440, 76)
        pygame.draw.rect(superficie, BLANCO, panel, border_radius=16)
        pygame.draw.rect(superficie, ROSA, panel, width=3, border_radius=16)
        superficie.blit(mensaje_victoria, mensaje_victoria.get_rect(center=panel.center))


def main(max_frames=None):
    """Inicializa Pygame, ejecuta el bucle principal y cierra la ventana."""
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Luna y la estrella")
    reloj = pygame.time.Clock()
    fuente_titulo = pygame.font.SysFont("arial", 24, bold=True)
    fuente_ui = pygame.font.SysFont("arial", 16)
    # Se preparan una vez el escenario y el texto para no volverlos a crear cada cuadro.
    fondo = crear_fondo(fuente_titulo, fuente_ui)
    mensaje_victoria = fuente_titulo.render("¡Llegaste a la estrella!", True, TEXTO)
    estado = crear_estado()
    continuar = True
    cuadros = 0
    try:
        while continuar:
            dt = min(reloj.tick(FPS) / 1000.0, DT_MAXIMO)
            continuar, reiniciar = manejar_eventos(estado)
            if reiniciar:
                estado = crear_estado()
            actualizar(estado, dt) 
            dibujar_escena(pantalla, estado, fondo, mensaje_victoria)
            pygame.display.flip()
            cuadros += 1
            # Este límite opcional permite comprobar que el ciclo abre y cierra.
            if max_frames is not None and cuadros >= max_frames:
                continuar = False
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
