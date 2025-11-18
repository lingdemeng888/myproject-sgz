const { ensureStudent } = require('../../../utils/auth');
const { get } = require('../../../utils/request');
const { PAPER_STATUS_COLOR, PAPER_STATUS_TEXT } = require('../../../utils/constants');

Page({
  data: {
    filters: {
      academic_year: '',
      term: null,
      status: null
    },
    termOptions: [
      { label: '学期不限', value: null },
      { label: '上学期', value: 1 },
      { label: '下学期', value: 2 }
    ],
    termIndex: 0,
    statusOptions: [
      { label: '状态不限', value: null },
      { label: '编辑中', value: 0 },
      { label: '已提交', value: 1 },
      { label: '评审中', value: 2 },
      { label: '待修改', value: 3 },
      { label: '已通过', value: 4 },
      { label: '已归档', value: 5 }
    ],
    statusIndex: 0,
    papers: [],
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
    this.fetchPapers();
  },

  onYearInput(e) {
    this.setData({ 'filters.academic_year': e.detail.value });
  },

  onTermChange(e) {
    const index = Number(e.detail.value);
    this.setData({
      termIndex: index,
      'filters.term': this.data.termOptions[index].value
    });
  },

  onStatusChange(e) {
    const index = Number(e.detail.value);
    this.setData({
      statusIndex: index,
      'filters.status': this.data.statusOptions[index].value
    });
  },

  applyFilters() {
    this.refresh();
  },

  refresh() {
    this.setData({ papers: [], page: 1, hasMore: true });
    this.fetchPapers(true);
  },

  async fetchPapers(showLoading = false) {
    if (!this.data.hasMore || this.data.loading) return;
    this.setData({ loading: true });
    const params = {
      page: this.data.page,
      page_size: this.data.pageSize
    };
    const { academic_year, term, status } = this.data.filters;
    if (academic_year) params.academic_year = academic_year.trim();
    if (Number.isInteger(term)) params.term = term;
    if (Number.isInteger(status)) params.status = status;

    try {
      const res = await get('/student/papers', params, { showLoading });
      const items = res?.items || [];
      const decorated = items.map(item => ({
        ...item,
        term_name: item.term_name || this.formatTerm(item.term),
        status_color: PAPER_STATUS_COLOR[item.status] || '#666'
      }));
      const list = [...this.data.papers, ...decorated];
      const total = res?.total || list.length;
      this.setData({
        papers: list,
        page: this.data.page + 1,
        hasMore: list.length < total
      });
    } catch (err) {
      console.error('获取论文列表失败', err);
    } finally {
      this.setData({ loading: false });
      wx.stopPullDownRefresh();
    }
  },

  formatTerm(term) {
    if (term === 1) return '上学期';
    if (term === 2) return '下学期';
    return '未知学期';
  },

  goDetail(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({ url: `/pages/student/paper-detail/index?id=${id}` });
  }
});
