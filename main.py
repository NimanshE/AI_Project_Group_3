from letter_tree import build_tree_from_file
from board import *
from solver import SolveState
from game import *
from adversarial_player import AdversarialAIPlayer
from dumb_human_player import DumbHumanPlayer
from mcts_player import MCTSPlayer
from conservative_player import ConservativeAIPlayer

greedy_player = GreedyAIPlayer("Greedy AI")
human_player = HumanPlayer("Human")
mcts_player = MCTSPlayer("MCTS AI", num_simulations=5)
conservative_player = ConservativeAIPlayer("Conservative AI")
adversarial_player = AdversarialAIPlayer("Adversary AI")


game = ScrabbleGame(conservative_player, adversarial_player)
game.start_game()
