const { ensureStudent } = require('../../../utils/auth');
const { post } = require('../../../utils/request');

Page({
  data: {
    paperId: null,
    content: '',
    notes: '',
    formatOptions: [
      { label: '纯文本', value: 3 },
      { label: 'Markdown', value: 1 },
      { label: 'HTML', value: 2 },
      { label: '无格式', value: 0 }
    ],
    formatIndex: 0,
    saving: false
  },

  onLoad(options) {
    if (options?.paperId) {
      this.setData({ paperId: Number(options.paperId) });
    }
  },

  onShow() {
    ensureStudent();
  },

  onContentInput(e) {
    this.setData({ content: e.detail.value });
  },

  onNotesInput(e) {
    this.setData({ notes: e.detail.value });
  },

  onFormatChange(e) {
    this.setData({ formatIndex: Number(e.detail.value) });
  },

  async saveVersion() {
    if (!this.data.paperId) {
      wx.showToast({ title: '缺少论文ID', icon: 'none' });
      return;
    }
    const content = this.data.content.trim();
    if (content.length < 20) {
      wx.showToast({ title: '正文不少于20字', icon: 'none' });
      return;
    }
    this.setData({ saving: true });
    try {
      await post(`/student/papers/${this.data.paperId}/versions`, {
        content_text: content,
        content_format: this.data.formatOptions[this.data.formatIndex].value,
        notes: this.data.notes.trim() || undefined
      }, { showLoading: true });
      wx.showToast({ title: '版本已保存', icon: 'success' });
      setTimeout(() => {
        wx.navigateBack();
      }, 800);
    } catch (err) {
      console.error('保存论文版本失败', err);
    } finally {
      this.setData({ saving: false });
    }
  }
});
