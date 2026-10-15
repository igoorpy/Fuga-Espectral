import sys
import os
import pygame

try:
    from src.levels import NIVEIS
except ModuleNotFoundError:
    from levels import NIVEIS

# --- CONFIGURAÇÕES DO EDITOR 2D ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 36  # Bloco idêntico ao tamanho do Slime (36x36 px)
NUM_ROWS = 12   # 12 Linhas de altura (Mapa esticado verticalmente)
FLOOR_Y = 612    # Linha do Chão
CEILING_Y = FLOOR_Y - (NUM_ROWS * TILE_SIZE) # 180px

# Cores
COLOR_BG = (15, 12, 25)
COLOR_GRID = (38, 32, 58)
COLOR_FLOOR = (40, 30, 60)
COLOR_SPIKE = (230, 50, 50)
COLOR_BLOCK = (80, 70, 110)
COLOR_LAVA = (255, 80, 0)
COLOR_PAD = (255, 230, 0)
COLOR_RING = (255, 200, 0)
COLOR_COIN = (255, 215, 0)
COLOR_PORTAL = (255, 105, 180)
COLOR_TEXT = (255, 255, 255)

# Teclas e Ferramentas
FERRAMENTAS = {
    pygame.K_0: ("0: Apagar", " "),
    pygame.K_1: ("1: Bloco Inteiro", "1"),
    pygame.K_2: ("2: Meio Bloco (Fino)", "h"),
    pygame.K_3: ("3: Espinho Chão", "^"),
    pygame.K_4: ("4: Espinho Teto", "v"),
    pygame.K_5: ("5: Lava / Ácido", "~"),
    pygame.K_6: ("6: Trampolim", "*"),
    pygame.K_7: ("7: Orbe de Pulo", "@"),
    pygame.K_8: ("8: Portal Voo", "C"),
    pygame.K_9: ("9: Moeda", "O"),
    pygame.K_e: ("E: Linha Chegada", "E"),
}


def carregar_matriz_fase():
    fase_linhas = NIVEIS[1]["fase"]
    matriz = []
    for row in range(NUM_ROWS):
        if row < len(fase_linhas):
            linha = list(fase_linhas[row])
        else:
            linha = [" "] * 500
        if len(linha) < 500:
            linha.extend([" "] * (500 - len(linha)))
        matriz.append(linha)
    return matriz


