AGE_GROUPS = ["小学低年级组", "小学高年级组", "初中组"]
GAME_PANDA = "大熊猫国家公园"
GAME_SNOW = "雪山之巅·三江源"
GAME_RAINFOREST = "雨林奇境"
GAMES = [GAME_PANDA, GAME_SNOW, GAME_RAINFOREST]
GAME_ALIASES = {
    "游戏A": GAME_PANDA,
    "游戏B": GAME_SNOW,
    "游戏C": GAME_RAINFOREST,
}

ROUND_STATUS = ["未开始", "进行中", "已结束"]
TRANSITION_CHOICES = ["自由人补位", "跟随原学校"]
IDENTITY_NORMAL = "正常"
IDENTITY_FREE_AGENT = "自由人"
IDENTITY_ORIGINAL_SCHOOL = "原校特批"

SCORE_MAP = {
    4: [5, 3, 2, 1],
    3: [5, 3, 2],
    2: [5, 3],
    1: [5],
}

PRELIM_ROUNDS = {1, 2, 3}
FINAL_ROUNDS = {4, 5, 6}
