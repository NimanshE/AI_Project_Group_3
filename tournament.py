from game import ScrabbleGame
from typing import List, Tuple, Dict
import random
from collections import defaultdict
import statistics


class TournamentManager:
    def __init__(self,self_matchup_players: List, players: List, games_per_matchup: int = 10):
        """
        Initialize tournament manager.

        Args:
            players: List of Player instances to compete
            games_per_matchup: Number of games to play for each player pair
        """
        self.players = players
        self.self_matchup_players = self_matchup_players
        self.games_per_matchup = games_per_matchup
        self.results = defaultdict(list)  # Store all game results
        self.player_stats = defaultdict(lambda: {
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'total_points': 0,
            'avg_score': 0,
            'scores': []
        })

    def run_match(self, player1, player2) -> tuple:
        """Run a single match between two players and return their scores."""
        game = ScrabbleGame(player1, player2)
        return game.start_game()

    def run_tournament(self) -> Dict:
        """
        Run complete tournament with all players facing each other.

        Returns:
            Dictionary containing tournament statistics
        """
        # run matches between self matchups
        for player1, player2 in self.self_matchup_players:
            print(f"\nPlaying matches between {player1.name} and {player2.name}")

            for game_num in range(self.games_per_matchup):
                print(f"\nGame {game_num + 1}/{self.games_per_matchup}")

                # Randomly decide who goes first
                if random.random() < 0.5:
                    p1, p2 = player1, player2
                else:
                    p1, p2 = player2, player1

                score1, score2 = self.run_match(p1, p2)

                # Store results with original player order
                if p1 == player1:
                    self.results[(player1.name, player2.name)].append((score1, score2))
                    self._update_stats(player1.name, player2.name, score1, score2)
                else:
                    self.results[(player1.name, player2.name)].append((score2, score1))
                    self._update_stats(player1.name, player2.name, score2, score1)


        # Run matches between all player pairs
        for i, player1 in enumerate(self.players):
            for j, player2 in enumerate(self.players[i + 1:], i + 1):
                print(f"\nPlaying matches between {player1.name} and {player2.name}")

                for game_num in range(self.games_per_matchup):
                    print(f"\nGame {game_num + 1}/{self.games_per_matchup}")

                    # Randomly decide who goes first
                    if random.random() < 0.5:
                        p1, p2 = player1, player2
                    else:
                        p1, p2 = player2, player1

                    score1, score2 = self.run_match(p1, p2)

                    # Store results with original player order
                    if p1 == player1:
                        self.results[(player1.name, player2.name)].append((score1, score2))
                        self._update_stats(player1.name, player2.name, score1, score2)
                    else:
                        self.results[(player1.name, player2.name)].append((score2, score1))
                        self._update_stats(player1.name, player2.name, score2, score1)

        return self._compile_tournament_stats()

    def _update_stats(self, player1_name: str, player2_name: str, score1: int, score2: int):
        """Update player statistics after each game."""
        # Update scores list
        self.player_stats[player1_name]['scores'].append(score1)
        self.player_stats[player2_name]['scores'].append(score2)

        # Update wins/losses/draws
        if score1 > score2:
            self.player_stats[player1_name]['wins'] += 1
            self.player_stats[player2_name]['losses'] += 1
        elif score2 > score1:
            self.player_stats[player1_name]['losses'] += 1
            self.player_stats[player2_name]['wins'] += 1
        else:
            self.player_stats[player1_name]['draws'] += 1
            self.player_stats[player2_name]['draws'] += 1

        # Update total points
        self.player_stats[player1_name]['total_points'] += score1
        self.player_stats[player2_name]['total_points'] += score2

    def _compile_tournament_stats(self) -> Dict:
        """Compile final tournament statistics."""
        stats = {}

        # Calculate derived statistics for each player
        for player_name, player_data in self.player_stats.items():
            num_games = len(player_data['scores'])
            stats[player_name] = {
                'total_games': num_games,
                'wins': player_data['wins'],
                'losses': player_data['losses'],
                'draws': player_data['draws'],
                'win_rate': player_data['wins'] / num_games * 100,
                'total_points': player_data['total_points'],
                'avg_score': statistics.mean(player_data['scores']),
                'max_score': max(player_data['scores']),
                'min_score': min(player_data['scores']),
                'score_std_dev': statistics.stdev(player_data['scores']) if len(player_data['scores']) > 1 else 0
            }

        # Add head-to-head records
        stats['matchups'] = dict(self.results)

        return stats

    def print_results(self):
        """Print tournament results in a readable format."""
        print("\n=== Tournament Results ===\n")

        # Print individual player statistics
        print("Player Statistics:")
        print("-----------------")
        for player_name, player_stats in self.player_stats.items():
            print(f"\n{player_name}:")
            print(f"Wins: {player_stats['wins']}")
            print(f"Losses: {player_stats['losses']}")
            print(f"Draws: {player_stats['draws']}")
            avg_score = statistics.mean(player_stats['scores'])
            print(f"Average Score: {avg_score:.2f}")
            if len(player_stats['scores']) > 1:
                print(f"Score Std Dev: {statistics.stdev(player_stats['scores']):.2f}")

        # Print head-to-head results
        print("\nHead-to-head Results:")
        print("--------------------")
        for (p1, p2), results in self.results.items():
            print(f"\n{p1} vs {p2}:")
            p1_wins = sum(1 for s1, s2 in results if s1 > s2)
            p2_wins = sum(1 for s1, s2 in results if s2 > s1)
            draws = sum(1 for s1, s2 in results if s1 == s2)
            print(f"Record: {p1_wins}-{p2_wins}-{draws}")
            p1_avg = statistics.mean(s1 for s1, _ in results)
            p2_avg = statistics.mean(s2 for _, s2 in results)
            print(f"Average Scores: {p1}: {p1_avg:.2f}, {p2}: {p2_avg:.2f}")


if __name__ == "__main__":
    # Example usage
    from game import GreedyAIPlayer
    from adversarial_player import AdversarialAIPlayer
    from mcts_player import MCTSPlayer
    from conservative_player import ConservativeAIPlayer

    self_matchup_players = [
        (GreedyAIPlayer("Greedy AI"), GreedyAIPlayer("Greedy AI")),
        (AdversarialAIPlayer("Adversarial AI"), AdversarialAIPlayer("Adversarial AI")),
        (MCTSPlayer("MCTS AI", num_simulations=5), MCTSPlayer("MCTS AI", num_simulations=5)),
        (ConservativeAIPlayer("Conservative AI"), ConservativeAIPlayer("Conservative AI"))
    ]

    # Create players
    players = [
        GreedyAIPlayer("Greedy AI"),
        AdversarialAIPlayer("Adversarial AI"),
        MCTSPlayer("MCTS AI", num_simulations=5),
        ConservativeAIPlayer("Conservative AI")
    ]

    # Run tournament
    tournament = TournamentManager(self_matchup_players,players, games_per_matchup=5)
    stats = tournament.run_tournament()
    tournament.print_results()