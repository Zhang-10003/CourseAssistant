<template>
  <div class="course-component-wrapper">
    <div class="panel-header">
      <div class="header-left">
        <div class="title-line"></div>
        <h3 class="breadcrumb-title">
          <span class="root-node" @click="resetToLevel(1)">学情报告</span>
          <template v-if="viewLevel === 2">
            <span class="sep">></span>
            <span class="current-node">作业详情</span>
          </template>
        </h3>
      </div>
    </div>

    <div v-if="viewLevel === 1" class="course-grid">
      <div v-for="item in homeworkNotifications" :key="item.id" class="course-card">
        <div class="course-cover" :style="{ border: `1.5px solid ${item.themeColor}`, background: 'white' }">
          <span class="cover-icon" :style="{ color: item.themeColor }">{{ item.icon }}</span>
        </div>

        <div class="course-main">
          <div class="title-row">
            <h4>{{ item.typeText }}</h4>
            <span class="class-tag">{{ item.time }}</span>
          </div>
          <div class="info-meta">
            <div class="meta-line">
              <span>
                {{ item.prefix }} 
                <span class="highlight-link">{{ item.courseName }}</span> 
                {{ item.midfix }} 
                <span class="highlight-link">{{ item.taskName }}</span>
                <template v-if="item.score">
                   获得了 <span class="score-num">{{ item.score }}</span> 分
                </template>
              </span>
            </div>
          </div>
        </div>

        <div class="course-action">
          <button class="manage-btn" @click="enterDetail(item)">查看详情</button>
        </div>
      </div>
    </div>

    <div v-else-if="viewLevel === 2" class="detail-view">
      <button class="manage-btn" @click="resetToLevel(1)" style="margin-bottom: 20px;">返回列表</button>
      <div class="course-card" style="cursor: default;">
        <div class="course-main">
           <h4>{{ activeItem?.taskName }}</h4>
           <p style="color: #666; margin-top: 10px;">这里是该作业的具体提交要求、截止日期等详细内容...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const viewLevel = ref(1);
const activeItem = ref(null);

// 模拟作业数据
const homeworkNotifications = ref([
  {
    id: 2,
    typeText: '作业成绩',
    icon: '🔔',
    themeColor: '#28b5c1', // 青色
    time: '2023.03.28 17:26',
    prefix: '你在课程',
    courseName: '高等数学A2（二）',
    midfix: '的作业',
    taskName: '练习6.6 方向导数与梯度',
    score: '98.0'
  }
]);

const enterDetail = (item) => {
  activeItem.value = item;
  viewLevel.value = 2;
};

const resetToLevel = (level) => {
  viewLevel.value = level;
};
</script>

<style scoped>

.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid #f0f2f5; }
.header-left { display: flex; align-items: center; }
.title-line { width: 4px; height: 20px; background-color: #28b5c1; margin-right: 12px; }
.breadcrumb-title { margin: 0; font-size: 18px; display: flex; align-items: center; color: #333; }
.root-node { cursor: pointer; transition: color 0.2s; }
.root-node:hover { color: #28b5c1; }
.sep { margin: 0 10px; color: #999; font-weight: normal; }
.current-node { color: #28b5c1; font-weight: bold; }

.course-card { 
  display: flex; 
  padding: 20px; 
  background: #ffffff; 
  border: 1px solid #f0f0f0; 
  border-radius: 12px; 
  align-items: center; 
  margin-bottom: 16px; 
  transition: all 0.3s ease; 
  cursor: pointer; 
}
.course-card:hover { border-color: #28b5c1; box-shadow: 0 6px 16px rgba(40, 181, 193, 0.12); }

/* 图标区域：保持你之前的大小 */
.course-cover { width: 60px; height: 60px; border-radius: 8px; margin-right: 20px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.cover-icon { font-size: 24px; }

.course-main { flex-grow: 1; }
.title-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.title-row h4 { margin: 0; font-size: 16px; color: #333; }

/* 班级标签样式改为时间样式 */
.class-tag { font-size: 12px; background: #f5f5f5; padding: 2px 8px; border-radius: 4px; color: #999; }

.info-meta { color: #444; font-size: 14px; line-height: 1.6; }

/* 新增：作业特有的链接和分数高亮 */
.highlight-link { color: #28b5c1; cursor: pointer; font-weight: 500; }
.highlight-link:hover { text-decoration: underline; }
.score-num { color: #28b5c1; font-weight: bold; font-size: 16px; }

/* 按钮样式：保持你原来的 manage-btn */
.manage-btn { background: transparent; color: #28b5c1; border: 1px solid #28b5c1; padding: 6px 15px; border-radius: 4px; font-size: 13px; cursor: pointer; }
.manage-btn:hover { background: #28b5c1; color: white; }

.detail-view { padding: 10px; }
</style>