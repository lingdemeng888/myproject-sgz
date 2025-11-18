const { ensureTutor } = require('../../../utils/auth');
const { get, put } = require('../../../utils/request');
const { TOPIC_STATUS_TEXT, TOPIC_STATUS_COLOR } = require('../../../utils/constants');

Page({
  data: {
    topics: [],
    keyword: '',
    statusFilter: null,
    page: 1,
    pageSize: 10,
    total: 0,
    loading: false,
    hasMore: true
  },

  onLoad(options) {
    const user = ensureTutor();
    if (!user) return;
  },

  onShow() {
    // 每次显示时重新加载数据
    this.resetAndLoad();
  },

  onPullDownRefresh() {
    this.resetAndLoad(true);
  },

  // 重置数据并加载
  resetAndLoad(fromPullDown = false) {
    this.setData({
      topics: [],
      page: 1,
      hasMore: true
    });
    this.loadTopics(fromPullDown);
  },

  // 加载选题列表
  async loadTopics(fromPullDown = false) {
    if (this.data.loading || !this.data.hasMore) return;

    this.setData({ loading: true });

    try {
      const params = {
        page: this.data.page,
        page_size: this.data.pageSize
      };

      if (this.data.keyword) {
        params.keyword = this.data.keyword;
      }

      if (this.data.statusFilter !== null) {
        params.status = this.data.statusFilter;
      }

      const result = await get('/tutor/topics', params, { showLoading: !fromPullDown });

      const decoratedTopics = this.decorateTopics(result.items || []);

      this.setData({
        topics: this.data.page === 1 ? decoratedTopics : [...this.data.topics, ...decoratedTopics],
        total: result.total || 0,
        hasMore: decoratedTopics.length >= this.data.pageSize
      });
    } catch (err) {
      console.error('加载选题列表失败:', err);
      wx.showToast({ title: '加载失败，请重试', icon: 'none' });
    } finally {
      this.setData({ loading: false });
      if (fromPullDown) {
        wx.stopPullDownRefresh();
      }
    }
  },

  // 装饰选题数据
  decorateTopics(list) {
    return list.map(item => ({
      ...item,
      status_name: TOPIC_STATUS_TEXT[item.status] || '未知',
      status_color: TOPIC_STATUS_COLOR[item.status] || '#999',
      created_at_fmt: this.formatDate(item.created_at)
    }));
  },

  // 格式化日期
  formatDate(value) {
    if (!value) return '-';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  },

  // 关键词输入
  onKeywordInput(e) {
    this.setData({ keyword: e.detail.value });
  },

  // 搜索
  onSearch() {
    this.resetAndLoad();
  },

  // 状态筛选
  filterByStatus(e) {
    const status = e.currentTarget.dataset.status;
    this.setData({ statusFilter: status });
    this.resetAndLoad();
  },

  // 加载更多
  loadMore() {
    if (this.data.hasMore && !this.data.loading) {
      this.setData({ page: this.data.page + 1 });
      this.loadTopics();
    }
  },

  // 发布选题
  goCreateTopic() {
    wx.navigateTo({ url: '/pages/tutor/topic-edit/index' });
  },

  // 查看选题详情
  goTopicDetail(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({ url: `/pages/tutor/topic-detail/index?id=${id}` });
  },

  // 编辑选题
  editTopic(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({ url: `/pages/tutor/topic-edit/index?id=${id}` });
  },

  // 发布选题
  async publishTopic(e) {
    const { id } = e.currentTarget.dataset;
    
    const res = await wx.showModal({
      title: '确认发布',
      content: '发布后学生即可申请该选题，确认发布吗？'
    });

    if (!res.confirm) return;

    try {
      await put(`/tutor/topics/${id}/publish`, {}, { showLoading: true });
      wx.showToast({ title: '发布成功', icon: 'success' });
      this.resetAndLoad();
    } catch (err) {
      console.error('发布失败:', err);
    }
  },

  // 锁定选题
  async lockTopic(e) {
    const { id } = e.currentTarget.dataset;
    
    const res = await wx.showModal({
      title: '确认锁定',
      content: '锁定后学生将无法申请该选题，确认锁定吗？'
    });

    if (!res.confirm) return;

    try {
      await put(`/tutor/topics/${id}/lock`, {}, { showLoading: true });
      wx.showToast({ title: '锁定成功', icon: 'success' });
      this.resetAndLoad();
    } catch (err) {
      console.error('锁定失败:', err);
    }
  },

  // 归档选题
  async archiveTopic(e) {
    const { id } = e.currentTarget.dataset;
    
    const res = await wx.showModal({
      title: '确认归档',
      content: '归档后该选题将不再显示在列表中，确认归档吗？'
    });

    if (!res.confirm) return;

    try {
      await put(`/tutor/topics/${id}/archive`, {}, { showLoading: true });
      wx.showToast({ title: '归档成功', icon: 'success' });
      this.resetAndLoad();
    } catch (err) {
      console.error('归档失败:', err);
    }
  }
});
