const { ensureStudent } = require('../../../utils/auth');
const { get, put } = require('../../../utils/request');
const { PAPER_STATUS_COLOR } = require('../../../utils/constants');

Page({
  data: {
    paperId: null,
    paper: null,
    canSubmit: false,
    submitting: false
  },

  onLoad(options) {
    if (options?.id) {
      this.setData({ paperId: Number(options.id) });
    }
  },

  onShow() {
    if (!ensureStudent()) return;
    if (this.data.paperId) {
      this.fetchPaper();
    }
  },

  async fetchPaper() {
    try {
      const paper = await get(`/student/papers/${this.data.paperId}`, {}, { showLoading: true });
      const decorated = this.decoratePaper(paper);
      this.setData({
        paper: decorated,
        canSubmit: this.canSubmitPaper(decorated)
      });
    } catch (err) {
      console.error('获取论文详情失败', err);
    }
  },

  decoratePaper(paper) {
    if (!paper) return null;
    const formatTime = (value) => {
      if (!value) return '';
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return value;
      const y = date.getFullYear();
      const m = String(date.getMonth() + 1).padStart(2, '0');
      const d = String(date.getDate()).padStart(2, '0');
      const hh = String(date.getHours()).padStart(2, '0');
      const mm = String(date.getMinutes()).padStart(2, '0');
      return `${y}-${m}-${d} ${hh}:${mm}`;
    };
    return {
      ...paper,
      term_name: paper.term_name || (paper.term === 1 ? '上学期' : paper.term === 2 ? '下学期' : '未知学期'),
      status_color: PAPER_STATUS_COLOR[paper.status] || '#666',
      submitted_at_fmt: formatTime(paper.submitted_at),
      created_at_fmt: formatTime(paper.created_at),
      versions: (paper.versions || []).map(v => ({
        ...v,
        submitted_at_fmt: formatTime(v.submitted_at)
      }))
    };
  },

  canSubmitPaper(paper) {
    if (!paper) return false;
    return paper.status === 0 && paper.versions && paper.versions.length > 0;
  },

  goAddVersion() {
    wx.navigateTo({ url: `/pages/student/paper-version-edit/index?paperId=${this.data.paperId}` });
  },

  submitPaper() {
    if (!this.data.canSubmit || !this.data.paperId) return;
    wx.showModal({
      title: '提交确认',
      content: '提交后将进入导师评审流程，期间不可修改。确定要提交吗？',
      success: (res) => {
        if (res.confirm) {
          this.doSubmitPaper();
        }
      }
    });
  },

  async doSubmitPaper() {
    this.setData({ submitting: true });
    try {
      const updated = await put(`/student/papers/${this.data.paperId}/submit`, {}, { showLoading: true });
      const decorated = this.decoratePaper(updated);
      this.setData({
        paper: decorated,
        canSubmit: this.canSubmitPaper(decorated)
      });
      wx.showToast({ title: '提交成功', icon: 'success' });
    } catch (err) {
      console.error('提交论文失败', err);
    } finally {
      this.setData({ submitting: false });
    }
  }
});
