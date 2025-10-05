import './styles/tailwind.css'
import './styles/style.less'

import { createApp } from 'vue'
import App from './App.vue'
import router from './config/router/index'

const app = createApp(App)
app.use(router)
app.mount('#app')
