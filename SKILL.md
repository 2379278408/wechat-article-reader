---
name: wechat-article-reader
description: 读取微信公众号文章内容，将 mp.weixin.qq.com 链接转为可读 Markdown。当用户提供微信公众号文章链接、要求读取微信文章、读取公众号内容、或 fetch_web 因 robots.txt 无法访问微信文章时使用此技能。
---

# 微信公众号文章读取

将微信公众号文章 URL 转为结构化 Markdown 内容。解决 fetch_web 因 robots.txt 无法读取 mp.weixin.qq.com 的问题。

## 工作流程

1. 从用户消息中提取微信公众号文章 URL（格式通常为 `https://mp.weixin.qq.com/s/xxxxx`）
2. 调用 `main.py` 传入 URL，获取解析后的 Markdown 内容
3. 将结果返回给用户，格式为：标题 + 作者 + 正文内容

## 输入格式

命令行参数：`python main.py <微信文章URL>`

URL 必须为 mp.weixin.qq.com 域名下的链接。

## 输出格式

```
# {文章标题}
作者：{公众号名称}

{文章正文，Markdown格式}
```

## 边界情况处理

- URL 不是 mp.weixin.qq.com 域名 → 提示用户该技能仅支持微信公众号文章
- 页面返回404或已删除 → 告知文章不可访问
- 内容为空（可能需要关注公众号才能查看）→ 提示可能需要关注公众号
- 超长文章 → 正常输出全部内容，不要截断

## 技术原理

微信公众号的 robots.txt 禁止了自动化访问，导致 fetch_web 等工具无法读取。但直接发起 HTTP 请求获取 HTML 并解析是可行的。本技能绕过 robots.txt 限制，模拟浏览器请求获取页面 HTML，然后从中提取标题、作者和正文内容，转为 Markdown 格式输出。
