import math
import random
import sys
import pygame

# --- CONFIGURAÇÕES GLOBAIS ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Cores
COLOR_BG = (15, 12, 25)
COLOR_FLOOR = (40, 30, 60)
COLOR_SLIME_GOSMA = (50, 240, 100)
COLOR_SLIME_CHICLETE = (255, 105, 180)
COLOR_SLIME_NEVE = (135, 206, 250)
COLOR_SPIKE = (230, 50, 50)
COLOR_BLOCK = (80, 70, 110)
COLOR_EYES = (255, 255, 255)
COLOR_PUPIL = (10, 10, 20)

# --- REPRESENTAÇÃO DA FASE 1 EM TEXTO ---
FASE_NIVEL_1 = (
    "    ^   11   ^^   22   ^   C   ^   ^   N   ^^   G   111   ^^^   END"
)


class Particle:

    def __init__(self, x: float, y: float, color: tuple):
        self.x = x
        self.y = y
        self.color = color
        self.radius = random.randint(3, 6)
        self.vel_x = random.uniform(-2, -0.5)
        self.vel_y = random.uniform(-1.5, 1.5)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.radius = max(0, self.radius - 0.15)

    def draw(self, surface: pygame.Surface):
        if self.radius > 0:
            pygame.draw.circle(
                surface, self.color, (int(self.x), int(self.y)), int(self.radius)
            )


