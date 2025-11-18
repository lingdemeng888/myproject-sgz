const { ensureStudent } = require('../../../utils/auth');
const { get, post } = require('../../../utils/request');
const { APPLICATION_STATUS_COLOR } = require('../../../utils/constants');

Page({
  data: {
    applications: [],
    activeStatus: '',
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false
  },
  loaded: false,

  onShow() {
    if (!ensureStudent()) return;
    if (!this.loaded) {
      this.loaded = true;
      this.refresh();
    }
  },

  onPullDownRefresh() {
    this.refresh();
  },

  onReachBottom() {
    this.fetchApplications();
  },

  changeStatus(e) {
    const value = e.currentTarget.dataset.value;
    const parsed = value === '' ? '' : Number(value);
    if (parsed === this.data.activeStatus) return;
    this.setData({ activeStatus: parsed, applications: [], page: 1, hasMore: true });
    this.fetchApplications(true);
  },

  refresh() {
    this.setData({ applications: [], page: 1, hasMore: true });
    this.fetchApplications(true);
  },

  async fetchApplications(showLoading = false) {
    if (!this.data.hasMore || this.data.loading) return;
    this.setData({ loading: true });
    const params = {
      page: this.data.page,
      page_size: this.data.pageSize
    };
    if (this.data.activeStatus !== '' && this.data.activeStatus !== null) {
      params.status = this.data.activeStatus;
    }
    try {
      const res = await get('/student/topics/applications', params, { showLoading });
      const items = res?.items || [];
      const decorated = items.map(item => ({
        ...item,
        created_at_fmt: this.formatDate(item.created_at),
        status_color: APPLICATION_STATUS_COLOR[item.status] || '#666'
      }));
      const list = [...this.data.applications, ...decorated];
      const total = res?.total || list.length;
      this.setData({
        applications: list,
        page: this.data.page + 1,
        hasMore: list.length < total
      });
    } catch (err) {
      console.error('获取申请列表失败', err);
    } finally {
      this.setData({ loading: false });
      wx.stopPullDownRefresh();
    }
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

  showDetail(e) {
    const { index } = e.currentTarget.dataset;
    const item = this.data.applications[index];
    if (!item) return;
    const content = [
      `申请理由：${item.application_reason || '无'}`,
      `提交时间：${item.created_at_fmt}`,
      item.decision_by_name ? `审批人：${item.decision_by_name}` : '',
      item.decision_comment ? `导师意见：${item.decision_comment}` : ''
    ].filter(Boolean).join('\n');
    wx.showModal({
      title: item.topic_title,
      content,
      showCancel: false
    });
  },

  async createPaper(e) {
    const application = e.currentTarget.dataset.application;
    if (!application) return;
    
    wx.showModal({
      title: '创建论文',
      content: `选题：${application.topic_title}`,
      editable: true,
      placeholderText: '请输入论文标题',
      success: async (res) => {
        if (res.confirm) {
          const title = res.content?.trim();
          if (!title) {
            wx.showToast({ title: '请输入论文标题', icon: 'none' });
            return;
          }
          if (title.length < 5) {
            wx.showToast({ title: '论文标题至少5个字符', icon: 'none' });
            return;
          }
          
          try {
            const result = await post('/student/papers', {
              topic_id: application.topic_id,
              title: title,
              academic_year: application.academic_year || new Date().getFullYear() + '-' + (new Date().getFullYear() + 1),
              term: application.term || 1
            }, { showLoading: true });
            
            wx.showModal({
              title: '创建成功',
              content: '论文已创建，是否立即前往查看？',
              success: (modalRes) => {
                if (modalRes.confirm && result?.id) {
                  wx.navigateTo({ url: `/pages/student/paper-detail/index?id=${result.id}` });
                } else {
                  this.refresh();
                }
              }
            });
          } catch (err) {
            console.error('创建论文失败', err);
          }
        }
      }
    });
  },

  viewPaper(e) {
    const { id } = e.currentTarget.dataset;
    if (!id) return;
    wx.navigateTo({ url: `/pages/student/paper-detail/index?id=${id}` });
  }
});
