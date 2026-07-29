# 华丽电器制造有限公司 — 企业官网开发手册

> **版本**：v1.30 · **最后更新**：2026-07-29
> **开发者**：本项目为前后端分离架构，AI 辅助开发

> **文档维护约定**：每次完成会改变项目结构、功能状态、接口、数据模型、运行方式或待办事项的开发工作后，必须同步更新本文件。

---

## 一、项目说明

### 1.1 项目概述

华丽电器制造有限公司的企业官方网站，用于展示公司形象、产品信息、新闻动态、供应链体系，并提供在线询盘、经销商入口等功能。支持中英双语（开发中），适配手机/平板/电脑。

### 1.2 公司背景

| 项目 | 内容 |
|------|------|
| 公司全称 | 华丽电器制造有限公司（原武义华丽电器制造有限公司，2019 年更名） |
| 成立时间 | 2003 年 3 月 6 日 |
| 法人代表 | 俞振腾 |
| 注册资本 | 6000 万元人民币 |
| 注册地址 | 浙江省金华市武义县泉溪镇王元工业区（一照多址） |
| 信用代码 | 913307237490117726 |
| 企业性质 | 国家高新技术企业，浙江省专精特新中小企业 |
| 核心产品 | 电锤、电镐、电钻、型材切割机等专业电动工具及配件 |
| 国际业务 | 自营进出口权 / 技术进出口资质，产品远销欧洲、北美、东南亚、中东、非洲等 80+ 国家和地区 |

### 1.3 荣誉资质

- 国家高新技术企业
- 浙江省专精特新中小企业
- 2025 年入选国家级 5G 工厂
- 浙江省企业技术中心 amp; 工业设计中心
- 浙江省智能工厂
- 2024 年金华纳税千万元以上工业企业
- 2025 年税务信用 A 级
- 200+ 专利，500+ 注册商标

### 1.4 架构模式

采用**前后端分离架构**：

- **前端独立运行**：Vue 3 SPA（单页应用），通过 AJAX 调用后端 API
- **后端仅做 API**：Django 不渲染前台页面，只提供 REST API 和管理后台
- **开发时双服务**：Vite 开发服务器（:5173）+ Django 开发服务器（:8000）同时运行
- **生产部署时**：Nginx 提供预渲染前端、公开媒体和 Django 静态文件，Gunicorn 运行 Django API 与后台

---

## 二、技术栈

### 2.1 前端（frontend/）

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | ^3.5 | 前端框架（Composition API 语法） |
| Vite | ^6.0 | 构建工具 / 开发服务器 |
| Vue Router | ^4.5 | 前端路由（8 个主页面 + 产品/新闻详情页） |
| Axios | ^1.7 | HTTP 请求库（调用 Django API） |
| PhotoSwipe | ^5.4 | 产品详情图库、全屏缩放与移动端手势 |
| Quill | ^2.0.3 | 后台富文本编辑器；保存时由 Bleach 再次清洗 |
| Playwright | ^1.62 | SEO 预渲染和桌面/手机浏览器冒烟测试 |
| @vitejs/plugin-vue | ^5.2 | Vite 的 Vue 编译插件 |
| Font Awesome 6 | CDN | 图标库 |
| AOS.js | CDN | 页面滚动动画 |

### 2.2 后端（Django）

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.14 | 运行环境 |
| Django | 6.0.7 | Web 框架 |
| django-simpleui | 2026.1.13 | 后台管理主题 |
| Django REST framework | 3.17.1 | 公开 API、限流和统一响应 |
| Bleach / Pillow | 6.4 / 12.3 | 富文本清洗与安全图片处理 |
| django-otp / django-axes | 1.7 / 8.3 | TOTP 双重验证与登录限流 |
| SQLite | 内置 | 开发与生产数据库，生产开启 WAL 与 busy timeout |
| Gunicorn / Nginx | 23.0 / 系统包 | 生产应用服务与反向代理 |

### 2.3 代理与通信

Vite 开发服务器配置了代理规则，将 `/api/*` 开头的请求转发到 Django（localhost:8000），避免跨域问题。

---

## 三、目录结构

