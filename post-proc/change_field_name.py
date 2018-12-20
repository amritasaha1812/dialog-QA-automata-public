#!/home/vardaan/anaconda2/bin/python
import codecs, random, pickle, json, math, logging, sys, os, resource, fcntl, collections
from fcntl import flock, LOCK_EX, LOCK_NB
from collections import defaultdict
from collections import Counter
import numpy as np

from pattern.en import lemma, conjugate, tenses
import argparse
import itertools

import timeit
import time
import logging

sys.path.append(os.getcwd())

parser = argparse.ArgumentParser(description='Hyper-parameter settings')
parser.add_argument('--input_dir', dest='input_dir', type=str, help='directory in which source dialogs are present', required=True)
parser.add_argument('--output_dir',dest='output_dir', type=str, help = 'name of dir (wrt cwd) where dialogue dirs are created',required=True) # should be required

args = parser.parse_args()
print(args)

count = 0

for dir_name in [d for d in os.listdir(args.input_dir) if os.path.isdir(os.path.join(args.input_dir, d))]:
    # if count > 500:
    #     break
    if not os.path.exists(os.path.join(args.output_dir, dir_name)):
        os.makedirs(os.path.join(args.output_dir, dir_name))

    for filename in os.listdir(os.path.join(args.input_dir, dir_name)):
        count += 1
        if count % 100 == 0:
            print count
        dialog_json_file = os.path.join(args.input_dir, dir_name, filename)
        # print dialog_json_file
        try:
            with open(dialog_json_file,'r') as data_file:
                utter_list = json.load(data_file)
                dialog_list_new = []

                for idx, utter in enumerate(utter_list):
                    utter_new = utter.copy()

                    if 'entities' in utter:
                        utter_new['entities_in_utterance'] = utter['entities']
                        del utter_new['entities']

                    if 'ans_list_full' in utter:
                        utter_new['all_entities'] = utter['ans_list_full']
                        del utter_new['ans_list_full']
                    
                    if 'active_set' in utter:
                        del utter_new['active_set']

                    if 'signature' in utter:
                        del utter_new['signature']

                    if 'ques_type_id' in utter and 'count_ques_sub_type' in utter and ((utter['ques_type_id'] == 7 and utter['count_ques_sub_type'] in [1,2,3,5,7]) or (utter['ques_type_id'] == 8 and utter['count_ques_sub_type'] in [1,2,3,4,6,8])):
                        ques_type = 'Quantitative'
                        utter_new['question-type'] = ques_type
                    elif 'ques_type_id' in utter and 'count_ques_sub_type' in utter and ((utter['ques_type_id'] == 7 and utter['count_ques_sub_type'] in [4,6,8,9]) or (utter['ques_type_id'] == 8 and utter['count_ques_sub_type'] in [5,7,9,10])):
                        ques_type = 'Comparative'
                        utter_new['question-type'] = ques_type
                    elif ('ques_type_id' in utter and utter['ques_type_id'] == 4) or ('ques_type_id' not in utter_list[idx] and idx > 1 and 'ques_type_id' in utter_list[idx-2] and utter_list[idx-2]['ques_type_id'] == 4):
                        ques_type = 'Logical'
                        utter_new['question-type'] = ques_type

                    dialog_list_new.append(utter_new)
                    # print dialog_list_new[-1]['utterance']

                with open(os.path.join(args.output_dir, dir_name, filename), 'wb') as outfile:
                        json.dump(dialog_list_new, outfile, indent = 1)

        except:
            print 'Issue with filename: %s' % dialog_json_file
            logging.exception("Something aweful happened")
            continue
