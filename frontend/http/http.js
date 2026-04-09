/**
 * 封装 uni.request 
 * 适配后端格式: { code: "xxx", message: "提示信息", data: {} }
 */

// 1. 环境配置
let BASE_URL = "";
if (process.env.NODE_ENV === "development") {
    BASE_URL = "http://127.0.0.1:8000"; // 确保此地址后端可连通
} else {
    BASE_URL = "https://api.yourdomain.com";
}

// 2. 核心请求封装
const request = (url, options = {}) => {
    // 每次请求动态获取最新的 token
    const token = uni.getStorageSync("token");

    // URL 拼接优化
    const finalUrl = url.startsWith('http') 
        ? url 
        : BASE_URL + (url.startsWith('/') ? url : '/' + url);

    return new Promise((resolve, reject) => {
        uni.request({
            url: finalUrl,
            method: options.method || 'GET',
            data: options.data || {},
            header: {
                "content-type": "application/json",
                // 自动携带 Authorization 头
                ...(token && { "authorization": "Bearer " + token }),
                ...options.header
            },
            success: (res) => {
                // res.data 包含后端返回的 { code, message, data }
                const { statusCode, data } = res;

                // --- 核心逻辑开始 ---
                
                // 1. 优先判断是否有后端定义的业务 code
                if (data && typeof data.code !== 'undefined') {
                    if (data.code === "000") {
                        // 业务成功：返回 data 供页面使用
                        resolve(data);
                    } else {
                        // 业务失败：即使状态码是 400/500，只要有 message 也要提示用户
                        const msg = data.message || "操作失败";
                        uni.showToast({ title: msg, icon: 'none' });
                        
                        // 特殊处理：比如 401 或特定的登录失效 code
                        if (statusCode === 401 || data.code === "401") {
                            uni.removeStorageSync('token');
                            // 可以视情况跳转到登录页
                        }
                        
                        reject(data); // 抛出 data 供业务层 try...catch 捕获
                    }
                } 
                // 2. 如果后端没有按约定的 JSON 格式返回（可能是网络层面的严重错误）
                else {
                    const errorMsg = `服务器异常 (${statusCode})`;
                    uni.showToast({ title: errorMsg, icon: 'none' });
                    reject({ code: statusCode, message: errorMsg });
                }
                
                // --- 核心逻辑结束 ---
            },
            fail: (err) => {
                // 网络断开、超时等物理层面的失败
                uni.showToast({ title: "网络连接失败，请检查网络", icon: 'none' });
                reject(err);
            }
        });
    });
};

// 3. 常用方法快捷调用
const http = {
    get: (url, data, options = {}) => request(url, { ...options, method: 'GET', data }),
    post: (url, data, options = {}) => request(url, { ...options, method: 'POST', data }),
    put: (url, data, options = {}) => request(url, { ...options, method: 'PUT', data }),
    delete: (url, data, options = {}) => request(url, { ...options, method: 'DELETE', data }),
};

// 4. 定义具体业务接口
const api = {
    // 认证相关
    auth: {
        login: (data) => http.post('/auth/login', data),
        getEmailCode: (email) => http.get('/auth/code', { email }),
    },
    // 用户相关
    user: {
        getInfo: () => http.get('/user/info'),
    }
};

// 5. 导出统一对象
export default {
    ...http,
    ...api.auth, // 展开后支持 http.login()
    ...api.user, // 展开后支持 http.getInfo()
    raw: request // 暴露原始 request 方法备用
};