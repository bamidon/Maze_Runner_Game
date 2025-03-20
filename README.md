# Maze Runner Game

A challenging maze navigation game with enemies, traps, and multiple levels of difficulty.

## Table of Contents
- [Game Overview](#game-overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Option 1: Running from Source](#option-1-running-from-source)
  - [Option 2: Running the Executable](#option-2-running-the-executable)
- [How to Play](#how-to-play)
  - [Controls](#controls)
  - [Game Elements](#game-elements)
  - [Enemies and Traps](#enemies-and-traps)
- [Troubleshooting](#troubleshooting)
- [Credits](#credits)

## Game Overview

Maze Runner is a challenging maze navigation game where you must find your way through increasingly complex mazes while avoiding enemies and traps. The game features multiple difficulty levels, each with unique challenges including patrolling enemies, activating traps, keys and locked doors, and multi-floor mazes.

## Features

- Procedurally generated mazes that are different every time you play
- 10 difficulty levels with progressive challenges
- Enemies that patrol the maze with increasing speed in higher levels
- Traps that activate periodically
- Keys and locked doors
- Multi-floor mazes in higher difficulties
- Minimap to help with navigation
- Sound effects and background music
- Lighting effects that limit visibility
- Score tracking and high scores

## Requirements

- Python 3.7 or higher (if running from source)
- Pygame library (if running from source)
- NumPy library (if running from source)
- Windows, macOS, or Linux operating system

## Installation

### Option 1: Running from Source

If you want to run the game from source code, follow these steps:

1. **Install Python**:
   - Download and install Python 3.7 or higher from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation (Windows)

2. **Download the Game**:
   - Download the game source code zip file
   - Extract the zip file to a folder of your choice

3. **Install Required Libraries**:
   - Open a command prompt or terminal
   - Navigate to the game folder:
     ```
     cd path/to/maze_runner
     ```
   - Install the required libraries:
     ```
     pip install pygame numpy
     ```

4. **Run the Game**:
   - In the command prompt or terminal, run:
     ```
     python main.py
     ```

### Option 2: Running the Executable

If you're using the pre-built executable version:

1. **Download the Game**:
   - Download the game executable zip file
   - Extract the zip file to a folder of your choice

2. **Run the Game**:
   - Navigate to the extracted folder
   - Double-click on `maze_runner.exe` (Windows) or `maze_runner` (macOS/Linux)

## How to Play

### Controls

- **Arrow Keys**: Move the player character
- **Space**: Stop movement immediately
- **M**: Toggle minimap visibility
- **X**: Toggle sound on/off
- **P**: Pause/unpause the game
- **R**: Restart the current level
- **ESC**: Return to level select screen
- **1-9**: Quick select difficulty level

### Game Elements

- **Player (Blue Square)**: Your character
- **Exit (Green Square)**: Reach this to complete the level
- **Keys (Gold Squares)**: Collect these to unlock doors
- **Doors (Brown/Red Squares)**: Require keys to pass through
- **Stairs (Purple Squares)**: Move to the next floor in multi-level mazes
- **Walls (Gray Squares)**: Obstacles that cannot be passed through

### Enemies and Traps

- **Enemies (Red Squares)**: Patrol the maze in random patterns. If they touch you, you lose the game.
- **Traps (Gray Squares with Spikes)**:
  - Gray: Inactive and safe to pass
  - Orange: About to activate (warning)
  - Red: Active and dangerous

## Troubleshooting

### Game Won't Start

- **If running from source**:
  - Make sure Python is installed correctly
  - Verify that Pygame and NumPy are installed
  - Check that you're running the command from the correct directory

- **If running the executable**:
  - Make sure all files were extracted from the zip
  - Try running as administrator (Windows)
  - Check if your antivirus is blocking the executable

### No Sound

- Make sure your computer's sound is not muted
- Check that the sound is not muted in-game (press X to toggle)
- Verify that the assets folder contains all sound files

### Game Performance Issues

- Try reducing your screen resolution
- Close other applications running in the background
- If running from source, make sure you have the latest version of Pygame

## Credits

- Game developed by [Your Name]
- Sound effects from [Source]
- Special thanks to [Anyone you want to thank]

---

If you encounter any issues not covered in this README, please contact [your contact information]. 