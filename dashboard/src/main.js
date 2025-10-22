import './styles/tailwind.css'
import './styles/style.less'
import 'ant-design-vue/dist/reset.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './config/router/index'
import Antd from 'ant-design-vue'

const app = createApp(App)
app.use(router)
app.use(Antd)
app.mount('#app')
