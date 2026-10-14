import math
import random
import sys
import os
import pygame

# Importação com Fallback Seguro para rodar direto ou via unittest
try:
    from src.levels import NIVEIS, obter_configuracao_nivel
except ModuleNotFoundError:
    from levels import NIVEIS, obter_configuracao_nivel

# --- CONFIGURAÇÕES GLOBAIS ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Cores Base
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


class SoundManager:

    def __init__(self):
        self.sounds_enabled = True
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except Exception:
            self.sounds_enabled = False

        self.sfx_jump = self._gerar_som_sintetico(frequencia=520, duracao_ms=60)
        self.sfx_coin = self._gerar_som_sintetico(frequencia=980, duracao_ms=100)
        self.sfx_death = self._gerar_som_sintetico(frequencia=130, duracao_ms=180)

        self.carregar_e_tocar_musica("assets/fase1.mp3")

    def _gerar_som_sintetico(self, frequencia: int, duracao_ms: int):
        if not self.sounds_enabled:
            return None
        try:
            import numpy as np
            sample_rate = 44100
            n_samples = int(sample_rate * (duracao_ms / 1000.0))
            t = np.linspace(0, duracao_ms / 1000.0, n_samples, False)
            waveform = np.sin(2 * np.pi * frequencia * t) * 0.2
            sound_array = np.int16(waveform * 32767)
            sound_array = np.column_stack((sound_array, sound_array))
            return pygame.sndarray.make_sound(sound_array)
        except Exception:
            return None

    def carregar_e_tocar_musica(self, caminho_musica: str):
        if self.sounds_enabled and os.path.exists(caminho_musica):
            try:
                pygame.mixer.music.load(caminho_musica)
                pygame.mixer.music.set_volume(0.6)
                pygame.mixer.music.play(-1)
            except Exception:
                pass

    def reiniciar_musica(self):
        if self.sounds_enabled and pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.rewind()
                pygame.mixer.music.play(-1)
            except Exception:
                pass

    def tocar(self, som):
        if self.sounds_enabled and som is not None:
            try:
                som.play()
            except Exception:
                pass


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

        self.jump_buffer = 0
        self.modo = "GOSMA"
        self.color = COLOR_SLIME_GOSMA
        self.gravity = 1.0
        self.jump_strength = -15.0
        self.is_grounded = False

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

    def tentar_pular(self, sound_mgr: SoundManager = None):
        if self.jump_buffer > 0:
            poulou = False
            if self.modo == "GOSMA" and self.is_grounded:
                self.vel_y = self.jump_strength
                self.is_grounded = False
                self.jump_buffer = 0
                self.current_width, self.current_height = 24.0, 48.0
                poulou = True
            elif self.modo == "CHICLETE":
                self.vel_y = self.jump_strength
                self.jump_buffer = 0
                self.current_width, self.current_height = 28.0, 42.0
                poulou = True
            elif self.modo == "NEVE" and self.is_grounded:
                self.vel_y = self.jump_strength
                self.is_grounded = False
                self.jump_buffer = 0
                self.current_width, self.current_height = 24.0, 48.0
                poulou = True

            if poulou and sound_mgr is not None:
                sound_mgr.tocar(sound_mgr.sfx_jump)

    def update(
        self,
        floor_y: int,
        ceiling_y: int,
        particles: list,
        space_held: bool = False,
        sound_mgr: SoundManager = None,
    ):
        if self.jump_buffer > 0:
            self.jump_buffer -= 1

        if space_held:
            self.jump_buffer = 4

        self.tentar_pular(sound_mgr)

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
                self.tentar_pular(sound_mgr)

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
                self.tentar_pular(sound_mgr)

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
    sound_mgr = SoundManager()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Slime Dash - Multi-Level Progression Engine v2.3")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 20, bold=True)
    title_font = pygame.font.SysFont("Consolas", 48, bold=True)

    floor_y = 580
    ceiling_y = 100
    scroll_speed = 6.0
    tile_size = 60

    # Controle de Progressão de Nível
    id_nivel_atual = 1
    config_nivel = obter_configuracao_nivel(id_nivel_atual)
    fase_texto = config_nivel["fase"]
    bpm_atual = config_nivel["bpm"]
    largura_total_fase = len(fase_texto) * tile_size

    distancia_percorrida = 0.0
    tentativas = 1
    moedas_coletadas = 0
    moedas_pegas_ids = set()
    vitoria = False
    jogo_zerado = False

    frames_contador = 0
    frames_por_batida = int((60 * FPS) / bpm_atual)
    beat_pulse = 0.0

    checkpoint = None
    slime = Slime(x=180, y=300)
    particles = []

    def carregar_nivel(id_nivel: int):
        nonlocal config_nivel, fase_texto, bpm_atual, largura_total_fase
        nonlocal distancia_percorrida, moedas_coletadas, moedas_pegas_ids
        nonlocal vitoria, checkpoint, frames_por_batida

        config_nivel = obter_configuracao_nivel(id_nivel)
        fase_texto = config_nivel["fase"]
        bpm_atual = config_nivel["bpm"]
        largura_total_fase = len(fase_texto) * tile_size
        frames_por_batida = int((60 * FPS) / bpm_atual)

        distancia_percorrida = 0.0
        moedas_coletadas = 0
        moedas_pegas_ids.clear()
        checkpoint = None
        vitoria = False

        slime.mudar_modo("GOSMA")
        slime.y = 300
        slime.vel_y = 0

    def reset_game():
        nonlocal distancia_percorrida, tentativas, moedas_coletadas, vitoria
        tentativas += 1
        vitoria = False
        sound_mgr.tocar(sound_mgr.sfx_death)
        sound_mgr.reiniciar_musica()

        if checkpoint is not None:
            distancia_percorrida = checkpoint["distancia"]
            slime.mudar_modo(checkpoint["modo"])
            slime.y = checkpoint["y"]
            slime.vel_y = 0
        else:
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
                    reset_game()
                elif event.key == pygame.K_z:
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
                    checkpoint = None
                elif event.key == pygame.K_SPACE:
                    if vitoria:
                        if id_nivel_atual < len(NIVEIS):
                            id_nivel_atual += 1
                            carregar_nivel(id_nivel_atual)
                        else:
                            # Se concluiu a última fase, reinicia do nível 1
                            id_nivel_atual = 1
                            carregar_nivel(id_nivel_atual)
                            jogo_zerado = False
                    else:
                        slime.solicitar_pulo()

        keys = pygame.key.get_pressed()
        space_held = keys[pygame.K_SPACE]

        frames_contador += 1
        if frames_contador % frames_por_batida == 0:
            beat_pulse = 1.0
        else:
            beat_pulse = max(0.0, beat_pulse - 0.1)

        if not vitoria:
            distancia_percorrida += scroll_speed
            slime.update(
                floor_y, ceiling_y, particles, space_held, sound_mgr
            )

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

        for i, char in enumerate(fase_texto):
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
                    sound_mgr.tocar(sound_mgr.sfx_coin)
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
                        slime.tentar_pular(sound_mgr)

                    elif (
                        slime.gravity < 0
                        and slime.vel_y <= 3.0
                        and topo_do_slime >= block.bottom - 22
                    ):
                        slime.y = block.bottom + slime.current_height / 2
                        slime.vel_y = 0
                        slime.is_grounded = True
                        slime.tentar_pular(sound_mgr)

                    else:
                        reset_game()

            if fim_fase_x is not None and slime.x >= fim_fase_x:
                vitoria = True
                if id_nivel_atual == len(NIVEIS):
                    jogo_zerado = True

        screen.fill(COLOR_BG)

        pygame.draw.rect(
            screen,
            COLOR_FLOOR,
            (0, floor_y, SCREEN_WIDTH, SCREEN_HEIGHT - floor_y),
        )
        pygame.draw.rect(screen, COLOR_FLOOR, (0, 0, SCREEN_WIDTH, ceiling_y))

        line_bright = int(120 + beat_pulse * 100)
        pygame.draw.line(
            screen,
            (0, line_bright, int(line_bright * 0.8)),
            (0, floor_y),
            (SCREEN_WIDTH, floor_y),
            3,
        )

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
            config_nivel["cor_tema"],
            (bar_x, bar_y, int(bar_width * (porcentagem / 100)), bar_height),
            border_radius=8,
        )

        txt_pct = font.render(f"{porcentagem}%", True, (255, 255, 255))
        screen.blit(txt_pct, (bar_x + bar_width + 15, bar_y - 2))

        txt_nome = font.render(config_nivel["nome"], True, config_nivel["cor_tema"])
        txt_tentativas = font.render(f"Tentativa: {tentativas}", True, (255, 255, 255))
        txt_moedas = font.render(f"Moedas: {moedas_coletadas}/3", True, COLOR_COIN)

        screen.blit(txt_nome, (20, 20))
        screen.blit(txt_tentativas, (20, 50))
        screen.blit(txt_moedas, (20, 80))

        if checkpoint is not None:
            txt_chk = font.render(
                "[Z] Checkpoint Ativo | [X] Remover",
                True,
                COLOR_CHECKPOINT,
            )
            screen.blit(txt_chk, (20, 110))

        # Tela de Transição / Vitória de Nível
        if vitoria:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            screen.blit(s, (0, 0))

            titulo_txt = "JOGO ZERADO!" if jogo_zerado else "FASE CONCLUÍDA!"
            sub_txt = (
                "Pressione ESPAÇO para jogar novamente do Nível 1"
                if jogo_zerado
                else f"Moedas: {moedas_coletadas}/3  |  Pressione ESPAÇO para a Próxima Fase"
            )

            txt_vic = title_font.render(titulo_txt, True, config_nivel["cor_tema"])
            txt_sub = font.render(sub_txt, True, (255, 255, 255))

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