class Slime(pygame.sprite.Sprite):

    def __init__(self, x: int, y: int):
        super().__init__()
        self.base_size = 36
        self.x = float(x)
        self.y = float(y)
        self.vel_y = 0.0

        # Jump Buffer (Tolerância de entrada para pulos perfeitos)
        self.jump_buffer = 0

        # Estado Elemental
        self.modo = "GOSMA"  # "GOSMA", "CHICLETE", "NEVE"
        self.color = COLOR_SLIME_GOSMA
        self.gravity = 1.0  # Gravidade mais firme e rápida
        self.jump_strength = -15.0  # Pulo responsivo
        self.is_grounded = False

        # Visual de Deformação
        self.current_width = float(self.base_size)
        self.current_height = float(self.base_size)
        self.rect = pygame.Rect(x, y, self.base_size, self.base_size)

    def mudar_modo(self, novo_modo: str):
        """Transição de Estado do Slime ao passar por um Portal"""
        self.modo = novo_modo
        if novo_modo == "GOSMA":
            self.color = COLOR_SLIME_GOSMA
            self.gravity = 1.0
            self.jump_strength = -15.0
        elif novo_modo == "CHICLETE":
            self.color = COLOR_SLIME_CHICLETE
            self.gravity = 0.45  # Voo suave estilo Flappy
            self.jump_strength = -8.5
        elif novo_modo == "NEVE":
            self.color = COLOR_SLIME_NEVE
            self.gravity = -1.0  # Gravidade invertida para o teto
            self.jump_strength = 15.0

    def solicitar_pulo(self):
        """Ativa a intenção de pulo (Buffer de entrada)"""
        self.jump_buffer = 8  # Tenta pular pelos próximos 8 frames (~0.13s)

    def tentar_pular(self):
        """Executa o pulo se houver buffer ativo e o Slime estiver apto"""
        if self.jump_buffer > 0:
            if self.modo == "GOSMA" and self.is_grounded:
                self.vel_y = self.jump_strength
                self.is_grounded = False
                self.jump_buffer = 0
                self.current_width, self.current_height = 24.0, 48.0
            elif self.modo == "CHICLETE":
                self.vel_y = self.jump_strength
                self.jump_buffer = 0
                self.current_width, self.current_height = 28.0, 42.0
            elif self.modo == "NEVE" and self.is_grounded:
                self.vel_y = self.jump_strength  # Empurra para baixo (descola do teto)
                self.is_grounded = False
                self.jump_buffer = 0
                self.current_width, self.current_height = 24.0, 48.0

    def update(
        self,
        floor_y: int,
        ceiling_y: int,
        particles: list,
        space_held: bool = False,
    ):
        # 1. Atualiza Buffer de Pulo
        if self.jump_buffer > 0:
            self.jump_buffer -= 1

        if space_held:
            self.jump_buffer = 4  # Mantém o buffer ativo se a tecla estiver segurada

        # Tenta disparar o pulo
        self.tentar_pular()

        # 2. Aplica Gravidade
        self.vel_y += self.gravity
        self.y += self.vel_y

        # 3. Colisão com o Chão (Gravidade Positiva)
        if self.gravity > 0:
            slime_bottom = self.y + self.current_height / 2
            if slime_bottom >= floor_y:
                if not self.is_grounded:
                    self.current_width, self.current_height = 46.0, 24.0
                    for _ in range(5):
                        particles.append(
                            Particle(self.x, floor_y - 5, self.color)
                        )
                self.y = floor_y - self.current_height / 2
                self.vel_y = 0
                self.is_grounded = True
                self.tentar_pular()  # Pula instantaneamente se o buffer estiver ativo

        # 4. Colisão com o Teto (Modo Neve / Gravidade Negativa)
        elif self.gravity < 0:
            slime_top = self.y - self.current_height / 2
            if slime_top <= ceiling_y:
                if not self.is_grounded:
                    self.current_width, self.current_height = 46.0, 24.0
                    for _ in range(5):
                        particles.append(
                            Particle(self.x, ceiling_y + 5, self.color)
                        )
                self.y = ceiling_y + self.current_height / 2
                self.vel_y = 0
                self.is_grounded = True
                self.tentar_pular()

        # 5. Recuperação Elástica
        self.current_width += (self.base_size - self.current_width) * 0.2
        self.current_height += (self.base_size - self.current_height) * 0.2

        self.rect = pygame.Rect(
            int(self.x - self.current_width / 2),
            int(self.y - self.current_height / 2),
            int(self.current_width),
            int(self.current_height),
        )

    def draw(self, surface: pygame.Surface):
        pygame.draw.ellipse(surface, self.color, self.rect)
        eye_y = self.rect.centery - (2 if self.gravity > 0 else -2)
        pygame.draw.circle(
            surface, COLOR_EYES, (self.rect.centerx - 4, eye_y), 4
        )
        pygame.draw.circle(
            surface, COLOR_EYES, (self.rect.centerx + 4, eye_y), 4
        )
        pygame.draw.circle(
            surface, COLOR_PUPIL, (self.rect.centerx - 4, eye_y), 2
        )
        pygame.draw.circle(
            surface, COLOR_PUPIL, (self.rect.centerx + 4, eye_y), 2
        )


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Slime Dash - Smooth Jump Engine v0.4")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 24, bold=True)

    floor_y = 580
    ceiling_y = 100
    scroll_speed = 6.0
    distancia_percorrida = 0.0
    tentativas = 1

    slime = Slime(x=180, y=300)
    particles = []

    def reset_game():
        nonlocal distancia_percorrida, tentativas
        distancia_percorrida = 0.0
        tentativas += 1
        slime.mudar_modo("GOSMA")
        slime.y = 300
        slime.vel_y = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    slime.solicitar_pulo()

        keys = pygame.key.get_pressed()
        space_held = keys[pygame.K_SPACE]

        # Atualizações
        distancia_percorrida += scroll_speed
        slime.update(floor_y, ceiling_y, particles, space_held)

        for p in particles[:]:
            p.update()
            if p.radius <= 0:
                particles.remove(p)

        # Matriz da Fase
        espinhos_rects = []
        blocos_rects = []
        portais = []

        tile_size = 60
        for i, char in enumerate(FASE_NIVEL_1):
            obj_x = (i * tile_size) + 600 - distancia_percorrida

            if -100 < obj_x < SCREEN_WIDTH + 100:
                if char == "^":
                    spike_rect = pygame.Rect(
                        obj_x + 10, floor_y - 40, tile_size - 20, 40
                    )
                    espinhos_rects.append(spike_rect)
                elif char in ("1", "2"):
                    altura = 50 if char == "1" else 100
                    block_rect = pygame.Rect(
                        obj_x, floor_y - altura, tile_size, altura
                    )
                    blocos_rects.append(block_rect)
                elif char in ("C", "N", "G"):
                    portal_rect = pygame.Rect(obj_x, floor_y - 120, 30, 120)
                    portais.append((portal_rect, char))

        # Colisões
        for portal_rect, tipo in portais:
            if slime.rect.colliderect(portal_rect):
                if tipo == "C" and slime.modo != "CHICLETE":
                    slime.mudar_modo("CHICLETE")
                elif tipo == "N" and slime.modo != "NEVE":
                    slime.mudar_modo("NEVE")
                elif tipo == "G" and slime.modo != "GOSMA":
                    slime.mudar_modo("GOSMA")

        for spike in espinhos_rects:
            if slime.rect.colliderect(spike):
                reset_game()

        for block in blocos_rects:
            if slime.rect.colliderect(block):
                if (
                    slime.rect.right > block.left
                    and slime.rect.left < block.left
                ):
                    reset_game()

        # Renderização
        screen.fill(COLOR_BG)
        pygame.draw.rect(
            screen,
            COLOR_FLOOR,
            (0, floor_y, SCREEN_WIDTH, SCREEN_HEIGHT - floor_y),
        )
        pygame.draw.rect(screen, COLOR_FLOOR, (0, 0, SCREEN_WIDTH, ceiling_y))

        for spike in espinhos_rects:
            pygame.draw.polygon(
                screen,
                COLOR_SPIKE,
                [
                    spike.bottomleft,
                    (spike.centerx, spike.top),
                    spike.bottomright,
                ],
            )

        for block in blocos_rects:
            pygame.draw.rect(screen, COLOR_BLOCK, block)
            pygame.draw.rect(screen, (120, 110, 150), block, 2)

        for portal_rect, tipo in portais:
            p_color = (
                COLOR_SLIME_CHICLETE
                if tipo == "C"
                else (COLOR_SLIME_NEVE if tipo == "N" else COLOR_SLIME_GOSMA)
            )
            pygame.draw.rect(screen, p_color, portal_rect, 4)

        for p in particles:
            p.draw(screen)

        slime.draw(screen)

        # UI
        txt_tentativas = font.render(
            f"Tentativa: {tentativas}", True, (255, 255, 255)
        )
        txt_modo = font.render(f"Modo: {slime.modo}", True, slime.color)
        screen.blit(txt_tentativas, (20, 20))
        screen.blit(txt_modo, (20, 50))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()