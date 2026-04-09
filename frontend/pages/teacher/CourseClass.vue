<template>
  <div class="course-component-wrapper">
    <div class="panel-header">
      <div class="header-left">
        <div class="title-line"></div>
        <div class="header-content-column">
          <h3 class="breadcrumb-title">
            <span class="root-node" @click="resetToLevel(1)">课程管理</span>
            <template v-if="activeCourse">
              <span class="sep">></span>
              <span class="root-node" @click="resetToLevel(2)">{{ activeCourse.title }}</span>
            </template>
            <template v-if="viewLevel >= 3">
              <span class="sep">></span>
              <span class="root-node" @click="resetToLevel(3)">
                {{ subTab === 'student' ? '学生管理' : '作业管理' }}
              </span>
            </template>
            <template v-if="viewLevel === 4">
              <span class="sep">></span>
              <span class="current-node">作业情况</span>
            </template>
            <template v-if="viewLevel === 5">
              <span class="sep">></span>
              <span class="current-node">排行榜与统计</span>
            </template>
          </h3>
        </div>
      </div>

      <div v-if="viewLevel === 3" class="header-action-bar-sub">
        <template v-if="subTab === 'homework'">
          <button class="op-btn standard-btn primary" @click="isPublishModalOpen = true">发布作业</button>
        </template>
        <template v-else-if="subTab === 'student'">
          <button class="op-btn standard-btn" @click="triggerFileInput">
            📥 批量导入学生
          </button>
          <button class="op-btn standard-btn" @click="openAddStudentModal">➕ 单个添加学生</button>
        </template>
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
        </div>
        <div class="course-action">
          <button class="manage-btn">管理班级</button>
        </div>
      </div>
    </div>

    <div v-else-if="viewLevel === 2" class="class-detail-view">
      <div class="class-list">
        <div v-for="cls in classes" :key="cls.class_id" class="class-item-row">
          <div class="class-info">
            <div class="class-title">{{ cls.class_name }}</div>
          </div>
          <div class="class-ops">
            <button class="op-btn" @click="enterLevel3(cls, 'student')">学生管理</button>
            <button class="op-btn primary" @click="enterLevel3(cls, 'homework')">作业管理</button>
          </div>
        </div>
        <div v-if="classes.length === 0" style="text-align: center; color: #999; padding: 20px;">暂无班级数据</div>
      </div>
    </div>

    <div v-else-if="viewLevel === 3 && subTab === 'homework'" class="sub-management-view">
      <div class="homework-history">
        <div v-for="hw in homeworkList" :key="hw.id" class="class-item-row" style="padding: 15px;">
          <div class="class-info">
            <div class="class-title">
              <span :style="{ color: isExpired(hw.end_at) ? '#999' : '#52c41a', marginRight: '8px' }">●</span>
              <span :style="{ color: isExpired(hw.end_at) ? '#999' : '#333' }">{{ hw.title }}</span>
            </div>
            <div class="class-sub">截止时间：{{ hw.end_at }}</div>
          </div>
          <div class="class-ops">
            <button v-if="isExpired(hw.end_at)" class="op-btn report-btn" @click="openReport(hw)">查看报告</button>
            <button class="op-btn" @click="enterLevel4(hw.id)">数据大屏</button>
            <button class="op-btn" @click="enterLevel5(hw.id)">查看排行</button>
          </div>
        </div>
        <div v-if="homeworkList.length === 0" style="text-align: center; color: #999; padding: 20px;">该班级暂无已发布作业</div>
      </div>
    </div>

    <div v-else-if="viewLevel === 3 && subTab === 'student'" class="sub-management-view">
      <div class="info-banner">当前班级：{{ activeClass?.class_name }}</div>
      <div class="homework-history">
        <div v-for="stu in classStudents" :key="stu.student_no" class="class-item-row" style="padding: 15px; display: flex; justify-content: space-between; align-items: center;">
          <div class="class-info">
            <div class="class-title">{{ stu.name }}</div>
            <div class="class-sub">学号：{{ stu.student_no }} | 邮箱：{{ stu.email }}</div>
          </div>
          <div class="class-ops">
            <button class="op-btn primary" @click="openStudentAnalysis(stu)">
              AI 学习画像
            </button>
          </div>
        </div>
        <div v-if="classStudents.length === 0" style="text-align: center; color: #999; padding: 20px;">该班级暂无学生</div>
      </div>
    </div>

    <div v-else-if="viewLevel === 4" class="dashboard-wrapper">
      <div class="db-stats">
        <div class="db-stat-card">
          <div class="db-label">总提交人数</div>
          <div class="db-value">{{ dashboardData.submit_student }} <small>/ {{ dashboardData.total_student }}</small></div>
        </div>
        <div class="db-stat-card">
          <div class="db-label">平均分</div>
          <div class="db-value">{{ dashboardData.average_score }} <small>/ {{ dashboardData.max_score }}</small></div>
        </div>
        <div class="db-stat-card">
          <div class="db-label">剩余时间</div>
          <div class="db-value red" style="font-size: 20px;">
            {{ countdownText }}
            <span @click="stopAssignment" style="font-size: 12px; margin-left: 10px; color: #28b5c1; cursor: pointer; border: 1px solid #28b5c1; padding: 2px 6px; border-radius: 4px; font-weight: normal;">
              立即截止
            </span>
          </div>
        </div>
      </div>

      <div class="db-charts">
        <div class="db-chart-box">
          <div class="db-box-title">典型错误分布</div>
          <div class="pie-container">
            <template v-if="pieChartData.length > 0">
              <svg viewBox="0 0 32 32" class="pie-chart">
                <circle r="16" cx="16" cy="16" fill="none" stroke="#f5f5f5" stroke-width="32" />
                <circle v-for="(seg, idx) in pieChartData" :key="idx" r="16" cx="16" cy="16" fill="none" class="pie-segment" :stroke="seg.color" :stroke-width="32" :stroke-dasharray="`${seg.percentage + 0.5} 100`" :stroke-dashoffset="seg.offset">
                  <title>{{ seg.key }}: {{ seg.percentage }}%</title>
                </circle>
              </svg>
              <div class="donut-list">
                <p v-for="(seg, idx) in pieChartData" :key="idx">
                  <span class="dot" :style="{ backgroundColor: seg.color }"></span> 
                  <span class="legend-text">{{ seg.key }}</span>
                  <span class="percent-text">{{ seg.percentage }}%</span>
                </p>
              </div>
            </template>
            <div v-else class="no-data-placeholder">暂无提交数据，无法生成统计</div>
          </div>
        </div>
        
        <div class="db-chart-box">
            <div class="db-box-title">知识点分布统计</div>
            <div class="mock-bar-container">
              <div class="bar-line" v-for="(item, idx) in dashboardData.knowledge_distribution.slice(0, 5)" :key="idx">
                <span class="bar-txt">{{ item.key }}</span>
                <div class="bar-track">
                  <div class="bar-inner" :style="{ 
                    width: (item.count / (dashboardData.submit_student || 1) * 100) + '%',
                    backgroundColor: pieChartData[idx]?.color || '#8e71ff' 
                  }"></div>
                </div>
                <span class="bar-val" :style="{ color: pieChartData[idx]?.color || '#8e71ff' }">{{ item.count }}</span>
              </div>
            </div>
          </div>
      </div>

      <div class="db-table-box">
        <div class="db-box-title">实时提交动态</div>
        <table class="db-table">
          <thead>
            <tr><th>姓名</th><th>提交时间</th><th>状态</th><th>耗时</th><th>得分</th></tr>
          </thead>
          <tbody>
            <tr v-for="(record, idx) in dashboardData.rank" :key="idx">
              <td @click="showStudentDetail(record)" :style="{ color: !record.submit_at ? '#ff4d4f' : '#28b5c1', cursor: record.submit_at ? 'pointer' : 'default' }">
                {{ record.name }}
              </td>
              <td>{{ record.submit_at ? record.submit_at.split(' ')[1] : '--' }}</td>
              <td>
                <span class="s-dot" :class="record.submit_at ? 'g' : 'r'"></span>
                {{ record.submit_at ? '已提交' : '未提交' }}
              </td>
              <td>{{ record.duration || '--' }}</td>
              <td :class="{ 'high': record.submit_at && record.total_score >= (dashboardData.max_score * 0.9) }">
                 {{ record.submit_at ? (record.total_score ?? 0) : '--' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else-if="viewLevel === 5" class="dashboard-wrapper">
      <div class="db-table-box">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>作业成绩排行榜</span>
          <div class="stat-group">
            <span class="stat-item"><span class="s-dot g"></span>已提交: {{ dashboardData.submit_student }}</span>
            <span class="stat-item"><span class="s-dot r"></span>未提交: {{ dashboardData.total_student - dashboardData.submit_student }}</span>
            <button class="op-btn" @click="resetToLevel(3)" style="margin-left: 10px;">返回列表</button>
          </div>
        </div>
        <table class="db-table">
          <thead>
            <tr>
              <th style="width: 80px;">名次</th>
              <th>姓名</th>
              <th>提交时间</th>
              <th>得分</th>
              <th>提交状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(stu, index) in dashboardData.rank" :key="index" :class="{ 'unsubmitted-row': !stu.submit_at }">
              <td>
                <span v-if="stu.submit_at" :class="['rank-badge', index < 3 ? 'top-' + (index + 1) : '']">
                  {{ index + 1 }}
                </span>
                <span v-else class="rank-badge">-</span>
              </td>
              <td>{{ stu.name }}</td>
              <td>{{ stu.submit_at || '--' }}</td>
              <td :class="stu.submit_at ? 'high' : 'pending'">{{ stu.submit_at ? stu.total_score : '--' }}</td>
              <td>
                <span v-if="stu.submit_at">
                  <span class="s-dot g"></span> 已提交
                </span>
                <span v-else>
                  <span class="s-dot r"></span> <span style="color: #ff4d4f;">未提交</span>
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Transition name="fade">
      <div v-if="isPublishModalOpen" class="modal-overlay" @click.self="isPublishModalOpen = false">
        <div class="modal-content draft-modal">
          <div class="modal-header">
            <div class="modal-header-left">
              <div class="title-line"></div>
              <span class="modal-title-text">作业草稿</span>
            </div>
            <button class="save-exit-btn" :disabled="selectedDraftId === null" @click="handlePublish">发布</button>
          </div>
          <div class="modal-body">
            <div v-for="draft in draftHomeworks" :key="draft.id" class="draft-item" :class="{ 'is-selected': selectedDraftId === draft.id }" @click="selectedDraftId = draft.id">
              <div class="draft-info">
                <div class="draft-name">{{ draft.title }} <span class="draft-tag">草稿</span></div>
                <div class="draft-meta">题目数量：{{ draft.count }} 道 | 最后编辑：{{ draft.time }}</div>
              </div>
            </div>
            <div v-if="draftHomeworks.length === 0" style="text-align: center; color: #999; padding: 20px;">暂无草稿数据</div>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="fade">
      <div v-if="reportVisible" class="modal-overlay" @click.self="reportVisible = false">
        <div class="report-pop-card">
          <div class="pop-close" @click="reportVisible = false">×</div>
          <div class="report-content-inner">
            <div class="report-header-line">
              <div class="v-line"></div>
              <span class="report-title-text">LLM 教学调整建议</span>
            </div>
            <div v-if="reportLoading || !reportContent" class="report-loading-status">
              <div class="loading-spinner"></div>
              <p>AI 正在深度分析班级薄弱点，请稍候...</p>
            </div>
            <div v-else class="report-main-body">
              <p class="report-desc-text" style="white-space: pre-wrap;">{{ reportContent }}</p>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="fade">
      <div v-if="isStudentDetailVisible" class="modal-overlay" @click.self="isStudentDetailVisible = false">
        <div class="modal-content" style="width: 80%; max-width: 900px; height: 80vh; background: #fff; border-radius: 12px; display: flex; flex-direction: column; overflow: hidden;">
          <div class="modal-header" style="display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; border-bottom: 1px solid #eee;">
            <div class="modal-header-left" style="display: flex; align-items: center;">
              <div class="title-line" style="width: 4px; height: 18px; background: #28b5c1; margin-right: 10px;"></div>
              <span class="modal-title-text" style="font-size: 16px; font-weight: bold; color: #333;">
                {{ currentStudentDetail?.student_name || '学生' }} 的作业详情
              </span>
            </div>
            <div style="display: flex; align-items: center; gap: 20px;">
              <div v-if="currentStudentDetail" style="font-size: 14px; color: #666;">
                作业得分: <b style="color: #28b5c1; font-size: 20px; margin-left: 5px;">{{ currentStudentDetail.total_score ?? '--' }}</b>
              </div>
              <button class="op-btn" @click="isStudentDetailVisible = false">关闭</button>
            </div>
          </div>
          <div style="flex: 1; overflow-y: auto; padding: 20px; background: #f8f9fa;">
            <div v-if="loadingDetail" style="text-align: center; padding: 40px;">加载详情中...</div>
            <div v-else-if="currentStudentDetail?.answers" v-for="(q, index) in currentStudentDetail.answers" :key="index" style="background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #eee;">
              <div style="margin-bottom: 10px;">
                <span style="background: #e6f7ff; color: #1890ff; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-right: 8px;">
                  {{ q.q_type === 0 ? '单选题' : (q.q_type === 1 ? '多选题' : '填空题') }}
                </span>
                <b>{{ index + 1 }}. {{ q.content }}</b>
              </div>
              <div v-if="q.options_data" style="margin-left: 20px;">
                <div v-for="(opt, optIdx) in q.options_data" :key="optIdx" :style="{ color: q.correct_data.includes(optIdx) ? '#52c41a' : '#666', padding: '4px 0' }">
                  {{ String.fromCharCode(65 + optIdx) }}. {{ opt }}
                </div>
              </div>
              <div style="margin-top: 15px; padding-top: 15px; border-top: 1px dashed #eee; display: flex; gap: 40px;">
                <div>
                  <span style="color: #999;">学生回答：</span>
                  <span :style="{ color: q.score > 0 ? '#52c41a' : '#ff4d4f', fontWeight: 'bold' }">
                    {{ Array.isArray(q.student_answer) ? q.student_answer.map(v => String.fromCharCode(65 + parseInt(v))).join(', ') : (q.q_type <= 1 ? String.fromCharCode(65 + parseInt(q.student_answer)) : q.student_answer) }}
                  </span>
                </div>
                <div>
                  <span style="color: #999;">得分：</span>
                  <span>{{ q.score }} / {{ q.points }}</span>
                </div>
              </div>
              <div v-if="q.ai_feedback" style="margin-top: 10px; background: #f0fbfc; padding: 10px; border-radius: 4px; font-size: 13px; color: #444;">
                <span style="color: #28b5c1; font-weight: bold;">AI 解析：</span>{{ q.ai_feedback }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
	<Transition name="fade">
	  <div v-if="isAddStudentModalOpen" class="modal-overlay" @click.self="isAddStudentModalOpen = false">
	    
	    <div class="modal-content centered-modal">
	      <div class="modal-header">
	        <span class="modal-title-text">添加单个学生</span>
	      </div>
	      <div class="modal-body">
	        <div class="form-row">
	          <label class="form-label">学生姓名</label>
	          <input v-model="newStudent.name" type="text" placeholder="请输入姓名" class="row-input" />
	        </div>
	        
	        <div class="form-row">
	          <label class="form-label">学生邮箱</label>
	          <input v-model="newStudent.email" type="email" placeholder="请输入邮箱" class="row-input" />
	        </div>
	        
	        <div class="modal-footer">
	          <button class="confirm-btn" @click="handleAddStudent">确 定</button>
	        </div>
	      </div>
	    </div>
	    
	  </div>
	</Transition>

    <div class="course-component-wrapper">
        <Transition name="fade">
          <div v-if="isStudentAnalysisVisible" class="modal-overlay" @click.self="isStudentAnalysisVisible = false">
            <div class="report-pop-card-v2">
              <div class="pop-close" @click="isStudentAnalysisVisible = false">×</div>
              
              <div class="analysis-container-inner">
                <header class="profile-header-new">
                  <div class="info-card-new">
                    <h2 style="margin-top:0;">{{ currentStuName }}</h2>
                    <p><strong>学号：</strong>{{ studentAnalysisData.id || '8208220317' }}</p>
                    <p><strong>班级：</strong>{{ activeClass?.class_name || '计算机科学与技术2206' }}</p>
                    <p><strong>综合评分：</strong><span class="score-highlight">{{ studentAnalysisData.accuracy }}</span></p>
                  </div>
                  <div class="ai-report-card-new">
                    <span class="ai-badge-new">✨ LLM 智能分析</span>
                    <h3>个性化学习诊断报告</h3>
                    <p class="report-text">
                      "根据近期的课堂互动表现，该生在逻辑思维维度表现极其出色，但在知识点<b>【{{ studentAnalysisData.weakestPoint }}】</b>的实际应用上存在明显波动。建议在后续练习中增加该模块的深度，系统已为您自动推送相关强化练习。"
                    </p>
                  </div>
                </header>
    
                <div class="chart-grid-new">
                  <div class="chart-container-new">
                    <h4 style="margin-top:0;">能力多维画像</h4>
                    <div id="radarChart" style="width: 100%; height: 300px;"></div>
                  </div>
                  <div class="chart-container-new">
                    <h4 style="margin-top:0;">学习成长曲线</h4>
                    <div id="lineChart" style="width: 100%; height: 300px;"></div>
                  </div>
                </div>
    
                <div class="details-card-new">
                  <h4 style="margin-top:0;">知识点掌握明细 (AI 深度识别)</h4>
                  <table class="analysis-table-new">
                    <thead>
                      <tr>
                        <th>知识点名称</th>
                        <th>掌握程度</th>
                        <th>错误频率</th>
                        <th>AI 改进建议</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="item in studentAnalysisData.knowledgePoints" :key="item.name">
                        <td>{{ item.name }}</td>
                        <td>
                          <div class="progress-bar-bg">
                            <div class="progress-bar-fill" :style="{ width: item.progress + '%' }"></div>
                          </div>
                        </td>
                        <td><span class="error-tag-new">{{ item.errorRate }}%</span></td>
                        <td class="suggestion-text">{{ item.suggestion }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue' 
import * as echarts from 'echarts' // 引入 echarts

const isStudentAnalysisVisible = ref(false);
const currentStuName = ref('');
const studentAnalysisData = ref({});

// 打开 AI 学习画像
const openStudentAnalysis = (stu) => {
  currentStuName.value = stu.name;
  isStudentAnalysisVisible.value = true;
  
  // 模拟 AI 分析数据请求 [cite: 467, 468]
  setTimeout(async () => {
    studentAnalysisData.value = {
      id: stu.student_no || '8208220317',
      accuracy: 88.5,
      weakestPoint: '数据链路层协议',
      knowledgePoints: [
        { name: '计算机网络体系结构', progress: 95, errorRate: 5, suggestion: '基础扎实，可挑战更深层的协议分析。' },
        { name: '物理层编码', progress: 80, errorRate: 15, suggestion: '注意区分不同编码方式的效率差异。' },
        { name: '数据链路层协议', progress: 45, errorRate: 42, suggestion: '建议重新观看有关滑动窗口机制的讲解视频。' }
      ]
    };
    
    await nextTick();
    renderCharts();
  }, 300);
};

// 渲染图表 [cite: 469, 472]
const renderCharts = () => {
  const radarChartDom = document.getElementById('radarChart');
  const lineChartDom = document.getElementById('lineChart');
  
  if (!radarChartDom || !lineChartDom) return;

  const radarChart = echarts.init(radarChartDom);
  radarChart.setOption({
    radar: {
      indicator: [
        { name: '基础理论', max: 100 }, { name: '代码实现', max: 100 },
        { name: '互动参与', max: 100 }, { name: '解题速度', max: 100 },
        { name: '创新思维', max: 100 }
      ]
    },
    series: [{
      type: 'radar',
      data: [{ value: [90, 85, 95, 70, 88], name: '学生画像' }],
      itemStyle: { color: '#4facfe' },
      areaStyle: { opacity: 0.3 }
    }]
  });

  const lineChart = echarts.init(lineChartDom);
    lineChart.setOption({
      // 1. 配置滚动特效：紧贴 X 轴，支持直接拉动
      dataZoom: [
        {
          type: 'slider',      // 滑块条
          show: true,
          xAxisIndex: [0],
          height: 20,          // 调薄滑块，使其更精致
          bottom: 5,           // 紧贴底部，靠近轴标签
          start: 0,
          end: 70,             // 默认显示前 70% 的数据，确保文字不会太挤
          handleIcon: 'path://M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
          handleSize: '80%',
          showDetail: false,   // 拖动时不显示百分比提示，保持界面清爽
          brushSelect: false,  // 关闭刷选，只保留滑动
          fillerColor: 'rgba(118, 75, 162, 0.2)', // 使用你线条颜色的透明色
          borderColor: 'transparent',             // 隐藏边框
          backgroundColor: 'rgba(0,0,0,0.03)'     // 极淡的底色
        },
        {
          type: 'inside',      // 允许在图表主体区域直接用手指/鼠标拉动
          xAxisIndex: [0],
          zoomOnMouseWheel: false, // 建议关闭滚轮缩放，防止误触
          moveOnMouseMove: true   // 允许滑动
        }
      ],
      // 2. 调整布局，为倾斜文字留出精确空间
      grid: {
        top: '10%',
        left: '5%',
        right: '5%',
        bottom: '100px', // 因为文字斜着且有滑动条，这里需要加大
        containLabel: true
      },
      xAxis: { 
        type: 'category', 
        data: ['作业1：大语言模型分析', '作业2：后端API规范设计', '作业3：数据库异步构建', '作业4：前端组件封装', '作业5：系统集成测试', '作业6', '作业7'],
        axisLabel: {
          interval: 0,
          rotate: 40,   // 倾斜 40 度
          margin: 15,   // 文字距离轴线的距离
          color: '#666',
          fontSize: 11,
          formatter: function (value) {
            return value.length > 8 ? value.slice(0, 8) + '...' : value;
          }
        },
        axisTick: { show: false }, // 隐藏刻度线，视觉更简洁
        axisLine: { lineStyle: { color: '#ddd' } }
      },
      yAxis: { 
        type: 'value',
        splitLine: { lineStyle: { type: 'dashed' } } // 背景线设为虚线
      },
      series: [{
        data: [78, 82, 85, 81, 88, 92, 88],
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { color: '#764ba2', width: 3 },
        itemStyle: { color: '#764ba2', borderColor: '#fff', borderWidth: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(118, 75, 162, 0.3)' },
            { offset: 1, color: 'rgba(118, 75, 162, 0)' }
          ])
        }
      }]
    });
};

// 新增：图表初始化函数
const initAnalysisCharts = (chartData) => {
  // 注意：需要确保你的环境中引入了 echarts，或者通过 window.echarts 调用
  const radarDom = document.getElementById('radarChart');
  const lineDom = document.getElementById('lineChart');
  if(!radarDom || !lineDom) return;

  const radarChart = echarts.init(radarDom);
  const lineChart = echarts.init(lineDom);

  radarChart.setOption({
    radar: {
      indicator: [
        { name: '基础理论', max: 100 }, { name: '逻辑表达', max: 100 },
        { name: '互动参与', max: 100 }, { name: '解题速度', max: 100 }, { name: '综合潜能', max: 100 }
      ],
      shape: 'circle'
    },
    series: [{
      type: 'radar',
      data: [{ value: chartData?.radar_values || [80, 70, 90, 60, 85], name: '表现' }],
      itemStyle: { color: '#4facfe' },
      areaStyle: { opacity: 0.3 }
    }]
  });

  lineChart.setOption({
    xAxis: { type: 'category', data: ['1次', '2次', '3次', '4次', '5次'] },
    yAxis: { type: 'value' },
    series: [{
      data: chartData?.line_values || [70, 75, 80, 78, 85],
      type: 'line', smooth: true,
      lineStyle: { color: '#764ba2' },
      areaStyle: { color: 'rgba(118, 75, 162, 0.1)' }
    }]
  });
};


let refreshTimer = null; 
const props = defineProps(['activeCourse']);
const emit = defineEmits(['manage', 'back']);

const viewLevel = ref(1); 
const subTab = ref(''); 
const activeClass = ref(null); 
const currentTime = ref(new Date()); 
const activeAssignmentId = ref(null);

// --- 新增：学生作业详情弹窗状态 ---
const isStudentDetailVisible = ref(false);
const currentStudentDetail = ref(null);
const loadingDetail = ref(false);

// 点击列表某一行时的处理函数
const showStudentDetail = (record) => {
  // 1. 未提交拦截
  if (!record.submit_at) {
      uni.showToast({ title: '该学生尚未提交作业', icon: 'none' });
      return;
    }
  
    isStudentDetailVisible.value = true;
    loadingDetail.value = true;
    
    // 记录下从列表页带来的分数，防止被后续接口覆盖
    const safeScore = record.total_score;
    const safeName = record.name;
  
    currentStudentDetail.value = {
      student_name: safeName,
      total_score: safeScore,
      answers: []
    };

  // 4. 异步获取答题详情
  uni.request({
    url: `http://127.0.0.1:8000/student/${activeAssignmentId.value}/detail`,
        data: { student_id: record.student_id },
        success: (res) => {
          if (res.data?.code === 200) {
            // 修正合并逻辑：优先保留列表页的分数
            currentStudentDetail.value = {
              ...res.data.data,       // 后端详情放在前面
              student_name: safeName, // 强制覆盖为列表页的姓名
              total_score: safeScore  // 强制覆盖为列表页的分数
            };
          }
        },
    fail: () => {
      uni.showToast({ title: '获取详情失败', icon: 'none' });
    },
    complete: () => {
      loadingDetail.value = false;
    }
  });
};


const reportVisible = ref(false);
const reportLoading = ref(false);
const reportContent = ref(""); // 用于存储从后端拿到的 report 文本

const openReport = (hw) => {
  reportVisible.value = true;
  reportLoading.value = true;
  reportContent.value = ""; // 重置内容

  // 向后端接口发送请求
  uni.request({
    url: `http://127.0.0.1:8000/teacher/${hw.id}/report`, // 使用动态 assignment_id
    method: 'GET',
    success: (res) => {
      if (res.data && res.data.code === 200) {
        const data = res.data.data;
        // 判断 report 是否为空值（对应“正在生成”状态）
        if (data && data.report && data.report.trim() !== "") {
          reportContent.value = data.report;
          reportLoading.value = false;
        } else {
          // 拿到空值或 report 为空，说明 LLM 还在计算中
          reportContent.value = ""; 
          reportLoading.value = true; 
        }
      } else {
        uni.showToast({ title: '获取报告失败', icon: 'none' });
        reportVisible.value = false;
      }
    },
    fail: () => {
      uni.showToast({ title: '网络请求错误', icon: 'none' });
      reportVisible.value = false;
    }
  });
};

// --- 数据大屏状态管理 ---
const dashboardData = ref({
  total_student: 0,
  submit_student: 0,
  max_score: 0,
  average_score: 0,
  create_at: "",
  end_at: "",
  knowledge_distribution: [],
  rank: []
});

const targetDeadline = ref(new Date());

const fetchAssignmentDetail = (id) => {
  if (!id) return;
  uni.request({
    url: `http://127.0.0.1:8000/teacher/${id}/detail_show`,
    method: 'GET',
    success: (res) => {
      if (res.data && res.data.code === 200) {
        dashboardData.value = res.data.data;
        if (res.data.data.end_at) {
          const deadline = new Date(res.data.data.end_at.replace(/-/g, '/'));
          targetDeadline.value = deadline;
          
          // 如果获取到的最新数据表明已截止，立即关掉定时器
          if (new Date() > deadline) {
            stopLiveUpdate();
          }
        }
      }
    }
  });
};

const startLiveUpdate = (id) => {
  stopLiveUpdate(); 
  
  // 先获取一次详情
  uni.request({
    url: `http://127.0.0.1:8000/teacher/${id}/detail_show`,
    method: 'GET',
    success: (res) => {
      if (res.data && res.data.code === 200) {
        dashboardData.value = res.data.data;
        const endTime = res.data.data.end_at;
        
        // 核心改动：判断是否已截止
        if (endTime) {
          const deadline = new Date(endTime.replace(/-/g, '/'));
          targetDeadline.value = deadline;
          
          if (new Date() > deadline) {
            console.log("作业已截止，跳过轮询");
            return; // 直接返回，不启动定时器
          }
        }

        // 未截止则启动轮询
        refreshTimer = setInterval(() => {
          if (viewLevel.value === 4 || viewLevel.value === 5) {
            // 在轮询内部也增加判断，防止运行中到期
            if (new Date() > targetDeadline.value) {
              stopLiveUpdate();
              console.log("轮询过程中作业到期，已停止");
              return;
            }
            fetchAssignmentDetail(id);
          }
        }, 5000); 
      }
    }
  });
};

const stopLiveUpdate = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
};

const countdownText = computed(() => {
  const diff = targetDeadline.value - currentTime.value;
  if (diff <= 0) return '已截止';
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
  const minutes = Math.floor((diff / (1000 * 60)) % 60);
  const seconds = Math.floor((diff / 1000) % 60);
  const format = (num) => String(num).padStart(2, '0');
  return `${days}天 ${format(hours)}:${format(minutes)}:${format(seconds)}`;
});

const stopAssignment = (e) => {
  e.stopPropagation(); 
  if(confirm('确定要立即截止该作业吗？')){
    const assignmentId = activeAssignmentId.value;
    uni.request({
      url: `http://127.0.0.1:8000/teacher/${assignmentId}/end`,
      method: 'POST',
      success: (res) => {
        if (res.data && res.data.code === 200) {
          targetDeadline.value = new Date();
          uni.showToast({ title: '已成功截止', icon: 'success' });
          fetchAssignmentDetail(assignmentId);
        }
      }
    });
  }
};

let timer = null;
onMounted(() => {
  stopLiveUpdate();
  timer = setInterval(() => {
    currentTime.value = new Date();
  }, 1000);
  fetchCourseData(); 
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});

const isPublishModalOpen = ref(false);
const selectedDraftId = ref(null);
const draftHomeworks = ref([]); 
const homeworkList = ref([]); 
const courses = ref([]);
const classes = ref([]); 
const classStudents = ref([]);

const isExpired = (deadlineStr) => {
  if (!deadlineStr) return false;
  const deadline = new Date(deadlineStr.replace(/-/g, '/')); 
  return currentTime.value > deadline;
};

const fetchClassAssignments = () => {
  const userId = 2;
  const courseId = props.activeCourse?.id;
  const classId = activeClass.value?.class_id;
  if (!courseId || !classId) return;
  uni.request({
    url: `http://127.0.0.1:8000/teacher/${userId}/${courseId}/${classId}/assignment`,
    method: 'GET',
    success: (res) => {
      if (res.data && res.data.code === 200) {
        homeworkList.value = res.data.data;
      }
    }
  });
};

const fetchDraftAssignments = () => {
  const userId = 2; 
  uni.request({
    url: `http://127.0.0.1:8000/teacher/${userId}/assignments`,
    method: 'GET',
    success: (res) => {
      if (res.data && res.data.code === 200) {
        draftHomeworks.value = res.data.data.map(item => ({
          id: item.assignment_id,
          title: item.title,
          count: item.q_count,
          time: item.created_at 
        }));
      }
    }
  });
};

const handlePublish = () => {
  if (!selectedDraftId.value) return;
  const userId = 2;
  const courseId = props.activeCourse?.id;
  const classId = activeClass.value?.class_id;
  uni.request({
    url: `http://127.0.0.1:8000/teacher/${userId}/${courseId}/${classId}/${selectedDraftId.value}/publish`,
    method: 'POST',
    success: (res) => {
      if (res.data && res.data.code === 200) {
        uni.showToast({ title: '作业发布成功', icon: 'success' });
        isPublishModalOpen.value = false;
        fetchClassAssignments(); 
      }
    }
  });
};

const fetchCourseData = () => {
  uni.request({
    url: `http://127.0.0.1:8000/teacher/2/course`,
    method: 'GET',
    success: (res) => {
      if (res.data && res.data.code === 200) {
        courses.value = res.data.data.map((item, index) => ({
          id: item.course_id,
          title: item.course_name,
          color: index % 2 === 0 ? '#e3f2fd' : '#fce4ec'
        }));
      }
    }
  });
};

const fetchClasses = (courseId) => {
  uni.request({
    url: `http://127.0.0.1:8000/teacher/2/${courseId}/class`,
    method: 'GET',
    success: (res) => {
      if (res.data && res.data.code === 200) {
        classes.value = res.data.data;
      }
    }
  });
};

const fetchClassStudents = (classObj) => {
  uni.request({
    url: `http://127.0.0.1:8000/teacher/2/${props.activeCourse?.id}/${classObj.class_id}/student`,
    method: 'GET',
    success: (res) => {
      if (res.data && res.data.code === 200) {
        classStudents.value = res.data.data;
      }
    }
  });
};

const pieChartData = computed(() => {
  const list = dashboardData.value.knowledge_distribution || [];
  const top5 = list.slice(0, 5);
  const itemsTotal = top5.reduce((sum, item) => sum + item.count, 0);
  if (itemsTotal === 0) return [];
  let cumulativePercent = 0;
  const colors = ['#5370C6', '#EE6566', '#FAC858', '#91CD74', '#A74695'];
  return top5.map((item, index) => {
    const percent = (item.count / itemsTotal) * 100;
    const currentOffset = -cumulativePercent;
    cumulativePercent += percent;
    return {
      key: item.key,
      percentage: Math.round(percent),
      offset: currentOffset, 
      color: colors[index]
    };
  });
});

const enterLevel2 = (course) => { 
  emit('manage', course); 
  viewLevel.value = 2; 
  fetchClasses(course.id); 
};

const enterLevel3 = (cls, tab) => { 
  subTab.value = tab; 
  viewLevel.value = 3; 
  activeClass.value = cls; 
  tab === 'student' ? fetchClassStudents(cls) : fetchClassAssignments(); 
};

const enterLevel4 = (id) => {
  activeAssignmentId.value = id; 
  viewLevel.value = 4;
  startLiveUpdate(id); 
};

const enterLevel5 = (id) => {
  activeAssignmentId.value = id;
  viewLevel.value = 5;
  startLiveUpdate(id); 
};

const resetToLevel = (level) => {
  viewLevel.value = level;
  if (level < 4) stopLiveUpdate(); 
  if (level === 1) { subTab.value = ''; emit('back'); }
  else if (level === 2) { subTab.value = ''; }
};

watch(isPublishModalOpen, (val) => val && fetchDraftAssignments());
watch(() => props.activeCourse, (newVal) => { if (!newVal) { viewLevel.value = 1; subTab.value = ''; } });
watch(() => props.showModal, (newVal) => {
  if (newVal) {
    // 必须等待弹窗 DOM 渲染完成后再初始化图表
    nextTick(() => {
      initCharts();
    });
  }
});

const initChart = () => {
  if (chartContainer.value) {
    const myChart = echarts.init(chartContainer.value);
    const option = {
      // 保持你原有的标题配置
      title: {
        text: '学习成长曲线',
        left: 'left',
        textStyle: {
          fontSize: 18,
          fontWeight: 'bold'
        }
      },
      // 1. 新增：添加数据缩放组件，实现左右拖动
      dataZoom: [
        {
          type: 'slider', // 滑块条
          show: true,
          xAxisIndex: [0],
          start: 0,
          end: 100,      // 默认显示全部，作业多了可以调小，比如 50
          bottom: 10     // 距离容器底部的距离
        },
        {
          type: 'inside', // 支持鼠标滚轮和手势拖动
          xAxisIndex: [0],
          start: 0,
          end: 100
        }
      ],
      // 调整布局，防止底部标题被遮挡
      grid: {
        left: '3%',
        right: '4%',
        bottom: '80px', // 留出足够空间给倾斜的文字和滑动条
        containLabel: true
      },
      xAxis: {
        type: 'category',
        // 这里替换为你动态获取的作业名称数组
        data: ['作业1：基于大语言模型的系统分析', '作业2：后端API接口规范化设计', '作业3：数据库异步模型构建', '更多作业标题...'],
        // 2. 修改：配置标签倾斜
        axisLabel: {
          interval: 0,    // 强制显示所有标签
          rotate: 35,     // 倾斜角度
          formatter: function (value) {
            // 长标题超过 10 个字加省略号
            return value.length > 10 ? value.slice(0, 10) + '...' : value;
          }
        },
        axisTick: { alignWithLabel: true }
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100
      },
      series: [
        {
          // 这里的数据建议与 data 长度保持一致
          data: [78, 82, 85, 81], 
          type: 'line',
          smooth: true,   // 平滑曲线
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: { color: '#5470c6', width: 3 },
          itemStyle: { color: '#5470c6', borderColor: '#fff', borderWidth: 2 },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(84, 112, 198, 0.3)' },
              { offset: 1, color: 'rgba(84, 112, 198, 0)' }
            ])
          }
        }
      ]
    };
    myChart.setOption(option);
  }
};
const fileInput = ref(null);
/**
 * 触发文件选择（动态创建方式，无需 HTML 标签）
 */
