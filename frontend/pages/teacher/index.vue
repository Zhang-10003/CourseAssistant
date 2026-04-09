<template>
  <div class="page-wrapper">
    <div class="app-container">
      <header class="top-nav">
        <div class="nav-content">
          <span :class="{ 'clickable': currentCourse }" @click="currentCourse = null">课程助手 - 教师端</span>
          <template v-if="currentCourse">
            <span class="breadcrumb-sep"> / </span>
            <span class="breadcrumb-active">{{ currentCourse.title }}</span>
          </template>
        </div>
      </header>

      <main class="main-body">
        <aside class="sidebar">
          <div class="user-card">
            <div class="avatar-wrapper">
              <svg class="avatar-svg" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
                <path d="M512 512c121.5 0 220-98.5 220-220S633.5 72 512 72s-220 98.5-220 220 98.5 220 220 220z m0 60c-162.4 0-492 81.4-492 243.2V892h984V815.2c0-161.8-329.6-243.2-492-243.2z" fill="#28b5c1"/>
              </svg>
            </div>
            <p class="user-name">{{ userName }}</p>
            <p class="user-role">{{ userRole }}</p>
          </div>

          <div class="sidebar-divider"></div>
			
          <nav class="menu-list">
            <div 
              class="nav-item hover-effect" 
              :class="{ 'active-item': currentTab === 'CourseClass' }"
              @click="tabChange('CourseClass')"
            >📋 课程班级</div>
            
            <div 
              class="nav-item hover-effect" 
              :class="{ 'active-item': currentTab === 'WorkAssign' }"
              @click="tabChange('WorkAssign')"
            >🗄️ 作业布置</div>


          </nav>
        </aside>

        <section class="content-panel">
          <CourseClass 
            v-if="currentTab === 'CourseClass'" 
            :activeCourse="currentCourse"
            @manage="handleManage" 
            @back="currentCourse = null"
          />
          <WorkAssign v-else-if="currentTab === 'WorkAssign'" />
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import CourseClass from './CourseClass.vue';
import WorkAssign from './WorkAssign.vue';

const currentTab = ref('CourseClass');
const currentCourse = ref(null);

// 用户信息状态
const userName = ref('加载中...');
const userRole = ref('教师');

const handleManage = (course) => { currentCourse.value = course; };
const tabChange = (tab) => { currentTab.value = tab; currentCourse.value = null; };

/**
 * 核心逻辑：获取用户信息
 */
const fetchUserInfo = async () => {
  const token = localStorage.getItem('token');
  let userId = localStorage.getItem('user_id');

  // --- 关键防御逻辑：清洗 userId ---
  // 如果 userId 包含 JSON 字符（如你报错图中所示），尝试解析它
  if (userId && (userId.includes('{') || userId.includes(':'))) {
    try {
      const obj = JSON.parse(userId);
      userId = obj.data || obj.user_id || userId;
    } catch (e) {
      console.error("解析 userId 出错", e);
    }
  }

  // 最终确保 userId 只是一个单纯的数字字符串
  userId = String(userId).replace(/[^0-9]/g, '');

  if (!token || !userId) {
    userName.value = "未登录";
    return;
  }

  // 使用 uni.request 发起请求
  uni.request({
    url: `http://127.0.0.1:8000/auth/user/${userId}/name`,
    method: 'GET',
    header: {
      'Authorization': `Bearer ${token}`
    },
    success: (res) => {
      // res.data 才是后端返回的 ResponseOut 结构
      if (res.data && res.data.code === "000") {
        userName.value = res.data.data.name;
        const roleMap = { 0: '管理员', 1: '教师', 2: '学生' };
        userRole.value = roleMap[res.data.data.user_type] || '教师';
      } else {
        userName.value = "查询失败";
        console.error("后端返回错误:", res.data);
      }
    },
    fail: (err) => {
      userName.value = "网络异常";
      console.error("请求失败:", err);
    }
  });
};

onMounted(() => {
  fetchUserInfo();
});
</script>

<style scoped>
/* 样式保持不变 */
.page-wrapper { background-color: #e5e5e5; min-height: 100vh; width: 100%; box-sizing: border-box; }
.app-container { max-width: 1600px; min-width: 1100px; margin: 0 auto; min-height: 100vh; background-color: #F4F4F4; display: flex; flex-direction: column; box-shadow: 0 0 10px rgba(0,0,0,0.05); }
.top-nav { width: 100%; height: 60px; background-color: #3A445C; display: flex; align-items: center; padding: 0 40px; color: white; font-size: 14px; box-sizing: border-box; }
.main-body { display: flex; padding: 30px 40px; gap: 20px; align-items: flex-start; flex: 1; box-sizing: border-box; overflow: hidden; }
.sidebar { width: 210px; background-color: #ffffff; border: 1px solid #e0e0e0; flex-shrink: 0; display: flex; flex-direction: column; }
.content-panel { flex: 1; background-color: #ffffff; border: 1px solid #e0e0e0; padding: 20px; min-height: 500px; width: 0; min-width: 0; display: flex; flex-direction: column; }
.breadcrumb-sep { margin: 0 8px; color: #888; }
.breadcrumb-active { color: #28b5c1; font-weight: bold; }
.clickable { cursor: pointer; transition: opacity 0.2s; }
.clickable:hover { opacity: 0.8; }
.user-card { padding: 20px 0; text-align: center; }
.avatar-wrapper { width: 65px; height: 65px; border: 2px solid #28b5c1; border-radius: 50%; margin: 0 auto 10px; display: flex; align-items: center; justify-content: center; }
.avatar-svg { width: 40px; height: 40px; }
.user-name { font-size: 16px; font-weight: bold; margin: 4px 0; }
.user-role { font-size: 13px; color: #999; margin-bottom: 8px; }
.sidebar-divider { height: 1px; background-color: #f0f0f0; width: 100%; }
.menu-list { padding: 10px; }
.nav-item { height: 38px; line-height: 38px; padding: 0 15px; margin-bottom: 4px; border-radius: 19px; font-size: 14px; cursor: pointer; transition: 0.2s; }
.active-item { background-color: #28b5c1 !important; color: white !important; }
.hover-effect:hover { background-color: #eeeeee; }
</style>