```
D:\13486\Desktop\企业网站\
│
├── AGENTS.md                  # 本开发手册
├── logo.jpg                   # 公司 Logo（红白 H 标志）
├── requirements.txt           # Python 依赖清单
│
├── frontend/                  # ===== Vue 前端 =====
│   ├── index.html             #   HTML 入口
│   ├── package.json           #   npm 依赖和脚本
│   ├── vite.config.js         #   Vite 配置（代理、别名、构建）
│   ├── scripts/               #   预渲染、预渲染冒烟和浏览器验收脚本
│   ├── public/                #   静态资源
│   │   └── images/            #     Logo、产品、公司与新闻图片
│   │       └── editorial/     #     AI 生成的采购、历程、荣誉、经销商专题图片
│   └── src/
│       ├── main.js            #   Vue 应用入口
│       ├── App.vue            #   根组件（导航 + 路由出口 + 页脚）
│       ├── router/
│       │   └── index.js       #   主页面及产品/新闻详情路由
│       ├── api/                #   Axios 客户端与内容 API
│       ├── composables/        #   异步状态和安全表单组合式函数
│       ├── views/             #   页面组件
│       │   ├── Home.vue       #     首页
│       │   ├── About.vue      #     关于我们
│       │   ├── Products.vue   #     产品中心
│       │   ├── ProductDetail.vue #  产品详情
│       │   ├── News.vue       #     新闻中心
│       │   ├── NewsDetail.vue #     新闻详情
│       │   ├── SupplyChain.vue #    供应链
│       │   ├── Inquiry.vue    #     在线询盘
│       │   ├── Dealer.vue     #     经销商入口
│       │   ├── Contact.vue    #     联系我们
│       │   ├── Privacy.vue    #     隐私政策（禁止索引）
│       │   └── NotFound.vue   #     404 页面（禁止索引）
│       ├── components/
│       │   ├── NavBar.vue     #     顶部导航栏
│       │   ├── FooterBar.vue  #     页脚
│       │   └── SectionHeading.vue #  带小图标的统一模块标题
│       └── assets/
│           └── styles/
│               └── main.css   #   全局样式、工业侧边纹理与影像化页头
│
├── huali_website/             # ===== Django 项目配置 =====
│   ├── __init__.py
│   ├── settings.py            #   开发与通用配置
│   ├── settings_production.py #   生产安全配置
│   ├── urls.py                #   根路由
│   ├── wsgi.py                #   WSGI 部署入口
│   └── asgi.py                #   ASGI 部署入口
│
├── main/                      # ===== Django 主应用 =====
│   ├── __init__.py
│   ├── admin.py               #   后台模型注册
│   ├── apps.py                #   应用配置
│   ├── forms.py               #   API 表单校验与附件限制
│   ├── models.py              #   数据模型
│   ├── views.py               #   API 视图
│   ├── urls.py                #   应用路由
│   └── tests.py               #   单元测试
│
├── products/                  # ===== 产品模型、后台、API 与种子命令 =====
├── news/                      # ===== 新闻模型、后台与 API =====
├── company_content/           # ===== 企业资料、事实、历程、供应链、地点与 FAQ =====
├── honors/                    # ===== 荣誉分类、荣誉条目与公开 API =====
├── page_builder/              # ===== 统一媒体库、许可台账、素材槽位与引用关系 =====
├── operations/                # ===== 安全、隐私、邮件、审计、预渲染、备份与健康看板 =====
├── docs/                      # ===== 中文操作手册 =====
├── deploy/                    # ===== Ubuntu、Nginx、Gunicorn 与 systemd 部署文件 =====
├── .github/workflows/ci.yml   # ===== GitHub Actions 持续集成 =====
├── private_media/             # ===== 私有询盘/邮件附件（禁止公开访问） =====
├── backups/                   # ===== AES-256 加密备份（运行时生成） =====
├── prerender_releases/        # ===== 预渲染版本与 current 软链接 =====
├── media/                     # ===== 用户上传附件（运行时生成） =====
├── db.sqlite3                 # ===== SQLite 开发数据库 =====
├── venv/                      # ===== Python 虚拟环境 =====
└── manage.py                  # ===== Django 管理入口 =====
```

---

## 四、本地运行

### 4.1 前置条件

- **Node.js** >= 18（已安装 v24.18.0）
- **Python** >= 3.10（已安装 v3.14.6）

### 4.2 启动步骤

打开**两个终端窗口**，同时运行：

**终端 1 — Django 后端：**
```powershell
cd D:\13486\Desktop\企业网站
.\venv\Scripts\Activate.ps1
python manage.py runserver
```
激活后终端前面会出现 `(venv)` 标记。如遇执行策略错误，使用：
```powershell
powershell -ExecutionPolicy Bypass -File .\venv\Scripts\Activate.ps1
```

**终端 2 — Vue 前端：**
```powershell
cd D:\13486\Desktop\企业网站\frontend
npm run dev
```

### 4.3 访问地址

| 地址 | 说明 |
|------|------|
| http://localhost:5173 | 前台网站（Vue） |
| http://localhost:8000/admin/ | 后台管理（Django + SimpleUI） |

### 4.4 停止服务

在对应终端按 `Ctrl + C` 即可停止。退出虚拟环境运行 `deactivate`。

---

## 五、后台账号

| 项目 | 内容 |
|------|------|
| 用户名 | yiyu5331 |
| 密码 | 不在文档中保存；上线前必须通过管理命令更换 |
| 邮箱 | 13486955804@163.com |
| 权限 | 超级管理员（所有权限） |
| 后台地址 | http://localhost:8000/admin/ |

重置密码命令：`python manage.py changepassword yiyu5331`

生产环境超级管理员必须绑定 TOTP 双重验证；恢复码仅在首次绑定时显示一次。恢复入口仅限服务器命令：`python manage.py reset_superuser_2fa 用户名`。

---

## 六、前端开发

### 6.1 技术约定

