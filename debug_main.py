import traceback
from game import MazeGame

if __name__ == "__main__":
    try:
        print("Starting Maze Runner game...")
        game = MazeGame()
        print("MazeGame instance created successfully.")
        game.run()
        print("Game run completed.")
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        print("Game crashed. See error above.") 