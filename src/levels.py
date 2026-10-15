"""
Módulo de Gerenciamento e Definição das Fases do Slime Dash.
Sincronizado com a duração real da música de fundo (65 segundos).
"""

VELOCIDADE_JOGO = 6.0
FPS_JOGO = 60
DURACAO_MUSICA_SEGUNDOS = 65.0  # 1 min e 05 seg
TILE_SIZE = 60

# Total de colunas necessárias para cobrir a música inteira
COLUNAS_TOTAL = int((VELOCIDADE_JOGO * FPS_JOGO * DURACAO_MUSICA_SEGUNDOS) / TILE_SIZE)  # ~390 colunas


def criar_fase_limpa():
    linhas = [" " * COLUNAS_TOTAL for _ in range(8)]
    lista_chao = list(linhas[0])
    lista_chao[-10] = "E"
    linhas[0] = "".join(lista_chao)
    return linhas


NIVEIS = {
    1: {
        "nome": "1. Origem da Gosma",
        "bpm": 122,
        "cor_tema": (50, 240, 100),
        "fase": criar_fase_limpa(),
    },
    2: {
        "nome": "2. Céu Doce",
        "bpm": 128,
        "cor_tema": (255, 105, 180),
        "fase": [" " * COLUNAS_TOTAL for _ in range(8)],
    },
    3: {
        "nome": "3. Pico Congelado",
        "bpm": 130,
        "cor_tema": (135, 206, 250),
        "fase": [" " * COLUNAS_TOTAL for _ in range(8)],
    },
}


def obter_configuracao_nivel(id_nivel: int) -> dict:
    return NIVEIS.get(id_nivel, NIVEIS[1])