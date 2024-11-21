from letter_tree import build_tree_from_file
from board import sample_board

class SolveState:
    def __init__(self, dictionary, board, rack):
        self.dictionary = dictionary
        self.board = board
        self.rack = rack
        self.reference_rack = rack.copy()
        self.cross_check_results = None
        self.direction = None
        self.found_moves = []

    def before(self, pos):
        row, col = pos
        if self.direction == 'across':
            return row, col - 1
        else:
            return row - 1, col

    def after(self, pos):
        row, col = pos
        if self.direction == 'across':
            return row, col + 1
        else:
            return row + 1, col

    def before_cross(self, pos):
        row, col = pos
        if self.direction == 'across':
            return row - 1, col
        else:
            return row, col - 1

    def after_cross(self, pos):
        row, col = pos
        if self.direction == 'across':
            return row + 1, col
        else:
            return row, col + 1

    def legal_move(self, word, last_pos):
        play_pos = last_pos
        word_idx = len(word) - 1
        while word_idx >= 0:
            play_pos = self.before(play_pos)
            word_idx -= 1
        start_pos = self.after(play_pos)
        score = self.board.calculate_score(word, start_pos, self.direction, self.rack.copy())
        # remove self.rack.copy() from self.reference_rack
        used_rack = self.reference_rack.copy()
        for letter in self.rack:
            used_rack.remove(letter)
        self.found_moves.append((word, self.after(play_pos), self.direction, used_rack, score))

    def cross_check(self):
        result = dict()
        for pos in self.board.all_positions():
            if self.board.is_filled(pos):
                continue
            letters_before = ""
            scan_pos = pos
            while self.board.is_filled(self.before_cross(scan_pos)):
                scan_pos = self.before_cross(scan_pos)
                letters_before = self.board.get_tile(scan_pos) + letters_before
            letters_after = ""
            scan_pos = pos
            while self.board.is_filled(self.after_cross(scan_pos)):
                scan_pos = self.after_cross(scan_pos)
                letters_after = letters_after + self.board.get_tile(scan_pos)
            if len(letters_before) == 0 and len(letters_after) == 0:
                legal_here = list('abcdefghijklmnopqrstuvwxyz')
            else:
                legal_here = []
                for letter in 'abcdefghijklmnopqrstuvwxyz':
                    word_formed = letters_before + letter + letters_after
                    if self.dictionary.is_word(word_formed):
                        legal_here.append(letter)
            result[pos] = legal_here
        return result

    def find_anchors(self):
        anchors = []
        for pos in self.board.all_positions():
            empty = self.board.is_empty(pos)
            neighbor_filled = self.board.is_filled(self.before(pos)) or \
                              self.board.is_filled(self.after(pos)) or \
                              self.board.is_filled(self.before_cross(pos)) or \
                              self.board.is_filled(self.after_cross(pos))
            if empty and neighbor_filled:
                anchors.append(pos)
        return anchors

    def before_part(self, partial_word, current_node, anchor_pos, limit):
        self.extend_after(partial_word, current_node, anchor_pos, False)
        if limit > 0:
            for next_letter in current_node.children.keys():
                if next_letter in self.rack:
                    self.rack.remove(next_letter)
                    self.before_part(
                        partial_word + next_letter,
                        current_node.children[next_letter],
                        anchor_pos,
                        limit - 1
                    )
                    self.rack.append(next_letter)

    def extend_after(self, partial_word, current_node, next_pos, anchor_filled):
        if not self.board.is_filled(next_pos) and current_node.is_word and anchor_filled:
            self.legal_move(partial_word, self.before(next_pos))
        if self.board.in_bounds(next_pos):
            if self.board.is_empty(next_pos):
                for next_letter in current_node.children.keys():
                    if next_letter in self.rack and next_letter in self.cross_check_results[next_pos]:
                        self.rack.remove(next_letter)
                        self.extend_after(
                            partial_word + next_letter,
                            current_node.children[next_letter],
                            self.after(next_pos),
                            True
                        )
                        self.rack.append(next_letter)
            else:
                existing_letter = self.board.get_tile(next_pos)
                if existing_letter in current_node.children.keys():
                    self.extend_after(
                        partial_word + existing_letter,
                        current_node.children[existing_letter],
                        self.after(next_pos),
                        True
                    )

    def find_all_options(self):
        for direction in ['across', 'down']:
            self.direction = direction
            anchors = self.find_anchors()
            self.cross_check_results = self.cross_check()
            for anchor_pos in anchors:
                if self.board.is_filled(self.before(anchor_pos)):
                    scan_pos = self.before(anchor_pos)
                    partial_word = self.board.get_tile(scan_pos)
                    while self.board.is_filled(self.before(scan_pos)):
                        scan_pos = self.before(scan_pos)
                        partial_word = self.board.get_tile(scan_pos) + partial_word
                    pw_node = self.dictionary.lookup(partial_word)
                    if pw_node is not None:
                        self.extend_after(
                            partial_word,
                            pw_node,
                            anchor_pos,
                            False
                        )
                else:
                    limit = 0
                    scan_pos = anchor_pos
                    while self.board.is_empty(self.before(scan_pos)) and self.before(scan_pos) not in anchors:
                        limit = limit + 1
                        scan_pos = self.before(scan_pos)
                    self.before_part("", self.dictionary.root, anchor_pos, limit)


if __name__ == '__main__':
    board = sample_board()
    rack = ['e', 'f', 'f', 'e', 'c', 't']
    solver = SolveState(build_tree_from_file(), board, rack)

    print(board)
    print()

    solver.find_all_options()
    print("Legal moves:")
    for move in solver.found_moves:
        print(move)
