<template>
  <div class="db-component-wrapper">
    <div class="panel-header">
      <h3>作业草稿</h3>
      <div class="header-right">
        <button class="pure-text-btn" @click="handleAIClick">LLM智能出题</button>
      </div>
    </div>

    <div class="draft-list">
      <div 
        v-for="(item, index) in draftList" 
        :key="index" 
        class="course-card-style"
        @click="openDraftDetail(item)" 
      >
        <div class="status-side">
          <div class="status-dot" :style="{ backgroundColor: getStatusColor(item.deadline) }"></div>
        </div>
        <div class="course-main-content">
          <div class="title-row">
            <h4>{{ item.title }}</h4>
            <span class="status-tag">草稿</span>
          </div>
          <div class="info-meta">
            <span>截止时间: {{ item.deadline }}</span>
            <span class="divider">|</span>
            <span>题目数量: {{ item.qCount }} 道</span>
          </div>
        </div>
        <div class="course-action-area">
          <span class="action-link">查看详情</span>
          <span class="action-link delete" @click.stop="deleteDraft(index)">删除</span>
        </div>
      </div>
      
      <div v-if="draftList.length === 0" style="text-align: center; color: #999; padding: 40px;">
        暂无草稿数据
      </div>
    </div>

    <div v-if="isDraftDetailOpen" class="modal-overlay">
      <div class="draft-detail-modal">
        <div class="ai-preview-section">
          <div class="ai-preview-header">
            <div class="ai-preview-title">{{ currentDraft.title }} - 内容预览</div>
            <div class="header-right-ops">
              <div class="ai-close-icon" @click="isDraftDetailOpen = false">×</div>
            </div>
          </div>
          
          <div class="ai-preview-body">
            <div 
              v-for="(q, index) in currentDraftQuestions" 
              :key="index" 
              class="ai-q-card-v2"
            >
              <div class="ai-q-header-row">
                <span class="ai-type-label blue">
                  {{ q.q_type === 1 ? '多选题' : q.q_type === 2 ? '简答题' : '单选题' }}
                </span>
                <span class="ai-q-num">{{ index + 1 }}. {{ q.content }}</span>
              </div>
              <div class="ai-opt-list-v2">
                <div v-for="(opt, oIdx) in q.options" :key="oIdx" class="ai-opt-row">
                  <strong>{{ String.fromCharCode(65 + oIdx) }}.</strong> {{ opt }}
                </div>
              </div>
            </div>
            
            <div v-if="currentDraftQuestions.length === 0" class="ai-empty-preview">
              <p>该草稿暂无题目内容</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isAIModalOpen" class="modal-overlay">
      <div class="ai-window-container">
        <div class="ai-chat-section">
          <div class="ai-chat-body">
            <div class="ai-gemini-info">
              <div class="ai-text-bubble">
                我是LLM智能出题小助手，请问您有什么需要帮助的嘛！
              </div>
            </div>

            <div v-for="(msg, idx) in chatHistory" :key="idx">
              <div v-if="msg.role === 'user'" class="ai-chat-header">
                <div class="ai-user-bubble">{{ msg.content }}</div>
              </div>
              <div v-else class="ai-gemini-info">
                <div class="ai-text-bubble">{{ msg.content }}</div>
              </div>
            </div>
          </div>

          <div class="ai-chat-footer">
            <div class="ai-input-wrapper">
              <input 
                type="text" 
                v-model="aiInput" 
                placeholder="输入指令(如: 出2道Python题)" 
                @keyup.enter="sendAIRequest"
              >
              <div class="ai-send-btn" @click="sendAIRequest" title="发送指令">▲</div>
            </div>
          </div>
        </div>

        <div class="ai-preview-section">
          <div class="ai-preview-header">
            <div class="ai-preview-title">内容预览</div>
            <div class="header-right-ops">
              <span class="save-draft-span" @click="openSaveDialog">存为草稿</span>
              <div class="ai-close-icon" @click="isAIModalOpen = false">×</div>
            </div>
          </div>
          
          <div class="ai-preview-body">
            <div 
              v-for="(q, index) in aiGeneratedQuestions" 
              :key="index" 
              class="ai-q-card-v2"
            >
              <div class="ai-q-delete-btn" @click="removeAIQuestion(index)">删除</div>
              <div class="ai-q-header-row">
                <span class="ai-type-label" :class="q.typeColor">{{ q.typeName }}</span>
                <span class="ai-q-num">{{ index + 1 }}. {{ q.content }}</span>
              </div>
              <div v-if="q.options && q.options.length > 0" class="ai-opt-list-v2">
                <div v-for="(opt, oIdx) in q.options" :key="oIdx" class="ai-opt-row">
                  <strong>{{ String.fromCharCode(65 + oIdx) }}.</strong> {{ opt }}
                </div>
              </div>
            </div>

            <div v-if="isSaveDialogOpen" 
              class="save-dialog-overlay"
              :style="{ left: dialogPos.x + 'px', top: dialogPos.y + 'px' }"
            >
              <div class="dialog-header" @mousedown="startDrag">
                <span class="dialog-title">完善作业信息</span>
                <div class="drag-handle">⋮⋮</div>
              </div>

              <div class="dialog-form-v2">
                <div class="form-item-v2">
                  <label>作业标题</label>
                  <input v-model="saveForm.title" type="text" placeholder="输入作业名称..." class="styled-input">
                </div>

                <div class="form-item-v2">
                  <label>截止时间 ({{ currentYear }}年)</label>
                  <div class="time-picker-mini">
                    <div class="picker-group">
                      <input v-model="timeParts.month" type="number" min="1" max="12"><span>月</span>
                    </div>
                    <div class="picker-group">
                      <input v-model="timeParts.day" type="number" min="1" max="31"><span>日</span>
                    </div>
                    <div class="time-sep">:</div>
                    <div class="picker-group">
                      <input v-model="timeParts.hour" type="number" min="0" max="23"><span>时</span>
                    </div>
                    <div class="picker-group">
                      <input v-model="timeParts.minute" type="number" min="0" max="59"><span>分</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="dialog-footer-v2">
                <button class="btn-cancel" @click="isSaveDialogOpen = false">取消</button>
                <button class="btn-confirm" @click="saveDraft">确认保存</button>
              </div>
            </div>

            <div v-if="isLoading" class="ai-loading-box">
              <div class="spinner"></div>
              <div class="loading-text">正在为您出题...</div>
            </div>

            <div v-else-if="aiGeneratedQuestions.length === 0" class="ai-empty-preview">
              <p>暂无预览题目，请在左侧输入指令生成</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue';

