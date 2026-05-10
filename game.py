from game_objects import *
from quiz import *

class Game:
    """Основной класс игры."""

    # общие состояния
    EXPLORATION = 0
    FIGHTING = 1
    GAME_OVER = 2

    # состояния "исследования"
    BOT_CHOICE = 0
    PLAYER_CHOICE = 1
    QUIZ_WAIT = 2
    QUIZ_CHOICE = 3
    QUIZ_RESULT = 4


    def __init__(self, surface : pygame.Surface):
        self.surface = surface
        # задаём позиции территорий и матрицу смежности.
        # Надо: наверное, перенести это в Map, сделать файлик с 
        # картами. Пока пусть такая карта будет.
        territory_position = list()
        start_x = (WIDTH - (CELL_SIZE * 3)) // 2
        start_y = (HEIGHT - CELL_SIZE) // 3
        for r in range(3):
            for c in range(3):
                x = start_x + (CELL_SIZE * r)
                y = start_y + (CELL_SIZE * c)
                territory_position.append((x, y))
        adjective_list = [[max(x // 3 * 3, x - 1), min(x + 1, x // 3 * 3 + 2), max(x % 3, x - 3), min(x + 3, x % 3 + 6)] for x in range(9)]
        self.battlefield = Map(surface, territory_position, adjective_list)

        self.selected_territories = []

        self.winner = NOBODY

        # квиз
        self.quiz = Quiz()
        self.quiz_wait_timer = 0
        self.quiz_timer = 0
        self.quiz_result_timer = 0
        self.quiz_result = []

        # всё для бота и огорода
        self.bot_timer = 0

        # сообщение
        self.message = Message()

        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

        self.current_step = self.BOT_CHOICE
        self.current_state = self.EXPLORATION


    # тупая версия
    def check_win(self) -> bool:
        """Возвращает True и устанавливает победителя. Иначе возвращает False."""
        pt = self.battlefield.get_territories(PLAYER)
        bt = self.battlefield.get_territories(BOT)
        nt = self.battlefield.get_territories(NOBODY)
        if len(nt) == 0 or len(nt) == 1:
            self.current_state = self.GAME_OVER
            self.winner = PLAYER if len(pt) > len(bt) else BOT
            return True
        return False


    def update(self) -> None:
        """Главный метод. Обновляет все состояния игры."""
        if self.current_state == self.GAME_OVER:
            return

        if self.current_step == self.BOT_CHOICE: # бот выбирает территорию
            # сначала ждёт
            if self.bot_timer == 0:
                self.bot_timer = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.bot_timer > 1000:
                self.selected_territories.append(random.choice(self.battlefield.get_able_to_capture(BOT)))
                self.selected_territories[0].set_owner(BOT, temporary=True)

                self.bot_timer = 0
                self.current_step = self.PLAYER_CHOICE

        elif self.current_step == self.QUIZ_WAIT: # ожидание квиза
            if self.quiz_wait_timer == 0:
                self.quiz_wait_timer = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.quiz_wait_timer > 200:
                self.quiz_wait_timer = 0
                self.current_step = self.QUIZ_CHOICE

        elif self.current_step == self.QUIZ_RESULT: # подведение итогов квиза
            # в конце будет проверять победителя
            if self.quiz_result_timer == 0:
                self.quiz_result_timer = pygame.time.get_ticks()
                self.message.show("Правильно!" if self.quiz_result[1] else "Неправильно!")
            elif pygame.time.get_ticks() - self.quiz_result_timer > 1500:
                self.quiz_result_timer = 0
                self.quiz_result = []
                self.message.is_show = False
                self.check_win()
                self.current_step = self.BOT_CHOICE


    def event_update(self, event : pygame.Event) -> None:
        """Обновляем атрибуты, зависящие от события event."""
        if self.current_step == self.PLAYER_CHOICE: # игрок выбирает территорию
            flag = False
            # определяем территорию, куда будет ходить игрок: в соседние
            # или в незанятую
            territories_to_capture = self.battlefield.get_able_to_capture(PLAYER)
            for territory in territories_to_capture:
                if event.type == pygame.MOUSEBUTTONDOWN and territory.rect.collidepoint(event.pos):
                    self.selected_territories.append(territory)
                    self.selected_territories[1].set_owner(PLAYER, temporary=True)
                    flag = True
                    break
                if flag:
                    break
            if flag:
                self.current_step = self.QUIZ_WAIT
        elif self.current_step == self.QUIZ_CHOICE: # квиз
            if self.quiz_timer == -1:
                self.selected_territories[0].set_owner(BOT if self.quiz_result[0] else NOBODY)
                self.selected_territories[1].set_owner(PLAYER if self.quiz_result[1] else NOBODY)
                self.selected_territories = []
                self.quiz_timer = 0
                self.quiz.reset()
                self.current_step = self.QUIZ_RESULT
            elif self.quiz_timer == 0:
                self.quiz_timer = pygame.time.get_ticks()
                self.quiz.new_question()
                self.quiz_result.append(random.random() < 0.8)
            elif pygame.time.get_ticks() - self.quiz_timer > 3000:
                self.quiz_timer = -1
                self.quiz_result.append(False)
            elif self.quiz_timer > 0:
                result = self.quiz.handle_event(event)
                if result is not None:
                    self.quiz_timer = -1
                    self.quiz_result.append(result)


    def draw(self) -> None:
        """Отрисовка всей игры."""
        self.surface.fill(WHITE)

        self.battlefield.draw()

        # подсказки хода
        if self.current_step == self.PLAYER_CHOICE or self.current_step == self.BOT_CHOICE:
            if self.current_step == self.PLAYER_CHOICE:
                turn_text = self.font.render("ВАШ ХОД! Нажмите на свободную территорию", True, GREEN)
            elif self.current_step == self.BOT_CHOICE:
                turn_text = self.font.render("ХОД БОТА...", True, BLUE)
            else:
                turn_text = self.font.render("", True, BLACK)
            turn_rect = turn_text.get_rect(center=(self.surface.width // 2, self.surface.height - 30))
            self.surface.blit(turn_text, turn_rect)

        # викторина
        if self.current_step == self.QUIZ_CHOICE:
            self.quiz.draw(self.surface)

        # рисуем временное сообщение
        if self.current_step == self.QUIZ_RESULT:
            self.message.draw(self.surface)

        # награждение
        if self.current_state == self.GAME_OVER:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            self.surface.blit(overlay, (0, 0))

            if self.winner == PLAYER:
                win_text = self.big_font.render("ПОБЕДИЛ ГЛИФИНДОЛ!1!", True, GREEN)
                sub_text = self.font.render("Нажмите ESC для выхода", True, WHITE)
            else:
                win_text = self.big_font.render("ЮУ ЛУУЗ!!", True, RED)
                sub_text = self.font.render("Нажмите ESC для выхода", True, WHITE)

            win_rect = win_text.get_rect(center=(self.surface.width // 2, self.surface.height // 2 - 50))
            sub_rect = sub_text.get_rect(center=(self.surface.width // 2, self.surface.height // 2 + 50))

            self.surface.blit(win_text, win_rect)
            self.surface.blit(sub_text, sub_rect)

    def reset(self) -> None:
        """Отчистка для перезапуска игры."""
        self.battlefield.reset()
        self.selected_territories = []

        self.winner = NOBODY

        self.quiz.reset()
        self.quiz_wait_timer = 0
        self.quiz_timer = 0
        self.quiz_result_timer = 0
        self.quiz_result = []

        self.bot_timer = 0

        self.message.reset()

        self.current_step = self.BOT_CHOICE
        self.current_state = self.EXPLORATION
