from game import Player

class DumbHumanPlayer(Player):
    """A more realistic human player implementation that doesn't see all legal moves."""

    def choose_move(self, game_state):
        """
        Prompt human player to try moves until they find a valid one or give up.

        Args:
            game_state (dict): Dictionary containing game state information
                - legal_moves (list): List of legal moves (hidden from player)
                - board (Board): Current state of the game board
                - tile_distribution (dict): Original distribution of tiles

        Returns:
            int: Index of chosen move (if found in legal_moves) or 0 to end game
        """
        legal_moves = game_state['legal_moves']

        while True:
            print(f"\n{self.name}'s turn. Your rack: {self.rack}")
            print(game_state['board'])
            print("What would you like to do?")
            print("1. Try to play a word")
            print("2. Give up (end game)")

            try:
                choice = input("Enter your choice (1 or 2): ").strip()

                if choice == "2":
                    print(f"{self.name} gives up.")
                    return 0

                if choice == "1":
                    # Get word from player
                    word = input("Enter the word you want to play: ").strip().lower()

                    # Get position
                    try:
                        row = int(input("Enter row number (0-14): "))
                        col = int(input("Enter column number (0-14): "))
                        if not (0 <= row <= 14 and 0 <= col <= 14):
                            print("Position must be between 0 and 14.")
                            continue
                    except ValueError:
                        print("Please enter valid numbers for position.")
                        continue

                    # Get direction
                    direction = input("Enter direction (across/down): ").strip().lower()
                    if direction not in ['across', 'down']:
                        print("Direction must be 'across' or 'down'.")
                        continue

                    # Check if move exists in legal moves
                    for i, move in enumerate(legal_moves, 1):
                        legal_word, legal_pos, legal_dir, _, _ = move
                        if (word == legal_word and
                                (row, col) == legal_pos and
                                direction == legal_dir):
                            print(f"Valid move! Playing '{word}' at position ({row}, {col}) {direction}")
                            return i

                    print("\nThat move is not valid. Reasons could be:")
                    print("- The word doesn't exist in the dictionary")
                    print("- You don't have the required letters")
                    print("- The word doesn't connect with existing tiles properly")
                    print("- The position creates invalid words")
                    continue

                print("Please enter 1 or 2.")

            except ValueError:
                print("Invalid input. Please try again.")