const triggerFileInput = () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.xlsx, .xls';
  
  input.onchange = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // 前端后缀校验
    const fileName = file.name;
    const ext = fileName.split('.').pop().toLowerCase();
    
    if (ext !== 'xlsx' && ext !== 'xls') {
      uni.showToast({ title: '仅支持 Excel 文件 (.xlsx/.xls)', icon: 'none' });
      return;
    }

    // 执行上传
    uploadExcelFile(file);
  };

  input.click();
};

/**
 * 使用 uni.uploadFile 上传
 */
const uploadExcelFile = (file) => {
  uni.showLoading({ title: '正在解析上传...' });

  uni.uploadFile({
    url: 'http://127.0.0.1:8000/teacher/student/batch_import', 
    file: file, 
    name: 'file', // 确保你的后端代码里参数名也叫 file
    formData: {
      'class_id': activeClass.value?.class_id || ''
    },
    success: (uploadRes) => {
      // 这里的 uploadRes.data 是字符串！
      try {
        const res = JSON.parse(uploadRes.data);
        if (res.code === 200) {
          uni.showToast({ title: '导入成功', icon: 'success' });
          if (activeClass.value) fetchClassStudents(activeClass.value);
        } else {
          // 如果这里显示格式错误，说明是后端判断后的结果
          uni.showToast({ title: res.msg || '后端识别格式错误', icon: 'none' });
        }
      } catch (e) {
        uni.showToast({ title: '服务器解析失败', icon: 'none' });
      }
    },
    fail: () => {
      uni.showToast({ title: '网络请求失败', icon: 'none' });
    },
    complete: () => {
      uni.hideLoading();
    }
  });
};

