import pygame
import sys
from config import *

from game_objects import *
# инициализируем
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("math-game")
clock = pygame.time.Clock()

# Кнопочки
start_button = Button(WIDTH//2 - 100, 400, 200, 60, "Начать игру", BLUE, WHITE)

# состояния игры:
MENU = 0
GAMEPLAY = 1
curent_state = 0

# отрисовка меню
def draw_menu():
    # делаем фончик голубым
    screen.fill(LIGHT_BLUE)
    # создаём шрифт и надпись
    font = pygame.font.Font(None, 52)
    title = font.render("math-game", True, BLACK)
    # переносим пиксели с title на screen
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    
    start_button.draw(screen)
    
    # font_small = pygame.font.Font(None, 36)
    # start_text = font_small.render("Нажмите ПРОБЕЛ для начала", True, BLACK)
    # screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, 300))

# отрисовка игры
def draw_gameplay():
    screen.fill(YELLOW)
    font = pygame.font.Font(None, 25)
    text = font.render('идёт жоская каточка в бравл старс...', True, BLACK)
    screen.blit(text, (50, 50))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if curent_state == MENU:
            if start_button.handle_event(event):
                curent_state = GAMEPLAY
        if event.type == pygame.KEYDOWN:
            if curent_state == MENU and event.key == pygame.K_SPACE:
                curent_state = GAMEPLAY
            elif curent_state == GAMEPLAY and event.key == pygame.K_ESCAPE:
                curent_state = MENU
    if curent_state == MENU:
        draw_menu()
    elif curent_state == GAMEPLAY:
        draw_gameplay()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
