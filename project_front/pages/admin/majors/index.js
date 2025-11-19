const { get, post, put, del } = require('../../../utils/request');

Page({
  data: {
    majors: [],
    departments: [],
    total: 0,
    loading: false,
    
    // 筛选
    departmentOptions: [{ label: '全部系部', value: '' }],
    deptFilterIndex: 0,
    
    // 对话框
    showModal: false,
    isEdit: false,
    selectedDeptIndex: -1,
    formData: {
      id: null,
      name: '',
      code: '',
      department_id: null,
      description: ''
    }
  },

  onLoad() {
    this.fetchDepartments();
    this.fetchMajors();
  },

  onPullDownRefresh() {
    this.fetchMajors(true);
  },

  async fetchDepartments() {
    try {
      const result = await get('/departments', { page: 1, page_size: 100 }, { showLoading: false });
      const departments = result.items || [];
      
      const departmentOptions = [
        { label: '全部系部', value: '' },
        ...departments.map(d => ({ label: d.name, value: d.id }))
      ];
      
      this.setData({
        departments,
        departmentOptions
      });
    } catch (err) {
      console.error('[ERROR] 获取系部列表失败:', err);
    }
  },

  async fetchMajors(fromPullDown = false) {
    if (this.data.loading) return;
    
    this.setData({ loading: true });
    
    try {
      const { deptFilterIndex, departmentOptions } = this.data;
      
      const params = {
        page: 1,
        page_size: 1000
      };
      
      // 添加系部筛选
      if (deptFilterIndex > 0) {
        params.department_id = departmentOptions[deptFilterIndex].value;
      }
      
      // 限制最大page_size
      if (params.page_size > 100) {
        params.page_size = 100;
      }
      
      console.log('[DEBUG] 获取专业列表，参数:', params);
      const result = await get('/majors', params, { showLoading: !fromPullDown });
      
      this.setData({
        majors: result.items || [],
        total: result.total || 0
      });
      
    } catch (err) {
      console.error('[ERROR] 获取专业列表失败:', err);
      wx.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      this.setData({ loading: false });
      if (fromPullDown) {
        wx.stopPullDownRefresh();
      }
    }
  },

  onDeptFilterChange(e) {
    const index = parseInt(e.detail.value);
    this.setData({ deptFilterIndex: index });
    this.fetchMajors();
  },

  refreshList() {
    this.fetchMajors();
  },

  showAddDialog() {
    this.setData({
      showModal: true,
      isEdit: false,
      selectedDeptIndex: -1,
      formData: {
        id: null,
        name: '',
        code: '',
        department_id: null,
        description: ''
      }
    });
  },

  showEditDialog(e) {
    const item = e.currentTarget.dataset.item;
    
    // 找到对应的系部索引
    const deptIndex = this.data.departments.findIndex(d => d.id === item.department_id);
    
    this.setData({
      showModal: true,
      isEdit: true,
      selectedDeptIndex: deptIndex,
      formData: {
        id: item.id,
        name: item.name,
        code: item.code || '',
        department_id: item.department_id,
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

  onDeptChange(e) {
    const index = parseInt(e.detail.value);
    const department_id = this.data.departments[index].id;
    this.setData({ 
      selectedDeptIndex: index,
      'formData.department_id': department_id
    });
  },

  async confirmSave() {
    const { formData, isEdit } = this.data;
    
    // 验证必填字段
    if (!formData.name || !formData.name.trim()) {
      wx.showToast({ title: '请输入专业名称', icon: 'none' });
      return;
    }
    
    if (!formData.department_id) {
      wx.showToast({ title: '请选择所属系部', icon: 'none' });
      return;
    }
    
    try {
      const data = {
        name: formData.name.trim(),
        major_code: formData.code.trim() || formData.name.trim(),
        department_id: formData.department_id,
        status: 1
      };
      
      if (isEdit) {
        // 编辑专业
        await put(`/majors/${formData.id}`, data);
        wx.showToast({ title: '更新成功', icon: 'success' });
      } else {
        // 新增专业
        await post('/majors', data);
        wx.showToast({ title: '新增成功', icon: 'success' });
      }
      
      this.setData({ showModal: false });
      this.fetchMajors();
      
    } catch (err) {
      console.error('[ERROR] 保存专业失败:', err);
      wx.showToast({ title: '保存失败', icon: 'none' });
    }
  },

  deleteMajor(e) {
    const { id, name } = e.currentTarget.dataset;
    
    wx.showModal({
      title: '确认删除',
      content: `确定要删除专业"${name}"吗？此操作不可恢复。`,
      success: async (res) => {
        if (res.confirm) {
          try {
            await del(`/majors/${id}`);
            wx.showToast({ title: '删除成功', icon: 'success' });
            this.fetchMajors();
          } catch (err) {
            console.error('[ERROR] 删除专业失败:', err);
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