// 控制弹窗显隐
const isAddStudentModalOpen = ref(false);
// 表单数据
const newStudent = ref({
  name: '',
  email: ''
});

// 点击按钮打开弹窗
const openAddStudentModal = () => {
  newStudent.value = { name: '', email: '' }; // 清空数据
  isAddStudentModalOpen.value = true;         // 改变状态
  console.log("弹窗状态：", isAddStudentModalOpen.value); // 调试用
};

// 提交逻辑
const handleAddStudent = () => {
  if (!newStudent.value.name || !newStudent.value.email) {
    uni.showToast({ title: '请填写完整信息', icon: 'none' });
    return;
  }
  
  uni.request({
    url: `http://127.0.0.1:8000/teacher/add_student`, // 请根据实际接口修改
    method: 'POST',
    data: {
      ...newStudent.value,
      class_id: activeClass.value?.class_id
    },
    success: (res) => {
      if (res.data?.code === 200) {
        uni.showToast({ title: '添加成功', icon: 'success' });
        isAddStudentModalOpen.value = false;
        fetchClassStudents(activeClass.value); // 刷新列表 [cite: 78]
      }
    }
  });
};
</script>

<style scoped>
/* 弹窗容器居中 */
.centered-modal {
  width: 400px;
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  /* 移除原有的 margin: 100px auto 等定位属性，靠父级 flex 控制即可 */
}

