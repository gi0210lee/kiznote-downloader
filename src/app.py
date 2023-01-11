import os
import requests
import time
import util
from datetime import datetime
from bs4 import BeautifulSoup

dir_output = 'output/'

custom_headers = {
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'cookie': 'sessionid=v8but91g9z6mpvwijnrov1nh7evwlqpd; current_user=dayomi; _hjSessionUser_3251788=eyJpZCI6IjNmZDdjZjE2LTBmN2ItNTlkMy05MDM2LTAzNGE5OGFjZjA2YSIsImNyZWF0ZWQiOjE2NzMzOTgwOTQ5ODcsImV4aXN0aW5nIjp0cnVlfQ==; csrftoken=GS4bUiUxOyMMQHoMFNj2Z8WdFv0eeYouZfU7kWnY4iHD7NFJs1S7lDelP2CPCscB; _gid=GA1.2.109501274.1673398107; _ga_6HBPNX8FC2=GS1.1.1673398094.1.1.1673399130.0.0.0; _ga=GA1.2.687922305.1673398094; _gat=1'
}
base_url = 'https://www.kidsnote.com'
report_url = base_url + '/reports' + '/'
alnums_url = base_url + '/albums' + '/'


# 알림장 마지막 페이지 구하기
res = requests.get(report_url, headers=custom_headers)
soup = BeautifulSoup(res.content, 'html.parser')
page_list = soup.find_all('a', class_='page-link')

number = 0
last_page = 0
for i in page_list:
    number = number + 1
last_page = page_list[number - 2].text

page = 0
while page <= int(last_page):
    page = page + 1
    # 알림장 페이지 별 목록
    report_page_url = report_url + '?page=' + str(page)
    res = requests.get(report_page_url, headers=custom_headers)

    soup = BeautifulSoup(res.content, 'html.parser')
    a_list = soup.find('div', class_='report-list-wrapper').find_all('a')

    href_list = []
    for href in a_list:
        href_list.append(href['href'])

    for href_item in href_list:
        # 알림장 상세 페이지
        detail_url = base_url + href_item
        res = requests.get(detail_url, headers=custom_headers)
        soup = BeautifulSoup(res.content, 'html.parser')

        # 타이틀, 본문
        sTitle = soup.find('h3', class_='sub-header-title').text.strip()
        # dtTitle = datetime.strptime(sTitle, '%Y년 %m월 %d일 %A')
        print(sTitle)
        # title = datetime.strftime(dtTitle, '%Y%m%d')
        # print(Title)

        exit()

        # 타이틀 명으로 폴더 생성
        path = dir_output + title + '/'
        util.createFolder(path)

        # 본문 이쁘게
        contentString = soup.find('div', class_='content-text')
        contentString_list = []
        for s in contentString:
            contentString_list.append(s.text)
        content_body = '\n'.join(contentString_list)

        # 댓글
        comment_list = soup.find(
            'ul', class_='comment-list').find_all('li', class_='comment')
        if comment_list is not None:
            comment_body_list = []
            for comment_item in comment_list:
                comment_author = comment_item.find(
                    'span', class_='author-name').text
                comment_time = comment_item.find(
                    'span', class_='date-written').text
                commentString = comment_item.find('p')
                commentString_list = []
                for s in commentString:
                    commentString_list.append(s.text)
                commentStr = '\n'.join(commentString_list)
                comment_body_list.append(comment_author + '\n' +
                                         comment_time + '\n' + commentStr + '\n')
            comment_body = '\n'.join(comment_body_list)

        # 텍스트 파일로 본문 댓글 저장
        filename = path + title + '.txt'
        report = 'ㅁ 일시' + '\n' + title + '\n\n' + \
            'ㅁ 본문' + '\n' + content_body + '\n\n' + \
            'ㅁ 댓글' + '\n' + comment_body
        util.SaveFile(filename, report)

        # 이미지 다운로드
        img_grid = soup.find('div', class_='image-section')
        if img_grid is not None:
            imgs = img_grid.find_all('div', class_='grid')
            for img in imgs:
                download_url = img.find('a')['data-download']
                name, ext = os.path.splitext(download_url)
                img_name = title + '-' + img['data-index'] + ext
                start = time.time()

                fullPath = path + img_name
                res = requests.get(download_url)
                os.system(f'curl "{download_url}" --output {fullPath}')