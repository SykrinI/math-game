import pygame
from config import *

class Button:
    def __init__(self, x, y, width, height, text, color, text_color=BLACK, font_size=36):
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
        
    def draw(self, surface):
        # чуть-чуть осветляем кнопку, если is_hovered=True
        current_color = self.color
        if self.is_hovered:
            # current_color = tuple(min(c + 50, 255) for c in self.color)
            current_color = GREEN
        
        pygame.draw.rect(surface, current_color, self.rect , border_radius=12)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=12)
        
        # делаем surface с текстом на нём
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    # событие нажатия на кнопку
    def handle_event(self, event):
        # если событие - движение мыши, то изменияем состояние наведённости на кнопку
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True  # если кнопка нажат ЛКМ, то возвращаем true
        return False
