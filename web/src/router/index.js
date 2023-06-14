import VueRouter from 'vue-router'
/* import HelloWorld from '../components/HelloWorld.vue' */
import SearchPage from '../pages/SearchPage.vue'

export default new VueRouter({
    mode: 'history',
    routes: [
        {path: '/search', name: 'SearchPage', component: SearchPage},
        /*{path: '/hello', name: 'HelloWorld', component: HelloWorld}*/
    ]
})