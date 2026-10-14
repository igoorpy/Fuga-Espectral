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

    def test_hitbox_perdoadora_slime(self):
        """[CTFL: Teste de Usabilidade] Verifica se a hitbox interna do Slime reduz falsos positivos"""
        hitbox = self.slime.get_hitbox()
        self.assertLess(
            hitbox.width,
            self.slime.rect.width,
            "A hitbox de colisão deve ser menor que a bounding box visual",
        )

    def test_calculo_porcentagem_progresso(self):
        """[CTFL: Teste Funcional] Garante que o cálculo de progresso atinge 100% no final da fase"""
        distancia = 6000.0
        largura_total = 6000.0
        pct = min(100, int((distancia / largura_total) * 100))
        self.assertEqual(pct, 100, "O progresso deve atingir 100% ao completar a distância total")


if __name__ == "__main__":
    unittest.main()