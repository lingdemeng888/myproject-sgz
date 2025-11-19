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
    // 尝试读取记住的用户名和密码
    const savedUsername = wx.getStorageSync('savedUsername_student');
    const savedPassword = wx.getStorageSync('savedPassword_student');
    const rememberMe = wx.getStorageSync('rememberMe_student');
    
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
    const newShowPassword = !this.data.showPassword;
    console.log('[DEBUG] 切换密码显示状态:', newShowPassword ? '明文' : '密文');
    this.setData({ showPassword: newShowPassword });
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
      
      // 检查角色（必须包含STUDENT角色）
      if (!result.roles || !result.roles.includes('STUDENT')) {
        wx.showToast({ 
          title: '该账号不是学生角色，请使用正确的登录入口', 
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
        wx.setStorageSync('savedUsername_student', username);
        wx.setStorageSync('savedPassword_student', password);
        wx.setStorageSync('rememberMe_student', true);
      } else {
        wx.removeStorageSync('savedUsername_student');
        wx.removeStorageSync('savedPassword_student');
        wx.removeStorageSync('rememberMe_student');
      }

      // 显示欢迎信息
      wx.showToast({ 
        title: `欢迎回来，${result.real_name}`, 
        icon: 'success',
        duration: 1500
      });
      this.setData({ loading: false });
      
      // 延迟跳转到首页
      setTimeout(() => {
        wx.reLaunch({ url: '/pages/student/home/index' });
      }, 1500);
      
    } catch (error) {
      console.error('登录失败:', error);
      // request.js已经显示了错误提示，这里不需要重复显示
      this.setData({ loading: false });
    }
  },

  goRegister() {
    wx.navigateTo({ url: '/pages/student/register/index' });
  },

  goForgotPassword() {
    wx.showToast({ title: '请联系管理员重置密码', icon: 'none' });
  },

  goIdentitySelect() {
    wx.reLaunch({ url: '/pages/auth/identity/index' });
  }
});
