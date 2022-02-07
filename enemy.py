import pygame

"""Class that represents aliens"""
class Enemy(pygame.sprite.Sprite):
    def __init__(self,name_image,x,y):
        super().__init__()
        image_path = 'Sprites/' + name_image + '.png'
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft = (x,y))

    def update(self,direction):
        self.rect.x += direction

"""Class that represents UFO extra"""
class Ovni(pygame.sprite.Sprite):
    def __init__(self,direction,screen_width):
        super().__init__()
        self.image = pygame.image.load("Sprites/ovni.png").convert_alpha()
        
        if direction == "right":
            x = screen_width + 50
            self.speed =- 3
        else:
            x = -50
            self.speed = 3

        self.rect = self.image.get_rect(topleft = (x,80))

    def update(self):
        self.rect.x += self.speed