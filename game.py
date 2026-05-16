from game_objects import *
from quiz import *

class Game:
    """Основной класс игры."""

    # состояния
    BOT_EXPLORATION = 0
    PLAYER_EXPLORATION = 1
    BOT_CHOICE = 2
    PLAYER_CHOICE = 3
    QUIZ_WAIT = 4
    QUIZ_CHOICE = 5
    QUIZ_RESULT = 6


    def __init__(self, surface : pygame.Surface):
        self.surface = surface
        self.battlefield = Map(surface)

        self.selected_territories = []

        self.winner = NOBODY

        # квиз
        self.quiz = Quiz()
        self.quiz_wait_timer = 0
        self.quiz_timer = 0
        self.quiz_result_timer = 0
        self.quiz_result = []
        self.selected_answers = []

        # всё для бота и огорода
        self.bot_timer = 0

        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

        self.current_state = self.BOT_EXPLORATION
        self.game_over = False


    # тупая версия
    def check_win(self) -> bool:
        """Возвращает True и устанавливает победителя. Иначе возвращает False."""
        pt = self.battlefield.get_territories(PLAYER)
        bt = self.battlefield.get_territories(BOT)
        nt = self.battlefield.get_territories(NOBODY)
        if len(nt) == 0 or len(nt) == 1:
            self.game_over = True
            self.winner = PLAYER if len(pt) > len(bt) else BOT
            return True
        return False


    def update(self) -> None:
        """Главный метод. Обновляет все состояния игры."""
        if self.game_over:
            return

        if self.current_state == self.BOT_EXPLORATION:
            # сначала ждёт
            if self.bot_timer == 0:
                self.bot_timer = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.bot_timer > 1000:
                random.choice(self.battlefield.get_able_to_capture(BOT)).set_owner(BOT)
                self.bot_timer = 0
                self.current_state = self.PLAYER_EXPLORATION

        if self.current_state == self.BOT_CHOICE: # бот выбирает территорию
            # сначала ждёт
            if self.bot_timer == 0:
                self.bot_timer = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.bot_timer > 1000:
                self.selected_territories.append(random.choice(self.battlefield.get_able_to_capture(BOT)))
                self.selected_territories[0].set_owner(BOT, temporary=True)

                self.bot_timer = 0
                self.current_state = self.PLAYER_CHOICE

        elif self.current_state == self.QUIZ_WAIT: # ожидание квиза
            if self.quiz_wait_timer == 0:
                self.quiz_wait_timer = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.quiz_wait_timer > 200:
                self.quiz_wait_timer = 0
                self.current_state = self.QUIZ_CHOICE

        elif self.current_state == self.QUIZ_CHOICE:  # квиз
            if self.quiz_timer == -1:
                self.selected_territories[0].set_owner(BOT if self.quiz_result[0] else NOBODY)
                self.selected_territories[1].set_owner(PLAYER if self.quiz_result[1] else NOBODY)
                self.selected_territories = []
                self.quiz_timer = 0
                self.current_state = self.QUIZ_RESULT
            elif self.quiz_timer == 0:
                self.quiz_timer = pygame.time.get_ticks()
                self.quiz.new_question()
                self.quiz_result.append(random.random() < 0.8)
                if self.quiz_result[0]:
                    self.selected_answers.append(self.quiz.current_question[1] )
                else:
                    self.selected_answers.append(np.random.choice(self.quiz.current_question[2:]))
            elif pygame.time.get_ticks() - self.quiz_timer > 4000:
                self.quiz_timer = -1
                self.quiz_result.append(False)
                self.selected_answers.append(None)


        elif self.current_state == self.QUIZ_RESULT: # подведение итогов квиза
            # в конце будет проверять победителя
            if self.quiz_result_timer == 0:
                self.quiz_result_timer = pygame.time.get_ticks()
                self.quiz.reset_buttons()
                self.quiz.set_answer(self.selected_answers[0], BOT)
                self.quiz.set_answer(self.selected_answers[1], PLAYER)
            elif pygame.time.get_ticks() - self.quiz_result_timer > 3000:
                self.quiz_result_timer = 0
                self.quiz_result = []
                self.selected_answers = []
                self.check_win()
                self.quiz.reset()
                self.current_state = self.BOT_CHOICE
            elif pygame.time.get_ticks() - self.quiz_result_timer > 1500:
                self.quiz.backlight_correct_answer()


    def event_update(self, event : pygame.Event) -> None:
        """Обновляем атрибуты, зависящие от события event."""
        if self.current_state == self.PLAYER_EXPLORATION:
            # определяем территорию, куда будет ходить игрок: в соседние или в незанятую
            territories_to_capture = self.battlefield.get_able_to_capture(PLAYER)
            for territory in territories_to_capture:
                if event.type == pygame.MOUSEBUTTONDOWN and territory.rect.collidepoint(event.pos):
                    territory.set_owner(PLAYER)
                    self.current_state = self.BOT_CHOICE
                    break

        elif self.current_state == self.PLAYER_CHOICE: # игрок выбирает территорию
            # определяем территорию, куда будет ходить игрок: в соседние или в незанятую
            territories_to_capture = self.battlefield.get_able_to_capture(PLAYER)
            for territory in territories_to_capture:
                if event.type == pygame.MOUSEBUTTONDOWN and territory.rect.collidepoint(event.pos):
                    self.selected_territories.append(territory)
                    self.selected_territories[1].set_owner(PLAYER, temporary=True)
                    self.current_state = self.QUIZ_WAIT
                    break

        elif self.current_state == self.QUIZ_CHOICE: # квиз
            if self.quiz_timer > 0:
                result = self.quiz.handle_event(event)
                if result is not None:
                    self.quiz_timer = -1
                    self.quiz_result.append(result == self.quiz.current_question[1])
                    self.selected_answers.append(result)


    def draw(self) -> None:
        """Отрисовка всей игры."""
        self.surface.fill(WHITE)

        # помечаем зелёной обводкой территории, на которые можем сходить
        if self.current_state in [self.PLAYER_CHOICE, self.PLAYER_EXPLORATION]:
            self.battlefield.draw_with_able_to_capture()
        else:
            self.battlefield.draw()

        # подсказки хода
        if self.current_state in [self.PLAYER_CHOICE, self.BOT_CHOICE, self.BOT_EXPLORATION, self.PLAYER_EXPLORATION]:
            if self.current_state in [self.PLAYER_CHOICE, self.PLAYER_EXPLORATION]:
                turn_text = self.font.render("ВАШ ХОД! Нажмите на свободную территорию", True, GREEN)
            elif self.current_state in [self.BOT_CHOICE, self.BOT_EXPLORATION]:
                turn_text = self.font.render("ХОД БОТА...", True, BLUE)
            else:
                turn_text = self.font.render("", True, BLACK)
            turn_rect = turn_text.get_rect(center=(self.surface.width // 2, self.surface.height - 30))
            self.surface.blit(turn_text, turn_rect)

        # викторина
        if self.quiz.active: # будет рисоваться до конца quiz_result
            self.quiz.draw(self.surface)

        # награждение
        if self.game_over:
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
        self.selected_answers = []

        self.bot_timer = 0

        self.current_state = self.BOT_EXPLORATION
        self.game_over = False