const draftList = ref([]);
const isAIModalOpen = ref(false);
const aiInput = ref('');
const isLoading = ref(false);
const chatHistory = ref([]);
const aiGeneratedQuestions = ref([]);

const isDraftDetailOpen = ref(false);
const currentDraft = ref({});
const currentDraftQuestions = ref([]);
// 在 script setup 块中添加此函数
const getStatusColor = (deadlineStr) => {
  if (!deadlineStr) return '#52c41a'; // 默认绿色

  const now = new Date();
  // 将截止时间字符串 (例如 "2026-03-29 23:59") 转换为 Date 对象
  // 注意：如果后端返回格式不规范，可能需要处理兼容性
  const deadline = new Date(deadlineStr.replace(/-/g, '/')); 

  // 如果当前时间已经超过截止时间，返回灰色，否则返回绿色
  return now > deadline ? '#bfbfbf' : '#52c41a';
};
// --- 时间处理逻辑开始 ---
const currentYear = new Date().getFullYear();

// 获取当前时间的辅助函数
const getCurrentTimeParts = () => {
  const now = new Date();
  return {
    month: now.getMonth() + 1,
    day: now.getDate(),
    hour: now.getHours(),
    minute: now.getMinutes()
  };
};

const isSaveDialogOpen = ref(false);
const saveForm = reactive({ title: '', deadline: '' });
// 初始化为当前时间
const timeParts = reactive(getCurrentTimeParts());

