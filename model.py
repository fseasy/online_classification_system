#/usr/bin/env python
#coding=utf8

import sys
import math
import logging
from collections import Counter
try :
    import cPickle as pickle
except :
    import pickle
from config import ( LIBLINEAR_LIB_PATH ,)
sys.path.append(LIBLINEAR_LIB_PATH)

import liblinearutil 

class Model(object) :
    def __init__(self , name="classification model") :
        self.name = name 
        self.model = None
        self.POSITIVE_LABEL = 1
        self.NEGATIVE_LABEL = -1
        self.POSITIVE_NAME = "正例"
        self.NEGATIVE_NAME = "负例"

    def load_model(self , path) :
        raise AssertionError("This must been implemented")

    def vectorizing(self , sent) :
        raise AssertionError("This must been implemented")
    
    def ipredict(self , vec) :
        raise AssertionError("This must been implemented")
    
    def predict(self , vec) :
        '''
        vec : [ {idx : val , ...} ] , list with only one element !
        return : str , POSITIVE_NAME / NEGATIVE_NAME
        '''
        y_fake = [ self.NEGATIVE_LABEL ,] # for liblinear
        p_labels , _ , _ = liblinearutil.predict(y_fake , vec , self.model , "-q")
        p_label = int(p_labels[0])
        p_name = self.POSITIVE_NAME if p_label == self.POSITIVE_LABEL else self.NEGATIVE_NAME
        return p_name

    def _tokenize(self , sentence , ngram) :
        words = sentence.split()
        cnt = len(words)
        tokens = []
        # get gram from 1 to ngram
        for gram in range(1,ngram+1) :
        #gram = ngram
            for i in range(0,cnt - gram + 1) :
                token_l = words[i:i+gram]
                tokens.append('_'.join(token_l))
        return tokens

    def _load_svm_model(self , f_path , gzip_on=False) :
        if type(f_path) == file :
            input_f = f_path 
        else :
            try :
                if gzip_on :
                    input_f = gzip.open(f_path)
                else :
                    input_f = open(f_path)
            except IOError , e :
                raise IOError("failed to load svm model : open file error ")
        model = pickle.load(input_f)
        if type(f_path) != file :
            input_f.close()
        return model

class TFIDFModel(Model) :
    def __init__(self , name="TFIDF classification model for junk class") :
        super(TFIDFModel , self).__init__(name)
        self.POSITIVE_NAME = "垃圾"
        self.NEGATIVE_NAME = "非垃圾"

    def load_model(self , path) :
        logging.info("load model of %s" % self.name)
        self.model = liblinearutil.load_model(path)
        model_ext = self._load_svm_model(".".join([path , "ext"]))
        self.words2idx = model_ext["words2idx"]
        self.words_idf = model_ext["words_idf"]
        self.gram_n = model_ext["gram_n"]
        logging.info("done.")
    

    def vectorizing(self , sent) :
        words_tf = self._abstract_ngrams(sent) 
        return self._build_SVM_format_X_from_sent_words(words_tf)


    def _abstract_ngrams(self , sent) :
        '''
        sent -> [(word , TF) , ...]
        '''
        words_list = self._tokenize(sent , self.gram_n)
        words_counter = Counter(words_list)
        return words_counter.items()

    def _build_SVM_format_X_from_sent_words(self , sent_words) :
        '''
        input > doc_words_list : [ (word , TF),... ]
        return > [ {idx:val , ...}  ]
        ###ATTENTION ! SVM format , idx counted from 1 , not 0
        '''
        words_idf = self.words_idf
        words2idx = self.words2idx
        one_docs_repr = {}
        square_sum = 0
        for word , tf in sent_words :
            if word not in words2idx : continue
            idx_svm = words2idx[word]
            idf =words_idf.get(word , 0)
            val = tf*idf
            square_sum += val ** 2
            if val != 0 :
                one_docs_repr[idx_svm] = val
        #normalize
        sqrt_square_sum = math.sqrt(square_sum)
        for idx in one_docs_repr :
            try :
                one_docs_repr[idx] /= sqrt_square_sum # may be zero , leave it
            except ZeroDivisionError , e :
                traceback.print_exc()
        return [ one_docs_repr , ] # return a list !

class BOOLModel(Model) :
    def __init__(self , name="BOOL classification model for sensitive class") :
        super(BOOLModel , self).__init__(name)
        self.POSITIVE_NAME = "敏感"
        self.NEGATIVE_NAME = "非敏感"

    def load_model(self , path) :
        logging.info("load model of %s" % self.name)
        self.model = liblinearutil.load_model(path)
        model_ext = self._load_svm_model(".".join([path , "ext"]))
        self.feature_dict = model_ext["feature_dict"]
        self.gram_n = model_ext["gram_n"]
        logging.info("done") 

    def vectorizing(self , sent) :
        return self._vectorize_sentence_using_bool_feature(sent)

    def _vectorize_sentence_using_bool_feature(self , sent) :
        dic = self.feature_dict
        ngram = self.gram_n
        tokens = self._tokenize(sent,ngram)
        tokens = list(set(tokens))
        index = []
        for word in tokens :
            if word in dic :
                index.append(dic[word])
        sent_repr = { idx:1 for idx in index } 
        return [ sent_repr ,] # return a list !
    
