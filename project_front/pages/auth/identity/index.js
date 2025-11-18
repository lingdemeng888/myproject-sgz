Page({
  onLoad(options) {
    // 如果是从登出返回,显示提示
    if (options.from === 'logout') {
      wx.showToast({ title: '已退出登录', icon: 'none' });
    }
  },
  
  // 学生登录
  goStudent() {
    wx.navigateTo({ url: '/pages/student/login/index' });
  },
  
  // 导师登录
  goTutor() {
    wx.navigateTo({ url: '/pages/tutor/login/index' });
  },
  
  // 管理员登录
  goAdmin() {
    wx.navigateTo({ url: '/pages/admin/login/index' });
  }
});
