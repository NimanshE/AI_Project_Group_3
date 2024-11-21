# visualize_tournament.py
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict


def load_tournament_data(filename='tournament_results.json'):
    """Load tournament results from JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)


def create_win_rate_chart(data, output_file='win_rates.png'):
    """Create bar chart of win rates for each AI."""
    plt.figure(figsize=(10, 6))
    players = []
    win_rates = []

    for player, stats in data['player_stats'].items():
        players.append(player)
        win_rates.append(stats['win_rate'])

    plt.bar(players, win_rates)
    plt.title('Win Rates by AI Player')
    plt.xlabel('AI Player')
    plt.ylabel('Win Rate (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def create_score_distribution_box(data, output_file='score_distribution.png'):
    """Create box plot of score distributions."""
    player_scores = defaultdict(list)

    # Collect all scores for each player
    for matchup_info in data['matchups'].values():
        p1 = matchup_info['player1']
        p2 = matchup_info['player2']
        for score_pair in matchup_info['scores']:
            player_scores[p1].append(score_pair[0])
            player_scores[p2].append(score_pair[1])

    plt.figure(figsize=(12, 6))
    plt.boxplot(player_scores.values(), labels=player_scores.keys())
    plt.title('Score Distribution by AI Player')
    plt.xlabel('AI Player')
    plt.ylabel('Score')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def create_correlation_heatmap(data, output_file='correlation_heatmap.png'):
    """Create correlation heatmap between different metrics."""
    # Extract metrics for each player
    metrics = []
    for player, stats in data['player_stats'].items():
        metrics.append({
            'Player': player,
            'Win Rate': stats['win_rate'],
            'Avg Score': stats['average_score'],
            'Score StdDev': stats['score_std_dev']
        })

    df = pd.DataFrame(metrics)
    corr = df.select_dtypes(include=[np.number]).corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='RdBu', center=0, vmin=-1, vmax=1)
    plt.title('Correlation between AI Performance Metrics')
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def create_head_to_head_matrix(data, output_file='head_to_head.png'):
    """Create a matrix showing head-to-head win rates."""
    players = list(data['player_stats'].keys())
    n_players = len(players)
    matrix = np.zeros((n_players, n_players))

    for matchup_info in data['matchups'].values():
        p1 = matchup_info['player1']
        p2 = matchup_info['player2']
        if p1 != p2:  # Skip self-matches
            p1_idx = players.index(p1)
            p2_idx = players.index(p2)

            # Calculate win rate of p1 against p2
            p1_wins = sum(1 for s1, s2 in matchup_info['scores'] if s1 > s2)
            win_rate = (p1_wins / len(matchup_info['scores'])) * 100
            matrix[p1_idx][p2_idx] = win_rate
            matrix[p2_idx][p1_idx] = 100 - win_rate  # Opposite win rate

    plt.figure(figsize=(10, 8))
    sns.heatmap(matrix, annot=True, fmt='.1f', cmap='RdBu',
                xticklabels=players, yticklabels=players)
    plt.title('Head-to-Head Win Rates (%)')
    plt.xlabel('Opponent')
    plt.ylabel('Player')
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def create_average_score_comparison(data, output_file='average_scores.png'):
    """Create bar chart comparing average scores with error bars."""
    plt.figure(figsize=(12, 6))

    players = []
    avg_scores = []
    std_devs = []

    for player, stats in data['player_stats'].items():
        players.append(player)
        avg_scores.append(stats['average_score'])
        std_devs.append(stats['score_std_dev'])

    plt.bar(players, avg_scores, yerr=std_devs, capsize=5)
    plt.title('Average Scores by AI Player (with Standard Deviation)')
    plt.xlabel('AI Player')
    plt.ylabel('Score')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def generate_all_visualizations(data_file='tournament_results.json'):
    """Generate all tournament visualizations."""
    data = load_tournament_data(data_file)

    create_win_rate_chart(data)
    create_score_distribution_box(data)
    create_correlation_heatmap(data)
    create_head_to_head_matrix(data)
    create_average_score_comparison(data)


if __name__ == "__main__":
    generate_all_visualizations()