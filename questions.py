import pygame
import random
from config import *

# мучающие меня вопросы
QUESTIONS = [
    ("Почему?", "Потому что"),
    ("2 + 1?", "21"),
    ("Напиши 7 пыж пыж пыж пыж", "7"),
    ("Зачем?", "За мясом"),
    ("Ку", "КуКу"),
    ("Откуда?", "От верблюда")
]

class Quiz:
    def __init__(self, surface):
        self.surface = surface
        self.current_question = None
        self.current_answer = None
        self.input_text = ""
        self.active = False
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def new_question(self):
        self.current_question, self.current_answer = random.choice(QUESTIONS)
        self.input_text = ""
        self.active = True

    # событие ввода с клавы (коки)
    def handle_event(self, event):
        if not self.active:
            return None

        # вводим ответик
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.active = False
                return self.input_text.strip().lower() == self.current_answer.lower()
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                self.input_text += event.unicode
        return None

    def draw(self):
        if not self.active:
            return

        # затемнение фона (тёмное стёклышко)
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(100)
        overlay.fill(BLACK)
        self.surface.blit(overlay, (0, 0))

        # окно викторины
        quiz_rect = pygame.Rect(WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2)
        pygame.draw.rect(self.surface, WHITE, quiz_rect,  border_radius=12)
        pygame.draw.rect(self.surface, BLACK, quiz_rect, 2,  border_radius=12)

        # текст вопрома
        q_text = self.font.render(self.current_question, True, BLACK)
        q_rect = q_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.surface.blit(q_text, q_rect)

        # поле ввода (и текст на нём)
        input_rect = pygame.Rect(WIDTH // 3, HEIGHT // 2, WIDTH // 3, 50)
        pygame.draw.rect(self.surface, GRAY, input_rect)
        pygame.draw.rect(self.surface, BLACK, input_rect, 2)

        input_surface = self.font.render(self.input_text + "|", True, BLACK)
        self.surface.blit(input_surface, (input_rect.x + 10, input_rect.y + 10))

        # Инструкция
        instr_text = self.small_font.render("Введите ответ и нажмите Enter", True, BLACK)
        instr_rect = instr_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        self.surface.blit(instr_text, instr_rect)
