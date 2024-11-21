from game import Player
from collections import Counter
from typing import List, Dict, Tuple


class ConservativeAIPlayer(Player):
    """
    AI player that prioritizes consistent scoring and rack management over maximum points.
    Focuses on maintaining a balanced rack and making safer plays.
    """

    # Vowels and their relative values for rack balance
    VOWELS = {'a', 'e', 'i', 'o', 'u'}

    # Power tiles that should be saved for high-scoring opportunities
    POWER_TILES = {'s', 'z', 'q', 'j', 'x'}

    # Ideal rack composition metrics
    IDEAL_VOWEL_RATIO = 0.4  # Aim for 40% vowels

    # Tile values for rack balance evaluation
    TILE_VALUES = {
        'a': 3, 'b': 2, 'c': 2, 'd': 2, 'e': 3, 'f': 1, 'g': 2, 'h': 2,
        'i': 3, 'j': 1, 'k': 1, 'l': 2, 'm': 2, 'n': 2, 'o': 3, 'p': 2,
        'q': 1, 'r': 2, 's': 4, 't': 2, 'u': 3, 'v': 1, 'w': 1, 'x': 1,
        'y': 2, 'z': 1
    }

    def __init__(self, name: str):
        """Initialize player with custom parameters."""
        super().__init__(name)
        self.min_acceptable_score = 8  # Minimum score to consider a move
        self.power_tile_threshold = 20  # Minimum points to use power tiles

    def _evaluate_rack_balance(self, rack: List[str]) -> float:
        """
        Evaluate how well-balanced a rack is for future plays.

        Args:
            rack: List of tiles in the rack

        Returns:
            float: Score between 0 and 1, where 1 is perfectly balanced
        """
        if not rack:
            return 0.0

        # Count vowels and consonants
        vowel_count = sum(1 for tile in rack if tile in self.VOWELS)
        current_ratio = vowel_count / len(rack)

        # Penalize deviation from ideal ratio
        ratio_score = 1.0 - abs(current_ratio - self.IDEAL_VOWEL_RATIO)

        # Check for duplicate letters (penalize having too many of the same tile)
        letter_counts = Counter(rack)
        duplication_penalty = sum(count - 1 for count in letter_counts.values()) * 0.1

        # Calculate final balance score
        balance_score = max(0.0, ratio_score - duplication_penalty)

        return balance_score

    def _evaluate_leave(self, remaining_rack: List[str]) -> float:
        """
        Evaluate the quality of tiles that would remain after a play.

        Args:
            remaining_rack: List of tiles that would remain

        Returns:
            float: Score representing the quality of the leave
        """
        # Start with rack balance score
        leave_score = self._evaluate_rack_balance(remaining_rack)

        # Bonus for keeping flexible tiles
        leave_score += sum(self.TILE_VALUES.get(tile, 0) * 0.1 for tile in remaining_rack)

        # Penalty for keeping power tiles too long
        power_tile_count = sum(1 for tile in remaining_rack if tile in self.POWER_TILES)
        leave_score -= power_tile_count * 0.15

        return leave_score

    def _should_use_power_tile(self, move: Tuple, game_state: Dict) -> bool:
        """
        Determine if it's appropriate to use a power tile in this move.

        Args:
            move: Tuple of (word, position, direction, rack_tiles, score)
            game_state: Current game state

        Returns:
            bool: Whether to allow using the power tile
        """
        word, _, _, rack_tiles, score = move

        # Check if move uses any power tiles
        uses_power_tile = any(tile in self.POWER_TILES for tile in rack_tiles)
        if not uses_power_tile:
            return True

        # Always allow S for pluralization if score is good
        if 's' in rack_tiles and score >= self.power_tile_threshold * 0.75:
            return True

        # For other power tiles, require higher threshold
        return score >= self.power_tile_threshold

    def _evaluate_move(self, move: Tuple, game_state: Dict) -> float:
        """
        Evaluate a move considering multiple factors.

        Args:
            move: Tuple of (word, position, direction, rack_tiles, score)
            game_state: Current game state

        Returns:
            float: Overall move evaluation score
        """
        word, position, direction, rack_tiles, score = move

        # Start with raw score, but scale it down
        evaluation = score * 0.5

        # Calculate remaining rack after this move
        remaining_rack = self.rack.copy()
        for tile in rack_tiles:
            remaining_rack.remove(tile)

        # Add leave evaluation
        leave_quality = self._evaluate_leave(remaining_rack)
        evaluation += leave_quality * 15  # Significant weight on leave quality

        # Penalize moves that use power tiles suboptimally
        if not self._should_use_power_tile(move, game_state):
            evaluation *= 0.5

        # Bonus for moves that maintain good board control
        board = game_state['board']
        row, col = position

        # Penalize moves that open triple word score squares
        if row > 0 and board.is_empty((row - 1, col)):
            evaluation *= 0.8
        if row < 14 and board.is_empty((row + 1, col)):
            evaluation *= 0.8

        return evaluation

    def choose_move(self, game_state: Dict) -> int:
        """
        Choose the best move based on conservative evaluation criteria.

        Args:
            game_state: Dictionary containing game state information

        Returns:
            int: Index of chosen move (1-based) or 0 to pass
        """
        legal_moves = game_state['legal_moves']

        if not legal_moves:
            return 0

        # Filter out moves below minimum score threshold
        viable_moves = [
            (i, move) for i, move in enumerate(legal_moves, 1)
            if move[4] >= self.min_acceptable_score
        ]

        if not viable_moves:
            # If no moves meet threshold, take best available if score > 0
            best_move = max(enumerate(legal_moves, 1), key=lambda x: x[1][4])
            if best_move[1][4] > 0:
                return best_move[0]
            return 0

        # Evaluate all viable moves
        move_evaluations = [
            (i, self._evaluate_move(move, game_state))
            for i, move in viable_moves
        ]

        # Choose move with highest evaluation
        best_move_idx, best_eval = max(move_evaluations, key=lambda x: x[1])
        chosen_move = legal_moves[best_move_idx - 1]

        # Print explanation of choice
        print(f"\n{self.name}'s decision process:")
        print(f"Choosing to play '{chosen_move[0]}' at {chosen_move[1]} "
              f"({chosen_move[2]}) for {chosen_move[4]} points")
        print(f"Move evaluation score: {best_eval:.1f}")
        print(f"Rack balance after move: "
              f"{self._evaluate_rack_balance(self.rack):.2f}")

        return best_move_idx