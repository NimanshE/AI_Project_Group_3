class LetterTreeNode:
    def __init__(self, is_word):
        self.is_word = is_word
        self.children = dict()

class LetterTree:
    def __init__(self, words):
        self.root = LetterTreeNode(False)
        for word in words:
            current_node = self.root
            for letter in word:
                if letter not in current_node.children.keys():
                    current_node.children[letter] = LetterTreeNode(False)
                current_node = current_node.children[letter]
            current_node.is_word = True

    def lookup(self, word):
        current_node = self.root
        for letter in word:
            if letter not in current_node.children.keys():
                return None
            current_node = current_node.children[letter]
        return current_node

    def is_word(self, word):
        word_node = self.lookup(word)
        if word_node is None:
            return False
        return word_node.is_word

def build_tree_from_file(file_name = 'lexicon/lexicon_basic.txt'):
    with open(file_name, 'rt') as file:
        words = []
        for line in file:
            word = line.strip()
            words.append(word)
    return LetterTree(words)

from graphviz import Digraph

def visualize_tree(tree, file_path="assets/lexicon_tree"):
    dot = Digraph(comment='Letter Tree')
    dot.attr(rankdir="LR", dpi="300")

    # Set default node attributes
    dot.attr('node', shape='circle', width='0.3', height='0.3', style='filled', color='black', fillcolor='white')

    def add_nodes_edges(node, dot, parent=None, edge_label="", visited=None):
        if visited is None:
            visited = set()

        if id(node) in visited:
            return

        visited.add(id(node))
        node_id = str(id(node))

        # Set node attributes based on whether it's a word
        if node.is_word:
            dot.node(node_id, shape="doublecircle", fillcolor="lightblue", label="")
        else:
            dot.node(node_id, label="")

        for letter, child in node.children.items():
            add_nodes_edges(child, dot, node, letter, visited)
            dot.edge(node_id, str(id(child)), label=letter, fontsize='14', fontweight='bold')

    dot.node(str(id(tree.root)), 'Root')
    add_nodes_edges(tree.root, dot)
    dot.render(file_path, format='png', cleanup=True)

if __name__ == '__main__':
    lexicon_type = "lexicon/lexicon_ref.txt"
    tree = build_tree_from_file(lexicon_type)

    print("Do you want to visualize the tree? (y/n)")
    visualize = input()
    if visualize == 'y':
        visualize_tree(tree)
        print(f"Tree visualization saved as assets/lexicon_tree.png")
    else:
        print("Tree visualization skipped")
