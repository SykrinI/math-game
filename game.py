from game_objects import *
from quiz import *

class Game:
    """Основной класс игры."""
    EXPLORATION = 0
    FIGHTING = 1
    GAME_OVER = 2

    def __init__(self, surface : pygame.Surface, col_count : int, row_count : int) -> None:
        self.surface = surface
        self.battlefield = Map(surface, col_count, row_count)

        self.current_turn = random.choice([PLAYER, BOT])
        self.winner = NOBODY
        self.quiz = Quiz(surface)
        self.waiting_for_quiz = False
        self.selected_territory = None

        # всё для бота и огорода
        self.bot_timer = 0

        # сообщение (используется для квиза и ходов бота)
        self.show_message = False
        self.message_text = ""
        self.message_timer = 0

        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

        self.exploration_step = 0
        self.fighting_step = 0
        self.current_state = 0

    # тупая версия
    def check_win(self) -> bool:
        """Возвращает True и устанавливает победителя. Иначе возвращает False."""
        pt = self.battlefield.get_territories(PLAYER)
        bt = self.battlefield.get_territories(BOT)

        if len(self.battlefield.get_territories(NOBODY)) == 0:
            self.current_state = self.GAME_OVER
            self.winner = PLAYER if len(pt) > len(bt) else BOT
            return True
        return False

    # запускает сообщение ботяры
    def show_temporary_message(self, text : str) -> None:
        """Вспомогательная функция, обновляющая текст сообщения игры."""
        self.show_message = True
        self.message_text = text
        self.message_timer = pygame.time.get_ticks()

    def bot_move(self):
        """Функция, выполняющая ход бота."""
        empty = self.battlefield.get_territories(NOBODY)
        if empty:
            self.selected_territory = random.choice(empty)
            # ботяра отвечает на вопрос (80% шанс правильного ответа)
            bot_answer_correct = random.random() < 0.8

            if bot_answer_correct:
                self.capture_territory(self.selected_territory, BOT)
                self.show_temporary_message("Ботяра захватил территорию!")
            else:
                self.show_temporary_message(f"Бот ошибся, дурачёк, что сказать...")

            self.selected_territory = None

            self.current_turn = PLAYER
        else:
            self.check_win()

    def handle_click(self, pos : tuple[int, int]) -> None:
        """Смотрит, куда походил игрок. Обновляет состояние игры в зависимости от данных."""
        if self.current_state == self.GAME_OVER or self.waiting_for_quiz or self.show_message:
            return

        # ищему куда тыкнул и запускаем квиз
        if self.current_turn == PLAYER:
            for row in self.battlefield.grid:
                for territory in row:
                    if territory.rect.collidepoint(pos) and territory.owner == 0:
                        self.selected_territory = territory
                        self.waiting_for_quiz = True
                        self.quiz.new_question()
                        return

    def capture_territory(self, territory : Territory, owner : Literal[NOBODY, PLAYER, BOT]) -> None:
        """Захват территории :-). Меняет владельца территории territory на owner и сменяет ход."""
        territory.set_owner(owner)
        self.check_win()
        # смена хода
        if self.current_state != self.GAME_OVER:
            self.current_turn = BOT if owner == PLAYER else PLAYER

    # делается то, что не зависит от игрока
    def update(self) -> None:
        """Обновляет всё, что не зависит от игрока."""
        if self.current_state == self.GAME_OVER:
            return

        # сидим ждём пока покажется сообщение
        if self.show_message and pygame.time.get_ticks() - self.message_timer > 1500:
            self.show_message = False

        # сидим ждём пока походит ботяра
        if self.current_turn == BOT and not self.waiting_for_quiz and not self.show_message:
            # сидим сидим
            if self.bot_timer == 0:
                self.bot_timer = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.bot_timer > 1500:
                self.bot_move()
                self.bot_timer = 0
        else:
            self.bot_timer = 0

    def draw(self) -> None:
        """Отрисовка всей игры."""
        self.surface.fill(WHITE)

        self.battlefield.draw()

        # подсказки хода
        if self.current_state != self.GAME_OVER:
            if self.current_turn == PLAYER:
                turn_text = self.font.render("ВАШ ХОД! Нажмите на свободную территорию", True, GREEN)
            else:
                if self.bot_timer > 0:
                    turn_text = self.font.render("ХОД БОТА...", True, BLUE)
                else:
                    turn_text = self.font.render("ХОД БОТА", True, BLUE)
        else:
            turn_text = self.font.render("", True, BLACK)

        turn_rect = turn_text.get_rect(center=(WIDTH // 2, HEIGHT - 30))
        self.surface.blit(turn_text, turn_rect)

        # рисуем викторину
        self.quiz.draw()

        # рисуем временное сообщение
        if self.show_message:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.surface.blit(overlay, (0, 0))

            msg_rect = pygame.Rect(WIDTH // 6, HEIGHT // 3, (WIDTH * 2) // 3, 80)
            pygame.draw.rect(self.surface, WHITE, msg_rect)
            pygame.draw.rect(self.surface, BLACK, msg_rect, 3)

            msg_text = self.font.render(self.message_text, True, BLACK)
            msg_rect_text = msg_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 40))
            self.surface.blit(msg_text, msg_rect_text)

        # награждение пикселями
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

            win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

            self.surface.blit(win_text, win_rect)
            self.surface.blit(sub_text, sub_rect)

    def handle_quiz_result(self, is_correct : bool) -> None:
        """Обновляет данные по результату квиза."""
        if is_correct:
            if self.selected_territory:
                self.capture_territory(self.selected_territory, PLAYER)
                self.show_temporary_message("Правильно!")
        else:
            self.show_temporary_message(f"Неправильно!")
            self.current_turn = BOT

        self.waiting_for_quiz = False
        self.selected_territory = None

    def reset(self) -> None:
        """Отчистка для перезапуска игры."""
        self.current_turn = random.choice([PLAYER, BOT])
        self.winner = NOBODY
        self.waiting_for_quiz = False
        self.selected_territory = None
        self.bot_timer = 0
        self.show_message = False
        self.message_text = ""
        self.message_timer = 0

        self.exploration_step = 0
        self.fighting_step = 0
        self.current_state = 0
        self.battlefield.reset()

    def event_update(self, event : pygame.Event) -> None:
        """Обновляем атрибуты в зависимости от события event."""
        if self.waiting_for_quiz:
            result = self.quiz.handle_event(event)
            if result is not None:
                self.handle_quiz_result(result)
        elif self.current_state != self.GAME_OVER and not self.show_message:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_click(event.pos)

