from game_objects import *

class Menu:
    def __init__(self, surface : pygame.Surface):
        self.surface = surface
        self.start_button = Button(WIDTH // 2 - 100, 400, 200, 60, "Начать игру", color=BLUE, text_color=WHITE)

    def draw(self) -> None:
        """Отрисовка меню"""
        # делаем фончик голубым
        self.surface.fill(LIGHT_BLUE)
        # создаём шрифт и надпись
        font = pygame.font.Font(None, 52)
        title = font.render("math-game", True, BLACK)
        # переносим пиксели с title на screen
        self.surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        self.start_button.draw(self.surface)

        font_small = pygame.font.Font(None, 36)
        start_text = font_small.render("Нажмите ПРОБЕЛ для начала", True, BLACK)
        self.surface.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 300))

    def event_update(self, event: pygame.event.Event) -> bool:
        """
        Обновляем атрибуты в зависимости от события event.
        Возвращает True, если меню активно (игра не началась). Иначе - False.
        """
        return not self.start_button.handle_event(event)