/* 标签与输入框单行排列 */
.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 12px;
}

.form-label {
  width: 70px; /* 固定宽度保证对齐 */
  font-size: 14px;
  color: #333;
  text-align: right;
  font-weight: bold;
}

.row-input {
  flex: 1;
  height: 38px;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 0 12px;
  font-size: 14px;
  outline: none;
}

.row-input:focus {
  border-color: #28b5c1;
}

/* 底部按钮 */
.modal-footer {
  margin-top: 30px;
  text-align: center;
}

.confirm-btn {
  width: 100%;
  height: 42px;
  background: #28b5c1;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  font-weight: bold;
  cursor: pointer;
  transition: opacity 0.2s;
}

.confirm-btn:active {
  opacity: 0.8;
}

/* 弹窗遮罩：磨砂透明效果 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  
  /* 关键：使用 Flex 布局实现居中 */
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center;     /* 竖直居中 */
  
  z-index: 999;
}

/* 2. 弹窗主容器：确保高度不会被切断 */
.report-pop-card-v2 {
  width: 95%;
  max-width: 1100px;
  background: #ffffff;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  
  /* 位置控制：改为 40px，解决“上方空隙太大”的问题 */
  margin-top: 40px; 
  margin-bottom: 40px;
  
  /* 滚动控制 */
  max-height: calc(100vh - 80px); /* 动态计算高度，确保不超出屏幕 */
  overflow-y: auto;
  
  /* --- 彻底隐藏滚动条样式 --- */
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;     /* Firefox */
}

