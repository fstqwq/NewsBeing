<template>
  <a-layout id="components-layout-demo-side" style="min-height: 100vh">
    <a-layout-sider v-model="collapsed" collapsible>
      <div class="logo">
          News Being
      </div>
      <a-menu theme="dark" :default-selected-keys="['1']" mode="inline">
        <a-menu-item key="1" @click="toSearch()">
          <a-icon type="desktop" />
          <span>Search</span>
        </a-menu-item>
        <!-- <a-menu-item key="2" @click="toHello()">
          <a-icon type="desktop" />
          <span>Hello</span>
        </a-menu-item> -->
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header style="background: #fff; padding: 0" />
      <a-layout-content style="margin: 0 16px">
        <Search></Search>
      </a-layout-content>
      <a-layout-footer style="text-align: center">
        News Being ©2023 Created by 杨宗翰, 吕优, 傅凌玥, 刘遇时 <br>
        UI Powered by Ant Design
      </a-layout-footer>
    </a-layout>
  </a-layout>
</template>
<script>
import Search from '../components/Search.vue'
export default {
  components: {
    Search
  },
  data() {
    return {
      collapsed: false,
    };
  },
  methods: {
    toSearch(){
      this.$router.push('/search')
    },
    toHello(){
      this.$router.push('/hello')
    }
  }
};
</script>

<style>
#components-layout-demo-side .logo {
  height: 32px;
  /* background: rgba(255, 255, 255, 0.2); */
  margin: 16px;
  font-size: 20px;
  color: white;
}
</style>