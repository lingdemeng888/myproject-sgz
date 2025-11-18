const { get, post } = require('../../../utils/request');

Page({
  data: {
    no: '',
    name: '',
    phone: '',
    email: '',
    pwd1: '',
    pwd2: '',
    primaryMajorId: null,
    selectedMajorName: '',
    majorOptions: [],
    majorIndex: 0,
    majorsLoading: false,
    submitting: false
  },

  onLoad() {
    this.fetchMajors();
  },

  onFieldInput(e) {
    const { field } = e.currentTarget.dataset;
    if (!field) return;
    this.setData({ [field]: e.detail.value });
  },

  async fetchMajors() {
    this.setData({ majorsLoading: true });
    try {
      const res = await get(
        '/majors',
        { page: 1, page_size: 100, status: 1 },
        { showLoading: false, showError: false, requireAuth: false, autoRedirectOn401: false }
      );
      const options = Array.isArray(res?.items) ? res.items : [];
      const nextState = {
        majorOptions: options,
        majorsLoading: false
      };
      if (!this.data.primaryMajorId && options.length > 0) {
        nextState.primaryMajorId = options[0].id;
        nextState.selectedMajorName = options[0].name;
        nextState.majorIndex = 0;
      }
      this.setData(nextState);
    } catch (error) {
      console.error('获取专业列表失败', error);
      this.setData({ majorsLoading: false });
      wx.showToast({ title: '无法获取专业列表', icon: 'none' });
    }
  },

  onMajorChange(e) {
    const index = Number(e.detail.value);
    const major = this.data.majorOptions[index];
    if (!major) return;
    this.setData({
      majorIndex: index,
      primaryMajorId: major.id,
      selectedMajorName: major.name
    });
  },

  validate() {
    const { no, name, phone, email, pwd1, pwd2, primaryMajorId } = this.data;
    if (!no.trim()) {
      wx.showToast({ title: '请输入学号', icon: 'none' });
      return false;
    }
    if (!name.trim()) {
      wx.showToast({ title: '请输入姓名', icon: 'none' });
      return false;
    }
    if (!/^1[3-9]\d{9}$/.test(phone.trim())) {
      wx.showToast({ title: '请输入有效手机号', icon: 'none' });
      return false;
    }
    const mail = email.trim();
    if (!mail) {
      wx.showToast({ title: '请输入邮箱', icon: 'none' });
      return false;
    }
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailPattern.test(mail)) {
      wx.showToast({ title: '请输入有效邮箱', icon: 'none' });
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
    if (!primaryMajorId) {
      wx.showToast({ title: '请选择专业', icon: 'none' });
      return false;
    }
    return true;
  },

  submit() {
    if (!this.validate()) return;
    const { no, name, phone, email, pwd1, primaryMajorId } = this.data;
    const trimmedNo = no.trim();
    const payload = {
      username: trimmedNo,
      real_name: name.trim(),
      student_no: trimmedNo,
      phone: phone.trim(),
      email: email.trim(),
      password: pwd1,
      primary_major_id: primaryMajorId
    };
    this.setData({ submitting: true });
    post('/auth/register/student', payload, { showLoading: true })
      .then(() => {
        wx.showModal({
          title: '注册成功',
          content: '账户已创建，请使用学号作为用户名登录。',
          showCancel: false,
          success: () => {
            this.backToLogin();
          }
        });
      })
      .catch(error => {
        console.error('学生注册失败', error);
      })
      .finally(() => {
        this.setData({ submitting: false });
      });
  },

  backToLogin() {
    wx.navigateBack();
  }
});
