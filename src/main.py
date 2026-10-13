import sys
import pygame

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

COLOR_BG = (20, 15, 30)
COLOR_GHOST = (0, 230, 255)
COLOR_KNIGHT = (140, 140, 150)
COLOR_FLOOR = (60, 50, 70)


class Ghost(pygame.sprite.Sprite):

    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill(COLOR_GHOST)
        self.rect = self.image.get_rect(topleft=(x, y))

        self.speed = 6
        self.energy = 100.0
        self.is_possessing = False

    def drenar_energia(self, quantidade: float):
        self.energy = max(0.0, self.energy - quantidade)

    def update(self, keys=None):
        if self.is_possessing or keys is None:
            return

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))


class Knight(pygame.sprite.Sprite):

    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pygame.Surface((36, 52))
        self.image.fill(COLOR_KNIGHT)
        self.rect = self.image.get_rect(topleft=(x, y))

        # Posição interna em float para física e gravidade precisas
        self.pos_x = float(x)
        self.pos_y = float(y)

        self.speed = 3
        self.vel_y = 0.0
        self.gravity = 0.8
        self.is_possessed = False

    def update(self, keys=None, floor_rect=None):
        # Aplica gravidade contínua
        self.vel_y += self.gravity
        self.pos_y += self.vel_y
        self.rect.y = round(self.pos_y)

        # Checa colisão simples com o chão
        if floor_rect and self.rect.colliderect(floor_rect):
            self.rect.bottom = floor_rect.top
            self.pos_y = float(self.rect.y)
            self.vel_y = 0

        # Movimentação apenas se estiver possuído
        if self.is_possessed and keys:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.pos_x -= self.speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.pos_x += self.speed
            self.rect.x = round(self.pos_x)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(
        "Fuga Espectral - Build v0.3 [Possessão & Gravidade]"
    )
    clock = pygame.time.Clock()

    # Entidades
    ghost = Ghost(200, 300)
    knight = Knight(600, 300)

    # Chão para teste de gravidade
    floor_rect = pygame.Rect(0, 600, SCREEN_WIDTH, 120)

    all_sprites = pygame.sprite.Group(knight, ghost)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Tecla 'E': Possuir o Cavaleiro
                elif event.key == pygame.K_e and not ghost.is_possessing:
                    if ghost.rect.colliderect(knight.rect):
                        ghost.is_possessing = True
                        knight.is_possessed = True

                # Tecla 'Q': Ejetar do Cavaleiro
                elif event.key == pygame.K_q and ghost.is_possessing:
                    ghost.is_possessing = False
                    knight.is_possessed = False
                    ghost.rect.midbottom = knight.rect.midtop

        keys = pygame.key.get_pressed()

        # Atualização
        ghost.update(keys)
        knight.update(keys, floor_rect)

        if ghost.is_possessing:
            ghost.rect.center = knight.rect.center
        else:
            ghost.drenar_energia(0.05)  # Perde energia enquanto voa livre

        # Renderização
        screen.fill(COLOR_BG)
        pygame.draw.rect(screen, COLOR_FLOOR, floor_rect)  # Desenha chão

        if not ghost.is_possessing:
            screen.blit(ghost.image, ghost.rect)
        screen.blit(knight.image, knight.rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()