import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import Vant from 'vant'
import 'element-plus/dist/index.css'
import 'vant/lib/index.css'
import App from './App.vue'
import router from './router'
import './styles/global.css'

createApp(App).use(router).use(ElementPlus).use(Vant).mount('#app')
