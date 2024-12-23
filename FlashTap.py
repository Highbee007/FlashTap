import pygame
import sys
import random
from typing import List, Optional

# Constants for colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 205, 50)
RED = (255, 99, 71)
GOLD = (255, 215, 0)
LIGHT_BLUE = (173, 216, 230)
DARK_GRAY = (30, 30, 30)

# Button types
class ButtonType:
    GREEN = 1
    RED = 2
    GOLD = 3

class Button:
    def __init__(self, x, y, width, height, color, text=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.font = pygame.font.Font(None, 30)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        if self.text:
            text_surface = self.font.render(self.text, True, BLACK)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

class FlashTap:
    def __init__(self):
        pygame.init()
        self.width, self.height = 400, 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("FlashTap")
        self.clock = pygame.time.Clock()

        self.running = True
        self.game_active = False
        self.show_instructions = True

        self.score = 0
        self.mistakes = 0
        self.max_mistakes = 3

        self.buttons: List[Button] = []
        self.lane_width = self.width // 4
        self.spawn_timer = 0
        self.spawn_interval = 1.0
        self.tiles: List[Button] = []

        self.tile_speed = 200  # Base speed of tiles
        self.max_tiles = 6  # Maximum number of tiles on screen

        # Start, Instruction, Replay, and Quit buttons
        self.start_button = Button(self.width // 2 - 75, self.height // 2 - 50, 150, 50, GREEN, "Start")
        self.instructions_button = Button(self.width // 2 - 75, self.height // 2 + 20, 150, 50, GOLD, "Instructions")
        self.back_button = Button(10, 10, 100, 40, RED, "Back")
        self.replay_button = Button(self.width // 2 - 75, self.height // 2 - 50, 150, 50, GREEN, "Replay")
        self.quit_button = Button(self.width // 2 - 75, self.height // 2 + 20, 150, 50, RED, "Quit")

    def reset_game(self):
        self.score = 0
        self.mistakes = 0
        self.tiles.clear()
        self.tile_speed = 200  # Reset speed
        self.game_active = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                if not self.game_active:
                    if self.start_button.rect.collidepoint(x, y):
                        self.reset_game()
                    elif self.instructions_button.rect.collidepoint(x, y):
                        self.show_instructions = True
                    elif self.back_button.rect.collidepoint(x, y):
                        self.show_instructions = False
                    elif self.replay_button.rect.collidepoint(x, y):
                        self.reset_game()
                    elif self.quit_button.rect.collidepoint(x, y):
                        self.running = False
                else:
                    self.handle_tap(x, y)

    def handle_tap(self, x, y):
        for tile in self.tiles[:]:
            if tile.rect.collidepoint(x, y):
                if tile.color == GREEN:
                    self.score += 10
                elif tile.color == RED:
                    self.mistakes += 1
                elif tile.color == GOLD:
                    self.score += 50
                self.tiles.remove(tile)
                break

    def spawn_tile(self):
        if len(self.tiles) < self.max_tiles:
            lane = random.randint(0, 3)
            x = lane * self.lane_width + self.lane_width // 4
            color = random.choices([GREEN, RED, GOLD], weights=[70, 20, 10])[0]
            self.tiles.append(Button(x, -80, self.lane_width // 2, 80, color))

    def update(self, delta_time):
        if self.game_active:
            self.spawn_timer += delta_time
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_tile()
                self.spawn_timer = 0

            # Gradually increase tile speed based on score
            self.tile_speed = 200 + (self.score // 50) * 20

            for tile in self.tiles[:]:
                tile.rect.y += self.tile_speed * delta_time
                if tile.rect.y > self.height:
                    if tile.color == GREEN:
                        self.mistakes += 1
                    self.tiles.remove(tile)

            if self.mistakes >= self.max_mistakes:
                self.game_active = False

    def draw(self):
        self.screen.fill(DARK_GRAY)

        if self.show_instructions:
            self.draw_instructions()
        elif not self.game_active:
            self.draw_menu()
        else:
            self.draw_game()

        pygame.display.flip()

    def draw_menu(self):
        font = pygame.font.Font(None, 50)
        title = font.render("FlashTap", True, WHITE)
        title_rect = title.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title, title_rect)

        if self.score > 0:
            self.replay_button.draw(self.screen)
            self.quit_button.draw(self.screen)

            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Your Score: {self.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(self.width // 2, 300))
            self.screen.blit(score_text, score_rect)
        else:
            self.start_button.draw(self.screen)
            self.instructions_button.draw(self.screen)

    def draw_instructions(self):
        font = pygame.font.Font(None, 36)
        instructions = [
            "Tap GREEN tiles to score points.",
            "Tap GOLD tiles for bonus points.",
            "Avoid RED tiles to prevent mistakes.",
            "Don't let GREEN tiles fall more than 2 times!",
        ]
        for i, line in enumerate(instructions):
            text = font.render(line, True, WHITE)
            text_rect = text.get_rect(center=(self.width // 2, 150 + i * 40))
            self.screen.blit(text, text_rect)

        self.back_button.draw(self.screen)

    def draw_game(self):
        for tile in self.tiles:
            tile.draw(self.screen)

        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        mistakes_text = font.render(f"Lives: {self.max_mistakes - self.mistakes}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(mistakes_text, (10, 50))

    def run(self):
        while self.running:
            delta_time = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(delta_time)
            self.draw()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = FlashTap()
    game.run()
