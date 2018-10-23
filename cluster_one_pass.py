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
    tfidf_vectors, lsi_vectors = get_tfidf_and_lsi(texts)
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
            strObj = str(key) + '#' + str(_id) + '#' + title + '#' + text + '\n'
            fout.write(strObj)

def computeSimilarity_lsm(X, query):
    index = similarities.MatrixSimilarity(X)
    sims = index[query]
    scoreList = list(enumerate(sims))
    rankList = [scoreList[i][1] for i in range(len(scoreList))]
    return rankList

def get_tfidf_and_lsi(corpus):
    dictionary = corpora.Dictionary(corpus)
    length_of_dictionary = len(dictionary)
    doc_vectors = [dictionary.doc2bow(text) for text in corpus]
    # TF-IDF特征
    tfidf = models.TfidfModel(doc_vectors)
    tfidf_vectors = tfidf[doc_vectors]
    # LSI特征
    lsi = models.LsiModel(tfidf_vectors, id2word=dictionary, num_topics=num_topics)
    lsi_vectors = lsi[tfidf_vectors]
    return tfidf_vectors, lsi_vectors

def one_pass_cluster2():
    data = []
    for line in codecs.open('news_for_day/%d_ner_filter.txt' % day, encoding='utf8'):
        line = json.loads(line)
        line['type'] = -1
        data.append(line)

    # 获取实体特征，添加"feature_ner_tfidf"和"feature_ner_lsi"字段
    ners = []
    for news in data:
        text = news['text_ner']
        ners.append(text)
    tfidf_vectors_ner, lsi_vectors_ner = get_tfidf_and_lsi(ners)
    for i, ele in enumerate(data):
        ele['feature_ner_tfidf'] = tfidf_vectors_ner[i]
        ele['feature_ner_lsi'] = lsi_vectors_ner[i]

    # 获取关键词特征，添加"feature_k_tfidf"和"feature_k_lsi"字段
    keywords = []
    for news in data:
        text = news['text_keywords']
        text = [ele[0] for ele in text]
        keywords.append(text)
    tfidf_vectors_k, lsi_vectors_k = get_tfidf_and_lsi(keywords)
    for i, ele in enumerate(data):
        ele['feature_k_tfidf'] = tfidf_vectors_k[i]
        ele['feature_k_lsi'] = lsi_vectors_k[i]

    # one pass聚类
    result = {0: [0]}
    for i, news in enumerate(data):
        print(i)
        if i == 0:
            continue
        feature_ner_lsi_now = news['feature_ner_lsi']
        feature_k_lsi_now = news['feature_k_lsi']
        if len(feature_ner_lsi_now) == 0:
            result[len(result)] = [i]
        else:
            scores_ner = {}
            scores_k = {}
            for key in result:
                value = result[key]
                X_ner = []
                for index in value:
                    X_ner.append(data[index]['feature_ner_lsi'])
                if len(X_ner) == 1 and len(X_ner[0]) == 0:
                    continue
                X_k = []
                for index in value:
                    X_k.append(data[index]['feature_k_lsi'])
                scoreList_ner = computeSimilarity_lsm(X_ner, feature_ner_lsi_now)
                scoreList_k = computeSimilarity_lsm(X_k, feature_k_lsi_now)
                score_average_ner = sum(scoreList_ner) / len(scoreList_ner)
                score_average_k = sum(scoreList_k) / len(scoreList_k)
                scores_ner[key] = score_average_ner
                scores_k[key] = score_average_k
            scores_sort_ner = sorted(scores_ner.items(), key=lambda d: d[1], reverse=True)
            scores_sort_k = sorted(scores_k.items(), key=lambda d: d[1], reverse=True)
            max_score_ner = scores_sort_ner[0][1]
            max_score_ner_index = scores_sort_ner[0][0]
            max_score_k = scores_sort_k[0][1]
            max_score_k_index = scores_sort_k

            if max_score_ner >= 0.85 and max_score_k > 0.5 and max_score_ner_index == max_score_k_index:
                result[scores_sort_ner[0][0]].append(i)
            else:
                result[len(result)] = [i]

    # 保存聚类结果，写入文件
    fout = codecs.open('result_one_pass/%d_.txt' % day, 'w', encoding='utf8')
    for key in result:
        value = result[key]
        for index in value:
            news = data[index]
            _id = news['id']
            title = news['title']
            text = news['text']
            strObj = str(key) + '#' + str(_id) + '#' + title + '#' + text + '\n'
            fout.write(strObj)


if __name__ == '__main__':
    num_of_days = 1
    num_topics = 500
    for day in range(num_of_days):
        d0 = datetime.now()
        day = day + 1
        print('cluster for day %d' % day)
        # one_pass_cluster()
        one_pass_cluster2()
        d1 = datetime.now()
        print(d0, d1, d1 - d0)

