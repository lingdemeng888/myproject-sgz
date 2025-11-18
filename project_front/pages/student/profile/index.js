const { ensureStudent, logout, setUserInfo } = require('../../../utils/auth');
const { get } = require('../../../utils/request');

Page({
  data: {
    user: null,
    majorLabel: '',
    initial: ''
  },

  onShow() {
    const cached = ensureStudent();
    if (!cached) return;
    this.updateView(cached);
    this.fetchProfile();
  },

  async fetchProfile() {
    try {
      const user = await get('/auth/me', {}, { showLoading: true });
      setUserInfo(user); // 覆盖缓存
      this.updateView(user);
    } catch (err) {
      console.error('获取个人信息失败', err);
    }
  },

  updateView(user) {
    if (!user) return;
    const majorLabel = user.primary_major_name ? user.primary_major_name : (user.primary_major_id ? `ID：${user.primary_major_id}` : '未设置');
    const source = user.real_name || user.username || '';
    const initial = source ? source.slice(0, 1) : '?';
    this.setData({ user, majorLabel, initial });
  },

  logout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出当前学生账号吗？',
      success(res) {
        if (res.confirm) {
          logout();
        }
      }
    });
  }
});