- 使用 Vue 3 **Composition API** 语法
- 路由使用 **Vue Router 4**（createWebHistory 模式，URL 无 `#`）
- 页面组件放在 `views/`，公共组件放在 `components/`
- 每个页面通过 `import()` 懒加载
- 全局样式在 `main.css` 管理，组件样式使用 `<style scoped>`

### 6.2 路由一览

| 路径 | 组件 | 页面名 |
|------|------|--------|
| `/` | Home.vue | 首页 |
| `/about` | About.vue | 关于我们 |
| `/products/` | Products.vue | 产品中心 |
| `/products/category/:categorySlug/` | Products.vue | 产品分类 |
| `/products/:categorySlug/:model/` | ProductDetail.vue | 产品详情 |
| `/news/` | News.vue | 新闻中心 |
| `/news/category/:categorySlug/` | News.vue | 新闻分类 |
| `/news/:categorySlug/:slug/` | NewsDetail.vue | 新闻详情 |
| `/supply-chain/` | SupplyChain.vue | 供应链 |
| `/inquiry/` | Inquiry.vue | 在线询盘（禁止索引） |
| `/dealer/` | Dealer.vue | 经销商入口 |
| `/contact/` | Contact.vue | 联系我们 |
| `/privacy/` | Privacy.vue | 隐私政策（禁止索引） |
| `/:pathMatch(.*)*` | NotFound.vue | 404 页面（禁止索引） |

SEO 正式 URL 已统一使用尾斜杠：产品分类 `/products/category/{slug}/`，产品详情 `/products/{category-slug}/{model}/`，新闻分类 `/news/category/{slug}/`，新闻详情 `/news/{category-slug}/{article-slug}/`。旧产品与新闻详情地址由 Django/Nginx 返回 301。

### 6.3 组件说明

**NavBar.vue**：置顶固定导航，移动端 768px 以下显示汉堡菜单，当前路由高亮。

**FooterBar.vue**：深色三栏页脚，含公司简介、快速链接、联系方式、版权信息。

### 6.4 API 调用规范

前后端通过 `/api/` 前缀通信，Vite 自动代理到 Django：
```javascript
import axios from 'axios'
axios.post('/api/inquiries/', formData)
axios.post('/api/contacts/', messageData)
```

现有接口：

| 方法 | 路径 | 用途 | 数据格式 |
|------|------|------|----------|
| POST | `/api/inquiries/` | 新增在线询盘 | `multipart/form-data`，支持附件 |
| POST | `/api/contacts/` | 新增联系留言 | JSON 或普通表单 |

接口成功时返回 HTTP `201` 和新增记录 ID；字段错误时返回 HTTP `400` 与具体错误信息。

### 6.5 设计规范

**色彩体系：**
- 品牌红（主色）：`#C41E24` — 按钮、导航栏、标题
- 亮红（悬停）：`#E8373D` — hover 状态
- 深文字：`#222222` — 正文标题
- 灰背景：`#F5F5F5` — 分区背景
- 灰边框：`#E0E0E0` — 卡片/分割线
- 白色：`#FFFFFF` — 底色

**字体：** 中文微软雅黑/思源黑体，英文 Arial，正文 16px/1.6

**响应式断点：** 手机 <= 768px，平板 769-1024px，电脑 >= 1025px

**通用 CSS 类（main.css）：**
- `.container` — 版心 1200px 居中
- `.btn` / `.btn-primary` / `.btn-outline` — 按钮
- `.section` / `.section-title` — 分区
- `.card` — 卡片（带 hover 上浮）
- `.page-banner` — 页面标题区

**页面影像与留白：** 供应链和经销商页面使用 `visual-edge-section`，桌面端真实图片占屏幕侧边约 1/4，并用蒙版向正文方向淡出；移动端自动隐藏侧边图。供应链采购品类使用物料台账式列表，图片优先展示原料、零部件或生产环节，不把成品工具当作采购品类。统一标题使用 `SectionHeading.vue`，小图标控制在约 19px，避免图标喧宾夺主。

`frontend/public/images/editorial/` 保存通过 `codex-image2` 生成的专题素材。网页使用 WebP 版本（质量约 82），PNG 原图保留用于后续重新裁切和编辑。目前已接入供应商审核、核心采购零部件、电机电子物料、公司发展陈列、荣誉证书陈列和经销商合作图片；其余采购物料概念图生成任务可继续补充，页面已有可靠素材兜底。

### 6.6 新增页面流程

1. 在 `src/views/` 创建 `YourPage.vue`
2. 在 `src/router/index.js` 添加路由配置
3. 在 `src/components/NavBar.vue` 添加导航链接

---

## 七、Django 配置要点

### 7.1 settings.py 关键配置

**已注册应用：** simpleui、DRF、drf-spectacular、products、news、company_content、honors、page_builder、main、operations 及 Django 内置应用。

**国际化：** LANGUAGE_CODE = 'zh-hans'，TIME_ZONE = 'Asia/Shanghai'

