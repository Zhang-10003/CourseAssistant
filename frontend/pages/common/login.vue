<template>
  <view class="page-container">
    <view class="login-container">
      <h2 class="title">LOGIN</h2>
      
      <view class="form-item">
        <input type="text" placeholder="Username" v-model="form.username" />
      </view>
      
      <view class="form-item">
        <input type="password" placeholder="Password" v-model="form.password" />
      </view>
      
      <button class="submit-btn" @click="onLogin">Sign in</button>
    </view>
  </view>
</template>

<script setup>
import { reactive } from 'vue';
import http from '../../http/http';

const form = reactive({
  username: '',
  password: ''
});

const onLogin = async () => {
    try {
        uni.showLoading({ title: '登录中...' });
        const res = await http.login(form); // 调用上面的接口
        console.log(res);
        if (res.code === '000') {
            const { token, user_id, user_type } = res.data;

            // 1. 持久化存储
            uni.setStorageSync('token', token);
            uni.setStorageSync('user_id', user_id);
            uni.setStorageSync('user_type', user_type);

            uni.showToast({ title: '欢迎回来' });

            // 2. 根据角色跳转页面
            const roleRoutes = {
                0: '/pages/admin/index',
                1: '/pages/teacher/index',
                2: '/pages/student/index'
            };
            uni.redirectTo({ url: roleRoutes[user_type] });
        }
    } catch (e) {
        uni.showToast({ title: '登录失败', icon: 'none' });
    } finally {
        uni.hideLoading();
    }
};
</script>

<style scoped>
/* 样式部分保持不变... */
.page-container {
  width: 100vw;
  height: 100vh;
  background-color: #f0f2f5; 
  display: flex;
  justify-content: center;
  align-items: center;
}
.login-container {
  width: 450px;
  height: 350px;
  background: #ffffff; 
  border-radius: 15px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  box-sizing: border-box;
}
.title { color: #333333; margin-bottom: 40px; }
.form-item { width: 80%; margin-bottom: 20px; }
input { width: 100%; padding: 12px; background: #f9f9f9; border: 1px solid #dcdfe6; border-radius: 4px; }
.submit-btn { width: 80%; padding: 12px; background-color: #4a90e2; color: white; border-radius: 4px; }
</style>