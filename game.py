import pygame
import sys
import time
import os
import math
import random
from maze_generator import MazeGenerator
from player import Player
from enemy import Enemy
from trap import Trap
from theme import Theme
from level_manager import LevelManager
from sound_manager import SoundManager

class MazeGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Get screen info to ensure maze fits
        screen_info = pygame.display.Info()
        self.max_screen_width = screen_info.current_w
        self.max_screen_height = screen_info.current_h
        
        # Initialize managers
        self.level_manager = LevelManager()
        self.sound_manager = SoundManager()
        
        # Game state
        self.game_active = False
        self.game_paused = False
        self.game_over = False
        self.level_complete = False
        self.show_minimap = True
        self.current_floor = 1
        self.total_floors = 1
        self.keys_collected = 0
        self.keys_required = 0
        self.time_limit = 0
        self.start_time = 0
        self.elapsed_time = 0
        self.score = 0
        
        # Screen settings
        self.info_panel_height = 100
        self.minimap_size = 150
        
        # Game objects
        self.player = None
        self.enemies = []
        self.traps = []
        
        # Theme
        self.theme = Theme("dungeon")
        
        # Light surface for lighting effects
        self.light_surface = None
        
        # Game screens
        self.current_screen = "menu"  # menu, level_select, game, game_over, victory
        
        # Sound settings
        self.sound_muted = False
        
        # Initialize the menu
        self.init_menu()
        
    def init_menu(self):
        # Set up the main menu
        self.current_screen = "menu"
        
        # Calculate screen dimensions for menu
        screen_width = min(800, self.max_screen_width)
        screen_height = min(600, self.max_screen_height)
        
        # Initialize screen
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Maze Runner")
        
        # Play menu music
        self.sound_manager.play_menu_music()
        
    def init_level_select(self):
        # Set up the level selection screen
        self.current_screen = "level_select"
        
        # Calculate screen dimensions for level select
        screen_width = min(800, self.max_screen_width)
        screen_height = min(600, self.max_screen_height)
        
        # Initialize screen
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Maze Runner - Level Select")
        
    def init_game(self, level_num=None):
        # Set the current level if provided
        if level_num is not None:
            self.level_manager.set_level(level_num)
        
        # Get the level configuration
        level_config = self.level_manager.get_level_config(level_num)
        
        # Set theme based on level
        self.theme = Theme(level_config["theme"])
        
        # Set level parameters
        maze_width, maze_height = level_config["size"]
        self.keys_required = level_config["keys_required"]
        self.time_limit = level_config["time_limit"]
        self.total_floors = level_config["floors"]
        self.current_floor = 1
        
        # Calculate appropriate cell size to fit screen
        max_cell_width = (self.max_screen_width - 40) // maze_width  # 40px margin
        max_cell_height = (self.max_screen_height - self.info_panel_height - 40) // maze_height  # 40px margin
        self.cell_size = min(max_cell_width, max_cell_height, 20)  # Cap at 20px for smaller cells
        
        # Ensure minimum cell size
        self.cell_size = max(self.cell_size, 8)  # Reduced minimum size
        
        # Calculate screen dimensions
        screen_width = max(maze_width * self.cell_size + 40, 800)  # Add margin and ensure minimum width
        screen_height = maze_height * self.cell_size + self.info_panel_height + 20  # Add margin
        
        # Ensure screen fits within display
        screen_width = min(screen_width, self.max_screen_width)
        screen_height = min(screen_height, self.max_screen_height)
        
        # Initialize screen
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption(f"Maze Runner - Level {self.level_manager.current_level}")
        
        # Generate the maze
        maze_generator = MazeGenerator(maze_width, maze_height)
        self.maze_generator = maze_generator  # Store reference to maze generator
        
        maze_result = maze_generator.generate_maze(
            keys_required=level_config.get("keys_required", 0),
            num_enemies=level_config.get("enemies", 0),
            num_traps=level_config.get("traps", 0),
            num_floors=level_config.get("num_floors", 1),
            current_floor=1,
            complexity=level_config.get("complexity", 0.75),
            density=level_config.get("density", 0.75),
            min_exit_distance=level_config.get("min_exit_distance", None)
        )
        
        # Unpack the result properly
        self.maze, self.start_pos, self.exit_pos = maze_result
        
        # Initialize player
        start_x, start_y = self.start_pos
        self.player = Player(start_x, start_y, self.cell_size)
        
        # Initialize enemies
        self.enemies = []
        enemy_speed = level_config.get("enemy_speed", 0.5)  # Default speed if not specified
        for enemy_pos in maze_generator.get_enemy_positions():
            self.enemies.append(Enemy(
                enemy_pos[0], 
                enemy_pos[1], 
                self.cell_size, 
                self.maze,
                speed=enemy_speed
            ))
        
        # Initialize traps
        self.traps = []
        trap_activation_time = level_config.get("trap_activation_time", 3.0)  # Default if not specified
        for trap_info in maze_generator.get_trap_positions():
            x, y, trap_type = trap_info
            self.traps.append(Trap(
                x, y, 
                self.cell_size, 
                trap_type,
                activation_time=trap_activation_time
            ))
        
        # Initialize key and door positions
        self.key_positions = maze_generator.get_key_positions()
        self.door_position = maze_generator.get_door_position()
        self.stair_positions = maze_generator.get_stair_positions()
        
        # Reset game state
        self.game_active = True
        self.game_paused = False
        self.game_over = False
        self.level_complete = False
        self.keys_collected = 0
        self.start_time = time.time()
        self.elapsed_time = 0
        self.score = 0
        
        # Adjust player speed based on cell size
        self.player.speed = max(2, self.cell_size // 6)
        
        # Create light surface for lighting effects
        self.create_light_surface()
        
        # Play theme music
        self.sound_manager.play_theme_music(self.theme.name)
        
        # Set current screen to game
        self.current_screen = "game"
    
    def create_light_surface(self):
        # Get the maze dimensions from the maze array
        maze_width, maze_height = self.maze.shape[1], self.maze.shape[0]
        
        # Create a surface for the lighting effect
        self.light_surface = pygame.Surface((maze_width * self.cell_size, maze_height * self.cell_size), pygame.SRCALPHA)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Global key handlers (work in any screen)
            if event.type == pygame.KEYDOWN:
                # Toggle sound mute with X key instead of M
                if event.key == pygame.K_x:
                    self.toggle_sound_mute()
            
            # Handle events based on current screen
            if self.current_screen == "menu":
                self.handle_menu_events(event)
            elif self.current_screen == "level_select":
                self.handle_level_select_events(event)
            elif self.current_screen == "game":
                self.handle_game_events(event)
            elif self.current_screen == "description":
                self.handle_description_events(event)
            
            # Handle game over screen events
            elif self.current_screen == "game_over":
                self.handle_game_over_events(event)
            
            # Handle victory screen events
            elif self.current_screen == "victory":
                self.handle_victory_events(event)
    
    def handle_menu_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Start the game with level 1
                self.sound_manager.play_sound("menu_click")
                self.init_level_select()
            elif event.key == pygame.K_h:
                # Show how to play screen
                self.sound_manager.play_sound("menu_click")
                self.current_screen = "description"
                # Reset scroll position when entering the screen
                self.description_scroll_y = 0
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if mute button was clicked
            if hasattr(self, 'mute_button_rect') and self.mute_button_rect.collidepoint(mouse_pos):
                self.toggle_sound_mute()
                return  # Don't process other buttons if mute was clicked
            
            # Check if buttons were clicked
            if hasattr(self, 'menu_buttons'):
                if self.menu_buttons["play"].collidepoint(mouse_pos):
                    self.sound_manager.play_sound("menu_click")
                    self.init_level_select()
                elif self.menu_buttons["how_to_play"].collidepoint(mouse_pos):
                    self.sound_manager.play_sound("menu_click")
                    self.current_screen = "description"
                    # Reset scroll position when entering the screen
                    self.description_scroll_y = 0
                elif self.menu_buttons["quit"].collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
    
    def handle_level_select_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.sound_manager.play_sound("menu_back")
                self.init_menu()
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                              pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0):
                # Convert key to level number
                level_num = event.key - pygame.K_0 if event.key != pygame.K_0 else 10
                
                # Check if level is unlocked
                if self.level_manager.is_level_unlocked(level_num):
                    self.sound_manager.play_sound("menu_click")
                    self.init_game(level_num)
            elif event.key == pygame.K_r:
                # Reset progress when R is pressed in level select
                self.reset_progress()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if mute button was clicked
            if hasattr(self, 'mute_button_rect') and self.mute_button_rect.collidepoint(mouse_pos):
                self.toggle_sound_mute()
                return  # Don't process other buttons if mute was clicked
            
            # Get level buttons
            font = pygame.font.SysFont("Arial", 24)
            level_buttons = self.level_manager.get_level_selection_surfaces(font)
            
            # Position buttons in a grid
            button_width, button_height = 200, 60
            grid_cols = 3
            start_x = (self.screen.get_width() - (grid_cols * button_width + (grid_cols - 1) * 20)) // 2
            start_y = 150
            
            for i, (button_surface, level) in enumerate(level_buttons):
                col = i % grid_cols
                row = i // grid_cols
                x = start_x + col * (button_width + 20)
                y = start_y + row * (button_height + 20)
                
                button_rect = pygame.Rect(x, y, button_width, button_height)
                if button_rect.collidepoint(mouse_pos) and self.level_manager.is_level_unlocked(level):
                    self.sound_manager.play_sound("menu_click")
                    self.init_game(level)
            
            # Back button
            back_rect = pygame.Rect(20, 20, 100, 40)
            if back_rect.collidepoint(mouse_pos):
                self.sound_manager.play_sound("menu_back")
                self.init_menu()
            
            # Reset progress button
            reset_rect = pygame.Rect(self.screen.get_width() - 120, 20, 100, 40)
            if reset_rect.collidepoint(mouse_pos):
                self.reset_progress()
    
    def handle_game_events(self, event):
        if event.type == pygame.KEYDOWN:
            if self.game_active and not self.game_paused:
                if event.key == pygame.K_UP:
                    # Stop any existing movement and start moving up
                    self.player.stop_continuous_movement()
                    if self.player.move(0, -1, self.maze):
                        # Play footstep sound only if not muted
                        if not self.sound_muted:
                            self.sound_manager.play_sound("move")
                elif event.key == pygame.K_DOWN:
                    # Stop any existing movement and start moving down
                    self.player.stop_continuous_movement()
                    if self.player.move(0, 1, self.maze):
                        # Play footstep sound only if not muted
                        if not self.sound_muted:
                            self.sound_manager.play_sound("move")
                elif event.key == pygame.K_LEFT:
                    # Stop any existing movement and start moving left
                    self.player.stop_continuous_movement()
                    if self.player.move(-1, 0, self.maze):
                        # Play footstep sound only if not muted
                        if not self.sound_muted:
                            self.sound_manager.play_sound("move")
                elif event.key == pygame.K_RIGHT:
                    # Stop any existing movement and start moving right
                    self.player.stop_continuous_movement()
                    if self.player.move(1, 0, self.maze):
                        # Play footstep sound only if not muted
                        if not self.sound_muted:
                            self.sound_manager.play_sound("move")
                elif event.key == pygame.K_SPACE:
                    # Stop continuous movement when space is pressed
                    self.player.stop_continuous_movement()
            
            if event.key == pygame.K_p:
                # Toggle pause
                self.game_paused = not self.game_paused
            
            if event.key == pygame.K_r:
                # Restart the current level
                self.init_game(self.level_manager.current_level)
            
            if event.key == pygame.K_m:
                # Toggle minimap
                self.show_minimap = not self.show_minimap
            
            if event.key == pygame.K_ESCAPE:
                # Return to level select
                self.sound_manager.play_sound("menu_back")
                self.init_level_select()
        
        # Handle key releases to stop continuous movement
        elif event.type == pygame.KEYUP:
            if self.game_active and not self.game_paused:
                if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    # Check if the released key matches the current movement direction
                    if (event.key == pygame.K_UP and self.player.continuous_dy == -1) or \
                       (event.key == pygame.K_DOWN and self.player.continuous_dy == 1) or \
                       (event.key == pygame.K_LEFT and self.player.continuous_dx == -1) or \
                       (event.key == pygame.K_RIGHT and self.player.continuous_dx == 1):
                        self.player.stop_continuous_movement()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if mute button was clicked
            if hasattr(self, 'mute_button_rect') and self.mute_button_rect.collidepoint(mouse_pos):
                self.toggle_sound_mute()
                return  # Don't process other game actions if mute was clicked
            
            # ... rest of game click handling ...
    
    def handle_game_over_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Restart the current level
                self.init_game(self.level_manager.current_level)
            elif event.key == pygame.K_ESCAPE:
                # Return to level select
                self.sound_manager.play_sound("menu_back")
                self.init_level_select()
    
    def handle_victory_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                # Go to next level if available
                if self.level_manager.next_level():
                    self.init_game()
                else:
                    # Return to level select if no more levels
                    self.init_level_select()
            elif event.key == pygame.K_r:
                # Replay the current level
                self.init_game(self.level_manager.current_level)
            elif event.key == pygame.K_ESCAPE:
                # Return to level select
                self.sound_manager.play_sound("menu_back")
                self.init_level_select()
    
    def update(self, delta_time):
        if self.current_screen == "game" and self.game_active and not self.game_paused:
            # Update player
            player_moved = self.player.update()
            
            # Play footstep sound if player moved to a new cell and sound is not muted
            if player_moved and not self.sound_muted:
                self.sound_manager.play_sound("move")
            
            # Continue movement if player is not currently moving
            if not self.player.moving:
                if self.player.continue_movement(self.maze):
                    # Only play sound when actually moving to a new cell and sound is not muted
                    if not self.sound_muted:
                        self.sound_manager.play_sound("move")
            
            # Update enemies
            for enemy in self.enemies:
                enemy.update(delta_time)
                
                # Check for collision with player
                if self.player.get_rect().colliderect(enemy.get_rect()):
                    self.game_over = True
                    self.game_active = False
                    self.sound_manager.play_sound("enemy_attack")
                    self.sound_manager.play_sound("game_over")
                    self.current_screen = "game_over"
            
            # Update traps
            for trap in self.traps:
                trap.update(delta_time)
                
                # Check for collision with active trap
                if trap.is_dangerous() and self.player.get_position() == (trap.x, trap.y):
                    self.game_over = True
                    self.game_active = False
                    self.sound_manager.play_sound("trap_activate")
                    self.sound_manager.play_sound("game_over")
                    self.current_screen = "game_over"
            
            # Check for key collection
            player_pos = self.player.get_position()
            if player_pos in self.key_positions:
                self.key_positions.remove(player_pos)
                self.keys_collected += 1
                self.sound_manager.play_sound("key_pickup")
            
            # Check if player reached stairs
            if player_pos in self.stair_positions and self.current_floor < self.total_floors:
                self.current_floor += 1
                self.sound_manager.play_sound("stairs")
                
                # Generate new floor
                level_config = self.level_manager.get_level_config()
                maze_width, maze_height = level_config["size"]
                
                self.maze_generator = MazeGenerator(maze_width, maze_height)
                self.maze = self.maze_generator.generate_maze(
                    keys_required=self.keys_required if self.current_floor == 1 else 0,
                    num_enemies=level_config["enemies"] // self.total_floors,
                    num_traps=level_config["traps"] // self.total_floors,
                    num_floors=self.total_floors,
                    current_floor=self.current_floor
                )
                
                # Reset player position
                start_x, start_y = self.maze_generator.get_start_position()
                self.player.reset(start_x, start_y)
                
                # Update game objects for new floor
                self.exit_pos = self.maze_generator.get_exit_position()
                
                # Initialize enemies
                self.enemies = []
                enemy_speed = level_config.get("enemy_speed", 0.5)  # Default speed if not specified
                for enemy_pos in self.maze_generator.get_enemy_positions():
                    self.enemies.append(Enemy(
                        enemy_pos[0], 
                        enemy_pos[1], 
                        self.cell_size, 
                        self.maze,
                        speed=enemy_speed
                    ))
                
                # Initialize traps
                self.traps = []
                trap_activation_time = level_config.get("trap_activation_time", 3.0)  # Default if not specified
                for trap_info in self.maze_generator.get_trap_positions():
                    x, y, trap_type = trap_info
                    self.traps.append(Trap(
                        x, y, 
                        self.cell_size, 
                        trap_type,
                        activation_time=trap_activation_time
                    ))
                
                # Update key and door positions
                self.key_positions = self.maze_generator.get_key_positions()
                self.door_position = self.maze_generator.get_door_position()
                self.stair_positions = self.maze_generator.get_stair_positions()
                
                # Create new light surface
                self.create_light_surface()
            
            # Check if player reached the exit
            if player_pos == self.exit_pos:
                # Check if door is locked and player has enough keys
                if self.door_position == player_pos and self.keys_collected < self.keys_required:
                    # Door is locked
                    self.sound_manager.play_sound("door_unlock")
                else:
                    # Level complete
                    self.game_active = False
                    self.level_complete = True
                    self.elapsed_time = time.time() - self.start_time
                    self.calculate_score()
                    
                    # Unlock next level if this is the highest level completed
                    if self.level_manager.current_level == self.level_manager.levels_unlocked:
                        self.level_manager.unlock_next_level()
                    
                    # Update high score
                    self.level_manager.update_high_score(self.level_manager.current_level, self.score)
                    
                    # Play victory sounds
                    self.sound_manager.play_sound("victory")
                    self.sound_manager.play_victory_music()
                    
                    # Set screen to victory
                    self.current_screen = "victory"
            
            # Check time limit if set
            if self.time_limit > 0:
                current_time = time.time() - self.start_time
                if current_time >= self.time_limit:
                    self.game_over = True
                    self.game_active = False
                    self.sound_manager.play_sound("game_over")
                    
                    # Set screen to game over
                    self.current_screen = "game_over"
            
            # Adjust music based on proximity to exit or enemies
            self.update_music_by_proximity()
    
    def update_music_by_proximity(self):
        # Check proximity to exit
        player_pos = self.player.get_position()
        exit_pos = self.exit_pos
        
        # Calculate Manhattan distance to exit
        exit_distance = abs(player_pos[0] - exit_pos[0]) + abs(player_pos[1] - exit_pos[1])
        
        # Check proximity to enemies
        enemy_distance = float('inf')
        for enemy in self.enemies:
            enemy_pos = enemy.get_position()
            dist = abs(player_pos[0] - enemy_pos[0]) + abs(player_pos[1] - enemy_pos[1])
            enemy_distance = min(enemy_distance, dist)
        
        # Determine which proximity to use for music adjustment
        proximity_distance = min(exit_distance, enemy_distance)
        max_distance = 10  # Maximum distance to consider for music adjustment
        
        # Adjust music based on proximity
        if proximity_distance < max_distance:
            self.sound_manager.adjust_music_by_distance(proximity_distance, max_distance)
    
    def calculate_score(self):
        # Get level configuration
        level_config = self.level_manager.get_level_config()
        
        # Base score factors - use a default value if time_bonus is not present
        time_bonus = level_config.get("time_bonus", 100)  # Default to 100 if missing
        steps_penalty = self.player.get_steps_taken() // 2
        
        # Time factor
        if self.time_limit > 0:
            time_factor = 1.0 - (self.elapsed_time / self.time_limit)
        else:
            time_factor = max(0, 1.0 - (self.elapsed_time / 300))  # Assume 5 minutes is par
        
        # Calculate score
        self.score = int(time_bonus * time_factor) - steps_penalty
        
        # Bonus for keys collected
        self.score += self.keys_collected * 50
        
        # Bonus for completing multiple floors
        self.score += (self.current_floor - 1) * 100
        
        # Ensure minimum score of 10
        self.score = max(10, self.score)
    
    def draw(self):
        if self.current_screen == "menu":
            self.draw_menu()
        elif self.current_screen == "level_select":
            self.draw_level_select()
        elif self.current_screen == "game":
            self.draw_game()
        elif self.current_screen == "game_over":
            self.draw_game_over()
        elif self.current_screen == "victory":
            self.draw_victory()
        elif self.current_screen == "description":
            self.draw_game_description()
        
        pygame.display.flip()
    
    def draw_menu(self):
        # Draw background
        self.screen.fill((20, 20, 30))
        
        # Draw title
        font_title = pygame.font.SysFont("Arial", 48)
        title_text = font_title.render("MAZE RUNNER", True, (255, 255, 255))
        self.screen.blit(title_text, (self.screen.get_width() // 2 - title_text.get_width() // 2, 100))
        
        # Draw buttons
        font_button = pygame.font.SysFont("Arial", 32)
        
        # Play button
        play_rect = pygame.Rect(300, 220, 200, 50)
        pygame.draw.rect(self.screen, (50, 120, 50), play_rect)
        play_text = font_button.render("PLAY", True, (255, 255, 255))
        self.screen.blit(play_text, (play_rect.centerx - play_text.get_width() // 2, play_rect.centery - play_text.get_height() // 2))
        
        # How to Play button
        how_to_play_rect = pygame.Rect(300, 290, 200, 50)
        pygame.draw.rect(self.screen, (50, 50, 120), how_to_play_rect)
        how_to_play_text = font_button.render("HOW TO PLAY", True, (255, 255, 255))
        self.screen.blit(how_to_play_text, (how_to_play_rect.centerx - how_to_play_text.get_width() // 2, how_to_play_rect.centery - how_to_play_text.get_height() // 2))
        
        # Quit button
        quit_rect = pygame.Rect(300, 360, 200, 50)
        pygame.draw.rect(self.screen, (120, 50, 50), quit_rect)
        quit_text = font_button.render("QUIT", True, (255, 255, 255))
        self.screen.blit(quit_text, (quit_rect.centerx - quit_text.get_width() // 2, quit_rect.centery - quit_text.get_height() // 2))
        
        # Draw instructions
        font_instructions = pygame.font.SysFont("Arial", 18)
        instructions_text = font_instructions.render("Press ENTER to start or click PLAY", True, (200, 200, 200))
        self.screen.blit(instructions_text, (self.screen.get_width() // 2 - instructions_text.get_width() // 2, 430))
        
        # Store button rects for click detection
        self.menu_buttons = {
            "play": play_rect,
            "how_to_play": how_to_play_rect,
            "quit": quit_rect
        }
        
        # Draw mute button
        self.mute_button_rect = self.draw_mute_button()
    
    def draw_level_select(self):
        # Draw background
        self.screen.fill((30, 30, 40))
        
        # Draw title
        font_title = pygame.font.SysFont("Arial", 36)
        title_text = font_title.render("SELECT LEVEL", True, (255, 255, 255))
        self.screen.blit(title_text, (self.screen.get_width() // 2 - title_text.get_width() // 2, 50))
        
        # Draw level buttons
        font = pygame.font.SysFont("Arial", 24)
        level_buttons = self.level_manager.get_level_selection_surfaces(font)
        
        # Position buttons in a grid
        button_width, button_height = 200, 60
        grid_cols = 3
        start_x = (self.screen.get_width() - (grid_cols * button_width + (grid_cols - 1) * 20)) // 2
        start_y = 150
        
        for i, (button_surface, level) in enumerate(level_buttons):
            col = i % grid_cols
            row = i // grid_cols
            x = start_x + col * (button_width + 20)
            y = start_y + row * (button_height + 20)
            
            self.screen.blit(button_surface, (x, y))
        
        # Draw back button
        back_rect = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(self.screen, (100, 100, 100), back_rect)
        back_text = font.render("BACK", True, (255, 255, 255))
        self.screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, back_rect.centery - back_text.get_height() // 2))
        
        # Draw reset progress button
        reset_rect = pygame.Rect(self.screen.get_width() - 120, 20, 100, 40)
        pygame.draw.rect(self.screen, (150, 50, 50), reset_rect)
        reset_text = font.render("RESET", True, (255, 255, 255))
        self.screen.blit(reset_text, (reset_rect.centerx - reset_text.get_width() // 2, reset_rect.centery - reset_text.get_height() // 2))
        
        # Draw instructions
        font_instructions = pygame.font.SysFont("Arial", 18)
        instructions_text = font_instructions.render("Press 1-9 to select a level or click on a level", True, (200, 200, 200))
        self.screen.blit(instructions_text, (self.screen.get_width() // 2 - instructions_text.get_width() // 2, 500))
        
        reset_instructions = font_instructions.render("Press R to reset all progress", True, (200, 150, 150))
        self.screen.blit(reset_instructions, (self.screen.get_width() // 2 - reset_instructions.get_width() // 2, 530))
        
        # Draw mute button
        self.mute_button_rect = self.draw_mute_button()
    
    def draw_game(self):
        self.screen.fill((0, 0, 0))
        
        # Draw maze with lighting effects
        self.draw_maze_with_lighting()
        
        # Draw game objects
        self.draw_game_objects()
        
        # Draw info panel (which now includes the mute button)
        self.draw_info_panel()
        
        # Draw minimap if enabled
        if self.show_minimap:
            self.draw_minimap()
        
        # Draw pause overlay if paused
        if self.game_paused:
            self.draw_pause_overlay()
            # Draw mute button again on top of pause overlay
            self.mute_button_rect = self.draw_mute_button()
    
    def draw_maze_with_lighting(self):
        # Clear the light surface
        self.light_surface.fill((0, 0, 0, 255))
        
        # Get player position
        player_x, player_y = self.player.get_position()
        
        # Get light radius in cells
        light_radius = self.theme.get_light_radius()
        
        # Get ambient light level (0-1)
        ambient_light = self.theme.get_ambient_light()
        
        # Draw light around player
        light_gradient = self.theme.get_light_gradient()
        light_size = light_gradient.get_width()
        light_pos = (
            player_x * self.cell_size + self.cell_size // 2 - light_size // 2,
            player_y * self.cell_size + self.cell_size // 2 - light_size // 2
        )
        
        # Draw the light gradient at player position
        self.light_surface.blit(light_gradient, light_pos)
        
        # Draw the maze
        for y in range(self.maze.shape[0]):
            for x in range(self.maze.shape[1]):
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                
                # Calculate distance from player for ambient light
                distance = max(abs(x - player_x), abs(y - player_y))
                
                # Determine cell visibility
                if distance <= light_radius:
                    # Cell is in light radius
                    visibility = 1.0
                else:
                    # Cell is in ambient light
                    visibility = ambient_light
                
                if self.maze[y][x] == 1:  # Wall
                    pygame.draw.rect(self.screen, (50, 50, 50), rect)
                else:  # Path
                    pygame.draw.rect(self.screen, (200, 200, 200), rect)
                    pygame.draw.rect(self.screen, (150, 150, 150), rect, 1)
        
        # Draw exit
        exit_x, exit_y = self.exit_pos
        exit_rect = pygame.Rect(
            exit_x * self.cell_size,
            exit_y * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        pygame.draw.rect(self.screen, (0, 255, 0), exit_rect)  # Green exit
    
    def draw_info_panel(self):
        panel_rect = pygame.Rect(
            0,
            self.maze.shape[0] * self.cell_size,
            self.screen.get_width(),
            self.info_panel_height
        )
        pygame.draw.rect(self.screen, (30, 30, 30), panel_rect)
        
        # Scale font size based on panel height
        font_size = max(14, min(24, self.info_panel_height // 5))
        small_font_size = max(10, min(18, self.info_panel_height // 6))
        
        # Create fonts with appropriate sizes
        font = pygame.font.SysFont("Arial", font_size)
        small_font = pygame.font.SysFont("Arial", small_font_size)
        
        # Calculate the right boundary for text to avoid overlapping with minimap
        # Reserve space for minimap (plus margin)
        minimap_size = min(self.info_panel_height - 20, int(self.screen.get_width() * 0.15))
        right_boundary = self.screen.get_width() - minimap_size - 40  # 40px extra margin
        
        # Display time
        if self.game_active:
            current_time = time.time() - self.start_time
        else:
            current_time = self.elapsed_time
        
        time_text = font.render(f"Time: {current_time:.1f}s", True, (255, 255, 255))
        self.screen.blit(time_text, (20, panel_rect.y + 10))
        
        # Display steps
        steps_text = font.render(f"Steps: {self.player.get_steps_taken()}", True, (255, 255, 255))
        self.screen.blit(steps_text, (20, panel_rect.y + 10 + font_size + 5))
        
        # Calculate position for difficulty text
        diff_x = min(200, self.screen.get_width() // 3)
        diff_text = font.render(f"Difficulty: {self.level_manager.current_level}", True, (255, 255, 255))
        self.screen.blit(diff_text, (diff_x, panel_rect.y + 10))
        
        # Display controls - ensure they don't extend past the right boundary
        controls_text = small_font.render("Controls: Arrow Keys to move, SPACE to stop, R to restart, M for minimap", True, (200, 200, 200))
        # Truncate text if it would extend past the right boundary
        if diff_x + controls_text.get_width() > right_boundary:
            controls_text = small_font.render("Controls: Arrows to move, SPACE to stop, R to restart", True, (200, 200, 200))
        self.screen.blit(controls_text, (diff_x, panel_rect.y + 10 + font_size + 5))
        
        diff_controls_text = small_font.render("Press 1-9 to change difficulty", True, (200, 200, 200))
        self.screen.blit(diff_controls_text, (diff_x, panel_rect.y + 10 + font_size + 5 + small_font_size + 2))
        
        # Draw mute button under the control description
        button_size = 24
        button_x = diff_x
        button_y = panel_rect.y + 10 + font_size + 5 + small_font_size + 2 + small_font_size + 5
        
        # Draw button background
        button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
        pygame.draw.rect(self.screen, (60, 60, 60), button_rect)
        pygame.draw.rect(self.screen, (120, 120, 120), button_rect, 1)  # Add border
        
        # Draw icon based on mute state
        if self.sound_muted:
            # Draw muted icon (speaker with X)
            pygame.draw.polygon(self.screen, (200, 200, 200), [
                (button_x + 6, button_y + 12),  # Left
                (button_x + 10, button_y + 8),  # Top
                (button_x + 10, button_y + 16)   # Bottom
            ])
            pygame.draw.rect(self.screen, (200, 200, 200), 
                            pygame.Rect(button_x + 6, button_y + 10, 4, 4))
            
            # Draw X
            pygame.draw.line(self.screen, (255, 100, 100), 
                            (button_x + 12, button_y + 8), 
                            (button_x + 18, button_y + 16), 2)
            pygame.draw.line(self.screen, (255, 100, 100), 
                            (button_x + 18, button_y + 8), 
                            (button_x + 12, button_y + 16), 2)
        else:
            # Draw unmuted icon (speaker with waves)
            pygame.draw.polygon(self.screen, (200, 200, 200), [
                (button_x + 6, button_y + 12),  # Left
                (button_x + 10, button_y + 8),  # Top
                (button_x + 10, button_y + 16)   # Bottom
            ])
            pygame.draw.rect(self.screen, (200, 200, 200), 
                            pygame.Rect(button_x + 6, button_y + 10, 4, 4))
            
            # Draw sound waves
            pygame.draw.arc(self.screen, (200, 200, 200), 
                            pygame.Rect(button_x + 10, button_y + 6, 5, 12), 
                            -0.5, 0.5, 1)
            pygame.draw.arc(self.screen, (200, 200, 200), 
                            pygame.Rect(button_x + 13, button_y + 4, 8, 16), 
                            -0.5, 0.5, 1)
        
        # Add "SOUND" label next to the button - ensure it doesn't extend past the right boundary
        sound_text = small_font.render("SOUND (X)", True, (200, 200, 200))
        self.screen.blit(sound_text, (button_x + button_size + 5, button_y + button_size//2 - sound_text.get_height()//2))
        
        # Store the mute button rect for click detection
        self.mute_button_rect = button_rect
        
        # Display score if game is over
        if not self.game_active:
            score_x = min(400, self.screen.get_width() // 2 + 50)
            # Ensure score text doesn't overlap with minimap
            if score_x + 200 > right_boundary:  # Approximate width of score text
                score_x = right_boundary - 200
            
            score_text = font.render(f"Score: {self.score}", True, (255, 255, 0))
            self.screen.blit(score_text, (score_x, panel_rect.y + 10))
            
            win_text = font.render("Maze Completed! Press R to play again", True, (255, 255, 0))
            self.screen.blit(win_text, (score_x, panel_rect.y + 10 + font_size + 5))
    
    def draw_minimap(self):
        # Calculate minimap size to fit within the info panel
        panel_height = self.info_panel_height
        minimap_size = min(panel_height - 20, int(self.screen.get_width() * 0.15))
        
        # Calculate minimap position - place it in the right side of the info panel
        # Move it further to the right to avoid overlapping with text
        minimap_rect = pygame.Rect(
            self.screen.get_width() - minimap_size - 20,  # 20px margin from right edge
            self.maze.shape[0] * self.cell_size + (panel_height - minimap_size) // 2,
            minimap_size,
            minimap_size
        )
        
        # Draw minimap background
        pygame.draw.rect(self.screen, (10, 10, 10), minimap_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), minimap_rect, 1)  # Add border
        
        # Calculate cell size for minimap
        maze_width, maze_height = self.maze.shape[1], self.maze.shape[0]
        cell_width = minimap_rect.width / maze_width
        cell_height = minimap_rect.height / maze_height
        
        # Draw explored areas and walls
        for y in range(maze_height):
            for x in range(maze_width):
                mini_rect = pygame.Rect(
                    minimap_rect.x + x * cell_width,
                    minimap_rect.y + y * cell_height,
                    max(1, cell_width),  # Ensure minimum size of 1 pixel
                    max(1, cell_height)  # Ensure minimum size of 1 pixel
                )
                
                # Only draw cells that have been visited or are adjacent to visited cells
                is_adjacent = False
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    if (x + dx, y + dy) in self.player.visited_cells:
                        is_adjacent = True
                        break
                
                if (x, y) in self.player.visited_cells or is_adjacent:
                    if self.maze[y][x] == 1:  # Wall
                        pygame.draw.rect(self.screen, (100, 100, 100), mini_rect)
                    else:  # Path
                        pygame.draw.rect(self.screen, (180, 180, 180), mini_rect)
        
        # Draw player on minimap
        player_x, player_y = self.player.get_position()
        player_rect = pygame.Rect(
            minimap_rect.x + player_x * cell_width,
            minimap_rect.y + player_y * cell_height,
            max(2, cell_width),  # Ensure player is visible
            max(2, cell_height)  # Ensure player is visible
        )
        pygame.draw.rect(self.screen, (0, 0, 255), player_rect)  # Blue player
        
        # Draw exit on minimap
        exit_x, exit_y = self.exit_pos
        exit_rect = pygame.Rect(
            minimap_rect.x + exit_x * cell_width,
            minimap_rect.y + exit_y * cell_height,
            max(2, cell_width),  # Ensure exit is visible
            max(2, cell_height)  # Ensure exit is visible
        )
        pygame.draw.rect(self.screen, (0, 255, 0), exit_rect)  # Green exit
        
        # Add "MAP" label above minimap
        font = pygame.font.SysFont("Arial", 12)
        map_text = font.render("MAP (M)", True, (200, 200, 200))
        self.screen.blit(map_text, (minimap_rect.centerx - map_text.get_width() // 2, minimap_rect.y - 15))
    
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        font_title = pygame.font.SysFont("Arial", 48)
        title_text = font_title.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(title_text, (self.screen.get_width() // 2 - title_text.get_width() // 2, 200))
        
        # Instructions
        font_instructions = pygame.font.SysFont("Arial", 24)
        restart_text = font_instructions.render("Press R to restart level", True, (255, 255, 255))
        self.screen.blit(restart_text, (self.screen.get_width() // 2 - restart_text.get_width() // 2, 280))
        
        menu_text = font_instructions.render("Press ESC to return to level select", True, (255, 255, 255))
        self.screen.blit(menu_text, (self.screen.get_width() // 2 - menu_text.get_width() // 2, 320))
    
    def draw_victory(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Victory text
        font_title = pygame.font.SysFont("Arial", 48)
        title_text = font_title.render("LEVEL COMPLETE!", True, (0, 255, 0))
        self.screen.blit(title_text, (self.screen.get_width() // 2 - title_text.get_width() // 2, 180))
        
        # Score
        font_score = pygame.font.SysFont("Arial", 36)
        score_text = font_score.render(f"Score: {self.score}", True, (255, 255, 0))
        self.screen.blit(score_text, (self.screen.get_width() // 2 - score_text.get_width() // 2, 250))
        
        # Time and steps
        font_stats = pygame.font.SysFont("Arial", 24)
        time_text = font_stats.render(f"Time: {self.elapsed_time:.1f}s", True, (255, 255, 255))
        self.screen.blit(time_text, (self.screen.get_width() // 2 - time_text.get_width() // 2, 300))
        
        steps_text = font_stats.render(f"Steps: {self.player.get_steps_taken()}", True, (255, 255, 255))
        self.screen.blit(steps_text, (self.screen.get_width() // 2 - steps_text.get_width() // 2, 330))
        
        # Instructions
        font_instructions = pygame.font.SysFont("Arial", 24)
        next_text = font_instructions.render("Press N for next level", True, (255, 255, 255))
        self.screen.blit(next_text, (self.screen.get_width() // 2 - next_text.get_width() // 2, 380))
        
        restart_text = font_instructions.render("Press R to replay level", True, (255, 255, 255))
        self.screen.blit(restart_text, (self.screen.get_width() // 2 - restart_text.get_width() // 2, 410))
        
        menu_text = font_instructions.render("Press ESC to return to level select", True, (255, 255, 255))
        self.screen.blit(menu_text, (self.screen.get_width() // 2 - menu_text.get_width() // 2, 440))
    
    def draw_pause_overlay(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        font_title = pygame.font.SysFont("Arial", 48)
        title_text = font_title.render("PAUSED", True, (255, 255, 255))
        self.screen.blit(title_text, (self.screen.get_width() // 2 - title_text.get_width() // 2, 200))
        
        # Instructions
        font_instructions = pygame.font.SysFont("Arial", 24)
        continue_text = font_instructions.render("Press P to continue", True, (200, 200, 200))
        self.screen.blit(continue_text, (self.screen.get_width() // 2 - continue_text.get_width() // 2, 280))
        
        restart_text = font_instructions.render("Press R to restart level", True, (200, 200, 200))
        self.screen.blit(restart_text, (self.screen.get_width() // 2 - restart_text.get_width() // 2, 320))
        
        menu_text = font_instructions.render("Press ESC to return to level select", True, (200, 200, 200))
        self.screen.blit(menu_text, (self.screen.get_width() // 2 - menu_text.get_width() // 2, 360))
    
    def draw_game_objects(self):
        # Draw player
        self.player.draw(self.screen)
        
        # Draw keys
        for key_pos in self.key_positions:
            key_x, key_y = key_pos
            key_rect = pygame.Rect(
                key_x * self.cell_size + self.cell_size // 4,
                key_y * self.cell_size + self.cell_size // 4,
                self.cell_size // 2,
                self.cell_size // 2
            )
            pygame.draw.rect(self.screen, (255, 215, 0), key_rect)  # Gold color for keys
        
        # Draw door if present
        if self.door_position:
            door_x, door_y = self.door_position
            door_rect = pygame.Rect(
                door_x * self.cell_size,
                door_y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            # Draw door in brown or red depending on whether it's locked
            door_color = (139, 69, 19) if self.keys_collected >= self.keys_required else (139, 0, 0)
            pygame.draw.rect(self.screen, door_color, door_rect)
        
        # Draw stairs
        for stair_pos in self.stair_positions:
            stair_x, stair_y = stair_pos
            stair_rect = pygame.Rect(
                stair_x * self.cell_size,
                stair_y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(self.screen, (128, 0, 128), stair_rect)  # Purple for stairs
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw traps
        for trap in self.traps:
            trap.draw(self.screen)
        
        # Apply lighting effect
        self.screen.blit(self.light_surface, (0, 0), special_flags=pygame.BLEND_MULT)
    
    def reset_progress(self):
        """Reset all progress, unlocking only level 1"""
        # Show confirmation dialog
        font = pygame.font.SysFont("Arial", 24)
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Draw confirmation message
        title_text = font.render("Reset Progress?", True, (255, 255, 255))
        self.screen.blit(title_text, (self.screen.get_width() // 2 - title_text.get_width() // 2, 200))
        
        confirm_text = font.render("This will reset all unlocked levels and high scores.", True, (255, 200, 200))
        self.screen.blit(confirm_text, (self.screen.get_width() // 2 - confirm_text.get_width() // 2, 240))
        
        # Draw buttons
        yes_rect = pygame.Rect(self.screen.get_width() // 2 - 110, 300, 100, 40)
        pygame.draw.rect(self.screen, (150, 50, 50), yes_rect)
        yes_text = font.render("Yes", True, (255, 255, 255))
        self.screen.blit(yes_text, (yes_rect.centerx - yes_text.get_width() // 2, yes_rect.centery - yes_text.get_height() // 2))
        
        no_rect = pygame.Rect(self.screen.get_width() // 2 + 10, 300, 100, 40)
        pygame.draw.rect(self.screen, (50, 150, 50), no_rect)
        no_text = font.render("No", True, (255, 255, 255))
        self.screen.blit(no_text, (no_rect.centerx - no_text.get_width() // 2, no_rect.centery - no_text.get_height() // 2))
        
        pygame.display.flip()
        
        # Wait for user confirmation
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if yes_rect.collidepoint(mouse_pos):
                        # Reset progress
                        self.level_manager.reset_progress()
                        self.sound_manager.play_sound("menu_click")
                        waiting_for_input = False
                    
                    if no_rect.collidepoint(mouse_pos):
                        # Cancel
                        self.sound_manager.play_sound("menu_back")
                        waiting_for_input = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        # Reset progress
                        self.level_manager.reset_progress()
                        self.sound_manager.play_sound("menu_click")
                        waiting_for_input = False
                    
                    if event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        # Cancel
                        self.sound_manager.play_sound("menu_back")
                        waiting_for_input = False
        
        # Redraw level select screen
        self.draw_level_select()
        pygame.display.flip()
    
    def toggle_sound_mute(self):
        """Toggle sound mute state"""
        self.sound_muted = not self.sound_muted
        
        if self.sound_muted:
            # Mute all sounds
            # Stop all channels
            self.sound_manager.effect_channel.set_volume(0)
            self.sound_manager.ambient_channel.set_volume(0)
            self.sound_manager.music_channel.set_volume(0)
            
            # Mute all individual sounds
            for sound in self.sound_manager.sounds.values():
                sound.set_volume(0)
            
            # Mute all music tracks
            for track in self.sound_manager.music_tracks.values():
                track.set_volume(0)
            
            print("Sound muted")
        else:
            # Restore sound volumes
            self.sound_manager.effect_channel.set_volume(self.sound_manager.effect_volume)
            self.sound_manager.ambient_channel.set_volume(self.sound_manager.ambient_volume)
            self.sound_manager.music_channel.set_volume(self.sound_manager.music_volume)
            
            # Restore individual sound volumes
            for sound in self.sound_manager.sounds.values():
                sound.set_volume(self.sound_manager.effect_volume)
            
            # Restore music track volumes based on type
            for name, track in self.sound_manager.music_tracks.items():
                if "ambient" in name:
                    track.set_volume(self.sound_manager.ambient_volume)
                else:
                    track.set_volume(self.sound_manager.music_volume)
            
            print("Sound unmuted")
        
        # Don't play a sound when toggling - it would be confusing
    
    def draw_mute_button(self):
        """Draw the mute button in the corner of the screen"""
        button_size = 30
        margin = 10
        button_x = self.screen.get_width() - button_size - margin
        button_y = self.screen.get_height() - button_size - margin
        
        # Draw button background
        button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
        pygame.draw.rect(self.screen, (80, 80, 80), button_rect)
        pygame.draw.rect(self.screen, (150, 150, 150), button_rect, 2)  # Border
        
        # Draw icon based on mute state
        if self.sound_muted:
            # Draw muted icon (speaker with X)
            pygame.draw.polygon(self.screen, (200, 200, 200), [
                (button_x + 6, button_y + 12),  # Left
                (button_x + 10, button_y + 8),  # Top
                (button_x + 10, button_y + 16)   # Bottom
            ])
            pygame.draw.rect(self.screen, (200, 200, 200), 
                            pygame.Rect(button_x + 6, button_y + 10, 4, 4))
            
            # Draw X
            pygame.draw.line(self.screen, (255, 100, 100), 
                            (button_x + 12, button_y + 8), 
                            (button_x + 18, button_y + 16), 2)
            pygame.draw.line(self.screen, (255, 100, 100), 
                            (button_x + 18, button_y + 8), 
                            (button_x + 12, button_y + 16), 2)
        else:
            # Draw unmuted icon (speaker with waves)
            pygame.draw.polygon(self.screen, (200, 200, 200), [
                (button_x + 6, button_y + 12),  # Left
                (button_x + 10, button_y + 8),  # Top
                (button_x + 10, button_y + 16)   # Bottom
            ])
            pygame.draw.rect(self.screen, (200, 200, 200), 
                            pygame.Rect(button_x + 6, button_y + 10, 4, 4))
            
            # Draw sound waves
            pygame.draw.arc(self.screen, (200, 200, 200), 
                            pygame.Rect(button_x + 10, button_y + 6, 5, 12), 
                            -0.5, 0.5, 1)
            pygame.draw.arc(self.screen, (200, 200, 200), 
                            pygame.Rect(button_x + 13, button_y + 4, 8, 16), 
                            -0.5, 0.5, 1)
        
        # Add tooltip text
        font = pygame.font.SysFont("Arial", 12)
        tooltip = font.render("X to toggle sound", True, (200, 200, 200))
        self.screen.blit(tooltip, (button_x - tooltip.get_width() + button_size, button_y - 15))
        
        return button_rect
    
    def draw_game_description(self):
        """Draw a screen with game description and instructions that can be scrolled"""
        # Fill background
        self.screen.fill((20, 20, 30))
        
        # Title
        font_title = pygame.font.SysFont("Arial", 36)
        title_text = font_title.render("MAZE RUNNER - GAME GUIDE", True, (255, 255, 255))
        self.screen.blit(title_text, (self.screen.get_width() // 2 - title_text.get_width() // 2, 50))
        
        # Create fonts
        font_heading = pygame.font.SysFont("Arial", 24)
        font_text = pygame.font.SysFont("Arial", 18)
        
        # Create a surface for the scrollable content
        # Make it taller than the screen to accommodate all content
        content_width = self.screen.get_width() - 100  # 50px margin on each side
        content_height = 1200  # Tall enough for all content
        content_surface = pygame.Surface((content_width, content_height))
        content_surface.fill((20, 20, 30))
        
        # Track the current y position for drawing content
        y_pos = 20
        
        # Game objective
        heading = font_heading.render("OBJECTIVE", True, (255, 200, 100))
        content_surface.blit(heading, (30, y_pos))
        
        y_pos += 35
        objective_lines = [
            "Navigate through the maze to find the exit (green square).",
            "Collect keys to unlock doors and reach higher levels.",
            "Avoid enemies and traps while finding the most efficient path.",
            "Complete levels to unlock new challenges."
        ]
        
        for line in objective_lines:
            text = font_text.render(line, True, (220, 220, 220))
            content_surface.blit(text, (50, y_pos))
            y_pos += 25
        
        # Enemies
        y_pos += 15
        heading = font_heading.render("ENEMIES", True, (255, 100, 100))
        content_surface.blit(heading, (30, y_pos))
        
        y_pos += 35
        enemy_lines = [
            "Red squares patrol the maze in random patterns.",
            "They move faster in higher difficulty levels.",
            "If an enemy touches you, you lose the game.",
            "Listen for audio cues when enemies are nearby.",
            "Enemies can't pass through walls, so use the maze layout to your advantage.",
            "Plan your route to avoid enemy patrol paths."
        ]
        
        for line in enemy_lines:
            text = font_text.render(line, True, (220, 220, 220))
            content_surface.blit(text, (50, y_pos))
            y_pos += 25
        
        # Traps
        y_pos += 15
        heading = font_heading.render("TRAPS", True, (255, 165, 0))
        content_surface.blit(heading, (30, y_pos))
        
        y_pos += 35
        trap_lines = [
            "Gray squares with spikes activate periodically.",
            "Orange warning color indicates a trap is about to activate.",
            "Red color means the trap is active and dangerous.",
            "Traps activate more frequently in higher difficulty levels.",
            "Unlike enemies, traps stay in fixed positions.",
            "Watch the trap cycle to time your movement through dangerous areas."
        ]
        
        for line in trap_lines:
            text = font_text.render(line, True, (220, 220, 220))
            content_surface.blit(text, (50, y_pos))
            y_pos += 25
        
        # Game elements
        y_pos += 15
        heading = font_heading.render("GAME ELEMENTS", True, (100, 200, 255))
        content_surface.blit(heading, (30, y_pos))
        
        y_pos += 35
        elements_lines = [
            "Keys (gold squares): Collect to unlock doors.",
            "Doors (brown/red squares): Require keys to pass through.",
            "Stairs (purple squares): Move to the next floor in multi-level mazes.",
            "Exit (green square): Reach this to complete the level."
        ]
        
        for line in elements_lines:
            text = font_text.render(line, True, (220, 220, 220))
            content_surface.blit(text, (50, y_pos))
            y_pos += 25
        
        # Controls
        y_pos += 15
        heading = font_heading.render("CONTROLS", True, (150, 255, 150))
        content_surface.blit(heading, (30, y_pos))
        
        y_pos += 35
        controls_lines = [
            "Arrow Keys: Move the player character",
            "Space: Stop movement immediately",
            "M: Toggle minimap visibility",
            "X: Toggle sound on/off",
            "P: Pause/unpause the game",
            "R: Restart the current level",
            "ESC: Return to level select screen",
            "1-9: Quick select difficulty level"
        ]
        
        for line in controls_lines:
            text = font_text.render(line, True, (220, 220, 220))
            content_surface.blit(text, (50, y_pos))
            y_pos += 25
        
        # Scoring
        y_pos += 15
        heading = font_heading.render("SCORING", True, (255, 255, 150))
        content_surface.blit(heading, (30, y_pos))
        
        y_pos += 35
        scoring_lines = [
            "Complete levels faster for higher time bonuses.",
            "Each step taken reduces your score slightly.",
            "Collecting keys adds bonus points.",
            "Completing multiple floors in a level adds significant bonus points.",
            "Higher difficulty levels offer greater scoring potential."
        ]
        
        for line in scoring_lines:
            text = font_text.render(line, True, (220, 220, 220))
            content_surface.blit(text, (50, y_pos))
            y_pos += 25
        
        # Tips
        y_pos += 15
        heading = font_heading.render("TIPS & STRATEGIES", True, (150, 150, 255))
        content_surface.blit(heading, (30, y_pos))
        
        y_pos += 35
        tips_lines = [
            "Use the minimap to plan your route through the maze.",
            "Listen for audio cues that indicate nearby enemies or traps.",
            "In higher levels, focus on finding keys before heading to the exit.",
            "The lighting effect shows a limited view - be cautious when exploring.",
            "Enemies move in predictable patterns - observe before rushing through.",
            "If you get stuck, try restarting the level with a fresh maze layout.",
            "Multi-floor mazes require careful planning to navigate efficiently."
        ]
        
        for line in tips_lines:
            text = font_text.render(line, True, (220, 220, 220))
            content_surface.blit(text, (50, y_pos))
            y_pos += 25
        
        # Store the total content height
        self.description_content_height = y_pos + 50
        
        # Get the current scroll position (or initialize it)
        if not hasattr(self, 'description_scroll_y'):
            self.description_scroll_y = 0
        
        # Calculate the visible area height
        visible_height = self.screen.get_height() - 150  # Account for title and buttons
        
        # Draw the visible portion of the content
        visible_content_rect = pygame.Rect(0, self.description_scroll_y, content_width, visible_height)
        self.screen.blit(content_surface, (50, 100), visible_content_rect)
        
        # Draw scroll indicators if needed
        if self.description_scroll_y > 0:
            # Draw up arrow
            pygame.draw.polygon(self.screen, (200, 200, 200), [
                (self.screen.get_width() // 2, 85),
                (self.screen.get_width() // 2 - 10, 95),
                (self.screen.get_width() // 2 + 10, 95)
            ])
        
        if self.description_scroll_y < self.description_content_height - visible_height and self.description_content_height > visible_height:
            # Draw down arrow
            pygame.draw.polygon(self.screen, (200, 200, 200), [
                (self.screen.get_width() // 2, self.screen.get_height() - 35),
                (self.screen.get_width() // 2 - 10, self.screen.get_height() - 45),
                (self.screen.get_width() // 2 + 10, self.screen.get_height() - 45)
            ])
        
        # Draw scroll instructions
        scroll_text = font_text.render("Use UP/DOWN arrows or mouse wheel to scroll", True, (180, 180, 180))
        self.screen.blit(scroll_text, (self.screen.get_width() // 2 - scroll_text.get_width() // 2, self.screen.get_height() - 60))
        
        # Draw back button
        back_rect = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(self.screen, (100, 100, 100), back_rect)
        back_text = font_text.render("BACK", True, (255, 255, 255))
        self.screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, back_rect.centery - back_text.get_height() // 2))
        
        # Store the back button rect for click detection
        self.description_back_button = back_rect
        
        # Draw mute button
        self.mute_button_rect = self.draw_mute_button()
    
    def handle_description_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Return to menu
                self.sound_manager.play_sound("menu_back")
                self.current_screen = "menu"
            elif event.key == pygame.K_UP:
                # Scroll up
                self.description_scroll_y = max(0, self.description_scroll_y - 30)
            elif event.key == pygame.K_DOWN:
                # Scroll down
                visible_height = self.screen.get_height() - 150
                max_scroll = max(0, self.description_content_height - visible_height)
                self.description_scroll_y = min(max_scroll, self.description_scroll_y + 30)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if back button was clicked
            if hasattr(self, 'description_back_button') and self.description_back_button.collidepoint(mouse_pos):
                self.sound_manager.play_sound("menu_back")
                self.current_screen = "menu"
                return
            
            # Check if mute button was clicked
            if hasattr(self, 'mute_button_rect') and self.mute_button_rect.collidepoint(mouse_pos):
                self.toggle_sound_mute()
                return
            
            # Handle mouse wheel scrolling
            if event.button == 4:  # Scroll up
                self.description_scroll_y = max(0, self.description_scroll_y - 30)
            elif event.button == 5:  # Scroll down
                visible_height = self.screen.get_height() - 150
                max_scroll = max(0, self.description_content_height - visible_height)
                self.description_scroll_y = min(max_scroll, self.description_scroll_y + 30)
    
    def run(self):
        clock = pygame.time.Clock()
        
        while True:
            self.handle_events()
            
            if self.game_active and not self.game_paused:
                self.update(clock.tick(60) / 1000)
            else:
                # Still tick the clock even when not updating
                clock.tick(60)
            
            self.draw() 