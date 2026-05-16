import pygame
import sys
from game import *
from menu import *

# инициализируем
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("math-game")
clock = pygame.time.Clock()

# Меню
game_menu = Menu(screen)

#Игра
game = Game(screen)

# состояния игры:
MENU = 0
GAMEPLAY = 1
current_state = 0


running = True
while running:
    for event in pygame.event.get():
        # простые события
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if current_state == MENU and event.key == pygame.K_SPACE:
                current_state = GAMEPLAY
            elif current_state == MENU and event.key == pygame.K_ESCAPE:
                running = False
            elif current_state == GAMEPLAY and event.key == pygame.K_ESCAPE:
                current_state = MENU
                game.reset()

        # события состояния
        if current_state == MENU:
            active = game_menu.event_update(event)
            if not active:
                current_state = GAMEPLAY
        if current_state == GAMEPLAY:
            game.event_update(event)

    # рисуем по состоянию
    if current_state == MENU:
        game_menu.draw()
    elif current_state == GAMEPLAY:
        game.update()
        game.draw()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
