const { ensureStudent } = require('../../../utils/auth');
const { post, upload } = require('../../../utils/request');

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
    saving: false,
    selectedFiles: []
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

  chooseFile() {
    const maxCount = 5 - this.data.selectedFiles.length;
    if (maxCount <= 0) {
      wx.showToast({ title: '最多选择5个文件', icon: 'none' });
      return;
    }
    
    wx.chooseMessageFile({
      count: maxCount,
      type: 'file',
      extension: ['pdf', 'doc', 'docx', 'zip', 'rar'],
      success: (res) => {
        const files = res.tempFiles.map(f => {
          // 检查文件大小（1GB限制）
          if (f.size > 1024 * 1024 * 1024) {
            wx.showToast({ title: `${f.name} 超过1GB`, icon: 'none' });
            return null;
          }
          return {
            path: f.path,
            name: f.name,
            size: f.size,
            sizeText: this.formatFileSize(f.size)
          };
        }).filter(f => f !== null);
        
        if (files.length > 0) {
          this.setData({
            selectedFiles: [...this.data.selectedFiles, ...files]
          });
        }
      },
      fail: (err) => {
        console.log('选择文件失败', err);
        if (err.errMsg.includes('cancel')) {
          // 用户取消，不提示
        } else {
          wx.showToast({ title: '选择文件失败', icon: 'none' });
        }
      }
    });
  },

  removeFile(e) {
    const index = e.currentTarget.dataset.index;
    const files = this.data.selectedFiles.filter((_, i) => i !== index);
    this.setData({ selectedFiles: files });
  },

  formatFileSize(bytes) {
    if (bytes < 1024) return bytes + 'B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB';
    return (bytes / (1024 * 1024)).toFixed(1) + 'MB';
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
      // 1. 创建版本
      const paper = await post(`/student/papers/${this.data.paperId}/versions`, {
        content_text: content,
        content_format: this.data.formatOptions[this.data.formatIndex].value,
        notes: this.data.notes.trim() || undefined
      }, { showLoading: true });

      // 获取最新版本ID（版本按version_no降序排列，第一个就是最新的）
      const latestVersion = paper.versions && paper.versions.length > 0 ? paper.versions[0] : null;
      
      if (!latestVersion) {
        console.error('未能获取到新创建的版本信息');
        wx.showToast({ title: '版本已保存', icon: 'success' });
        setTimeout(() => {
          wx.navigateBack();
        }, 800);
        return;
      }

      console.log('新创建的版本:', latestVersion);

      // 2. 上传附件
      if (this.data.selectedFiles.length > 0) {
        for (const file of this.data.selectedFiles) {
          try {
            console.log(`上传附件到版本 ${latestVersion.id}:`, file.name);
            await upload('/upload/attachment', file.path, {
              version_id: latestVersion.id
            });
          } catch (err) {
            console.error('上传附件失败', file.name, err);
          }
        }
      }

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
