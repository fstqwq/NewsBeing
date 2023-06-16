<template>
  <a-layout id="components-layout-demo-side" style="min-height: 100vh">
    <a-layout-sider v-model="collapsed" collapsible>
      <div class="logo">
          <span style="color: #1890ff;">New</span><span style="color: #52c41a;">s</span> <span style="color: #1890ff;">B</span><span style="color: #52c41a;">e</span><span style="color: #1890ff;">ing</span>      
      </div>
      <a-menu theme="dark" :default-selected-keys="['2']" mode="inline">
        <a-menu-item key="1" @click="toSearch()">
          <a-icon type="file-search" />
          <span>Search</span>
        </a-menu-item>
        <a-menu-item key="2" @click="toChat()">
          <a-icon type="message" />
          <span>Chat</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-content style="margin: 0 16px">
        <Chat></Chat>
      </a-layout-content>
      <a-layout-footer style="text-align: center">
        News Being ©2023 Created by 杨宗翰, 吕优, 傅凌玥, 刘遇时 <br>
        UI Powered by Ant Design
      </a-layout-footer>
    </a-layout>
  </a-layout>
</template>
<script>
import Chat from '../components/Chat.vue'
export default {
  components: {
    Chat
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
    toChat(){
      this.$router.push('/chat')
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