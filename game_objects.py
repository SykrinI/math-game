import pygame
import random
from config import *
from typing import Literal

class Button:
    """Простой класс кнопки. Имеет отрисовку и обработку наводки/нажатия."""
    def __init__(self, x : int, y : int, width : int, height : int, text : str = '',
                 color : tuple[int, int, int] = WHITE, text_color : tuple[int, int, int] = BLACK, font_size : int = 36):
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
        """Отрисовывает кнопку, учитывая наводку курсором.
        Принимает поверхность, на которой рисуем."""
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
        """Обрабатывает события, связанные с кнопкой.
        Принимает событие. Возвращает True, если кнопка была нажата, иначе - False."""
        # если событие - движение мыши, то изменияем состояние наведённости на кнопку
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True  # если кнопка нажат ЛКМ, то возвращаем true
        return False

class Territory:
    """Класс "территории" - представляет из себя одну ячейку, которую можно захватить.
    Поддерживает отрисовку и работу с владельцем территории.
    Хранит положение прямоугольника, номер строки и столбца на карте и владельца."""
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
        """Отрисовка. Пока - прямоугольник с обводкой."""
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, width=2)

    def set_owner(self, owner : Literal[NOBODY, PLAYER, BOT]) -> None:
        """Сеттер. Задаёт владельца территории."""
        self.owner = owner
        if owner == PLAYER:
            self.color = RED
        elif owner == BOT:
            self.color = BLUE
        else:
            self.color = GRAY


class Map:
    """Класс карты. Пока это просто row_count на col_count ячеек территории."""
    def __init__(self, surface : pygame.Surface, col_count : int, row_count : int):
        self.grid = []
        self.surface = surface
        self.row_count = row_count
        self.col_count = col_count
        self.create_grid()

    def create_grid(self) -> None:
        """Создаёт решётку."""
        start_x = (WIDTH - (CELL_SIZE * self.col_count)) // 2
        start_y = (HEIGHT - (CELL_SIZE * self.row_count)) // 2

        for r in range(self.row_count):
            row = []
            for c in range(self.col_count):
                x = start_x + (CELL_SIZE * c)
                y = start_y + (CELL_SIZE * r)
                row.append(Territory(x, y, r, c))
            self.grid.append(row)

    def get_territories(self, owner : Literal[NOBODY, PLAYER, BOT]) -> list[Territory]:
        """Возвращает список территорий, принадлежащих owner."""
        territories = []
        for row in self.grid:
            for territory in row:
                if territory.owner == owner:
                    territories.append(territory)
        return territories

    def reset(self) -> None:
        """Пересоздаём решётку. Нужно для перезапуска игры."""
        self.grid = []
        self.create_grid()

    def draw(self) -> None:
        """Отрисовка всех территорий на surface."""
        for row in self.grid:
            for territory in row:
                territory.draw(self.surface)

