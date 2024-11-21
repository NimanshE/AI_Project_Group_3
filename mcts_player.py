from game import Player
from solver import SolveState
from collections import defaultdict
import random


class MCTSPlayer(Player):
    """AI player using 2-ply Monte Carlo Tree Search to evaluate moves."""

    def __init__(self, name, num_simulations=50):
        """
        Initialize MCTS player.

        Args:
            name (str): Player name
            num_simulations (int): Number of Monte Carlo simulations per move
        """
        super().__init__(name)
        self.num_simulations = num_simulations

    def _simulate_opponent_rack(self, game_state, my_used_tiles):
        """
        Generate a probable opponent rack based on remaining tiles.

        Args:
            game_state (dict): Current game state
            my_used_tiles (list): Tiles we're planning to use in our move

        Returns:
            list: Simulated opponent rack
        """
        # Get original tile distribution
        tile_dist = game_state['tile_distribution'].copy()

        # Remove tiles that are on the board
        board = game_state['board']
        for pos in board.all_positions():
            tile = board.get_tile(pos)
            if tile and tile in tile_dist and tile_dist[tile] > 0:
                tile_dist[tile] -= 1

        # Remove tiles that are in our rack
        for tile in self.rack:
            if tile in tile_dist and tile_dist[tile] > 0:
                tile_dist[tile] -= 1

        # Remove tiles we're planning to use
        for tile in my_used_tiles:
            if tile in tile_dist and tile_dist[tile] > 0:
                tile_dist[tile] -= 1

        # Convert remaining distribution to list of tiles
        remaining_tiles = []
        for tile, count in tile_dist.items():
            remaining_tiles.extend([tile] * count)

        # Randomly select 7 tiles (or fewer if not enough remain)
        num_tiles = min(7, len(remaining_tiles))
        return random.sample(remaining_tiles, num_tiles) if remaining_tiles else []

    def _evaluate_move_sequence(self, game_state, my_move, opponent_rack):
        """
        Evaluate a move sequence (our move + opponent's response).

        Args:
            game_state (dict): Current game state
            my_move (tuple): Our planned move (word, pos, direction, rack_used, score)
            opponent_rack (list): Simulated opponent rack

        Returns:
            float: Net score advantage of this move sequence
        """
        # Create a copy of the board to simulate moves
        test_board = game_state['board'].copy()

        # Apply our move
        word, pos, direction, rack_used, my_score = my_move
        test_board.place_word(word, pos, direction, self.rack.copy())

        # Find opponent's best response with their simulated rack
        opponent_solver = SolveState(game_state['lexicon_tree'], test_board, opponent_rack)
        opponent_solver.find_all_options()

        # If opponent has no moves, they score 0
        if not opponent_solver.found_moves:
            return my_score

        # Find opponent's highest scoring response
        opponent_best_score = max(move[4] for move in opponent_solver.found_moves)

        # Return net score advantage (our score - opponent's best score)
        return my_score - opponent_best_score

    def choose_move(self, game_state):
        """
        Choose the best move using Monte Carlo Tree Search.

        Args:
            game_state (dict): Dictionary containing:
                - legal_moves (list): List of legal moves
                - board (Board): Current state of the game board
                - tile_distribution (dict): Original distribution of tiles
                - lexicon_tree: Game's lexicon tree

        Returns:
            int: Index of chosen move or 0 to end game
        """
        legal_moves = game_state['legal_moves']

        # If no legal moves available, end turn
        if not legal_moves:
            return 0

        # Track average net score for each move
        move_scores = defaultdict(list)

        # Run Monte Carlo simulations for each legal move
        for move_idx, move in enumerate(legal_moves, 1):
            # For each move, simulate multiple opponent racks and responses
            for _ in range(self.num_simulations):
                # Simulate opponent's rack
                opponent_rack = self._simulate_opponent_rack(game_state, move[3])

                # Evaluate this move sequence
                net_score = self._evaluate_move_sequence(game_state, move, opponent_rack)
                move_scores[move_idx].append(net_score)

        # Calculate average net score for each move
        avg_scores = {
            move_idx: sum(scores) / len(scores)
            for move_idx, scores in move_scores.items()
        }

        # Choose move with highest average net score
        best_move_idx = max(avg_scores.items(), key=lambda x: x[1])[0]

        # Print decision reasoning
        chosen_move = legal_moves[best_move_idx - 1]
        avg_net_score = avg_scores[best_move_idx]
        print(f"\n{self.name}'s decision process:")
        print(f"Choosing to play '{chosen_move[0]}' at {chosen_move[1]} "
              f"({chosen_move[2]}) for {chosen_move[4]} points")
        print(f"Expected net score advantage: {avg_net_score:.1f} points")
        print(f"Based on {self.num_simulations} simulated opponent responses")

        return best_move_idx