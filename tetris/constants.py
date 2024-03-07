# Grid
GRID_SHAPE = (20, 20)

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

FONT_SIZE = 15
FPS = 60
DELAY_TIME = 60


SHAPES = [
    # T
    [
        [[1, 1, 1], [0, 1, 0]],
        [[0, 1], [1, 1], [0, 1]],
        [[0, 1, 0], [1, 1, 1]],
        [[1, 0], [1, 1], [1, 0]],
    ],
    # L
    [
        [[1, 0], [1, 0], [1, 1]],
        [[1, 1, 1], [1, 0, 0]],
        [[1, 1], [0, 1], [0, 1]],
        [[0, 0, 1], [1, 1, 1]],
    ],
    # J
    [
        [[0, 1], [0, 1], [1, 1]],
        [[1, 0, 0], [1, 1, 1]],
        [[1, 1], [1, 0], [1, 0]],
        [[1, 1, 1], [0, 0, 1]],
    ],
    # S
    [
        [[0, 1, 1], [1, 1, 0]],
        [[1, 0], [1, 1], [0, 1]],
    ],
    # Z
    [
        [[1, 1, 0], [0, 1, 1]],
        [[0, 1], [1, 1], [1, 0]],
    ],
    # I
    [
        [[1, 1, 1, 1]],
        [[1], [1], [1], [1]],
    ],
    # O
    [
        [[1, 1], [1, 1]],
    ],
]

COLORS = [
    (255, 0, 255),  # T
    (255, 165, 0),  # L
    (0, 0, 255),  # J
    (0, 255, 0),  # S
    (255, 0, 0),  # Z
    (0, 255, 255),  # I
    (255, 255, 0),  # O
]
