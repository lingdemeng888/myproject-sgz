// components/back-button/index.js
Component({
  /**
   * 组件的属性列表
   */
  properties: {
    // 是否显示文字
    showText: {
      type: Boolean,
      value: false
    },
    // 返回按钮文字
    text: {
      type: String,
      value: '返回'
    },
    // 自定义返回逻辑
    customBack: {
      type: Boolean,
      value: false
    }
  },

  /**
   * 组件的初始数据
   */
  data: {

  },

  /**
   * 组件的方法列表
   */
  methods: {
    handleBack() {
      if (this.properties.customBack) {
        // 触发自定义返回事件
        this.triggerEvent('back');
      } else {
        // 默认返回上一页
        wx.navigateBack({
          delta: 1,
          fail: () => {
            // 如果返回失败（比如是第一个页面），跳转到首页
            wx.reLaunch({
              url: '/pages/student/home/index'
            });
          }
        });
      }
    }
  }
});
