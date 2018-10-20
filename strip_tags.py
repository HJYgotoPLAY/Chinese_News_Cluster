# -*- coding: utf-8 -*-
#数据清洗（去除HTML标签）
def strip_tags(html):
    import re
    dr = re.compile(r'<[^>.*]+>', re.S)
    dd = dr.sub('', html)
    return dd