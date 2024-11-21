from enum import Enum
from PIL import Image, ImageDraw, ImageFont

class Modifier(Enum):
    NORMAL = ("Normal", "white")
    DOUBLE_LETTER = ("2LS", "cyan")
    TRIPLE_LETTER = ("3LS", "blue")
    DOUBLE_WORD = ("2WS", "pink")
    TRIPLE_WORD = ("3WS", "red")

class Square:

    def __init__(self, letter=None, modifier=Modifier.NORMAL):
        self.letter = letter
        self.modifier = modifier

    def __str__(self):
        if not self.letter:
            return "_"
        else:
            return self.letter

class Board:

    LETTER_SCORES = {
        'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2, 'h': 4, 'i': 1,
        'j': 8, 'k': 5, 'l': 1, 'm': 3, 'n': 1, 'o': 1, 'p': 3, 'q': 10, 'r': 1,
        's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 4, 'x': 8, 'y': 4, 'z': 10
    }

    def __init__(self, size):
        self.size = size
        self._tiles = [[Square() for _ in range(self.size)] for _ in range(self.size)]
        self._setup_board()

    def _setup_board(self):
        # Set up triple word squares
        for i, j in [(0, 0), (0, 7), (0, 14), (7, 0), (7, 14), (14, 0), (14, 7), (14, 14)]:
            self._tiles[i][j].modifier = Modifier.TRIPLE_WORD

        # Set up double word squares
        for i, j in [(1, 1), (2, 2), (3, 3), (4, 4), (1, 13), (2, 12), (3, 11), (4, 10),
                     (13, 1), (12, 2), (11, 3), (10, 4), (13, 13), (12, 12), (11, 11), (10, 10)]:
            self._tiles[i][j].modifier = Modifier.DOUBLE_WORD

        # Set up triple letter squares
        for i, j in [(1, 5), (1, 9), (5, 1), (5, 5), (5, 9), (5, 13), (9, 1), (9, 5), (9, 9), (9, 13), (13, 5),
                     (13, 9)]:
            self._tiles[i][j].modifier = Modifier.TRIPLE_LETTER

        # Set up double letter squares
        for i, j in [(0, 3), (0, 11), (2, 6), (2, 8), (3, 0), (3, 7), (3, 14),
                     (6, 2), (6, 6), (6, 8), (6, 12), (7, 3), (7, 11),
                     (8, 2), (8, 6), (8, 8), (8, 12), (11, 0), (11, 7), (11, 14),
                     (12, 6), (12, 8), (14, 3), (14, 11)]:
            self._tiles[i][j].modifier = Modifier.DOUBLE_LETTER

    def __str__(self):
        return '\n'.join(''.join(str(tile) for tile in row) for row in self._tiles)

    def all_positions(self):
        result = []
        for row in range(self.size):
            for col in range(self.size):
                result.append((row, col))
        return result

    def get_tile(self, pos):
        row, col = pos
        return self._tiles[row][col].letter

    def set_tile(self, pos, tile):
        row, col = pos
        self._tiles[row][col].letter = tile

    def place_word(self, word, pos, direction, rack):
        """
        Place a word on the board and calculate the score.

        Args:
            word (str): The word to be placed
            pos (tuple): Starting position (row, col)
            direction (str): 'across' or 'down'
            rack (list): Player's rack of available letters

        Returns:
            tuple: (score, remaining_rack)
        """
        # Create a copy of the rack to track used letters
        rack_used_cp1 = rack.copy()
        row_cp1, col_cp1 = pos

        rack_used_cp2 = rack.copy()
        row_cp2, col_cp2 = pos

        # Check if word can be placed
        for letter in word:
            # If the letter isn't already on the board, it must be in the rack
            if self.get_tile((row_cp2, col_cp2)) is None:
                try:
                    rack_used_cp2.remove(letter.lower())
                except ValueError:
                    # If letter not in rack, word can't be placed
                    return 0, rack

            # Move to next position
            if direction == 'across':
                col_cp2 += 1
            else:
                row_cp2 += 1

        used_rack = rack.copy()
        for letter in rack_used_cp2:
            used_rack.remove(letter)

        # Calculate score using the existing method
        score = self.calculate_score(word, pos, direction, used_rack)

        # Check if word can be placed
        for letter in word:
            # If the letter isn't already on the board, it must be in the rack
            if self.get_tile((row_cp1, col_cp1)) is None:
                try:
                    rack_used_cp1.remove(letter.lower())
                except ValueError:
                    # If letter not in rack, word can't be placed
                    return 0, rack

            # Place the letter
            self.set_tile((row_cp1, col_cp1), letter)

            # Move to next position
            if direction == 'across':
                col_cp1 += 1
            else:
                row_cp1 += 1


        # Determine the remaining rack
        remaining_rack = rack_used_cp1

        return score, remaining_rack

    def in_bounds(self, pos):
        row, col = pos
        return 0 <= row < self.size and 0 <= col < self.size

    def is_empty(self, pos):
        return self.in_bounds(pos) and self.get_tile(pos) is None

    def is_filled(self, pos):
        return self.in_bounds(pos) and self.get_tile(pos) is not None

    def copy(self):
        result = Board(self.size)
        for pos in self.all_positions():
            result.set_tile(pos, self.get_tile(pos))
        return result

    def calculate_score(self, word, pos, direction, rack_used):
        """
        Calculate the score for a move, including cross-words formed.

        Args:
            word (str): The word being placed
            pos (tuple): Starting position (row, col)
            direction (str): 'across' or 'down'
            rack_used (list): List of letters used from the rack

        Returns:
            int: Total score for the move
        """
        total_score = 0
        row, col = pos
        word_multiplier = 1
        main_word_score = 0
        tiles_used = 0

        # Score the main word
        for letter in word:
            curr_pos = (row, col)
            letter_multiplier = 1
            square = self._tiles[row][col]

            # Only apply multipliers if the tile is being placed (not already on board)
            if square.letter is None:
                tiles_used += 1
                if square.modifier == Modifier.DOUBLE_LETTER:
                    letter_multiplier = 2
                elif square.modifier == Modifier.TRIPLE_LETTER:
                    letter_multiplier = 3
                elif square.modifier == Modifier.DOUBLE_WORD:
                    word_multiplier *= 2
                elif square.modifier == Modifier.TRIPLE_WORD:
                    word_multiplier *= 3

            main_word_score += self.LETTER_SCORES[letter.lower()] * letter_multiplier

            # Move to next position
            if direction == 'across':
                col += 1
            else:
                row += 1

        main_word_score *= word_multiplier
        total_score += main_word_score

        # Score cross-words
        row, col = pos
        for i, letter in enumerate(word):
            curr_pos = (row, col)
            if self._tiles[row][col].letter is None:  # Only check for cross-words at new tile positions
                cross_word = self._get_cross_word(curr_pos, direction)
                if cross_word is not None:
                    cross_score = self._score_cross_word(cross_word, curr_pos, direction, letter)
                    total_score += cross_score

            if direction == 'across':
                col += 1
            else:
                row += 1

        # Add bingo bonus (50 points) if all 7 tiles are used
        if len(rack_used) == 7:
            total_score += 50

        return total_score

    def _get_cross_word(self, pos, main_direction):
        """Get complete cross-word at given position, if one exists."""
        row, col = pos
        cross_direction = 'down' if main_direction == 'across' else 'across'

        # Find start of cross-word
        start_row, start_col = row, col
        while True:
            if cross_direction == 'down':
                if start_row > 0 and self._tiles[start_row - 1][col].letter is not None:
                    start_row -= 1
                else:
                    break
            else:
                if start_col > 0 and self._tiles[row][start_col - 1].letter is not None:
                    start_col -= 1
                else:
                    break

        # Build cross-word if it exists
        cross_word = ""
        curr_row, curr_col = start_row, start_col
        while curr_row < self.size and curr_col < self.size:
            if cross_direction == 'down':
                if curr_row == row and self._tiles[curr_row][col].letter is None:
                    # This is where the new tile will go
                    cross_word += "?"
                elif self._tiles[curr_row][col].letter is not None:
                    cross_word += self._tiles[curr_row][col].letter
                else:
                    break
                curr_row += 1
            else:
                if curr_col == col and self._tiles[row][curr_col].letter is None:
                    cross_word += "?"
                elif self._tiles[row][curr_col].letter is not None:
                    cross_word += self._tiles[row][curr_col].letter
                else:
                    break
                curr_col += 1

        # Return None if no cross-word is formed
        return cross_word if len(cross_word) > 1 else None

    def _score_cross_word(self, cross_word, pos, main_direction, new_letter):
        """Score a cross-word formed by placing a tile."""
        row, col = pos
        word_multiplier = 1
        word_score = 0

        # Get starting position of cross-word
        start_row, start_col = row, col
        cross_direction = 'down' if main_direction == 'across' else 'across'
        while True:
            if cross_direction == 'down':
                if start_row > 0 and self._tiles[start_row - 1][col].letter is not None:
                    start_row -= 1
                else:
                    break
            else:
                if start_col > 0 and self._tiles[row][start_col - 1].letter is not None:
                    start_col -= 1
                else:
                    break

        # Score the cross-word
        curr_row, curr_col = start_row, start_col
        for letter in cross_word:
            letter_multiplier = 1
            curr_pos = (curr_row, curr_col)

            # If this is the intersection point
            if curr_row == row and curr_col == col:
                square = self._tiles[curr_row][curr_col]
                if square.modifier == Modifier.DOUBLE_LETTER:
                    letter_multiplier = 2
                elif square.modifier == Modifier.TRIPLE_LETTER:
                    letter_multiplier = 3
                elif square.modifier == Modifier.DOUBLE_WORD:
                    word_multiplier *= 2
                elif square.modifier == Modifier.TRIPLE_WORD:
                    word_multiplier *= 3
                word_score += self.LETTER_SCORES[new_letter.lower()] * letter_multiplier
            else:
                word_score += self.LETTER_SCORES[letter.lower()]

            if cross_direction == 'down':
                curr_row += 1
            else:
                curr_col += 1

        return word_score * word_multiplier

    def visualize(self, filename='scrabble_board.png'):
        cell_size = 40
        img_size = (self.size + 1) * cell_size
        img = Image.new('RGB', (img_size, img_size), color='beige')
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()

        for i in range(self.size):
            for j in range(self.size):
                x, y = (j + 1) * cell_size, (i + 1) * cell_size
                square = self._tiles[i][j]

                # Draw modifier circle
                if square.modifier != Modifier.NORMAL:
                    draw.ellipse([x + 5, y + 5, x + cell_size - 5, y + cell_size - 5],
                                 fill=square.modifier.value[1])

                # Draw cell border
                draw.rectangle([x, y, x + cell_size, y + cell_size], outline='black')

                # Draw letter
                if square.letter:
                    draw.text((x + cell_size // 4, y + cell_size // 4),
                              square.letter.upper(), fill='black', font=font)

        # Draw row numbers
        for i in range(self.size):
            y = (i + 1) * cell_size
            draw.text((cell_size // 4, y + cell_size // 4), str(i), fill='black', font=font)

        # Draw column numbers
        for j in range(self.size):
            x = (j + 1) * cell_size
            draw.text((x + cell_size // 4, cell_size // 4), str(j), fill='black', font=font)

        img.save(filename)
        print(f"Board saved to '{filename}'")

def sample_board():
    rack = ['c', 'a', 't', 's', 'e', 'r', 'a']
    result = Board(15)
    result.place_word("cats", (7, 7), 'across', rack)
    result.place_word("ears", (6, 8), 'down', rack)
    result.place_word("tea", (1, 1), 'down', rack)
    return result

if __name__ == '__main__':
    board = Board(15)
    board.place_word("cats", (7, 7), 'across')
    board.place_word("ears", (6, 8), 'down')
    board.place_word("off", (1, 1), 'down')
    print(board)
    board.visualize()
