import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException

from backend import database, tournament


class ScoreCorrectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_db_path = database.DB_PATH
        database.DB_PATH = Path(self.temp_dir.name) / "test.sqlite3"
        database.init_db()

        with database.get_conn() as conn:
            for index in range(1, 5):
                conn.execute(
                    """
                    INSERT INTO players(name, team_name, age_group, game_type, seed_rank)
                    VALUES(?, ?, '小学低年级组', '大熊猫国家公园', ?)
                    """,
                    (f"选手{index}", f"队伍{index}", index),
                )
            self.player_ids = [row["id"] for row in conn.execute("SELECT id FROM players ORDER BY id").fetchall()]
            self.round1_id = conn.execute("SELECT id FROM rounds WHERE round_no = 1").fetchone()["id"]
            self.round2_id = conn.execute("SELECT id FROM rounds WHERE round_no = 2").fetchone()["id"]
            self.table_id = conn.execute(
                """
                INSERT INTO tables(
                    round_id, table_no, age_group, game_type, player_ids_json,
                    is_bye, participant_count, submitted_at
                ) VALUES(?, 'R1-01', '小学低年级组', '大熊猫国家公园', ?, 0, 4, ?)
                """,
                (self.round1_id, json.dumps(self.player_ids), datetime.now().isoformat(timespec="seconds")),
            ).lastrowid
            for rank, player_id in enumerate(self.player_ids, start=1):
                conn.execute(
                    """
                    INSERT INTO scores(player_id, round_id, table_id, table_rank, round_score, is_absent, is_advanced)
                    VALUES(?, ?, ?, ?, ?, 0, ?)
                    """,
                    (player_id, self.round1_id, self.table_id, rank, [5, 3, 2, 1][rank - 1], 1 if rank <= 2 else 0),
                )
            judge_id = conn.execute(
                """
                INSERT INTO judges(account, password_hash, initial_password, created_at)
                VALUES('J001', 'test', '000000', ?)
                """,
                (datetime.now().isoformat(timespec="seconds"),),
            ).lastrowid
            conn.execute(
                """
                INSERT INTO judge_submissions(
                    judge_id, round_id, table_id, judge_name, submitted_at, scores_json
                ) VALUES(?, ?, ?, '裁判甲', ?, ?)
                """,
                (
                    judge_id,
                    self.round1_id,
                    self.table_id,
                    datetime.now().isoformat(timespec="seconds"),
                    json.dumps([{"player_id": player_id, "score": score} for player_id, score in zip(self.player_ids, [5, 3, 2, 1])]),
                ),
            )

    def tearDown(self) -> None:
        database.DB_PATH = self.previous_db_path
        self.temp_dir.cleanup()

    def test_corrects_scores_and_records_an_audit_entry(self) -> None:
        result = tournament.correct_score(
            1,
            self.table_id,
            {
                "operator_name": "管理员测试",
                "reason": "裁判将前两名分数填反",
                "results": [
                    {"player_id": self.player_ids[0], "score": 3, "absent": False},
                    {"player_id": self.player_ids[1], "score": 5, "absent": False},
                    {"player_id": self.player_ids[2], "score": 2, "absent": False},
                    {"player_id": self.player_ids[3], "score": 1, "absent": False},
                ],
            },
        )
        self.assertTrue(result["ok"])

        with database.get_conn() as conn:
            scores = conn.execute(
                "SELECT player_id, table_rank, round_score, is_advanced FROM scores WHERE table_id = ? ORDER BY table_rank",
                (self.table_id,),
            ).fetchall()
            audit = conn.execute("SELECT operator_name, reason, old_scores_json, new_scores_json FROM score_corrections").fetchone()

        self.assertEqual([row["player_id"] for row in scores], [self.player_ids[1], self.player_ids[0], self.player_ids[2], self.player_ids[3]])
        self.assertEqual([row["round_score"] for row in scores], [5, 3, 2, 1])
        self.assertEqual([row["is_advanced"] for row in scores], [1, 1, 0, 0])
        self.assertEqual(audit["operator_name"], "管理员测试")
        self.assertIn("填反", audit["reason"])
        self.assertEqual(len(json.loads(audit["old_scores_json"])), 4)
        self.assertEqual(len(json.loads(audit["new_scores_json"])), 4)

        submissions = tournament.list_judge_submissions()
        self.assertEqual(submissions[0]["correction_count"], 1)
        self.assertEqual(submissions[0]["scores"][0]["player_id"], self.player_ids[1])

    def test_rejects_correction_after_next_round_is_generated(self) -> None:
        with database.get_conn() as conn:
            conn.execute(
                """
                INSERT INTO tables(
                    round_id, table_no, age_group, game_type, player_ids_json,
                    is_bye, participant_count
                ) VALUES(?, 'R2-01', '小学低年级组', '大熊猫国家公园', ?, 0, 4)
                """,
                (self.round2_id, json.dumps(self.player_ids)),
            )

        with self.assertRaises(HTTPException) as context:
            tournament.correct_score(
                1,
                self.table_id,
                {
                    "operator_name": "管理员测试",
                    "reason": "测试后续轮次保护",
                    "results": [
                        {"player_id": self.player_ids[0], "score": 5, "absent": False},
                        {"player_id": self.player_ids[1], "score": 3, "absent": False},
                        {"player_id": self.player_ids[2], "score": 2, "absent": False},
                        {"player_id": self.player_ids[3], "score": 1, "absent": False},
                    ],
                },
            )
        self.assertEqual(context.exception.status_code, 409)


if __name__ == "__main__":
    unittest.main()
