import requests
from bs4 import BeautifulSoup
import pdfkit
import os
import re
from urllib.parse import urljoin
import argparse

OUTPUT_DIR = 'output'

def get_menu_links(url):
    """获取菜单中的所有链接"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
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
        # 清理文件名中的非法字符

        filename = os.path.join(OUTPUT_DIR, "pdf", re.sub(r'[\\/*?:"<>|]', '_', title) + '.pdf')
        # 创建 Pdf 输出目录
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        if not os.path.exists(os.path.join(OUTPUT_DIR, "pdf")):
            os.makedirs(os.path.join(OUTPUT_DIR, "pdf"))

        # 创建 Html 输出目录
        html_filename = os.path.join(OUTPUT_DIR, "html", re.sub(r'[\\/*?:"<>|]', '_', title) + '.html')
        if not os.path.exists(os.path.join(OUTPUT_DIR, "html")):
            os.makedirs(os.path.join(OUTPUT_DIR, "html"))

        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"已保存: {html_filename}")

        print(f"页面标题: {title}")
        print(f"页面HTML: {response.text}")
        
        # 找到主要内容区域
        main_content = soup.find('div', {'id': 'pc-markdown-container'})
        if not main_content:
            print(f"未找到主要内容区域: {url}")
            return
        
        # 创建临时HTML文件
        temp_html = 'temp.html'
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(str(main_content))
        
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
    
    # 处理每个链接
    for i, link in enumerate(links, 1):
        print(f"正在处理第 {i}/{len(links)} 个页面: {link}")
        save_page_as_pdf(link)

if __name__ == '__main__':
    main() 