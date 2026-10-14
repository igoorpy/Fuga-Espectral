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
        """[CTFL: Transição de Estado] Garante que o Portal Chiclete reduz a gravidade"""
        self.slime.mudar_modo("CHICLETE")
        self.assertEqual(self.slime.modo, "CHICLETE")
        self.assertEqual(
            self.slime.gravity,
            0.4,
            "A gravidade no modo Chiclete deve ser reduzida para 0.4",
        )

    def test_transicao_estado_portal_neve(self):
        """[CTFL: Transição de Estado] Garante que o Portal Neve inverte a gravidade"""
        self.slime.mudar_modo("NEVE")
        self.assertEqual(self.slime.modo, "NEVE")
        self.assertLess(
            self.slime.gravity,
            0,
            "A gravidade no modo Neve deve ser negativa (Invertida)",
        )

    def test_deformacao_squish_ao_impactar_chao(self):
        """[CTFL: Teste Funcional] Verifica achatamento horizontal ao tocar o chão"""
        particles = []
        floor_y, ceiling_y = 580, 100
        self.slime.y = floor_y - 10
        self.slime.vel_y = 10.0
        self.slime.is_grounded = False

        self.slime.update(floor_y, ceiling_y, particles)
        self.assertGreater(
            self.slime.current_width,
            36,
            "O Slime deve alargar na horizontal ao impactar o chão",
        )


if __name__ == "__main__":
    unittest.main()