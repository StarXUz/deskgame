<template>
  <div class="score-page">
    <div class="score-card">
      <div class="score-header">
        <h1>{{ title }}</h1>
        <div v-if="scoreData">{{ scoreData.age_group }} · {{ scoreData.game_type }}</div>
      </div>

      <van-empty v-if="loadError" :description="loadError" />

      <template v-else-if="scoreData">
        <van-notice-bar v-if="scoreData.submitted" text="本桌成绩已录入，不可重复提交。" />
        <template v-else>
          <van-cell-group v-if="!judgeToken" inset style="margin-top: 14px">
            <van-field v-model="judgeRealName" label="裁判姓名" placeholder="请输入本人姓名" />
            <van-field v-model="judgeAccount" label="裁判账号" placeholder="例如 J001" />
            <van-field v-model="judgePassword" label="密码" type="password" placeholder="6位数字密码" />
            <div style="padding: 12px 16px">
              <van-button block type="primary" :loading="loggingIn" @click="judgeLogin">裁判登录后录分</van-button>
            </div>
          </van-cell-group>
          <van-empty v-if="!judgeToken" description="请先登录裁判账号，登录后才会显示分数录入表。" />

          <template v-else>
            <van-notice-bar :text="`当前裁判：${judgeName}`" />
            <div class="rule-card">
              <strong>录入规则</strong>
              <span>分数选 5 / 3 / 2 / 1，缺席自动 0 分；同分晋级时由系统按成绩提交时间判断。</span>
            </div>
            <van-cell-group inset>
              <van-cell v-for="item in formRows" :key="item.player_id" class="score-player" :class="{ absent: item.absent }">
                <template #title>
                  <div class="player-title-row">
                    <strong>{{ item.name }}</strong>
                    <van-tag v-if="item.absent" type="danger">缺席</van-tag>
                  </div>
                  <van-tag v-if="item.identity_label === '自由人'" type="warning" style="margin-left: 8px">自由人</van-tag>
                </template>
                <template #label>{{ item.team_name }}</template>
                <template #value>
                  <div class="score-controls">
                    <van-checkbox v-model="item.absent">缺席</van-checkbox>
                    <div class="select-row">
                      <label>
                        <span>分数</span>
                        <select v-model.number="item.score" :disabled="item.absent" class="score-select">
                          <option :value="null">选择</option>
                          <option v-for="score in scoreOptions" :key="score" :value="score">{{ score }} 分</option>
                        </select>
                      </label>
                    </div>
                  </div>
                </template>
              </van-cell>
            </van-cell-group>

            <div style="padding: 16px">
              <van-button block type="primary" size="large" :loading="submitting" @click="submit">
                提交本桌成绩
              </van-button>
              <van-button block plain size="small" style="margin-top: 10px" @click="logoutJudge">
                切换裁判账号
              </van-button>
            </div>
          </template>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { showFailToast, showSuccessToast } from 'vant'
import { useRoute } from 'vue-router'
import { api, errorText } from '../api/client'

interface ScorePlayer {
  id: number
  name: string
  team_name: string
  identity_label: string
}

interface ScoreData {
  valid: boolean
  submitted: boolean
  round_no: number
  table_no: string
  age_group: string
  game_type: string
  has_free_agent: boolean
  players: ScorePlayer[]
}

interface FormRow {
  player_id: number
  name: string
  team_name: string
  identity_label: string
  score: number | null
  absent: boolean
}

const route = useRoute()
const token = computed(() => String(route.query.token || ''))
const scoreData = ref<ScoreData | null>(null)
const formRows = ref<FormRow[]>([])
const loadError = ref('')
const submitting = ref(false)
const loggingIn = ref(false)
const judgeRealName = ref('')
const judgeAccount = ref('')
const judgePassword = ref('')
const judgeToken = ref('')
const judgeName = ref('')
const title = computed(() => (scoreData.value ? `第 ${scoreData.value.round_no} 轮 ${scoreData.value.table_no}` : '成绩录入'))
const scoreOptions = [5, 3, 2, 1]

watch(
  () => formRows.value.map((item) => item.absent).join(','),
  () => {
    for (const item of formRows.value) {
      if (item.absent) {
        item.score = 0
      }
      if (!item.absent && item.score !== null && !scoreOptions.includes(item.score)) item.score = null
    }
  }
)

async function load() {
  if (!token.value) {
    loadError.value = '二维码缺少有效参数'
    return
  }
  try {
    const resp = await api.get('/score', { params: { token: token.value } })
    scoreData.value = resp.data
    formRows.value = resp.data.players.map((player: ScorePlayer) => ({
      player_id: player.id,
      name: player.name,
      team_name: player.team_name,
      identity_label: player.identity_label,
      score: null,
      absent: false
    }))
  } catch (error) {
    loadError.value = errorText(error)
  }
}

async function judgeLogin() {
  if (!judgeRealName.value.trim() || !judgeAccount.value.trim() || !judgePassword.value) {
    showFailToast('请输入裁判姓名、账号和密码')
    return
  }
  loggingIn.value = true
  try {
    const resp = await api.post('/judge/login', {
      judge_name: judgeRealName.value.trim(),
      account: judgeAccount.value.trim(),
      password: judgePassword.value
    })
    judgeToken.value = resp.data.token
    judgeName.value = resp.data.judge.login_name || judgeRealName.value.trim()
    showSuccessToast('裁判登录成功')
  } catch (error) {
    showFailToast(errorText(error))
  } finally {
    loggingIn.value = false
  }
}

function logoutJudge() {
  judgeToken.value = ''
  judgeName.value = ''
  judgeRealName.value = ''
  judgePassword.value = ''
}

function validate(): boolean {
  if (!judgeToken.value) {
    showFailToast('请先使用裁判账号登录')
    return false
  }
  const present = formRows.value.filter((item) => !item.absent)
  const scores = present.map((item) => item.score)
  if (scores.some((score) => score === null)) {
    showFailToast('请为所有未缺席选手选择分数')
    return false
  }
  return true
}

async function submit() {
  if (!validate()) return
  submitting.value = true
  try {
    await api.post('/score/submit', {
      token: token.value,
      judge_token: judgeToken.value,
      results: formRows.value.map((item) => ({
        player_id: item.player_id,
        score: item.absent ? 0 : item.score,
        absent: item.absent
      }))
    })
    showSuccessToast('提交成功')
    await load()
  } catch (error) {
    showFailToast(errorText(error))
  } finally {
    submitting.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.rule-card {
  margin: 12px 16px;
  padding: 12px;
  display: grid;
  gap: 4px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #f8fbff;
  color: #334155;
  font-size: 13px;
  line-height: 1.55;
}

.player-title-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.score-player.absent {
  background: #fff7f7;
}

.score-controls {
  min-width: 120px;
  display: grid;
  justify-items: end;
  gap: 8px;
}

.select-row {
  display: grid;
  gap: 8px;
}

.select-row label {
  display: grid;
  gap: 4px;
  color: #64748b;
  font-size: 12px;
  text-align: left;
}

.score-select {
  width: 112px;
  min-height: 36px;
  border: 1px solid #d8dde6;
  border-radius: 6px;
  background: #fff;
  color: #172033;
  font-size: 15px;
  padding: 0 8px;
}

.score-select:disabled {
  color: #94a3b8;
  background: #eef2f7;
}

@media (max-width: 430px) {
  .score-controls {
    min-width: 120px;
  }

  .score-select {
    width: 108px;
  }
}
</style>
