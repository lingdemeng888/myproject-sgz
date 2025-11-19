const { get, put, post } = require('../../../utils/request');

Page({
  data: {
    users: [],
    total: 0,
    page: 1,
    pageSize: 20,
    loading: false,
    loadingMore: false,
    hasMore: true,
    
    // 筛选条件
    roleOptions: [
      { label: '全部角色', value: '' },
      { label: '学生', value: 'STUDENT' },
      { label: '导师', value: 'TUTOR' },
      { label: '管理员', value: 'ADMIN' }
    ],
    roleFilterIndex: 0,
    statusOptions: [
      { label: '全部状态', value: '' },
      { label: '正常', value: '1' },
      { label: '禁用', value: '0' }
    ],
    statusFilterIndex: 0,
    searchKeyword: '',
    
    // 角色分配对话框
    showRoleModal: false,
    currentUser: {},
    selectedRoles: []
  },

  onLoad() {
    this.fetchUsers();
  },

  onPullDownRefresh() {
    this.setData({ page: 1, users: [], hasMore: true });
    this.fetchUsers(true);
  },

  async fetchUsers(fromPullDown = false) {
    if (this.data.loading) return;
    
    this.setData({ loading: true });
    
    try {
      const { page, pageSize, roleFilterIndex, statusFilterIndex, searchKeyword, roleOptions, statusOptions } = this.data;
      
      const params = {
        page,
        page_size: pageSize
      };
      
      // 添加角色筛选
      if (roleFilterIndex > 0) {
        params.role_key = roleOptions[roleFilterIndex].value;
      }
      
      // 添加状态筛选
      if (statusFilterIndex > 0) {
        params.status = parseInt(statusOptions[statusFilterIndex].value);
      }
      
      // 添加关键词搜索
      if (searchKeyword.trim()) {
        params.keyword = searchKeyword.trim();
      }
      
      console.log('[DEBUG] 获取用户列表，参数:', params);
      const result = await get('/admin/users', params, { showLoading: !fromPullDown });
      
      const newUsers = page === 1 ? result.items : [...this.data.users, ...result.items];
      
      this.setData({
        users: newUsers,
        total: result.total,
        hasMore: newUsers.length < result.total
      });
      
    } catch (err) {
      console.error('[ERROR] 获取用户列表失败:', err);
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
    this.fetchUsers();
  },

  onRoleFilterChange(e) {
    const index = parseInt(e.detail.value);
    this.setData({ 
      roleFilterIndex: index,
      page: 1,
      users: [],
      hasMore: true
    });
    this.fetchUsers();
  },

  onStatusFilterChange(e) {
    const index = parseInt(e.detail.value);
    this.setData({ 
      statusFilterIndex: index,
      page: 1,
      users: [],
      hasMore: true
    });
    this.fetchUsers();
  },

  onSearchInput(e) {
    this.setData({ searchKeyword: e.detail.value });
  },

  handleSearch() {
    this.setData({ 
      page: 1,
      users: [],
      hasMore: true
    });
    this.fetchUsers();
  },

  refreshList() {
    this.setData({ 
      page: 1,
      users: [],
      hasMore: true
    });
    this.fetchUsers();
  },

  async toggleUserStatus(e) {
    const { id, status } = e.currentTarget.dataset;
    const newStatus = status === 1 ? 0 : 1;
    const statusText = newStatus === 1 ? '启用' : '禁用';
    
    wx.showModal({
      title: '确认操作',
      content: `确定要${statusText}该用户吗？`,
      success: async (res) => {
        if (res.confirm) {
          try {
            await put(`/admin/users/${id}/status`, { status: newStatus });
            wx.showToast({ title: `${statusText}成功`, icon: 'success' });
            
            // 更新本地数据
            const users = this.data.users.map(user => {
              if (user.id === id) {
                return { ...user, status: newStatus };
              }
              return user;
            });
            this.setData({ users });
            
          } catch (err) {
            console.error('[ERROR] 更新用户状态失败:', err);
            wx.showToast({ title: '操作失败', icon: 'none' });
          }
        }
      }
    });
  },

  showRoleDialog(e) {
    const user = e.currentTarget.dataset.user;
    this.setData({
      showRoleModal: true,
      currentUser: user,
      selectedRoles: user.roles || []
    });
  },

  closeRoleDialog() {
    this.setData({ showRoleModal: false });
  },

  stopPropagation() {
    // 阻止事件冒泡
  },

  toggleRole(e) {
    const role = e.currentTarget.dataset.role;
    let selectedRoles = [...this.data.selectedRoles];
    
    const index = selectedRoles.indexOf(role);
    if (index > -1) {
      selectedRoles.splice(index, 1);
    } else {
      selectedRoles.push(role);
    }
    
    this.setData({ selectedRoles });
  },

  async confirmRoleAssignment() {
    const { currentUser, selectedRoles } = this.data;
    
    if (selectedRoles.length === 0) {
      wx.showToast({ title: '请至少选择一个角色', icon: 'none' });
      return;
    }
    
    try {
      await post(`/admin/users/${currentUser.id}/roles`, { roles: selectedRoles });
      wx.showToast({ title: '角色分配成功', icon: 'success' });
      
      // 更新本地数据
      const users = this.data.users.map(user => {
        if (user.id === currentUser.id) {
          return { ...user, roles: selectedRoles };
        }
        return user;
      });
      this.setData({ users, showRoleModal: false });
      
    } catch (err) {
      console.error('[ERROR] 分配角色失败:', err);
      wx.showToast({ title: '操作失败', icon: 'none' });
    }
  },

  viewUserDetail(e) {
    const { id } = e.currentTarget.dataset;
    // 这里可以跳转到用户详情页，暂时显示提示
    wx.showToast({ title: `查看用户 ${id} 详情`, icon: 'none' });
  },

  getRoleLabel(role) {
    const roleMap = {
      'STUDENT': '学生',
      'TUTOR': '导师',
      'ADMIN': '管理员'
    };
    return roleMap[role] || role;
  }
});
