import pygame
import random
import pandas as pd
import numpy as np
from game_objects import *
from config import *

# мучающие меня вопросы
QUESTIONS = pd.read_csv("questions.csv")


class Quiz:
    """"Класс квиза. Реализует создание и отрисовку вопросов."""
    def __init__(self, surface : pygame.Surface):
        self.surface = surface
        self.current_question = None
        self.current_button = None
        self.active = False
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.buttons = [Button(WIDTH // 3, 2 * HEIGHT // 3, WIDTH // 3, 50, color=GRAY),
                        Button(WIDTH // 3, 2 * HEIGHT // 3 - 65, WIDTH // 3, 50, color=GRAY),
                        Button(WIDTH // 3, 2 * HEIGHT // 3 - 130, WIDTH // 3, 50, color=GRAY),
                        Button(WIDTH // 3, 2 * HEIGHT // 3 - 195, WIDTH // 3, 50, color=GRAY)]


    def new_question(self) -> None:
        """"
        Выбирает новый вопрос. Для него перезагружает объект класса. Запускает квиз.
        """
        self.current_button = None
        self.active = True
        # случайный вопрос
        self.current_question = QUESTIONS.sample().values[0]
        # случайная расстановка кнопок
        answers = np.random.choice(self.current_question[1:], size=4, replace=False)
        for i in range(4):
            self.buttons[i].color = GRAY
            self.buttons[i].text = answers[i]

    # событие выбора ответа
    def handle_event(self, event : pygame.Event) -> bool | None:
        """
        Обрабатывет событие выбора ответа игроком.
        Принимает событие. Если нажатия не было, возвращает None.
        Если ответ верен возвращает True. Иначе - False.
        """
        if not self.active:
            return None
        # выбираем ответик
        for button in self.buttons:
            if button.handle_event(event):
                self.active = False
                return self.current_question[1] == button.text
        return None

    def draw(self) -> None:
        """
        Отрисовка.
        """
        if not self.active:
            return

        # затемнение фона (тёмное стёклышко)
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(100)
        overlay.fill(BLACK)
        self.surface.blit(overlay, (0, 0))

        # окно викторины
        quiz_rect = pygame.Rect(WIDTH // 6, HEIGHT // 6, 2 * WIDTH // 3, 2 * HEIGHT // 3)
        pygame.draw.rect(self.surface, WHITE, quiz_rect,  border_radius=12)
        pygame.draw.rect(self.surface, BLACK, quiz_rect, 2,  border_radius=12)

        # текст вопроcа
        q_text = self.font.render(self.current_question[0], True, BLACK)
        q_rect = q_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        self.surface.blit(q_text, q_rect)

        # кнопки
        for button in self.buttons:
            button.draw(self.surface)

        # Инструкция
        instr_text = self.small_font.render("Выберите один вариант", True, BLACK)
        instr_rect = instr_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 175))
        self.surface.blit(instr_text, instr_rect)
