const { get, post } = require('../../../utils/request');

Page({
  data: {
    no: '',
    name: '',
    phone: '',
    email: '',
    pwd1: '',
    pwd2: '',
    deptId: null,
    deptName: '',
    deptOptions: [],
    deptIndex: 0,
    deptLoading: false,
    submitting: false
  },

  onLoad() {
    this.fetchDepartments();
  },

  onFieldInput(e) {
    const { field } = e.currentTarget.dataset;
    if (!field) return;
    this.setData({ [field]: e.detail.value });
  },

  async fetchDepartments() {
    this.setData({ deptLoading: true });
    try {
      const pageSize = 100;
      let page = 1;
      let fetched = [];
      let total = 0;
      while (true) {
        const res = await get(
          '/majors',
          { page, page_size: pageSize, status: 1 },
          { requireAuth: false, autoRedirectOn401: false, showError: false }
        );
        const items = Array.isArray(res?.items) ? res.items : [];
        fetched = fetched.concat(items);
        total = res?.total ?? fetched.length;
        if (items.length < pageSize || fetched.length >= total) {
          break;
        }
        page += 1;
      }

      const map = {};
      fetched.forEach(item => {
        if (item?.department_id && !map[item.department_id]) {
          map[item.department_id] = item.department_name || `院系 #${item.department_id}`;
        }
      });
      const deptOptions = Object.keys(map)
        .map(id => ({ id: Number(id), name: map[id] }))
        .sort((a, b) => a.name.localeCompare(b.name, 'zh-Hans-CN'));
      const nextState = {
        deptOptions,
        deptLoading: false
      };
      if (deptOptions.length && !this.data.deptId) {
        nextState.deptId = deptOptions[0].id;
        nextState.deptName = deptOptions[0].name;
        nextState.deptIndex = 0;
      }
      this.setData(nextState);
    } catch (error) {
      console.error('获取院系列表失败', error);
      this.setData({ deptLoading: false });
      wx.showToast({ title: '无法获取院系列表', icon: 'none' });
    }
  },

  onDeptChange(e) {
    const index = Number(e.detail.value);
    const dept = this.data.deptOptions[index];
    if (!dept) return;
    this.setData({
      deptIndex: index,
      deptId: dept.id,
      deptName: dept.name
    });
  },

  validate() {
    const { no, name, deptId, phone, email, pwd1, pwd2 } = this.data;
    const trimmedNo = no.trim();
    if (!trimmedNo) {
      wx.showToast({ title: '请输入工号', icon: 'none' });
      return false;
    }
    if (trimmedNo.length < 3) {
      wx.showToast({ title: '工号至少3个字符', icon: 'none' });
      return false;
    }
    if (!name.trim()) {
      wx.showToast({ title: '请输入姓名', icon: 'none' });
      return false;
    }
    if (!deptId) {
      wx.showToast({ title: '请选择院系', icon: 'none' });
      return false;
    }
    if (!/^1[3-9]\d{9}$/.test(phone.trim())) {
      wx.showToast({ title: '请输入有效手机号', icon: 'none' });
      return false;
    }
    const emailValue = email.trim();
    if (emailValue && !/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(emailValue)) {
      wx.showToast({ title: '请输入正确的邮箱', icon: 'none' });
      return false;
    }
    if (pwd1.length < 6) {
      wx.showToast({ title: '密码至少6位', icon: 'none' });
      return false;
    }
    if (pwd1 !== pwd2) {
      wx.showToast({ title: '两次密码不一致', icon: 'none' });
      return false;
    }
    return true;
  },

  submit() {
    if (!this.validate()) return;
    const { no, name, phone, email, pwd1, deptId } = this.data;
    const trimmedNo = no.trim();
    const payload = {
      username: trimmedNo,
      real_name: name.trim(),
      teacher_no: trimmedNo,
      phone: phone.trim(),
      password: pwd1,
      department_id: deptId
    };
    if (email.trim()) {
      payload.email = email.trim();
    }
    this.setData({ submitting: true });
    post('/auth/register/tutor', payload, { showLoading: true, requireAuth: false })
      .then(() => {
        wx.showModal({
          title: '注册成功',
          content: '账户已创建，请使用工号作为用户名登录。',
          showCancel: false,
          success: () => {
            this.backToLogin();
          }
        });
      })
      .catch(error => {
        console.error('导师注册失败', error);
      })
      .finally(() => {
        this.setData({ submitting: false });
      });
  },

  backToLogin() {
    wx.navigateBack();
  }
});
