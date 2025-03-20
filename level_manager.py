import os
import json
import pygame

class LevelManager:
    def __init__(self):
        self.current_level = 1
        self.max_level = 10
        self.levels_unlocked = 1
        self.high_scores = {}
        self.save_file = "maze_progress.json"
        self.load_progress()
        
        # Level configurations
        self.level_configs = {
            # Level 1: Basic maze with minimal enemies and traps
            1: {
                "size": (31, 31),
                "enemies": 1,
                "traps": 1,
                "keys_required": 0,
                "time_limit": 0,  # No time limit
                "floors": 1,
                "theme": "dungeon",
                "description": "Find your way through a simple maze with a single enemy and trap.",
                "enemy_speed": 0.3,  # Slow enemy speed
                "trap_activation_time": 5.0,  # Long trap activation cycle
                "min_exit_distance": 15  # Ensure exit is not too close
            },
            # Level 2: Slightly more challenging
            2: {
                "size": (31, 31),
                "enemies": 2,
                "traps": 2,
                "keys_required": 0,
                "time_limit": 0,
                "floors": 1,
                "theme": "dungeon",
                "description": "More enemies and traps to avoid.",
                "enemy_speed": 0.4,
                "trap_activation_time": 4.0,
                "min_exit_distance": 18
            },
            # Level 3: Introducing keys
            3: {
                "size": (35, 35),
                "enemies": 3,
                "traps": 3,
                "keys_required": 1,
                "time_limit": 0,
                "floors": 1,
                "theme": "dungeon",
                "description": "Find the key while avoiding enemies and traps.",
                "enemy_speed": 0.5,
                "trap_activation_time": 3.5,
                "min_exit_distance": 20
            },
            # Level 4: More challenging
            4: {
                "size": (35, 35),
                "enemies": 4,
                "traps": 4,
                "keys_required": 1,
                "time_limit": 180,  # 3 minutes
                "floors": 1,
                "theme": "dungeon",
                "description": "Beat the clock while navigating through dangers.",
                "enemy_speed": 0.6,
                "trap_activation_time": 3.0,
                "min_exit_distance": 22
            },
            # Level 5: Forest theme
            5: {
                "size": (41, 41),
                "enemies": 5,
                "traps": 6,
                "keys_required": 1,
                "time_limit": 210,  # 3.5 minutes
                "floors": 1,
                "theme": "forest",
                "description": "Navigate through the forest maze with increased dangers.",
                "enemy_speed": 0.7,
                "trap_activation_time": 2.5,
                "min_exit_distance": 25
            },
            # Level 6: Multi-floor dungeon
            6: {
                "size": (31, 31),
                "enemies": 6,
                "traps": 8,
                "keys_required": 2,
                "time_limit": 240,  # 4 minutes
                "floors": 2,
                "theme": "dungeon",
                "description": "Find the stairs while avoiding numerous enemies and traps.",
                "enemy_speed": 0.8,
                "trap_activation_time": 2.0,
                "min_exit_distance": 20
            },
            # Level 7: Space theme
            7: {
                "size": (41, 41),
                "enemies": 7,
                "traps": 10,
                "keys_required": 2,
                "time_limit": 300,  # 5 minutes
                "floors": 1,
                "theme": "space",
                "description": "Navigate through the space station with fast enemies.",
                "enemy_speed": 0.9,
                "trap_activation_time": 1.8,
                "min_exit_distance": 28
            },
            # Level 8: Complex multi-floor
            8: {
                "size": (41, 41),
                "enemies": 8,
                "traps": 12,
                "keys_required": 3,
                "time_limit": 360,  # 6 minutes
                "floors": 2,
                "theme": "space",
                "description": "A complex multi-floor space station with aggressive enemies.",
                "enemy_speed": 1.0,
                "trap_activation_time": 1.5,
                "min_exit_distance": 30
            },
            # Level 9: Forest challenge
            9: {
                "size": (45, 45),
                "enemies": 9,
                "traps": 15,
                "keys_required": 3,
                "time_limit": 420,  # 7 minutes
                "floors": 2,
                "theme": "forest",
                "description": "A challenging forest maze with fast enemies and quick traps.",
                "enemy_speed": 1.1,
                "trap_activation_time": 1.2,
                "min_exit_distance": 32
            },
            # Level 10: Ultimate challenge
            10: {
                "size": (51, 51),
                "enemies": 10,
                "traps": 20,
                "keys_required": 4,
                "time_limit": 600,  # 10 minutes
                "floors": 3,
                "theme": "dungeon",
                "description": "The ultimate maze challenge with deadly enemies and traps.",
                "enemy_speed": 1.2,
                "trap_activation_time": 1.0,
                "min_exit_distance": 35
            }
        }
    
    def load_progress(self):
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    self.levels_unlocked = data.get("levels_unlocked", 1)
                    self.high_scores = data.get("high_scores", {})
                    # Convert string keys back to integers
                    self.high_scores = {int(k): v for k, v in self.high_scores.items()}
        except Exception as e:
            print(f"Error loading progress: {e}")
            # Initialize with defaults if loading fails
            self.levels_unlocked = 1
            self.high_scores = {}
    
    def save_progress(self):
        try:
            data = {
                "levels_unlocked": self.levels_unlocked,
                "high_scores": self.high_scores
            }
            with open(self.save_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving progress: {e}")
    
    def get_level_config(self, level_num=None):
        if level_num is None:
            level_num = self.current_level
        
        # Ensure level number is valid
        level_num = max(1, min(level_num, self.max_level))
        
        return self.level_configs.get(level_num, self.level_configs[1])
    
    def set_level(self, level_num):
        if 1 <= level_num <= self.max_level and level_num <= self.levels_unlocked:
            self.current_level = level_num
            return True
        return False
    
    def next_level(self):
        if self.current_level < self.max_level:
            self.current_level += 1
            return True
        return False
    
    def unlock_next_level(self):
        if self.levels_unlocked < self.max_level:
            self.levels_unlocked += 1
            self.save_progress()
            return True
        return False
    
    def update_high_score(self, level, score):
        # Convert level to string for JSON serialization
        level_key = level
        
        # Update high score if it's better than the existing one
        if level_key not in self.high_scores or score > self.high_scores[level_key]:
            self.high_scores[level_key] = score
            self.save_progress()
            return True
        return False
    
    def get_high_score(self, level):
        return self.high_scores.get(level, 0)
    
    def is_level_unlocked(self, level):
        return level <= self.levels_unlocked
    
    def get_level_selection_surfaces(self, font, selected_level=None):
        surfaces = []
        
        for level in range(1, self.max_level + 1):
            # Determine if level is unlocked and/or selected
            unlocked = self.is_level_unlocked(level)
            selected = level == selected_level
            
            # Create background color based on state
            if selected:
                bg_color = (100, 100, 255)  # Blue for selected
            elif unlocked:
                bg_color = (50, 150, 50)  # Green for unlocked
            else:
                bg_color = (150, 50, 50)  # Red for locked
            
            # Create text color based on state
            text_color = (255, 255, 255)
            
            # Create level button surface
            button_width, button_height = 200, 60
            button_surface = pygame.Surface((button_width, button_height))
            button_surface.fill(bg_color)
            
            # Add level number and high score
            level_text = font.render(f"Level {level}", True, text_color)
            button_surface.blit(level_text, (10, 10))
            
            if unlocked:
                high_score = self.get_high_score(level)
                if high_score > 0:
                    score_text = font.render(f"Best: {high_score}", True, text_color)
                    button_surface.blit(score_text, (10, 35))
            else:
                lock_text = font.render("LOCKED", True, text_color)
                button_surface.blit(lock_text, (10, 35))
            
            surfaces.append((button_surface, level))
        
        return surfaces 
    
    def reset_progress(self):
        """Reset all progress, unlocking only level 1"""
        self.levels_unlocked = 1
        self.high_scores = {1: 0}  # Reset all high scores
        
        # Save the reset progress
        self.save_progress() 