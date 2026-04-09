<template>
  <div class="course-component-wrapper">
    <div v-if="showSuccessModal" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 10000;">
      <div style="background: #fff; width: 300px; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.1);">
        <div style="color: #52c41a; font-size: 50px; margin-bottom: 15px;">✔</div>
        <div style="font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px;">提交成功</div>
        <button @click="showSuccessModal = false" style="background: #28b5c1; color: white; border: none; padding: 10px 30px; border-radius: 66px; cursor: pointer; font-weight: bold;">确定</button>
      </div>
    </div>

    <div class="panel-header">
      <div class="header-left">
        <div class="title-line"></div>
        <h3 class="breadcrumb-title">
          <span class="root-node" @click="resetToLevel(1)">我的课程</span>
          <template v-if="viewLevel >= 2 && internalActiveCourse">
            <span class="sep">></span>
            <span :class="viewLevel === 3 ? 'root-node' : 'current-node'" @click="resetToLevel(2)">
              {{ internalActiveCourse.title }}
            </span>
          </template>
          <template v-if="viewLevel === 3">
            <span class="sep">></span>
            <span class="current-node">在线作业答题</span>
          </template>
        </h3>
      </div>
    </div>

    <div v-if="viewLevel === 1" class="course-grid">
      <div v-for="item in courses" :key="item.id" class="course-card" @click="enterLevel2(item)">
        <div class="course-cover" :style="{ background: `linear-gradient(135deg, ${item.color} 0%, #ffffff 150%)` }">
          <span class="cover-icon">📚</span>
        </div>
        <div class="course-main">
          <div class="title-row">
            <h4>{{ item.title }}</h4>
          </div>
          <div class="info-meta">
            <div class="meta-line">
              <span>👥 {{ item.studentCount }}人</span>
            </div>
          </div>
        </div>
        <div class="course-action"><button class="manage-btn">进入课程</button></div>
      </div>
      <div v-if="courses.length === 0" style="text-align: center; color: #999; padding: 20px;">加载中...</div>
    </div>

    <div v-else-if="viewLevel === 2" class="homework-view">
      <div class="homework-list">
        <div v-for="hw in homeworks" :key="hw.id" class="class-item-row" @click="enterLevel3(hw)">
          <div class="class-info">
            <div class="class-title">
              <span :style="{ color: hw.isExpired ? '#999' : '#52c41a', marginRight: '8px' }">●</span>
              {{ hw.title }}
              <span v-if="hw.isExpired" style="font-size:12px; color:#ff4d4f; margin-left:10px;">[已截止]</span>
            </div>
            <div class="class-sub">截止时间：{{ hw.deadline }}</div>
          </div>
          <div class="class-ops">
            <button class="op-btn" :class="{primary: !hw.isExpired}">{{ hw.isExpired ? '查看详情' : '去答题' }}</button>
          </div>
        </div>
        <div v-if="homeworks.length === 0" style="text-align: center; color: #999; padding: 20px;">暂无作业安排</div>
      </div>
    </div>

    <div v-else-if="viewLevel === 3" class="homework-detail-container">
      <div v-if="!assignmentDetail" style="text-align: center; color: #999; padding: 50px;">正在获取题目详情...</div>
      
      <div v-else class="homework-layout">
        <div class="questions-column">
          <div class="homework-section-card">
            <div v-for="(q, index) in assignmentDetail.questions" :key="'q-' + q.id" class="question-item">
              <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:20px;">
                <div class="q-title" style="margin-bottom:0; flex: 1;">
                  <span class="q-type" :class="{'multi': q.q_type === 1,'essay': q.q_type === 2}">
                    {{ q.q_type === 0 ? '单选题' : (q.q_type === 1 ? '多选题' : '简答题') }}
                  </span> 
                  {{ index + 1 }}. {{ q.content }}
                </div>
                <div style="color:#28b5c1; font-weight:bold; font-size:16px; white-space:nowrap; margin-left:20px;">
                  题分：{{ q.points || q.full_points }}分
                </div>
              </div>

              <div v-if="q.q_type === 0 || q.q_type === 1" 
                   class="options-list" 
                   :class="{'readonly-wrapper': isReadOnly}">
                <div v-for="(optText, optIdx) in q.options_data" 
                     :key="q.id + '-' + optIdx"
                     class="option-row" 
                     :class="{
                       active: checkIsSelected(q.id, optIdx),
                       /* 核心：只有在【已截止】后，才高亮绿色正确选项 */
                       'correct-opt': showDetailAnalysis && (q.correct_data || q.correct_answer || []).includes(optIdx)
                     }" 
                     @click="handleAnswerSelect(q, optIdx)">
                  <span class="option-prefix">{{ String.fromCharCode(65 + optIdx) }}.</span>
                  <span class="option-text">{{ optText }}</span>
                </div>
              </div>

              <textarea v-else class="q-textarea" 
                        :disabled="isReadOnly" 
                        placeholder="在此输入您的回答..." 
                        v-model="answers[q.id]"></textarea>

              <div v-if="showDetailAnalysis" class="analysis-box">
                <div v-if="q.score !== undefined" style="color: #28b5c1; font-weight: bold; margin-bottom: 8px;">
                  得分：{{ q.score }} / {{ q.points || q.full_points }}
                </div>
                <p v-if="q.ai_feedback"><b>AI评价：</b> {{ q.ai_feedback }}</p>
                <p><b>参考答案：</b> 
                  <span style="color:#52c41a">
                    {{ formatCorrectAnswer(q) }}
                  </span>
                </p>
                <p><b>题目解析：</b> {{ q.analysis || '暂无解析' }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="actions-column">
          <div class="sticky-side-card">
            <div class="side-info">
              <div class="side-item"><span>当前课程</span><b>{{ internalActiveCourse?.title }}</b></div>
              
              <div v-if="showDetailAnalysis" class="side-item">
                <span>最终得分</span>
                <b style="font-size:20px; color:#28b5c1">{{ assignmentDetail.total_score || '--' }}</b>
              </div>
              
              <div class="side-item">
                <span>剩余时间</span>
                <b :style="{ color: isExpired ? '#999' : '#ff4d4f' }">{{ countdownText }}</b>
              </div>
            </div>
            
            <div v-if="!isReadOnly" class="progress-info">
              答题进度: {{ completionRate }}%
              <div class="progress-bar"><div class="progress-inner" :style="{width: completionRate+'%'}"></div></div>
            </div>

            <div class="side-btns">
              <button class="back-full-btn" @click="resetToLevel(2)">返回列表</button>
              
              <button v-if="!isReadOnly" 
                      class="submit-full-btn" 
                      @click="submitAction">
                提交作业
              </button>
              
              <button v-else 
                      class="submit-full-btn disabled-btn">
                {{ isManual ? (isExpired ? '已截止' : '已提交') : '已截止' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, inject, watch } from 'vue'

const props = defineProps(['activeCourse']);
const emit = defineEmits(['manage', 'back']);

const userId = inject('sharedUserId');

const viewLevel = ref(1); 
const internalActiveCourse = ref(null);
const activeHomework = ref(null);
const assignmentDetail = ref(null); 
const courses = ref([]);
const homeworks = ref([]); 

const showSuccessModal = ref(false); 
const isManual = ref(false); 
const answers = ref({}); 
const currentTimeStamp = ref(new Date().getTime());
let timer = null;

// 1. 判断是否过期
const isExpired = computed(() => {
  if (!activeHomework.value?.deadline) return false;
  const end = new Date(activeHomework.value.deadline.replace(/-/g, '/')).getTime();
  return currentTimeStamp.value > end;
});

// 2. 只读逻辑：已手动提交成功 OR 后端返回已提交状态 OR 已截止
const isReadOnly = computed(() => 
  assignmentDetail.value?.status === 1 || 
  isManual.value || 
  isExpired.value
);

// 3. 核心：是否可以查看详情（解析/得分/AI反馈）- 仅在截止后
const showDetailAnalysis = computed(() => isExpired.value);

const completionRate = computed(() => {
  if (!assignmentDetail.value || !assignmentDetail.value.questions) return 0;
  const total = assignmentDetail.value.questions.length;
  if (total === 0) return 0;
  let completedCount = 0;
  assignmentDetail.value.questions.forEach(q => {
    const val = answers.value[q.id];
    if (Array.isArray(val)) {
      if (val.length > 0) completedCount++;
    } else {
      if (val !== "" && val !== null && val !== undefined) completedCount++;
    }
  });
  return Math.round((completedCount / total) * 100);
});

const fetchCourses = () => {
  if (!userId.value) return;
  uni.request({
    url: `http://127.0.0.1:8000/student/${userId.value}/class`,
    method: 'GET',
    success: (res) => {
      if (res.statusCode === 200) {
        const dataList = Array.isArray(res.data) ? res.data : [res.data];
        courses.value = dataList.map((item, index) => ({
          id: item.class_id || index, 
          title: item.class_name?.split('-')[0] || '未知课程',
          className: item.class_name,
          studentCount: item.total_students,
          color: index % 2 === 0 ? '#e3f2fd' : '#fce4ec'
        }));
      }
    }
  });
};

const fetchHomeworks = (classId) => {
  uni.request({
    url: `http://127.0.0.1:8000/student/${classId}/assignment`,
    method: 'GET',
    success: (res) => {
      if (res.statusCode === 200) {
        const currentTime = new Date().getTime();
        homeworks.value = res.data.map(item => {
          const endTime = new Date(item.end_at).getTime();
          return {
            id: item.id, 
            assignment_id: item.assignment_id,
            title: item.title,
            deadline: item.end_at,
            isExpired: currentTime > endTime 
          };
        });
      }
    }
  });
};

const fetchAssignmentDetail = (assignmentId) => {
  if (!userId.value) return;
  uni.request({
    url: `http://127.0.0.1:8000/student/${assignmentId}/detail?student_id=${userId.value}`,
    method: 'GET',
    success: (res) => {
      if (res.statusCode === 200 && res.data.code === 200) {
        const detailData = res.data.data;
        isManual.value = detailData.is_manual_submit === 1; 

        const rawQuestions = detailData.answers || [];
        const processedQuestions = rawQuestions.map(q => ({
          ...q,
          id: q.question_id || q.id 
        }));

        assignmentDetail.value = { ...detailData, questions: processedQuestions };

        const tempAnswers = {};
        processedQuestions.forEach(q => {
          tempAnswers[q.id] = q.student_answer !== undefined ? q.student_answer : (q.q_type === 1 ? [] : "");
        });
        answers.value = tempAnswers;
      }
    }
  });
};

const handleAnswerSelect = (question, optIdx) => {
  if (isReadOnly.value) return;
  if (question.q_type === 0) {
    answers.value[question.id] = optIdx;
  } else if (question.q_type === 1) {
    if (!Array.isArray(answers.value[question.id])) {
      answers.value[question.id] = [];
    }
    const arr = [...answers.value[question.id]];
    const pos = arr.indexOf(optIdx);
    if (pos > -1) arr.splice(pos, 1);
    else arr.push(optIdx);
    answers.value[question.id] = arr;
  }
};

const checkIsSelected = (qId, optIdx) => {
  const ans = answers.value[qId];
  if (Array.isArray(ans)) return ans.includes(optIdx);
  return ans === optIdx;
};

const formatCorrectAnswer = (q) => {
  const correct = q.correct_data || q.correct_answer;
  if (!correct || !Array.isArray(correct)) return '详见解析';
  if (q.q_type === 2) return (correct.length > 0 && correct[0] !== '已隐藏') ? correct[0] : '详见解析';
  return correct.map(idx => String.fromCharCode(65 + idx)).join(', ');
};

const countdownText = computed(() => {
  if (!activeHomework.value?.deadline) return '';
  const end = new Date(activeHomework.value.deadline.replace(/-/g, '/')).getTime();
  const diff = end - currentTimeStamp.value;
  if (diff <= 0) return '已截止';
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((diff % (1000 * 60)) / 1000);
  return `${days}天 ${String(hours).padStart(2,'0')}:${String(minutes).padStart(2,'0')}:${String(seconds).padStart(2,'0')}`;
});

const enterLevel2 = (course) => { 
  internalActiveCourse.value = course; 
  emit('manage', course); 
  viewLevel.value = 2; 
  fetchHomeworks(course.id); 
};

const enterLevel3 = (hw) => { 
  activeHomework.value = hw; 
  viewLevel.value = 3; 
  assignmentDetail.value = null; 
  isManual.value = false; 
  fetchAssignmentDetail(hw.id); 
};

const resetToLevel = (level) => {
  viewLevel.value = level;
  if (level === 1) { 
    internalActiveCourse.value = null; 
    emit('back'); 
  }
};

const submitAction = () => {
  if (!assignmentDetail.value || !activeHomework.value || !userId.value) return;
  const answersList = assignmentDetail.value.questions.map(q => ({
    question_id: q.id,
    q_type: q.q_type,
    student_answer: answers.value[q.id]
  }));
  const submitData = {
    class_assignment_id: activeHomework.value.id,
    submit_time: new Date().toISOString().replace('T', ' ').substring(0, 19),
    answers: answersList,
    student_id: userId.value
  };
  uni.showLoading({ title: '正在提交...' });
  uni.request({
    url: `http://127.0.0.1:8000/student/${activeHomework.value.id}/${userId.value}/submit`,
    method: 'POST',
    data: submitData,
    success: (res) => {
      uni.hideLoading();
      if (res.statusCode === 200) {
        showSuccessModal.value = true;
        isManual.value = true; 
        fetchAssignmentDetail(activeHomework.value.id);
      }
    }
  });
};

watch(() => userId.value, (newVal) => { if (newVal) fetchCourses(); }, { immediate: true });

onMounted(() => {
  fetchCourses();
  timer = setInterval(() => { currentTimeStamp.value = new Date().getTime(); }, 1000);
});

onUnmounted(() => { if (timer) clearInterval(timer); });
</script>

<style scoped>
.course-component-wrapper { padding: 20px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid #f0f2f5; }
.header-left { display: flex; align-items: center; }
.title-line { width: 4px; height: 20px; background-color: #28b5c1; margin-right: 12px; }
.breadcrumb-title { margin: 0; font-size: 18px; display: flex; align-items: center; color: #333; }
.root-node { cursor: pointer; transition: color 0.2s; }
.root-node:hover { color: #28b5c1; }
.sep { margin: 0 10px; color: #999; font-weight: normal; font-family: "SimSun", serif; }
.current-node { color: #28b5c1; font-weight: bold; cursor: pointer; }

/* 课程卡片 */
.course-card { display: flex; padding: 10px; background: #ffffff; border: 1px solid #f0f0f0; border-radius: 12px; align-items: center; margin-bottom: 16px; transition: all 0.3s ease; cursor: pointer; }
.course-card:hover { border-color: #28b5c1; background-color: #f9fdfd; transform: translateY(-3px); box-shadow: 0 6px 16px rgba(40, 181, 193, 0.12); }
.course-cover { width: 100px; height: 100px; border-radius: 8px; margin-right: 20px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.cover-icon { font-size: 32px; }
.course-main { flex-grow: 1; }
.title-row h4 { margin: 0; font-size: 17px; color: #333; }
.info-meta { color: #7f8c8d; font-size: 13px; }
.meta-line { display: flex; align-items: center; gap: 8px; }
.manage-btn { background: #28b5c1; color: white; border: none; padding: 6px 12px; border-radius: 4px; font-size: 12px; cursor: pointer; }

/* 作业行 */
.class-item-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 20px; border: 1px solid #f0f0f0; border-radius: 12px; margin-bottom: 16px; background: #fff; cursor: pointer; transition: all 0.3s ease; }
.class-item-row:hover { border-color: #28b5c1; background-color: #f9fdfd; transform: translateY(-3px); box-shadow: 0 6px 16px rgba(40, 181, 193, 0.12); }
.class-title { font-weight: bold; font-size: 15px; color: #333; }
.class-sub { font-size: 12px; color: #999; margin-top: 5px; }
.op-btn { padding: 6px 14px; border-radius: 4px; border: 1px solid #ddd; background: white; cursor: pointer; font-size: 12px; }
.op-btn.primary { background: #28b5c1; border-color: #28b5c1; color: white; }

/* 答题布局 */
.homework-layout { display: flex; gap: 20px; align-items: flex-start; }
.questions-column { flex: 1; }
.actions-column { width: 280px; position: sticky; top: 20px; }
.homework-section-card { background: #fff; border: 1px solid #f0f0f0; border-radius: 12px; padding: 25px; }
.question-item { margin-bottom: 40px; }
.q-title { font-weight: bold; font-size: 16px; margin-bottom: 20px; color: #333; line-height: 1.5; }
.q-type { font-size: 12px; padding: 2px 6px; border-radius: 4px; background: #e6f7ff; color: #1890ff; margin-right: 8px; }
.q-type.multi { background: #f6ffed; color: #52c41a; }
.q-type.essay { background: #fff7e6; color: #fa8c16; }

/* 选项区域核心逻辑：提交后禁用鼠标交互 */
.options-list { display: flex; flex-direction: column; gap: 12px; }
.readonly-wrapper {
  pointer-events: none; /* 禁止所有鼠标点击、悬浮事件 */
}

.option-row { display: flex; align-items: center; padding: 14px 18px; border: 1px solid #f0f0f0; border-radius: 8px; cursor: pointer; transition: all 0.2s; background: #fff; }

/* 仅在非只读模式下显示 Hover 特效 */
.options-list:not(.readonly-wrapper) .option-row:hover { 
  background: #f9fdfd; 
  border-color: #28b5c1; 
}

.option-row.active { border-color: #28b5c1; background: #f0fbff; color: #28b5c1; }
.option-prefix { font-weight: bold; margin-right: 12px; width: 25px; }
.option-text { font-size: 14px; flex: 1; }

/* 文本框 */
.q-textarea { width: 100%; min-height: 150px; padding: 15px; border: 1px solid #f0f0f0; border-radius: 8px; outline: none; transition: all 0.3s; font-family: inherit; font-size: 14px; box-sizing: border-box; }
.q-textarea:focus { border-color: #28b5c1; background: #fcfcfc; box-shadow: 0 0 0 2px rgba(40, 181, 193, 0.1); }
/* 禁用态样式 */
.q-textarea:disabled { 
  background-color: #f9f9f9; 
  color: #666; 
  cursor: not-allowed; 
  border-color: #e0e0e0;
}

/* 侧边栏 */
.sticky-side-card { background: #fff; border: 1px solid #f0f0f0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.02); }
.side-item { display: flex; justify-content: space-between; margin-bottom: 15px; font-size: 13px; color: #666; }
.progress-info { border-top: 1px solid #f5f5f5; padding-top: 15px; font-size: 13px; color: #333; }
.progress-bar { height: 8px; background: #eee; border-radius: 4px; margin-top: 10px; overflow: hidden; }
.progress-inner { height: 100%; background: #28b5c1; transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1); }

/* 按钮组 - 还原回来的单行布局 */
.side-btns { margin-top: 30px; display: flex; flex-direction: row; gap: 12px; }
.submit-full-btn { flex: 2; background: #28b5c1; color: white; border: none; padding: 10px 12px; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 13px; transition: background 0.3s; }
.back-full-btn { flex: 1; background: #fff; color: #999; border: 1px solid #eee; padding: 7px 10px; border-radius: 8px; cursor: pointer; font-size: 12px; }

.disabled-btn {
  background: #bfbfbf !important;
  color: #ffffff !important;
  cursor: not-allowed !important;
  box-shadow: none !important;
}

/* 解析框 */
.analysis-box { margin-top: 15px; background: #fcfcfc; border: 1px dashed #e0e0e0; padding: 15px; border-radius: 8px; font-size: 14px; color: #666; }
.correct-opt { border: 1.5px solid #52c41a !important; background-color: #f6ffed !important; color: #52c41a !important; }
</style>