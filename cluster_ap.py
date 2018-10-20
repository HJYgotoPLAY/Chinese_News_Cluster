# -*- coding:utf-8 -*-
'''
AP聚类
'''
import codecs
import json
import numpy as np
from gensim import corpora, models, similarities
from sklearn.cluster import AffinityPropagation
from xlwt import Workbook

def computeSimilarity_lsm(X, query):
    index = similarities.MatrixSimilarity(X)
    sims = index[query]
    scoreList = list(enumerate(sims))
    rankList = [scoreList[i][1] for i in range(len(scoreList))]
    return rankList

def get_corpus():
    news_list = []  # 新闻编号
    text_ner_corpus =[]  # 新闻标题加正文的命名实体识别结果
    text_noun_corpus = []  # 新闻标题加正文的名词
    text_verb_corpus = []  # 新闻标题加正文的动词
    text_word_corpus = []  # 新闻标题加正文的名词加动词
    texts = []  # 新闻标题加正文
    for line in codecs.open('news_for_day/%d_ner_filter.txt' % day, encoding='utf8'):
        line_dict = json.loads(line)
        id = line_dict['id']
        text_noun = line_dict['text_noun']
        text_verb = line_dict['text_verb']
        text_ner = line_dict['text_ner']
        text_word = text_noun
        text_word.extend(text_verb)
        text = line_dict['text']
        news_list.append(id)
        text_ner_corpus.append(text_ner)
        text_noun_corpus.append(text_noun)
        text_verb_corpus.append(text_verb)
        text_word_corpus.append(text_word)
        texts.append(text)
    return news_list, text_ner_corpus, text_noun_corpus, text_verb_corpus, text_word_corpus, texts

def cluster(corpus, num_topics):
    dictionary = corpora.Dictionary(corpus)
    length_of_dictionary = len(dictionary)
    print("length of dictionary: ", length_of_dictionary)
    doc_vectors = [dictionary.doc2bow(text) for text in corpus]
    # TF-IDF特征
    tfidf = models.TfidfModel(doc_vectors)
    tfidf_vectors = tfidf[doc_vectors]
    # LSI特征
    lsi = models.LsiModel(tfidf_vectors, id2word=dictionary, num_topics=num_topics)
    lsi_vectors = lsi[tfidf_vectors]
    vec = []
    for i, ele in enumerate(lsi_vectors):
        feature = np.zeros(num_topics)
        for idx, val in ele:
            feature[idx] = val
        vec.append(feature)
    # AP聚类（自动确定聚类数目）
    af = AffinityPropagation().fit(vec)
    cluster_centers_indices = af.cluster_centers_indices_
    result = af.labels_
    num_of_clusters = len(cluster_centers_indices)
    return result, num_of_clusters

def get_cluster_result(result, corpus, num_topics):
    f = codecs.open('result_ap/cluster%d.txt' % day, 'w', encoding='utf-8')
    for i in range(0, num_topics):
        for linenumber, eachline in enumerate(corpus):
            if linenumber >= len(result):
                break
            if result[linenumber] == i:
                f.write(str(news_list[linenumber]) + '#' + str(i) + '#' + eachline)
                f.write('\n')
    f.close()

