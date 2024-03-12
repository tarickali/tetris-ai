from typing import Any
import pygame

from arcade.engine.ui import Pane, Window
from tetris.game import Game

################################################################################
# Constants
################################################################################
# Grid cells
CELL_SHAPE = (20, 20)

# Screen
SCREEN_SHAPE = (600, 600)

# NOTE: These are defined in pixels
MAIN_PANE_SHAPE = (400, 400)
MAIN_PANE_POSITION = (10, 10)
MAIN_PANE_SCALE = (1.0, 1.0)
SIDE_PANE_SHAPE = (100, 300)
SIDE_PANE_POSITION = (420, 10)
SIDE_PANE_SCALE = (1.0, 1.0)
INFO_PANE_SHAPE = (100, 100)
INFO_PANE_POSITION = (420, 310)
INFO_PANE_SCALE = (1.0, 1.0)

# Fonts
FONT_SIZE = 15
################################################################################


class Renderer:
    def __init__(self, game: Game) -> None:
        self.game = game

        panes = {
            "main": Pane(
                MAIN_PANE_SHAPE, MAIN_PANE_POSITION, MAIN_PANE_SCALE, (2, -1, "red")
            ),
            "info": Pane(
                INFO_PANE_SHAPE, INFO_PANE_POSITION, INFO_PANE_SCALE, (2, -1, "red")
            ),
            "side": Pane(
                SIDE_PANE_SHAPE, SIDE_PANE_POSITION, SIDE_PANE_SCALE, (2, -1, "red")
            ),
        }
        self.window = Window(SCREEN_SHAPE, panes)
        self.font = pygame.font.Font(None, FONT_SIZE)

    def render(self) -> None:
        state = self.game.state()
        self.draw_main_pane(state)
        self.draw_side_pane(state)
        self.draw_info_pane(state)

        # Render the window
        self.window.render()
        self.window.update()

    def draw_main_pane(self, state: dict[str, Any]) -> None:
        # Update main pane
        main_pane = self.window.panes["main"]
        main_pane.surface.fill("black")
        self.draw_gridlines(main_pane.surface)

        for y in range(len(state["grid"])):
            for x in range(len(state["grid"][y])):
                num = state["grid"][y][x]
                if num == 0:
                    continue

                self.draw_block(
                    main_pane.surface,
                    (x * CELL_SHAPE[0], y * CELL_SHAPE[1]),
                    CELL_SHAPE,
                    self.game.colors[self.game.itos[num]],
                )

    def draw_block(
        self,
        surface: pygame.Surface,
        position: tuple[int, int],
        shape: tuple[int, int],
        color: pygame.Color,
    ) -> None:
        block = Block(position, shape, color)
        block.draw(surface)

    def draw_tetromino(
        self,
        surface: pygame.Surface,
        position: tuple[int, int],
        shape: tuple[int, int],
        num: str,
    ):
        tetromino = self.game.shapes[self.game.itos[num]][0]
        color = self.game.colors[self.game.itos[num]]

        for y in range(len(tetromino)):
            for x in range(len(tetromino[y])):
                if tetromino[y][x] == 0:
                    continue
                self.draw_block(
                    surface,
                    (position[0] + x * shape[0], position[1] + y * shape[1]),
                    shape,
                    color,
                )

    def draw_side_pane(self, state: dict[str, Any]) -> None:
        # Update side pane
        side_pane = self.window.panes["side"]
        side_pane.surface.fill("black")
        side_text = self.font.render("Next Tetromino", False, "white", None)
        side_pane.surface.blit(side_text, side_text.get_rect(topleft=(20, 10)))
        self.draw_tetromino(
            side_pane.surface, (20, 50), (20, 20), state["next_tetrominos"][-1]
        )

        side_text = self.font.render("Held Tetromino", False, "white", None)
        side_pane.surface.blit(side_text, side_text.get_rect(topleft=(20, 150)))
        if state["held_tetromino"]:
            self.draw_tetromino(
                side_pane.surface, (20, 180), (20, 20), state["held_tetromino"]
            )

    def draw_info_pane(self, state: dict[str, Any]) -> None:
        # Update info pane
        info_pane = self.window.panes["info"]
        info_pane.surface.fill("black")
        score_text = self.font.render(f"Score: {state['score']}", False, "white", None)
        info_pane.surface.blit(score_text, score_text.get_rect(topleft=(10, 10)))
        lines_text = self.font.render(f"Lines: {state['lines']}", False, "white", None)
        info_pane.surface.blit(lines_text, score_text.get_rect(topleft=(10, 30)))

    def draw_gridlines(self, display: pygame.Surface):
        for y in range(self.game.height):
            for x in range(self.game.width):
                rect = pygame.Rect(x * CELL_SHAPE[0], y * CELL_SHAPE[1], *CELL_SHAPE)
                pygame.draw.rect(display, "white", rect, 1)


class Block(pygame.sprite.Sprite):
    def __init__(
        self,
        position: tuple[int, int],
        shape: tuple[int, int],
        color: pygame.Color = "white",
    ) -> None:
        super().__init__()
        self.image = pygame.Surface(shape)
        self.rect = self.image.get_rect(topleft=position)
        self.image.fill(color)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)
        x, y, w, h = self.rect.x, self.rect.y, self.rect.w, self.rect.h
        # top line
        pygame.draw.rect(screen, "grey", [x, y, w, 2])
        # bottom line
        pygame.draw.rect(screen, "grey", [x, y + h, w, 2])
        # left line
        pygame.draw.rect(screen, "grey", [x, y, 2, h])
        # right line
        pygame.draw.rect(screen, "grey", [x + w, y, 2, h + 2])