**媒体文件：** 公开产品与新闻媒体使用 `MEDIA_ROOT`；询盘和邮件附件使用 `PRIVATE_MEDIA_ROOT`，只能通过后台权限校验后的受控下载接口访问。

**SimpleUI 主题：** 蓝色主题（e-blue.css），已关闭首页资讯和数据分析，后台 Logo 指向 /static/images/logo.jpg，首页直跳 /admin/

后台首页已移除重复的 `SIMPLEUI_INDEX` 和 `SIMPLEUI_HOME_PAGE` 配置，避免 SimpleUI 首页重复跳转造成闪烁。产品、新闻、询盘和联系表单列表使用后台专用脚本拆分为两个独立日期框：左侧为起始日期，右侧为截止日期，中间显示横杠，点击日期框打开日历选择日期；首次无日期参数进入时自动默认最近 30 日，后续选择日期不强制保持 30 天跨度。截止日期提交为当天 23:59:59，确保包含截止日全天数据。产品默认按最后修改时间，新闻默认按发布时间，表单默认按提交时间。产品、产品分类、产品标签、新闻和新闻分类列表均提供明确的“编辑”入口；联系表单与询盘表单保留为原始提交记录查看页，不提供编辑按钮。

日期筛选使用 `main/admin_filters.py` 中的 `DefaultDateRangeAdminMixin`，并由 `main/static/admin/date_range_split.js` 与 `date_range_split.css` 将 SimpleUI 的 `daterange`/`datetimerange` 控件隐藏，替换为两个互不联动的 ElementUI `el-date-picker` 日历框。产品和新闻已有自定义后台 Media 时也显式合并这两个资源。开始日期与截止日期分别写回独立查询参数，用户可以分别调整任意跨度；仅首次无日期参数进入列表时默认最近 30 日。

日期框样式统一了日历图标、输入文字、前缀和后缀的高度与垂直居中，避免图标和日期数字上下错位。

**后台表单菜单：** Django 主应用显示为一级菜单“表单管理”，下设“联系表单”和“询盘表单”两个二级菜单。列表页通过 Django ORM 直接查询 `lianxi`、`xunpan` 的真实数据，支持关键词搜索、处理状态/负责人筛选、日期导航、详情查看及询盘附件访问。两类表单均可在后台编辑处理状态、负责人、内部备注和最后跟进时间；管理员可对选中记录导出 UTF-8 CSV 或 Excel 文件。

### 7.2 内容运营应用与公开 API

`products/` 和 `news/` 已建立独立内容模型、后台管理、媒体处理与幂等种子命令。当前数据库包含 18 款原有产品、12 款 `DEMO-` 概念产品、9 条原有新闻和 12 条制造知识测试新闻；前台产品、新闻、首页聚合、产品选项均从 SQLite API 获取。

第三阶段里程碑一新增 `company_content/`、`honors/` 和 `page_builder/`。后台现在可维护企业资料、事实指标、发展历程、供应链、经销商权益、地点、FAQ、荣誉、媒体文件夹、标签、许可台账、桌面/手机素材变体、焦点坐标、素材槽位和引用关系。产品后台增加标准参数字典与“参数映射建议”，建议必须由管理员确认后才会写入产品参数。

`SITE_CONTENT_MODE=test|production` 控制内容可见性。默认 `test` 模式允许本地展示演示产品、AI 占位和待核验内容；`production` 模式只公开“非演示 + 已核验”的内容，并阻止演示或待核验内容发布。后台首页只读显示当前模式。

公开 API 统一使用 `/api/v1/` 前缀：

| 方法 | 路径 | 用途 |
|------|------|------|
| GET | `/api/v1/product-categories/` | 已发布产品分类 |
| GET | `/api/v1/products/` | 产品列表、分类、搜索、分页 |
| GET | `/api/v1/products/{model}/` | 产品详情、图库、参数、资料、相关产品 |
| GET | `/api/v1/product-options/` | 询盘产品选择 |
| GET | `/api/v1/news-categories/` | 已发布新闻分类 |
| GET | `/api/v1/news/` | 新闻列表、分类、搜索、分页 |
| GET | `/api/v1/news/{slug}/` | 新闻详情和相关新闻 |
| GET | `/api/v1/homepage/` | 首页推荐内容聚合 |
| GET | `/api/v1/site-content/` | 企业资料、指标、历程、供应链、经销商权益和地点聚合 |
| GET | `/api/v1/locations/` | 公开地点与联系方式 |
| GET | `/api/v1/faqs/?category=` | FAQ 列表和分类筛选 |
| GET | `/api/v1/honor-categories/` | 有公开条目的荣誉分类 |
| GET | `/api/v1/honors/?category=` | 荣誉条目和分类筛选 |
| POST | `/api/v1/inquiries/` | 新增在线询盘，保留产品名称/型号快照并自动关联有效产品 |
| POST | `/api/v1/contacts/` | 新增联系我们留言 |

第二阶段安全接口：

