const { ensureTutor } = require('../../../utils/auth');
const { get } = require('../../../utils/request');
const { PAPER_STATUS_COLOR } = require('../../../utils/constants');

Page({
  data: {
    studentName: '',
    academicYear: '',
    list: [],
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false
  },

  onLoad() {
    if (!ensureTutor()) return;
    this.fetchList();
  },

  onPullDownRefresh() {
    this.setData({ page: 1, list: [], hasMore: true });
    this.fetchList(true);
  },

  onStudentNameInput(e) {
    this.setData({ studentName: e.detail.value });
  },

  onYearInput(e) {
    this.setData({ academicYear: e.detail.value });
  },

  applyFilter() {
    this.setData({ page: 1, list: [], hasMore: true });
    this.fetchList();
  },

  resetFilter() {
    this.setData({
      studentName: '',
      academicYear: '',
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
      if (this.data.studentName) {
        params.student_name = this.data.studentName;
      }
      if (this.data.academicYear) {
        params.academic_year = this.data.academicYear;
      }

      const res = await get('/tutor/papers', params, { showLoading: !fromPullDown });
      
      if (!res || typeof res !== 'object') {
        console.error('响应数据格式错误:', res);
        throw new Error('数据格式错误');
      }
      
      const items = Array.isArray(res.items) ? res.items : [];
      const decoratedList = this.decorateList(items);
      
      this.setData({
        list: this.data.page === 1 ? decoratedList : [...this.data.list, ...decoratedList],
        hasMore: items.length >= this.data.pageSize
      });
    } catch (err) {
      console.error('获取论文列表失败', err);
      wx.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      this.setData({ loading: false });
      if (fromPullDown) {
        wx.stopPullDownRefresh();
      }
    }
  },

  decorateList(items) {
    return items.map(item => {
      try {
        return {
          ...item,
          term_name: this.formatTerm(item.term),
          status_color: PAPER_STATUS_COLOR[item.status] || '#666',
          status_name: item.status_name || this.getStatusName(item.status)
        };
      } catch (err) {
        console.error('装饰论文数据失败:', item, err);
        return item;
      }
    });
  },

  formatTerm(term) {
    if (term === 1) return '上学期';
    if (term === 2) return '下学期';
    return '';
  },

  getStatusName(status) {
    const map = {
      0: '草稿',
      1: '已提交',
      2: '评审中',
      3: '待修改',
      4: '已通过'
    };
    return map[status] || '未知';
  },

  loadMore() {
    if (!this.data.hasMore || this.data.loading) return;
    this.setData({ page: this.data.page + 1 });
    this.fetchList();
  },

  goDetail(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({ url: `/pages/tutor/paper-detail/index?id=${id}` });
  }
});
