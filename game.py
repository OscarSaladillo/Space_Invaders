import pygame, sys
from ship import Ship
from enemy import Enemy, Ovni
from random import choice, randint
from laser import Laser
import obstacle
import matplotlib.pyplot as plt
import numpy as np
import os

#Main class that starts the game
class AlienInvasion:
    def __init__(self,screen_width,screen_height):
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.settings()

        self.lives = 3
        self.live_surf = pygame.image.load("Sprites/player.png").convert_alpha()
        self.live_x_start_pos = screen_width - (self.live_surf.get_size()[0] * 2 + 20)
        self.score = 0
        self.font = pygame.font.Font("Fonts/04B_30__.TTF",20)

        self.shape = obstacle.shape
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.obstacle_amount = 4
        self.obstacle_x_positions = [num  * (screen_width / self.obstacle_amount) for num in range(self.obstacle_amount)]
        self.create_multiple_obstacles(*self.obstacle_x_positions,x_start = screen_width / 15, y_start = 480)

        self.enemies = pygame.sprite.Group()
        self.enemy_lasers = pygame.sprite.Group()
        self.enemy_setup(rows=6,cols=8)
        self.enemy_direction = 1

        self.ovni = pygame.sprite.GroupSingle()
        self.ovni_spawn_time = randint(400,800)

        self.canRestart = False
        self.unlock = True

    def create_obstacle(self, x_start, y_start,offset_x):
        for row_index, row in enumerate(self.shape):
            for col_index,col in enumerate(row):
                if col =="x":
                    x = x_start + col_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = obstacle.Block(self.block_size,(81,241,150),x,y)
                    self.blocks.add(block)

    def create_multiple_obstacles(self,*offset,x_start,y_start):
        for x in offset:
            self.create_obstacle(x_start,y_start,x)

    def settings(self):
        self.screen = pygame.display.set_mode((self.screen_width,self.screen_height + 50))
        self.clock = pygame.time.Clock() #variable that handles the fps of the game
        ship_sprite = Ship((self.screen_width / 2,self.screen_height),self.screen_width,5)
        self.ship = pygame.sprite.GroupSingle(ship_sprite)

    """Method used to set enemies in the screen
    
    x_offset: used to add to the x position, the width of the sprite.
    y_offset: used to add to the y position, the height of the sprite."""
    def enemy_setup(self,rows,cols,x_distance = 60,y_distance = 48,x_offset = 70, y_offset = 100):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_distance + x_offset
                y = row_index * y_distance + y_offset

                if row_index == 0: enemy_sprite = Enemy('yellow',x,y)
                elif 1 <= row_index <= 2: enemy_sprite = Enemy('green',x,y)
                else: enemy_sprite = Enemy('red',x,y)
                self.enemies.add(enemy_sprite)

    """Method used to clear the screen of enemies when the player loses all lives"""
    def kill_enemies(self):
        for enemy in self.enemies:
            enemy.kill()           
    """method used to control the 
    direction of aliens when they collide with the edge of the screen."""
    def enemy_position_checker(self):
        all_enemies = self.enemies.sprites()
        for enemy in all_enemies:
            if enemy.rect.right >= self.screen_width:
                self.enemy_direction = -1
                self.enemy_move_down(2)
            elif enemy.rect.left <= 0:
                self.enemy_direction = 1
                self.enemy_move_down(2)
                
    def enemy_move_down(self,distance):
        if self.enemies:
            for enemy in self.enemies.sprites():
                enemy.rect.y += distance

    def enemy_shoot(self):
        if self.enemies.sprites():
            random_enemy = choice(self.enemies.sprites())
            laser_sprite = Laser(random_enemy.rect.center,self.screen_height,6)
            self.enemy_lasers.add(laser_sprite)

    def isCollision(self):
        if self.ship.sprite.lasers:
            for laser in self.ship.sprite.lasers:
                if pygame.sprite.spritecollide(laser,self.blocks,True):
                    laser.kill()
                if pygame.sprite.spritecollide(laser,self.enemies,True):
                    self.score += 300
                    laser.kill()
                if pygame.sprite.spritecollide(laser,self.ovni,True):
                    self.score += 500
                    laser.kill()

        if self.enemy_lasers:
            for laser in self.enemy_lasers:
                if pygame.sprite.spritecollide(laser,self.blocks,True):
                    laser.kill()
                if pygame.sprite.spritecollide(laser,self.ship,False):
                    laser.kill()
                    if self.lives > 0:
                        self.lives -= 1
                        self.kill_enemies()
                        self.enemy_setup(rows=6,cols=8)
                        self.create_multiple_obstacles(*self.obstacle_x_positions,x_start = self.screen_width / 15, y_start = 480)
        
        if self.enemies:
            for enemy in self.enemies:
                pygame.sprite.spritecollide(enemy,self.blocks,True)

                if pygame.sprite.spritecollide(enemy,self.ship,False):
                    if self.lives > 0:
                        self.lives -= 1
                        self.kill_enemies()
                        self.enemy_setup(rows=6,cols=8)
                        self.create_multiple_obstacles(*self.obstacle_x_positions,x_start = self.screen_width / 15, y_start = 480)

    def display_score(self):
        score_surf = self.font.render(f"score {self.score}",False,"white")
        score_rect = score_surf.get_rect(topleft = (10,10))
        self.screen.blit(score_surf,score_rect)

    def update_screen(self):
        self.ship.update()
        self.enemies.update(self.enemy_direction)
        self.enemy_position_checker()
        self.enemy_lasers.update()
        self.ovni_timer()
        self.ovni.update()
        self.isCollision()
        self.display_lives()
        self.victory_message()
        self.defeat_message()
        
        self.ship.sprite.lasers.draw(self.screen)
        self.ship.draw(self.screen)

        self.blocks.draw(self.screen)
        self.enemies.draw(self.screen)
        self.enemy_lasers.draw(self.screen)
        self.ovni.draw(self.screen)
        self.display_score()

    """method used to determine when the UFO above the aliens is coming out"""
    def ovni_timer(self):
        self.ovni_spawn_time -= 1
        if self.ovni_spawn_time <= 0:
            self.ovni.add(Ovni(choice(["right","left"]),self.screen_width))
            self.ovni_spawn_time = randint(400,800)

    def display_lives(self):
        for live in range(self.lives - 1):
            x = self.live_x_start_pos + (live * (self.live_surf.get_size()[0] + 10))
            self.screen.blit(self.live_surf,(x,8))

    def victory_message(self):
        if not self.enemies.sprites() and self.lives > 0:
            self.canRestart = True
            victory_surf = self.font.render("You win", False,"white")
            victory_rect = victory_surf.get_rect(center = (self.screen_width /2, self.screen_height /2))
            self.screen.blit(victory_surf,victory_rect)
            self.help_message()
            

    def defeat_message(self):
        if self.lives <= 0:
            self.canRestart = True
            self.kill_enemies()
            defeat_surf = self.font.render("Game Over", False,"white")
            defeat_rect = defeat_surf.get_rect(center = (self.screen_width /2, self.screen_height /2))
            self.screen.blit(defeat_surf,defeat_rect)
            self.help_message()

    def help_message(self):
        """This condition allows us to send the message to press g 
        to see the score when the player has lost all lives, 
        because if we put a message of something that the user
        cannot do, it will annoy the user."""
        if self.lives <= 0:
            message_help = self.font.render("Press G for see your score", False, "white")
            help_rect = message_help.get_rect(center = (self.screen_width /2, self.screen_height / 3.5))
            self.screen.blit(message_help,help_rect)
        message_help2 = self.font.render("Press Enter for Restart Game", False, "white")
        help_rect2 = message_help2.get_rect(center = (self.screen_width /2, self.screen_height / 3))
        self.screen.blit(message_help2,help_rect2)

    def get_input(self):
        keys = pygame.key.get_pressed()

        """The canRestart condition is set to prevent the player from unintentionally 
        pressing the enter button and the game inadvertently restarting or to 
        prevent the player from cheating with the scores."""
        if keys[pygame.K_RETURN] and self.canRestart:
            if self.lives <= 0:
                self.get_scores()
                self.lives = 3
                self.score = 0
                file = open("save", "wb")
                np.save(file, self.scores)
                file.close
            self.enemy_setup(rows=6,cols=8)
            self.create_multiple_obstacles(*self.obstacle_x_positions,x_start = self.screen_width / 15, y_start = 480)
            self.canRestart = False

        """This condition is set to only load scores when the player has had a gameover."""
        if keys[pygame.K_g] and self.canRestart and self.lives <= 0:
            ids = [x for x in range(len(np.append(self.scores,self.score).tolist()))]
            plt.bar(ids, np.append(self.scores,self.score).tolist())

            plt.xlabel('intentos')
            plt.ylabel('puntos')

            plt.title('Puntuaciones\n:)')
            self.unlock = False
            plt.show()
            self.unlock = True 

    """method used to load the different scores saved in the save file in scores array"""
    def get_scores(self):
        if not os.path.exists("save") or os.stat("save").st_size == 0:
            scores = np.array([0])
            file = open("save", "wb")
            np.save(file, scores)
            file.close
        file = open("save", "rb")
        self.scores = np.load(file)
        file.close      

        self.scores = np.append(self.scores, self. score)

    def run_game(self):
        """Here you set a timer to know when an alien should fire a laser."""
        ALIENLASER = pygame.USEREVENT + 1
        pygame.time.set_timer(ALIENLASER,800)
        self.get_scores()
        while True:
            if self.unlock:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == ALIENLASER:
                        game.enemy_shoot()

                self.screen.fill((0,0,0))
                self.get_input()

                self.update_screen()
                pygame.display.flip()
                self.clock.tick(60)

                """This method call is placed to give the player a much faster and more fluid movement.
                """
                self.ship.update()
                self.ship.draw(self.screen)

game = AlienInvasion(600,600)
game.run_game()


    