| 方法 | 路径 | 用途 |
|------|------|------|
| GET | `/api/v1/forms/bootstrap/?kind=inquiry|contact` | 签发 CSRF Cookie、一次性表单令牌并返回当前隐私政策版本 |
| POST | `/api/v1/captcha/` | 获取 4 位、5 分钟有效的一次性图形验证码 |
| GET | `/api/v1/privacy-policy/` | 获取当前已发布的中英双语隐私政策 |
| GET | `/api/v1/health/` | 返回最小化服务状态和版本 |

在线表单必须经过隐私同意、一次性令牌、风险验证码、蜜罐和 IP 指纹限流。IP 只保存使用 `FORM_SECURITY_KEY` 生成的 HMAC 指纹，不保存明文。询盘附件保存到 `private_media/`，不能通过 `/media/` 直接访问，后台使用受控下载接口读取。Windows 开发环境记录为跳过 ClamAV；生产环境必须启用 ClamAV，扫描不可用时拒绝附件但允许移除附件后提交纯文本。

开发环境额外提供 `/api/schema/`、`/api/docs/` 和 `/api/redoc/`。公开接口匿名限流为 120 次/分钟，产品每页 12 条、新闻每页 8 条。

第三阶段基础种子命令导入 20 条测试 FAQ、8 条待核验荣誉、4 个演示产品系列、12 款 `DEMO-` 产品、12 条测试新闻、8 个标准参数、参数映射建议、媒体许可/标签/槽位，以及 4 份双语 4 页测试 PDF。所有演示内容均带演示标识或免责声明，不可作为真实采购、认证或经营依据。

### 7.3 创建新 API 流程

1. 在 `main/models.py` 定义模型
2. 运行 `makemigrations` + `migrate`
3. 在 `main/admin.py` 注册模型
4. 在 `main/views.py` 编写 API 视图
5. 在 `main/urls.py` 配置路由（前缀 `/api/`）
6. 在 `huali_website/urls.py` 用 `include()` 引入

### 7.4 邮件队列与客户跟进

询盘和留言保存后，会在同一数据库事务中创建销售通知与客户中英双语回执任务，网页不等待 SMTP。邮件任务由 `python manage.py process_email_queue` 处理，失败后约 1、5、30 分钟重试，最终失败生成系统告警并尝试通知独立运维邮箱。

后台“安全与运维 → 邮件模板”可维护销售通知、询盘回执、留言回执和跟进模板，并可恢复系统默认内容。询盘和联系表单详情页提供“发送跟进邮件”，支持多份 PDF、Word、Excel 或图片附件，单封总计不超过 20 MB；发送成功后更新最后跟进时间，待处理线索自动转为跟进中。

### 7.5 SEO 与预渲染

使用 Playwright + Chromium 对首页、公司、产品/新闻列表、分类、详情、供应链、经销商和联系页面做浏览器式预渲染。页面等待 API 和懒加载图片完成后保存完整 HTML，正文在禁用 JavaScript时仍可读取。每次发布生成独立版本目录并原子切换 `prerender_releases/current`，保留最近 3 个成功版本。

预渲染同步生成 `sitemap.xml` 和 `robots.txt`，并输出 canonical、Open Graph、Organization、BreadcrumbList、Product 和 NewsArticle 结构化数据。当前本地验收使用 `https://example.com` 占位；正式上线前必须在 `.env` 设置真实 `SITE_URL` 后重新执行全量预渲染。

### 7.6 备份、运维与部署

`python manage.py backup_site` 使用 SQLite 在线备份 API 创建一致性快照，再将数据库、公开媒体和私有附件打包为 AES-256 加密文件，并记录 SHA-256、迁移签名、文件大小和可选 S3 上传状态。`restore_site` 会在覆盖前校验密钥、包哈希、数据库哈希、SQLite `integrity_check`、迁移兼容性和磁盘空间，且必须显式输入确认词。

生产共享数据路径由 `DATABASE_PATH`、`STATIC_ROOT`、`MEDIA_ROOT`、`PRIVATE_MEDIA_ROOT`、`BACKUP_ROOT` 和 `PRERENDER_ROOT` 配置，代码版本切换不会覆盖业务数据。后台首页健康看板显示邮件队列、预渲染、备份、ClamAV、数据库大小、磁盘空间、证书到期时间和未解决告警；公开 `/api/v1/health/` 只返回最小状态和版本。

`deploy/` 已提供 Ubuntu 24.04 的 Nginx、Gunicorn 和 systemd 文件：邮件队列每分钟执行，增量预渲染每 5 分钟执行，全量预渲染每日 02:00 执行，备份每日 03:00 执行，匿名化与清理每日 03:30 执行。GitHub Actions 会检查后端测试、迁移、生产安全配置、前端构建、Playwright 预渲染、依赖漏洞和敏感信息。

### 7.7 数据库

开发环境使用 SQLite（`db.sqlite3`），如需切换到 MySQL/PostgreSQL 修改 `settings.py` 中 `DATABASES` 配置。

现有业务数据表：