/* 兼容 Chrome/Edge/Safari 的隐藏逻辑 */
.report-pop-card-v2::-webkit-scrollbar {
  display: none; 
}

.report-pop-card-v2::-webkit-scrollbar-thumb {
  background-color: transparent; /* 默认透明 */
  border-radius: 10px;
}

/* 只有当鼠标悬停在弹窗上时，才显示滚动条滑块 */
.report-pop-card-v2:hover::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.15); 
}

/* Firefox 悬停显示 */
.report-pop-card-v2:hover {
  scrollbar-color: rgba(0, 0, 0, 0.15) transparent;
}

.pop-close {
  position: absolute;
  top: 15px; right: 20px;
  font-size: 24px; color: #999;
  cursor: pointer; z-index: 10;
}

/* 顶部信息栏：紧凑布局 */
.profile-header-new {
  display: grid;
  grid-template-columns: 320px 1fr;
  border-bottom: 1px solid #f0f0f0; /* 使用细线分隔，不留缝隙 */
}

.info-card-new {
  padding: 30px;
  border-right: 1px solid #f0f0f0;
}

.info-card-new h2 {
  font-size: 24px; /* 增大姓名比例 */
  margin: 0 0 15px 0;
  color: #1a1a1a;
}

.info-card-new p {
  font-size: 14px;
  color: #666;
  margin: 8px 0;
}

