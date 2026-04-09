<template>
  <div class="page-wrapper">
    <div class="app-container">
      
      <header class="top-nav"></header>

      <main class="main-body">
        
        <aside class="sidebar">
          <div class="user-card">
            <div class="avatar-wrapper">
              <svg class="avatar-svg" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
                <path d="M512 512c121.5 0 220-98.5 220-220S633.5 72 512 72s-220 98.5-220 220 98.5 220 220 220z m0 60c-162.4 0-492 81.4-492 243.2V892h984V815.2c0-161.8-329.6-243.2-492-243.2z" fill="#28b5c1"/>
              </svg>
            </div>
            <p class="user-name">张俊琛</p>
            <p class="user-role">学生</p>
          </div>

          <div class="sidebar-divider"></div>

          <nav class="menu-list">
            <div class="nav-item hover-effect">🏠 首页</div>
            <div class="nav-item active-item">📋 我的课程</div>
            <div class="nav-item hover-effect">📢 公告</div>
            <div class="nav-item hover-effect" @click="openImportModal">📁 导入教师</div>
            <div class="nav-item hover-effect">🗂️ 我的档案</div>
          </nav>
        </aside>

        <section class="content-panel">
          <div class="panel-header">
            <h3>我的课程</h3>
          </div>
          <div v-for="i in 8" :key="i" class="course-item">
            <div class="course-thumb"></div>
            <div class="course-info">
              <h4>IT项目管理培训-计算机2201-08</h4>
              <p>计算机学院 | 开课: 2025-09-08 | 学分: 2.0</p>
              <div class="teacher">授课教师: <span class="avatar-icon">👤</span></div>
            </div>
            <div class="more-link">更多</div>
          </div>
        </section>

      </main>
    </div>

    <!-- <div v-if="showModal" class="modal-mask">
      <div class="modal-container">
        <h3>导入教师数据</h3>
        <div class="upload-box" @click="triggerFile">
          <p v-if="!file">点击此处选择 Excel 文件</p>
          <p v-else class="file-name">已选文件: {{ file.name }}</p>
          <input type="file" ref="fileInput" hidden accept=".xlsx,.xls" @change="onFileChange">
        </div>
        <div class="modal-btns">
          <button @click="closeModal">取消</button>
          <button class="confirm" :disabled="!file" @click="handleImport">确认导入</button>
        </div>
      </div>
    </div> -->
  </div>
</template>

<script setup>
import { ref } from 'vue';

const showModal = ref(false);
const file = ref(null);
const fileInput = ref(null);

const openImportModal = () => { showModal.value = true; };
const closeModal = () => { showModal.value = false; file.value = null; };
const triggerFile = () => { fileInput.value.click(); };
const onFileChange = (e) => { file.value = e.target.files[0]; };
const handleImport = () => {
  alert('导入成功: ' + file.value.name);
  closeModal();
};
</script>

<style scoped>
/* 基础背景 */
.page-wrapper {
  background-color: #e5e5e5;
  min-height: 100vh;
  display: flex;
  justify-content: center;
}

/* 主容器 1260*660 */
.app-container {
  width: 1260px;
  min-height: 660px;
  background-color: #F4F4F4;
  display: flex;
  flex-direction: column;
}

/* 顶部蓝色条 */
.top-nav {
  width: 100%;
  height: 60px;
  background-color: #3A445C;
}

/* 主体内容布局：左右留白 40px */
.main-body {
  display: flex;
  padding: 30px 40px; 
  gap: 20px;
  align-items: flex-start;
}

/* --- 左侧边栏样式 --- */
.sidebar {
  width: 210px;
  height: 500px; /* 固定高度 */
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.user-card {
  padding: 20px 0;
  text-align: center;
}

.avatar-wrapper {
  width: 65px; height: 65px;
  border: 2px solid #28b5c1;
  border-radius: 50%;
  margin: 0 auto 10px;
  display: flex;
  align-items: center; justify-content: center;
}

.avatar-svg { width: 40px; height: 40px; }

.user-name { font-size: 16px; font-weight: bold; margin: 4px 0; }
.user-role { font-size: 13px; color: #999; margin-bottom: 8px; }

.sidebar-divider {
  height: 1px;
  background-color: #f0f0f0;
  width: 100%;
}

.menu-list { padding: 10px; }

/* 菜单按钮：圆角矩形 */
.nav-item {
  height: 38px;
  line-height: 38px;
  padding: 0 15px;
  margin-bottom: 4px;
  border-radius: 19px; /* 高度的一半 */
  font-size: 14px;
  cursor: pointer;
  transition: 0.2s;
}

.active-item { background-color: #28b5c1; color: white; }
.hover-effect:hover { background-color: #eeeeee; }

/* --- 右侧内容面板 --- */
.content-panel {
  flex: 1;
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  padding: 20px;
}

.course-item {
  display: flex;
  padding: 15px 0;
  border-bottom: 1px solid #f5f5f5;
  align-items: center;
}

.course-thumb { width: 140px; height: 80px; background-color: #e3f2fd; border-radius: 4px; margin-right: 15px; }
.course-info h4 { margin: 0 0 8px 0; font-size: 15px; }
.course-info p { margin: 0; font-size: 12px; color: #666; }
.teacher { margin-top: 5px; font-size: 12px; color: #888; }
.more-link { margin-left: auto; color: #28b5c1; cursor: pointer; font-size: 13px; }

/* --- 弹窗样式 --- */
.modal-mask {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center;
}
.modal-container { background: white; padding: 25px; border-radius: 8px; width: 350px; text-align: center; }
.upload-box { border: 2px dashed #ddd; padding: 30px; margin: 20px 0; cursor: pointer; }
.upload-box:hover { border-color: #28b5c1; }
.modal-btns { display: flex; justify-content: space-around; }
.modal-btns button { padding: 8px 20px; border: none; cursor: pointer; border-radius: 4px; }
.confirm { background: #3A445C; color: white; }
.confirm:disabled { background: #ccc; }
</style>