| 数据表 | Django 模型 | 用途 |
|--------|-------------|------|
| `xunpan` | `Xunpan` | 保存在线询盘、产品需求与附件路径 |
| `lianxi` | `Lianxi` | 保存联系我们页面的留言 |

第三阶段结构化内容表由 Django 自动命名，主要包括 `company_content_*`、`honors_*`、`page_builder_*`，以及产品应用中的标准参数、参数映射建议和演示标记字段。`operations_jobtask` 是 AI 翻译、生图、索引、统计和页面发布后续共用的数据库任务中心。

`xunpan` 额外保存 `product_name_snapshot`、`product_model_snapshot` 和可选的产品外键，确保客户提交询盘后产品名称、型号不会因后台改名而丢失；询盘产品选项接口同时返回产品缩略图，前端选择产品后显示名称、型号和图片。`xunpan`、`lianxi` 均保存处理状态、负责人、内部备注和最后跟进时间。迁移和种子命令均不会清空既有表单记录。

两张表已注册到 Django 管理后台，也可以使用 Navicat 直接打开项目根目录的 `db.sqlite3` 查看。

后台菜单对应关系：

| 一级菜单 | 二级菜单 | 数据表 | 后台路径 |
|----------|----------|--------|----------|
| 表单管理 | 联系表单 | `lianxi` | `/admin/main/lianxi/` |
| 表单管理 | 询盘表单 | `xunpan` | `/admin/main/xunpan/` |

询盘附件支持 PDF、Word、Excel、JPG、PNG，最大 10 MB；文件保存在 `private_media/inquiry_attachments/年/月/`，数据库只保存私有文件路径和扫描状态。Excel 导出依赖 `openpyxl==3.1.5`，CSV 导出带 UTF-8 BOM，便于在 Windows Excel 中直接打开中文。

---

## 八、常用命令

### Python 虚拟环境
| 命令 | 说明 |
|------|------|
| `.\venv\Scripts\Activate.ps1` | 激活 |
| `deactivate` | 退出 |
| `python -m pip install 包名` | 安装包 |
| `python -m pip freeze > requirements.txt` | 导出依赖 |

### Django
| 命令 | 说明 |
|------|------|
| `python manage.py runserver` | 启动开发服务器 |
| `python manage.py startapp 应用名` | 创建新应用 |
| `python manage.py migrate` | 迁移数据库 |
| `python manage.py makemigrations` | 生成迁移文件 |
| `python manage.py createsuperuser` | 创建管理员 |
| `python manage.py changepassword 用户名` | 修改密码 |
| `python manage.py shell` | Django Shell |
| `python manage.py check` | 检查配置 |
| `python manage.py test main` | 运行询盘与留言 API 自动化测试 |
| `python manage.py collectstatic` | 收集静态文件 |
| `python manage.py seed_content` | 幂等导入产品、新闻及媒体内容 |
| `python manage.py seed_content --check` | 只检查种子与数据库差异，不写入 |
| `python manage.py seed_content --overwrite` | 允许覆盖已有内容后重新导入 |
| `python manage.py seed_phase3_foundation` | 幂等导入第三阶段公司内容、荣誉、FAQ、演示产品/新闻、媒体基础和 4 份测试 PDF |
| `python manage.py seed_phase3_foundation --check` | 只检查第三阶段种子差异，不写数据库 |
| `python manage.py seed_phase3_foundation --overwrite` | 恢复种子管理的演示内容；不会重置人工已核验的真实产品/新闻 |
| `python manage.py process_email_queue` | 处理到期邮件任务并执行失败重试 |
| `python manage.py reset_superuser_2fa 用户名` | 在服务器重置超级管理员双重验证 |
| `python manage.py list_prerender_routes` | 输出全部可索引页面路由 |
| `python manage.py process_prerender_queue` | 合并处理待重建页面 |
| `python manage.py process_prerender_queue --full` | 全量构建并校验 43 个公开页面 |
| `python manage.py submit_search_engines` | 向已配置的百度和 IndexNow 提交 URL；Google 使用 sitemap |
| `python manage.py backup_site` | 在线快照并创建 AES-256 加密站点备份 |
| `python manage.py restore_site 备份路径 --confirm RESTORE-HUALI` | 完整校验后恢复数据库和媒体，执行前必须停止 Gunicorn |
| `python manage.py cleanup_operations` | 匿名化满 3 年线索并清理过期验证码、任务和旧备份 |
| `python manage.py check --deploy --settings=huali_website.settings_production` | 检查生产安全配置是否具备启动条件 |

### Vue / npm
| 命令 | 说明 |
|------|------|
| `npm run dev` | 启动开发服务器 |
| `npm run build` | 构建生产版本 |
| `npm run preview` | 预览构建结果 |
| `npm run prerender` | 使用 Chromium 生成预渲染 HTML |
| `npm run prerender:smoke` | 检查预渲染页面正文、元信息与资源 |
| `npm run test:smoke` | 验证桌面和手机页面无破图、横向滚动或控制台错误 |
| `npm install 包名` | 安装依赖 |
| `npm install 包名 --save-dev` | 安装开发依赖 |

---

