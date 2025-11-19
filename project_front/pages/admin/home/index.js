const { ensureAdmin, logout } = require('../../../utils/auth');
const { get } = require('../../../utils/request');

Page({
  data: {
    userInfo: {},
    stats: {},
    recentLogs: [],
    loading: false
  },

  onShow() {
    const user = ensureAdmin();
    if (!user) return;
    
    this.setData({ userInfo: user });
    this.fetchOverview();
  },

  onPullDownRefresh() {
    this.fetchOverview(true);
  },

  async fetchOverview(fromPullDown = false) {
    this.setData({ loading: true });
    try {
      console.log('[DEBUG] 开始获取管理员工作台数据...');
      
      // 获取用户列表统计
      let usersData, departmentsData, majorsData, logsData;
      
      try {
        usersData = await get('/admin/users', { page: 1, page_size: 1 }, { showLoading: !fromPullDown });
      } catch (err) {
        console.warn('[WARN] 用户列表获取失败:', err);
        usersData = { total: 0, items: [] };
      }
      
      try {
        departmentsData = await get('/departments', { page: 1, page_size: 1 }, { showLoading: false });
      } catch (err) {
        console.warn('[WARN] 系部列表获取失败:', err);
        departmentsData = { total: 0, items: [] };
      }
      
      try {
        majorsData = await get('/majors', { page: 1, page_size: 1 }, { showLoading: false });
      } catch (err) {
        console.warn('[WARN] 专业列表获取失败:', err);
        majorsData = { total: 0, items: [] };
      }
      
      try {
        // 获取最近日志
        const today = new Date();
        const startOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate());
        const start_time = startOfDay.toISOString();
        logsData = await get('/admin/logs', { 
          page: 1, 
          page_size: 10,
          start_time 
        }, { showLoading: false });
      } catch (err) {
        console.warn('[WARN] 操作日志获取失败:', err);
        logsData = { total: 0, items: [] };
      }

      // 计算各角色用户数（需要遍历用户列表）
      let roleStats = { student_count: 0, tutor_count: 0, admin_count: 0 };
      try {
        const allUsers = await get('/admin/users', { page: 1, page_size: 100 }, { showLoading: false });
        if (allUsers && allUsers.items) {
          allUsers.items.forEach(user => {
            if (user.roles && user.roles.includes('STUDENT')) roleStats.student_count++;
            if (user.roles && user.roles.includes('TUTOR')) roleStats.tutor_count++;
            if (user.roles && user.roles.includes('ADMIN')) roleStats.admin_count++;
          });
        }
      } catch (err) {
        console.warn('[WARN] 角色统计失败:', err);
      }

      const stats = {
        total_users: usersData?.total || 0,
        total_departments: departmentsData?.total || 0,
        total_majors: majorsData?.total || 0,
        recent_logs: logsData?.total || 0,
        ...roleStats
      };

      this.setData({
        stats,
        recentLogs: this.decorateLogs(logsData?.items || [])
      });
    } catch (err) {
      console.error('[ERROR] 概览数据获取失败:', err);
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

  decorateLogs(list) {
    return list.map(item => ({
      ...item,
      created_at_fmt: this.formatDate(item.created_at),
      action_name: this.formatAction(item.action)
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

  formatAction(action) {
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

  refreshData() {
    this.fetchOverview();
  },

  goUsers() {
    wx.navigateTo({ url: '/pages/admin/users/index' });
  },

  goDepartments() {
    wx.navigateTo({ url: '/pages/admin/departments/index' });
  },

  goMajors() {
    wx.navigateTo({ url: '/pages/admin/majors/index' });
  },

  goLogs() {
    wx.navigateTo({ url: '/pages/admin/logs/index' });
  },

  handleLogout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          logout();
          wx.reLaunch({ url: '/pages/auth/identity/index' });
        }
      }
    });
  }
});
