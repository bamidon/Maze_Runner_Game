import pygame
import random

class Trap:
    def __init__(self, x, y, cell_size, trap_type="spike", activation_time=3.0):
        self.x = x
        self.y = y
        self.cell_size = cell_size
        self.trap_type = trap_type
        self.activation_time = activation_time  # Time between activations
        self.active_duration = 1.0  # How long the trap stays active
        self.time_since_last_cycle = 0
        self.active = False
        
        # Colors for different trap states
        self.inactive_color = (100, 100, 100)  # Gray when inactive
        self.active_color = (255, 0, 0)  # Red when active
        self.warning_color = (255, 165, 0)  # Orange when about to activate
    
    def update(self, delta_time):
        self.time_since_last_cycle += delta_time
        
        # Calculate the full cycle time
        cycle_time = self.activation_time + self.active_duration
        
        # Determine if the trap is active based on the cycle
        if self.time_since_last_cycle % cycle_time < self.active_duration:
            self.active = True
        else:
            self.active = False
        
        # Reset the cycle if needed
        if self.time_since_last_cycle >= cycle_time:
            self.time_since_last_cycle = 0
    
    def draw(self, screen):
        rect = pygame.Rect(
            self.x * self.cell_size,
            self.y * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        
        # Draw base
        pygame.draw.rect(screen, (100, 100, 100), rect)
        
        # Determine the current color based on trap state
        if self.active:
            current_color = self.active_color
        else:
            # Check if trap is about to activate (last 0.5 seconds of inactive period)
            time_until_active = self.activation_time - (self.time_since_last_cycle % (self.activation_time + self.active_duration))
            if time_until_active < 0.5:
                current_color = self.warning_color  # About to activate
            else:
                current_color = self.inactive_color  # Safely inactive
        
        if self.trap_type == "spike":
            # Draw spikes
            if self.active:
                # Active spikes (taller)
                spike_height = self.cell_size // 2
                base_y = self.y * self.cell_size + self.cell_size - spike_height
            else:
                # Inactive or warning spikes (shorter)
                spike_height = self.cell_size // 6
                base_y = self.y * self.cell_size + self.cell_size - spike_height
            
            # Draw multiple spikes
            spike_width = max(2, self.cell_size // 8)
            num_spikes = self.cell_size // (spike_width * 2)
            
            for i in range(num_spikes):
                spike_x = self.x * self.cell_size + (i * 2 + 1) * spike_width
                
                # Draw triangle spike
                pygame.draw.polygon(
                    screen,
                    current_color,  # Use the determined color
                    [
                        (spike_x - spike_width // 2, base_y + spike_height),  # Bottom left
                        (spike_x, base_y),  # Top
                        (spike_x + spike_width // 2, base_y + spike_height)   # Bottom right
                    ]
                )
        
        elif self.trap_type == "fire":
            # Draw fire
            if self.active or current_color == self.warning_color:
                # Draw flames
                flame_height = self.cell_size // 2 if self.active else self.cell_size // 4
                base_y = self.y * self.cell_size + self.cell_size - flame_height
                
                # Draw multiple flames
                flame_width = max(4, self.cell_size // 6)
                num_flames = max(3, self.cell_size // (flame_width * 2))
                
                for i in range(num_flames):
                    flame_x = self.x * self.cell_size + (i * 2 + 1) * flame_width
                    
                    # Draw flame (curved triangle)
                    pygame.draw.polygon(
                        screen,
                        current_color,  # Use the determined color
                        [
                            (flame_x - flame_width // 2, base_y + flame_height),  # Bottom left
                            (flame_x - flame_width // 4, base_y + flame_height // 2),  # Middle left
                            (flame_x, base_y),  # Top
                            (flame_x + flame_width // 4, base_y + flame_height // 2),  # Middle right
                            (flame_x + flame_width // 2, base_y + flame_height)   # Bottom right
                        ]
                    )
    
    def is_dangerous(self):
        return self.active
    
    def get_rect(self):
        return pygame.Rect(
            self.x * self.cell_size,
            self.y * self.cell_size,
            self.cell_size,
            self.cell_size
        )
    
    def set_cell_size(self, new_cell_size):
        self.cell_size = new_cell_size 