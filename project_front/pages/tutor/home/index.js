const { ensureTutor } = require('../../../utils/auth');
const { get } = require('../../../utils/request');
const { APPLICATION_STATUS_COLOR, PAPER_STATUS_COLOR } = require('../../../utils/constants');

Page({
  data: {
    userInfo: {},
    departmentLabel: '未设置',
    stats: {},
    pendingApplications: [],
    recentPapers: [],
    loading: false
  },

  onShow() {
    const user = ensureTutor();
    if (!user) return;
    this.setData({
      userInfo: user,
      departmentLabel: this.parseDepartment(user)
    });
    this.fetchOverview();
  },

  onPullDownRefresh() {
    this.fetchOverview(true);
  },

  parseDepartment(user) {
    if (!user) return '未设置';
    if (user.department_name) return user.department_name;
    if (user.department_id) return `院系ID: ${user.department_id}`;
    return '未设置';
  },

  async fetchOverview(fromPullDown = false) {
    this.setData({ loading: true });
    try {
      console.log('[DEBUG] 开始获取导师工作台数据...');
      
      // 分别获取两个API，便于诊断
      let applications, papers;
      
      try {
        applications = await get('/tutor/applications', { page: 1, page_size: 5, status: 0 }, { showLoading: !fromPullDown });
      } catch (appErr) {
        console.warn('[WARN] 申请列表获取失败，使用空数据:', appErr);
        applications = { total: 0, items: [] };
      }
      
      try {
        papers = await get('/tutor/papers', { page: 1, page_size: 5 }, { showLoading: !fromPullDown });
      } catch (paperErr) {
        console.warn('[WARN] 论文列表获取失败，使用空数据:', paperErr);
        papers = { total: 0, items: [] };
      }
      
      // 计算统计数据
      const stats = {
        pending_applications: applications?.total || 0,
        published_topics: 0, // 需要调用选题接口获取
        guiding_students: papers?.total || 0,
        reviewing_papers: papers?.items?.filter(p => p.status === 1 || p.status === 2).length || 0
      };

      this.setData({
        stats,
        pendingApplications: this.decorateApplications(applications?.items || []),
        recentPapers: this.decoratePapers(papers?.items || [])
      });
    } catch (err) {
      console.error('[ERROR] 概览数据获取失败:', err);
      console.error('[ERROR] 错误详情:', JSON.stringify(err));
      wx.showToast({ 
        title: '数据加载失败，请重试', 
        icon: 'none' 
      });
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

  goTopics() {
    wx.navigateTo({ url: '/pages/tutor/topics/index' });
  },

  goApplications() {
    wx.navigateTo({ url: '/pages/tutor/applications/index' });
  },

  goPapers() {
    wx.navigateTo({ url: '/pages/tutor/papers/index' });
  },

  goProfile() {
    wx.navigateTo({ url: '/pages/tutor/profile/index' });
  },

  handleApplication(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({ url: `/pages/tutor/applications/index?id=${id}` });
  },

  goPaperDetail(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({ url: `/pages/tutor/paper-detail/index?id=${id}` });
  }
});
