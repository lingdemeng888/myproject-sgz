const { ensureStudent } = require('../../../utils/auth');
const { get } = require('../../../utils/request');
const { APPLICATION_STATUS_COLOR, PAPER_STATUS_COLOR } = require('../../../utils/constants');

Page({
  data: {
    userInfo: {},
    majorLabel: '未设置',
    recentApplications: [],
    recentPapers: [],
    loading: false
  },

  onShow() {
    const user = ensureStudent();
    if (!user) return;
    this.setData({
      userInfo: user,
      majorLabel: this.parseMajor(user)
    });
    this.fetchOverview();
  },

  onPullDownRefresh() {
    this.fetchOverview(true);
  },

  parseMajor(user) {
    if (!user) return '未设置';
    if (user.primary_major_name) return user.primary_major_name;
    if (user.primary_major_id) return `专业ID：${user.primary_major_id}`;
    return '未设置';
  },

  async fetchOverview(fromPullDown = false) {
    this.setData({ loading: true });
    try {
      const [apps, papers] = await Promise.all([
        get('/student/topics/applications', { page: 1, page_size: 3 }, { showLoading: !fromPullDown }),
        get('/student/papers', { page: 1, page_size: 3 }, { showLoading: !fromPullDown })
      ]);
      this.setData({
        recentApplications: this.decorateApplications(apps?.items || []),
        recentPapers: this.decoratePapers(papers?.items || [])
      });
    } catch (err) {
      console.error('概览数据获取失败', err);
    } finally {
      this.setData({ loading: false });
      if (fromPullDown) {
        wx.stopPullDownRefresh();
      }
    }
  },

  decorateApplications(list) {
    return list.map(item => ({
      ...item,
      created_at_fmt: this.formatDate(item.created_at),
      status_color: APPLICATION_STATUS_COLOR[item.status] || '#888'
    }));
  },

  decoratePapers(list) {
    return list.map(item => ({
      ...item,
      term_name: item.term_name || this.formatTerm(item.term),
      status_color: PAPER_STATUS_COLOR[item.status] || '#666'
    }));
  },

  formatDate(value) {
    if (!value) return '-';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    const hh = String(date.getHours()).padStart(2, '0');
    const mm = String(date.getMinutes()).padStart(2, '0');
    return `${y}-${m}-${d} ${hh}:${mm}`;
  },

  formatTerm(term) {
    if (term === 1) return '上学期';
    if (term === 2) return '下学期';
    return '未知学期';
  },

  refreshData() {
    this.fetchOverview();
  },

  goTopicList() {
    wx.navigateTo({ url: '/pages/student/topic-list/index' });
  },

  goApplications() {
    wx.navigateTo({ url: '/pages/student/my-applications/index' });
  },

  goPapers() {
    wx.navigateTo({ url: '/pages/student/my-papers/index' });
  },

  goProfile() {
    wx.navigateTo({ url: '/pages/student/profile/index' });
  },

  goPaperDetail(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({ url: `/pages/student/paper-detail/index?id=${id}` });
  }
});
