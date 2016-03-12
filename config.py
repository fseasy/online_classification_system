#coding=utf8

import sys
import os

def enum(**enums) :
    return type('Enum' , () , enums)

classname = enum(JUNK="junk" , SENSITIVE="sensitive")

SAMPLE_END_SYMBOL_OF_CRLF_MODE = "\r\n"
SAMPLE_END_SYMBOL_OF_LINE_MODE = "$$END$$" # we omit the '\n' , because we firstly strip the readline !

sampleIntervalMode = enum(LINE_MODE="linemode" , CRLF_MODE="crlfmode")

cur_dir_abspath = os.path.dirname(os.path.realpath(__file__))
junk_model_relative_path = "model/junk.svmtfidf.model"
sensitive_model_relative_path = "model/sensitive.svmbool.model"
liblinear_lib_relative_path = "third_party_libs/liblinear-1.96/python/"

JUNK_MODEL_PATH = os.path.normpath( "/".join([cur_dir_abspath , junk_model_relative_path]) )
SENSITIVE_MODEL_PATH = os.path.normpath( "/".join([cur_dir_abspath , sensitive_model_relative_path]) ) 
LIBLINEAR_LIB_PATH = os.path.normpath( "/".join([cur_dir_abspath , liblinear_lib_relative_path]) )
CWS_MODEL_PATH = "/data/ltp/ltp-models/3.3.0/ltp_data/cws.model"
# For checking 
checking_dict = {
            "junk-class model " : JUNK_MODEL_PATH ,
            "sensitive-class model" : SENSITIVE_MODEL_PATH ,
            "liblinear " : LIBLINEAR_LIB_PATH ,
            "cws model " : CWS_MODEL_PATH
        }
for name , path in checking_dict.items() :
    if not os.path.exists(path) :
        print >> sys.stderr , \
        '''
        %s path check error .
        the path `%s` is not exists .
        Exit .
        ''' %(name , path)
        exit(1)

del checking_dict