.score-highlight {
  color: #4facfe;
  font-size: 32px; /* 突出综合得分 */
  font-weight: 700;
  margin-left: 10px;
}

/* AI 报告区域：渐变背景保持美感 */
.ai-report-card-new {
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.ai-badge-new {
  display: inline-block;
  width: fit-content;
  background: rgba(255,255,255,0.15);
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 12px;
  margin-bottom: 12px;
}

.ai-report-card-new h3 {
  font-size: 20px;
  margin: 0 0 10px 0;
}

.report-text {
  font-size: 15px;
  line-height: 1.8;
  opacity: 0.95;
  margin: 0;
}

/* 图表区域：左右等分，无缝隙 */
.chart-grid-new {
  display: grid;
  grid-template-columns: 1fr 1fr;
  width: 100%;
  background: #fff;
}
.chart-container {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  height: 350px; /* 必须有固定高度，或者 calc 高度 */
  min-height: 350px; 
  width: 100%;
}

#radarChart, #lineChart {
  width: 100% !important;
  height: 300px !important;
  min-height: 300px !important;
  display: block !important;
}

.chart-container-new {
  padding: 20px;
  height: 350px !important;  /* 使用 !important 防止被后面样式覆盖 */
  min-height: 350px !important;
  width: 100%;
  box-sizing: border-box;
}

