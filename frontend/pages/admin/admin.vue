<template>
  <div class="admin-component-wrapper">
    <div class="panel-header">
      <h3>教师管理</h3>
    </div>
    <button class="import-btn" @click="openImportModal">📁 导入教师</button>
    <div v-for="i in 8" :key="i" class="course-item">
      <div class="course-thumb"></div>
      <div class="course-info">
        <h4>教师姓名-管理单元-0{{i}}</h4>
        <p>所属学院 | 入职日期: 2023-09-01 | 状态: 在职</p>
        <div class="teacher">管理工号: <span class="avatar-icon">🆔</span></div>
      </div>
      <div class="more-link">详情</div>
    </div>

    <div v-if="showModal" class="modal-mask">
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
    </div>
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
const handleImport = () => { alert('导入成功'); closeModal(); };
</script>

<style scoped>
	/* 保持你原本的所有样式定义 */
	.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
	.panel-header h3 { margin: 0; font-size: 18px; color: #333; border-left: 4px solid #28b5c1; padding-left: 12px; line-height: 1.2; }
	.import-btn { background-color: #3A445C; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; }

	.course-item { display: flex; padding: 15px 0; border-bottom: 1px solid #f5f5f5; align-items: center; }
	.course-thumb { width: 140px; height: 80px; background-color: #e3f2fd; border-radius: 4px; margin-right: 15px; }
	.course-info h4 { margin: 0 0 8px 0; font-size: 15px; }
	.course-info p { margin: 0; font-size: 12px; color: #666; }
	.teacher { margin-top: 5px; font-size: 12px; color: #888; }
	.more-link { margin-left: auto; color: #28b5c1; cursor: pointer; font-size: 13px; }

	.modal-mask { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 100; }
	.modal-container { background: white; padding: 25px; border-radius: 8px; width: 350px; text-align: center; }
	.upload-box { border: 2px dashed #ddd; padding: 30px; margin: 20px 0; cursor: pointer; }
	.modal-btns button { padding: 8px 20px; border: none; cursor: pointer; border-radius: 4px; }
	.confirm { background: #3A445C; color: white; }
</style>