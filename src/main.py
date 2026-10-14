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
COLOR_COIN = (255, 215, 0)
COLOR_CHECKPOINT = (50, 255, 150)
COLOR_EYES = (255, 255, 255)
COLOR_PUPIL = (10, 10, 20)

# --- REPRESENTAÇÃO DA FASE 1 EM TEXTO ---
FASE_NIVEL_1 = (
    "    ^   11   O   ^^   22   ^   C   ^   O   ^   N   ^^   G   111   O   ^^^   END"
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

        # Jump Buffer
        self.jump_buffer = 0

        # Estado Elemental
        self.modo = "GOSMA"
        self.color = COLOR_SLIME_GOSMA
        self.gravity = 1.0
        self.jump_strength = -15.0
        self.is_grounded = False

        # Visual de Deformação
        self.current_width = float(self.base_size)
        self.current_height = float(self.base_size)
        self.rect = pygame.Rect(x, y, self.base_size, self.base_size)

    def get_hitbox(self) -> pygame.Rect:
        return self.rect.inflate(-10, -6)

    def mudar_modo(self, novo_modo: str):
        self.modo = novo_modo
        if novo_modo == "GOSMA":
            self.color = COLOR_SLIME_GOSMA
            self.gravity = 1.0
            self.jump_strength = -15.0
        elif novo_modo == "CHICLETE":
            self.color = COLOR_SLIME_CHICLETE
            self.gravity = 0.45
            self.jump_strength = -8.5
        elif novo_modo == "NEVE":
            self.color = COLOR_SLIME_NEVE
            self.gravity = -1.0
            self.jump_strength = 15.0

    def solicitar_pulo(self):
        self.jump_buffer = 8

    def tentar_pular(self):
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
                self.vel_y = self.jump_strength
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
        if self.jump_buffer > 0:
            self.jump_buffer -= 1

        if space_held:
            self.jump_buffer = 4

        self.tentar_pular()

        self.vel_y += self.gravity
        self.y += self.vel_y

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
                self.tentar_pular()

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
    pygame.display.set_caption("Slime Dash - Complete Core Engine v1.0")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 20, bold=True)
    title_font = pygame.font.SysFont("Consolas", 48, bold=True)

    floor_y = 580
    ceiling_y = 100
    scroll_speed = 6.0
    tile_size = 60

    largura_total_fase = len(FASE_NIVEL_1) * tile_size

    distancia_percorrida = 0.0
    tentativas = 1
    moedas_coletadas = 0
    moedas_pegas_ids = set()
    vitoria = False

    # Estado de Checkpoint / Modo Treino
    checkpoint = None  # Formato: (distancia, modo_slime, y_slime)

    slime = Slime(x=180, y=300)
    particles = []

    def reset_game():
        nonlocal distancia_percorrida, tentativas, moedas_coletadas, vitoria
        tentativas += 1
        vitoria = False

        if checkpoint is not None:
            # Restaura do Checkpoint (Modo Treino)
            distancia_percorrida = checkpoint["distancia"]
            slime.mudar_modo(checkpoint["modo"])
            slime.y = checkpoint["y"]
            slime.vel_y = 0
        else:
            # Reinício Completo do 0%
            distancia_percorrida = 0.0
            moedas_coletadas = 0
            moedas_pegas_ids.clear()
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
                elif event.key == pygame.K_r:
                    reset_game()  # Atalho de QA para resetar
                elif event.key == pygame.K_z:
                    # Salva Checkpoint (Modo Treino)
                    checkpoint = {
                        "distancia": distancia_percorrida,
                        "modo": slime.modo,
                        "y": slime.y,
                    }
                    for _ in range(10):
                        particles.append(
                            Particle(slime.x, slime.y, COLOR_CHECKPOINT)
                        )
                elif event.key == pygame.K_x:
                    # Remove Checkpoint
                    checkpoint = None
                elif event.key == pygame.K_SPACE:
                    if vitoria:
                        reset_game()
                    else:
                        slime.solicitar_pulo()

        keys = pygame.key.get_pressed()
        space_held = keys[pygame.K_SPACE]

        # Loop Principal
        if not vitoria:
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
        moedas = []
        fim_fase_x = None

        for i, char in enumerate(FASE_NIVEL_1):
            obj_x = (i * tile_size) + 600 - distancia_percorrida

            if char == "E":
                fim_fase_x = obj_x

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
                elif char == "O" and i not in moedas_pegas_ids:
                    coin_rect = pygame.Rect(obj_x + 18, floor_y - 80, 24, 24)
                    moedas.append((coin_rect, i))

        slime_hb = slime.get_hitbox()

        # Regras de Colisão e Lógica
        if not vitoria:
            for portal_rect, tipo in portais:
                if slime_hb.colliderect(portal_rect):
                    if tipo == "C" and slime.modo != "CHICLETE":
                        slime.mudar_modo("CHICLETE")
                    elif tipo == "N" and slime.modo != "NEVE":
                        slime.mudar_modo("NEVE")
                    elif tipo == "G" and slime.modo != "GOSMA":
                        slime.mudar_modo("GOSMA")

            for coin_rect, coin_id in moedas:
                if slime_hb.colliderect(coin_rect):
                    moedas_pegas_ids.add(coin_id)
                    moedas_coletadas += 1
                    for _ in range(8):
                        particles.append(
                            Particle(
                                coin_rect.centerx,
                                coin_rect.centery,
                                COLOR_COIN,
                            )
                        )

            for spike in espinhos_rects:
                spike_hb = spike.inflate(-18, -14).move(0, 6)
                if slime_hb.colliderect(spike_hb):
                    reset_game()

            for block in blocos_rects:
                if slime_hb.colliderect(block):
                    pes_do_slime = slime.rect.bottom
                    topo_do_slime = slime.rect.top

                    if (
                        slime.gravity > 0
                        and slime.vel_y >= -3.0
                        and pes_do_slime <= block.top + 22
                    ):
                        slime.y = block.top - slime.current_height / 2
                        slime.vel_y = 0
                        slime.is_grounded = True
                        slime.tentar_pular()

                    elif (
                        slime.gravity < 0
                        and slime.vel_y <= 3.0
                        and topo_do_slime >= block.bottom - 22
                    ):
                        slime.y = block.bottom + slime.current_height / 2
                        slime.vel_y = 0
                        slime.is_grounded = True
                        slime.tentar_pular()

                    else:
                        reset_game()

            if fim_fase_x is not None and slime.x >= fim_fase_x:
                vitoria = True

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

        for coin_rect, _ in moedas:
            pygame.draw.circle(screen, COLOR_COIN, coin_rect.center, 12)
            pygame.draw.circle(screen, (255, 255, 200), coin_rect.center, 6)

        for p in particles:
            p.draw(screen)

        slime.draw(screen)

        # UI
        porcentagem = min(
            100, int((distancia_percorrida / largura_total_fase) * 100)
        )
        if vitoria:
            porcentagem = 100

        bar_width = 400
        bar_height = 16
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = 20

        pygame.draw.rect(
            screen,
            (50, 40, 70),
            (bar_x, bar_y, bar_width, bar_height),
            border_radius=8,
        )
        pygame.draw.rect(
            screen,
            COLOR_SLIME_GOSMA,
            (bar_x, bar_y, int(bar_width * (porcentagem / 100)), bar_height),
            border_radius=8,
        )

        txt_pct = font.render(f"{porcentagem}%", True, (255, 255, 255))
        screen.blit(txt_pct, (bar_x + bar_width + 15, bar_y - 2))

        # Indicadores Laterais
        txt_tentativas = font.render(
            f"Tentativa: {tentativas}", True, (255, 255, 255)
        )
        txt_moedas = font.render(
            f"Moedas: {moedas_coletadas}/3", True, COLOR_COIN
        )
        screen.blit(txt_tentativas, (20, 50))
        screen.blit(txt_moedas, (20, 80))

        # Painel do Modo Treino / Checkpoint (UI)
        if checkpoint is not None:
            txt_chk = font.render(
                "[Z] Checkpoint Ativo | [X] Remover Checkpoint",
                True,
                COLOR_CHECKPOINT,
            )
            screen.blit(txt_chk, (20, 110))

        # Tela de Vitória
        if vitoria:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            screen.blit(s, (0, 0))

            txt_vic = title_font.render(
                "FASE CONCLUÍDA!", True, COLOR_SLIME_GOSMA
            )
            txt_sub = font.render(
                f"Moedas Secretas: {moedas_coletadas}/3  |  Pressione ESPAÇO para reiniciar",
                True,
                (255, 255, 255),
            )
            screen.blit(
                txt_vic, (SCREEN_WIDTH // 2 - txt_vic.get_width() // 2, 280)
            )
            screen.blit(
                txt_sub, (SCREEN_WIDTH // 2 - txt_sub.get_width() // 2, 360)
            )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()