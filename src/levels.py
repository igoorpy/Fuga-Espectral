"""
Módulo de Gerenciamento e Definição das Fases do Slime Dash.
Contém as matrizes de texto, BPM e configurações de cada nível.
"""

# Mapeamento de Símbolos:
# ' ' = Espaço Vazio
# '^' = Espinho Triangular
# '1' = Bloco Baixo (Plataforma)
# '2' = Bloco Alto
# 'O' = Moeda Secreta (3 por fase)
# 'C' = Portal de Chiclete (Voo)
# 'N' = Portal de Neve (Gravidade Invertida)
# 'G' = Portal de Gosma (Chão Tradicional)
# 'E' = Linha de Chegada (END)

NIVEIS = {
    1: {
        "nome": "1. Origem da Gosma",
        "bpm": 124,
        "cor_tema": (50, 240, 100),
        "fase": (
            "    ^   11   O   ^^   22   ^   C   ^   O   ^   N   ^^   G   111   O   ^^^   E"
        ),
    },
    2: {
        "nome": "2. Céu Doce",
        "bpm": 128,
        "cor_tema": (255, 105, 180),
        "fase": (
            "    C   ^   ^   O   ^^   11   ^   O   ^^   G   ^   11   O   ^^^   E"
        ),
    },
    3: {
        "nome": "3. Pico Congelado",
        "bpm": 130,
        "cor_tema": (135, 206, 250),
        "fase": (
            "    N   ^^   11   O   ^^   22   G   ^   O   C   ^^   O   ^^^   E"
        ),
    },
}


def obter_configuracao_nivel(id_nivel: int) -> dict:
    """Retorna os dados do nível solicitado ou o nível 1 como padrão (Fallback)."""
    return NIVEIS.get(id_nivel, NIVEIS[1])