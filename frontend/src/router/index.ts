import { createRouter, createWebHistory } from 'vue-router'
import AdminView from '../views/AdminView.vue'
import ScoreView from '../views/ScoreView.vue'
import PlayerView from '../views/PlayerView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/admin' },
    { path: '/admin', component: AdminView },
    { path: '/score', component: ScoreView },
    { path: '/player', component: PlayerView }
  ]
})

export default router
