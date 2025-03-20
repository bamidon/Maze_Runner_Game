import pygame

class Theme:
    def __init__(self, name="dungeon"):
        self.name = name
        self.setup_theme()
    
    def setup_theme(self):
        # Default colors and assets for each theme
        themes = {
            "dungeon": {
                "wall_color": (60, 60, 70),
                "path_color": (120, 110, 100),
                "path_border": (90, 80, 70),
                "exit_color": (0, 200, 0),
                "info_panel": (40, 40, 50),
                "text_color": (220, 220, 220),
                "minimap_bg": (30, 30, 40),
                "minimap_wall": (80, 80, 90),
                "minimap_path": (150, 140, 130),
                "light_radius": 5,  # In cells
                "light_intensity": 0.8,  # 0-1 scale
                "ambient_light": 0.2,  # 0-1 scale
            },
            "forest": {
                "wall_color": (30, 80, 30),
                "path_color": (150, 180, 120),
                "path_border": (100, 130, 80),
                "exit_color": (220, 180, 50),
                "info_panel": (40, 70, 40),
                "text_color": (230, 230, 200),
                "minimap_bg": (20, 50, 20),
                "minimap_wall": (60, 100, 60),
                "minimap_path": (170, 200, 140),
                "light_radius": 6,  # In cells
                "light_intensity": 0.9,  # 0-1 scale
                "ambient_light": 0.3,  # 0-1 scale
            },
            "space": {
                "wall_color": (20, 20, 40),
                "path_color": (50, 50, 80),
                "path_border": (70, 70, 120),
                "exit_color": (100, 200, 255),
                "info_panel": (10, 10, 30),
                "text_color": (180, 200, 255),
                "minimap_bg": (5, 5, 20),
                "minimap_wall": (40, 40, 70),
                "minimap_path": (70, 70, 120),
                "light_radius": 4,  # In cells
                "light_intensity": 0.7,  # 0-1 scale
                "ambient_light": 0.1,  # 0-1 scale
            }
        }
        
        # Set theme properties
        self.properties = themes.get(self.name, themes["dungeon"])
        
        # Create light gradient surface for lighting effects
        self.create_light_gradient()
    
    def create_light_gradient(self):
        # Create a radial gradient for the light effect
        size = 400  # Size of the gradient surface
        center = (size // 2, size // 2)
        radius = size // 2
        
        # Create a surface with alpha channel
        self.light_gradient = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw the gradient
        for x in range(size):
            for y in range(size):
                # Calculate distance from center
                distance = ((x - center[0]) ** 2 + (y - center[1]) ** 2) ** 0.5
                
                # Calculate alpha based on distance
                if distance < radius:
                    # Linear falloff
                    alpha = int(255 * (1 - distance / radius) * self.properties["light_intensity"])
                    # Draw pixel
                    self.light_gradient.set_at((x, y), (255, 255, 255, alpha))
    
    def get_wall_color(self):
        return self.properties["wall_color"]
    
    def get_path_color(self):
        return self.properties["path_color"]
    
    def get_path_border(self):
        return self.properties["path_border"]
    
    def get_exit_color(self):
        return self.properties["exit_color"]
    
    def get_info_panel_color(self):
        return self.properties["info_panel"]
    
    def get_text_color(self):
        return self.properties["text_color"]
    
    def get_minimap_bg(self):
        return self.properties["minimap_bg"]
    
    def get_minimap_wall(self):
        return self.properties["minimap_wall"]
    
    def get_minimap_path(self):
        return self.properties["minimap_path"]
    
    def get_light_radius(self):
        return self.properties["light_radius"]
    
    def get_ambient_light(self):
        return self.properties["ambient_light"]
    
    def get_light_gradient(self):
        return self.light_gradient
    
    def change_theme(self, new_theme):
        self.name = new_theme
        self.setup_theme()
        return self.properties 