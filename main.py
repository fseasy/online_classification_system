#/usr/bin/env python
#coding=utf8

import sys
import argparse
import logging
from pyltp import Segmentor
from model import TFIDFModel , BOOLModel
from preprocessor import PreProcessor
from config import ( JUNK_MODEL_PATH , SENSITIVE_MODEL_PATH , 
                     LIBLINEAR_LIB_PATH , CWS_MODEL_PATH ,
                     classname , sampleIntervalMode )

logging.basicConfig(level=logging.INFO , 
                    format="%(levelname)s : [%(filename)s] %(message)s")

def main(model , preprocessor , ifo) :
    for sample_line_list in preprocessor.read_sample(ifo) :
        preprocessed_sample = preprocessor.preprocess_sample(sample_line_list)
        vec = model.vectorizing(preprocessed_sample)
        p_name = model.predict(vec)
        print p_name

if __name__ == "__main__" :
    argp = argparse.ArgumentParser(description="Online Classification System")
    argp.add_argument("-c" , "--classname" , choices=[classname.JUNK , classname.SENSITIVE] , required=True ,
                      help="Classification Type , junk-class or sensitive class ")
    argp.add_argument("-s" , "--sample_interval_mode" , choices=[sampleIntervalMode.LINE_MODE , sampleIntervalMode.CRLF_MODE] , 
                      default=sampleIntervalMode.LINE_MODE ,
                      help="The mode with describes what is the inverval symbol between samples , default is LINE_MODE")
    argp.add_argument("-i" , "--input" , type=str , default="stdin" , 
                      help="'sysin' for using standard input ; else file path is needed.")
    args = argp.parse_args()

    logging.info("loadding segmentor")
    segmentor = Segmentor()
    segmentor.load(CWS_MODEL_PATH)
    logging.info("done")

    # loading model
    if args.classname == classname.JUNK :
        model = TFIDFModel()
        model.load_model(JUNK_MODEL_PATH)
    else :
        model = BOOLModel()
        model.load_model(SENSITIVE_MODEL_PATH)
    
    #process the input file
    if args.input == "stdin" :
        ifo = sys.stdin
    else :
        ifo = open(args.input) # if error , just quit
    logging.info("reading samples from %s" %ifo.name)
    
    #print sample interval mode
    logging.info("set sample interval mode as '%s'" %args.sample_interval_mode)
    
    preprocessor = PreProcessor(segmentor , args.sample_interval_mode)
   
    main(model , preprocessor , ifo)
    
    #release resourse
    segmentor.release()
    if ifo != sys.stdin :
        ifo.close()
