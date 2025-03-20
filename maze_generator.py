import random
import numpy as np

class MazeGenerator:
    def __init__(self, width, height):
        # Ensure width and height are odd numbers to have proper walls
        self.width = width if width % 2 == 1 else width + 1
        self.height = height if height % 2 == 1 else height + 1
        self.maze = np.ones((self.height, self.width), dtype=int)  # 1 represents walls
        self.exit_x = 0
        self.exit_y = 0
        self.key_positions = []
        self.door_position = None
        self.stair_positions = []
        self.enemy_positions = []
        self.trap_positions = []
    
    def generate_maze(self, keys_required=0, num_enemies=0, num_traps=0, num_floors=1, current_floor=1, complexity=0.75, density=0.75, start_pos=None, min_exit_distance=None):
        """
        Generate a maze using a randomized algorithm.
        Ensures the maze is solvable by validating paths.
        
        Parameters:
        complexity: Complexity of the maze (0-1)
        density: Density of the maze (0-1)
        start_pos: Optional tuple (x, y) for the starting position
        min_exit_distance: Minimum Manhattan distance from start to exit
        
        Returns:
        maze: 2D numpy array where 0 represents paths and 1 represents walls
        start_pos: Tuple (x, y) of the starting position
        exit_pos: Tuple (x, y) of the exit position
        """
        # Adjust complexity and density relative to maze size
        complexity = int(complexity * (5 * (self.height + self.width)))
        density = int(density * ((self.height // 2) * (self.width // 2)))
        
        # Create an array of ones (walls)
        self.maze = np.ones((self.height, self.width), dtype=int)
        
        # Fill borders with ones (walls)
        self.maze[0, :] = self.maze[-1, :] = self.maze[:, 0] = self.maze[:, -1] = 1
        
        # Set a default minimum exit distance if not provided
        if min_exit_distance is None:
            min_exit_distance = max(self.width, self.height) // 2
        
        # Generate random starting position if not provided
        if start_pos is None:
            # Make sure starting position is on an odd cell (path)
            start_x = np.random.randint(1, self.width // 2) * 2 - 1
            start_y = np.random.randint(1, self.height // 2) * 2 - 1
            start_pos = (start_x, start_y)
        else:
            # Ensure start_pos is a tuple with two elements
            if not isinstance(start_pos, tuple) or len(start_pos) != 2:
                print("Warning: Invalid start_pos provided. Using default.")
                start_x = np.random.randint(1, self.width // 2) * 2 - 1
                start_y = np.random.randint(1, self.height // 2) * 2 - 1
                start_pos = (start_x, start_y)
            else:
                start_x, start_y = start_pos
        
        # Make sure the starting position is a path
        self.maze[start_y, start_x] = 0
        
        # Create paths by randomly removing walls
        for _ in range(density):
            x = np.random.randint(0, self.width // 2) * 2
            y = np.random.randint(0, self.height // 2) * 2
            self.maze[y, x] = 0
            
            for _ in range(complexity):
                directions = []
                if x > 1:
                    directions.append((x - 2, y))
                if x < self.width - 2:
                    directions.append((x + 2, y))
                if y > 1:
                    directions.append((x, y - 2))
                if y < self.height - 2:
                    directions.append((x, y + 2))
                
                if len(directions) > 0:
                    next_x, next_y = directions[np.random.randint(0, len(directions))]
                    if self.maze[next_y, next_x] == 1:
                        self.maze[next_y, next_x] = 0
                        self.maze[y + (next_y - y) // 2, x + (next_x - x) // 2] = 0
                        x, y = next_x, next_y
        
        # Reset positions
        self.key_positions = []
        self.door_position = None
        self.stair_positions = []
        self.enemy_positions = []
        self.trap_positions = []
        
        # Find valid positions for the exit (open spaces)
        valid_positions = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.maze[y, x] == 0:
                    # Calculate Manhattan distance from start
                    distance = abs(x - start_x) + abs(y - start_y)
                    # Only consider positions that are far enough from start
                    if distance >= min_exit_distance:
                        valid_positions.append((x, y, distance))
        
        # If no valid positions found with minimum distance, relax the constraint
        if not valid_positions:
            print("Warning: No positions meet the minimum distance requirement. Relaxing constraint.")
            for y in range(1, self.height - 1):
                for x in range(1, self.width - 1):
                    if self.maze[y, x] == 0 and (x != start_x or y != start_y):
                        valid_positions.append((x, y, abs(x - start_x) + abs(y - start_y)))
        
        # Initialize exit_pos with a default value
        exit_pos = None
        
        # Sort by distance (descending) and pick one of the furthest positions
        if valid_positions:
            valid_positions.sort(key=lambda pos: pos[2], reverse=True)
            # Choose randomly from the top 25% furthest positions
            top_count = max(1, len(valid_positions) // 4)
            top_positions = valid_positions[:top_count]
            idx = np.random.randint(0, len(top_positions))
            exit_x, exit_y, _ = top_positions[idx]
            exit_pos = (exit_x, exit_y)
        else:
            # Fallback: just pick a random position that's not the start
            print("Warning: No valid exit positions found. Using fallback method.")
            attempts = 0
            while attempts < 100:  # Prevent infinite loop
                exit_x = np.random.randint(1, self.width - 1)
                exit_y = np.random.randint(1, self.height - 1)
                if self.maze[exit_y, exit_x] == 0 and (exit_x != start_x or exit_y != start_y):
                    exit_pos = (exit_x, exit_y)
                    break
                attempts += 1
            
            if attempts >= 100 or exit_pos is None:
                # Last resort: find any open cell
                for y in range(1, self.height - 1):
                    for x in range(1, self.width - 1):
                        if self.maze[y, x] == 0 and (x != start_x or y != start_y):
                            exit_pos = (x, y)
                            break
                    if exit_pos is not None:
                        break
                
                # If still no exit position, create one
                if exit_pos is None:
                    exit_x = self.width - 2
                    exit_y = self.height - 2
                    self.maze[exit_y, exit_x] = 0
                    exit_pos = (exit_x, exit_y)
        
        # Store exit position
        self.exit_x, self.exit_y = exit_pos
        
        # Place keys if required
        if keys_required > 0:
            self._place_keys(keys_required)
            # Place a locked door before the exit
            self._place_door()
        
        # Place stairs if this is a multi-floor maze and not the last floor
        if num_floors > 1 and current_floor < num_floors:
            self._place_stairs()
        
        # Place enemies
        if num_enemies > 0:
            self._place_enemies(num_enemies)
        
        # Place traps
        if num_traps > 0:
            self._place_traps(num_traps)
        
        # Add some random paths to make the maze less rigid
        self._add_random_paths()
        
        # After placing all elements (keys, doors, enemies, traps, etc.)
        # Verify that the maze is solvable
        attempts = 0
        max_attempts = 5  # Maximum number of attempts to generate a solvable maze
        
        while not self._is_maze_solvable() and attempts < max_attempts:
            print(f"Generated maze is not solvable. Regenerating (attempt {attempts+1}/{max_attempts})...")
            
            # Regenerate the maze
            self.maze = np.ones((self.height, self.width), dtype=int)
            self.maze[0, :] = self.maze[-1, :] = self.maze[:, 0] = self.maze[:, -1] = 1
            
            # Make sure the starting position is a path
            self.maze[start_y, start_x] = 0
            
            # Create paths by randomly removing walls
            for _ in range(density):
                x = np.random.randint(0, self.width // 2) * 2
                y = np.random.randint(0, self.height // 2) * 2
                self.maze[y, x] = 0
                
                for _ in range(complexity):
                    directions = []
                    if x > 1:
                        directions.append((x - 2, y))
                    if x < self.width - 2:
                        directions.append((x + 2, y))
                    if y > 1:
                        directions.append((x, y - 2))
                    if y < self.height - 2:
                        directions.append((x, y + 2))
                    
                    if len(directions) > 0:
                        next_x, next_y = directions[np.random.randint(0, len(directions))]
                        if self.maze[next_y, next_x] == 1:
                            self.maze[next_y, next_x] = 0
                            self.maze[y + (next_y - y) // 2, x + (next_x - x) // 2] = 0
                            x, y = next_x, next_y
            
            # Reset positions
            self.key_positions = []
            self.door_position = None
            self.stair_positions = []
            self.enemy_positions = []
            self.trap_positions = []
            
            # Find valid positions for the exit
            valid_positions = []
            for y in range(1, self.height - 1):
                for x in range(1, self.width - 1):
                    if self.maze[y, x] == 0:
                        # Calculate Manhattan distance from start
                        distance = abs(x - start_x) + abs(y - start_y)
                        # Only consider positions that are far enough from start
                        if distance >= min_exit_distance:
                            valid_positions.append((x, y, distance))
            
            # ... rest of exit position selection code ...
            
            # Place keys, doors, stairs, enemies, and traps
            if keys_required > 0:
                self._place_keys(keys_required)
                self._place_door()
            
            if num_floors > 1 and current_floor < num_floors:
                self._place_stairs()
            
            if num_enemies > 0:
                self._place_enemies(num_enemies)
            
            if num_traps > 0:
                self._place_traps(num_traps)
            
            self._add_random_paths()
            
            attempts += 1
        
        if attempts >= max_attempts and not self._is_maze_solvable():
            print("Failed to generate a solvable maze after maximum attempts. Creating a simple solvable maze.")
            self._create_simple_solvable_maze(start_pos, min_exit_distance, keys_required)
        
        return self.maze, start_pos, (self.exit_x, self.exit_y)
    
    def _carve_paths(self, x, y):
        # Directions: right, down, left, up
        directions = [(2, 0), (0, 2), (-2, 0), (0, -2)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            
            # Check if the new position is within bounds and is a wall
            if (0 < new_x < self.width - 1 and 
                0 < new_y < self.height - 1 and 
                self.maze[new_y][new_x] == 1):
                
                # Carve a path by setting the cells to 0
                self.maze[y + dy // 2][x + dx // 2] = 0
                self.maze[new_y][new_x] = 0
                
                # Continue carving paths from the new position
                self._carve_paths(new_x, new_y)
    
    def _add_random_paths(self):
        # Add some random paths to make the maze less rigid
        # This creates more path options and makes the maze more interesting
        
        # Number of random paths to add (based on maze size)
        num_paths = (self.width * self.height) // 30  # Increased from 40 to 30 for more paths
        
        for _ in range(num_paths):
            # Pick a random wall that's not on the border
            while True:
                x = random.randint(1, self.width - 2)
                y = random.randint(1, self.height - 2)
                
                # Only consider walls
                if self.maze[y][x] == 1:
                    # Count adjacent paths
                    adjacent_paths = 0
                    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        if 0 <= x + dx < self.width and 0 <= y + dy < self.height:
                            if self.maze[y + dy][x + dx] == 0:
                                adjacent_paths += 1
                    
                    # Only remove walls that connect exactly two paths
                    # This prevents creating large open areas
                    if adjacent_paths == 2:
                        self.maze[y][x] = 0
                        break
    
    def _place_keys(self, num_keys):
        # Find possible key positions (path cells away from entrance and exit)
        possible_positions = []
        
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.maze[y][x] == 0:
                    # Make sure it's not too close to the entrance
                    distance_from_start = abs(x - 0) + abs(y - 1)
                    if distance_from_start > 5:  # At least 5 cells away from start
                        possible_positions.append((x, y))
        
        # Place keys
        for _ in range(min(num_keys, len(possible_positions))):
            if possible_positions:
                pos = random.choice(possible_positions)
                self.key_positions.append(pos)
                possible_positions.remove(pos)
    
    def _place_door(self):
        # Place a door near the exit
        possible_door_positions = []
        
        # Find path cells that are close to where the exit might be
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.maze[y][x] == 0:
                    # Check if it's in the far half of the maze
                    if x > self.width // 2 and y > self.height // 4:
                        # Make sure it's not a key position
                        if (x, y) not in self.key_positions:
                            possible_door_positions.append((x, y))
        
        if possible_door_positions:
            self.door_position = random.choice(possible_door_positions)
    
    def _place_stairs(self):
        # Find possible stair positions (path cells away from entrance, keys, and door)
        possible_positions = []
        
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.maze[y][x] == 0:
                    # Make sure it's not too close to the entrance
                    distance_from_start = abs(x - 0) + abs(y - 1)
                    if distance_from_start > 5:  # At least 5 cells away from start
                        # Check it's not a key or door position
                        if (x, y) not in self.key_positions and (x, y) != self.door_position:
                            possible_positions.append((x, y))
        
        # Place stairs
        if possible_positions:
            stair_pos = random.choice(possible_positions)
            self.stair_positions.append(stair_pos)
    
    def _place_enemies(self, num_enemies):
        # Find possible enemy positions (path cells away from entrance, keys, door, and stairs)
        possible_positions = []
        
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.maze[y][x] == 0:
                    # Make sure it's not too close to the entrance
                    distance_from_start = abs(x - 0) + abs(y - 1)
                    if distance_from_start > 3:  # At least 3 cells away from start
                        # Check it's not a key, door, stair, or exit position
                        if ((x, y) not in self.key_positions and 
                            (x, y) != self.door_position and 
                            (x, y) not in self.stair_positions and
                            (x, y) != (self.exit_x, self.exit_y)):
                            possible_positions.append((x, y))
        
        # Place enemies
        for _ in range(min(num_enemies, len(possible_positions))):
            if possible_positions:
                pos = random.choice(possible_positions)
                self.enemy_positions.append(pos)
                possible_positions.remove(pos)
    
    def _place_traps(self, num_traps):
        # Find possible trap positions (path cells away from entrance, keys, door, stairs, and enemies)
        possible_positions = []
        
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.maze[y][x] == 0:
                    # Make sure it's not too close to the entrance
                    distance_from_start = abs(x - 0) + abs(y - 1)
                    if distance_from_start > 3:  # At least 3 cells away from start
                        # Check it's not a key, door, stair, enemy, or exit position
                        if ((x, y) not in self.key_positions and 
                            (x, y) != self.door_position and 
                            (x, y) not in self.stair_positions and
                            (x, y) not in self.enemy_positions and
                            (x, y) != (self.exit_x, self.exit_y)):
                            possible_positions.append((x, y))
        
        # Place traps
        for _ in range(min(num_traps, len(possible_positions))):
            if possible_positions:
                pos = random.choice(possible_positions)
                trap_type = random.choice(["spike", "fire"])
                self.trap_positions.append((pos[0], pos[1], trap_type))
                possible_positions.remove(pos)
    
    def get_start_position(self):
        return (0, 1)  # x, y coordinates
    
    def get_exit_position(self):
        return (self.exit_x, self.exit_y)  # x, y coordinates
    
    def get_key_positions(self):
        return self.key_positions
    
    def get_door_position(self):
        return self.door_position
    
    def get_stair_positions(self):
        return self.stair_positions
    
    def get_enemy_positions(self):
        return self.enemy_positions
    
    def get_trap_positions(self):
        return self.trap_positions
    
    def _is_maze_solvable(self):
        """
        Check if the maze is solvable using breadth-first search.
        Accounts for keys, doors, and multiple floors.
        """
        from collections import deque
        
        # Start position
        start_x, start_y = self.start_pos if hasattr(self, 'start_pos') else (1, 1)
        
        # If there's a door, we need to check if all keys are reachable and then if the exit is reachable
        if self.door_position is not None and self.key_positions:
            # First, check if all keys are reachable from the start
            keys_reachable = set()
            
            # For each key, check if it's reachable
            for key_pos in self.key_positions:
                # Create a visited set
                visited = set()
                queue = deque([(start_x, start_y)])
                
                while queue:
                    x, y = queue.popleft()
                    
                    if (x, y) == key_pos:
                        keys_reachable.add(key_pos)
                        break
                    
                    if (x, y) in visited:
                        continue
                    
                    visited.add((x, y))
                    
                    # Check all four directions
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        
                        # Check if the new position is valid
                        if (0 <= nx < self.width and 0 <= ny < self.height and 
                            self.maze[ny, nx] == 0 and (nx, ny) not in visited):
                            queue.append((nx, ny))
            
            # If not all keys are reachable, the maze is not solvable
            if len(keys_reachable) < len(self.key_positions):
                return False
            
            # Now check if the door is reachable from the start
            visited = set()
            queue = deque([(start_x, start_y)])
            door_reachable = False
            
            while queue:
                x, y = queue.popleft()
                
                if (x, y) == self.door_position:
                    door_reachable = True
                    break
                
                if (x, y) in visited:
                    continue
                
                visited.add((x, y))
                
                # Check all four directions
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    
                    # Check if the new position is valid
                    if (0 <= nx < self.width and 0 <= ny < self.height and 
                        self.maze[ny, nx] == 0 and (nx, ny) not in visited):
                        queue.append((nx, ny))
            
            # If the door is not reachable, the maze is not solvable
            if not door_reachable:
                return False
            
            # Finally, check if the exit is reachable from the door
            visited = set()
            queue = deque([self.door_position])
            
            while queue:
                x, y = queue.popleft()
                
                if (x, y) == (self.exit_x, self.exit_y):
                    return True
                
                if (x, y) in visited:
                    continue
                
                visited.add((x, y))
                
                # Check all four directions
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    
                    # Check if the new position is valid
                    if (0 <= nx < self.width and 0 <= ny < self.height and 
                        self.maze[ny, nx] == 0 and (nx, ny) not in visited):
                        queue.append((nx, ny))
            
            # If we get here, the exit is not reachable from the door
            return False
        
        # If there's no door, just check if the exit is reachable from the start
        else:
            # Create a visited set
            visited = set()
            queue = deque([(start_x, start_y)])
            
            while queue:
                x, y = queue.popleft()
                
                if (x, y) == (self.exit_x, self.exit_y):
                    return True
                
                if (x, y) in visited:
                    continue
                
                visited.add((x, y))
                
                # Check all four directions
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    
                    # Check if the new position is valid
                    if (0 <= nx < self.width and 0 <= ny < self.height and 
                        self.maze[ny, nx] == 0 and (nx, ny) not in visited):
                        queue.append((nx, ny))
            
            # If we get here, the exit is not reachable
            return False
    
    def _create_simple_solvable_maze(self, start_pos, min_exit_distance, keys_required):
        """
        Create a simple maze that is guaranteed to be solvable.
        Used as a fallback when normal generation fails.
        """
        # Reset the maze to all walls
        self.maze = np.ones((self.height, self.width), dtype=int)
        self.maze[0, :] = self.maze[-1, :] = self.maze[:, 0] = self.maze[:, -1] = 1
        
        # Extract start position
        start_x, start_y = start_pos
        
        # Create a path from start to a distant point for the exit
        exit_x = self.width - 2
        exit_y = self.height - 2
        
        # Ensure minimum distance
        if min_exit_distance is not None:
            while abs(exit_x - start_x) + abs(exit_y - start_y) < min_exit_distance:
                if exit_x > start_x + min_exit_distance // 2:
                    exit_x = start_x + min_exit_distance // 2
                if exit_y > start_y + min_exit_distance // 2:
                    exit_y = start_y + min_exit_distance // 2
        
        # Create a direct path from start to exit
        x, y = start_x, start_y
        self.maze[y, x] = 0  # Start position
        
        # If keys are required, create paths to key positions first
        self.key_positions = []
        if keys_required > 0:
            # Place keys along the path
            key_spacing = min(self.width, self.height) // (keys_required + 2)
            
            for i in range(keys_required):
                # Move horizontally then vertically to create a path
                key_x = start_x + (i + 1) * key_spacing
                key_y = start_y + (i + 1) * key_spacing
                
                # Ensure key is within bounds
                key_x = min(key_x, self.width - 2)
                key_y = min(key_y, self.height - 2)
                
                # Create path to key
                while x < key_x:
                    x += 1
                    self.maze[y, x] = 0
                while x > key_x:
                    x -= 1
                    self.maze[y, x] = 0
                while y < key_y:
                    y += 1
                    self.maze[y, x] = 0
                while y > key_y:
                    y -= 1
                    self.maze[y, x] = 0
                
                # Add key position
                self.key_positions.append((key_x, key_y))
            
            # Place door before exit
            door_x = (exit_x + x) // 2
            door_y = (exit_y + y) // 2
            self.door_position = (door_x, door_y)
            
            # Create path to door
            while x < door_x:
                x += 1
                self.maze[y, x] = 0
            while x > door_x:
                x -= 1
                self.maze[y, x] = 0
            while y < door_y:
                y += 1
                self.maze[y, x] = 0
            while y > door_y:
                y -= 1
                self.maze[y, x] = 0
        
        # Create path to exit
        while x < exit_x:
            x += 1
            self.maze[y, x] = 0
        while x > exit_x:
            x -= 1
            self.maze[y, x] = 0
        while y < exit_y:
            y += 1
            self.maze[y, x] = 0
        while y > exit_y:
            y -= 1
            self.maze[y, x] = 0
        
        # Set exit position
        self.exit_x, self.exit_y = exit_x, exit_y
        
        # Add some random paths to make it less obvious
        self._add_random_paths(extra_paths=True) 