.chart-container-new:first-child {
  border-right: 1px solid #f0f0f0;
}

.chart-container-new h4 {
  font-size: 16px;
  color: #333;
  margin-bottom: 20px;
  border-left: 4px solid #4facfe;
  padding-left: 10px;
}

/* 底部明细：表格化布局 */
.details-card-new {
  padding: 25px;
}

.details-card-new h4 {
  font-size: 16px;
  margin-bottom: 15px;
  color: #333;
}

.analysis-table-new {
  width: 100%;
  border-collapse: collapse;
}

.analysis-table-new th {
  background: #fafafa;
  color: #888;
  font-weight: 500;
  padding: 12px 15px;
  text-align: left;
  font-size: 13px;
}

.analysis-table-new td {
  padding: 15px;
  border-bottom: 1px solid #f5f5f5;
  font-size: 14px;
}

/* 进度条与标签 */
.progress-bar-bg {
  width: 120px;
  height: 6px;
  background: #eee;
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #4facfe, #00f2fe);
  border-radius: 3px;
}

.error-tag-new {
  background: #fff1f0;
  color: #ff4d4f;
  border: 1px solid #ffccc7;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.suggestion-text {
  color: #666;
  font-size: 13px;
  max-width: 400px;
}
/* =================== 新增报告弹窗样式 =================== */
.report-pop-card {
  position: relative;
  background-color: #ffffff; /* 图片背景色 */
  width: 700px;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  border: 1px solid rgba(40, 181, 193, 0.2);
}

.pop-close {
  position: absolute;
  top: 20px;
  right: 25px;
  font-size: 28px;
  color: #666;
  cursor: pointer;
  line-height: 1;
  transition: color 0.2s;
}

.pop-close:hover {
  color: #ff4d4f;
}

.report-header-line {
  display: flex;
  align-items: center;
  margin-bottom: 25px;
}

.v-line {
  width: 5px;
  height: 28px;
  background-color: #28b5c1;
  margin-right: 15px;
}

