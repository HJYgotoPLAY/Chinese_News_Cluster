# -*- coding:utf-8 -*-
"""
文本预处理
"""
import os
from pyltp import Segmentor, Postagger, NamedEntityRecognizer
from pyltp import SentenceSplitter
import codecs
import json
import jieba
from jieba.analyse import textrank

def preprocessing():
    '''
    输入txt文件，每行为一篇资讯，格式为：新闻编号#新闻标题#新闻正文
    使用pyltp工具进行文本预处理，包括分词，词性标注，命名实体识别
    '''
    jieba.load_userdict('WordsDic/userdict_.txt')
    jieba.analyse.set_stop_words('WordsDic/stopwords.txt')
    LTP_DATA_DIR = 'ltp_data_v3.4.0'
    cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
    pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')
    ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')
    segmentor = Segmentor()
    segmentor.load_with_lexicon(cws_model_path, 'WordsDic/userdict.txt')
    postagger = Postagger()
    postagger.load_with_lexicon(pos_model_path, 'WordDic/userdict_.txt')
    recognizer = NamedEntityRecognizer()
    recognizer.load(ner_model_path)

    ids = []
    titles = []
    texts = []
    count = 0
    for line in codecs.open('news_for_day/%d.txt' % day, encoding='utf8'):
        line = line.strip().split('#')
        id = line[0]
        title = line[1]
        text = line[2]
        text = title + '。' + text
        count += 1
        ids.append(id)
        texts.append(text)
        titles.append(title)

    texts_ner = []
    texts_ner_tag = []
    texts_noun = []
    texts_verb = []
    texts_keywords = []
    k = 0
    for t in texts:
        k += 1
        print(k)
        key = textrank(t, withWeight=True, allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'nrt', 'v', 'vn'))
        texts_keywords.append(key)

        t_ner = []
        t_ner_tag = []
        t_noun = []
        t_verb = []

        sents = SentenceSplitter.split(t)
        sents = '\n'.join(sents)
        sents = sents.split('\n')
        for sen in sents:
            words = segmentor.segment(sen)
            words = '\t'.join(words)
            words = words.split('\t')
            postags = postagger.postag(words)
            netags = recognizer.recognize(words, postags)
            netags =  '\t'.join(netags)
            netags = netags.split('\t')
            for i in range(len(postags)):
                if postags[i] in ['n', 'nh', 'ni', 'nl', 'ns', 'nz']:
                    t_noun.append(words[i])
            for i in range(len(postags)):
                if postags[i] in ['v']:
                    t_verb.append(words[i])
            w = ''
            tag = ''
            for i in range(len(netags)):
                if netags[i] == 'O':
                    continue
                if netags[i].startswith('S'):
                    t_ner.append(words[i])
                    t_ner_tag.append(netags[i][2:])
                if netags[i].startswith('B') or netags[i].startswith('I'):
                    w += words[i]
                if netags[i].startswith('E'):
                    w += words[i]
                    tag = netags[i][2:]
                    t_ner.append(w)
                    t_ner_tag.append(tag)
                    w = ''
                    tag = ''
        texts_noun.append(t_noun)
        texts_verb.append(t_verb)
        texts_ner.append(t_ner)
        texts_ner_tag.append(t_ner_tag)
    segmentor.release()
    postagger.release()
    recognizer.release()
    fout = codecs.open('news_for_day/%d_ner.txt' % day, 'w', encoding='utf8')
    for i in range(len(ids)):
        d = {}
        d['id'] = ids[i]
        d['title'] = titles[i]
        d['text'] = texts[i]
        d['text_ner'] = texts_ner[i]
        d['text_ner_tag'] = texts_ner_tag[i]
        d['text_noun'] = texts_noun[i]
        d['text_verb'] = texts_verb[i]
        d['text_keywords'] = texts_keywords[i]
        strObj = json.dumps(d, ensure_ascii=0)
        fout.write(strObj)
        fout.write('\n')
    fout.close()


if __name__ == '__main__':
    num_of_days = 1
    for day in range(num_of_days):
        day = day + 1
        preprocessing()


