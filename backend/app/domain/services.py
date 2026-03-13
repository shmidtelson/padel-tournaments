"""Domain services: pure business logic without persistence.

Pairing algorithms (all return list of (team1, team2) with team = (id1, id2); 4 players -> one match):
- random: full random shuffle (Americano-style).
- by_ranking: weak+strong vs weak+strong — 1st+3rd vs 2nd+4th by points (Mexicano-style).
- similar_points_avoid_rematch: group by similar points (consecutive quartets), pick split that minimizes
  how often the two pairs have already been in the same match.
"""

import random
from typing import Sequence


def generate_random_pairs(player_ids: Sequence[int]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """
    Full random: shuffle and take consecutive groups of 4 as one match.
    player_ids must have len divisible by 4.
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


def generate_americano_pairs(player_ids: Sequence[int]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """Alias for generate_random_pairs (Americano traditionally uses random pairs)."""
    return generate_random_pairs(player_ids)


def generate_by_ranking_pairs(
    player_ids_ordered_by_points: Sequence[int],
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """
    Weak+strong vs weak+strong: in each group of 4 by ranking, team1 = 1st+3rd, team2 = 2nd+4th.
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


def generate_mexicano_pairs(
    player_ids_ordered_by_points: Sequence[int],
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """Alias for generate_by_ranking_pairs (Mexicano uses this pairing)."""
    return generate_by_ranking_pairs(player_ids_ordered_by_points)


def _pair_key(a: int, b: int) -> tuple[int, int]:
    return (min(a, b), max(a, b))


def _count_shared_matches(
    past_match_quartets: list[tuple[int, int, int, int]],
) -> dict[tuple[int, int], int]:
    """For each pair (a,b), count how many past matches contained both a and b."""
    counts: dict[tuple[int, int], int] = {}
    for (p1, p2, p3, p4) in past_match_quartets:
        for a, b in [(p1, p2), (p1, p3), (p1, p4), (p2, p3), (p2, p4), (p3, p4)]:
            k = _pair_key(a, b)
            counts[k] = counts.get(k, 0) + 1
    return counts


def generate_similar_points_avoid_rematch_pairs(
    player_ids_ordered_by_points: Sequence[int],
    past_match_quartets: list[tuple[int, int, int, int]],
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """
    Similar points (group by ranking) but avoid re-matches: form groups of 4 by consecutive
    ranking, then for each group choose the 2v2 split that minimizes total "times these two
    have been in the same match" for the two pairs.
    past_match_quartets: list of (player1_id, player2_id, player3_id, player4_id) for each past match.
    """
    ids = list(player_ids_ordered_by_points)
    if len(ids) % 4 != 0:
        raise ValueError("Player count must be divisible by 4")
    pair_counts = _count_shared_matches(past_match_quartets)
    result = []
    for i in range(0, len(ids), 4):
        a, b, c, d = ids[i], ids[i + 1], ids[i + 2], ids[i + 3]
        # Three ways to split into two teams of two
        splits = [
            ((a, b), (c, d)),
            ((a, c), (b, d)),
            ((a, d), (b, c)),
        ]
        def score_split(team1: tuple[int, int], team2: tuple[int, int]) -> int:
            k1 = _pair_key(team1[0], team1[1])
            k2 = _pair_key(team2[0], team2[1])
            return pair_counts.get(k1, 0) + pair_counts.get(k2, 0)
        best = min(splits, key=lambda s: score_split(s[0], s[1]))
        result.append(best)
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
