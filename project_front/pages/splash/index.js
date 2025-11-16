Page({
  data: {
    seconds: 5,
    // 请将校园景观.jpg 放到 /assets/images/ 目录
    bgPath: '/assets/images/校园景观.jpg'
  },
  onLoad() {
    this.startCountdown();
  },
  startCountdown() {
    const timer = setInterval(() => {
      let s = this.data.seconds - 1;
      if (s <= 1) {
        clearInterval(this._timer);
        // 倒计时完成后进入身份选择页
        wx.redirectTo({ url: '/pages/auth/identity/index' });
        return;
      }
      this.setData({ seconds: s });
    }, 1000);
    this._timer = timer;
  },
  onUnload() {
    if (this._timer) clearInterval(this._timer);
  }
});
