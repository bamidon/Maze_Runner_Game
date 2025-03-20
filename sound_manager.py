import pygame
import os
import math
import random

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        
        # Sound effect channels
        self.effect_channel = pygame.mixer.Channel(0)
        self.ambient_channel = pygame.mixer.Channel(1)
        self.music_channel = pygame.mixer.Channel(2)
        
        # Sound volumes
        self.music_volume = 0.5
        self.effect_volume = 0.7
        self.ambient_volume = 0.4
        
        # Sound effects dictionary
        self.sounds = {}
        
        # Music tracks
        self.music_tracks = {}
        
        # Current music
        self.current_music = None
        self.current_ambient = None
        
        # Load sounds
        self.load_sounds()
    
    def load_sounds(self):
        # Define sound paths
        sound_paths = {
            # Movement sounds
            "move": "assets/footstep.wav",
            "footstep1": "assets/footstep1.wav",
            "footstep2": "assets/footstep2.wav",
            
            # Interaction sounds
            "key_pickup": "assets/key.wav",
            "door_unlock": "assets/door.wav",
            "stairs": "assets/stairs.wav",
            
            # Game state sounds
            "victory": "assets/victory.wav",
            "game_over": "assets/game_over.wav",
            "level_complete": "assets/level_complete.wav",
            
            # Enemy sounds
            "enemy_nearby": "assets/enemy_nearby.wav",
            "enemy_attack": "assets/enemy.wav",
            
            # Trap sounds
            "trap_activate": "assets/trap.wav",
            "trap_warning": "assets/trap_warning.wav",
            
            # UI sounds
            "menu_select": "assets/menu_select.wav",
            "menu_click": "assets/click.wav",
            "menu_back": "assets/back.wav"
        }
        
        # Music paths
        music_paths = {
            "dungeon_ambient": "assets/dungeon_ambient.wav",
            "forest_ambient": "assets/forest_ambient.wav",
            "space_ambient": "assets/space_ambient.wav",
            
            "dungeon_music": "assets/dungeon_music.wav",
            "forest_music": "assets/forest_music.wav",
            "space_music": "assets/space_music.wav",
            
            "tension": "assets/tension.wav",
            "victory_music": "assets/victory_music.wav",
            "menu_music": "assets/menu_music.wav"
        }
        
        # Load sound effects
        for name, path in sound_paths.items():
            try:
                if os.path.exists(path) and os.path.getsize(path) > 100:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(self.effect_volume)
            except:
                print(f"Warning: Could not load sound {name} from {path}")
        
        # Load music tracks
        for name, path in music_paths.items():
            try:
                if os.path.exists(path) and os.path.getsize(path) > 100:
                    self.music_tracks[name] = pygame.mixer.Sound(path)
                    # Set appropriate volume based on type
                    if "ambient" in name:
                        self.music_tracks[name].set_volume(self.ambient_volume)
                    else:
                        self.music_tracks[name].set_volume(self.music_volume)
            except:
                print(f"Warning: Could not load music {name} from {path}")
        
        # Create fallback sounds if needed
        self._create_fallback_sounds()
    
    def _create_fallback_sounds(self):
        # If no move sound is loaded, create a simple beep
        if "move" not in self.sounds:
            self.sounds["move"] = self._create_beep(220, 100)  # 220Hz for 100ms
            self.sounds["move"].set_volume(self.effect_volume)
        
        # If no victory sound is loaded, create a victory jingle
        if "victory" not in self.sounds:
            self.sounds["victory"] = self._create_beep(440, 500)  # 440Hz for 500ms
            self.sounds["victory"].set_volume(self.effect_volume)
    
    def _create_beep(self, frequency, duration):
        # Create a simple beep sound
        sample_rate = 44100
        bits = 16
        
        # Calculate the number of samples needed
        num_samples = int(duration * sample_rate / 1000)
        
        # Create the buffer
        buf = bytearray(num_samples * 2)  # 2 bytes per sample for 16-bit
        
        # Fill the buffer with a sine wave
        for i in range(num_samples):
            t = i / sample_rate
            value = int(32767 * math.sin(2 * math.pi * frequency * t))
            # Convert to 16-bit little-endian
            buf[i*2] = value & 0xFF
            buf[i*2+1] = (value >> 8) & 0xFF
        
        # Create a Sound object from the buffer
        return pygame.mixer.Sound(buffer=bytes(buf))
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        # Check if game is muted (access through the game instance)
        if hasattr(self, 'game') and self.game.sound_muted:
            return  # Don't play sounds if muted
        
        if sound_name in self.sounds:
            # Add variation to movement sounds
            if sound_name == "move":
                # Use a click sound instead of footstep
                # Slightly vary the pitch for more natural effect
                pitch_variation = random.uniform(0.95, 1.05)  # Less variation for clicks
                volume_variation = random.uniform(0.4, 0.6)   # Quieter for clicks
                
                # Set a lower volume for movement clicks
                self.sounds[sound_name].set_volume(volume_variation)
                
                # Play with a shorter duration for a crisp click
                self.sounds[sound_name].play(maxtime=int(100 * pitch_variation))
            else:
                self.sounds[sound_name].play()
    
    def play_music(self, music_name, loop=True):
        if music_name in self.music_tracks:
            # Stop current music if playing
            self.music_channel.stop()
            
            # Play new music
            self.music_channel.play(self.music_tracks[music_name], -1 if loop else 0)
            self.current_music = music_name
    
    def play_ambient(self, ambient_name, loop=True):
        if ambient_name in self.music_tracks:
            # Stop current ambient if playing
            self.ambient_channel.stop()
            
            # Play new ambient
            self.ambient_channel.play(self.music_tracks[ambient_name], -1 if loop else 0)
            self.current_ambient = ambient_name
    
    def stop_music(self):
        self.music_channel.stop()
        self.current_music = None
    
    def stop_ambient(self):
        self.ambient_channel.stop()
        self.current_ambient = None
    
    def stop_all(self):
        self.effect_channel.stop()
        self.ambient_channel.stop()
        self.music_channel.stop()
        self.current_music = None
        self.current_ambient = None
    
    def set_music_volume(self, volume):
        """Set the volume for background music (0.0 to 1.0)"""
        pygame.mixer.music.set_volume(volume)
    
    def set_effect_volume(self, volume):
        """Set the volume for sound effects (0.0 to 1.0)"""
        for sound in self.sounds.values():
            sound.set_volume(volume)
    
    def set_ambient_volume(self, volume):
        """Set the volume for ambient sounds (0.0 to 1.0)"""
        # If you have separate ambient sounds, adjust their volume here
        pass  # This can be empty if ambient sounds are handled through pygame.mixer.music
    
    def play_theme_music(self, theme_name):
        # Play appropriate music based on theme
        if theme_name == "dungeon":
            self.play_ambient("dungeon_ambient")
            self.play_music("dungeon_music")
        elif theme_name == "forest":
            self.play_ambient("forest_ambient")
            self.play_music("forest_music")
        elif theme_name == "space":
            self.play_ambient("space_ambient")
            self.play_music("space_music")
    
    def play_tension_music(self):
        # Play tension music when near enemies or exit
        if "tension" in self.music_tracks:
            self.play_music("tension", loop=False)
    
    def play_victory_music(self):
        # Play victory music when level is completed
        if "victory_music" in self.music_tracks:
            self.play_music("victory_music", loop=False)
    
    def play_menu_music(self):
        # Play menu music
        if "menu_music" in self.music_tracks:
            self.play_music("menu_music")
            self.stop_ambient()
    
    def adjust_music_by_distance(self, distance, max_distance):
        # Adjust music volume based on distance to exit or enemy
        # Used to create tension as player gets closer to goal or danger
        if distance <= max_distance:
            # Calculate ratio (0 = close, 1 = far)
            ratio = distance / max_distance
            
            # Adjust volumes
            tension_vol = self.music_volume * (1 - ratio)
            normal_vol = self.music_volume * ratio
            
            # Apply volume changes
            if self.current_music and "tension" in self.music_tracks:
                self.music_tracks[self.current_music].set_volume(normal_vol)
                self.music_tracks["tension"].set_volume(tension_vol)
                
                # Play tension music if not already playing
                if not self.music_channel.get_busy() or self.current_music != "tension":
                    self.play_music("tension", loop=True)
    
    def set_sound_volume(self, volume):
        """Set the volume for all sound effects (0.0 to 1.0)"""
        for sound in self.sounds.values():
            sound.set_volume(volume) 