def get_top_clusters(corpus_original, num_topics, Threshold):
    f = codecs.open('result_ap/cluster%d.txt' % day, 'r', encoding='utf-8')
    data = []
    for line in f.readlines():
        data_pair = line.split('#')
        data.append(data_pair)
    news = []
    for ele in data:
        news.append(ele[0])
    types = []
    for ele in data:
        types.append(ele[1])
    corpus = []
    for ele in news:
        index = news_list.index(ele)
        corpus.append(corpus_original[int(index)])
    topic_list = []
    for i in range(num_topics):
        num = 0
        for ele in types:
            if int(ele) == i:
                num += 1
        topic_list.append(num)
    # build dictionary
    dictionary = corpora.Dictionary(corpus)
    doc_vectors = [dictionary.doc2bow(text) for text in corpus]
    # TFIDF特征
    tfidf = models.TfidfModel(doc_vectors)
    tfidf_vectors = tfidf[doc_vectors]
    # LSI特征
    lsi = models.LsiModel(tfidf_vectors, id2word=dictionary, num_topics=num_topics)
    lsi_vectors = lsi[tfidf_vectors]
    # 计算簇的平均文本相似度
    result = []
    del_news_id = []
    del_news_type = []
    for i in range(len(topic_list)):
        l = sum(topic_list[:i])
        r = l + topic_list[i]
        X = lsi_vectors[l: r]
        # 对于大于等于200的簇取消计算
        if topic_list[i] >= 200:
            result.append(0.0)
        # 对于小于等于1的簇取消计算
        elif topic_list[i] <= 1:
            result.append(0.0)
        else:
            X_score = []
            for j in range(topic_list[i]):
                query = X[j]
                scoreList = computeSimilarity_lsm(X, query)
                X_score.append(scoreList)
            num_of_compute = topic_list[i] * topic_list[i] - topic_list[i]
            # 一个簇的平均文本相似度
            score = (sum([sum(ele) for ele in X_score]) - topic_list[i]) / num_of_compute
            # 过滤簇内的噪音
            every_list = []
            for ele in X_score:
                every_list.append((sum(ele) - 1) / (len(ele) - 1))
            every = score
            delete = []
            for k in range(len(every_list)):
                if every - every_list[k] > 0.1:
                    del_news_id.append(news[l + k])
                    del_news_type.append(i)
                    delete.append(k)
            new_X = []
            for _ in range(topic_list[i]):
                if _ not in delete:
                    new_X.append(X[_])
            new_X_score = []
            for j in range(len(new_X)):
                query = new_X[j]
                scoreList = computeSimilarity_lsm(new_X, query)
                new_X_score.append(scoreList)
            length = topic_list[i] - len(delete)
            new_num_of_compute = length * length - length
            # 过滤噪音后的簇内平均文本相似度
            new_score = (sum([sum(ele) for ele in new_X_score]) - length) / new_num_of_compute
            result.append(new_score)
    result_pair = []
    for index, s in enumerate(result):
        result_pair.append((index, s))
    get_result(Threshold, data, result_pair, del_news_id)

def get_result(Threshold, data, result_pair, del_news_id):
    news_id = []
    type_list = []
    word_list = []
    for i in range(len(data)):
        id = data[i][0]
        type = data[i][1]
        word = data[i][2]
        news_id.append(id)
        type_list.append(type)
        word_list.append(word)
    event_list = [ele[0] for ele in result_pair]
    score_list = [ele[1] for ele in result_pair]
    new_news_id = []
    new_type_list = []
    new_word_list = []
    new_score_list = []
    for i in range(len(type_list)):
        if int(type_list[i]) in event_list and news_id[i] not in del_news_id:
            index = int(type_list[i])
            new_news_id.append(news_id[i])
            new_type_list.append(type_list[i])
            new_word_list.append(word_list[i])
            new_score_list.append(score_list[index])
    book = Workbook()
    sheet1 = book.add_sheet('sheet1')
    length2 = len(new_type_list)
    k = -1
    for i in range(length2):
        if new_score_list[i] >= Threshold:
            k = k + 1
            row = sheet1.row(k)
            row.write(0, new_news_id[i])
            row.write(1, new_type_list[i])
            row.write(2, new_score_list[i])  # 全文本相似度(lsi)
            title = new_word_list[i].split('。')[0]
            row.write(3, title)
            row.write(4, new_word_list[i][:150])
    book.save( 'result_ap/%d.xls' % day)

if __name__ == '__main__':
    num_of_days = 1
    for day in range(num_of_days):
        day = day + 1
        print('cluster for day %d' % day)
        news_list, text_ner_corpus, text_noun_corpus, text_verb_corpus, text_word_corpus, texts = get_corpus()
        num_of_topics = 500  # LSI主题数设置与聚类粒度的关系
        cluster_result, num_of_clusters = cluster(text_ner_corpus, num_of_topics)
        # news_list, text_word_corpus, texts, cluster_result一一对应
        get_cluster_result(cluster_result, texts, num_of_clusters)
        cluster_Threshold = 0.0  # 设定阈值，过滤小于阈值的簇
        get_top_clusters(text_word_corpus, num_of_clusters, cluster_Threshold)




