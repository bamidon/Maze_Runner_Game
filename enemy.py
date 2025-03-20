import pygame
import random

class Enemy:
    def __init__(self, x, y, cell_size, maze, speed=0.5):
        self.x = x
        self.y = y
        self.cell_size = cell_size
        self.color = (255, 0, 0)  # Red
        self.speed = speed  # Movement speed (cells per second)
        self.target_x = x * cell_size
        self.target_y = y * cell_size
        self.current_x = self.target_x
        self.current_y = self.target_y
        self.moving = False
        self.maze = maze
        self.direction = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
        self.time_until_direction_change = random.uniform(2.0, 5.0)
        self.patrol_timer = 0
        self.patrol_change_time = random.randint(3, 8) * 1000  # 3-8 seconds in milliseconds
    
    def update(self, delta_time):
        # Update patrol timer
        self.patrol_timer += delta_time
        if self.patrol_timer >= self.patrol_change_time:
            self.patrol_timer = 0
            self.patrol_change_time = random.randint(3, 8) * 1000
            self.change_direction()
        
        # Handle movement animation
        if self.moving:
            dx = self.target_x - self.current_x
            dy = self.target_y - self.current_y
            
            if abs(dx) < self.speed and abs(dy) < self.speed:
                self.current_x = self.target_x
                self.current_y = self.target_y
                self.moving = False
            else:
                if dx != 0:
                    self.current_x += self.speed if dx > 0 else -self.speed
                if dy != 0:
                    self.current_y += self.speed if dy > 0 else -self.speed
        else:
            # Try to move in the current direction
            self.move()
    
    def move(self):
        dx, dy = self.direction
        new_x, new_y = self.x + dx, self.y + dy
        
        # Check if the new position is valid (not a wall)
        if 0 <= new_x < self.maze.shape[1] and 0 <= new_y < self.maze.shape[0] and self.maze[new_y][new_x] == 0:
            self.x = new_x
            self.y = new_y
            self.target_x = self.x * self.cell_size
            self.target_y = self.y * self.cell_size
            self.moving = True
            return True
        else:
            # Hit a wall, change direction
            self.change_direction()
            return False
    
    def change_direction(self):
        # Try to find a valid direction
        possible_directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(possible_directions)
        
        for dx, dy in possible_directions:
            new_x, new_y = self.x + dx, self.y + dy
            if 0 <= new_x < self.maze.shape[1] and 0 <= new_y < self.maze.shape[0] and self.maze[new_y][new_x] == 0:
                self.direction = (dx, dy)
                return
    
    def draw(self, screen):
        # Draw enemy body
        pygame.draw.circle(
            screen, 
            self.color, 
            (self.current_x + self.cell_size // 2, self.current_y + self.cell_size // 2), 
            self.cell_size // 2 - 2
        )
        
        # Draw eyes to indicate direction
        eye_color = (255, 255, 255)
        eye_size = max(2, self.cell_size // 8)
        
        # Base eye positions
        center_x = self.current_x + self.cell_size // 2
        center_y = self.current_y + self.cell_size // 2
        eye_offset = self.cell_size // 4
        
        # Adjust eye positions based on direction
        dx, dy = self.direction
        if dx == 1:  # Right
            eye1_pos = (center_x + eye_offset // 2, center_y - eye_offset)
            eye2_pos = (center_x + eye_offset // 2, center_y + eye_offset)
        elif dx == -1:  # Left
            eye1_pos = (center_x - eye_offset // 2, center_y - eye_offset)
            eye2_pos = (center_x - eye_offset // 2, center_y + eye_offset)
        elif dy == 1:  # Down
            eye1_pos = (center_x - eye_offset, center_y + eye_offset // 2)
            eye2_pos = (center_x + eye_offset, center_y + eye_offset // 2)
        else:  # Up
            eye1_pos = (center_x - eye_offset, center_y - eye_offset // 2)
            eye2_pos = (center_x + eye_offset, center_y - eye_offset // 2)
        
        pygame.draw.circle(screen, eye_color, eye1_pos, eye_size)
        pygame.draw.circle(screen, eye_color, eye2_pos, eye_size)
    
    def get_position(self):
        return (self.x, self.y)
    
    def get_rect(self):
        return pygame.Rect(
            self.current_x + 2,
            self.current_y + 2,
            self.cell_size - 4,
            self.cell_size - 4
        )
    
    def set_cell_size(self, new_cell_size):
        ratio = new_cell_size / self.cell_size
        self.cell_size = new_cell_size
        self.speed = max(1, new_cell_size // 10)
        self.target_x = self.x * new_cell_size
        self.target_y = self.y * new_cell_size
        self.current_x = self.current_x * ratio
        self.current_y = self.current_y * ratio 