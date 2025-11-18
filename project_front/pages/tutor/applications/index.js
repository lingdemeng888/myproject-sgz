const { ensureTutor } = require('../../../utils/auth');
const { get, put } = require('../../../utils/request');
const { APPLICATION_STATUS_COLOR } = require('../../../utils/constants');

Page({
  data: {
    activeStatus: null,
    studentName: '',
    list: [],
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false
  },

  onLoad(options) {
    if (!ensureTutor()) return;
    // 如果有id参数，说明是从首页点击特定申请进来的
    if (options.id) {
      this.setData({ activeStatus: 0 });
    }
    this.fetchList();
  },

  onPullDownRefresh() {
    this.setData({ page: 1, list: [], hasMore: true });
    this.fetchList(true);
  },

  changeStatus(e) {
    const value = e.currentTarget.dataset.value;
    this.setData({ 
      activeStatus: value === '' ? null : Number(value),
      page: 1,
      list: [],
      hasMore: true
    });
    this.fetchList();
  },

  onStudentNameInput(e) {
    this.setData({ studentName: e.detail.value });
  },

  applyFilter() {
    this.setData({ page: 1, list: [], hasMore: true });
    this.fetchList();
  },

  resetFilter() {
    this.setData({
      studentName: '',
      activeStatus: null,
      page: 1,
      list: [],
      hasMore: true
    });
    this.fetchList();
  },

  async fetchList(fromPullDown = false) {
    if (this.data.loading) return;
    this.setData({ loading: true });

    try {
      const params = {
        page: this.data.page,
        page_size: this.data.pageSize
      };
      if (this.data.activeStatus !== null) {
        params.status = this.data.activeStatus;
      }
      if (this.data.studentName) {
        params.student_name = this.data.studentName;
      }

      const res = await get('/tutor/applications', params, { showLoading: !fromPullDown });
      const decoratedList = this.decorateList(res.items || []);
      
      this.setData({
        list: this.data.page === 1 ? decoratedList : [...this.data.list, ...decoratedList],
        hasMore: res.items.length >= this.data.pageSize
      });
    } catch (err) {
      console.error('获取申请列表失败', err);
      wx.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      this.setData({ loading: false });
      if (fromPullDown) {
        wx.stopPullDownRefresh();
      }
    }
  },

  decorateList(items) {
    return items.map(item => ({
      ...item,
      created_at_fmt: this.formatDate(item.created_at),
      status_color: APPLICATION_STATUS_COLOR[item.status] || '#888',
      status_name: this.getStatusName(item.status)
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

  getStatusName(status) {
    const map = { 0: '待审批', 1: '已通过', 2: '已拒绝' };
    return map[status] || '未知';
  },

  loadMore() {
    if (!this.data.hasMore || this.data.loading) return;
    this.setData({ page: this.data.page + 1 });
    this.fetchList();
  },

  approveApplication(e) {
    const { id, title } = e.currentTarget.dataset;
    wx.showModal({
      title: '审批通过',
      content: `确定通过《${title}》的申请吗？`,
      editable: true,
      placeholderText: '请输入审批意见（必填）',
      success: async (res) => {
        if (res.confirm) {
          const comment = res.content?.trim();
          if (!comment) {
            wx.showToast({ title: '请填写审批意见', icon: 'none' });
            return;
          }
          try {
            await put(`/tutor/applications/${id}/approve`, {
              status: 1,
              decision_comment: comment
            }, { showLoading: true });
            wx.showToast({ title: '审批成功', icon: 'success' });
            this.setData({ page: 1, list: [], hasMore: true });
            this.fetchList();
          } catch (err) {
            console.error('审批失败', err);
          }
        }
      }
    });
  },

  rejectApplication(e) {
    const { id, title } = e.currentTarget.dataset;
    wx.showModal({
      title: '审批拒绝',
      content: `确定拒绝《${title}》的申请吗？`,
      editable: true,
      placeholderText: '请输入拒绝理由（至少20字）',
      success: async (res) => {
        if (res.confirm) {
          const comment = res.content?.trim();
          if (!comment || comment.length < 20) {
            wx.showToast({ title: '拒绝理由至少20字', icon: 'none' });
            return;
          }
          try {
            await put(`/tutor/applications/${id}/reject`, {
              status: 2,
              decision_comment: comment
            }, { showLoading: true });
            wx.showToast({ title: '已拒绝', icon: 'success' });
            this.setData({ page: 1, list: [], hasMore: true });
            this.fetchList();
          } catch (err) {
            console.error('操作失败', err);
          }
        }
      }
    });
  }
});
