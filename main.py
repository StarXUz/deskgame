from pathlib import Path
import socket
import subprocess
from urllib.parse import urlparse

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.database import BASE_DIR, init_db, write_lock
from backend.schemas import ScoreSubmit
from backend.tournament import (
    advancement_chart,
    export_report,
    export_live_scoreboard,
    build_team_bracket,
    generate_round,
    generate_judge_accounts,
    get_tables,
    import_players_from_excel,
    judge_login,
    leaderboard,
    list_judge_submissions,
    list_judges,
    list_players,
    list_rounds,
    pool_status,
    player_status,
    refresh_player_qrcodes,
    score_page_data,
    seating_chart,
    reset_judge_password,
    set_table_seat,
    submit_score,
    team_rankings,
    update_judge,
    update_transition,
)


app = FastAPI(title="桌游比赛管理系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

STATIC_DIR = BASE_DIR / "static"
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/players/import")
async def import_players(request: Request, file: UploadFile = File(...), force: bool = False) -> dict:
    content = await file.read()
    async with write_lock:
        return import_players_from_excel(content, force, qr_base_url(request))


@app.get("/api/players")
def players(transition_only: bool = False) -> list[dict]:
    return list_players(transition_only)


@app.patch("/api/players/transition")
async def patch_transition(payload: dict) -> dict:
    async with write_lock:
        return update_transition(payload.get("players", []))


@app.get("/api/pool-status")
def api_pool_status() -> dict:
    return pool_status()


@app.get("/api/rounds")
def rounds() -> list[dict]:
    return list_rounds()


def local_lan_ip() -> str:
    for interface in ("en0", "en1"):
        try:
            value = subprocess.check_output(
                ["ipconfig", "getifaddr", interface],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            if value:
                return value
        except Exception:
            pass
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def qr_base_url(request: Request) -> str:
    parsed = urlparse(str(request.base_url))
    host = parsed.hostname or "127.0.0.1"
    if host in {"127.0.0.1", "localhost", "0.0.0.0", "::1"}:
        host = local_lan_ip()
    return f"{parsed.scheme}://{host}:8000"


@app.post("/api/rounds/{round_no}/generate")
async def api_generate_round(round_no: int, request: Request) -> dict:
    async with write_lock:
        return generate_round(round_no, qr_base_url(request))


@app.post("/api/players/refresh-qrcodes")
async def api_refresh_player_qrcodes(request: Request) -> dict:
    async with write_lock:
        return refresh_player_qrcodes(qr_base_url(request))


@app.get("/api/judges")
def api_judges() -> list[dict]:
    return list_judges()


@app.post("/api/judges/generate")
async def api_generate_judges(payload: dict) -> dict:
    async with write_lock:
        return generate_judge_accounts(int(payload.get("count", 20)))


@app.patch("/api/judges/{judge_id}")
async def api_update_judge(judge_id: int, payload: dict) -> dict:
    async with write_lock:
        return update_judge(judge_id, payload)


@app.post("/api/judges/{judge_id}/reset-password")
async def api_reset_judge_password(judge_id: int) -> dict:
    async with write_lock:
        return reset_judge_password(judge_id)


@app.get("/api/judge-submissions")
def api_judge_submissions() -> list[dict]:
    return list_judge_submissions()


@app.post("/api/judge/login")
def api_judge_login(payload: dict) -> dict:
    return judge_login(payload.get("account", ""), payload.get("password", ""), payload.get("judge_name", ""))


@app.get("/api/rounds/{round_no}/tables")
def api_round_tables(round_no: int) -> list[dict]:
    return get_tables(round_no)


@app.get("/api/rounds/{round_no}/seating-chart")
def api_seating_chart(round_no: int, priority: str = "small_group_first") -> dict:
    return seating_chart(round_no, priority)


@app.get("/api/advancement-chart")
def api_advancement_chart() -> dict:
    return advancement_chart()


@app.patch("/api/rounds/{round_no}/tables/{table_id}/seat")
async def api_set_table_seat(round_no: int, table_id: int, payload: dict) -> dict:
    async with write_lock:
        return set_table_seat(round_no, table_id, payload.get("seat_no"))


@app.get("/api/score")
def api_score(token: str) -> dict:
    return score_page_data(token)


@app.get("/api/player-status")
def api_player_status(token: str) -> dict:
    return player_status(token)


@app.post("/api/score/submit")
async def api_submit_score(payload: ScoreSubmit, request: Request) -> dict:
    async with write_lock:
        client_ip = request.client.host if request.client else ""
        user_agent = request.headers.get("user-agent", "")
        return submit_score(payload.model_dump(), client_ip, user_agent)


@app.get("/api/leaderboard")
def api_leaderboard(limit: int = 0) -> list[dict]:
    return leaderboard(limit)


@app.get("/api/team-leaderboard")
def api_team_leaderboard(limit: int = 0, metric: str = "total") -> list[dict]:
    teams = team_rankings(metric=metric)
    return teams[:limit] if limit and limit > 0 else teams


@app.get("/api/bracket")
def api_bracket(age_group: str | None = None, game_type: str | None = None, metric: str = "final") -> dict:
    return build_team_bracket(age_group, game_type, metric)


@app.get("/api/export")
def api_export() -> FileResponse:
    path = export_report()
    return FileResponse(
        path,
        filename=path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.get("/api/export/live-scoreboard")
def api_export_live_scoreboard() -> FileResponse:
    path = export_live_scoreboard()
    return FileResponse(
        path,
        filename=path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def frontend_file() -> Path:
    index = FRONTEND_DIST / "index.html"
    if index.exists():
        return index
    return BASE_DIR / "README.md"


@app.get("/{full_path:path}")
def spa(full_path: str) -> FileResponse:
    target = FRONTEND_DIST / full_path
    if target.exists() and target.is_file():
        return FileResponse(target)
    return FileResponse(frontend_file())
