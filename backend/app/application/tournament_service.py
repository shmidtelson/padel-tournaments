"""Application service: tournament CRUD, players, rounds, matches, leaderboard."""

from app.domain.entities import Tournament, Player, Round, Match
from app.domain.repositories import (
    ITournamentRepository,
    IPlayerRepository,
    IRoundRepository,
    IMatchRepository,
    IOrganizationMemberRepository,
    IOrganizationRepository,
)
from app.domain.value_objects import TournamentFormat, PairingStrategy
from app.domain.services import (
    generate_random_pairs,
    generate_by_ranking_pairs,
    generate_similar_points_avoid_rematch_pairs,
    compute_match_points,
)
from app.application.dto import (
    CreateTournamentCommand,
    AddPlayerCommand,
    UpdateMatchScoreCommand,
    LeaderboardEntry,
    MatchDto,
    RoundDto,
)


class TournamentApplicationService:
    def __init__(
        self,
        tournament_repo: ITournamentRepository,
        player_repo: IPlayerRepository,
        round_repo: IRoundRepository,
        match_repo: IMatchRepository,
        org_member_repo: IOrganizationMemberRepository,
        org_repo: IOrganizationRepository | None = None,
    ):
        self._tournaments = tournament_repo
        self._players = player_repo
        self._rounds = round_repo
        self._matches = match_repo
        self._org_members = org_member_repo
        self._orgs = org_repo

    async def ensure_org_admin(self, user_id: int, organization_id: int) -> None:
        ok = await self._org_members.is_user_org_admin(user_id, organization_id)
        if not ok:
            raise PermissionError("User is not an admin of this organization")

    async def create_tournament(self, user_id: int, cmd: CreateTournamentCommand) -> Tournament:
        await self.ensure_org_admin(user_id, cmd.organization_id)
        if self._orgs:
            org = await self._orgs.get_by_id(cmd.organization_id)
            if not org or not org.is_approved():
                raise ValueError("Organization must be approved by a superuser before creating tournaments")
        slug = cmd.name.lower().replace(" ", "-")[:100]
        tournament = Tournament(
            id=0,
            organization_id=cmd.organization_id,
            name=cmd.name,
            format=cmd.format,
            slug=slug,
            status="draft",
            points_per_round=cmd.points_per_round,
            pairing_strategy=cmd.pairing_strategy,
        )
        return await self._tournaments.add(tournament)

    async def get_tournament(self, tournament_id: int) -> Tournament | None:
        return await self._tournaments.get_by_id(tournament_id)

    async def list_tournaments_for_user(self, user_id: int) -> list[Tournament]:
        organization_ids = await self._org_members.get_organization_ids_for_user(user_id)
        result = []
        for oid in organization_ids:
            tournaments = await self._tournaments.list_by_organization(oid)
            result.extend(tournaments)
        return list(result)

    async def list_players(self, tournament_id: int) -> list[Player]:
        return list(await self._players.list_by_tournament(tournament_id))

    async def add_player(self, user_id: int, cmd: AddPlayerCommand) -> Player:
        tournament = await self._tournaments.get_by_id(cmd.tournament_id)
        if not tournament:
            raise ValueError("Tournament not found")
        await self.ensure_org_admin(user_id, tournament.organization_id)
        player = Player(
            id=0,
            tournament_id=cmd.tournament_id,
            first_name=cmd.first_name,
            last_name=cmd.last_name,
            user_id=cmd.user_id,
            total_points=0,
        )
        return await self._players.add(player)

    def _resolve_pairing_strategy(self, tournament: Tournament) -> str:
        """Resolve effective pairing strategy: explicit or format default."""
        if tournament.pairing_strategy:
            return tournament.pairing_strategy
        if tournament.format == TournamentFormat.americano:
            return PairingStrategy.random.value
        return PairingStrategy.by_ranking.value

    async def generate_next_round(self, user_id: int, tournament_id: int) -> RoundDto | None:
        tournament = await self._tournaments.get_by_id(tournament_id)
        if not tournament:
            raise ValueError("Tournament not found")
        await self.ensure_org_admin(user_id, tournament.organization_id)
        if tournament.format not in (TournamentFormat.americano, TournamentFormat.mexicano):
            raise ValueError("Generate next round only for Americano/Mexicano")
        players = await self._players.list_by_tournament(tournament_id)
        if len(players) % 4 != 0:
            raise ValueError("Player count must be divisible by 4")
        existing_rounds = await self._rounds.list_by_tournament(tournament_id)
        next_index = len(existing_rounds)
        ordered = sorted(players, key=lambda p: -p.total_points)
        player_ids = [p.id for p in ordered]
        strategy = self._resolve_pairing_strategy(tournament)

        if strategy == PairingStrategy.random.value:
            pairs = generate_random_pairs(player_ids)
        elif strategy == PairingStrategy.by_ranking.value:
            pairs = generate_by_ranking_pairs(player_ids)
        elif strategy == PairingStrategy.similar_points_avoid_rematch.value:
            past_quartets: list[tuple[int, int, int, int]] = []
            for r in existing_rounds:
                matches = await self._matches.list_by_round(r.id)
                for m in matches:
                    past_quartets.append((m.player1_id, m.player2_id, m.player3_id, m.player4_id))
            pairs = generate_similar_points_avoid_rematch_pairs(player_ids, past_quartets)
        else:
            # Fallback: by format
            if tournament.format == TournamentFormat.americano:
                pairs = generate_random_pairs(player_ids)
            else:
                pairs = generate_by_ranking_pairs(player_ids)
        round_entity = Round(id=0, tournament_id=tournament_id, round_index=next_index)
        round_entity = await self._rounds.add(round_entity)
        match_dtos = []
        for (t1, t2) in pairs:
            match = Match(
                id=0,
                round_id=round_entity.id,
                player1_id=t1[0],
                player2_id=t1[1],
                player3_id=t2[0],
                player4_id=t2[1],
                score_team1=None,
                score_team2=None,
            )
            match = await self._matches.add(match)
            p1 = next(p for p in players if p.id == t1[0])
            p2 = next(p for p in players if p.id == t1[1])
            p3 = next(p for p in players if p.id == t2[0])
            p4 = next(p for p in players if p.id == t2[1])
            match_dtos.append(MatchDto(
                id=match.id,
                round_index=next_index,
                player1_id=match.player1_id,
                player2_id=match.player2_id,
                player3_id=match.player3_id,
                player4_id=match.player4_id,
                score_team1=None,
                score_team2=None,
                player1_name=p1.display_name(),
                player2_name=p2.display_name(),
                player3_name=p3.display_name(),
                player4_name=p4.display_name(),
            ))
        return RoundDto(round_index=next_index, matches=match_dtos)

    async def update_match_score(self, user_id: int, cmd: UpdateMatchScoreCommand) -> int:
        """Обновляет счёт матча. Возвращает tournament_id для рассылки SSE."""
        match = await self._matches.get_by_id(cmd.match_id)
        if not match:
            raise ValueError("Match not found")
        round_entity = await self._rounds.get_by_id(match.round_id)
        if not round_entity:
            raise ValueError("Round not found")
        tournament = await self._tournaments.get_by_id(round_entity.tournament_id)
        if not tournament:
            raise ValueError("Tournament not found")
        await self.ensure_org_admin(user_id, tournament.organization_id)
        tournament_id = round_entity.tournament_id
        if tournament.is_americano_or_mexicano() and tournament.points_per_round:
            if match.score_team1 is not None and match.score_team2 is not None:
                old_p1, old_p2, old_p3, old_p4 = compute_match_points(
                    match.score_team1, match.score_team2, tournament.points_per_round
                )
                for pid, pts in [(match.player1_id, old_p1), (match.player2_id, old_p2), (match.player3_id, old_p3), (match.player4_id, old_p4)]:
                    pl = await self._players.get_by_id(pid)
                    if pl:
                        pl.total_points -= pts
                        await self._players.save(pl)
            p1_pts, p2_pts, p3_pts, p4_pts = compute_match_points(
                cmd.score_team1, cmd.score_team2, tournament.points_per_round
            )
            for pid, pts in [(match.player1_id, p1_pts), (match.player2_id, p2_pts), (match.player3_id, p3_pts), (match.player4_id, p4_pts)]:
                player = await self._players.get_by_id(pid)
                if player:
                    player.total_points += pts
                    await self._players.save(player)
        match.score_team1 = cmd.score_team1
        match.score_team2 = cmd.score_team2
        await self._matches.save(match)
        return tournament_id

    async def get_leaderboard(self, tournament_id: int) -> list[LeaderboardEntry]:
        players = await self._players.list_by_tournament(tournament_id)
        sorted_players = sorted(players, key=lambda p: -p.total_points)
        return [
            LeaderboardEntry(rank=i + 1, player_id=p.id, first_name=p.first_name, last_name=p.last_name, total_points=p.total_points)
            for i, p in enumerate(sorted_players)
        ]

    async def get_rounds_with_matches(self, tournament_id: int) -> list[RoundDto]:
        rounds = await self._rounds.list_by_tournament(tournament_id)
        players = await self._players.list_by_tournament(tournament_id)
        player_map = {p.id: p for p in players}
        result = []
        for r in rounds:
            matches = await self._matches.list_by_round(r.id)
            match_dtos = []
            for m in matches:
                p1 = player_map.get(m.player1_id)
                p2 = player_map.get(m.player2_id)
                p3 = player_map.get(m.player3_id)
                p4 = player_map.get(m.player4_id)
                match_dtos.append(MatchDto(
                    id=m.id,
                    round_index=r.round_index,
                    player1_id=m.player1_id,
                    player2_id=m.player2_id,
                    player3_id=m.player3_id,
                    player4_id=m.player4_id,
                    score_team1=m.score_team1,
                    score_team2=m.score_team2,
                    player1_name=p1.display_name() if p1 else "",
                    player2_name=p2.display_name() if p2 else "",
                    player3_name=p3.display_name() if p3 else "",
                    player4_name=p4.display_name() if p4 else "",
                ))
            result.append(RoundDto(round_index=r.round_index, matches=match_dtos))
        return result
