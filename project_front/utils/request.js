/**
 * 网络请求封装
 */
const { API_BASE_URL } = require('./constants');
const { getToken, clearAuth } = require('./auth');

/**
 * 统一请求方法
 * @param {string} url - 请求路径(相对路径,如 /auth/login)
 * @param {object} options - 请求配置
 * @param {string} options.method - 请求方法(GET/POST/PUT/DELETE)
 * @param {object} options.data - 请求数据
 * @param {object} options.header - 请求头
 * @param {boolean} options.showLoading - 是否显示加载提示
 * @param {boolean} options.showError - 是否显示错误提示
 * @returns {Promise} 返回Promise对象
 */
function request(url, options = {}) {
  const {
    method = 'GET',
    data = {},
    header = {},
    showLoading = false,
    showError = true,
    requireAuth = true,
    autoRedirectOn401 = true
  } = options;

  // 显示加载提示
  if (showLoading) {
    wx.showLoading({ title: '加载中...', mask: true });
  }

  // 获取Token
  const token = getToken();

  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API_BASE_URL}${url}`,
      method: method.toUpperCase(),
      data: data,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...header
      },
      success(res) {
        // 隐藏加载提示
        if (showLoading) {
          wx.hideLoading();
        }

        // HTTP状态码处理
        if (res.statusCode === 200) {
          // 后端统一响应格式: { code: number, message: string, data: any }
          const response = res.data;
          
          if (response.code === 200) {
            // 请求成功
            resolve(response.data);
          } else {
            // 业务错误（code !== 200）
            if (showError) {
              wx.showToast({ 
                title: response.message || '请求失败', 
                icon: 'none',
                duration: 2000
              });
            }
            reject(response);
          }
        } else if (res.statusCode === 401) {
          // Token过期或未授权
          if (showError) {
            wx.showToast({ title: requireAuth ? '登录已过期,请重新登录' : '当前请求未授权', icon: 'none' });
          }
          if (requireAuth) {
            clearAuth();
            if (autoRedirectOn401) {
              setTimeout(() => {
                wx.reLaunch({ url: '/pages/auth/identity/index' });
              }, 1500);
            }
          }
          reject(res);
        } else if (res.statusCode === 403) {
          // 无权限
          if (showError) {
            wx.showToast({ title: '无权限访问', icon: 'none' });
          }
          reject(res);
        } else if (res.statusCode === 404) {
          // 资源不存在
          if (showError) {
            wx.showToast({ title: '请求的资源不存在', icon: 'none' });
          }
          reject(res);
        } else if (res.statusCode >= 500) {
          // 服务器错误
          if (showError) {
            wx.showToast({ title: '服务器错误,请稍后重试', icon: 'none' });
          }
          reject(res);
        } else {
          // 其他错误
          if (showError) {
            wx.showToast({ 
              title: `请求错误 ${res.statusCode}`, 
              icon: 'none' 
            });
          }
          reject(res);
        }
      },
      fail(err) {
        // 隐藏加载提示
        if (showLoading) {
          wx.hideLoading();
        }
        
        // 网络请求失败
        if (showError) {
          wx.showToast({ 
            title: '网络请求失败,请检查网络', 
            icon: 'none',
            duration: 2000
          });
        }
        console.error('网络请求失败:', err);
        reject(err);
      }
    });
  });
}

/**
 * GET请求
 */
function get(url, data = {}, options = {}) {
  return request(url, { ...options, method: 'GET', data });
}

/**
 * POST请求
 */
function post(url, data = {}, options = {}) {
  return request(url, { ...options, method: 'POST', data });
}

/**
 * PUT请求
 */
function put(url, data = {}, options = {}) {
  return request(url, { ...options, method: 'PUT', data });
}

/**
 * DELETE请求
 */
function del(url, data = {}, options = {}) {
  return request(url, { ...options, method: 'DELETE', data });
}

/**
 * 上传文件
 * @param {string} url - 上传地址
 * @param {string} filePath - 文件路径
 * @param {object} formData - 额外表单数据
 * @param {function} onProgress - 上传进度回调
 */
function uploadFile(url, filePath, formData = {}, onProgress) {
  const token = getToken();
  
  return new Promise((resolve, reject) => {
    const uploadTask = wx.uploadFile({
      url: `${API_BASE_URL}${url}`,
      filePath: filePath,
      name: 'file',
      formData: formData,
      header: {
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success(res) {
        if (res.statusCode === 200) {
          const response = JSON.parse(res.data);
          if (response.code === 200) {
            resolve(response.data);
          } else {
            wx.showToast({ title: response.message || '上传失败', icon: 'none' });
            reject(response);
          }
        } else {
          wx.showToast({ title: '上传失败', icon: 'none' });
          reject(res);
        }
      },
      fail(err) {
        wx.showToast({ title: '上传失败', icon: 'none' });
        reject(err);
      }
    });

    // 监听上传进度
    if (onProgress && typeof onProgress === 'function') {
      uploadTask.onProgressUpdate((res) => {
        onProgress(res.progress);
      });
    }
  });
}

module.exports = {
  request,
  get,
  post,
  put,
  del,
  uploadFile,
  upload: uploadFile  // 添加别名
};
