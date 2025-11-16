Page({
  goStudent() {
    wx.navigateTo({ url: '/pages/student/login/index' });
  },
  goTeacherOrAdmin() {
    wx.navigateTo({ url: '/pages/auth/teacher/index' });
  }
});
