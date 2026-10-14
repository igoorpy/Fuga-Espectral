import unittest
import pygame
from src.main import Slime


class TestSlimeDashEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()

    def setUp(self):
        self.slime = Slime(x=180, y=300)

    def test_transicao_estado_portal_chiclete(self):
        """[CTFL: Transição de Estado] Garante que o Portal Chiclete altera a gravidade"""
        self.slime.mudar_modo("CHICLETE")
        self.assertEqual(self.slime.modo, "CHICLETE")
        self.assertEqual(self.slime.gravity, 0.45)

    def test_transicao_estado_portal_neve(self):
        """[CTFL: Transição de Estado] Garante que o Portal Neve inverte a gravidade"""
        self.slime.mudar_modo("NEVE")
        self.assertEqual(self.slime.modo, "NEVE")
        self.assertLess(self.slime.gravity, 0)

    def test_jump_buffering(self):
        """[CTFL: Teste de Usabilidade] Garante que solicitar pulo ativa o buffer de entrada"""
        self.slime.solicitar_pulo()
        self.assertEqual(
            self.slime.jump_buffer,
            8,
            "O buffer de pulo deve ser preenchido com 8 frames",
        )


if __name__ == "__main__":
    unittest.main()