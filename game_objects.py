import pygame
import random
import pandas as pd
import numpy as np
from config import *
from typing import Literal

GRAPHS = pd.read_csv('maps/graphs.csv')
VERTICES = pd.read_csv('maps/vertices.csv')
EDGES = pd.read_csv('maps/adjacency.csv')

class Button:
    """Простой класс кнопки. Имеет отрисовку и обработку наводки/нажатия."""
    def __init__(self, x : int, y : int, width : int, height : int, text : str = '',
                 color : tuple[int, int, int] = WHITE, aim_color : tuple[int, int, int] = GREEN,
                 backlight_color: tuple[int, int, int] = BLACK, text_color : tuple[int, int, int] = BLACK,
                 font_size : int = 36):
        # коллайдер
        self.rect = pygame.Rect(x, y, width, height)
        # цвет кнопки(если использовать колайдер, как кнопку
        self.color = color
        # цвет кнопки при наведении
        self.aim_color = aim_color
        # цвет обводки
        self.backlight_color = backlight_color
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
            current_color = self.aim_color

        pygame.draw.rect(surface, current_color, self.rect , border_radius=12)
        pygame.draw.rect(surface, self.backlight_color, self.rect, 2, border_radius=12)

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
    def __init__(self, x : int, y : int):
        # коллайдер
        self.rect = pygame.Rect(x, y, CELL_SIZE - 5, CELL_SIZE - 5)
        # соседи
        self.neighbors : list[Territory] = []
        # владелец
        self.owner = NOBODY
        self.temporary = False
        # цвет
        self.color = GRAY

    def draw(self, surface : pygame.Surface, border_color : int = BLACK) -> None:
        """Отрисовка. Пока - прямоугольник с обводкой."""
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, width=2)

    def set_owner(self, owner : Literal[NOBODY, PLAYER, BOT], temporary : bool = False) -> None:
        """Сеттер. Задаёт владельца территории."""
        self.owner = owner
        self.temporary = temporary
        if owner == PLAYER:
            if self.temporary:
                self.color = PINK
            else:
                self.color = RED
        elif owner == BOT:
            if self.temporary:
                self.color = LIGHT_BLUE
            else:
                self.color = BLUE
        else:
            self.color = GRAY
            self.temporary = False


class Map:
    """Класс карты. Хранит граф территорий, рёбра и позиции территорий."""
    def __init__(self, surface : pygame.Surface):
        self.graph : list[Territory] = []
        self.surface = surface
        self.territory_position : list[(int, int)] = []
        self.edges_list : list[list[int]] = []
        self.load_new_graph()

    def load_new_graph(self) -> None:
        """Загружает новый граф из maps/"""
        graph = GRAPHS.sample().values[0]
        # print(graph[0])
        vertices = VERTICES[VERTICES['graph_id'] == graph[0]]
        adjacency = EDGES[EDGES['graph_id'] == graph[0]]
        # print(vertices)
        # print(adjacency)
        coordinates = vertices[['x_coord', 'y_coord']].values
        edges = adjacency[['territory_one', 'territory_two']].values
        self.create_graph(coordinates, edges)


    def create_graph(self, territory_pos : list[(int, int)] = [],
                     edges_list : list[list[int]] = []) -> None:
        """Создаёт граф по списку смежности с вершинами в указанных точках."""
        self.graph = [Territory(*pos) for pos in territory_pos]
        n = len(self.graph)
        for terr_a, terr_b in edges_list:
            self.graph[terr_b].neighbors.append(self.graph[terr_a])
            self.graph[terr_a].neighbors.append(self.graph[terr_b])
        self.territory_position = territory_pos
        self.edges_list = edges_list

    def get_territories(self, owner : Literal[NOBODY, PLAYER, BOT]) -> list[Territory]:
        """Возвращает список территорий, принадлежащих owner."""
        territories = []
        for territory in self.graph:
            if territory.owner == owner:
                territories.append(territory)
        return territories

    def get_neighbors(self, owner : Literal[PLAYER, BOT]) -> list[Territory]:
        """Возвращает список территорий, с которыми граничит owner."""
        territories = []
        owner_territories = self.get_territories(owner)
        for territory in owner_territories:
            for neighbor in territory.neighbors:
                if neighbor.owner != owner:
                    territories.append(neighbor)
        return territories

    def get_able_to_capture(self, owner : Literal[PLAYER, BOT]) -> list[Territory]:
        """
        Возвращает список свободных территорий, с которыми граничит owner.
        Если этот список пуст, то возвращает список свободных территорий.
        """
        territories = []
        owner_territories = self.get_territories(owner)
        for territory in owner_territories:
            for neighbor in territory.neighbors:
                if neighbor.owner == NOBODY:
                    territories.append(neighbor)
        if len(territories) == 0:
            return self.get_territories(NOBODY)
        return territories

    def reset(self) -> None:
        """Пересоздаём граф, можно сделать сохранение старого графа. Нужно для перезапуска игры."""
        # сохранение старого графа
        # self.create_graph(self.territory_position, self.edges_list)
        # генерация нового графа
        self.load_new_graph()

    def draw(self) -> None:
        """Отрисовка всех территорий на surface."""
        for territory in self.graph:
            territory.draw(self.surface)

    def draw_with_able_to_capture(self) -> None:
        """Отрисовка всех территорий на surface с подсветкой достижимых."""
        able_to_capture = self.get_able_to_capture(PLAYER)
        for territory in self.graph:
            territory.draw(self.surface, (GREEN if territory in able_to_capture else BLACK))


# сообщение (недоделан)
class Message:
    def __init__(self, alpha: int = 180):
        self.alpha = alpha
        self.is_show = False
        self.text = ""

        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

    def show(self, text : str) -> None:
        """Вспомогательная функция, запускает сообщение."""
        self.is_show = True
        self.text = text

    def draw(self, surface : pygame.Surface) -> None:
        """Рисует сообщение."""
        overlay = pygame.Surface(surface.get_size())
        overlay.set_alpha(self.alpha)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))

        msg_rect = pygame.Rect(surface.width // 3, surface.height // 3, surface.width // 3, 80)
        pygame.draw.rect(surface, WHITE, msg_rect)
        pygame.draw.rect(surface, BLACK, msg_rect, 3)

        msg_text = self.font.render(self.text, True, BLACK)
        msg_rect_text = msg_text.get_rect(center=(surface.width // 2, surface.height // 3 + 40))
        surface.blit(msg_text, msg_rect_text)

    def reset(self) -> None:
        self.is_show = False
        self.text = ""
