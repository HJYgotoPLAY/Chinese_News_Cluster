# -*- coding:utf-8 -*-
"""
下载资讯
"""
from urllib import request
import json
import codecs
from strip_tags import strip_tags

def get_total_number_of_news_for_day(start, end):
    '''
    返回从start到end时间段内总的资讯数目
    '''
    try:
        url = "http://info.zq88.cn:9085//news/advancedSearch.do?symbol=&page=1&size=1&start=%d&end=%d&theme=&keyword=&fulltext=&title=&searchType=2&classify=&isFacet=false&group=false" % (start, end)
        response = request.urlopen(url)
        data = response.read().decode('utf8')
    except Exception as e:
        print(e)
    linedata = json.loads(data)
    totalPage = linedata['totalPage']
    return totalPage

def download_news(start, end, totalPage):
    '''
    根据列表页资讯id索引资讯详情页，下载资讯标题和正文
    '''
    fout = codecs.open('news_for_day/5.txt', 'w', encoding='utf8')
    try:
        url = "http://info.zq88.cn:9085//news/advancedSearch.do?symbol=&page=1&size=%d&start=%d&end=%d&theme=&keyword=&fulltext=&title=&searchType=2&classify=&isFacet=false&group=false" % (totalPage, start, end)
        data = request.urlopen(url).read().decode('utf8')
    except Exception as e:
        print(e)
    linedata = json.loads(data)
    newsList = linedata['newsList']
    count = 0
    for newsdict in newsList:
        count += 1
        newsid = newsdict['id']
        print(count, newsid)
        try:
            url = "http://info.zq88.cn:9085//news/detail.do?id=%s" % newsid
            newsdata = request.urlopen(url).read().decode('utf8')
        except Exception as e:
            print(e)
        lineNews = json.loads(newsdata)
        title = lineNews['title']
        content = strip_tags(lineNews['content']).replace('\n','').replace('\r','')
        strObj = str(count) + '#' + title + '#' + content + '\n'
        fout.write(strObj)
    fout.close()


if __name__ == '__main__':

    start = 1539273600000  # 20181012
    end = 1539360000000  # 20181013

    totalPage = get_total_number_of_news_for_day(start, end)
    print('totalPage: ', totalPage)
    download_news(start, end, totalPage)


