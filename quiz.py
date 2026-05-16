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
    def __init__(self):
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
    def handle_event(self, event : pygame.Event) -> str | None:
        """
        Обрабатывет событие выбора ответа игроком.
        Принимает событие. Если нажатия не было, возвращает None.
        Иначе возвращает текст нажатой кнопки.
        """
        if not self.active:
            return None
        # выбираем ответик
        for button in self.buttons:
            if button.handle_event(event):
                return button.text
        return None

    def set_answer(self, answer : str | None, player : Literal[PLAYER, BOT]) -> None:
        """"Устанавливает цвет книпки, когда её выбирает один из игроков."""
        if answer is None:
            return
        for button in self.buttons:
            if button.text == answer:
                if button.color == PINK or button.color == LIGHT_BLUE:
                    button.color = PURPLE
                else:
                    button.color = PINK if player == PLAYER else LIGHT_BLUE
                break

    def backlight_correct_answer(self):
        for button in self.buttons:
            if button.text == self.current_question[1]:
                button.backlight_color = GREEN
                break

    def draw(self, surface : pygame.Surface) -> None:
        """
        Отрисовка.
        """

        # затемнение фона (тёмное стёклышко)
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(100)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))

        # окно викторины
        quiz_rect = pygame.Rect(WIDTH // 6, HEIGHT // 6, 2 * WIDTH // 3, 2 * HEIGHT // 3)
        pygame.draw.rect(surface, WHITE, quiz_rect,  border_radius=12)
        pygame.draw.rect(surface, BLACK, quiz_rect, 2,  border_radius=12)

        # текст вопроcа
        q_text = self.font.render(self.current_question[0], True, BLACK)
        q_rect = q_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        surface.blit(q_text, q_rect)

        # кнопки
        for button in self.buttons:
            button.draw(surface)

        # Инструкция
        instr_text = self.small_font.render("Выберите один вариант", True, BLACK)
        instr_rect = instr_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 175))
        surface.blit(instr_text, instr_rect)

    def reset(self):
        self.current_question = None
        self.current_button = None
        self.active = False
        for button in self.buttons:
            button.color = GRAY
            button.backlight_color = BLACK
            button.is_hovered = False

    def reset_buttons(self):
        for button in self.buttons:
            button.color = GRAY
            button.backlight_color = BLACK
            button.is_hovered = False

