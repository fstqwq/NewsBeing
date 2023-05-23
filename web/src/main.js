import Vue from 'vue'
import App from './App.vue'
import VueRouter from 'vue-router'
import router from './router'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/antd.css'

Vue.config.productionTip = false
Vue.use(VueRouter)
Vue.use(Antd)
new Vue({
  render: h => h(App),
  router: router
}).$mount('#app')
