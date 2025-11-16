# 苏州高等职业技术学校毕业设计论文选题管理系统（启动页 + 分角色登录原型）

当前包含：
- 启动倒计时页面（校园背景、两行口号、底部欢迎与 5→1 倒计时，结束后自动进入身份选择）
- 身份选择页（学生/教师）与教师二级选择页（导师/管理员）
- 学生/导师/管理员登录页；学生/导师注册页（登录页提供“无账号？前去注册！”入口）

字体与视觉：
- 标题字体：白色 华文新魏（含回退），带阴影立体效果；字号≈二号（60rpx）
- 选项/表单：楷体，对比度与阴影已适配校园背景

## 分包结构与路由
主包仅保留启动页以降低体积，其他页面进入分包：

```
pages: [
   "pages/splash/index"
]
subpackages: [
   { root: "pages/auth",   pages: ["identity/index", "teacher/index"] },
   { root: "pages/student", pages: ["login/index", "register/index"] },
   { root: "pages/tutor",   pages: ["login/index", "register/index"] },
   { root: "pages/admin",   pages: ["login/index"] }
]
preloadRule:
   splash → 预加载 auth 分包；identity → 预加载 student/tutor/admin 分包
```

启动页倒计时结束后跳转：`/pages/auth/identity/index`

## 图片放置与体积优化
- 启动页背景：将校园图命名为 `校园景观.jpg` 放到：`/assets/images/校园景观.jpg`
- 登录/注册背景（乐技楼）：已拆分至各分包的 `pages/<包>/assets/乐技楼.jpg`
   - 分包页面以相对路径引用：`../assets/乐技楼.jpg`（页面位于 `pages/<包>/<页面>/index.wxml`，资源位于 `pages/<包>/assets/`）
   - 主包不再包含 `乐技楼.jpg`，以降低主包体积

推荐压缩图片以避免 80051（主包资源超过 2MB）：
- 已提供压缩脚本：`tools/compress-image.ps1`
- 建议参数：最大宽度 1280~1440、JPEG 质量 55~70

可选命令（PowerShell）：
```powershell
# 压缩“乐技楼.jpg”到指定尺寸与质量（输出到新文件）：
powershell -ExecutionPolicy Bypass -File .\tools\compress-image.ps1 -InputPath .\assets\images\乐技楼.jpg -OutputPath .\assets\images\乐技楼.out.jpg -MaxWidth 1440 -Quality 65
Move-Item -Force .\assets\images\乐技楼.out.jpg .\assets\images\乐技楼.jpg

# 压缩“校园景观.jpg”（建议稍低质量以控制主包体积）
powershell -ExecutionPolicy Bypass -File .\tools\compress-image.ps1 -InputPath .\assets\images\校园景观.jpg -OutputPath .\assets\images\校园景观.out.jpg -MaxWidth 1440 -Quality 60
Move-Item -Force .\assets\images\校园景观.out.jpg .\assets\images\校园景观.jpg
```

提示：如需进一步降低体积，也可把启动页背景放到 CDN，然后把 `pages/splash/index.js` 的 `bgPath` 改为 CDN 地址。

## 快速开始
1) 放置两张图片到项目：
- `assets/images/校园景观.jpg`（启动页）
- `assets/images/乐技楼.jpg`（登录/注册通用背景）

2) 打开“微信开发者工具” → 导入：
- 目录：`c:\Users\徐恩睿\Desktop\苏州高等职业技术学校毕业论文选题管理系统`
- AppID：可用测试号/游客 AppID

3) 模拟器运行即可；真机调试如出现 80051，请先执行上面的图片压缩。

## 目录结构（简化）
```
.
├─ app.json
├─ pages
│  ├─ splash/                 # 主包
│  ├─ auth/identity/          # 分包 auth
│  ├─ auth/teacher/
│  ├─ student/login/          # 分包 student
│  ├─ student/register/
│  ├─ tutor/login/            # 分包 tutor
│  ├─ tutor/register/
│  └─ admin/login/            # 分包 admin（仅登录）
├─ assets/images/
│  └─ 校园景观.jpg            # 启动页背景（主包，仅此一张）
├─ pages/**/assets/乐技楼.jpg # 登录/注册背景（分包内各自持有）
├─ tools/
│  └─ compress-image.ps1      # PowerShell 图片压缩脚本
└─ styles/, utils/            # 公共样式与工具方法
```

## 常见问题（FAQ）
- 80051：主包资源超 2MB
   - 压缩 `assets/images/校园景观.jpg`（主包唯一大图）
   - 若仍超限，可把 `乐技楼.jpg` 拆分到各分包，并改为相对路径引用
- 字体显示差异：若系统无“华文新魏”，将回退到相近字体；如需完全一致，可后续引入自定义字体（注意版权与包体积）。
