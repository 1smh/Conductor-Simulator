from ursina import * 

# Title text
title_text = Text(
    "ONE-ARMED BAND",
    scale=3,
    origin=(0, 0),
    color=color.white
)

# Subtitle
subtitle_text = Text(
    "Sacrifices Must Be Made",
    scale=1.5,
    origin=(0, 0),
    y=-0.5,
    color=color.light_gray
)

# Start button
start_button = Button(
    text="Start Concert",
    scale=(0.3, 0.1),
    origin=(0, 0),
    y=0.4,
    color=color.green,
    highlight_color=color.lime
)

# Instructions
instructions = Text(
    "SPACE: Synchronize the orchestra\nQ: Remove bad musicians\nRight Mouse: Look around\nWASD: Move conductor",
    scale=1,
    origin=(0, 0),
    y=-2,
    color=color.gray,
    multiline=True
)

# Handle button click
start_button.on_click = start_game()

def start_game():
    """Start the main game"""
    # Hide title screen
    title_text.disable()
    subtitle_text.disable()
    start_button.disable()
    instructions.disable()
    