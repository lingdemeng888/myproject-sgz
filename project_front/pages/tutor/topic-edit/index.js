const { ensureTutor } = require('../../../utils/auth');
const { get, post, put } = require('../../../utils/request');

Page({
  data: {
    topicId: null, // 编辑时有ID，创建时为null
    formData: {
      title: '',
      description: '',
      major_id: null,
      academic_year: '',
      term: null,
      max_students: 3
    },
    majors: [],
    majorIndex: -1,
    selectedMajor: '',
    terms: [
      { value: 1, name: '上学期' },
      { value: 2, name: '下学期' }
    ],
    termIndex: -1,
    selectedTerm: '',
    saving: false,
    publishing: false
  },

  onLoad(options) {
    const user = ensureTutor();
    if (!user) return;

    // 如果有topic_id，说明是编辑模式
    if (options.id) {
      this.setData({ topicId: parseInt(options.id) });
      this.loadTopicDetail(options.id);
    }

    // 加载专业列表
    this.loadMajors();
  },

  // 加载专业列表
  async loadMajors() {
    try {
      const result = await get('/majors', { page: 1, page_size: 100 });
      this.setData({ majors: result.items || [] });
    } catch (err) {
      console.error('加载专业列表失败:', err);
    }
  },

  // 加载选题详情（编辑模式）
  async loadTopicDetail(id) {
    try {
      wx.showLoading({ title: '加载中...' });
      const topic = await get(`/tutor/topics/${id}`);
      
      this.setData({
        formData: {
          title: topic.title || '',
          description: topic.description || '',
          major_id: topic.major_id || null,
          academic_year: topic.academic_year || '',
          term: topic.term || null,
          max_students: topic.max_students || 3
        }
      });

      // 设置专业选择器
      if (topic.major_id && this.data.majors.length > 0) {
        const index = this.data.majors.findIndex(m => m.id === topic.major_id);
        if (index !== -1) {
          this.setData({
            majorIndex: index,
            selectedMajor: this.data.majors[index].name
          });
        }
      }

      // 设置学期选择器
      if (topic.term) {
        const termIndex = this.data.terms.findIndex(t => t.value === topic.term);
        if (termIndex !== -1) {
          this.setData({
            termIndex: termIndex,
            selectedTerm: this.data.terms[termIndex].name
          });
        }
      }

      wx.hideLoading();
    } catch (err) {
      wx.hideLoading();
      console.error('加载选题详情失败:', err);
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  // 表单输入
  onTitleInput(e) {
    this.setData({ 'formData.title': e.detail.value });
  },

  onDescInput(e) {
    this.setData({ 'formData.description': e.detail.value });
  },

  onMaxStudentsInput(e) {
    const value = parseInt(e.detail.value) || 0;
    this.setData({ 'formData.max_students': value });
  },

  onMajorChange(e) {
    const index = parseInt(e.detail.value);
    const major = this.data.majors[index];
    if (!major) {
      console.error('无效的专业索引:', index);
      return;
    }
    this.setData({
      majorIndex: index,
      selectedMajor: major.name,
      'formData.major_id': major.id
    });
  },

  onAcademicYearInput(e) {
    this.setData({ 'formData.academic_year': e.detail.value });
  },

  onTermChange(e) {
    const index = parseInt(e.detail.value);
    const term = this.data.terms[index];
    if (!term) {
      console.error('无效的学期索引:', index);
      return;
    }
    this.setData({
      termIndex: index,
      selectedTerm: term.name,
      'formData.term': term.value
    });
  },

  // 验证表单
  validateForm() {
    const { title, description, major_id, academic_year, term, max_students } = this.data.formData;

    if (!title || title.trim().length === 0) {
      wx.showToast({ title: '请输入选题标题', icon: 'none' });
      return false;
    }

    if (!description || description.trim().length < 10) {
      wx.showToast({ title: '选题描述至少10字符', icon: 'none' });
      return false;
    }

    if (!major_id) {
      wx.showToast({ title: '请选择所属专业', icon: 'none' });
      return false;
    }

    if (!academic_year || !/^\d{4}-\d{4}$/.test(academic_year)) {
      wx.showToast({ title: '请输入正确的学年格式（如：2024-2025）', icon: 'none' });
      return false;
    }

    if (!term || (term !== 1 && term !== 2)) {
      wx.showToast({ title: '请选择学期', icon: 'none' });
      return false;
    }

    if (!max_students || max_students < 1 || max_students > 10) {
      wx.showToast({ title: '最大学生数应在1-10之间', icon: 'none' });
      return false;
    }

    return true;
  },

  // 保存草稿
  async saveDraft() {
    if (!this.validateForm()) return;

    this.setData({ saving: true });

    try {
      if (this.data.topicId) {
        // 更新选题
        await put(`/tutor/topics/${this.data.topicId}`, this.data.formData);
        wx.showToast({ title: '更新成功', icon: 'success' });
      } else {
        // 创建选题
        await post('/tutor/topics', this.data.formData);
        wx.showToast({ title: '保存成功', icon: 'success' });
      }

      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    } catch (err) {
      console.error('保存失败:', err);
    } finally {
      this.setData({ saving: false });
    }
  },

  // 保存并发布
  async saveAndPublish() {
    if (!this.validateForm()) return;

    this.setData({ publishing: true });

    try {
      let topicId = this.data.topicId;

      // 先保存
      if (topicId) {
        await put(`/tutor/topics/${topicId}`, this.data.formData);
      } else {
        const result = await post('/tutor/topics', this.data.formData);
        topicId = result.id;
      }

      // 再发布
      await post(`/tutor/topics/${topicId}/publish`, {});
      
      wx.showToast({ title: '发布成功', icon: 'success' });
      
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    } catch (err) {
      console.error('发布失败:', err);
    } finally {
      this.setData({ publishing: false });
    }
  }
});
