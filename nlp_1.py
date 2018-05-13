from pprint import pprint

import jieba
import jieba.analyse
import os
import sys
import time
sys.path.append('../')

import mysql.connector

from gensim.models import word2vec
import logging

import webapi

start=time.clock()

##分词~~  加载和去除停用词
jieba.analyse.set_stop_words("./nlp_stopword.txt")

stops = set()
with open('nlp_stopword.txt','r') as stw:
    for line in stw.readlines():
        stops.add(line.strip('\n'))



# # #读取全训练集，一行一条记录： 字母小写，去换行
if(not os.path.exists('cropus.txt')):
    logging.warning("load mysql data ,and write cropus.txt")
    conn = mysql.connector.connect(host="localhost",user="root",passwd="xxx",db="crawler",charset="utf8")
    cursor=conn.cursor()

    # read
    sql1 = "select CONCAT(title,',',duty,',',requirements) from jd_tencent "
    sql2 = "select CONCAT(name,',',jobDescription,',',jobRequirements) from jd_alibaba "
    sql3 = "select CONCAT(name,',',serviceCondition) from jd_baidu "
    sql4 = "select CONCAT(title,',',description) from jobinfo_liepin_itclass limit 100000" # 100w模型有点大，需要裁剪
    cursor.execute(sql1)
    with open('cropus.txt','a') as f:
        for info in cursor:
            f.write(" ".join(info[0].lower().split()  ) )
            f.write('\n')

    cursor.execute(sql2)
    with open('cropus.txt','a') as f:
        for info in cursor:
            f.write(" ".join(info[0].lower().split()  ) )
            f.write('\n')

    cursor.execute(sql3)
    with open('cropus.txt','a') as f:
        for info in cursor:
            f.write(" ".join(info[0].lower().split()  ) )
            f.write('\n')
    cursor.execute(sql4)
    with open('cropus.txt','a') as f:
        for info in cursor:
            f.write(" ".join(info[0].lower().split()  ) )
            f.write('\n')
    cursor.close()
    conn.close()

if(not os.path.exists('cropus_seg.txt')):
    logging.warning("[jieba] seg raw txt file to ->cropus_seg.txt")
    with open('cropus.txt','r') as src:
        with open('cropus_seg.txt','w') as dest:
            for line in src.readlines():

                words = jieba.cut( line )
                # clean stop_words
                words = [w for w in words if w not in stops]

                dest.write( " ".join( words ))


#word 2 vec model
# logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', level=logging.INFO)
# sentences =word2vec.Text8Corpus(u"cropus_seg")  # 加载语料
# model =word2vec.Word2Vec(sentences)  #训练skip-gram模型，默认window=5
# model.save(u"fastjd.model")
#
# model_1=word2vec.Word2Vec.load('fastjd.model')
# print(model_1.similarity(u"java", u"lamp")  )
# print(model_1.similarity(u"java", u"tomcat")  )
#
#
# # 计算某个词的相关词列表
# y2 = model_1.most_similar(u"tomcat", topn=20)  # 20个最相关的
# print( u"和【xx】最相关的词有：\n")
# for item in y2:
#     print (item[0], item[1])
# print("-----\n")

# model_1.score()

from gensim import corpora, models, similarities

if(not os.path.exists('document.dict')):
    logging.warning("making -> document.dict")
    documents=[[ word for word in doc.split() ] for doc in open('cropus_seg.txt','r').readlines()]
    dictionary = corpora.Dictionary(documents)
    dictionary.save('document.dict')
else:
    dictionary = corpora.Dictionary.load('document.dict')
print(dictionary)

if(not os.path.exists('corpus.mm')):
    logging.warning("making -> corpus.mm")
    corpus = [ dictionary.doc2bow(text.split()) for text in open('cropus_seg.txt','r').readlines()]
    corpora.MmCorpus.serialize('corpus.mm', corpus)  # store to disk, for later use
else:
    corpus = corpora.MmCorpus('corpus.mm')

#2-dimensional LSI space:
lsi = models.LsiModel(corpus, id2word=dictionary)
if(not os.path.exists('corpus.index')):
    logging.warning("making -> corpus.index")
    index = similarities.MatrixSimilarity(lsi[corpus]) # transform corpus to LSI space and index it
    index.save('corpus.index')
else:
    index = similarities.MatrixSimilarity.load('corpus.index')


end=time.clock()
print('Init time: %s Seconds'%(end-start))

#query
querys = "java web"
print('doc2bow %s',querys)
vec_querys = dictionary.doc2bow(querys.lower().split())

print('lsi space..')
vec_lsi = lsi[vec_querys] # convert the query to LSI space

print('lsi index..')
sims = index[vec_lsi]
print('sort, enumerate..')
sims = sorted(enumerate(sims), key=lambda item: -item[1])[:5]


lines = open('cropus.txt','r').readlines()

print("make a Q:(%s) ,return top 5:",querys)
for s in sims:
    print(s[1],s[0])
    print(lines[s[0]])
