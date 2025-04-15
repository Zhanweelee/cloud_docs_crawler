import requests
from bs4 import BeautifulSoup
import pdfkit
import os
import re
from urllib.parse import urljoin
import argparse

# 输出目录
OUTPUT_DIR = 'output'

# 待处理 URL 列表
PENDING_URL_LIST = []

# 已处理 URL 列表
PROCESSED_URL_LIST = []


def get_menu_links(url):
    """获取菜单中的所有链接"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 输出 html 内容
        filename = os.path.join(OUTPUT_DIR, "html", "root.html")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)
        
        # 找到id为common-menu-container的ul标签
        menu_container = soup.find('ul', {'id': 'common-menu-container'})
        if not menu_container:
            print("未找到菜单容器")
            return []
        
        # 获取所有a标签的链接
        links = []
        for a_tag in menu_container.find_all('a'):
            href = a_tag.get('href')
            text = a_tag.get_text().strip()
            if href:
                # 将相对URL转换为绝对URL
                absolute_url = urljoin(url, href)
                links.append(absolute_url)
                print(f"找到菜单项: {text} -> {absolute_url}")
        return links
    except Exception as e:
        print(f"获取菜单链接时出错: {str(e)}")
        return []

def save_page_as_pdf(url):
    """将页面保存为PDF"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 获取页面标题
        title = soup.find('title').text.strip()

        # URL Example: https://help.aliyun.com/zh/cs/product-overview/product-billing-rules
        # 获取 URL 结构，不包含域名，取最后一个 / 后面的内容
        url_path = url.split('/')[1:-1]
        dir_sub_path = '/'.join(url_path)

        # 清理文件名中的非法字符
        filename = os.path.join(OUTPUT_DIR, "pdf", dir_sub_path, re.sub(r'[\\/*?:"<>|]', '_', title) + '.pdf')
        # 创建 Pdf 输出目录
        if not os.path.exists(os.path.join(OUTPUT_DIR, "pdf", dir_sub_path)):
            os.makedirs(os.path.join(OUTPUT_DIR, "pdf", dir_sub_path))

        # 创建 Html 输出目录
        html_filename = os.path.join(OUTPUT_DIR, "html", dir_sub_path, re.sub(r'[\\/*?:"<>|]', '_', title) + '.html')
        if not os.path.exists(os.path.join(OUTPUT_DIR, "html", dir_sub_path)):
            os.makedirs(os.path.join(OUTPUT_DIR, "html", dir_sub_path))

        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"已保存: {html_filename}")

        print(f"页面标题: {title}")
        print(f"页面HTML: {response.text}")

        # 从侧边栏菜单，找到子页面 URL
        main_content = soup.find('div', {'id': 'pc-markdown-container'})
        if main_content:
            sub_urls = main_content.find_all('ul')
            sub_urls = [a for ul in sub_urls for a in ul.find_all('a')]
        else:
            sub_urls = []
        for sub_url in sub_urls:
            href = sub_url.get('href')
            if href:
                sub_url = urljoin(url, href)
                PENDING_URL_LIST.append(sub_url)
        
        # 找到主要内容区域
        main_content = soup.find('div', {'id': 'pc-markdown-container'})
        if not main_content:
            print(f"未找到主要内容区域: {url}")
            return
        
        # 创建临时HTML文件
        temp_html = os.path.join(OUTPUT_DIR, "temp.html")
        # 创建完整的HTML结构
        temp_content = f"""<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8"/><title>{title}</title></head><body>{str(main_content)}</body></html>"""
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(temp_content)
        
        # 转换为PDF
        pdfkit.from_file(temp_html, filename)
        
        # 删除临时文件
        os.remove(temp_html)
        
        print(f"已保存: {filename}")
    except Exception as e:
        print(f"处理页面时出错 {url}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='阿里云产品页面爬虫')
    parser.add_argument('url', help='起始URL')
    args = parser.parse_args()
    
    # 获取所有菜单链接
    print("正在获取菜单链接...")
    links = get_menu_links(args.url)
    print(f"找到 {len(links)} 个链接")
    PENDING_URL_LIST.extend(links)

    # 处理每个链接
    while PENDING_URL_LIST:
        link = PENDING_URL_LIST.pop(0)
        if link in PROCESSED_URL_LIST:
            continue
        print(f"正在处理页面: {link}")
        save_page_as_pdf(link)
        PROCESSED_URL_LIST.append(link)

if __name__ == '__main__':
    main() 