.report-title-text {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

/* 修改加载状态样式 */
.report-loading-status {
  padding: 60px 0;
  text-align: center;
  color: #28b5c1;
}

.report-loading-status p {
  margin-top: 15px;
  font-size: 16px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

/* 确保内容换行解析正确 */
.report-desc-text {
  font-size: 16px;
  line-height: 1.8;
  color: #444;
  background: rgba(40, 181, 193, 0.05);
  padding: 20px;
  border-radius: 12px;
}

.highlight-text {
  font-weight: bold;
  color: #333;
}

/* .report-tags-row {
  display: flex;
  gap: 15px;
}

.report-tag-item {
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: bold;
  color: #fff;
}

.report-tag-item.error {
  background-color: #28b5c1;
}

.report-tag-item.focus {
  background-color: #28b5c1;
  opacity: 0.85;
} */

.report-btn {
  border-color: #28b5c1;
  color: black;
}

/* =================== 原有样式保持 =================== */
.pie-chart {
  width: 120px;
  height: 120px;
  transform: rotate(-90deg);
  border-radius: 50%;
  background: #f5f5f5; 
}
.pie-segment {
  fill: none;
  stroke-width: 32; 
  transition: all 0.3s ease; 
  cursor: pointer;
}

.pie-segment:hover {
  stroke-width: 34;
  filter: brightness(1.1); 
}

.pie-chart:hover .pie-segment:not(:hover) {
  opacity: 0.7;
}
.pie-container {
  display: flex;
  flex-direction: row;
  align-items: center; 
  justify-content: flex-start;
  gap: 40px; 
  padding: 20px 10px;
}

.pie-chart {
  width: 140px;  
  height: 140px;
  flex-shrink: 0; 
  transform: rotate(-90deg);
  border-radius: 50%;
  background: #f5f5f5;
}

.donut-list {
  flex: 1; 
  font-size: 13px;
  color: #666;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.donut-list p {
  margin: 0;
  display: flex;
  align-items: center;
  white-space: nowrap;
}

.legend-text {
  max-width: 200px; 
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 8px;
}

.percent-text {
  color: #999;
  font-weight: normal;
}

.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 10px;
  flex-shrink: 0;
}
/* .modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;  
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  
  display: flex;
  justify-content: center;
  align-items: center; 
  
  z-index: 2000;
} */
.draft-modal {
  background: white; width: 600px; border-radius: 8px; overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}
.modal-header {
  padding: 15px 20px; border-bottom: 1px solid #eee;
  display: flex; justify-content: space-between; align-items: center;
}
.modal-header-left { display: flex; align-items: center; }
.modal-title-text { font-size: 16px; font-weight: bold; color: #333; }
.save-exit-btn {
  background: #28b5c1; color: white; border: none; height: 24px; font-size: 12px;
  padding: 0 12px; line-height: 24px; margin-right: 10px; border-radius: 4px;
  cursor: pointer; transition: 0.3s; display: inline-flex; align-items: center;
}
.save-exit-btn:disabled { background: #ccc; cursor: not-allowed; }
.modal-body { padding: 20px; max-height: 400px; overflow-y: auto; background: #ffffff; }
.draft-item {
  display: flex; align-items: center; padding: 15px; background: white;
  border: 1px solid #eee; border-radius: 8px; margin-bottom: 12px;
  cursor: pointer; transition: 0.2s;
}
.draft-item:hover { border-color: #28b5c1; }
.draft-item.is-selected { border-color: #28b5c1; background: #f0fbfc; }
.draft-name { font-weight: bold; font-size: 14px; margin-bottom: 4px; }
.draft-tag { font-weight: normal; font-size: 11px; background: #eee; color: #999; padding: 1px 5px; border-radius: 3px; margin-left: 5px; }
.draft-meta { font-size: 12px; color: #999; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }
.header-left { display: flex; align-items: center; }
.title-line { width: 4px; height: 20px; background-color: #28b5c1; margin-right: 12px; }
.header-content-column { display: flex; flex-direction: column; }
.breadcrumb-title { margin: 0; font-size: 18px; display: flex; align-items: center; color: #333; height: 32px; }
.root-node { cursor: pointer; transition: color 0.2s; }
.root-node:hover { color: #28b5c1; }
.sep { margin: 0 10px; color: #999; font-weight: normal; font-family: "SimSun", serif; }
.current-node { color: #28b5c1; font-weight: bold; }
.header-action-bar-sub { display: flex; gap: 12px; }
.standard-btn {
  height: 32px; padding: 0 15px; font-size: 13px; display: flex;
  align-items: center; justify-content: center; border-radius: 4px;
  border: 1px solid #ddd; background: white; cursor: pointer; white-space: nowrap;
}
.standard-btn.primary { background: #28b5c1; border-color: #28b5c1; color: white; }
.course-card { 
  display: flex; padding: 10px; background: #ffffff; border: 1px solid #f0f0f0; 
  border-radius: 12px; align-items: center; margin-bottom: 16px; transition: all 0.3s ease; cursor: pointer; 
}
.course-card:hover { border-color: #28b5c1; background-color: #f9fdfd; transform: translateY(-3px); box-shadow: 0 6px 16px rgba(40, 181, 193, 0.12); }
.course-cover { width: 100px; height: 100px; border-radius: 8px; margin-right: 20px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.cover-icon { font-size: 32px; }
.course-main { flex-grow: 1}
.title-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.title-row h4 { margin: 0; font-size: 17px; color: #333; }
.manage-btn { background: transparent; color: #28b5c1; border: 1px solid #28b5c1; padding: 6px 15px; border-radius: 4px; font-size: 13px; cursor: pointer; }
.manage-btn:hover { background: #28b5c1; color: white; }
.class-item-row { display: flex; justify-content: space-between; align-items: center; padding: 18px; border: 1px solid #eee; border-radius: 10px; margin-bottom: 12px; background: #fff; transition: border-color 0.2s; }
.class-title { font-weight: bold; font-size: 15px; color: #333; }
.class-sub { font-size: 12px; color: #999; margin-top: 5px; }
.class-ops { display: flex; gap: 10px; }
.op-btn { padding: 6px 14px; border-radius: 4px; border: 1px solid #ddd; background: white; cursor: pointer; font-size: 12px; }
.op-btn:hover { border-color: #28b5c1; color: #28b5c1; }
.op-btn.primary { background: #28b5c1; border-color: #28b5c1; color: white; }
.info-banner { background-color: #fff9c4; padding: 10px; border-radius: 4px; font-size: 13px; margin-bottom: 20px; color: #856404; }
.dashboard-wrapper { display: flex; flex-direction: column; gap: 20px; margin-top: 5px; }
.db-stats { display: flex; gap: 20px; }
.db-stat-card { flex: 1; background: #fff; padding: 18px; border: 1px solid #eee; border-radius: 8px; }
.db-label { font-size: 13px; color: #999; }
.db-value { font-size: 26px; font-weight: bold; margin: 8px 0; }
.db-value small { font-size: 14px; color: #ccc; }
.db-value.red { color: #ff4d4f; }
.db-charts { display: flex; gap: 20px; }
.db-chart-box { flex: 1; background: #fff; border: 1px solid #eee; padding: 20px; border-radius: 8px; }
.db-box-title { font-weight: bold; font-size: 14px; margin-bottom: 20px; border-left: 3px solid #28b5c1; padding-left: 10px; }
.bar-line {
  display: flex;
  align-items: center;
  justify-content: space-between; 
  gap: 15px;
  margin-bottom: 12px;
}
.bar-txt {
  flex: 1;              
  white-space: nowrap; 
  overflow: hidden;    
  text-overflow: ellipsis; 
  color: #555;
  font-size: 14px;
  text-align: left;    
}
.bar-track {
  width: 240px;        
  flex: none;          
  height: 10px;
  background: #f5f5f5;
  border-radius: 5px;
  overflow: hidden;
}
.bar-inner {
  height: 100%;
  background: #8e71ff;
  border-radius: 5px;
  transition: width 0.6s ease;
}
.bar-val {
  width: 25px;         
  text-align: right;
  color: #8e71ff;
  font-weight: bold;
  font-size: 14px;
}
.db-table-box { background: #fff; border: 1px solid #eee; padding: 20px; border-radius: 8px; }
.db-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.db-table th { text-align: left; padding: 12px; color: #999; border-bottom: 1px solid #eee; }
.db-table td { padding: 12px; border-bottom: 1px solid #f9f9f9; }
.s-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.s-dot.g { background: #52c41a; } .s-dot.r { background: #ff4d4f; }
.high { color: #52c41a; font-weight: bold; }
.stat-group { display: flex; gap: 15px; font-size: 13px; font-weight: normal; align-items: center; }
.stat-item { display: flex; align-items: center; }
.unsubmitted-row { background-color: #fafafa; }
.unsubmitted-row td { color: #999; }
.pending { color: #bfbfbf; font-style: italic; }
.rank-badge { display: inline-block; width: 24px; height: 24px; line-height: 24px; text-align: center; border-radius: 50%; background: #f0f0f0; color: #666; font-weight: bold; font-size: 12px; }
.top-1 { background: #ffd700; color: #fff; box-shadow: 0 2px 4px rgba(255,215,0,0.3); }
.top-2 { background: #c0c0c0; color: #fff; box-shadow: 0 2px 4px rgba(192,192,192,0.3); }
.top-3 { background: #cd7f32; color: #fff; box-shadow: 0 2px 4px rgba(205,127,50,0.3); }
</style>