## 九、注意事项

### 9.1 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| localhost:5173 拒绝连接 | Vue 未启动 | 运行 `npm run dev` |
| localhost:8000 拒绝连接 | Django 未启动 | 激活 venv 后 `python manage.py runserver` |
| 'npm' 命令找不到 | Node.js 未安装 | 检查 `node --version` |
| 'python' 命令找不到 | Python 未安装 | 检查 `python --version` |
| 激活 venv 报执行策略错误 | PowerShell 限制 | 用 `.\venv\Scripts\python.exe` 直接调用 |
| 数据库迁移报错 | 模型修改未迁移 | 运行 `makemigrations + migrate` |
| 图片 404 | 未放在 public/ 下 | 开发时放 `frontend/public/images/` |
| 表单显示提交失败 | Django 后端未启动 | 启动 `python manage.py runserver` 并确认 8000 端口可用 |
| 产品、新闻大量显示加载失败 | 8000 端口运行的是旧 Django 进程，新增 `/api/v1/` 路由返回 404 | 重启当前项目的 Django 服务，再访问 `http://localhost:8000/api/v1/homepage/` 确认返回 200 |
| Navicat 看不到新记录 | 数据表未刷新 | 右键 `xunpan` 或 `lianxi` 后选择刷新 |
| 切换生产模式后演示内容消失 | `SITE_CONTENT_MODE=production` 会隐藏演示和待核验内容 | 本地测试使用 `test`；正式内容需完成来源和核验后再发布 |

### 9.2 开发约定

- 代码注释使用中文
- 提交信息使用英文（feat: / fix: / chore:）
- 前后端分离，不混合
- Vue 组件 PascalCase 命名（NavBar.vue）
- URL 路径小写字母 + 连字符（/supply-chain）
- 用户为代码初学者，AI 解释命令作用
- 开发进度变化后同步更新 `AGENTS.md`，保证文档与代码一致

### 9.3 安全提醒

- SECRET_KEY 不要提交公开仓库，生产环境使用环境变量
- 管理员密码为开发环境使用，上线前更换强密码
- DEBUG = True 仅在开发环境，生产必须改为 False
- `.env`、数据库、私有附件、备份和恢复码均已加入 `.gitignore`，不得提交到 Git
- 生产配置使用 `huali_website.settings_production`，缺少密钥、域名、SMTP、备份密钥或未启用 ClamAV 时拒绝启动
- 已发布隐私政策不可覆盖修改，更新内容必须创建新版本；没有已发布政策时在线表单自动暂停
- 询盘限流为同一 IP 指纹 30 分钟 3 次，联系留言为 10 分钟 5 次
- 当前数据库已存在已发布隐私政策版本；更新内容必须创建新版本
- 本地开发环境已完成 163 SMTP 邮件队列发送验证；正式上线后仍需使用公网环境再次验收
- `.env.example` 只保留空白邮箱占位；真实邮箱配置必须写入被 Git 忽略的 `.env`
- 隐私政策编辑页提供“保存并发布”按钮；SimpleUI 左侧菜单提供“账号安全（TOTP）”直达入口
- Axes 和 django-otp 后台应用名称显示为“登录保护（Axes）”与“双重验证（OTP-TOTP）”
- 账号安全页面为 `/admin/security/security-center/`，展示 TOTP 设备、Axes 登录失败记录和安全登录记录
- 账号安全页面同时兼容 `/admin/security-center/security-center/`，用于 SimpleUI iframe 菜单跳转
- Quill 2.0.3 当前存在两个上游 low severity XSS 告警；项目仍使用 Bleach 白名单二次清洗，暂不强制降级以避免破坏表格插件
- `DEMO-` 产品、测试新闻、测试 FAQ、演示指标和测试 PDF 只用于本地验收；不得删除演示标识或把内容当作真实公司事实
- 媒体素材通过审核前必须登记许可；未知许可或不允许商业使用的素材不能通过后台审核

### 9.4 第二阶段验收结果

- Django 全量 36 项测试、`manage.py check`、迁移检查和生产安全检查通过
- Vue 生产构建通过，43 个公开页面完成 Chromium 全量预渲染，sitemap 包含 43 条 URL
- Playwright 完成 1440px 桌面和 390px 手机共 16 个页面组合，未发现控制台错误、破图或横向滚动
- SQLite 加密备份与临时目录恢复演练通过，业务数据保持为 1 条询盘、0 条联系留言、18 款产品和 9 条新闻
- 本地 Git 仓库已初始化，敏感文件和运行数据均已忽略；远端已关联 GitHub `origin/main`，公网部署仍等待域名和服务器

### 9.5 第三阶段里程碑一验收结果

