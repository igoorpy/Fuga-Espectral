import unittest
import pygame
from src.main import Ghost, Knight


class TestEntidadesJogo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Inicializa o Pygame em modo headless para criar as Surfaces nos testes
        pygame.init()

    def setUp(self):
        self.ghost = Ghost(100, 100)
        self.knight = Knight(200, 200)

    def test_energia_inicial_fantasma(self):
        """Verifica se o Fantasma nasce com 100% de energia"""
        self.assertEqual(self.ghost.energy, 100.0)

    def test_drenar_energia_fantasma(self):
        """Verifica se a redução de energia funciona corretamente"""
        self.ghost.drenar_energia(10.0)
        self.assertEqual(self.ghost.energy, 90.0)

    def test_gravidade_cavaleiro(self):
        """Verifica se o Cavaleiro sofre efeito de gravidade ao atualizar"""
        y_inicial = self.knight.rect.y
        self.knight.update()
        self.assertGreater(
            self.knight.rect.y, y_inicial, "O Cavaleiro deve cair devido à gravidade"
        )


if __name__ == "__main__":
    unittest.main()