import VueRouter from 'vue-router'
/* import HelloWorld from '../components/HelloWorld.vue' */
import SearchPage from '../pages/SearchPage.vue'
import ChatPage from "../pages/ChatPage.vue"
export default new VueRouter({
    mode: 'history',
    routes: [
        {path: '/search', name: 'SearchPage', component: SearchPage},
        {path: '/chat', name: 'ChatPage', component: ChatPage}
    ]
})