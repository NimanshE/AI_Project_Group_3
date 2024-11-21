import random
from letter_tree import build_tree_from_file
from board import Board
from itertools import permutations


class Player:
    """Base class for players, to be extended for human or AI players."""

    def __init__(self, name):
        self.name = name
        self.rack = []
        self.score = 0

    def choose_move(self, game_state):
        """
        Method to be overridden by subclasses.

        Args:
            game_state (dict): Dictionary containing:
                - legal_moves (list): List of legal moves for the player
                - board (Board): Current state of the game board
                - tile_distribution (dict): Original distribution of tiles in the bag

        Returns:
            int: Index of chosen move or 0 to end game
        """
        raise NotImplementedError("Subclasses must implement choose_move method")


class HumanPlayer(Player):
    """Human player implementation."""

    def choose_move(self, game_state):
        """
        Prompt human player to choose a move from the list of legal moves.

        Args:
            game_state (dict): Dictionary containing game state information
                - legal_moves (list): List of legal moves
                - board (Board): Current state of the game board
                - tile_distribution (dict): Original distribution of tiles

        Returns:
            int: Index of chosen move or 0 to end game
        """
        legal_moves = game_state['legal_moves']
        print(f"\n{self.name}'s turn. Current rack: {self.rack}")
        print("Legal moves:")
        for i, move in enumerate(legal_moves, 1):
            print(f"{i}. {move[0]} at {move[1]} ({move[2]}) - Score: {move[4]}")
        print("0. End game")

        while True:
            try:
                choice = int(input("Choose a move (number): "))
                if choice == 0 or (1 <= choice <= len(legal_moves)):
                    return choice
                print("Invalid choice. Try again.")
            except ValueError:
                print("Please enter a number.")


class GreedyAIPlayer(Player):
    """AI player that always chooses the highest-scoring legal move available."""

    def choose_move(self, game_state):
        """
        Select the move with the highest score from the list of legal moves.

        Args:
            game_state (dict): Dictionary containing:
                - legal_moves (list): List of legal moves
                - board (Board): Current state of the game board
                - tile_distribution (dict): Original distribution of tiles

        Returns:
            int: Index of chosen move or 0 if no moves available
        """
        legal_moves = game_state['legal_moves']

        # If no legal moves are available, end turn
        if not legal_moves:
            return 0

        # Find move with highest score
        best_move_index = 1  # Initialize to first move
        best_score = legal_moves[0][4]  # Score is the fifth element in move tuple

        for i, move in enumerate(legal_moves[1:], 2):
            current_score = move[4]
            if current_score > best_score:
                best_score = current_score
                best_move_index = i

        # Print the chosen move for transparency
        chosen_move = legal_moves[best_move_index - 1]
        print(f"{self.name} chooses to play '{chosen_move[0]}' at {chosen_move[1]} "
              f"({chosen_move[2]}) for {chosen_move[4]} points")

        return best_move_index


class ScrabbleBag:
    """Represents the bag of tiles in a Scrabble game."""

    # Tile distribution for standard Scrabble (letter: count)
    TILE_DISTRIBUTION = {
        'a': 9, 'b': 2, 'c': 2, 'd': 4, 'e': 12, 'f': 2, 'g': 3, 'h': 2,
        'i': 9, 'j': 1, 'k': 1, 'l': 4, 'm': 2, 'n': 6, 'o': 8, 'p': 2,
        'q': 1, 'r': 6, 's': 4, 't': 6, 'u': 4, 'v': 2, 'w': 2, 'x': 1,
        'y': 2, 'z': 1
    }

    def __init__(self):
        """Initialize the bag with all tiles."""
        self.tiles = []
        for letter, count in self.TILE_DISTRIBUTION.items():
            self.tiles.extend([letter] * count)
        random.shuffle(self.tiles)

    def draw_tiles(self, num_tiles):
        """
        Draw specified number of tiles from the bag.

        Args:
            num_tiles (int): Number of tiles to draw

        Returns:
            list: Drawn tiles, or fewer if bag is depleted
        """
        drawn_tiles = self.tiles[:num_tiles]
        del self.tiles[:num_tiles]
        return drawn_tiles

    def is_empty(self):
        """Check if bag is empty."""
        return len(self.tiles) == 0


