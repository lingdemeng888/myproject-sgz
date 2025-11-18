const { ensureStudent } = require('../../../utils/auth');
const { get } = require('../../../utils/request');

Page({
  data: {
    keyword: '',
    topics: [],
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false,
    userMajorId: null
  },
  loaded: false,

  onShow() {
    const user = ensureStudent();
    if (!user) return;
    if (!this.loaded) {
      this.setData({ userMajorId: user.primary_major_id || null });
      this.loaded = true;
      this.refreshList();
    }
  },

  onPullDownRefresh() {
    this.refreshList();
  },

  onReachBottom() {
    this.fetchTopics();
  },

  onKeywordInput(e) {
    this.setData({ keyword: e.detail.value });
  },

  onSearch() {
    this.refreshList();
  },

  refreshList() {
    this.setData({ topics: [], page: 1, hasMore: true });
    this.fetchTopics(true);
  },

  async fetchTopics(showLoading = false) {
    if (!this.data.hasMore || this.data.loading) return;
    this.setData({ loading: true });
    const params = {
      page: this.data.page,
      page_size: this.data.pageSize,
      keyword: this.data.keyword.trim() || undefined,
      major_id: this.data.userMajorId || undefined
    };
    try {
      const res = await get('/student/topics', params, { showLoading });
      const items = res?.items || [];
      const decorated = items.map(item => ({
        ...item,
        term_name: this.formatTerm(item.term)
      }));
      const newList = [...this.data.topics, ...decorated];
      const total = res?.total || newList.length;
      this.setData({
        topics: newList,
        page: this.data.page + 1,
        hasMore: newList.length < total
      });
    } catch (err) {
      console.error('获取选题列表失败', err);
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
    wx.navigateTo({ url: `/pages/student/topic-detail/index?id=${id}` });
  }
});
