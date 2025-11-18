const { ensureStudent } = require('../../../utils/auth');
const { get, post } = require('../../../utils/request');
const { APPLICATION_STATUS_TEXT, APPLICATION_STATUS_COLOR } = require('../../../utils/constants');

Page({
  data: {
    topicId: null,
    detail: null,
    termName: '',
    reason: '',
    submitting: false,
    applicationStatus: {
      text: '未申请',
      color: '#666',
      desc: '尚未提交申请，可直接填写申请理由后提交。'
    },
    canApply: true
  },

  onLoad(options) {
    if (options?.id) {
      this.setData({ topicId: Number(options.id) });
    }
  },

  onShow() {
    if (!ensureStudent()) return;
    if (this.data.topicId) {
      this.loadDetail();
      this.loadApplicationStatus();
    }
  },

  async loadDetail() {
    try {
      const detail = await get(`/topics/${this.data.topicId}`, {}, { showLoading: true });
      this.setData({
        detail,
        termName: this.formatTerm(detail?.term)
      });
    } catch (err) {
      console.error('获取选题详情失败', err);
    }
  },

  async loadApplicationStatus() {
    try {
      const res = await get('/student/topics/applications', { page: 1, page_size: 50 }, { showLoading: false });
      const record = (res?.items || []).find(item => item.topic_id === this.data.topicId);
      const status = this.buildStatus(record);
      this.setData({
        applicationStatus: status,
        canApply: status.canApply
      });
    } catch (err) {
      console.error('获取申请状态失败', err);
    }
  },

  buildStatus(record) {
    if (!record) {
      return {
        text: '未申请',
        color: '#666',
        desc: '尚未提交申请，可直接填写申请理由后提交。',
        canApply: true
      };
    }
    const text = record.status_name || APPLICATION_STATUS_TEXT[record.status] || '未知状态';
    const color = APPLICATION_STATUS_COLOR[record.status] || '#888';
    let desc = `申请时间：${this.formatDate(record.created_at)}`;
    if (record.decision_comment) {
      desc += `\n导师意见：${record.decision_comment}`;
    }
    let canApply = false;
    if (record.status === 2 || record.status === 3) {
      desc += '\n可重新提交申请。';
      canApply = true;
    }
    if (record.status === 1) {
      desc += '\n该选题已通过，不可重复申请。';
    }
    if (record.status === 0) {
      desc += '\n导师尚未审批，请耐心等待。';
    }
    return { text, color, desc, canApply };
  },

  onReasonInput(e) {
    this.setData({ reason: e.detail.value });
  },

  validateReason() {
    const reason = this.data.reason.trim();
    if (reason.length < 10) {
      wx.showToast({ title: '理由至少10个字', icon: 'none' });
      return false;
    }
    if (reason.length > 500) {
      wx.showToast({ title: '理由不超过500字', icon: 'none' });
      return false;
    }
    return true;
  },

  async submitApplication() {
    if (!this.data.canApply) return;
    if (!this.validateReason()) return;
    this.setData({ submitting: true });
    try {
      await post('/student/topics/applications', {
        topic_id: this.data.topicId,
        application_reason: this.data.reason.trim()
      }, { showLoading: true });
      wx.showToast({ title: '申请已提交', icon: 'success' });
      this.setData({ reason: '' });
      this.loadApplicationStatus();
    } catch (err) {
      console.error('申请失败', err);
    } finally {
      this.setData({ submitting: false });
    }
  },

  formatDate(value) {
    if (!value) return '-';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  },

  formatTerm(term) {
    if (term === 1) return '上学期';
    if (term === 2) return '下学期';
    return '未知学期';
  }
});
