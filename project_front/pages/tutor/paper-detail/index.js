const { ensureTutor } = require('../../../utils/auth');
const { get, put } = require('../../../utils/request');
const { PAPER_STATUS_COLOR } = require('../../../utils/constants');

Page({
  data: {
    paper: null,
    versions: [],
    canReview: false,
    showModal: false,
    reviewStatus: null,
    reviewStatusName: '',
    reviewComment: '',
    reviewPlaceholder: '',
    showVersionModal: false,
    currentVersion: null
  },

  onLoad(options) {
    if (!ensureTutor()) return;
    if (options.id) {
      this.fetchDetail(options.id);
    }
  },

  async fetchDetail(id) {
    try {
      const res = await get(`/tutor/papers/${id}`, {}, { showLoading: true });
      const canReview = res.status === 1 || res.status === 2 || res.status === 3;
      
      console.log('论文详情:', res);
      console.log('版本列表:', res.versions);
      
      this.setData({
        paper: {
          ...res,
          term_name: this.formatTerm(res.term),
          status_color: PAPER_STATUS_COLOR[res.status] || '#666',
          status_name: this.getStatusName(res.status)
        },
        versions: this.decorateVersions(res.versions || []),
        canReview
      });
    } catch (err) {
      console.error('获取论文详情失败', err);
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  decorateVersions(versions) {
    return versions.map(v => ({
      ...v,
      created_at_fmt: this.formatDate(v.submitted_at),
      attachments: (v.attachments || []).map(att => ({
        ...att,
        fileSizeText: this.formatFileSize(att.file_size)
      }))
    }));
  },

  formatFileSize(bytes) {
    if (!bytes) return '0B';
    if (bytes < 1024) return bytes + 'B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB';
    return (bytes / (1024 * 1024)).toFixed(1) + 'MB';
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

  formatTerm(term) {
    if (term === 1) return '上学期';
    if (term === 2) return '下学期';
    return '';
  },

  getStatusName(status) {
    const map = {
      0: '草稿',
      1: '已提交',
      2: '评审中',
      3: '待修改',
      4: '已通过'
    };
    return map[status] || '未知';
  },

  showReviewModal(e) {
    const status = Number(e.currentTarget.dataset.status);
    const statusNameMap = { 2: '评审中', 3: '待修改', 4: '通过' };
    const placeholderMap = {
      2: '请输入评审意见（至少20字）',
      3: '请输入修改要求（至少50字）',
      4: '请输入通过意见（至少20字）'
    };

    this.setData({
      showModal: true,
      reviewStatus: status,
      reviewStatusName: statusNameMap[status],
      reviewPlaceholder: placeholderMap[status],
      reviewComment: ''
    });
  },

  hideModal() {
    this.setData({ showModal: false });
  },

  viewVersion(e) {
    const version = e.currentTarget.dataset.version;
    if (!version) return;
    console.log('查看版本:', version);
    console.log('版本附件:', version.attachments);
    this.setData({
      showVersionModal: true,
      currentVersion: version
    });
  },

  hideVersionModal() {
    this.setData({ 
      showVersionModal: false,
      currentVersion: null
    });
  },

  downloadAttachment(e) {
    const { id, name } = e.currentTarget.dataset;
    wx.showLoading({ title: '下载中...', mask: true });
    
    const { getToken } = require('../../../utils/auth');
    const { API_BASE_URL } = require('../../../utils/constants');
    const token = getToken();
    
    wx.downloadFile({
      url: `${API_BASE_URL}/upload/attachment/${id}`,
      header: {
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success(res) {
        wx.hideLoading();
        if (res.statusCode === 200) {
          wx.saveFile({
            tempFilePath: res.tempFilePath,
            success(saveRes) {
              wx.showToast({ title: '下载成功', icon: 'success' });
              wx.openDocument({
                filePath: saveRes.savedFilePath,
                showMenu: true
              });
            },
            fail() {
              wx.showToast({ title: '保存失败', icon: 'none' });
            }
          });
        } else {
          wx.showToast({ title: '下载失败', icon: 'none' });
        }
      },
      fail() {
        wx.hideLoading();
        wx.showToast({ title: '下载失败', icon: 'none' });
      }
    });
  },

  stopPropagation() {
    // 阻止事件冒泡
  },

  onCommentInput(e) {
    this.setData({ reviewComment: e.detail.value });
  },

  async submitReview() {
    const { reviewStatus, reviewComment } = this.data;
    const minLength = reviewStatus === 3 ? 50 : 20;

    if (!reviewComment.trim()) {
      wx.showToast({ title: '请填写评审意见', icon: 'none' });
      return;
    }

    if (reviewComment.trim().length < minLength) {
      wx.showToast({ title: `评审意见至少${minLength}字`, icon: 'none' });
      return;
    }

    try {
      await put(`/tutor/papers/${this.data.paper.id}/review`, {
        status: reviewStatus,
        review_comment: reviewComment.trim()
      }, { showLoading: true });

      wx.showToast({ title: '评审成功', icon: 'success' });
      this.setData({ showModal: false });
      
      // 重新加载数据
      setTimeout(() => {
        this.fetchDetail(this.data.paper.id);
      }, 500);
    } catch (err) {
      console.error('评审失败', err);
    }
  }
});
