Page({
  data: {
    seconds: 5,
    // 请将校园景观.jpg 放到 /assets/images/ 目录
    bgPath: '/assets/images/校园景观.jpg'
  },
  onLoad() {
    // 检查是否已登录
    this.checkLoginStatus();
  },
  
  // 检查登录状态
  checkLoginStatus() {
    try {
      const token = wx.getStorageSync('token');
      const userRole = wx.getStorageSync('userRole');
      
      if (token && userRole) {
        // 已登录,直接跳转到对应首页
        this.jumpToHomePage(userRole);
      } else {
        // 未登录,显示倒计时
        this.startCountdown();
      }
    } catch (e) {
      // 读取失败,显示倒计时
      this.startCountdown();
    }
  },
  
  // 根据角色跳转到对应首页
  jumpToHomePage(role) {
    const homeMap = {
      'STUDENT': '/pages/student/home/index',
      'TUTOR': '/pages/tutor/home/index',
      'ADMIN': '/pages/admin/home/index'
    };
    const homePage = homeMap[role] || '/pages/auth/identity/index';
    wx.reLaunch({ url: homePage });
  },
  
  startCountdown() {
    const timer = setInterval(() => {
      let s = this.data.seconds - 1;
      if (s <= 0) {
        clearInterval(this._timer);
        // 倒计时完成后进入身份选择页
        wx.redirectTo({ url: '/pages/auth/identity/index' });
        return;
      }
      this.setData({ seconds: s });
    }, 1000);
    this._timer = timer;
  },
  
  // 跳过倒计时
  skip() {
    if (this._timer) clearInterval(this._timer);
    wx.redirectTo({ url: '/pages/auth/identity/index' });
  },
  
  onUnload() {
    if (this._timer) clearInterval(this._timer);
  }
});
