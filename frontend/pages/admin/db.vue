<!-- <template>
  <div class="db-component-wrapper">
    <div class="panel-header">
      <h3>数据库管理</h3>
    </div>
    <div v-for="i in 8" :key="i" class="course-item">
      <div class="course-thumb" style="background-color: #fce4ec;"></div>
      <div class="course-info">
        <h4>IT项目管理培训-计算机2201-08</h4>
        <p>计算机学院 | 开课: 2025-09-08 | 学分: 2.0</p>
        <div class="teacher">授课教师: <span class="avatar-icon">👤</span></div>
      </div>
      <div class="more-link">更多</div>
    </div>
  </div>
</template>

<style scoped>
/* 样式与 admin.vue 保持一致，确保整体统一 */
.panel-header h3 { margin: 0 0 20px 0; font-size: 18px; color: #333; border-left: 4px solid #28b5c1; padding-left: 12px; line-height: 1.2; }
.course-item { display: flex; padding: 15px 0; border-bottom: 1px solid #f5f5f5; align-items: center; }
.course-thumb { width: 140px; height: 80px; border-radius: 4px; margin-right: 15px; }
.course-info h4 { margin: 0 0 8px 0; font-size: 15px; }
.course-info p { margin: 0; font-size: 12px; color: #666; }
.teacher { margin-top: 5px; font-size: 12px; color: #888; }
.more-link { margin-left: auto; color: #28b5c1; cursor: pointer; font-size: 13px; }
</style> -->



<template>
  <div class="db-component-wrapper">
    <div class="panel-header">
      <h3>教学分析</h3>
      
    </div>
	<button class="backup-btn" @click="handleBackupClick">⚡ 立即备份数据库</button>
    <div class="info-banner">
      最近备份时间：2026-02-04 14:30 (状态：成功)
    </div>

    <div v-for="i in 5" :key="i" class="course-item">
      <div class="course-thumb" style="background-color: #fce4ec;"></div>
      <div class="course-info">
        <h4>自动备份快照 - #00{{i}}</h4>
        <p>存储位置: Cloud_Storage_01 | 文件大小: 45.2MB | 格式: .sql.gz</p>
        <div class="teacher">操作员: <span class="avatar-icon">🤖 系统自动</span></div>
      </div>
      <div class="more-link">下载</div>
    </div>
  </div>
</template>

<script setup>
const handleBackupClick = () => {
  // 简单的系统原生弹出框，也可以改用你之前代码中的自定义 Modal
  const isConfirmed = confirm("确定要立即备份数据库吗？这可能需要几分钟时间。");
  if (isConfirmed) {
    alert("备份指令已发出，请稍后在下载列表中查看。");
    // 这里调用后台备份 API
  }
};
</script>

<style scoped>
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.panel-header h3 { 
  margin: 0; 
  font-size: 18px; 
  color: #333; 
  border-left: 4px solid #28b5c1; 
  padding-left: 12px; 
  line-height: 1.2; 
}

.backup-btn {
  background-color: #3A445C;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: 0.3s;
}

.backup-btn:hover {
  background-color: #28b5c1;
}

.info-banner {
  background-color: #fff9c4;
  padding: 10px;
  border-radius: 4px;
  font-size: 13px;
  margin-bottom: 20px;
  color: #856404;
}

.course-item { display: flex; padding: 15px 0; border-bottom: 1px solid #f5f5f5; align-items: center; }
.course-thumb { width: 140px; height: 80px; border-radius: 4px; margin-right: 15px; }
.course-info h4 { margin: 0 0 8px 0; font-size: 15px; }
.course-info p { margin: 0; font-size: 12px; color: #666; }
.teacher { margin-top: 5px; font-size: 12px; color: #888; }
.more-link { margin-left: auto; color: #28b5c1; cursor: pointer; font-size: 13px; }
</style>