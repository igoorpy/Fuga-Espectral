import unittest
import pygame
from src.main import Slime


class TestJitterDiagnostic(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()

    def test_zero_tremor_ao_pousar_no_bloco(self):
        """[CTFL: Teste de Estabilidade] Garante que a base do Slime não oscila NENHUM pixel no bloco"""
        slime = Slime(x=220, y=300)
        topo_do_bloco = 520.0

        # Simula o Slime pousado no topo do bloco
        slime.y = topo_do_bloco
        slime.is_grounded = True
        slime.vel_y = 0.0

        posicoes_da_base = []

        # Roda 100 frames simulados com deformação elástica ativa
        for _ in range(100):
            slime.update(floor_y=580, ceiling_y=100, particles=[])
            posicoes_da_base.append(slime.rect.bottom)

        # Valida se a base (rect.bottom) permaneceu cravada em 520px em TODOS os 100 frames
        variacao = max(posicoes_da_base) - min(posicoes_da_base)
        self.assertEqual(
            variacao,
            0,
            f"Detectado tremor! A base oscilou {variacao} pixels durante o pouso.",
        )


if __name__ == "__main__":
    unittest.main()