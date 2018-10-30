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

def computeSimilarity_lsm(X, query):
    # 余弦相似度
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

def one_pass_cluster():
    data = []
    for line in codecs.open('news_for_day/%d_ner_filter.txt' % day, encoding='utf8'):
        line = json.loads(line)
        line['type'] = -1
        data.append(line)

    # 获取实体特征，添加"feature_ner_lsi"字段
    ners = []
    for news in data:
        text = news['text_ner']
        ners.append(text)
    tfidf_vectors_ner, lsi_vectors_ner = get_tfidf_and_lsi(ners)
    for i, ele in enumerate(data):
        ele['feature_ner_lsi'] = lsi_vectors_ner[i]

    # 获取关键词特征，添加"feature_word_lsi"字段
    words = []
    for news in data:
        text = news['text_noun']
        text.extend(news['text_verb'])
        words.append(text)
    tfidf_vectors_word, lsi_vectors_word = get_tfidf_and_lsi(words)
    for i, ele in enumerate(data):
        ele['feature_word_lsi'] = lsi_vectors_word[i]

    result = {0: [0]}
    for i, news in enumerate(data):
        print(i)
        if i == 0:
            continue
        feature_ner_lsi_now = news['feature_ner_lsi']
        feature_word_lsi_now = news['feature_word_lsi']
        if len(feature_word_lsi_now) == 0:
            result[len(result)] = [i]
        else:
            flag = False
            for key in result:
                index = result[key][0]
                feature_ner_lsi = data[index]['feature_ner_lsi']
                feature_word_lsi = data[index]['feature_word_lsi']
                if len(feature_word_lsi) == 0:
                    continue
                index_word_lsi = similarities.MatrixSimilarity([feature_word_lsi_now])
                sims_word_lsi = index_word_lsi[feature_word_lsi][0]
                if len(feature_ner_lsi_now) == 0 or len(feature_ner_lsi) == 0:
                    sims_ner_lsi = 0
                else:
                    index_ner_lsi = similarities.MatrixSimilarity([feature_ner_lsi_now])
                    sims_ner_lsi = index_ner_lsi[feature_ner_lsi][0]
                if sims_word_lsi >= 0.85 and sims_ner_lsi >= 0.35:
                    result[key].append(i)
                    flag = True
                    break
                elif sims_word_lsi >= 0.8 and sims_ner_lsi == 0:
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
    fout.close()

def one_pass_cluster2():
    data = []
    for line in codecs.open('news_for_day/%d_ner_filter.txt' % day, encoding='utf8'):
        line = json.loads(line)
        line['type'] = -1
        data.append(line)

    # 获取实体特征，添加"feature_ner_lsi"字段
    ners = []
    for news in data:
        text = news['text_ner']
        ners.append(text)
    tfidf_vectors_ner, lsi_vectors_ner = get_tfidf_and_lsi(ners)
    for i, ele in enumerate(data):
        ele['feature_ner_lsi'] = lsi_vectors_ner[i]

    # 获取关键词特征，添加"feature_word_lsi"字段
    words = []
    for news in data:
        text = news['text_noun']
        text.extend(news['text_verb'])
        words.append(text)
    tfidf_vectors_word, lsi_vectors_word = get_tfidf_and_lsi(words)
    for i, ele in enumerate(data):
        ele['feature_word_lsi'] = lsi_vectors_word[i]

    data_confirm = []
    for ele in data:
        if len(ele['feature_ner_lsi']) == 0 or len(ele['feature_word_lsi']) == 0:
            continue
        data_confirm.append(ele)

    result = {0: [0]}
    for i, news in enumerate(data_confirm):
        print(i)
        if i == 0:
            continue
        # if i >= 50:
        #     break
        feature_ner_lsi_now = news['feature_ner_lsi']
        feature_word_lsi_now = news['feature_word_lsi']
        feature_ner_lsi = []
        feature_word_lsi = []
        for key in result:
            index = result[key][0]
            vec_lsi = data_confirm[index]['feature_ner_lsi']
            vec_word = data_confirm[index]['feature_word_lsi']
            feature_ner_lsi.append(vec_lsi)
            feature_word_lsi.append(vec_word)
        index_ner_lsi = similarities.MatrixSimilarity(feature_ner_lsi)
        sims_ner_lsi = index_ner_lsi[feature_ner_lsi_now]
        index_word_lsi = similarities.MatrixSimilarity(feature_word_lsi)
        sims_word_lsi = index_word_lsi[feature_word_lsi_now]

        sims_ner = dict(enumerate(sims_ner_lsi))
        sims_word = dict(enumerate(sims_word_lsi))

        sims_ner_sort = sorted(sims_ner.items(), key=lambda d: d[1], reverse=True)
        sims_word_sort = sorted(sims_word.items(), key=lambda d: d[1], reverse=True)

        max_score_ner = sims_ner_sort[0][1]
        max_score_ner_index = sims_ner_sort[0][0]
        max_score_word = sims_word_sort[0][1]
        max_score_word_index = sims_word_sort[0][0]

        if max_score_word >= 0.85 and max_score_ner >= 0.35:
            result[max_score_word_index].append(i)
        else:
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
    fout.close()


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