def salvar_fase(matriz_2d):
    novas_linhas = ["".join(row) for row in matriz_2d]
    NIVEIS[1]["fase"] = novas_linhas

    caminho_levels = "src/levels.py" if os.path.exists("src/levels.py") else "levels.py"
    with open(caminho_levels, "w", encoding="utf-8") as f:
        f.write("\"\"\"\nMódulo de Gerenciamento e Definição das Fases do Slime Dash.\n\"\"\"\n\n")
        f.write("NIVEIS = {\n    1: {\n")
        f.write(f"        'nome': '{NIVEIS[1]['nome']}',\n")
        f.write(f"        'bpm': {NIVEIS[1]['bpm']},\n")
        f.write(f"        'cor_tema': {NIVEIS[1]['cor_tema']},\n")
        f.write("        'fase': [\n")
        for line in novas_linhas:
            f.write(f"            \"{line}\",\n")
        f.write("        ],\n    },\n")
        f.write("    2: {'nome': '2. Céu Doce', 'bpm': 128, 'cor_tema': (255, 105, 180), 'fase': [\" \" * 500] * 12},\n")
        f.write("    3: {'nome': '3. Pico Congelado', 'bpm': 130, 'cor_tema': (135, 206, 250), 'fase': [\" \" * 500] * 12},\n")
        f.write("}\n\ndef obter_configuracao_nivel(id_nivel: int) -> dict:\n    return NIVEIS.get(id_nivel, NIVEIS[1])\n")

    print("[EDITOR 2D] Fase 1 salva com sucesso!")


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Slime Dash - Editor 2D (Tamanho GD 1:1 + Meio Bloco)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 15, bold=True)

    caminho_musica = "assets/sounds/fase1.mp3"
    if os.path.exists(caminho_musica):
        try:
            pygame.mixer.music.load(caminho_musica)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    matriz_grid = carregar_matriz_fase()
    coluna_offset = 0
    ferramenta_char = "1"
    ferramenta_nome = "1: Bloco Inteiro"

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in FERRAMENTAS:
                    ferramenta_nome, ferramenta_char = FERRAMENTAS[event.key]
                elif event.key == pygame.K_s:
                    salvar_fase(matriz_grid)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                m_x, m_y = event.pos

                if event.button == 4:  # Scroll Up -> Direita
                    coluna_offset = min(len(matriz_grid[0]) - 30, coluna_offset + 3)
                elif event.button == 5:  # Scroll Down -> Esquerda
                    coluna_offset = max(0, coluna_offset - 3)

                elif CEILING_Y <= m_y <= FLOOR_Y:
                    col = (m_x // TILE_SIZE) + coluna_offset
                    row_idx = (FLOOR_Y - m_y) // TILE_SIZE  # 0 = Chão, 11 = Teto

                    if 0 <= row_idx < NUM_ROWS and 0 <= col < len(matriz_grid[0]):
                        if event.button == 1:   # Clique Esquerdo -> Pintar
                            matriz_grid[row_idx][col] = ferramenta_char
                        elif event.button == 3: # Clique Direito -> Apagar
                            matriz_grid[row_idx][col] = " "

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            coluna_offset = min(len(matriz_grid[0]) - 30, coluna_offset + 1)
        elif keys[pygame.K_LEFT]:
            coluna_offset = max(0, coluna_offset - 1)

        screen.fill(COLOR_BG)

        # Chão e Teto
        pygame.draw.rect(screen, COLOR_FLOOR, (0, FLOOR_Y, SCREEN_WIDTH, SCREEN_HEIGHT - FLOOR_Y))
        pygame.draw.rect(screen, COLOR_FLOOR, (0, 0, SCREEN_WIDTH, CEILING_Y))

        # Desenhar Grade 12 Linhas
        for r in range(NUM_ROWS + 1):
            y_line = FLOOR_Y - (r * TILE_SIZE)
            pygame.draw.line(screen, COLOR_GRID, (0, y_line), (SCREEN_WIDTH, y_line), 1)

        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            pygame.draw.line(screen, COLOR_GRID, (x, CEILING_Y), (x, FLOOR_Y), 1)

        # Renderizar Matriz
        cols_visiveis = SCREEN_WIDTH // TILE_SIZE + 1
        for row in range(NUM_ROWS):
            y_pos = FLOOR_Y - ((row + 1) * TILE_SIZE)
            for c in range(cols_visiveis):
                col_idx = c + coluna_offset
                if col_idx < len(matriz_grid[row]):
                    char = matriz_grid[row][col_idx]
                    x_pos = c * TILE_SIZE

                    if char == "1":  # Bloco Inteiro (36x36)
                        blk = pygame.Rect(x_pos, y_pos, TILE_SIZE, TILE_SIZE)
                        pygame.draw.rect(screen, COLOR_BLOCK, blk)
                        pygame.draw.rect(screen, (150, 140, 180), blk, 2)
                    elif char == "h":  # Meio Bloco / Plataforma Fina (36x18)
                        half_blk = pygame.Rect(x_pos, y_pos + TILE_SIZE // 2, TILE_SIZE, TILE_SIZE // 2)
                        pygame.draw.rect(screen, COLOR_BLOCK, half_blk)
                        pygame.draw.rect(screen, (180, 170, 210), half_blk, 2)
                    elif char == "^":  # Espinho Chão
                        spk = pygame.Rect(x_pos + 6, y_pos + 6, TILE_SIZE - 12, TILE_SIZE - 6)
                        pygame.draw.polygon(screen, COLOR_SPIKE, [spk.bottomleft, (spk.centerx, spk.top), spk.bottomright])
                    elif char == "v":  # Espinho Teto
                        spk = pygame.Rect(x_pos + 6, y_pos, TILE_SIZE - 12, TILE_SIZE - 6)
                        pygame.draw.polygon(screen, COLOR_SPIKE, [spk.topleft, (spk.centerx, spk.bottom), spk.topright])
                    elif char == "~":  # Lava
                        lva = pygame.Rect(x_pos, y_pos + TILE_SIZE - 12, TILE_SIZE, 12)
                        pygame.draw.rect(screen, COLOR_LAVA, lva)
                    elif char == "*":  # Trampolim
                        pad = pygame.Rect(x_pos + 4, y_pos + TILE_SIZE - 10, TILE_SIZE - 8, 10)
                        pygame.draw.rect(screen, COLOR_PAD, pad, border_radius=3)
                    elif char == "@":  # Orbe
                        pygame.draw.circle(screen, COLOR_RING, (x_pos + TILE_SIZE // 2, y_pos + TILE_SIZE // 2), 11, 3)
                        pygame.draw.circle(screen, (255, 255, 255), (x_pos + TILE_SIZE // 2, y_pos + TILE_SIZE // 2), 5)
                    elif char == "C":  # Portal Voo
                        ptl = pygame.Rect(x_pos + 6, y_pos, TILE_SIZE - 12, TILE_SIZE)
                        pygame.draw.rect(screen, COLOR_PORTAL, ptl, 3)
                    elif char == "O":  # Moeda
                        pygame.draw.circle(screen, COLOR_COIN, (x_pos + TILE_SIZE // 2, y_pos + TILE_SIZE // 2), 10)
                    elif char == "E":  # Chegada
                        pygame.draw.line(screen, (50, 255, 100), (x_pos, CEILING_Y), (x_pos, FLOOR_Y), 4)

        # UI
        txt_tool = font.render(f"Ferramenta: [{ferramenta_nome}] | [Atalhos 0-9 e Tecla E]", True, (50, 240, 100))
        txt_pos = font.render(f"Coluna: {coluna_offset} | Setas / Scroll para navegar", True, COLOR_TEXT)
        txt_save = font.render("[Clique Esq]: Pintar | [Clique Dir]: Apagar | Tecla [S]: Salvar Fase", True, COLOR_TEXT)

        screen.blit(txt_tool, (20, 12))
        screen.blit(txt_pos, (20, 32))
        screen.blit(txt_save, (20, 52))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()