watch(timeParts, (newVal) => {
  const mm = String(newVal.month).padStart(2, '0');
  const dd = String(newVal.day).padStart(2, '0');
  const hh = String(newVal.hour).padStart(2, '0');
  const min = String(newVal.minute).padStart(2, '0');
  // 这里的年份也改成了动态变量
  saveForm.deadline = `${currentYear}-${mm}-${dd} ${hh}:${min}`;
}, { immediate: true });

const openSaveDialog = () => {
  if (aiGeneratedQuestions.value.length === 0) return;
  // 每次打开弹窗前，重新抓取最新的当前时间
  const now = getCurrentTimeParts();
  Object.assign(timeParts, now);
  isSaveDialogOpen.value = true;
};
// --- 时间处理逻辑结束 ---

const fetchDraftList = () => {
  const token = localStorage.getItem('token');
  uni.request({
    url: 'http://127.0.0.1:8000/teacher/2/assignments',
    method: 'GET',
    header: { 'Authorization': `Bearer ${token}` },
    success: (res) => {
      if (res.data && res.data.code === 200) {
        draftList.value = res.data.data.map(item => ({
          title: item.title,
          deadline: item.deadline,
          qCount: item.q_count,
          assignment_id: item.assignment_id,
          user_id: item.user_id
        }));
      }
    }
  });
};

onMounted(() => {
  fetchDraftList();
});

const dialogPos = reactive({ x: 100, y: 50 });
let isDragging = false;
let startOffset = { x: 0, y: 0 };
const startDrag = (e) => {
  isDragging = true;
  startOffset.x = e.clientX - dialogPos.x;
  startOffset.y = e.clientY - dialogPos.y;
  const onMouseMove = (moveEvent) => {
    if (!isDragging) return;
    dialogPos.x = moveEvent.clientX - startOffset.x;
    dialogPos.y = moveEvent.clientY - startOffset.y;
  };
  const onMouseUp = () => {
    isDragging = false;
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
  };
  document.addEventListener('mousemove', onMouseMove);
  document.addEventListener('mouseup', onMouseUp);
};

const handleAIClick = () => { isAIModalOpen.value = true; };

const sendAIRequest = () => {
  if (!aiInput.value.trim() || isLoading.value) return;
  const userMsg = aiInput.value;
  chatHistory.value.push({ role: 'user', content: userMsg });
  aiInput.value = ''; 
  isLoading.value = true;
  const token = localStorage.getItem('token');
  uni.request({
    url: 'http://127.0.0.1:8000/question/ai-generate',
    method: 'POST',
    header: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    data: { input: userMsg },
    success: (res) => {
      if (res.data && res.data.code === 200) {
        aiGeneratedQuestions.value = res.data.data.map((item, idx) => {
          let typeName = '单选题', typeColor = 'blue';
          if (item.q_type === 1) { typeName = '多选题'; typeColor = 'green'; }
          else if (item.q_type === 2) { typeName = '简答题'; typeColor = 'orange'; }
          return { id: idx, content: item.content, options: item.options_data, typeName, typeColor };
        });
        chatHistory.value.push({ role: 'assistant', content: '题目已生成完毕。' });
      }
    },
    complete: () => { isLoading.value = false; }
  });
};

const saveDraft = () => { 
  if (!saveForm.title.trim()) return alert('请输入作业标题');
  const token = localStorage.getItem('token');
  uni.request({
    url: 'http://127.0.0.1:8000/assignment/create',
    method: 'POST',
    header: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    data: { user_id: 2, title: saveForm.title, deadline: saveForm.deadline },
    success: (res) => {
      if (res.data && (res.data.code === 200 || res.statusCode === 200)) {
        isSaveDialogOpen.value = false;
        isAIModalOpen.value = false;
        fetchDraftList();
      }
    }
  });
};

