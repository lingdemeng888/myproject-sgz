const { ensureTutor, logout, setUserInfo } = require('../../../utils/auth');
const { get } = require('../../../utils/request');

Page({
  data: {
    user: null,
    departmentLabel: '',
    initial: ''
  },

  onShow() {
    const cached = ensureTutor();
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
    // 院系显示：优先名称，降级ID，最后未设置
    const departmentLabel = user.department_name || (user.department_id ? `院系ID: ${user.department_id}` : '未设置');
    const source = user.real_name || user.username || '';
    const initial = source ? source.slice(0, 1) : '?';
    this.setData({ user, departmentLabel, initial });
  },

  logout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出当前导师账号吗？',
      success(res) {
        if (res.confirm) {
          logout();
        }
      }
    });
  }
});
