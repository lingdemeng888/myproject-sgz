# 返回按钮组件使用说明

## 组件路径
`/components/back-button/index`

## 功能特点
- 统一的视觉风格（半透明黑色背景，毛玻璃效果）
- 固定在页面左上角
- 支持自定义返回逻辑
- 支持显示/隐藏文字
- 点击反馈动画效果
- 自动处理返回失败的情况

## 基本用法

### 1. 在页面配置文件中引入组件
```json
{
  "usingComponents": {
    "back-button": "/components/back-button/index"
  }
}
```

### 2. 在 WXML 中使用
```xml
<!-- 最简单的用法：只显示图标 -->
<back-button></back-button>

<!-- 显示图标和文字 -->
<back-button show-text="{{true}}"></back-button>

<!-- 自定义文字 -->
<back-button show-text="{{true}}" text="返回列表"></back-button>
```

## 组件属性

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| showText | Boolean | false | 是否显示文字 |
| text | String | '返回' | 返回按钮的文字 |
| customBack | Boolean | false | 是否使用自定义返回逻辑 |

## 自定义返回逻辑

如果需要在返回前执行特定操作（如保存草稿、弹出确认框等），可以使用自定义返回：

### 1. WXML
```xml
<back-button custom-back="{{true}}" bind:back="handleCustomBack"></back-button>
```

### 2. JS
```javascript
Page({
  handleCustomBack() {
    wx.showModal({
      title: '提示',
      content: '确定要离开吗？未保存的内容将丢失',
      success: (res) => {
        if (res.confirm) {
          wx.navigateBack();
        }
      }
    });
  }
});
```

## 样式说明

组件使用固定定位（fixed），不会影响页面内容布局。
- 位置：左上角（top: 24rpx, left: 24rpx）
- z-index: 999（确保在最上层）
- 背景：半透明黑色 + 毛玻璃效果
- 点击时有缩放反馈效果

## 已应用页面

学生端以下页面已集成该组件：
- ✅ 选题详情页 (`/pages/student/topic-detail/index`)
- ✅ 可申请选题列表 (`/pages/student/topic-list/index`)
- ✅ 我的申请 (`/pages/student/my-applications/index`)
- ✅ 我的论文 (`/pages/student/my-papers/index`)
- ✅ 论文详情 (`/pages/student/paper-detail/index`)
- ✅ 新增论文版本 (`/pages/student/paper-version-edit/index`)
- ✅ 个人中心 (`/pages/student/profile/index`)

## 注意事项

1. **首页/登录页不建议使用**：这些页面通常是入口页面，没有上一级
2. **与导航栏配合**：组件会叠加在微信导航栏之外，不会冲突
3. **自动降级**：如果返回失败（无上一级页面），会自动跳转到学生首页
