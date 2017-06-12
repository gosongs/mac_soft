#coding=utf-8
import requests
from bs4 import BeautifulSoup
import json
import re
import codecs
from xlrd import open_workbook

soft_links = []  # 存储所有的软件链接
soft_infos = []  # 存储抓到的下载链接

# 登录信息
UA = {
    "cookies": {
        "WP-LastViewedPosts":
        'a%3A2%3A%7Bi%3A0%3Bi%3A16696%3Bi%3A1%3Bi%3A16817%3B%7D',
        "Hm_lvt_38b7a5944c7219988e967cef466aac05":
        '1497270663',
        "Hm_lpvt_38b7a5944c7219988e967cef466aac05":
        '1497270797',
        "wordpress_test_cookie":
        'WP+Cookie+check',
        "wordpress_logged_in_9f5f042dd0580d4581aa22aeb45e8cc2":
        'by_openwater%7C1497443470%7CB1z3j10Twzhf3IQGENFQdpECkBTBx31H8v0tQbBrsOn%7C550c62b296966ae6045e121a2871cb4c69eaebe4d462b5a08f96a6c86acb694a'
    },
    "headers": {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
}


def url_to_soup(url):
    res = requests.get(url, cookies=UA['cookies'], headers=UA['headers'])
    return BeautifulSoup(res.content, 'lxml')


# 获取所有分类的链接
def get_cate_urls():
    urls = []
    main_url = 'http://www.ifunmac.com/category/'
    url_prefix = 'http://www.ifunmac.com'
    links = url_to_soup(main_url).select('ul#soft_category li span a')
    for link in links:
        href = link.get('href')
        if href is not None:
            urls.append(url_prefix + href)
    return urls


# 获取分类下所有软件的链接
def get_soft_urls(cate_url):
    all_pages = [cate_url]  # 当前分类下的每个分页的链接
    soup = url_to_soup(cate_url)
    multi_pages = len(soup.select('div#pagenavi span.pages'))
    if multi_pages != 0:
        # 多页
        page_text = soup.select('div#pagenavi span.pages')[0].get_text()
        total_num = re.findall(r'\d+', page_text)[-1]
        # http://www.ifunmac.com/category/app/remote-control/page/2/
        for i in range(2, int(total_num) + 1):
            all_pages.append(cate_url + 'page/' + str(i) + '/')
    for j in all_pages:
        page_soup = url_to_soup(j)
        page_soft_links = page_soup.select('div.archive_title h2 a')
        for k in page_soft_links:
            get_down_link(k.get('href'))


# 通过软件链接爬取软件的下载地址
def get_down_link(soft_url):
    soft_info = {'name': '', 'download': ''}
    soup = url_to_soup(soft_url)
    soft_info['name'] = soup.select('h2.entry_title')[0].get_text()

    is_vip = soup.select('div#entry > div.download-info')
    if len(is_vip) == 0:
        # 没有限制, 直接下载
        download = soup.select('div#entry > h3 + p')[-1]
    else:
        for i in soup.select('div#entry div.download-info a.btn-download'):
            true_soup = url_to_soup(i.get('href'))
            download = true_soup.select('div.container dl')[-3]
    # print download
    soft_info['download'] = str(download).replace('\n', '').replace('"', '\'')
    write_json(soft_info)


def write_json(soft_info):
    convert_info = json.dumps(soft_info).decode("unicode-escape")
    f = codecs.open('data.json', 'a', encoding='utf-8')
    # f = open('data.json', 'a')
    f.write(convert_info)
    f.write(',\n')
    f.close()


def write_excel():
    wb = open_workbook('data.xls', 'rb')
    for s in wb.sheets():
        print 'Sheet:', s.name
        for row in range(s.nrows):
            values = []
            for col in range(s.ncols):
                values.append(s.cell(row, col).value)
            print ",".join(values)
        print


def init():
    for i in get_cate_urls():
        get_soft_urls(i)


write_excel()