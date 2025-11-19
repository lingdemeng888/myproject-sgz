const { get } = require('../../../utils/request');

Page({
  data: {
    logs: [],
    total: 0,
    page: 1,
    pageSize: 20,
    loading: false,
    loadingMore: false,
    hasMore: true,
    
    // 筛选条件
    actionOptions: [
      { label: '全部操作', value: '' },
      { label: '创建', value: 'CREATE' },
      { label: '更新', value: 'UPDATE' },
      { label: '删除', value: 'DELETE' },
      { label: '登录', value: 'LOGIN' },
      { label: '登出', value: 'LOGOUT' },
      { label: '批准', value: 'APPROVE' },
      { label: '拒绝', value: 'REJECT' },
      { label: '评审', value: 'REVIEW' }
    ],
    actionFilterIndex: 0,
    
    resourceOptions: [
      { label: '全部资源', value: '' },
      { label: '用户', value: 'user' },
      { label: '系部', value: 'department' },
      { label: '专业', value: 'major' },
      { label: '选题', value: 'topic' },
      { label: '申请', value: 'application' },
      { label: '论文', value: 'paper' }
    ],
    resourceFilterIndex: 0,
    
    startDate: '',
    endDate: ''
  },

  onLoad() {
    this.fetchLogs();
  },

  onPullDownRefresh() {
    this.setData({ page: 1, logs: [], hasMore: true });
    this.fetchLogs(true);
  },

  async fetchLogs(fromPullDown = false) {
    if (this.data.loading) return;
    
    this.setData({ loading: true });
    
    try {
      const { page, pageSize, actionFilterIndex, resourceFilterIndex, startDate, endDate, actionOptions, resourceOptions } = this.data;
      
      const params = {
        page,
        page_size: pageSize
      };
      
      // 添加操作类型筛选
      if (actionFilterIndex > 0) {
        params.action = actionOptions[actionFilterIndex].value;
      }
      
      // 添加资源类型筛选
      if (resourceFilterIndex > 0) {
        params.resource_type = resourceOptions[resourceFilterIndex].value;
      }
      
      // 添加时间范围筛选
      if (startDate) {
        params.start_time = new Date(startDate + ' 00:00:00').toISOString();
      }
      if (endDate) {
        params.end_time = new Date(endDate + ' 23:59:59').toISOString();
      }
      
      console.log('[DEBUG] 获取日志列表，参数:', params);
      const result = await get('/admin/logs', params, { showLoading: !fromPullDown });
      
      const newLogs = page === 1 ? result.items : [...this.data.logs, ...result.items];
      
      this.setData({
        logs: newLogs,
        total: result.total,
        hasMore: newLogs.length < result.total
      });
      
    } catch (err) {
      console.error('[ERROR] 获取日志列表失败:', err);
      wx.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      this.setData({ loading: false, loadingMore: false });
      if (fromPullDown) {
        wx.stopPullDownRefresh();
      }
    }
  },

  loadMore() {
    if (this.data.loadingMore || !this.data.hasMore) return;
    
    this.setData({ 
      page: this.data.page + 1,
      loadingMore: true 
    });
    this.fetchLogs();
  },

  onActionFilterChange(e) {
    const index = parseInt(e.detail.value);
    this.setData({ 
      actionFilterIndex: index,
      page: 1,
      logs: [],
      hasMore: true
    });
    this.fetchLogs();
  },

  onResourceFilterChange(e) {
    const index = parseInt(e.detail.value);
    this.setData({ 
      resourceFilterIndex: index,
      page: 1,
      logs: [],
      hasMore: true
    });
    this.fetchLogs();
  },

  onStartDateChange(e) {
    this.setData({ 
      startDate: e.detail.value,
      page: 1,
      logs: [],
      hasMore: true
    });
    this.fetchLogs();
  },

  onEndDateChange(e) {
    this.setData({ 
      endDate: e.detail.value,
      page: 1,
      logs: [],
      hasMore: true
    });
    this.fetchLogs();
  },

  clearFilters() {
    this.setData({
      actionFilterIndex: 0,
      resourceFilterIndex: 0,
      startDate: '',
      endDate: '',
      page: 1,
      logs: [],
      hasMore: true
    });
    this.fetchLogs();
  },

  refreshList() {
    this.setData({ 
      page: 1,
      logs: [],
      hasMore: true
    });
    this.fetchLogs();
  },

  formatDate(value) {
    if (!value) return '';
    // 处理 ISO 格式的时间字符串
    const date = new Date(value);
    if (isNaN(date.getTime())) return value;
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    const hh = String(date.getHours()).padStart(2, '0');
    const mm = String(date.getMinutes()).padStart(2, '0');
    return `${y}-${m}-${d} ${hh}:${mm}`;
  },

  getActionLabel(action) {
    const actionMap = {
      'CREATE': '创建',
      'UPDATE': '更新',
      'DELETE': '删除',
      'LOGIN': '登录',
      'LOGOUT': '登出',
      'APPROVE': '批准',
      'REJECT': '拒绝',
      'REVIEW': '评审'
    };
    return actionMap[action] || action;
  },

  getActionClass(action) {
    const classMap = {
      'CREATE': 'create',
      'UPDATE': 'update',
      'DELETE': 'delete',
      'LOGIN': 'login',
      'LOGOUT': 'logout',
      'APPROVE': 'approve',
      'REJECT': 'reject',
      'REVIEW': 'review'
    };
    return classMap[action] || 'default';
  },

  getResourceLabel(resourceType) {
    const resourceMap = {
      'user': '用户',
      'department': '系部',
      'major': '专业',
      'topic': '选题',
      'application': '申请',
      'paper': '论文'
    };
    return resourceMap[resourceType] || resourceType;
  }
});
