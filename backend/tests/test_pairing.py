"""Unit tests for domain pairing algorithms (no DB, no app)."""

import pytest
from app.domain.services import (
    generate_random_pairs,
    generate_americano_pairs,
    generate_by_ranking_pairs,
    generate_mexicano_pairs,
    generate_similar_points_avoid_rematch_pairs,
    compute_match_points,
)


# --- Random / Americano ---


def test_random_pairs_count():
    ids = list(range(8))
    pairs = generate_random_pairs(ids)
    assert len(pairs) == 2  # 8 players -> 2 matches
    for (t1, t2) in pairs:
        assert len(t1) == 2 and len(t2) == 2
        assert len(set(t1) | set(t2)) == 4  # 4 distinct players per match


def test_random_pairs_uses_all_players():
    ids = list(range(12))
    pairs = generate_random_pairs(ids)
    used = set()
    for (t1, t2) in pairs:
        for p in t1 + t2:
            used.add(p)
    assert used == set(ids)


def test_random_pairs_requires_multiple_of_four():
    with pytest.raises(ValueError, match="divisible by 4"):
        generate_random_pairs([1, 2, 3, 4, 5])
    with pytest.raises(ValueError, match="divisible by 4"):
        generate_random_pairs([1, 2, 3])


def test_americano_pairs_same_as_random():
    ids = [10, 20, 30, 40, 50, 60, 70, 80]
    # Both produce valid pairings; americano is alias
    p_rand = generate_random_pairs(ids)
    p_amer = generate_americano_pairs(ids)
    assert len(p_rand) == len(p_amer) == 2
    for (t1, t2) in p_amer:
        assert set(t1) | set(t2) <= set(ids)


# --- By ranking (Mexicano) ---


def test_by_ranking_pairs_structure():
    # 1st=100, 2nd=90, 3rd=80, 4th=70 -> team1 = 1+3, team2 = 2+4
    ids = [1, 2, 3, 4, 5, 6, 7, 8]
    pairs = generate_by_ranking_pairs(ids)
    assert len(pairs) == 2
    # First match: (1,3) vs (2,4)
    assert pairs[0] == ((1, 3), (2, 4))
    # Second match: (5,7) vs (6,8)
    assert pairs[1] == ((5, 7), (6, 8))


def test_by_ranking_requires_multiple_of_four():
    with pytest.raises(ValueError, match="divisible by 4"):
        generate_by_ranking_pairs([1, 2, 3])
    with pytest.raises(ValueError, match="divisible by 4"):
        generate_by_ranking_pairs([1, 2, 3, 4, 5])


def test_mexicano_pairs_same_as_by_ranking():
    ids = [11, 22, 33, 44]
    p_by = generate_by_ranking_pairs(ids)
    p_mex = generate_mexicano_pairs(ids)
    assert p_by == p_mex == [((11, 33), (22, 44))]


# --- Similar points avoid rematch ---


def test_similar_points_avoid_rematch_no_past_matches():
    ids = [1, 2, 3, 4, 5, 6, 7, 8]
    pairs = generate_similar_points_avoid_rematch_pairs(ids, [])
    assert len(pairs) == 2
    # With no history, first split (a,b),(c,d) has score 0 so is chosen
    assert pairs[0] == ((1, 2), (3, 4))
    assert pairs[1] == ((5, 6), (7, 8))


def test_similar_points_avoid_rematch_prefers_fresh_pairs():
    # Past: (1,2) played together in 3 matches, (3,4) in 1. So for quartet [1,2,3,4]:
    # Split (1,2),(3,4) -> score 3+1 = 4
    # Split (1,3),(2,4) or (1,4),(2,3) -> score 1+1 = 2
    # Algorithm picks a 2-score split
    ids = [1, 2, 3, 4]
    past = [(1, 2, 3, 4), (1, 2, 5, 6), (1, 2, 7, 8)]  # (1,2) together 3 times
    pairs = generate_similar_points_avoid_rematch_pairs(ids, past)
    assert len(pairs) == 1
    (t1, t2) = pairs[0]
    assert set(t1) | set(t2) == {1, 2, 3, 4}
    assert (t1, t2) != ((1, 2), (3, 4))


def test_similar_points_avoid_rematch_requires_multiple_of_four():
    with pytest.raises(ValueError, match="divisible by 4"):
        generate_similar_points_avoid_rematch_pairs([1, 2, 3], [])
    with pytest.raises(ValueError, match="divisible by 4"):
        generate_similar_points_avoid_rematch_pairs([1, 2, 3, 4, 5], [])


def test_similar_points_avoid_rematch_multiple_groups():
    ids = [1, 2, 3, 4, 5, 6, 7, 8]
    # (1,2) and (5,6) appear often so (1,2),(3,4) and (5,6),(7,8) have higher score
    past = [(1, 2, 3, 4), (1, 2, 5, 6), (1, 2, 7, 8), (5, 6, 7, 8), (5, 6, 1, 2), (5, 6, 3, 4)]
    pairs = generate_similar_points_avoid_rematch_pairs(ids, past)
    assert len(pairs) == 2
    (t1a, t2a) = pairs[0]
    assert set(t1a) | set(t2a) == {1, 2, 3, 4}
    assert (t1a, t2a) != ((1, 2), (3, 4))
    (t1b, t2b) = pairs[1]
    assert set(t1b) | set(t2b) == {5, 6, 7, 8}
    assert (t1b, t2b) != ((5, 6), (7, 8))


