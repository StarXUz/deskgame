<template>
  <div class="score-page">
    <div class="score-card">
      <div class="score-header">
        <h1>{{ data?.player.name || '选手信息' }}</h1>
        <div v-if="data">{{ data.player.player_code || '未填写编号' }} · {{ data.player.team_name }}</div>
      </div>

      <van-empty v-if="loadError" :description="loadError" />

      <template v-else-if="data">
        <van-notice-bar :text="data.message" />

        <div class="assignment-card">
          <div class="assignment-kicker">当前安排</div>
          <template v-if="data.current_assignment">
            <div class="assignment-main">
              第 {{ data.current_assignment.round_no }} 轮 · {{ data.current_assignment.table_no }}
            </div>
            <div class="assignment-meta">{{ data.current_assignment.age_group }} · {{ data.player.game_type }}</div>
            <van-tag :type="data.current_assignment.is_bye ? 'warning' : (data.current_assignment.submitted ? 'success' : 'primary')" size="large">
              {{ data.current_assignment.is_bye ? '轮空晋级' : (data.current_assignment.submitted ? '已录入' : '待比赛') }}
            </van-tag>
          </template>
          <template v-else>
            <div class="assignment-main">等待分桌</div>
            <div class="assignment-meta">生成下一轮桌位后会自动更新。</div>
          </template>
        </div>

        <div v-if="data.current_assignment?.score_entry_url" class="primary-action">
          <van-button block type="primary" size="large" @click="openScoreEntry">
            裁判登录录入本桌成绩
          </van-button>
        </div>

        <div class="score-summary">
          <div>
            <span>个人总分</span>
            <strong>{{ data.player.total_score }}</strong>
          </div>
          <div>
            <span>决赛分</span>
            <strong>{{ data.player.final_score }}</strong>
          </div>
          <div>
            <span>团队总分</span>
            <strong>{{ data.team_score.total_score }}</strong>
          </div>
          <div>
            <span>团队决赛</span>
            <strong>{{ data.team_score.final_score }}</strong>
          </div>
        </div>

        <van-cell-group inset title="选手身份">
          <van-cell title="学校" :value="data.player.school || '-'" />
          <van-cell title="区" :value="data.player.district || '-'" />
          <van-cell title="组别 / 游戏" :value="`${data.player.age_group} / ${data.player.game_type}`" />
          <van-cell title="身份" :value="data.player.identity_label" />
        </van-cell-group>

        <van-cell-group inset title="每轮成绩" style="margin-top: 12px">
          <van-cell v-for="item in data.score_history" :key="item.round_no">
            <template #title>
              第 {{ item.round_no }} 轮
              <van-tag v-if="item.bye" type="warning" style="margin-left: 6px">轮空</van-tag>
              <van-tag v-if="item.absent" type="danger" style="margin-left: 6px">缺席</van-tag>
            </template>
            <template #label>
              {{ item.table_no || '未生成' }} {{ item.rank ? ` · 第${item.rank}名` : '' }}
            </template>
            <template #value>
              <div>{{ item.score === null ? '-' : `${item.score}分` }}</div>
              <div class="advance-text">{{ advanceText(item.advanced) }}</div>
            </template>
          </van-cell>
        </van-cell-group>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api, errorText } from '../api/client'

const route = useRoute()
const data = ref<any | null>(null)
const loadError = ref('')

function advanceText(value: boolean | null) {
  if (value === null) return ''
  return value ? '晋级' : '未晋级'
}

async function load() {
  const token = String(route.query.token || '')
  if (!token) {
    loadError.value = '缺少选手二维码参数'
    return
  }
  try {
    const resp = await api.get('/player-status', { params: { token } })
    data.value = resp.data
  } catch (error) {
    loadError.value = errorText(error)
  }
}

function openScoreEntry() {
  if (data.value?.current_assignment?.score_entry_url) {
    window.location.href = data.value.current_assignment.score_entry_url
  }
}

onMounted(load)
</script>

<style scoped>
.assignment-card {
  margin: 14px 16px;
  padding: 16px;
  display: grid;
  gap: 8px;
  border-radius: 8px;
  background: linear-gradient(135deg, #17324d, #2563eb);
  color: #fff;
  box-shadow: 0 10px 22px rgba(23, 50, 77, 0.16);
}

.assignment-kicker {
  color: rgba(255, 255, 255, 0.78);
  font-size: 13px;
}

.assignment-main {
  font-size: 22px;
  font-weight: 800;
  line-height: 1.25;
}

.assignment-meta {
  color: rgba(255, 255, 255, 0.82);
  font-size: 14px;
}

.primary-action {
  padding: 0 16px 14px;
}

.score-summary {
  margin: 0 16px 14px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.score-summary > div {
  padding: 12px;
  display: grid;
  gap: 4px;
  border: 1px solid #dbe6f3;
  border-radius: 8px;
  background: #fff;
}

.score-summary span {
  color: #64748b;
  font-size: 12px;
}

.score-summary strong {
  color: #172033;
  font-size: 22px;
  line-height: 1;
}

.advance-text {
  color: #64748b;
  font-size: 12px;
  margin-top: 2px;
}
</style>
