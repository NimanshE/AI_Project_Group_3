from game import Player
from solver import SolveState
from collections import Counter
import random


class AdversarialAIPlayer(Player):
    """AI player that tries to minimize opponent's potential scoring opportunities."""

    def _get_probable_opponent_rack(self, game_state):
        """
        Estimate the most probable tiles in opponent's rack based on remaining tiles.

        Args:
            game_state (dict): Current game state including board and tile distribution

        Returns:
            list: Seven most probable tiles the opponent might have
        """
        # Get original tile distribution
        tile_dist = game_state['tile_distribution'].copy()

        # Remove tiles that are on the board
        board = game_state['board']
        for pos in board.all_positions():
            tile = board.get_tile(pos)
            if tile:
                if tile in tile_dist and tile_dist[tile] > 0:
                    tile_dist[tile] -= 1

        # Remove tiles that are in our rack
        for tile in self.rack:
            if tile in tile_dist and tile_dist[tile] > 0:
                tile_dist[tile] -= 1

        # Convert remaining distribution to list of tiles
        remaining_tiles = []
        for tile, count in tile_dist.items():
            remaining_tiles.extend([tile] * count)

        # Select the 7 most frequent remaining tiles
        # (weighted random selection based on frequency)
        if len(remaining_tiles) <= 7:
            return remaining_tiles

        # Count frequency of remaining tiles
        freq = Counter(remaining_tiles)
        # Sort tiles by frequency, highest first
        sorted_tiles = sorted(freq.items(), key=lambda x: x[1], reverse=True)

        # Select tiles with preference for higher frequency ones
        probable_rack = []
        total_weight = sum(freq.values())
        while len(probable_rack) < 7:
            if not remaining_tiles:
                break
            # Weighted random selection
            weights = [count / total_weight for tile, count in sorted_tiles]
            chosen_tile = random.choices([tile for tile, count in sorted_tiles],
                                         weights=weights)[0]
            probable_rack.append(chosen_tile)
            # Update frequencies
            freq[chosen_tile] -= 1
            if freq[chosen_tile] == 0:
                sorted_tiles = [(t, c) for t, c in sorted_tiles if t != chosen_tile]
            total_weight -= 1

        return probable_rack

    def _evaluate_opponent_potential(self, board, opponent_rack, lexicon_tree):
        """
        Evaluate potential scoring opportunities for opponent with given rack.

        Args:
            board: Current board state after our move
            opponent_rack: Estimated opponent rack
            lexicon_tree: Game's lexicon tree

        Returns:
            int: Maximum potential score opponent could achieve
        """
        # Create solver for opponent's turn
        solver = SolveState(lexicon_tree, board, opponent_rack)
        solver.find_all_options()

        # If no moves available, return 0
        if not solver.found_moves:
            return 0

        # Return maximum possible score
        return max(move[4] for move in solver.found_moves)

    def choose_move(self, game_state):
        """
        Choose move that minimizes opponent's potential next move score.

        Args:
            game_state (dict): Dictionary containing:
                - legal_moves (list): List of legal moves
                - board (Board): Current state of the game board
                - tile_distribution (dict): Original distribution of tiles

        Returns:
            int: Index of chosen move or 0 to end game
        """
        legal_moves = game_state['legal_moves']

        # If no legal moves available, end turn
        if not legal_moves:
            return 0

        # Get probable opponent rack
        opponent_rack = self._get_probable_opponent_rack(game_state)

        best_move_index = 1  # Initialize to first move
        min_opponent_potential = float('inf')

        # For each possible move we can make
        for i, move in enumerate(legal_moves, 1):
            # Create a copy of the board
            test_board = game_state['board'].copy()

            # Apply our move to the test board
            word, pos, direction, rack_used, score = move
            test_board.place_word(word, pos, direction, self.rack.copy())

            # Evaluate opponent's potential after this move
            opponent_potential = self._evaluate_opponent_potential(
                test_board,
                opponent_rack,
                game_state.get('lexicon_tree')  # Add lexicon_tree to game_state in game.py
            )

            # Update best move if this leads to lower opponent potential
            # If opponent potentials are equal, prefer the move that scores more points for us
            if (opponent_potential < min_opponent_potential or
                    (opponent_potential == min_opponent_potential and score > legal_moves[best_move_index - 1][4])):
                min_opponent_potential = opponent_potential
                best_move_index = i

        # Print the chosen move and reasoning for transparency
        chosen_move = legal_moves[best_move_index - 1]
        print(f"{self.name} chooses to play '{chosen_move[0]}' at {chosen_move[1]} "
              f"({chosen_move[2]}) for {chosen_move[4]} points")
        print(f"This move limits opponent's maximum potential score to {min_opponent_potential} points")

        return best_move_index