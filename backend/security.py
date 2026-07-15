import base64
import hashlib
import hmac
import json
import os
import secrets
import time


SECRET = os.environ.get("TOURNAMENT_SECRET", "local-lan-tournament-secret-change-me")


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unb64(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def sign_payload(payload: dict) -> str:
    body = _b64(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    sig = hmac.new(SECRET.encode("utf-8"), body.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"


def make_table_token(table_id: int, round_id: int) -> str:
    return sign_payload({"table_id": table_id, "round_id": round_id, "ts": int(time.time())})


def make_player_token(player_id: int | None = None, player_code: str | None = None) -> str:
    payload = {"kind": "player"}
    if player_code:
        payload["player_code"] = player_code
    elif player_id is not None:
        payload["player_id"] = player_id
    else:
        raise ValueError("缺少选手标识")
    return sign_payload(payload)


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(12)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("ascii"), 120_000).hex()
    return f"pbkdf2_sha256${salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        method, salt, digest = password_hash.split("$", 2)
    except ValueError:
        return False
    if method != "pbkdf2_sha256":
        return False
    expected = hash_password(password, salt).split("$", 2)[2]
    return hmac.compare_digest(expected, digest)


def make_judge_token(judge_id: int, account: str, judge_name: str) -> str:
    return sign_payload(
        {
            "kind": "judge",
            "judge_id": judge_id,
            "account": account,
            "judge_name": judge_name,
            "ts": int(time.time()),
        }
    )


def verify_signed_token(token: str) -> dict:
    try:
        body, sig = token.rsplit(".", 1)
    except ValueError as exc:
        raise ValueError("二维码格式无效") from exc
    expected = hmac.new(SECRET.encode("utf-8"), body.encode("ascii"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        raise ValueError("二维码签名无效")
    return json.loads(_unb64(body).decode("utf-8"))


def verify_token(token: str) -> dict:
    payload = verify_signed_token(token)
    if "table_id" not in payload or "round_id" not in payload:
        raise ValueError("二维码内容缺少桌位信息")
    return payload


def verify_player_token(token: str) -> dict:
    payload = verify_signed_token(token)
    if payload.get("kind") != "player" or ("player_id" not in payload and "player_code" not in payload):
        raise ValueError("选手二维码内容无效")
    return payload


def verify_judge_token(token: str) -> dict:
    payload = verify_signed_token(token)
    if payload.get("kind") != "judge" or "judge_id" not in payload or "judge_name" not in payload:
        raise ValueError("裁判登录已失效，请重新登录")
    return payload