- 已完成公司内容、荣誉管理、页面设计三个后台应用，以及通用数据库任务中心
- 数据库现有 30 款产品（12 款演示）、21 条新闻（12 条演示）、20 条 FAQ、8 条待核验荣誉和 4 份双语测试 PDF
- 8 个标准参数已建立，现有参数只生成待人工确认的映射建议，不自动改写产品参数
- `SITE_CONTENT_MODE`、生产发布拦截、素材许可校验、桌面/手机媒体变体和内容核验日期已完成
- 迁移前创建两份 AES-256 加密备份，迁移与种子导入保持 1 条询盘、0 条联系留言不变
- Django 全量 50 项测试、迁移检查、系统检查、OpenAPI 校验和 Vue 生产构建通过；PDF 已完成 4 页文本与视觉检查
- 里程碑二“完整中英文内容系统”尚未开始，必须等待用户浏览器验收后继续

### 9.6 后续开发方向

- [x] 在线询盘与联系留言接入 SQLite 和 Django API
- [x] 后台增加表单管理一级菜单及联系/询盘二级菜单
- [x] 补充产品、公司、新闻图片和产品/新闻详情页
- [x] 产品与新闻迁移到 Django 模型、后台和公开 API
- [x] 首页、产品中心、产品详情、新闻中心、新闻详情接入数据库 API
- [x] 询盘产品选项、产品详情自动带入型号、联系留言接入 `/api/v1/`
- [x] Vite 增加 `/media` 代理，前端生产构建通过
- [x] 供应链采购流程、核心品类、发展历程、荣誉资质、经销商权益补充场景图
- [x] 供应链和经销商页面采用桌面端约四分之一屏宽的真实图片侧边淡出布局
- [x] 供应链采购品类改为物料、零部件和生产环节展示，统一使用小型标题图标
- [x] 生成并接入采购、发展历程、荣誉与经销商专题 AI 图片，压缩为 WebP
- [x] 修复后台首页重复跳转闪烁，优化产品运营日期筛选并增加内容编辑入口
- [x] 将后台日期筛选升级为日历年月日的起始日期/截止日期区间筛选
- [x] 修复日期区间筛选在新闻和表单列表中的参数兼容与页面崩溃问题
- [x] 将日期筛选改为起始日期-截止日期双日期框，默认最近 30 日
- [x] 将产品、新闻、询盘和联系列表统一为新闻管理同款的独立原生日历日期框
- [x] 修复已绑定 TOTP 页面打不开问题，并为 Axes/OTP-TOTP 后台加入双语字段、编辑分组和独立日期筛选
- [x] 将运营后台隐私政策、邮件任务、审计日志、任务运行、系统告警、预渲染和备份列表统一接入新闻管理同款独立日历日期筛选
- [x] 增加运行中任务超过 2 小时自动标记失败并生成告警，修复卡住的备份运行记录
- [x] 为产品和新闻公开 API 设置唯一 OpenAPI 操作名称，消除接口名称冲突
- [x] 询盘和联系留言增加处理状态、负责人、内部备注、最后跟进时间及后台筛选
- [x] 后台支持选中询盘/留言导出 UTF-8 CSV 和 Excel
- [x] 询盘自动关联有效产品并在前端显示产品名称、型号和缩略图
- [ ] 集成中英文双语切换功能
- [x] 第三阶段里程碑一：结构化公司内容、荣誉、FAQ、标准参数、统一媒体库、任务中心和演示数据
- [ ] 第三阶段里程碑二：独立翻译表、术语库、AI 翻译队列、英文路由和语言切换
- [ ] 第三阶段里程碑三：GrapesJS 搭建器、全站视觉原型、AI 图片、动画和 3D
- [ ] 第三阶段里程碑四：搜索、对比、资料申请、高德地图和业务联动
- [ ] 第三阶段里程碑五：匿名统计、数据看板、双语预渲染和整体验收
- [ ] 接入高德/百度地图
- [x] 表单增加 CSRF、一次性令牌、隐私同意、风险验证码、蜜罐、限流和 IP HMAC 指纹
- [x] 询盘附件迁移为私有存储并增加文件签名、结构、图片解码与 ClamAV 扫描
- [x] 增加中英双语隐私政策版本、TOTP 双重验证、登录限流和关键业务审计日志
- [x] 增加数据库邮件队列、双语回执、销售通知、后台模板、手动跟进、附件和失败告警
- [x] 完成语义 URL、旧地址 301、canonical、结构化数据、43 页 Chromium 预渲染和 sitemap
- [x] 完成 SQLite 在线加密备份、恢复演练、健康看板和 Ubuntu 部署文件
- [x] 完成 GitHub Actions、Git 忽略规则、生产配置检查和浏览器验收
- [x] 清理当前数据库中的旧任务状态和历史备份告警，确认未解决告警为 0
- [ ] 经销商登录验证逻辑
- [ ] 购买服务器与域名后正式部署（Nginx + Gunicorn + systemd）
- [ ] 正式上线后使用真实域名和公网环境再次验收隐私政策、163 邮件、ClamAV、备份恢复和 HTTPS
- [x] 创建 GitHub 私有仓库并关联本地远端
- [x] 已更新 163 邮箱授权码并避免写入当前工作区文件；正式上线前仍应在 Git 历史中复核敏感信息

---

*本手册由 AI 辅助生成，如有内容过期请及时更新。*