# --- 7 courts, 28 players (2v2 per court) ---

COURTS = 7
PLAYERS_PER_MATCH = 4  # 2v2
PLAYERS_28 = 28  # 7 courts * 4 players


def test_seven_courts_random_28_players():
    """7 courts: 28 players, random pairing → 7 matches, 4 players per match, each player once."""
    ids = list(range(1, PLAYERS_28 + 1))
    pairs = generate_random_pairs(ids)
    assert len(pairs) == COURTS, "7 courts = 7 matches"
    used = set()
    for (t1, t2) in pairs:
        assert len(t1) == 2 and len(t2) == 2, "2v2 per match"
        match_players = set(t1) | set(t2)
        assert len(match_players) == PLAYERS_PER_MATCH, "4 distinct players per court"
        assert not (match_players & used), "no player in two matches"
        used |= match_players
    assert used == set(ids), "all 28 players assigned to exactly one court"


def test_seven_courts_by_ranking_28_players():
    """7 courts: 28 players ordered by points → 7 matches, weak+strong vs weak+strong per court."""
    ids = list(range(1, PLAYERS_28 + 1))  # id 1 = best (rank 1), 28 = worst (rank 28)
    pairs = generate_by_ranking_pairs(ids)
    assert len(pairs) == COURTS
    used = set()
    for (t1, t2) in pairs:
        assert len(t1) == 2 and len(t2) == 2
        match_players = set(t1) | set(t2)
        assert len(match_players) == PLAYERS_PER_MATCH
        assert not (match_players & used)
        used |= match_players
    assert used == set(ids)
    # First court: ranks 1,2,3,4 → team1 = 1+3, team2 = 2+4
    assert pairs[0] == ((1, 3), (2, 4))
    # Second court: ranks 5,6,7,8
    assert pairs[1] == ((5, 7), (6, 8))
    # Last court: ranks 25,26,27,28
    assert pairs[6] == ((25, 27), (26, 28))


def test_seven_courts_similar_points_avoid_rematch_28_players():
    """7 courts: 28 players, similar points + avoid rematch → 7 matches, no duplicate pairs preferred."""
    ids = list(range(1, PLAYERS_28 + 1))
    # Simulate one past round: 7 matches (same structure as by_ranking for simplicity)
    past_round = [
        (1, 3, 2, 4), (5, 7, 6, 8), (9, 11, 10, 12), (13, 15, 14, 16),
        (17, 19, 18, 20), (21, 23, 22, 24), (25, 27, 26, 28),
    ]
    pairs = generate_similar_points_avoid_rematch_pairs(ids, past_round)
    assert len(pairs) == COURTS
    used = set()
    for (t1, t2) in pairs:
        assert len(t1) == 2 and len(t2) == 2
        match_players = set(t1) | set(t2)
        assert len(match_players) == PLAYERS_PER_MATCH
        assert not (match_players & used)
        used |= match_players
    assert used == set(ids)
    # First court (1,2,3,4): past had (1,3) vs (2,4). So (1,3) and (2,4) have count 1 each; other splits too.
    # All three splits have same score for one past match, so we get one of them. Just check we got valid pairs.
    (t1, t2) = pairs[0]
    assert set(t1) | set(t2) == {1, 2, 3, 4}


def test_seven_courts_similar_points_avoid_rematch_28_players_two_rounds():
    """After 2 rounds with same pairing, round 3 should prefer different pairs on each court."""
    ids = list(range(1, PLAYERS_28 + 1))
    # Two past rounds, same pairing each time: (1,3)/(2,4), (5,7)/(6,8), ...
    past = [
        (1, 3, 2, 4), (5, 7, 6, 8), (9, 11, 10, 12), (13, 15, 14, 16),
        (17, 19, 18, 20), (21, 23, 22, 24), (25, 27, 26, 28),
    ] * 2
    pairs = generate_similar_points_avoid_rematch_pairs(ids, past)
    assert len(pairs) == COURTS
    # First court: (1,3) and (2,4) each have count 2; (1,2),(3,4) and (1,4),(2,3) have 1+1=2.
    # So (1,3),(2,4) has score 4, others have 2 → algorithm picks (1,2),(3,4) or (1,4),(2,3)
    (t1, t2) = pairs[0]
    assert set(t1) | set(t2) == {1, 2, 3, 4}
    assert (t1, t2) != ((1, 3), (2, 4)), "should avoid repeating same teams on court 1"


# --- compute_match_points ---


def test_compute_match_points():
    p1, p2, p3, p4 = compute_match_points(6, 4, 10)
    assert (p1, p2, p3, p4) == (6, 6, 4, 4)


def test_compute_match_points_tie():
    p1, p2, p3, p4 = compute_match_points(5, 5, 10)
    assert (p1, p2, p3, p4) == (5, 5, 5, 5)
