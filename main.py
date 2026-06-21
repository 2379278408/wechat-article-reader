#!/usr/bin/env python3
"""
微信公众号文章读取工具
绕过 robots.txt 限制，直接获取并解析微信文章 HTML，转为 Markdown 输出。
"""

import sys
import re
import html
import json
from coze_workload_identity import requests


def fetch_wechat_article(url: str) -> dict:
    """获取微信公众号文章并解析为结构化内容"""
    
    # 验证 URL 域名
    if "mp.weixin.qq.com" not in url:
        return {"error": "仅支持微信公众号文章链接（mp.weixin.qq.com）"}
    
    # 模拟浏览器请求
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.encoding = "utf-8"
        content = resp.text
    except Exception as e:
        return {"error": f"请求失败: {str(e)}"}
    
    if resp.status_code == 404:
        return {"error": "文章不存在或已被删除"}
    if resp.status_code != 200:
        return {"error": f"HTTP 错误: {resp.status_code}"}
    
    # 提取标题
    title = ""
    # 尝试从 var msg_title 提取
    title_match = re.search(r'var\s+msg_title\s*=\s*["\'](.+?)["\']', content)
    if title_match:
        title = html.unescape(title_match.group(1))
    # 备选：从 og:title 提取
    if not title:
        title_match = re.search(r'property="og:title"\s+content="([^"]+)"', content)
        if title_match:
            title = html.unescape(title_match.group(1))
    # 备选：从 activity-name 提取
    if not title:
        title_match = re.search(r'id="activity-name"[^>]*>(.*?)</h\d>', content, re.DOTALL)
        if title_match:
            title = html.unescape(title_match.group(1).strip())
    
    # 提取作者/公众号名称
    author = ""
    author_match = re.search(r'var\s+nickname\s*=\s*["\'](.+?)["\']', content)
    if author_match:
        author = html.unescape(author_match.group(1))
    if not author:
        author_match = re.search(r'id="profileBt"[^>]*>.*?<a[^>]*>(.*?)</a>', content, re.DOTALL)
        if author_match:
            author = html.unescape(author_match.group(1).strip())
    if not author:
        author_match = re.search(r'class="profile_nickname"[^>]*>(.*?)</strong>', content, re.DOTALL)
        if author_match:
            author = html.unescape(author_match.group(1).strip())
    
    # 提取正文内容
    article_html = ""
    # 从 js_content div 提取
    content_match = re.search(r'id="js_content"[^>]*>(.*?)</div>\s*(?:<script|<div\s+class="rich_media_tool)', content, re.DOTALL)
    if content_match:
        article_html = content_match.group(1)
    
    if not article_html:
        # 备选：尝试从 rich_media_content 提取
        content_match = re.search(r'class="rich_media_content"[^>]*>(.*?)</div>\s*(?:<script|<div\s+class="rich_media_tool)', content, re.DOTALL)
        if content_match:
            article_html = content_match.group(1)
    
    if not article_html:
        # 检查是否是"关注后查看"类型
        if "关注后查看" in content or "关注公众号" in content:
            return {"error": "该文章需要关注公众号后才能查看完整内容"}
        return {"error": "无法提取文章正文，页面结构可能已变化"}
    
    # HTML 转 Markdown
    markdown = html_to_markdown(article_html)
    
    return {
        "title": title or "未知标题",
        "author": author or "未知公众号",
        "content": markdown
    }


def html_to_markdown(html_str: str) -> str:
    """将微信文章 HTML 转为简洁的 Markdown"""
    
    # 处理图片：提取 data-src 或 src
    def replace_img(match):
        img_tag = match.group(0)
        # 优先取 data-src（微信懒加载）
        src_match = re.search(r'data-src="([^"]+)"', img_tag)
        if not src_match:
            src_match = re.search(r'src="([^"]+)"', img_tag)
        if src_match:
            return f"\n![图片]({src_match.group(1)})\n"
        return ""
    
    # 处理链接
    def replace_link(match):
        href = match.group(1) or ""
        text = re.sub(r"<[^>]+>", "", match.group(2)).strip()
        if not text:
            return ""
        if href and href.startswith("http"):
            return f"[{text}]({href})"
        return text
    
    # 先处理块级元素（添加换行）
    html_str = re.sub(r'<br\s*/?>', '\n', html_str)
    html_str = re.sub(r'</p>', '\n\n', html_str)
    html_str = re.sub(r'</div>', '\n', html_str)
    html_str = re.sub(r'</h([1-6])>', lambda m: '\n\n', html_str)
    html_str = re.sub(r'<h([1-6])[^>]*>', lambda m: '#' * int(m.group(1)) + ' ', html_str)
    html_str = re.sub(r'</li>', '\n', html_str)
    html_str = re.sub(r'<li[^>]*>', '- ', html_str)
    html_str = re.sub(r'</blockquote>', '\n', html_str)
    html_str = re.sub(r'<blockquote[^>]*>', '> ', html_str)
    
    # 处理粗体和斜体
    html_str = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', html_str, flags=re.DOTALL)
    html_str = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', html_str, flags=re.DOTALL)
    html_str = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', html_str, flags=re.DOTALL)
    html_str = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', html_str, flags=re.DOTALL)
    
    # 处理图片（在移除其他标签前）
    html_str = re.sub(r'<img[^>]+>', replace_img, html_str)
    
    # 处理链接
    html_str = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', replace_link, html_str, flags=re.DOTALL)
    
    # 移除所有剩余 HTML 标签
    html_str = re.sub(r'<[^>]+>', '', html_str)
    
    # HTML 实体解码
    html_str = html.unescape(html_str)
    
    # 清理多余空白
    html_str = re.sub(r'&nbsp;', ' ', html_str)
    html_str = re.sub(r'\n{3,}', '\n\n', html_str)
    html_str = html_str.strip()
    
    return html_str


def main():
    if len(sys.argv) < 2:
        print("用法: python main.py <微信文章URL>", file=sys.stderr)
        sys.exit(1)
    
    url = sys.argv[1]
    result = fetch_wechat_article(url)
    
    if "error" in result:
        print(f"❌ {result['error']}", file=sys.stderr)
        sys.exit(1)
    
    # 输出格式化的 Markdown
    print(f"# {result['title']}")
    print(f"作者：{result['author']}")
    print()
    print(result['content'])


if __name__ == "__main__":
    main()
