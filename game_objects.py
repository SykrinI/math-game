from questions import *
from typing import Literal

class Button:
    '''Простой класс кнопки. Имеет отрисовку и обработку наводки/нажатия.'''
    def __init__(self, x : int, y : int, width : int, height : int, text : str, color : tuple[int, int, int], text_color : tuple[int, int, int] = BLACK, font_size : int = 36):
        # коллайдер
        self.rect = pygame.Rect(x, y, width, height)
        # цвет кнопки(если использовать колайдер, как кнопку
        self.color = color
        # текста на кнопке
        self.text = text
        # цвет текста на кнопке
        self.text_color = text_color
        # шрифт текта
        self.font = pygame.font.Font(None, font_size)
        # Is на кнопку наведён курсор?
        self.is_hovered = False

    def draw(self, surface : pygame.Surface) -> None:
        '''Отрисовывает кнопку, учитывая наводку курсором.
        Принимает поверхность, на которой рисуем. Возвращает None.'''
        current_color = self.color
        # меняем цвет кнопки, если is_hovered=True
        if self.is_hovered:
            # current_color = tuple(min(c + 50, 255) for c in self.color)
            current_color = GREEN

        pygame.draw.rect(surface, current_color, self.rect , border_radius=12)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=12)

        # делаем surface с текстом на нём
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event : pygame.Event) -> bool:
        '''Обрабатывает события, связанные с кнопкой.
        Принимает событие. Возвращает True, если кнопка была нажата, иначе - False.'''
        # если событие - движение мыши, то изменияем состояние наведённости на кнопку
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True  # если кнопка нажат ЛКМ, то возвращаем true
        return False

class Territory:
    '''Класс "территории" - представляет из себя одну ячейку, которую можно захватить. Поддерживает отрисовку и работу с владельцем территории.
    Хранит положение прямоугольника, номер строки и столбца на карте и владельца.'''
    def __init__(self, x : int, y : int, row : int, col : int):
        # коллайдер
        self.rect = pygame.Rect(x, y, CELL_SIZE - 5, CELL_SIZE - 5)
        # номер строки
        self.row = row
        # номер столбца
        self.col = col
        # владелец
        self.owner = NOBODY
        # цвет
        self.color = GRAY

    def draw(self, surface : pygame.Surface) -> None:
        '''Отрисовка. Пока прямоугольник с обводкой.'''
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, width=2)

    def set_owner(self, owner : Literal[NOBODY, PLAYER, BOT]) -> None:
        '''Сеттер. Задаёт владельца территории.'''
        self.owner = owner
        if owner == PLAYER:
            self.color = RED
        elif owner == BOT:
            self.color = BLUE
        else:
            self.color = GRAY


class Map:
    '''Класс карты. Пока это просто row_count на col_count ячеек территории.'''
    def __init__(self, surface : pygame.Surface, col_count : int, row_count : int):
        self.grid = []
        self.surface = surface
        self.row_count = row_count
        self.col_count = col_count
        self.create_grid()

    def create_grid(self) -> None:
        '''Создаёт решётку.'''
        start_x = (WIDTH - (CELL_SIZE * self.col_count)) // 2
        start_y = (HEIGHT - (CELL_SIZE * self.row_count)) // 2

        for r in range(self.row_count):
            row = []
            for c in range(self.col_count):
                x = start_x + (CELL_SIZE * c)
                y = start_y + (CELL_SIZE * r)
                row.append(Territory(x, y, r, c))
            self.grid.append(row)

    def get_territories(self, owner : Literal[NOBODY, PLAYER, BOT]) -> Territory:
        '''Возвращает список территорий, принадлежащих owner.'''
        territories = []
        for row in self.grid:
            for territory in row:
                if territory.owner == owner:
                    territories.append(territory)
        return territories

    def reset(self) -> None:
        '''Пересоздаём решётку. Нужно для перезапуска игры.'''
        self.grid = []
        self.create_grid()

    def draw(self) -> None:
        '''Отрисовка всех территорий на surface.'''
        for row in self.grid:
            for territory in row:
                territory.draw(self.surface)


class Game:
    '''Основной класс игры.'''
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
        '''Вспомогательная функция, обновляющая текст сообщения игры.'''
        self.show_message = True
        self.message_text = text
        self.message_timer = pygame.time.get_ticks()

    def bot_move(self):
        '''Функция, выполняющая ход бота.'''
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
        '''Смотрит, куда походил игрок. Обновляет состояние игры в зависимости от данных.'''
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
        '''Захват территории :-). Меняет владельца территории territory на owner и сменяет ход.'''
        territory.set_owner(owner)
        self.check_win()
        # смена хода
        if self.current_state != self.GAME_OVER:
            self.current_turn = BOT if owner == PLAYER else PLAYER

    # делается то, что не зависит от игрока
    def update(self) -> None:
        '''Обновляет всё, что не зависит от игрока.'''
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
        '''Отрисовка всей игры.'''
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
        '''Обновляет данные по результату квиза.'''
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
        '''Отчистка для перезапуска игры.'''
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
        '''Обновляем атрибуты в зависимости от события event.'''
        if self.waiting_for_quiz:
            result = self.quiz.handle_event(event)
            if result is not None:
                self.handle_quiz_result(result)
        elif self.current_state != self.GAME_OVER and not self.show_message:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_click(event.pos)

