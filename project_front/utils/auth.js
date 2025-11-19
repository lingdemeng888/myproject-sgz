/**
 * 认证管理工具
 */
const { STORAGE_KEY, ROLE_HOME_MAP, ROLE } = require('./constants');

/**
 * 保存Token
 * @param {string} token - JWT Token
 */
function setToken(token) {
  try {
    wx.setStorageSync(STORAGE_KEY.TOKEN, token);
    return true;
  } catch (e) {
    console.error('保存Token失败:', e);
    return false;
  }
}

/**
 * 获取Token
 * @returns {string|null} Token或null
 */
function getToken() {
  try {
    return wx.getStorageSync(STORAGE_KEY.TOKEN) || null;
  } catch (e) {
    console.error('读取Token失败:', e);
    return null;
  }
}

/**
 * 保存用户信息
 * @param {object} userInfo - 用户信息对象
 */
function setUserInfo(userInfo) {
  try {
    wx.setStorageSync(STORAGE_KEY.USER_INFO, JSON.stringify(userInfo));
    // 同时保存主要角色
    if (userInfo.roles && userInfo.roles.length > 0) {
      wx.setStorageSync(STORAGE_KEY.USER_ROLE, userInfo.roles[0]);
    }
    return true;
  } catch (e) {
    console.error('保存用户信息失败:', e);
    return false;
  }
}

/**
 * 获取用户信息
 * @returns {object|null} 用户信息对象或null
 */
function getUserInfo() {
  try {
    const userInfoStr = wx.getStorageSync(STORAGE_KEY.USER_INFO);
    return userInfoStr ? JSON.parse(userInfoStr) : null;
  } catch (e) {
    console.error('读取用户信息失败:', e);
    return null;
  }
}

/**
 * 获取用户角色
 * @returns {string|null} 角色标识或null
 */
function getUserRole() {
  try {
    return wx.getStorageSync(STORAGE_KEY.USER_ROLE) || null;
  } catch (e) {
    console.error('读取用户角色失败:', e);
    return null;
  }
}

/**
 * 检查是否已登录
 * @returns {boolean} 是否已登录
 */
function checkLogin() {
  const token = getToken();
  const userInfo = getUserInfo();
  return !!(token && userInfo);
}

/**
 * 清除认证信息(登出)
 */
function clearAuth() {
  try {
    wx.removeStorageSync(STORAGE_KEY.TOKEN);
    wx.removeStorageSync(STORAGE_KEY.USER_INFO);
    wx.removeStorageSync(STORAGE_KEY.USER_ROLE);
    return true;
  } catch (e) {
    console.error('清除认证信息失败:', e);
    return false;
  }
}

/**
 * 登出并跳转到身份选择页
 */
function logout() {
  clearAuth();
  wx.reLaunch({
    url: '/pages/auth/identity/index?from=logout'
  });
}

/**
 * 确保当前用户已登录且为学生角色
 * @param {object} options - 选项
 * @param {boolean} options.redirect - 是否在失败时跳转到身份选择页
 * @param {boolean} options.toast - 是否提示用户
 * @returns {object|null} 用户信息或null
 */
function ensureStudent(options = {}) {
  const { redirect = true, toast = true } = options;
  const user = getUserInfo();

  if (!user) {
    if (toast) {
      wx.showToast({ title: '请先登录学生账号', icon: 'none' });
    }
    if (redirect) {
      setTimeout(() => {
        wx.reLaunch({ url: '/pages/student/login/index' });
      }, 800);
    }
    return null;
  }

  const hasStudentRole = Array.isArray(user.roles) && user.roles.includes(ROLE.STUDENT);
  if (!hasStudentRole) {
    if (toast) {
      wx.showToast({ title: '当前账号非学生角色', icon: 'none' });
    }
    if (redirect) {
      setTimeout(() => {
        wx.reLaunch({ url: '/pages/auth/identity/index' });
      }, 800);
    }
    return null;
  }

  return user;
}

/**
 * 确保当前用户已登录且为导师角色
 * @param {object} options - 选项
 * @param {boolean} options.redirect - 是否在失败时跳转到登录页
 * @param {boolean} options.toast - 是否提示用户
 * @returns {object|null} 用户信息或null
 */
function ensureTutor(options = {}) {
  const { redirect = true, toast = true } = options;
  const user = getUserInfo();

  if (!user) {
    if (toast) {
      wx.showToast({ title: '请先登录导师账号', icon: 'none' });
    }
    if (redirect) {
      setTimeout(() => {
        wx.reLaunch({ url: '/pages/tutor/login/index' });
      }, 800);
    }
    return null;
  }

  const hasTutorRole = Array.isArray(user.roles) && user.roles.includes(ROLE.TUTOR);
  if (!hasTutorRole) {
    if (toast) {
      wx.showToast({ title: '当前账号非导师角色', icon: 'none' });
    }
    if (redirect) {
      setTimeout(() => {
        wx.reLaunch({ url: '/pages/auth/identity/index' });
      }, 800);
    }
    return null;
  }

  return user;
}

/**
 * 确保当前用户已登录且为管理员角色
 * @param {object} options - 选项
 * @param {boolean} options.redirect - 是否在失败时跳转到登录页
 * @param {boolean} options.toast - 是否提示用户
 * @returns {object|null} 用户信息或null
 */
function ensureAdmin(options = {}) {
  const { redirect = true, toast = true } = options;
  const user = getUserInfo();

  if (!user) {
    if (toast) {
      wx.showToast({ title: '请先登录管理员账号', icon: 'none' });
    }
    if (redirect) {
      setTimeout(() => {
        wx.reLaunch({ url: '/pages/admin/login/index' });
      }, 800);
    }
    return null;
  }

  const hasAdminRole = Array.isArray(user.roles) && user.roles.includes(ROLE.ADMIN);
  if (!hasAdminRole) {
    if (toast) {
      wx.showToast({ title: '当前账号非管理员角色', icon: 'none' });
    }
    if (redirect) {
      setTimeout(() => {
        wx.reLaunch({ url: '/pages/auth/identity/index' });
      }, 800);
    }
    return null;
  }

  return user;
}

/**
 * 登录成功后跳转到对应首页
 * @param {string} role - 用户角色
 */
function navigateToHome(role) {
  const homePage = ROLE_HOME_MAP[role];
  if (homePage) {
    wx.reLaunch({ url: homePage });
  } else {
    wx.showToast({ title: '未知角色,无法跳转', icon: 'none' });
  }
}

/**
 * 检查用户是否有指定角色
 * @param {string} role - 角色标识
 * @returns {boolean} 是否拥有该角色
 */
function hasRole(role) {
  const userInfo = getUserInfo();
  if (!userInfo || !userInfo.roles) return false;
  return userInfo.roles.includes(role);
}

/**
 * 执行登录流程
 * @param {string} username 用户名
 * @param {string} password 密码
 * @returns {Promise<object>} 用户信息对象
 */
function login(username, password) {
  const { post } = require('./request');
  return post('/auth/login', { username, password }, { showLoading: true })
    .then(data => {
      // data 结构: { access_token, token_type, expires_in, user }
      setToken(data.access_token);
      setUserInfo(data.user);
      return data.user;
    });
}

module.exports = {
  setToken,
  getToken,
  setUserInfo,
  getUserInfo,
  getUserRole,
  checkLogin,
  clearAuth,
  logout,
  navigateToHome,
  hasRole,
  login,
  ensureStudent,
  ensureTutor,
  ensureAdmin
};