class ScrabbleGame:
    """Main game class to control game flow."""

    def __init__(self, player1, player2):
        """
        Initialize the game.

        Args:
            player1_name (str): Name of first player
            player2_name (str): Name of second player
        """

        # Validate input types
        if not isinstance(player1, Player) or not isinstance(player2, Player):
            raise TypeError("Players must be instances of Player class or its subclasses")

        # Initialize board and lexicon
        self.board = Board(15)
        self.lexicon_tree = build_tree_from_file(file_name="lexicon/lexicon_full.txt")

        # Initialize bag and players
        self.bag = ScrabbleBag()
        self.players = [player1, player2]

        # Fill initial racks
        for player in self.players:
            player.rack = self.bag.draw_tiles(7)

        # Randomly choose starting player
        self.current_player_idx = random.randint(0, 1)

        # Add tracker for consecutive skipped turns
        self.consecutive_skips = 0

    def start_game(self):
        """
        Start and play the game.

        Returns:
            tuple: Final scores of both players (player1_score, player2_score)
        """
        # First move must be played on center tile at (7,7)
        starting_player = self.players[self.current_player_idx]
        print(f"{starting_player.name} starts the game!")

        # Try to find a valid first word
        valid_first_move = self._find_first_move(starting_player)

        if not valid_first_move:
            print("No valid first move found. Ending game.")
            return self._end_game()

        # Continue game until a player chooses to end
        while True:
            current_player = self.players[self.current_player_idx]

            # Find legal moves
            solver = self._get_legal_moves(current_player)
            legal_moves = solver.found_moves

            if not legal_moves:
                print(f"No moves available for {current_player.name}. Skipping turn.")
                self.consecutive_skips += 1

                # If both players have been skipped consecutively, end the game
                if self.consecutive_skips >= 2:
                    print("\nNeither player has any available moves. Game ending.")
                    return self._end_game()

                self._switch_player()
                continue

            # Reset consecutive skips counter since we found legal moves
            self.consecutive_skips = 0

            # Create game state dictionary
            game_state = {
                'legal_moves': legal_moves,
                'board': self.board,
                'tile_distribution': ScrabbleBag.TILE_DISTRIBUTION,
                'lexicon_tree': self.lexicon_tree
            }

            # Ask player to choose move
            move_choice = current_player.choose_move(game_state)

            # Check if game is ending
            if move_choice == 0:
                return self._end_game()

            # Execute chosen move
            chosen_move = legal_moves[move_choice - 1]
            self._execute_move(current_player, chosen_move)

            # Switch to next player
            self._switch_player()

    def _find_first_move(self, player):
        """
        Find a valid first move for the starting player by brute force searching the lexicon tree.

        Args:
            player (Player): Starting player

        Returns:
            bool: True if a first move was successfully played, False otherwise
        """
        # Generate all possible word combinations from the player's rack
        rack = player.rack
        for length in range(1, len(rack) + 1):
            for perm in permutations(rack, length):
                word = ''.join(perm)
                if self.lexicon_tree.is_word(word):
                    # Play the first valid word found
                    first_move = (word, (7, 7), 'across', rack, 0)
                    self._execute_move(player, first_move)
                    return True

        return False

    def _get_legal_moves(self, player):
        """
        Get legal moves for a player.

        Args:
            player (Player): Current player

        Returns:
            SolveState: Solver with found legal moves
        """
        from solver import SolveState
        solver = SolveState(self.lexicon_tree, self.board, player.rack.copy())
        solver.find_all_options()
        return solver

    def _execute_move(self, player, move):
        """
        Execute a player's move.

        Args:
            player (Player): Player making the move
            move (tuple): Move details (word, pos, direction, original_rack, score)
        """
        word, pos, direction, original_rack, score = move

        # Place word on board
        remaining_rack = player.rack.copy()
        result_score, remaining_rack = self.board.place_word(
            word, pos, direction, player.rack
        )

        # Update player's score and rack
        player.score += result_score
        player.rack = remaining_rack

        # Refill rack from bag
        tiles_to_draw = 7 - len(player.rack)
        if tiles_to_draw > 0 and not self.bag.is_empty():
            new_tiles = self.bag.draw_tiles(tiles_to_draw)
            player.rack.extend(new_tiles)

        print(f"{player.name} plays '{word}' at {pos} {direction} for {result_score} points!")

    def _switch_player(self):
        """Switch to the other player."""
        self.current_player_idx = 1 - self.current_player_idx

    def _end_game(self):
        """
        End the game and display final scores.

        Returns:
            tuple: Final scores of both players (player1_score, player2_score)
        """
        print("\n--- GAME OVER ---")
        print(f"Final Board:")
        print(self.board)
        self.board.visualize("assets/game_output.png")

        print("\nFinal Scores:")
        for player in self.players:
            print(f"{player.name}: {player.score} points")

        # Determine winner
        winner = max(self.players, key=lambda p: p.score)
        print(f"\n{winner.name} wins!")

        # Return tuple of scores in player order (player1, player2)
        return self.players[0].score, self.players[1].score


# Run the game if script is executed directly
if __name__ == '__main__':
    # Create player instances
    human_player = HumanPlayer("Human Player")
    ai_player = GreedyAIPlayer("Greedy AI")

    game = ScrabbleGame(human_player, ai_player)
    game.start_game()