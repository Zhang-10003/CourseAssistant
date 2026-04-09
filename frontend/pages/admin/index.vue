<template>
  <div class="page-wrapper">
    <div class="app-container">
      
      <header class="top-nav">
        <div class="nav-content">课程助手 - 管理员控制台</div>
      </header>

      <main class="main-body">
        <aside class="sidebar">
          <div class="user-card">
            <div class="avatar-wrapper">
              <svg class="avatar-svg" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
                <path d="M512 512c121.5 0 220-98.5 220-220S633.5 72 512 72s-220 98.5-220 220 98.5 220 220 220z m0 60c-162.4 0-492 81.4-492 243.2V892h984V815.2c0-161.8-329.6-243.2-492-243.2z" fill="#28b5c1"/>
              </svg>
            </div>
            <p class="user-name">管理员</p>
            <p class="user-role">管理</p>
          </div>

          <div class="sidebar-divider"></div>

          <nav class="menu-list">
            <div 
              class="nav-item hover-effect" 
              :class="{ 'active-item': currentTab === 'teacher' }"
              @click="currentTab = 'teacher'"
            >📋 教师管理</div>
            
            <div 
              class="nav-item hover-effect" 
              :class="{ 'active-item': currentTab === 'database' }"
              @click="currentTab = 'database'"
            >🗄️ 数据库管理</div>
          </nav>
        </aside>

        <section class="content-panel">
          <TeacherAdmin v-if="currentTab === 'teacher'" />
          <DbAdmin v-else-if="currentTab === 'database'" />
        </section>

      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import TeacherAdmin from './admin.vue';
import DbAdmin from './db.vue';

const currentTab = ref('teacher'); 
</script>

<style scoped>
/* 保持 B 站居中风格的容器逻辑 */
.page-wrapper {
  background-color: #e5e5e5;
  min-height: 100vh;
  width: 100%;
  overflow-x: auto;
}

.app-container {
  max-width: 1400px; 
  margin: 0 auto; 
  width: 100%;
  min-width: 1100px; 
  min-height: 100vh;
  background-color: #F4F4F4;
  display: flex;
  flex-direction: column;
  box-shadow: 0 0 20px rgba(0,0,0,0.05);
}

.top-nav {
  width: 100%;
  height: 60px;
  background-color: #3A445C;
  display: flex;
  align-items: center;
  padding: 0 40px;
  color: white;
  font-size: 14px;
  box-sizing: border-box;
}

.main-body {
  display: flex;
  padding: 30px 40px; 
  gap: 20px;
  align-items: flex-start;
  flex: 1;
  box-sizing: border-box;
}

.sidebar {
  width: 210px;
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

/* --- 侧边栏菜单样式优化 --- */
.user-card { padding: 20px 0; text-align: center; }
.avatar-wrapper { 
  width: 65px; height: 65px; 
  border: 2px solid #28b5c1; border-radius: 50%; 
  margin: 0 auto 10px; 
  display: flex; align-items: center; justify-content: center; 
}
.avatar-svg { width: 40px; height: 40px; }
.user-name { font-size: 16px; font-weight: bold; margin: 4px 0; }
.user-role { font-size: 13px; color: #999; margin-bottom: 8px; }
.sidebar-divider { height: 1px; background-color: #f0f0f0; width: 100%; }
.menu-list { padding: 10px; }

.nav-item { 
  height: 38px; 
  line-height: 38px; 
  padding: 0 15px; 
  margin-bottom: 4px; 
  border-radius: 19px; 
  font-size: 14px; 
  cursor: pointer; 
  transition: 0.2s; 
  color: #333;
}

/* 激活状态：固定青色背景和白色文字 */
.active-item { 
  background-color: #28b5c1 !important; 
  color: white !important; 
}

/* 悬浮状态修改：只对“没有激活”的项生效 */
.hover-effect:hover:not(.active-item) { 
  background-color: #eeeeee; 
}

/* 额外保险：确保激活项在悬浮时也不会变色 */
.active-item:hover {
  background-color: #28b5c1 !important;
  opacity: 0.9; /* 稍微给一点透明度变化作为反馈，如果不想要可以直接删掉 */
}

.content-panel {
  flex: 1; 
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  padding: 20px;
  min-height: 500px;
  min-width: 0;
}
</style>