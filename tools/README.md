# 主页素材

`render-profile.py` 生成 D「朱砂极简」方案的 SVG 和主页 README。修改文案、字号或配色后重新生成，不直接编辑字形路径。

需要 Python 3、`fonttools[woff]` 和霞鹜文楷屏幕阅读版（LXGW WenKai Screen Regular）。标题、正文、英文和技术栈全部使用这一字体。

```sh
python tools/render-profile.py --font /path/to/LXGWWenKaiScreen.ttf
```

`--font` 也支持官方字体的 WOFF2 文件。字体不提交进仓库，来源和许可保留在 `assets/FONT-LICENSES.txt`。

素材分为宽屏 / 窄屏、浅色 / 深色四份。宽屏画布宽度 840，窄屏宽度 420，README 使用 `<picture>` 的媒体条件选择；窄屏重新排文字而不是把宽屏素材缩小。系统深色偏好决定配色，GitHub 手动主题与系统偏好不一致时，以系统偏好为准。

SVG 文字转成路径，保证标题与说明不被平台替换字体。README 的图片替代文字保留完整内容，每个项目及博客均有独立链接。

桌面基准字号：姓名 112、主张 33、项目标题 29、项目说明 19、技术栈 16。窄屏基准字号：姓名 91、主张 31、项目标题 25、项目说明 18、技术栈 14。所有文字共用 `TEXT_SCALE = 0.88 * 2 / 3`，相对上一版统一缩小三分之一，文字度量与字距同步缩放。实际显示随 README 内容区宽度缩放。

个人简介、项目介绍和页脚格言通过 `BODY_TEXT_BOOST = 1.25` 单独放大 25%；竖排「代码与文字之间」通过 `VERTICAL_TEXT_BOOST = 1.5` 单独放大 50%。姓名、主张、项目标题、技术栈和其他文字继续使用统一倍率。
