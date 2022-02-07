import pygame

class Laser(pygame.sprite.Sprite):
    def __init__(self,pos,screen_height,speed = -8):
        super().__init__()
        self.image = pygame.Surface((4,20))
        self.image.fill("white")
        self.speed = speed
        self.rect = self.image.get_rect(center = pos)
        self.height_y_limit = screen_height

    """Function used to check if a laser went out of the limit of the screen and if so, it is destroyed, in order to optimise the game."""
    def destroy(self):
        if self.rect.y <= -50 or self.rect.y >= self.height_y_limit + 50:
            self.kill()

    def update(self):
        self.rect.y += self.speed
        self.destroy()