# 微信公众号文章读取 Skill

读取微信公众号文章内容，将 `mp.weixin.qq.com` 链接转为可读 Markdown。

## 为什么需要这个 Skill

微信公众号的 `robots.txt` 禁止了自动化访问，导致 `fetch_web`、`curl`（默认）等工具无法直接读取 `mp.weixin.qq.com` 下的文章内容。本 Skill 通过模拟浏览器请求获取页面 HTML，解析标题、作者和正文，转为结构化 Markdown 输出。

## 功能特性

- 🚀 绕过 robots.txt 限制，直接读取微信文章
- 📝 输出标准 Markdown 格式（标题、作者、正文、链接、粗体、引用等）
- 🖼️ 保留文章中的图片链接
- 🔗 保留文章中的超链接
- ⚡ 零依赖，纯 Python 标准库 + `coze_workload_identity`
- 🛡️ 无需 API Key 或第三方服务

## 使用方式

### 命令行

```bash
python main.py "https://mp.weixin.qq.com/s/xxxxxxxxx"
```

### 输出格式

```
# {文章标题}
作者：{公众号名称}

{文章正文，Markdown 格式}
```

### 在 Claw/Coze Agent 中使用

将本仓库 clone 到 `skills/wechat-article-reader/` 目录下，Agent 遇到微信文章链接时会自动调用。

## 安装

```bash
# 克隆到 skills 目录
cd skills/
git clone https://github.com/2379278408/wechat-article-reader.git wechat-article-reader
```

## 技术原理

1. 模拟浏览器 User-Agent 发起 HTTP GET 请求
2. 从 HTML 中提取 `msg_title`（标题）和 `nickname`（公众号名称）
3. 定位 `js_content` div 提取正文 HTML
4. 将 HTML 元素（标题/段落/链接/图片/粗体/引用等）转为 Markdown
5. 输出结构化结果

## 边界情况处理

| 场景 | 处理方式 |
|------|---------|
| 非 mp.weixin.qq.com 域名 | 提示仅支持微信公众号文章 |
| 文章已删除/404 | 返回"文章不可访问" |
| 需要关注才能查看 | 提示可能需要关注公众号 |
| 超长文章 | 完整输出，不截断 |

## License

MIT
