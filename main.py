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

#Карта
game_map = Map(screen, GRID_WIDTH, GRID_HEIGHT)
game = Game(screen, GRID_WIDTH, GRID_HEIGHT)

# состояния игры:
MENU = 0
GAMEPLAY = 1
current_state = 0

def draw_menu() -> None:
    '''Отрисовка меню'''
    # делаем фончик голубым
    screen.fill(LIGHT_BLUE)
    # создаём шрифт и надпись
    font = pygame.font.Font(None, 52)
    title = font.render("math-game", True, BLACK)
    # переносим пиксели с title на screen
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    
    start_button.draw(screen)
    
    font_small = pygame.font.Font(None, 36)
    start_text = font_small.render("Нажмите ПРОБЕЛ для начала", True, BLACK)
    screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, 300))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if current_state == MENU:
            if start_button.handle_event(event):
                current_state = GAMEPLAY
        if event.type == pygame.KEYDOWN:
            if current_state == MENU and event.key == pygame.K_SPACE:
                current_state = GAMEPLAY
            elif current_state == MENU and event.key == pygame.K_ESCAPE:
                running = False
            elif current_state == GAMEPLAY and event.key == pygame.K_ESCAPE:
                current_state = MENU
                game.reset()
        if current_state == GAMEPLAY:
            game.event_update(event)

    if current_state == MENU:
        draw_menu()
    elif current_state == GAMEPLAY:
        game.update()
        game.draw()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
