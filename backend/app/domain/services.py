"""Domain services: pure business logic without persistence."""

import random
from typing import Sequence


def generate_americano_pairs(player_ids: Sequence[int]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """
    For Americano: random pairs. player_ids must have len divisible by 4.
    Returns list of (team1, team2) where each team is (id1, id2).
    """
    ids = list(player_ids)
    if len(ids) % 4 != 0:
        raise ValueError("Player count must be divisible by 4")
    random.shuffle(ids)
    result = []
    for i in range(0, len(ids), 4):
        team1 = (ids[i], ids[i + 1])
        team2 = (ids[i + 2], ids[i + 3])
        result.append((team1, team2))
    return result


def generate_mexicano_pairs(
    player_ids_ordered_by_points: Sequence[int],
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """
    For Mexicano: pairs by ranking 1+3 vs 2+4, 5+7 vs 6+8, ...
    player_ids_ordered_by_points: sorted by total_points descending (best first).
    """
    ids = list(player_ids_ordered_by_points)
    if len(ids) % 4 != 0:
        raise ValueError("Player count must be divisible by 4")
    result = []
    for i in range(0, len(ids), 4):
        team1 = (ids[i], ids[i + 2])      # 1st + 3rd
        team2 = (ids[i + 1], ids[i + 3])  # 2nd + 4th
        result.append((team1, team2))
    return result


def compute_match_points(
    score_team1: int,
    score_team2: int,
    points_per_round: int,
) -> tuple[int, int, int, int]:
    """
    Americano/Mexicano: each player on winning team gets score_team1,
    each on losing team gets score_team2.
    Returns (points_player1, points_player2, points_player3, points_player4).
    """
    return (score_team1, score_team1, score_team2, score_team2)
