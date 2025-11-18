const { login } = require('../../../utils/auth');

Page({
  data: {
    username: '',
    password: '',
    showPassword: false,
    rememberMe: false,
    loading: false
  },

  onLoad() {
    // 尝试读取记住的用户名
    const savedUsername = wx.getStorageSync('savedUsername_admin');
    const savedPassword = wx.getStorageSync('savedPassword_admin');
    const rememberMe = wx.getStorageSync('rememberMe_admin');
    
    if (rememberMe) {
      this.setData({
        username: savedUsername || '',
        password: savedPassword || '',
        rememberMe: true
      });
    }
  },

  onUsernameInput(e) {
    this.setData({ username: e.detail.value });
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value });
  },

  togglePassword() {
    this.setData({ showPassword: !this.data.showPassword });
  },

  toggleRemember() {
    this.setData({ rememberMe: !this.data.rememberMe });
  },

  async handleLogin() {
    const { username, password, rememberMe } = this.data;

    // 表单验证
    if (!username || !password) {
      wx.showToast({ title: '请填写完整信息', icon: 'none' });
      return;
    }

    if (username.trim().length < 3) {
      wx.showToast({ title: '用户名至少3个字符', icon: 'none' });
      return;
    }

    if (password.length < 6) {
      wx.showToast({ title: '密码至少6个字符', icon: 'none' });
      return;
    }

    this.setData({ loading: true });

    try {
      const result = await login(username.trim(), password);
      
      // 检查角色（必须包含ADMIN角色）
      if (!result.roles || !result.roles.includes('ADMIN')) {
        wx.showToast({ 
          title: '该账号不是管理员角色，请使用正确的登录入口', 
          icon: 'none',
          duration: 2500
        });
        this.setData({ loading: false });
        return;
      }

      // 检查账号状态
      if (result.status !== 1) {
        wx.showToast({ 
          title: '账号已被禁用，请联系超级管理员', 
          icon: 'none',
          duration: 2500
        });
        this.setData({ loading: false });
        return;
      }

      // 记住密码（登录成功后才保存）
      if (rememberMe) {
        wx.setStorageSync('savedUsername_admin', username);
        wx.setStorageSync('savedPassword_admin', password);
        wx.setStorageSync('rememberMe_admin', true);
      } else {
        wx.removeStorageSync('savedUsername_admin');
        wx.removeStorageSync('savedPassword_admin');
        wx.removeStorageSync('rememberMe_admin');
      }

      // 显示欢迎信息
      wx.showToast({ 
        title: `欢迎回来，${result.real_name}`, 
        icon: 'success',
        duration: 1500
      });
      
      // 延迟跳转到后台首页
      setTimeout(() => {
        wx.reLaunch({ url: '/pages/admin/home/index' });
      }, 1500);
      
    } catch (error) {
      console.error('登录失败:', error);
      // request.js已经显示了错误提示，这里不需要重复显示
      this.setData({ loading: false });
    }
  },

  goForgotPassword() {
    wx.showToast({ title: '请联系超级管理员重置密码', icon: 'none', duration: 2000 });
  }
});
