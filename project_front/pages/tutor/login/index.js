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
    const savedUsername = wx.getStorageSync('savedUsername_tutor');
    const savedPassword = wx.getStorageSync('savedPassword_tutor');
    const rememberMe = wx.getStorageSync('rememberMe_tutor');
    
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
    const trimmedUsername = username.trim();

    // 表单验证
    if (!trimmedUsername || !password) {
      wx.showToast({ title: '请填写完整信息', icon: 'none' });
      return;
    }

    if (trimmedUsername.length < 3) {
      wx.showToast({ title: '用户名至少3个字符', icon: 'none' });
      return;
    }

    if (password.length < 6) {
      wx.showToast({ title: '密码至少6个字符', icon: 'none' });
      return;
    }

    this.setData({ loading: true });

    try {
      const result = await login(trimmedUsername, password);
      
      // 检查角色（必须包含TUTOR角色）
      if (!result.roles || !result.roles.includes('TUTOR')) {
        wx.showToast({ 
          title: '该账号不是导师角色，请使用正确的登录入口', 
          icon: 'none',
          duration: 2500
        });
        this.setData({ loading: false });
        return;
      }

      // 检查账号状态
      if (result.status !== 1) {
        wx.showToast({ 
          title: '账号已被禁用，请联系管理员', 
          icon: 'none',
          duration: 2500
        });
        this.setData({ loading: false });
        return;
      }

      // 记住密码（登录成功后才保存）
      if (rememberMe) {
        wx.setStorageSync('savedUsername_tutor', trimmedUsername);
        wx.setStorageSync('savedPassword_tutor', password);
        wx.setStorageSync('rememberMe_tutor', true);
      } else {
        wx.removeStorageSync('savedUsername_tutor');
        wx.removeStorageSync('savedPassword_tutor');
        wx.removeStorageSync('rememberMe_tutor');
      }

      // 显示欢迎信息
      wx.showToast({ 
        title: `欢迎回来，${result.real_name}`, 
        icon: 'success',
        duration: 1500
      });
      
      // 延迟跳转到首页
      setTimeout(() => {
        wx.reLaunch({ url: '/pages/tutor/home/index' });
      }, 1500);
      
    } catch (error) {
      console.error('登录失败:', error);
      // request.js已经显示了错误提示，这里不需要重复显示
      this.setData({ loading: false });
    }
  },

  goRegister() {
    wx.navigateTo({ url: '/pages/tutor/register/index' });
  },

  goForgotPassword() {
    wx.showToast({ title: '请联系管理员重置密码', icon: 'none' });
  }
});
