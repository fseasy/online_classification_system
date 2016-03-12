#/usr/bin/env python
#coding=utf8

import sys
import re
import logging

from config import ( SAMPLE_END_SYMBOL_OF_LINE_MODE , SAMPLE_END_SYMBOL_OF_CRLF_MODE ,
                     sampleIntervalMode)

class PreProcessor(object) :
    def __init__(self , segmentor , sample_interval_mode=sampleIntervalMode.LINE_MODE) :
        self.segmentor = segmentor
        self.sample_interval_mode = sample_interval_mode
        self.input_encoding="gb18030"

    def read_sample(self , ifo=sys.stdin) :
        '''
        Generator
        < sample_list , list for one sample , with Unicode
        '''
        ifo_is_file = ( type(ifo) == file )
        if not ifo_is_file :
            ifo = open(ifo) # if error  , just quit

        decoding = self._line_docoding
        if self.sample_interval_mode == sampleIntervalMode.LINE_MODE :
            # when read SAMPLE_END_SYMBOL_OF_LINE_MODE , return one sample
            sample_line_list = []
            #for line in ifo :     --- NO! this way has IO buffer , can't interactive in real time
            while True :
                line = ifo.readline()
                if line == "" : # EOF
                    if len(sample_line_list) > 0 :
                        yield sample_line_list
                    break
                line = line.strip()
                if line == SAMPLE_END_SYMBOL_OF_LINE_MODE :
                    # abandon the symbol line
                    yield sample_line_list
                    sample_line_list = []
                else :
                    sample_line_list.append(decoding(line))
        elif self.sample_interval_mode == sampleIntervalMode.CRLF_MODE :
            sample_line_list = []
            for line in ifo :
                if line.endswith(SAMPLE_END_SYMBOL_OF_CRLF_MODE) :
                    # append the line
                    line = line.strip()
                    sample_line_list.append(decoding(line))
                    yield sample_line_list
                    sample_line_list = []
                else :
                    line = line.strip()
                    sample_line_list.append(decoding(line))
            if len(sample_line_list) > 0 : # file has been read over , but the list may have data !
                yield sample_line_list
        if not ifo_is_file :
            ifo.close()
    
    def preprocess_sample(self , sample_line_list) :
        '''
        > sample_line_list , list , str with Unicode
        < preprocessed line , str , word which has been seged and combine to str with space
        '''
        one_line = self._combine_lines2sample(sample_line_list)
        sample = self._try2clean_sample(one_line)
        sentences = self._split_sample2sentences(sample)
        words_list = self._seg_sentences(sentences)
        return " ".join(words_list)

    def _line_docoding(self , line) :
        try :
            u_line = line.decode(self.input_encoding) 
        except UnicodeDecodeError , e :
            self.input_encoding = "utf8" if self.input_encoding == "gb18030" else "gb18030"
            try :
                u_line = line.decode(self.input_encoding)
            except UnicodeDecodeError , e :
                raise Exception("Unkown encoding for input")
        return u_line

    def _combine_lines2sample(self , lines) :
        sample = u"。".join(lines)
        return sample.replace(u"\n",'')
    
    def _try2clean_sample(self , dirty_sample) :
        parts = dirty_sample.rstrip().split(u'\t')
        if len(parts) == 7 or len(parts) == 4 :
           # The Standard sample in Excel format
           title = parts[1] 
           content = parts[2]
           txt_type = parts[-1]
           sample = u"。".join([ title , content , txt_type  ])
        else :
           # dirty sample , just return 
           sample = u"。".join(parts)
        return sample
    
    def _split_sample2sentences(self , sample) :
        '''
        暴力分割，忽略引号作用
        '''
        split_pattern = u"[。！？；…!?;~～ ]" # including space !
        sentence_slice = re.split(split_pattern , sample)
        return sentence_slice
    
    def _seg_sentences(self , sentences) :
        '''
        > sentences , list , sentence in unicode
        < word_list , list , list of segemented word with codding in utf8
        '''
        all_word_list = []
        for u_sentence in sentences :
            sentence = u_sentence.encode("utf8")
            word_list = self.segmentor.segment(sentence)
            all_word_list.extend(word_list)
        return all_word_list

