import pygame as pg
import os
import random
pg.init()

TILE = 40
COLUMNAS = 21
FILAS = 15

SCREEN = pg.display.set_mode((COLUMNAS * TILE, FILAS * TILE))
pg.display.set_caption("Laberinto del Gato")

FPS = 60
CLOCK = pg.time.Clock()

TAM_GATO = 35

def cargar_frames(carpeta):

    frames = []

    archivos = sorted(os.listdir(carpeta))

    for archivo in archivos:

        ruta = os.path.join(carpeta, archivo)

        img = pg.image.load(ruta).convert_alpha()

        img = pg.transform.smoothscale(
            img,
            (TAM_GATO, TAM_GATO)
        )

        frames.append(img)

    return frames

# Frames del gato
ani_der = cargar_frames("derecha")
ani_izq = cargar_frames("izquierda")
ani_arr = cargar_frames("arriba")
ani_aba = cargar_frames("abajo")

def generar_laberinto(cols, filas):

    cols = cols if cols % 2 == 1 else cols - 1
    filas = filas if filas % 2 == 1 else filas - 1

    mapa = [["1" for _ in range(cols)] for _ in range(filas)]

    def dfs(x, y):

        mapa[y][x] = "0"

        direcciones = [
            (2, 0),
            (-2, 0),
            (0, 2),
            (0, -2)
        ]

        random.shuffle(direcciones)

        for dx, dy in direcciones:

            nx = x + dx
            ny = y + dy

            if 0 < nx < cols - 1 and 0 < ny < filas - 1:

                if mapa[ny][nx] == "1":

                    mapa[y + dy // 2][x + dx // 2] = "0"

                    dfs(nx, ny)

    dfs(1, 1)

    return ["".join(fila) for fila in mapa]

mapa = []
paredes = []

inicio = (1, 1)
meta = (COLUMNAS - 2, FILAS - 2)

# GATO
class Gato(pg.sprite.Sprite):

    def __init__(self, pos):

        super().__init__()

        self.ani_derecha = ani_der
        self.ani_izquierda = ani_izq
        self.ani_arriba = ani_arr
        self.ani_abajo = ani_aba

        self.image = self.ani_derecha[0]

        self.rect = self.image.get_rect(
            topleft=pos
        )

        self.hitbox = pg.Rect(
            self.rect.x + 10,
            self.rect.y + 10,
            self.rect.width - 20,
            self.rect.height - 20
        )

        self.index = 0
        self.contador = 0

        self.vel_anim = 5

        self.speed = 3

        self.direction = "DER"

    def mover(self, dx, dy):

        # Movimiento X
        self.hitbox.x += dx

        for pared in paredes:

            if self.hitbox.colliderect(pared):

                if dx > 0:
                    self.hitbox.right = pared.left

                if dx < 0:
                    self.hitbox.left = pared.right

        # Movimiento Y
        self.hitbox.y += dy

        for pared in paredes:

            if self.hitbox.colliderect(pared):

                if dy > 0:
                    self.hitbox.bottom = pared.top

                if dy < 0:
                    self.hitbox.top = pared.bottom

        # Actualizar sprite visual
        self.rect.center = self.hitbox.center

    def update(self):

        self.contador += 1

        if self.contador >= self.vel_anim:

            self.contador = 0

            self.index += 1

            if self.direction == "DER":

                self.index %= len(self.ani_derecha)

                self.image = self.ani_derecha[self.index]

            elif self.direction == "IZQ":

                self.index %= len(self.ani_izquierda)

                self.image = self.ani_izquierda[self.index]

            elif self.direction == "ARR":

                self.index %= len(self.ani_arriba)

                self.image = self.ani_arriba[self.index]

            elif self.direction == "ABJ":

                self.index %= len(self.ani_abajo)

                self.image = self.ani_abajo[self.index]

    def hevent(self, key):

        dx = 0
        dy = 0

        if key[pg.K_LEFT]:

            dx = -self.speed
            self.direction = "IZQ"

        elif key[pg.K_RIGHT]:

            dx = self.speed
            self.direction = "DER"

        elif key[pg.K_UP]:

            dy = -self.speed
            self.direction = "ARR"

        elif key[pg.K_DOWN]:

            dy = self.speed
            self.direction = "ABJ"

        else:
            self.index = 0

        self.mover(dx, dy)

gato = Gato((
    inicio[0] * TILE + 5,
    inicio[1] * TILE + 5
))

g_sprites = pg.sprite.Group()
g_sprites.add(gato)

def nuevo_nivel():

    global mapa
    global paredes
    global meta

    mapa = generar_laberinto(
        COLUMNAS,
        FILAS
    )

    paredes = []

    for y, fila in enumerate(mapa):

        for x, col in enumerate(fila):

            if col == "1":

                paredes.append(
                    pg.Rect(
                        x * TILE,
                        y * TILE,
                        TILE,
                        TILE
                    )
                )

    # Meta
    meta = (COLUMNAS - 2, FILAS - 2)

    # Reiniciar gato
    gato.hitbox.topleft = (
        inicio[0] * TILE + 10,
        inicio[1] * TILE + 10
    )

    gato.rect.center = gato.hitbox.center


# Crear primer laberinto
nuevo_nivel()

run = True

while run:

    CLOCK.tick(FPS)

    for event in pg.event.get():

        if event.type == pg.QUIT:

            run = False

    key = pg.key.get_pressed()

    gato.hevent(key)

    # Update
    g_sprites.update()

    # Fondo blanco
    SCREEN.fill((255, 255, 255))

    for pared in paredes:

        pared_visual = pg.Rect(
            pared.x + 10,
            pared.y + 10,
            TILE - 20,
            TILE - 20
        )

        pg.draw.rect(
            SCREEN,
            (0, 0, 0),
            pared_visual
        )

    # META VERDE
    pg.draw.rect(
        SCREEN,
        (0, 255, 0),
        (
            meta[0] * TILE + 5,
            meta[1] * TILE + 5,
            TILE - 10,
            TILE - 10
        )
    )

    # Dibujar gato
    g_sprites.draw(SCREEN)

    jugador_tile = (
        gato.hitbox.centerx // TILE,
        gato.hitbox.centery // TILE
    )

    if jugador_tile == meta:

        print("¡NUEVO LABERINTO!")

        nuevo_nivel()

    pg.display.flip()

pg.quit()