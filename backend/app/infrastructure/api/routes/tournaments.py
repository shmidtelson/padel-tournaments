"""Tournament API routes. SSE: поток событий по турниру при обновлении матчей/раундов."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.application.dto import MatchDto
from app.application.tournament_service import TournamentApplicationService
from app.infrastructure.api.dependencies import get_tournament_service, require_current_user_id
from app.infrastructure.api.schemas import (
    AddPlayerRequest,
    CreateTournamentRequest,
    LeaderboardEntryResponse,
    MatchResponse,
    PlayerResponse,
    RoundResponse,
    TournamentResponse,
    UpdateMatchScoreRequest,
)
from app.infrastructure.sse.broadcaster import broadcaster

router = APIRouter(prefix="/tournaments", tags=["tournaments"])


def _tournament_to_response(t):
    return TournamentResponse(
        id=t.id,
        organization_id=t.organization_id,
        name=t.name,
        format=t.format,
        slug=t.slug,
        status=t.status,
        points_per_round=t.points_per_round,
        pairing_strategy=getattr(t, "pairing_strategy", None),
    )


def _match_to_response(m: MatchDto) -> MatchResponse:
    return MatchResponse(
        id=m.id,
        round_index=m.round_index,
        player1_id=m.player1_id,
        player2_id=m.player2_id,
        player3_id=m.player3_id,
        player4_id=m.player4_id,
        score_team1=m.score_team1,
        score_team2=m.score_team2,
        player1_name=m.player1_name,
        player2_name=m.player2_name,
        player3_name=m.player3_name,
        player4_name=m.player4_name,
    )


@router.post("", response_model=TournamentResponse)
async def create_tournament(
    body: CreateTournamentRequest,
    user_id: Annotated[int, Depends(require_current_user_id)],
    svc: Annotated[TournamentApplicationService, Depends(get_tournament_service)],
):
    try:
        from app.application.dto import CreateTournamentCommand

        cmd = CreateTournamentCommand(
            organization_id=body.organization_id,
            name=body.name,
            format=body.format,
            points_per_round=body.points_per_round,
            pairing_strategy=body.pairing_strategy,
        )
        t = await svc.create_tournament(user_id, cmd)
        return _tournament_to_response(t)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("", response_model=list[TournamentResponse])
async def list_tournaments(
    user_id: Annotated[int, Depends(require_current_user_id)],
    svc: Annotated[TournamentApplicationService, Depends(get_tournament_service)],
):
    tournaments = await svc.list_tournaments_for_user(user_id)
    return [_tournament_to_response(t) for t in tournaments]


@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(
    tournament_id: int,
    svc: Annotated[TournamentApplicationService, Depends(get_tournament_service)],
):
    t = await svc.get_tournament(tournament_id)
    if not t:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return _tournament_to_response(t)


@router.get("/{tournament_id}/players", response_model=list[PlayerResponse])
async def list_players(
    tournament_id: int,
    svc: Annotated[TournamentApplicationService, Depends(get_tournament_service)],
):
    players = await svc.list_players(tournament_id)
    return [
        PlayerResponse(
            id=p.id,
            tournament_id=p.tournament_id,
            first_name=p.first_name,
            last_name=p.last_name,
            user_id=p.user_id,
            total_points=p.total_points,
        )
        for p in players
    ]


@router.post("/{tournament_id}/players", response_model=PlayerResponse)
async def add_player(
    tournament_id: int,
    body: AddPlayerRequest,
    user_id: Annotated[int, Depends(require_current_user_id)],
    svc: Annotated[TournamentApplicationService, Depends(get_tournament_service)],
):
    try:
        from app.application.dto import AddPlayerCommand

        cmd = AddPlayerCommand(
            tournament_id=tournament_id,
            first_name=body.first_name,
            last_name=body.last_name,
            user_id=body.user_id,
        )
        p = await svc.add_player(user_id, cmd)
        return PlayerResponse(
            id=p.id,
            tournament_id=p.tournament_id,
            first_name=p.first_name,
            last_name=p.last_name,
            user_id=p.user_id,
            total_points=p.total_points,
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/{tournament_id}/rounds/next", response_model=RoundResponse)
async def generate_next_round(
    tournament_id: int,
    user_id: Annotated[int, Depends(require_current_user_id)],
    svc: Annotated[TournamentApplicationService, Depends(get_tournament_service)],
):
    try:
        r = await svc.generate_next_round(user_id, tournament_id)
        if not r:
            raise HTTPException(status_code=400, detail="No next round generated")
        await broadcaster.publish(tournament_id, "rounds_updated", {"round_index": r.round_index})
        return RoundResponse(
            round_index=r.round_index, matches=[_match_to_response(m) for m in r.matches]
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/{tournament_id}/rounds", response_model=list[RoundResponse])
async def list_rounds(
    tournament_id: int,
    svc: Annotated[TournamentApplicationService, Depends(get_tournament_service)],
):
    rounds = await svc.get_rounds_with_matches(tournament_id)
    return [
        RoundResponse(round_index=r.round_index, matches=[_match_to_response(m) for m in r.matches])
        for r in rounds
    ]


@router.get("/{tournament_id}/stream")
async def tournament_stream(tournament_id: int):
    """
    SSE-поток событий турнира. При обновлении матча (PATCH /matches/{id}) или
    добавлении раунда (POST .../rounds/next) все подписчики получают событие.
    События: match_updated, rounds_updated. Клиент может перезапросить раунды/лидерборд.
    """
    return EventSourceResponse(broadcaster.subscribe(tournament_id))


@router.patch("/matches/{match_id}")
async def update_match_score(
    match_id: int,
    body: UpdateMatchScoreRequest,
    user_id: Annotated[int, Depends(require_current_user_id)],
    svc: Annotated[TournamentApplicationService, Depends(get_tournament_service)],
):
    try:
        from app.application.dto import UpdateMatchScoreCommand

        cmd = UpdateMatchScoreCommand(
            match_id=match_id, score_team1=body.score_team1, score_team2=body.score_team2
        )
        tournament_id = await svc.update_match_score(user_id, cmd)
        await broadcaster.publish(tournament_id, "match_updated", {"match_id": match_id})
        return {"ok": True}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/{tournament_id}/leaderboard", response_model=list[LeaderboardEntryResponse])
async def get_leaderboard(
    tournament_id: int,
    svc: Annotated[TournamentApplicationService, Depends(get_tournament_service)],
):
    entries = await svc.get_leaderboard(tournament_id)
    return [
        LeaderboardEntryResponse(
            rank=e.rank,
            player_id=e.player_id,
            first_name=e.first_name,
            last_name=e.last_name,
            total_points=e.total_points,
        )
        for e in entries
    ]
