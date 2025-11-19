const { get, post, put, del } = require('../../../utils/request');

Page({
  data: {
    departments: [],
    total: 0,
    loading: false,
    
    // 对话框
    showModal: false,
    isEdit: false,
    formData: {
      id: null,
      name: '',
      code: '',
      description: ''
    }
  },

  onLoad() {
    this.fetchDepartments();
  },

  onPullDownRefresh() {
    this.fetchDepartments(true);
  },

  async fetchDepartments(fromPullDown = false) {
    if (this.data.loading) return;
    
    this.setData({ loading: true });
    
    try {
      console.log('[DEBUG] 获取系部列表...');
      const result = await get('/departments', { 
        page: 1, 
        page_size: 100 
      }, { showLoading: !fromPullDown });
      
      this.setData({
        departments: result.items || [],
        total: result.total || 0
      });
      
    } catch (err) {
      console.error('[ERROR] 获取系部列表失败:', err);
      wx.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      this.setData({ loading: false });
      if (fromPullDown) {
        wx.stopPullDownRefresh();
      }
    }
  },

  refreshList() {
    this.fetchDepartments();
  },

  showAddDialog() {
    this.setData({
      showModal: true,
      isEdit: false,
      formData: {
        id: null,
        name: '',
        code: '',
        description: ''
      }
    });
  },

  showEditDialog(e) {
    const item = e.currentTarget.dataset.item;
    this.setData({
      showModal: true,
      isEdit: true,
      formData: {
        id: item.id,
        name: item.name,
        code: item.code || '',
        description: item.description || ''
      }
    });
  },

  closeDialog() {
    this.setData({ showModal: false });
  },

  stopPropagation() {
    // 阻止事件冒泡
  },

  onNameInput(e) {
    this.setData({ 'formData.name': e.detail.value });
  },

  onCodeInput(e) {
    this.setData({ 'formData.code': e.detail.value });
  },

  onDescInput(e) {
    this.setData({ 'formData.description': e.detail.value });
  },

  async confirmSave() {
    const { formData, isEdit } = this.data;
    
    // 验证必填字段
    if (!formData.name || !formData.name.trim()) {
      wx.showToast({ title: '请输入系部名称', icon: 'none' });
      return;
    }
    
    try {
      const data = {
        name: formData.name.trim(),
        dept_code: formData.code.trim() || formData.name.trim(),
        status: 1
      };
      
      if (isEdit) {
        // 编辑系部
        await put(`/departments/${formData.id}`, data);
        wx.showToast({ title: '更新成功', icon: 'success' });
      } else {
        // 新增系部
        await post('/departments', data);
        wx.showToast({ title: '新增成功', icon: 'success' });
      }
      
      this.setData({ showModal: false });
      this.fetchDepartments();
      
    } catch (err) {
      console.error('[ERROR] 保存系部失败:', err);
      wx.showToast({ title: '保存失败', icon: 'none' });
    }
  },

  deleteDepartment(e) {
    const { id, name } = e.currentTarget.dataset;
    
    wx.showModal({
      title: '确认删除',
      content: `确定要删除系部"${name}"吗？此操作不可恢复。`,
      success: async (res) => {
        if (res.confirm) {
          try {
            await del(`/departments/${id}`);
            wx.showToast({ title: '删除成功', icon: 'success' });
            this.fetchDepartments();
          } catch (err) {
            console.error('[ERROR] 删除系部失败:', err);
            wx.showToast({ title: '删除失败', icon: 'none' });
          }
        }
      }
    });
  },

  formatDate(value) {
    if (!value) return '-';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  }
});
