<template>
  <div class="page-shell admin-layout">
    <aside class="admin-side">
      <h1>桌游比赛管理系统</h1>
      <el-menu :default-active="activeTab" background-color="#172033" text-color="#d4deed" active-text-color="#ffffff" @select="selectTab">
        <el-menu-item index="import">选手导入</el-menu-item>
        <el-menu-item index="transition">升学过渡管理</el-menu-item>
        <el-menu-item index="schedule">赛程控制台</el-menu-item>
        <el-menu-item index="seating">座位分布图</el-menu-item>
        <el-menu-item index="progression">选手轮次标记</el-menu-item>
        <el-menu-item index="leaderboard">实时积分榜</el-menu-item>
        <el-menu-item index="judges">裁判账号管理</el-menu-item>
        <el-menu-item index="export">最终报表</el-menu-item>
      </el-menu>
    </aside>

    <main class="admin-main">
      <section v-if="showOverviewCards" class="score-grid">
        <div class="panel">
          <h2 class="panel-title">个人实时榜</h2>
          <div class="search-row">
            <el-input v-model="leaderboardSearch" clearable placeholder="搜索姓名、编号、队伍、学校" />
            <el-tag type="info">共 {{ filteredLeaderboard.length }} 人</el-tag>
          </div>
          <el-table :data="filteredLeaderboard" height="280" stripe>
            <el-table-column type="index" label="#" width="56" />
            <el-table-column prop="name" label="姓名" min-width="100" />
            <el-table-column prop="team_name" label="队伍" min-width="130" />
            <el-table-column prop="game_type" label="游戏" width="90" />
            <el-table-column prop="total_score" label="总积分" width="90" />
          </el-table>
        </div>
        <div class="panel">
          <h2 class="panel-title">团队实时榜</h2>
          <div class="search-row">
            <el-input v-model="teamLeaderboardSearch" clearable placeholder="搜索队伍、学校、区、游戏" />
            <el-tag type="info">共 {{ filteredTeamLeaderboard.length }} 队</el-tag>
          </div>
          <el-table :data="filteredTeamLeaderboard" height="280" stripe>
            <el-table-column type="index" label="#" width="56" />
            <el-table-column prop="team_name" label="队伍" min-width="130" />
            <el-table-column prop="school" label="学校" min-width="160" />
            <el-table-column prop="game_type" label="游戏" width="90" />
            <el-table-column prop="total_score" label="团队总分" width="100" />
          </el-table>
        </div>
      </section>

      <section v-if="activeTab === 'import'" class="panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title">选手导入</h2>
            <p>导入名单、查看个人二维码和基础信息。</p>
          </div>
        </div>
        <div class="toolbar">
          <el-upload :show-file-list="false" accept=".xlsx" :http-request="uploadRoster">
            <el-button type="primary">选择 Excel 并导入</el-button>
          </el-upload>
          <el-button @click="refreshAll">刷新数据</el-button>
          <el-input v-model="playerSearch" clearable placeholder="搜索姓名、编号、队伍、学校" class="toolbar-search" />
          <el-tag type="info">共 {{ filteredPlayers.length }} 人</el-tag>
          <el-tag type="success">点击选手行查看二维码</el-tag>
        </div>
        <el-alert v-if="importWarnings.length" type="warning" show-icon :closable="false" style="margin-top: 14px">
          <template #title>导入警告</template>
          <div v-for="item in importWarnings" :key="item">{{ item }}</div>
          <el-button type="warning" size="small" style="margin-top: 10px" @click="forceImport">确认并强制导入</el-button>
        </el-alert>
        <el-table :data="filteredPlayers" class="clickable-table" style="margin-top: 16px" height="520" stripe @row-click="openPlayerQrDialog">
          <el-table-column prop="seed_rank" label="种子" width="76" />
          <el-table-column prop="player_code" label="队员编号" width="100" />
          <el-table-column label="姓名" width="110">
            <template #default="{ row }">
              <el-button link type="primary" @click.stop="openPlayerQrDialog(row)">{{ row.name }}</el-button>
            </template>
          </el-table-column>
          <el-table-column prop="team_name" label="队伍名称" min-width="140" />
          <el-table-column prop="district" label="区" width="100" />
          <el-table-column prop="school" label="学校" min-width="180" />
          <el-table-column prop="team_code" label="队伍编号" width="100" />
          <el-table-column prop="age_group" label="年级组别" min-width="130" />
          <el-table-column prop="game_type" label="所属游戏" width="100" />
          <el-table-column prop="identity_label" label="身份" width="110" />
          <el-table-column label="个人二维码" width="130">
            <template #default="{ row }">
              <el-button size="small" @click.stop="openPlayerQrDialog(row)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </section>

      <section v-if="activeTab === 'transition'" class="panel">
        <h2 class="panel-title">升学过渡管理</h2>
        <div class="toolbar">
          <el-tag v-for="(count, game) in poolStatus.free_by_game" :key="game" type="success">
            {{ game }} 自由人单独比赛池：{{ count }}人
          </el-tag>
          <el-button type="primary" @click="saveTransition">保存调整</el-button>
        </div>
        <el-table :data="transitionPlayers" style="margin-top: 16px" height="520" stripe>
          <el-table-column prop="seed_rank" label="种子" width="76" />
          <el-table-column prop="name" label="姓名" width="110" />
          <el-table-column prop="team_name" label="队伍" min-width="140" />
          <el-table-column prop="age_group" label="锁定组别" min-width="130" />
          <el-table-column prop="game_type" label="游戏" width="90" />
          <el-table-column label="升学出路选择" min-width="170">
            <template #default="{ row }">
              <el-select v-model="row.transition_choice" style="width: 150px">
                <el-option label="自由人补位" value="自由人补位" />
                <el-option label="跟随原学校" value="跟随原学校" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="identity_label" label="当前身份" width="120" />
        </el-table>
      </section>

      <section v-if="activeTab === 'schedule'" class="panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title">赛程控制台</h2>
            <p>生成当前轮次桌位，裁判通过选手个人二维码进入本桌录入。</p>
          </div>
        </div>
        <div class="toolbar">
          <el-select v-model="roundNo" style="width: 150px">
            <el-option v-for="item in 6" :key="item" :label="`第 ${item} 轮`" :value="item" />
          </el-select>
          <el-button type="primary" @click="generateTables">生成本轮桌位</el-button>
          <el-button @click="loadTables">查看本轮桌位</el-button>
          <el-tag type="info">裁判扫选手个人二维码进入本桌录入</el-tag>
        </div>
        <el-alert v-if="roundWarnings.length" type="warning" show-icon :closable="false" style="margin-top: 14px">
          <template #title>本轮提醒</template>
          <div v-for="item in roundWarnings" :key="item">{{ item }}</div>
        </el-alert>
        <el-table :data="tables" style="margin-top: 16px" stripe>
          <el-table-column prop="table_no" label="桌号" width="100" />
          <el-table-column prop="age_group" label="组别" width="130" />
          <el-table-column prop="game_type" label="游戏" width="90" />
          <el-table-column label="选手" min-width="280">
            <template #default="{ row }">
              <div class="player-tags">
                <el-tag v-for="player in row.players" :key="player.id" :type="player.identity_label === '自由人' ? 'warning' : 'info'">
                  {{ player.name }}{{ player.identity_label === '自由人' ? '（自由人）' : '' }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="150">
            <template #default="{ row }">
              <el-tag :type="row.is_bye ? 'warning' : 'success'">{{ row.is_bye ? '2人轮空' : `${row.participant_count}人桌` }}</el-tag>
              <el-tag v-if="row.has_free_agent" type="danger" style="margin-left: 6px">自由人桌</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="录入" width="90">
            <template #default="{ row }">
              <el-tag :type="row.submitted ? 'success' : 'info'">{{ row.submitted ? '已提交' : '待提交' }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </section>

      <section v-if="activeTab === 'seating'" class="panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title">座位分布图</h2>
            <p>点击座位号查看本轮成员、分数和裁判提交记录。</p>
          </div>
        </div>
        <div class="toolbar">
          <el-select v-model="roundNo" style="width: 150px">
            <el-option v-for="item in 6" :key="item" :label="`第 ${item} 轮`" :value="item" />
          </el-select>
          <el-select v-model="seatingPriority" style="width: 180px">
            <el-option label="少桌组别优先" value="small_group_first" />
            <el-option label="按桌号顺序" value="table_no" />
            <el-option label="小学低年级优先" value="小学低年级组" />
            <el-option label="小学高年级优先" value="小学高年级组" />
            <el-option label="初中组优先" value="初中组" />
          </el-select>
          <el-button type="primary" @click="loadSeatingChart">刷新座位图</el-button>
          <el-tag type="info">图上 {{ seatingChart?.occupied_count || 0 }} / {{ seatingChart?.seat_capacity || 113 }} 桌</el-tag>
          <el-tag v-if="seatingChart?.overflow_count" type="warning">未上图 {{ seatingChart.overflow_count }} 桌</el-tag>
        </div>
        <div class="seat-layout" v-if="seatingChart">
          <div class="seat-map-scroll">
            <div class="seat-map-canvas">
              <img v-if="seatingChart.map_image" class="seat-map-image" :src="seatingChart.map_image" alt="座位分布图" />
              <button
                v-for="seat in seatingChart.seats"
                :key="seat.seat_no"
                class="seat-marker"
                :class="{ occupied: seat.table, active: selectedSeat?.seat_no === seat.seat_no, submitted: seat.table?.submitted }"
                :style="{ left: `${seat.x}%`, top: `${seat.y}%` }"
                @click="selectSeat(seat)"
              >
                {{ seat.seat_no }}
              </button>
            </div>
          </div>
          <aside class="seat-detail">
            <template v-if="selectedSeat?.table">
              <div class="seat-detail-head">
                <div>
                  <h3>{{ selectedSeat.seat_no }}号座位</h3>
                  <p>{{ selectedSeat.table.table_no }} · {{ selectedSeat.table.age_group }} · {{ selectedSeat.table.game_type }}</p>
                </div>
                <el-tag :type="selectedSeat.table.submitted ? 'success' : 'info'">
                  {{ selectedSeat.table.submitted ? '已录入' : '待录入' }}
                </el-tag>
              </div>
              <div class="seat-actions" v-if="selectedSeat.table.seat_no">
                <el-button size="small" @click="clearSelectedTableSeat">移出固定座位</el-button>
              </div>
              <div v-if="selectedSeat.table.judge_submission" class="judge-submission-card">
                <strong>裁判：</strong>{{ selectedSeat.table.judge_submission.judge_name }}
                <span>（{{ selectedSeat.table.judge_submission.account }}）</span>
                <br />
                <strong>提交：</strong>{{ selectedSeat.table.judge_submission.submitted_at }}
                <br />
                <strong>分数：</strong>{{ scoreSummary(selectedSeat.table.judge_submission.scores) }}
              </div>
              <el-table :data="selectedSeat.table.players" size="small" stripe>
                <el-table-column prop="player_code" label="编号" width="76" />
                <el-table-column prop="name" label="姓名" min-width="82" />
                <el-table-column prop="team_name" label="队伍" min-width="110" />
                <el-table-column label="分数" width="64">
                  <template #default="{ row }">{{ row.round_result?.score ?? '-' }}</template>
                </el-table-column>
                <el-table-column label="名次" width="64">
                  <template #default="{ row }">{{ row.round_result?.rank ?? '-' }}</template>
                </el-table-column>
                <el-table-column label="状态" width="90">
                  <template #default="{ row }">
                    <el-tag v-if="row.round_result?.is_absent" type="danger">缺席</el-tag>
                    <el-tag v-else-if="row.round_result?.submitted && row.round_result?.is_advanced" type="success">晋级</el-tag>
                    <el-tag v-else-if="row.round_result?.submitted" type="info">完成</el-tag>
                    <el-tag v-else type="info">待赛</el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </template>
            <template v-else>
              <div class="empty-seat-tip">
                <h3>{{ selectedSeat ? `${selectedSeat.seat_no}号座位` : '选择一张桌子' }}</h3>
                <p>{{ selectedSeat ? '当前轮次没有安排桌位。' : '点击地图上的座位号查看成员和分数。' }}</p>
              </div>
            </template>
            <div v-if="seatingChart.overflow.length" class="overflow-list">
              <h3>未上图桌位</h3>
              <div v-for="table in seatingChart.overflow" :key="table.id" class="overflow-item" @click="selectOverflowTable(table)">
                <span>{{ table.table_no }} · {{ table.age_group }} · {{ table.game_type }} · {{ table.players.length }}人</span>
                <el-button
                  v-if="selectedSeat && selectedSeat.seat_no !== '未上图'"
                  size="small"
                  type="primary"
                  plain
                  @click.stop="assignTableToSelectedSeat(table)"
                >
                  安排到{{ selectedSeat.seat_no }}
                </el-button>
              </div>
            </div>
          </aside>
        </div>
      </section>

      <section v-if="activeTab === 'progression'" class="panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title">选手轮次标记</h2>
            <p>按轮次查看每张桌的选手、分数、二维码和比赛状态。</p>
          </div>
        </div>
        <div class="toolbar">
          <el-select v-model="progressionGroupKey" placeholder="选择组别 / 游戏" style="width: 280px">
            <el-option
              v-for="group in progressionGroups"
              :key="group.key"
              :label="`${group.age_group} · ${group.game_type}`"
              :value="group.key"
            />
          </el-select>
          <el-select v-model="progressionRoundNo" style="width: 140px">
            <el-option v-for="item in 6" :key="item" :label="`第 ${item} 轮`" :value="item" />
          </el-select>
          <el-input v-model="progressionSearch" clearable placeholder="搜索姓名、编号、队伍、桌号" class="toolbar-search" />
          <el-select v-model="progressionStatusFilter" style="width: 130px">
            <el-option label="全部状态" value="all" />
            <el-option label="晋级" value="晋级" />
            <el-option label="止步" value="止步" />
            <el-option label="待赛" value="待赛" />
            <el-option label="完成" value="完成" />
            <el-option label="缺席" value="缺席" />
          </el-select>
          <el-button type="primary" @click="loadProgressionChart">刷新标记</el-button>
          <el-tag type="info">共 {{ progressionGroups.length }} 个比赛池</el-tag>
          <el-tag v-if="selectedProgressionRound" type="success">
            显示 {{ selectedProgressionTables.length }} / {{ selectedProgressionRound.tables.length }} 桌
          </el-tag>
        </div>
        <el-empty v-if="!selectedProgressionGroup" description="暂无轮次标记数据" />
        <div v-else class="progression-board">
          <div v-if="selectedProgressionRound" class="progression-round">
            <div class="progression-round-head">
              <h3>{{ selectedProgressionRound.title }}</h3>
              <span>{{ selectedProgressionRound.note }}</span>
            </div>
            <div v-if="selectedProgressionTables.length" class="progression-table-list">
              <div v-for="table in selectedProgressionTables" :key="table.id" class="progression-table-card">
                <div class="progression-table-head">
                  <strong>{{ table.table_no }}</strong>
                  <span>{{ table.seat_no ? `${table.seat_no}号座位` : '未固定座位' }}</span>
                  <el-tag size="small" :type="table.submitted ? 'success' : 'info'">{{ table.submitted ? '已提交' : '待提交' }}</el-tag>
                </div>
                <button
                  v-for="player in table.players"
                  :key="`${table.id}-${player.id}`"
                  class="progression-player"
                  :class="progressionPlayerClass(player, selectedProgressionRound.round_no)"
                  @click="openPlayerQrDialog(player)"
                >
                  <span class="advance-icon">{{ progressionIconText(player, selectedProgressionRound.round_no) }}</span>
                  <span class="progression-player-main">
                    <strong>{{ player.name }}</strong>
                    <small>{{ player.player_code || '无编号' }} · {{ player.team_name }}</small>
                  </span>
                  <span class="progression-score">
                    {{ player.round_result?.score ?? '-' }}
                    <small>{{ progressionStatusText(player, selectedProgressionRound.round_no) }}</small>
                  </span>
                </button>
              </div>
            </div>
            <div v-else class="progression-empty">本轮暂无匹配结果</div>
          </div>
        </div>
      </section>

      <section v-if="activeTab === 'leaderboard'" class="panel">
        <h2 class="panel-title">实时积分榜</h2>
        <el-tabs v-model="leaderboardTab" class="leaderboard-tabs">
          <el-tab-pane label="个人榜" name="personal">
            <div class="toolbar">
              <el-input v-model="leaderboardSearch" clearable placeholder="搜索姓名、编号、队伍、学校、组别、游戏" class="toolbar-search" />
              <el-tag type="info">当前显示 {{ filteredLeaderboard.length }} / {{ leaderboard.length }} 人</el-tag>
            </div>
            <el-table :data="filteredLeaderboard" style="margin-top: 16px" stripe>
              <el-table-column type="index" label="排名" width="80" />
              <el-table-column prop="player_code" label="编号" width="100" />
              <el-table-column prop="name" label="姓名" min-width="100" />
              <el-table-column prop="team_name" label="队伍" min-width="130" />
              <el-table-column prop="age_group" label="组别" min-width="130" />
              <el-table-column prop="game_type" label="游戏" width="90" />
              <el-table-column prop="identity_label" label="身份" width="110" />
              <el-table-column prop="total_score" label="预赛+决赛总积分" width="160" />
              <el-table-column prop="final_score" label="决赛单独积分" width="140" />
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="团队榜" name="team">
            <div class="toolbar">
              <el-input v-model="teamLeaderboardSearch" clearable placeholder="搜索队伍、学校、区、组别、游戏" class="toolbar-search" />
              <el-tag type="info">当前显示 {{ filteredTeamLeaderboard.length }} / {{ teamLeaderboard.length }} 队</el-tag>
            </div>
            <el-table :data="filteredTeamLeaderboard" style="margin-top: 16px" stripe>
              <el-table-column type="index" label="排名" width="80" />
              <el-table-column prop="team_code" label="队伍编号" width="100" />
              <el-table-column prop="team_name" label="队伍" min-width="140" />
              <el-table-column prop="district" label="区" width="100" />
              <el-table-column prop="school" label="学校" min-width="180" />
              <el-table-column prop="age_group" label="组别" min-width="130" />
              <el-table-column prop="game_type" label="游戏" width="90" />
              <el-table-column prop="member_count" label="人数" width="80" />
              <el-table-column prop="total_score" label="团队总分" width="120" />
              <el-table-column prop="final_score" label="决赛团队分" width="130" />
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </section>

      <section v-if="activeTab === 'judges'" class="panel">
        <div class="panel-head">
          <div>
            <h2 class="panel-title">裁判账号管理</h2>
            <p>批量发放账号，记录每一轮实际裁判和提交分数。</p>
          </div>
        </div>
        <div class="toolbar">
          <el-input-number v-model="judgeGenerateCount" :min="1" :max="300" />
          <el-button type="primary" @click="generateJudges">批量生成账号</el-button>
          <el-button @click="copyJudgeText">复制微信群文本</el-button>
          <el-button @click="loadJudges">刷新</el-button>
          <el-input v-model="judgeSearch" clearable placeholder="搜索账号、领取人、备注" class="toolbar-search" />
          <el-tag type="info">账号 {{ judges.length }} 个</el-tag>
          <el-tag type="success">提交 {{ judgeSubmissions.length }} 次</el-tag>
        </div>
        <el-input
          v-model="judgeGroupText"
          type="textarea"
          :rows="7"
          readonly
          placeholder="生成账号后，这里会出现可复制到微信群的领取文本。"
          style="margin-top: 14px"
        />
        <el-table :data="filteredJudges" style="margin-top: 16px" height="420" stripe>
          <el-table-column prop="account" label="账号" width="90" />
          <el-table-column prop="initial_password" label="密码" width="100" />
          <el-table-column label="领取人" width="160">
            <template #default="{ row }">
              <el-input v-model="row.claimed_by" size="small" @change="saveJudge(row)" />
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="180">
            <template #default="{ row }">
              <el-input v-model="row.note" size="small" @change="saveJudge(row)" />
            </template>
          </el-table-column>
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="last_login_at" label="最后登录" min-width="150" />
          <el-table-column prop="submission_count" label="提交次数" width="100" />
          <el-table-column label="操作" width="230">
            <template #default="{ row }">
              <el-button size="small" @click="toggleJudge(row)">{{ row.is_active ? '禁用' : '启用' }}</el-button>
              <el-button size="small" @click="resetJudgePassword(row)">重置密码</el-button>
            </template>
          </el-table-column>
        </el-table>

        <h2 class="panel-title judge-record-title">成绩提交监管</h2>
        <el-table :data="judgeSubmissions" height="360" stripe>
          <el-table-column prop="round_no" label="轮次" width="70">
            <template #default="{ row }">第{{ row.round_no }}轮</template>
          </el-table-column>
          <el-table-column prop="seat_no" label="座位" width="80" />
          <el-table-column prop="table_no" label="桌号" width="100" />
          <el-table-column prop="account" label="裁判账号" width="110" />
          <el-table-column prop="judge_name" label="实际裁判" width="120" />
          <el-table-column prop="claimed_by" label="领取人" width="120" />
          <el-table-column prop="age_group" label="组别" min-width="120" />
          <el-table-column prop="game_type" label="游戏" width="90" />
          <el-table-column prop="submitted_at" label="提交时间" min-width="155" />
          <el-table-column prop="client_ip" label="IP" width="120" />
          <el-table-column label="分数" min-width="160">
            <template #default="{ row }">
              {{ scoreSummary(row.scores) }}
            </template>
          </el-table-column>
          <el-table-column label="更正" width="180" fixed="right">
            <template #default="{ row }">
              <el-popover v-if="row.correction_history?.length" trigger="click" width="320" placement="left">
                <div v-for="item in row.correction_history" :key="item.id" class="score-correction-history">
                  <strong>{{ item.operator_name }}</strong> · {{ item.corrected_at }}
                  <p>{{ item.reason }}</p>
                </div>
                <template #reference>
                  <el-button link type="warning">更正{{ row.correction_count }}次</el-button>
                </template>
              </el-popover>
              <el-button link type="primary" @click="openScoreCorrection(row)">更正成绩</el-button>
            </template>
          </el-table-column>
        </el-table>
      </section>

      <section v-if="activeTab === 'export'" class="panel">
        <h2 class="panel-title">报表导出</h2>
        <p>实时成绩统计表按组别展示每名选手第 1 至第 6 轮得分，并汇总团队总分，可在比赛过程中随时导出观看。</p>
        <div class="export-actions">
          <el-button type="primary" @click="downloadLiveScoreboard">导出实时成绩统计表</el-button>
          <el-button @click="downloadReport">导出最终 Excel 报表</el-button>
        </div>
        <p class="export-note">最终报表包含三个 Sheet：全量选手每轮明细、最终个人排名、团队奖项排名。</p>
      </section>
    </main>

    <el-dialog v-model="playerQrDialogVisible" title="选手个人二维码" width="420px">
      <div v-if="selectedQrPlayer" class="qr-dialog-body">
        <img v-if="selectedQrPlayer.player_qr_path" class="qr-dialog-image" :src="selectedQrPlayer.player_qr_path" alt="个人二维码" />
        <el-empty v-else description="当前选手暂未生成二维码" />
        <div class="qr-dialog-info">
          <h3>{{ selectedQrPlayer.name }}</h3>
          <p>{{ selectedQrPlayer.player_code || '未填写编号' }} · {{ selectedQrPlayer.team_name }}</p>
          <p>{{ selectedQrPlayer.age_group }} · {{ selectedQrPlayer.game_type }}</p>
          <p>{{ selectedQrPlayer.school || '未填写学校' }}</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="playerQrDialogVisible = false">关闭</el-button>
        <el-button type="primary" :disabled="!playerQrUrl" @click="copyPlayerQrUrl">复制扫码链接</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="scoreCorrectionDialogVisible" title="管理员成绩更正" width="760px" destroy-on-close>
      <template v-if="scoreCorrectionTarget">
        <el-alert
          type="warning"
          :closable="false"
          show-icon
          title="更正后会立即更新积分榜、团队积分和本轮晋级状态。下一轮桌位已经生成时，系统会拒绝本次更正。"
        />
        <div class="score-correction-meta">
          第{{ scoreCorrectionTarget.round_no }}轮 · {{ scoreCorrectionTarget.table_no }} · {{ scoreCorrectionTarget.age_group }} · {{ scoreCorrectionTarget.game_type }}
          <el-tag v-if="scoreCorrectionTarget.correction_count" type="warning" size="small">此前已更正 {{ scoreCorrectionTarget.correction_count }} 次</el-tag>
        </div>
        <el-table :data="scoreCorrectionResults" size="small" stripe>
          <el-table-column prop="player_code" label="编号" width="95" />
          <el-table-column prop="name" label="姓名" min-width="110" />
          <el-table-column prop="team_name" label="队伍" min-width="140" />
          <el-table-column label="缺席" width="90">
            <template #default="{ row }">
              <el-checkbox v-model="row.absent" @change="toggleCorrectionAbsent(row)" />
            </template>
          </el-table-column>
          <el-table-column label="分数" width="150">
            <template #default="{ row }">
              <el-tag v-if="row.absent" type="danger">缺席 0 分</el-tag>
              <el-select v-else v-model="row.score" style="width: 110px">
                <el-option v-for="score in scoreOptions" :key="score" :label="`${score} 分`" :value="score" />
              </el-select>
            </template>
          </el-table-column>
        </el-table>
        <div class="score-correction-form">
          <el-input v-model="scoreCorrectionOperator" maxlength="60" show-word-limit placeholder="更正人姓名（必填）" />
          <el-input v-model="scoreCorrectionReason" maxlength="300" show-word-limit type="textarea" :rows="3" placeholder="更正原因（必填，例如：裁判将两名选手分数填反）" />
        </div>
      </template>
      <template #footer>
        <el-button @click="scoreCorrectionDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="scoreCorrectionSubmitting" @click="submitScoreCorrection">确认更正</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api, errorText } from '../api/client'

interface Player {
  id: number
  name: string
  team_name: string
  district: string | null
  school: string | null
  team_code: string | null
  player_code: string | null
  player_qr_token: string | null
  player_qr_path: string | null
  age_group: string
  game_type: string
  seed_rank: number
  is_transition: number
  transition_choice: string | null
  identity_label: string
  round_result?: {
    rank: number | null
    score: number | null
    is_absent: boolean
    is_advanced: boolean
    submitted: boolean
  }
}

interface TableRow {
  id: number
  table_no: string
  age_group: string
  game_type: string
  players: Player[]
  seat_no: string | null
  is_bye: boolean
  participant_count: number
  has_free_agent: boolean
  submitted: boolean
  judge_submission?: {
    judge_name: string
    submitted_at: string
    account: string
    claimed_by: string
    scores: Array<{ score: number }>
  } | null
}

interface SeatAssignment {
  seat_no: string
  x: number
  y: number
  table: TableRow | null
  manual?: boolean
}

interface SeatingChart {
  round_no: number
  map_image: string
  seat_capacity: number
  table_count: number
  occupied_count: number
  overflow_count: number
  seats: SeatAssignment[]
  assignments: SeatAssignment[]
  overflow: TableRow[]
}

interface AdvancementRound {
  round_no: number
  title: string
  note: string
  tables: TableRow[]
}

interface AdvancementGroup {
  key: string
  age_group: string
  game_type: string
  rounds: AdvancementRound[]
}

interface JudgeAccount {
  id: number
  account: string
  initial_password: string
  claimed_by: string
  note: string
  is_active: boolean
  created_at: string
  last_login_at: string | null
  submission_count: number
}

interface JudgeSubmissionScore {
  player_id: number
  player_code: string | null
  name: string
  team_name?: string
  table_rank: number
  score: number
  absent: boolean
  advanced: boolean
}

interface JudgeSubmission {
  table_id: number
  round_no: number
  table_no: string
  seat_no: string | null
  age_group: string
  game_type: string
  account: string
  judge_name: string
  claimed_by: string | null
  submitted_at: string
  client_ip: string
  scores: JudgeSubmissionScore[]
  correction_count: number
  correction_history: Array<{
    id: number
    operator_name: string
    reason: string
    corrected_at: string
  }>
}

const adminTabs = ['import', 'transition', 'schedule', 'seating', 'progression', 'leaderboard', 'judges', 'export']
const activeTab = ref(readStoredTab())
const players = ref<Player[]>([])
const transitionPlayers = ref<Player[]>([])
const leaderboard = ref<any[]>([])
const teamLeaderboard = ref<any[]>([])
const tables = ref<TableRow[]>([])
const seatingChart = ref<SeatingChart | null>(null)
const selectedSeat = ref<SeatAssignment | null>(null)
const progressionGroups = ref<AdvancementGroup[]>([])
const progressionGroupKey = ref('')
const progressionRoundNo = ref(readStoredProgressionRound())
const judges = ref<JudgeAccount[]>([])
const judgeSubmissions = ref<JudgeSubmission[]>([])
const judgeGroupText = ref('')
const judgeGenerateCount = ref(20)
const roundNo = ref(readStoredRound())
const seatingPriority = ref(readStoredSeatingPriority())
const leaderboardTab = ref('personal')
const playerSearch = ref('')
const leaderboardSearch = ref('')
const teamLeaderboardSearch = ref('')
const judgeSearch = ref('')
const progressionSearch = ref('')
const progressionStatusFilter = ref('all')
const playerQrDialogVisible = ref(false)
const selectedQrPlayer = ref<Player | null>(null)
const scoreCorrectionDialogVisible = ref(false)
const scoreCorrectionTarget = ref<JudgeSubmission | null>(null)
const scoreCorrectionResults = ref<Array<JudgeSubmissionScore & { absent: boolean; score: number }>>([])
const scoreCorrectionOperator = ref('')
const scoreCorrectionReason = ref('')
const scoreCorrectionSubmitting = ref(false)
const scoreOptions = [5, 3, 2, 1]
const importWarnings = ref<string[]>([])
const roundWarnings = ref<string[]>([])
const lastImportFile = ref<File | null>(null)
const poolStatus = ref<{ free_by_game: Record<string, number>; transition_count: number }>({ free_by_game: {}, transition_count: 0 })
const showOverviewCards = computed(() => activeTab.value === 'import' || activeTab.value === 'schedule')
const playerQrUrl = computed(() =>
  selectedQrPlayer.value?.player_qr_token ? `${window.location.origin}/player?token=${selectedQrPlayer.value.player_qr_token}` : ''
)
const selectedProgressionGroup = computed(() => progressionGroups.value.find((group) => group.key === progressionGroupKey.value) || null)
const selectedProgressionRound = computed(
  () => selectedProgressionGroup.value?.rounds.find((round) => round.round_no === progressionRoundNo.value) || null
)
const selectedProgressionTables = computed(() => {
  const round = selectedProgressionRound.value
  if (!round) return []
  const keyword = progressionSearch.value.trim().toLowerCase()
  const statusFilter = progressionStatusFilter.value
  return round.tables
    .map((table) => {
      const tableMatched =
        !!keyword &&
        [table.table_no, table.seat_no || '', table.age_group, table.game_type].some((value) =>
          String(value ?? '').toLowerCase().includes(keyword)
        )
      const players = table.players.filter((player) => {
        const status = progressionStatusText(player, round.round_no)
        if (statusFilter !== 'all' && status !== statusFilter) return false
        if (!keyword || tableMatched) return true
        return [
          player.name,
          player.player_code,
          player.team_name,
          player.team_code,
          player.school,
          player.district,
          player.age_group,
          player.game_type,
          player.identity_label
        ].some((value) => String(value ?? '').toLowerCase().includes(keyword))
      })
      return { ...table, players }
    })
    .filter((table) => table.players.length > 0)
})

function readStoredTab() {
  const value = window.localStorage.getItem('boardgame-admin-tab')
  return value && adminTabs.includes(value) ? value : 'import'
}

function readStoredRound() {
  const value = Number(window.localStorage.getItem('boardgame-admin-round') || '1')
  return Number.isInteger(value) && value >= 1 && value <= 6 ? value : 1
}

function readStoredSeatingPriority() {
  return window.localStorage.getItem('boardgame-seating-priority') || 'small_group_first'
}

function readStoredProgressionRound() {
  const value = Number(window.localStorage.getItem('boardgame-progression-round') || '1')
  return Number.isInteger(value) && value >= 1 && value <= 6 ? value : 1
}

function selectTab(tab: string) {
  activeTab.value = tab
  window.localStorage.setItem('boardgame-admin-tab', tab)
  if (tab === 'schedule') {
    loadTables()
  }
  if (tab === 'seating') {
    loadSeatingChart()
  }
  if (tab === 'progression') {
    loadProgressionChart()
  }
  if (tab === 'leaderboard') {
    refreshLeaderboards()
  }
  if (tab === 'judges') {
    loadJudges()
  }
}

watch(roundNo, (value) => {
  window.localStorage.setItem('boardgame-admin-round', String(value))
  if (activeTab.value === 'schedule') {
    loadTables()
  }
  if (activeTab.value === 'seating') {
    loadSeatingChart()
  }
})

watch(seatingPriority, (value) => {
  window.localStorage.setItem('boardgame-seating-priority', value)
  if (activeTab.value === 'seating') {
    loadSeatingChart()
  }
})

watch(progressionRoundNo, (value) => {
  window.localStorage.setItem('boardgame-progression-round', String(value))
})

function matchesSearch(row: Record<string, unknown>, keyword: string, fields: string[]) {
  const text = keyword.trim().toLowerCase()
  if (!text) return true
  return fields.some((field) => String(row[field] ?? '').toLowerCase().includes(text))
}

const filteredPlayers = computed(() =>
  players.value.filter((player) =>
    matchesSearch(player as unknown as Record<string, unknown>, playerSearch.value, [
      'name',
      'player_code',
      'team_name',
      'team_code',
      'district',
      'school',
      'age_group',
      'game_type',
      'identity_label'
    ])
  )
)

const filteredLeaderboard = computed(() =>
  leaderboard.value.filter((player) =>
    matchesSearch(player, leaderboardSearch.value, [
      'name',
      'player_code',
      'team_name',
      'team_code',
      'district',
      'school',
      'age_group',
      'game_type',
      'identity_label'
    ])
  )
)

const filteredTeamLeaderboard = computed(() =>
  teamLeaderboard.value.filter((team) =>
    matchesSearch(team, teamLeaderboardSearch.value, ['team_name', 'team_code', 'district', 'school', 'age_group', 'game_type'])
  )
)

const filteredJudges = computed(() =>
  judges.value.filter((judge) =>
    matchesSearch(judge as unknown as Record<string, unknown>, judgeSearch.value, ['account', 'claimed_by', 'note', 'initial_password'])
  )
)

async function refreshAll() {
  const [playerResp, transitionResp, statusResp] = await Promise.all([
    api.get('/players'),
    api.get('/players', { params: { transition_only: true } }),
    api.get('/pool-status')
  ])
  players.value = playerResp.data
  transitionPlayers.value = transitionResp.data
  poolStatus.value = statusResp.data
  await refreshLeaderboards()
}

async function refreshLeaderboards() {
  const [boardResp, teamBoardResp] = await Promise.all([
    api.get('/leaderboard', { params: { limit: 0 } }),
    api.get('/team-leaderboard', { params: { limit: 0, metric: 'total' } })
  ])
  leaderboard.value = boardResp.data
  teamLeaderboard.value = teamBoardResp.data
}

async function refreshVisibleData() {
  if (activeTab.value === 'import' || activeTab.value === 'transition') {
    await refreshAll()
    return
  }
  if (activeTab.value === 'schedule') {
    await Promise.all([refreshLeaderboards(), loadTables()])
    return
  }
  if (activeTab.value === 'seating') {
    await loadSeatingChart()
    return
  }
  if (activeTab.value === 'progression') {
    await loadProgressionChart()
    return
  }
  if (activeTab.value === 'leaderboard') {
    await refreshLeaderboards()
    return
  }
  if (activeTab.value === 'judges') {
    await loadJudges()
  }
}

async function uploadRoster(options: any) {
  lastImportFile.value = options.file
  await doImport(false)
}

async function doImport(force: boolean) {
  if (!lastImportFile.value) return
  const form = new FormData()
  form.append('file', lastImportFile.value)
  try {
    const resp = await api.post('/players/import', form, {
      params: { force },
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    importWarnings.value = resp.data.warnings || []
    if (resp.data.imported) {
      ElMessage.success(`已导入 ${resp.data.count} 名选手`)
      await refreshAll()
    } else {
      ElMessage.warning(resp.data.message)
    }
  } catch (error) {
    ElMessage.error(errorText(error))
  }
}

async function forceImport() {
  await ElMessageBox.confirm('确认忽略警告并导入？导入会清空已有赛程和成绩。', '强制导入')
  await doImport(true)
}

async function saveTransition() {
  try {
    await api.patch('/players/transition', {
      players: transitionPlayers.value.map((player) => ({ id: player.id, transition_choice: player.transition_choice }))
    })
    ElMessage.success('升学过渡设置已保存')
    await refreshAll()
  } catch (error) {
    ElMessage.error(errorText(error))
  }
}

function openPlayerQrDialog(player: Player) {
  selectedQrPlayer.value = player
  playerQrDialogVisible.value = true
}

async function copyPlayerQrUrl() {
  if (!playerQrUrl.value) return
  await navigator.clipboard.writeText(playerQrUrl.value)
  ElMessage.success('选手扫码链接已复制')
}

async function generateTables() {
  try {
    const resp = await api.post(`/rounds/${roundNo.value}/generate`)
    tables.value = resp.data.tables
    roundWarnings.value = resp.data.warnings || []
    ElMessage.success(`第 ${roundNo.value} 轮桌位已生成`)
    await refreshAll()
  } catch (error) {
    ElMessage.error(errorText(error))
  }
}

async function loadTables() {
  try {
    const resp = await api.get(`/rounds/${roundNo.value}/tables`)
    tables.value = resp.data
  } catch (error) {
    ElMessage.error(errorText(error))
  }
}

function selectSeat(seat: SeatAssignment) {
  selectedSeat.value = seat
}

function selectOverflowTable(table: TableRow) {
  selectedSeat.value = {
    seat_no: '未上图',
    x: 0,
    y: 0,
    table
  }
}

async function loadSeatingChart() {
  try {
    const previousSeatNo = selectedSeat.value?.seat_no
    const resp = await api.get(`/rounds/${roundNo.value}/seating-chart`, {
      params: { priority: seatingPriority.value }
    })
    seatingChart.value = resp.data
    selectedSeat.value =
      seatingChart.value?.seats.find((seat) => seat.seat_no === previousSeatNo) ||
      seatingChart.value?.assignments[0] ||
      seatingChart.value?.seats[0] ||
      null
  } catch (error) {
    ElMessage.error(errorText(error))
  }
}

async function loadProgressionChart() {
  try {
    const previousKey = progressionGroupKey.value
    const resp = await api.get('/advancement-chart')
    progressionGroups.value = resp.data.groups || []
    progressionGroupKey.value =
      progressionGroups.value.find((group) => group.key === previousKey)?.key ||
      progressionGroups.value[0]?.key ||
      ''
  } catch (error) {
    ElMessage.error(errorText(error))
  }
}

function progressionStatusText(player: Player, roundNo: number) {
  const result = player.round_result
  if (!result?.submitted) return '待赛'
  if (result.is_absent) return '缺席'
  if (roundNo === 6) return '完成'
  return result.is_advanced ? '晋级' : '止步'
}

function progressionIconText(player: Player, roundNo: number) {
  const status = progressionStatusText(player, roundNo)
  if (status === '晋级') return '晋'
  if (status === '完成') return '终'
  if (status === '止步') return '止'
  if (status === '缺席') return '缺'
  return '待'
}

function progressionPlayerClass(player: Player, roundNo: number) {
  return {
    advanced: progressionStatusText(player, roundNo) === '晋级',
    final: progressionStatusText(player, roundNo) === '完成',
    stopped: progressionStatusText(player, roundNo) === '止步',
    absent: progressionStatusText(player, roundNo) === '缺席'
  }
}

async function assignTableToSelectedSeat(table: TableRow) {
  if (!selectedSeat.value || selectedSeat.value.seat_no === '未上图') return
  try {
    await api.patch(`/rounds/${roundNo.value}/tables/${table.id}/seat`, {
      seat_no: selectedSeat.value.seat_no
    })
    ElMessage.success(`${table.table_no} 已安排到 ${selectedSeat.value.seat_no} 号座位`)
    await loadSeatingChart()
  } catch (error) {
    ElMessage.error(errorText(error))
  }
}

async function clearSelectedTableSeat() {
  if (!selectedSeat.value?.table) return
  try {
    await api.patch(`/rounds/${roundNo.value}/tables/${selectedSeat.value.table.id}/seat`, {
      seat_no: null
    })
    ElMessage.success('已移出固定座位')
    await loadSeatingChart()
  } catch (error) {
    ElMessage.error(errorText(error))
  }
}

async function loadJudges() {
  try {
    const [judgeResp, submissionResp] = await Promise.all([api.get('/judges'), api.get('/judge-submissions')])
    judges.value = judgeResp.data
    judgeSubmissions.value = submissionResp.data
  } catch (error) {
    ElMessage.error(errorText(error))
  }
}

function openScoreCorrection(submission: JudgeSubmission) {
  scoreCorrectionTarget.value = submission
  scoreCorrectionResults.value = (submission.scores || []).map((score) => ({
    ...score,
    absent: Boolean(score.absent),
    score: Number(score.score)
  }))
  scoreCorrectionOperator.value = ''
  scoreCorrectionReason.value = ''
  scoreCorrectionDialogVisible.value = true
}

function toggleCorrectionAbsent(row: JudgeSubmissionScore & { absent: boolean; score: number }) {
  if (row.absent) {
    row.score = 0
  } else if (!scoreOptions.includes(row.score)) {
    row.score = 1
  }
}

async function submitScoreCorrection() {
  const target = scoreCorrectionTarget.value
  if (!target) return
  if (!scoreCorrectionOperator.value.trim() || !scoreCorrectionReason.value.trim()) {
    ElMessage.warning('请填写更正人姓名和更正原因')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确认更正第${target.round_no}轮 ${target.table_no} 的成绩？更正后积分和晋级状态会立即同步。`,
      '确认管理员更正',
      { type: 'warning', confirmButtonText: '确认更正', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  scoreCorrectionSubmitting.value = true
  try {
    const resp = await api.post(`/rounds/${target.round_no}/tables/${target.table_id}/correct-score`, {
      operator_name: scoreCorrectionOperator.value.trim(),
      reason: scoreCorrectionReason.value.trim(),
      results: scoreCorrectionResults.value.map((row) => ({
        player_id: row.player_id,
        score: row.absent ? 0 : row.score,
        absent: row.absent
      }))
    })
    ElMessage.success(resp.data.message)
    scoreCorrectionDialogVisible.value = false
    await Promise.all([loadJudges(), refreshLeaderboards(), loadTables(), loadSeatingChart(), loadProgressionChart()])
  } catch (error) {
    ElMessage.error(errorText(error))
  } finally {
    scoreCorrectionSubmitting.value = false
  }
}

async function generateJudges() {
  try {
    const resp = await api.post('/judges/generate', { count: judgeGenerateCount.value })
    judgeGroupText.value = resp.data.text
    ElMessage.success(`已生成 ${resp.data.created.length} 个裁判账号`)
    await loadJudges()
  } catch (error) {
    ElMessage.error(errorText(error))
  }
}

async function saveJudge(judge: JudgeAccount) {
  try {
    await api.patch(`/judges/${judge.id}`, {
      claimed_by: judge.claimed_by,
      note: judge.note,
      is_active: judge.is_active
    })
    ElMessage.success('裁判账号已保存')
  } catch (error) {
    ElMessage.error(errorText(error))
  }
}

async function toggleJudge(judge: JudgeAccount) {
  judge.is_active = !judge.is_active
  await saveJudge(judge)
  await loadJudges()
}

async function resetJudgePassword(judge: JudgeAccount) {
  try {
    const resp = await api.post(`/judges/${judge.id}/reset-password`)
    judge.initial_password = resp.data.password
    ElMessage.success(`${judge.account} 密码已重置为 ${resp.data.password}`)
    await loadJudges()
  } catch (error) {
    ElMessage.error(errorText(error))
  }
}

async function copyJudgeText() {
  const text =
    judgeGroupText.value ||
    ['裁判账号领取表', '请接龙：姓名 + 领取账号', '', ...judges.value.map((judge) => `${judge.account} / ${judge.initial_password}`)].join('\n')
  await navigator.clipboard.writeText(text)
  ElMessage.success('微信群文本已复制')
}

function scoreSummary(scores: Array<{ score: number }>) {
  return (scores || []).map((item) => item.score).join(' / ')
}

function downloadReport() {
  window.location.href = '/api/export'
}

function downloadLiveScoreboard() {
  window.location.href = '/api/export/live-scoreboard'
}

onMounted(() => {
  refreshAll()
  if (activeTab.value === 'schedule') {
    loadTables()
  }
  if (activeTab.value === 'seating') {
    loadSeatingChart()
  }
  if (activeTab.value === 'progression') {
    loadProgressionChart()
  }
  if (activeTab.value === 'judges') {
    loadJudges()
  }
  window.setInterval(refreshVisibleData, 12000)
})
</script>

<style scoped>
.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 14px;
}

.panel-head p {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 14px;
}

.score-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 16px;
}

.search-row {
  display: grid;
  grid-template-columns: minmax(180px, 1fr) auto;
  gap: 10px;
  align-items: center;
  margin-bottom: 12px;
}

.score-correction-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin: 16px 0 10px;
  color: #475569;
  font-size: 14px;
}

.score-correction-form {
  display: grid;
  gap: 12px;
  margin-top: 16px;
}

.score-correction-history + .score-correction-history {
  border-top: 1px solid #e2e8f0;
  margin-top: 10px;
  padding-top: 10px;
}

.score-correction-history p {
  margin: 4px 0 0;
  color: #475569;
  line-height: 1.45;
}

.toolbar-search {
  width: min(360px, 100%);
}

.leaderboard-tabs {
  margin-top: 4px;
}

.leaderboard-tabs :deep(.el-tabs__header) {
  margin-bottom: 6px;
}

.clickable-table :deep(.el-table__body tr) {
  cursor: pointer;
}

.clickable-table :deep(.el-table__body tr:hover > td.el-table__cell) {
  background: #eef6ff;
}

.qr-dialog-body {
  display: grid;
  justify-items: center;
  gap: 14px;
}

.qr-dialog-image {
  width: min(280px, 78vw);
  height: min(280px, 78vw);
  object-fit: contain;
  border: 1px solid #dbe4f0;
  border-radius: 8px;
  background: #fff;
}

.qr-dialog-info {
  width: 100%;
  text-align: center;
  color: #475569;
  line-height: 1.6;
}

.qr-dialog-info h3 {
  margin: 0 0 4px;
  color: #172033;
  font-size: 22px;
}

.qr-dialog-info p {
  margin: 2px 0;
}

.judge-record-title {
  margin-top: 24px;
}

.seat-layout {
  display: grid;
  grid-template-columns: minmax(300px, 1fr) 520px;
  gap: 16px;
  align-items: start;
  margin-top: 16px;
}

.seat-map-scroll {
  height: calc(100vh - 190px);
  min-height: 560px;
  overflow: hidden;
  border: 1px solid #d9e2ef;
  border-radius: 8px;
  background: #f8fafc;
  display: flex;
  justify-content: center;
  align-items: center;
}

.seat-map-canvas {
  position: relative;
  height: 100%;
  aspect-ratio: 1661 / 4456;
  max-width: 100%;
}

.seat-map-image {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.seat-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  width: clamp(16px, 1.55vw, 22px);
  height: clamp(12px, 1.05vw, 16px);
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.58);
  color: rgba(51, 65, 85, 0.72);
  font-size: clamp(7px, 0.48vw, 9px);
  font-weight: 700;
  cursor: pointer;
  box-shadow: none;
  padding: 0;
}

.seat-marker.occupied {
  border-color: #2563eb;
  background: rgba(37, 99, 235, 0.86);
  color: #fff;
}

.seat-marker.submitted {
  border-color: #16a34a;
  background: rgba(22, 163, 74, 0.86);
}

.seat-marker.active {
  width: clamp(22px, 2vw, 28px);
  height: clamp(16px, 1.35vw, 20px);
  font-size: clamp(8px, 0.62vw, 10px);
  outline: 2px solid rgba(245, 158, 11, 0.5);
  z-index: 3;
}

.seat-detail {
  position: sticky;
  top: 18px;
  display: grid;
  gap: 14px;
  min-width: 0;
}

.seat-detail-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.seat-actions {
  display: flex;
  justify-content: flex-end;
}

.judge-submission-card {
  padding: 10px 12px;
  border: 1px solid #d9e2ef;
  border-radius: 8px;
  background: #f8fafc;
  color: #334155;
  line-height: 1.8;
  font-size: 14px;
}

.seat-detail-head h3,
.empty-seat-tip h3,
.overflow-list h3 {
  margin: 0 0 6px;
  font-size: 17px;
}

.seat-detail-head p,
.empty-seat-tip p {
  margin: 0;
  color: #64748b;
}

.empty-seat-tip {
  padding: 18px;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  background: #f8fafc;
}

.overflow-list {
  display: grid;
  gap: 8px;
  max-height: 280px;
  overflow-y: auto;
  padding-right: 4px;
}

.overflow-item {
  width: 100%;
  border: 1px solid #d9e2ef;
  border-radius: 8px;
  background: #fff;
  padding: 10px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  cursor: pointer;
  color: #334155;
}

.overflow-item span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.overflow-item:hover {
  border-color: #2563eb;
  color: #1d4ed8;
}

.progression-board {
  margin-top: 18px;
  padding-bottom: 6px;
}

.progression-round {
  min-width: 0;
}

.progression-round-head {
  height: 54px;
  display: grid;
  align-content: center;
  text-align: center;
  margin-bottom: 12px;
}

.progression-round-head h3 {
  margin: 0;
  color: #172033;
  font-size: 18px;
}

.progression-round-head span {
  margin-top: 4px;
  color: #64748b;
  font-size: 13px;
}

.progression-table-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 14px;
}

.progression-table-card {
  position: relative;
  border: 1px solid #dbe4f0;
  border-radius: 8px;
  background: #f8fafc;
  overflow: hidden;
}

.progression-table-head {
  min-height: 40px;
  padding: 8px;
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 6px;
  align-items: center;
  border-bottom: 1px solid #e5edf6;
  color: #64748b;
  font-size: 13px;
}

.progression-table-head strong {
  color: #172033;
}

.progression-player {
  width: 100%;
  min-height: 58px;
  border: 0;
  border-bottom: 1px solid #e5edf6;
  background: #fff;
  display: grid;
  grid-template-columns: 32px minmax(0, 1fr) 44px;
  gap: 8px;
  align-items: center;
  padding: 9px 8px;
  color: #172033;
  text-align: left;
  cursor: pointer;
}

.progression-player:last-child {
  border-bottom: 0;
}

.progression-player:hover {
  background: #eef6ff;
}

.advance-icon {
  width: 28px;
  height: 32px;
  display: inline-grid;
  place-items: center;
  background: #cbd8e7;
  color: #fff;
  font-weight: 800;
  font-size: 14px;
  clip-path: polygon(0 0, 100% 0, 100% 100%, 50% 78%, 0 100%);
}

.progression-player.advanced .advance-icon {
  background: #2563eb;
}

.progression-player.final .advance-icon {
  background: #16a34a;
}

.progression-player.stopped .advance-icon {
  background: #94a3b8;
}

.progression-player.absent .advance-icon {
  background: #dc2626;
}

.progression-player-main {
  min-width: 0;
  display: grid;
  gap: 3px;
}

.progression-player-main strong,
.progression-player-main small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.progression-player-main small,
.progression-score small {
  color: #64748b;
  font-size: 12px;
}

.progression-score {
  display: grid;
  justify-items: end;
  gap: 2px;
  font-size: 18px;
  font-weight: 800;
}

.progression-empty {
  min-height: 90px;
  display: grid;
  place-items: center;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  color: #94a3b8;
  background: #f8fafc;
}

@media (max-width: 1200px) {
  .score-grid {
    grid-template-columns: 1fr;
  }

  .seat-layout {
    grid-template-columns: 1fr;
  }

  .seat-detail {
    position: static;
  }
}

@media (max-width: 1050px) {
  .progression-table-list {
    grid-template-columns: 1fr;
  }
}

.export-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin: 14px 0 10px;
}

.export-note {
  color: #64748b;
  margin-top: 8px;
}
</style>
