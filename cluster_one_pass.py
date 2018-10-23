# -*- encoding:utf8 -*-
'''
one pass聚类
'''
from datetime import datetime
import codecs
import json
from gensim import corpora
import numpy as np
from gensim import corpora, models, similarities

def one_pass_cluster():
    # 添加"type"字段，保存聚类结果
    data = []
    for line in codecs.open('news_for_day/%d_ner_filter.txt' % day, encoding='utf8'):
        line = json.loads(line)
        line['type'] = -1
        data.append(line)

    # 获取文本特征，添加"feature_ner_tfidf"和"feature_ner_lsi"字段，保存文本的ner特征
    texts = []
    for news in data:
        text = news['text_ner']
        texts.append(text)
    dictionary = corpora.Dictionary(texts)
    length_of_dictionary = len(dictionary)
    print("length of dictionary: ", length_of_dictionary)
    doc_vectors = [dictionary.doc2bow(text) for text in texts]
    # TF-IDF特征
    tfidf = models.TfidfModel(doc_vectors)
    tfidf_vectors = tfidf[doc_vectors]
    # LSI特征
    lsi = models.LsiModel(tfidf_vectors, id2word=dictionary, num_topics=num_topics)
    lsi_vectors = lsi[tfidf_vectors]
    for i, ele in enumerate(data):
        ele['feature_ner_tfidf'] = tfidf_vectors[i]
        ele['feature_ner_lsi'] = lsi_vectors[i]

    # one pass聚类
    result = {0:[0]}
    for i, news in enumerate(data):
        print(i)
        if i == 0:
            continue
        feature_ner_lsi_now = news['feature_ner_lsi']
        if len(feature_ner_lsi_now) == 0:
            result[len(result)] = [i]
        else:
            flag = False
            for key in result:
                index = result[key][0]
                feature_ner_lsi = data[index]['feature_ner_lsi']
                if len(feature_ner_lsi) == 0:
                    continue
                index_lsi = similarities.MatrixSimilarity([feature_ner_lsi_now])
                sims_lsi = index_lsi[feature_ner_lsi][0]
                if sims_lsi >= 0.9:
                    result[key].append(i)
                    flag = True
                    break
            if flag == False:
                result[len(result)] = [i]

    # 保存聚类结果，写入文件
    fout = codecs.open('result_one_pass/%d.txt' % day, 'w', encoding='utf8')
    for key in result:
        value = result[key]
        for index in value:
            news = data[index]
            _id = news['id']
            title = news['title']
            text = news['text']
            strObj = str(_id) + '#' + title + '#' + text + '\n'
            fout.write(strObj)
    fout.close()


if __name__ == '__main__':
    num_of_days = 1
    num_topics = 500
    for day in range(num_of_days):
        d0 = datetime.now()
        day = day + 1
        print('cluster for day %d' % day)
        one_pass_cluster()
        d1 = datetime.now()
        print(d0, d1, d1 - d0)

