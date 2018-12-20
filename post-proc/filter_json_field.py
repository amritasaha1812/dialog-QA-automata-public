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
sys.path.append(os.getcwd())

parser = argparse.ArgumentParser(description='Hyper-parameter settings')
parser.add_argument('--input_dir', dest='input_dir', type=str, help='directory in which dialogs are to be verified', required=True)
parser.add_argument('--output_dir',dest='output_dir', type=str, help = 'name of dir (wrt cwd) where dialogue dirs are created',required=True) # should be required
parser.add_argument('--field_whitelist_file', dest='field_whitelist_file', type=str, help='path to filename containing fields to keep', required=True)

args = parser.parse_args()
print(args)

def safe_str(obj):
    """ return the byte string representation of obj """
    try:
        return str(obj)
    except UnicodeEncodeError:
        # obj is unicode
        return unicode(obj).encode('unicode_escape')
        
def get_dict_signature(utter_dict):
    field_list = []
    for key in sorted(utter_dict.keys()):
        if key != 'ans_list_full':
            field_list.append('{%s:%s}' % (safe_str(key),safe_str(utter_dict[key])))
    return '@'.join(field_list)

def fix_count_mult(utter):
    pattern_1 = '%s and %s' % (utter['entities'][0],utter['entities'][0])
    pattern_2 = '%s or %s' % (utter['entities'][0],utter['entities'][0])

    utter['utterance'] = utter['utterance'].replace(pattern_1,utter['entities'][0])
    utter['utterance'] = utter['utterance'].replace(pattern_2,utter['entities'][0])

    del utter['set_op']
    utter['ques_type_id'] = 7
    utter['count_ques_sub_type'] = 1
    del utter['signature']
    utter['signature'] = get_dict_signature(utter.copy())

    return utter

with open(args.field_whitelist_file) as f1:
    wanted_global_key_list = f1.read().splitlines()

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

                for utter in utter_list:
                    utter_new = utter.copy()
                    if 'ques_type_id' in utter and utter['ques_type_id'] == 8 and 'count_ques_sub_type' in utter and utter['count_ques_sub_type']==1 and len(set(utter['entities'])) == 1:
                        utter_new = fix_count_mult(utter_new)

                    # unwanted_keys = set(utter_new.keys()).difference(set(wanted_global_key_list))
                    # for unwanted_key in unwanted_keys:
                    #     del utter_new[unwanted_key]

                    dialog_list_new.append(utter_new)
                    # print dialog_list_new[-1]['utterance']

                with open(os.path.join(args.output_dir, dir_name, filename), 'wb') as outfile:
                        json.dump(dialog_list_new, outfile, indent = 1)

        except:
            print 'Issue with filename: %s' % dialog_json_file
            continue