const removeAIQuestion = (index) => { aiGeneratedQuestions.value.splice(index, 1); };

const openDraftDetail = (item) => { 
  currentDraft.value = item;
  const token = localStorage.getItem('token');
  uni.request({
    url: `http://127.0.0.1:8000/teacher/${item.assignment_id}/detail`,
    method: 'GET',
    header: { 'Authorization': `Bearer ${token}` },
    success: (res) => {
      if (res.data && res.data.code === 200) {
        const questionList = res.data.data.questions;
        if (questionList && questionList.length > 0) {
          currentDraftQuestions.value = questionList.map(q => ({
            content: q.content,
            options: q.options_data || [],
            q_type: q.q_type 
          }));
        } else {
          currentDraftQuestions.value = [];
        }
        isDraftDetailOpen.value = true;
      }
    }
  });
};

const deleteDraft = (index) => { draftList.value.splice(index, 1); };
</script>

<style scoped>
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.panel-header h3 { margin: 0; font-size: 18px; color: #333; border-left: 4px solid #28b5c1; padding-left: 12px; line-height: 1.2; }
.pure-text-btn { background: transparent; color: #28b5c1; border: 1px solid #28b5c1; padding: 6px 15px; border-radius: 4px; font-size: 12px; cursor: pointer; }
.course-card-style { display: flex; padding: 20px; background: #fff; border: 1px solid #f0f0f0; border-radius: 12px; align-items: center; margin-bottom: 16px; cursor: pointer; transition: all 0.3s ease; }
.course-card-style:hover { border-color: #3b82f6; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1); }
.status-side { width: 30px; display: flex; justify-content: center; }
.status-dot { width: 10px; height: 10px; border-radius: 50%; }
.course-main-content { flex-grow: 1; padding-left: 10px; }
.title-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.title-row h4 { margin: 0; font-size: 16px; color: #333; }
.status-tag { font-size: 11px; background: #eee; padding: 1px 6px; border-radius: 3px; color: #888; }
.info-meta { color: #7f8c8d; font-size: 13px; }
.divider { margin: 0 8px; color: #e5e7eb; }
.course-action-area { display: flex; gap: 15px; margin-left: auto; }
.action-link { color: #28b5c1; font-size: 13px; }
.action-link.delete { color: #ff4d4f; }

.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.ai-window-container { width: 63vw; height: 85vh; background: #fff; border-radius: 12px; display: flex; overflow: hidden; }

.draft-detail-modal { width: 60%; height: 85vh; background: #fff; border-radius: 12px; display: flex; overflow: hidden; }

.ai-chat-section { width: 320px; background: #f8fafc; border-right: 1px solid #e5e7eb; display: flex; flex-direction: column; }
.ai-chat-body { flex: 1; padding: 15px; overflow-y: auto; }
.ai-text-bubble { background: #fff; padding: 10px 14px; border-radius: 4px 18px 18px 18px; font-size: 13px; color: #374151; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px; }
.ai-user-bubble { background: #3b82f6; color: #fff; padding: 10px 16px; border-radius: 20px 20px 4px 20px; font-size: 13px; margin-bottom: 15px; align-self: flex-end; }
.ai-chat-footer { padding: 12px 15px; border-top: 1px solid #e5e7eb; }
.ai-input-wrapper { position: relative; display: flex; align-items: center; }
.ai-input-wrapper input { width: 100%; padding: 10px 40px 10px 16px; border: 1px solid #e5e7eb; border-radius: 20px; outline: none; font-size: 13px; }
.ai-send-btn { position: absolute; right: 12px; color: #3b82f6; cursor: pointer; transition: transform 0.2s; }
.ai-send-btn:hover { transform: scale(1.2); }

.ai-preview-section { flex: 1; display: flex; flex-direction: column; position: relative; }
.ai-preview-header { padding: 15px 20px; border-bottom: 1px solid #f3f4f6; display: flex; justify-content: space-between; align-items: center; }
.ai-preview-title { font-weight: bold; font-size: 14px; }
.header-right-ops { display: flex; align-items: center; gap: 20px; }
.save-draft-span { font-size: 12px; color: #9ca3af; cursor: pointer; transition: color 0.2s; }
.save-draft-span:hover { color: #3b82f6; }
.ai-close-icon { font-size: 20px; color: #9ca3af; cursor: pointer; }
.ai-preview-body { flex: 1; overflow-y: auto; padding: 25px 35px; background: #fafafa; position: relative; }

.ai-q-card-v2 { position: relative; margin-bottom: 10px; padding: 20px; border: 1px solid transparent; border-radius: 12px; background: #fff; transition: border-color 0.2s; }
.ai-q-card-v2:hover { border-color: #3b82f6; }
.ai-q-delete-btn { position: absolute; top: 15px; right: 15px; font-size: 13px; color: #ff4d4f; cursor: pointer; opacity: 0; transition: opacity 0.2s; }
.ai-q-card-v2:hover .ai-q-delete-btn { opacity: 1; }
.ai-q-header-row { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 15px; }
.ai-type-label { font-size: 11px; font-weight: bold; padding: 1px 4px; border-radius: 3px; white-space: nowrap; }
.ai-type-label.blue { color: #1890ff; background: #e6f7ff; }
.ai-type-label.green { color: #52c41a; background: #f6ffed; }
.ai-type-label.orange { color: #fa8c16; background: #fff7e6; }
.ai-opt-list-v2 { display: flex; flex-direction: column; gap: 10px; }
.ai-opt-row { padding: 8px 12px; border-radius: 8px; font-size: 13px; color: #333; display: flex; gap: 10px; }

.save-dialog-overlay { position: absolute; z-index: 1000; width: 320px; background: #fff; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.18); border: 1px solid #edf2f7; overflow: hidden; }
.dialog-header { background: #f8fafc; padding: 12px 16px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; cursor: move; }
.dialog-title { font-size: 14px; font-weight: 600; color: #1e293b; }
.drag-handle { color: #cbd5e1; letter-spacing: 2px; }
.dialog-form-v2 { padding: 20px 16px; }
.form-item-v2 { margin-bottom: 18px; }
.form-item-v2 label { display: block; font-size: 12px; font-weight: 500; color: #64748b; margin-bottom: 8px; }
.styled-input { width: 90%; border: 1.5px solid #e2e8f0; border-radius: 8px; padding: 8px 12px; font-size: 13px; outline: none; }
.styled-input:focus { border-color: #3b82f6; }
.time-picker-mini { display: flex; align-items: center; gap: 4px; }
.picker-group { display: flex; align-items: center; background: #f1f5f9; border-radius: 6px; padding: 2px 6px; }
.picker-group input { width: 32px; border: none; background: transparent; text-align: center; font-size: 14px; font-weight: 600; color: #3b82f6; outline: none; }
.picker-group span { font-size: 11px; color: #94a3b8; }
.time-sep { font-weight: bold; color: #cbd5e1; margin: 0 2px; }
.dialog-footer-v2 { padding: 12px 16px; background: #f8fafc; display: flex; justify-content: flex-end; align-items: center; gap: 10px; border-top: 1px solid #f1f5f9; }
.btn-cancel { background: #fff; border: 1px solid #e2e8f0; padding: 0 16px; height: 32px; line-height: 30px; border-radius: 6px; font-size: 13px; color: #64748b; cursor: pointer; }
.btn-confirm { background: #3b82f6; color: #fff; border: none; padding: 0 16px; height: 32px; line-height: 32px; border-radius: 6px; font-size: 13px; cursor: pointer; }

.ai-loading-box { height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; }
.spinner { width: 30px; height: 30px; border: 3px solid #f3f3f3; border-top: 3px solid #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 10px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>