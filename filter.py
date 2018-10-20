# -*- coding:utf-8 -*-
"""
规则过滤指定类型资讯
"""
import codecs
import json

def filter_with_rule():
    filter_dict = []
    for line in codecs.open('WordsDic/filter.txt', encoding='utf8'):
        line = line.strip()
        filter_dict.append(line)
    fout = codecs.open('news_for_day/%d_ner_filter.txt' % day, 'w', encoding='utf8')
    total = 0
    total_filter = 0
    for line in codecs.open('news_for_day/%d_ner.txt' % day, encoding='utf8'):
        total += 1
        line_dict = json.loads(line)
        title = line_dict['title']
        text = line_dict['text']
        flag = True
        for ele in filter_dict:
            if ele in text:
                print(ele, text)
                flag = False
                total_filter += 1
                break
        if flag == True:
            fout.write(line)
    print(total_filter)
    print(total)


if __name__ == '__main__':
    num_of_days = 1
    for day in range(num_of_days):
        day = day + 1
        filter_with_rule()





