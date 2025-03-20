import pygame

class Player:
    def __init__(self, x, y, cell_size):
        self.x = x
        self.y = y
        self.cell_size = cell_size
        self.color = (0, 0, 255)  # Blue
        self.speed = 5
        self.target_x = x * cell_size
        self.target_y = y * cell_size
        self.current_x = self.target_x
        self.current_y = self.target_y
        self.moving = False
        self.steps_taken = 0
        self.visited_cells = set()
        self.visited_cells.add((x, y))
        self.continuous_dx = 0
        self.continuous_dy = 0
    
    def move(self, dx, dy, maze):
        if self.moving:
            return False
        
        new_x, new_y = self.x + dx, self.y + dy
        
        # Check if the new position is valid (not a wall)
        if 0 <= new_x < maze.shape[1] and 0 <= new_y < maze.shape[0] and maze[new_y][new_x] == 0:
            self.x = new_x
            self.y = new_y
            self.target_x = self.x * self.cell_size
            self.target_y = self.y * self.cell_size
            self.moving = True
            self.steps_taken += 1
            self.visited_cells.add((new_x, new_y))
            
            # Set continuous movement direction
            self.continuous_dx = dx
            self.continuous_dy = dy
            
            return True
        return False
    
    def continue_movement(self, maze):
        if not self.moving and (self.continuous_dx != 0 or self.continuous_dy != 0):
            # Try to move in the continuous direction
            if not self.move(self.continuous_dx, self.continuous_dy, maze):
                # If we hit a wall, stop continuous movement
                self.continuous_dx = 0
                self.continuous_dy = 0
    
    def stop_continuous_movement(self):
        self.continuous_dx = 0
        self.continuous_dy = 0
    
    def update(self):
        """Update player position based on continuous movement"""
        moved = False
        
        if self.moving:
            # Calculate target position
            target_x = self.x * self.cell_size
            target_y = self.y * self.cell_size
            
            # Move towards target position
            dx = target_x - self.current_x
            dy = target_y - self.current_y
            
            if abs(dx) < self.speed and abs(dy) < self.speed:
                # Reached target position
                self.current_x = target_x
                self.current_y = target_y
                self.moving = False
                moved = True  # Completed a move
            else:
                # Continue moving towards target
                if dx > 0:
                    self.current_x += self.speed
                elif dx < 0:
                    self.current_x -= self.speed
                
                if dy > 0:
                    self.current_y += self.speed
                elif dy < 0:
                    self.current_y -= self.speed
        
        return moved
    
    def draw(self, screen):
        pygame.draw.circle(
            screen, 
            self.color, 
            (self.current_x + self.cell_size // 2, self.current_y + self.cell_size // 2), 
            self.cell_size // 2 - 4
        )
    
    def reset(self, x, y):
        self.x = x
        self.y = y
        self.target_x = x * self.cell_size
        self.target_y = y * self.cell_size
        self.current_x = self.target_x
        self.current_y = self.target_y
        self.moving = False
        self.steps_taken = 0
        self.visited_cells = set()
        self.visited_cells.add((x, y))
        self.continuous_dx = 0
        self.continuous_dy = 0
    
    def get_position(self):
        return (self.x, self.y)
    
    def get_steps_taken(self):
        return self.steps_taken
    
    def get_rect(self):
        """
        Returns a pygame Rect object representing the player's position and size.
        Used for collision detection with enemies and other objects.
        """
        return pygame.Rect(
            self.current_x + 2,  # Add a small offset for more precise collisions
            self.current_y + 2,  # Add a small offset for more precise collisions
            self.cell_size - 4,  # Make hitbox slightly smaller than cell
            self.cell_size - 4   # Make hitbox slightly smaller than cell
        ) 