from gensim import corpora, models, similarities

class MM(object):
    def __init__(self):
        self.dictionary = corpora.Dictionary.load('document.dict')
        # global corpus
        self.corpus = corpora.MmCorpus('corpus.mm')
        # global lsi
        self.lsi = models.LsiModel(self.corpus, id2word=self.dictionary)
        # global index
        self.index = similarities.MatrixSimilarity.load('corpus.index')
