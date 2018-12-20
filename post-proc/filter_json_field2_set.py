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
parser.add_argument('--low',dest='low',type=int, help='lower index of QA')
parser.add_argument('--high',dest='high',type=int, help='higher index of QA')

args = parser.parse_args()
print(args)

def is_valid_dialog(dialog_l):
    for idx, utter in enumerate(dialog_l):
        if idx >= len(dialog_l)-1:
            try:
                assert utter['speaker'] == 'SYSTEM'
            except:
                return False
            break
        if utter['speaker'] == 'USER':
            try:
                assert dialog_l[idx+1]['speaker'] == 'SYSTEM'
            except:
                return False
        elif utter['speaker'] == 'SYSTEM':
            try:
                assert dialog_l[idx+1]['speaker'] == 'USER'
            except:
                return False
    return True
   
def check_unwanted_fields(dialog_l):
    unwanted_field_list = ['Qid','prop_res','prop_res_1','prop_Qid_par','prop_Qid_par_new','Qid_1','obj_par','obj_par_1','obj_par_2','sub_par','sub_par_1','sub_par_2','N','Z','qualifier_choice','len(ans_list) > 1','sub_list']
    
    for utter in dialog_l:
        if len(set(unwanted_field_list) & set(utter.keys())) > 0:
            print 'flag-1' + utter['utterance']
            return False
        if utter['speaker'] == 'SYSTEM' and ('question-type' in utter or 'type_list' in utter):
            print 'flag-2' + utter['utterance']
            return False
        if utter['speaker'] == 'USER' and ('question-type' not in utter):
            print 'flag-3' + utter['utterance']
            return False
    return True

def get_type_list(utter):
    type_list = []

    if 'prop_Qid_par' in utter:
        type_list.append(utter['prop_Qid_par'])

    if 'prop_Qid_par_new' in utter:
        type_list.append(utter['prop_Qid_par_new'])
        
    if 'obj_par' in utter:
        type_list.append(utter['obj_par'])
    if 'obj_par_1' in utter:
        type_list.append(utter['obj_par_1'])
    if 'obj_par_2' in utter:
        type_list.append(utter['obj_par_2'])

    if 'sub_par' in utter:
        type_list.append(utter['sub_par'])
    if 'sub_par_1' in utter:
        type_list.append(utter['sub_par_1'])
    if 'sub_par_2' in utter:
        type_list.append(utter['sub_par_2'])

    return type_list

def get_ques_type(utter):
    if 'ques_type_id' in utter and utter['ques_type_id'] == 1:
        ques_type = 'Simple Question (Direct)'

    elif 'ques_type_id' in utter and utter['ques_type_id'] == 2:
        if utter['sec_ques_sub_type'] in [1,4]:
            ques_type = 'Simple Question (Direct)'
        else:
            ques_type = 'Simple Question (Coreferenced)'

    # elif 'ques_type_id' in utter and utter['ques_type_id'] == 3:
    #     ques_type = 'Clarification'

    elif 'ques_type_id' in utter and utter['ques_type_id'] == 4:
        ques_type = 'Logical Reasoning (All)'

    elif 'ques_type_id' in utter and utter['ques_type_id'] == 5:
        ques_type = 'Verification (Boolean) (All)'

    elif 'ques_type_id' in utter and utter['ques_type_id'] == 6:
        if 'inc_ques_type' in utter and utter['inc_ques_type'] in [1,2]:
            ques_type = 'Simple Question (Ellipsis)'
        else:
            ques_type = 'Quantitative Reasoning (Count) (All)'

    elif 'ques_type_id' in utter and 'count_ques_sub_type' in utter:
        if (utter['ques_type_id'] == 7 and utter['count_ques_sub_type'] in [1,5,7]) or (utter['ques_type_id'] == 8 and utter['count_ques_sub_type'] in [1,2,6,8]):
            ques_type = 'Quantitative Reasoning (Count) (All)'
        elif (utter['ques_type_id'] == 7 and utter['count_ques_sub_type'] in [2,3]) or (utter['ques_type_id'] == 8 and utter['count_ques_sub_type'] in [3,4]):
            ques_type = 'Quantitative Reasoning (All)'
        elif (utter['ques_type_id'] == 7 and utter['count_ques_sub_type'] in [6,9]) or (utter['ques_type_id'] == 8 and utter['count_ques_sub_type'] in [7,10]):
            ques_type = 'Comparative Reasoning (Count) (All)'
        elif (utter['ques_type_id'] == 7 and utter['count_ques_sub_type'] in [4,8]) or (utter['ques_type_id'] == 8 and utter['count_ques_sub_type'] in [5,9]):
            ques_type = 'Comparative Reasoning (All)'
    else:
        if 'ques_type_id' in utter:
            print utter
            print 'ERROR!!!'
        ques_type = None

    return ques_type

def remove_unwanted_fields(utter):
    unwanted_keys = set(utter.keys()).difference(set(wanted_global_key_list))
    for unwanted_key in unwanted_keys:
        del utter[unwanted_key]

    if 'entities' in utter:
        utter['entities_in_utterance'] = utter['entities']
        del utter['entities']

    if 'ans_list_full' in utter:
        utter['all_entities'] = utter['ans_list_full']
        del utter['ans_list_full']

    if 'signature' in utter:
        del utter['signature']


with open(args.field_whitelist_file) as f1:
    wanted_global_key_list = f1.read().splitlines()

count = 0

for dir_name in [('QA_%d' % i) for i in range(args.low, args.high) if os.path.isdir(os.path.join(args.input_dir, ('QA_%d' % i)))]:
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

                utter_id = 0
                while utter_id < len(utter_list):
                    utter = utter_list[utter_id]

                    

                    # delete the ques_type_id for simple clarification question

                    # elif 'ques_type_id' in utter and utter['ques_type_id'] == 3:
                    #     del utter_new['ques_type_id']

                    if 'ques_type_id' in utter and utter['ques_type_id'] == 2 and 'sec_ques_sub_type' in utter and utter['sec_ques_sub_type']==2 and (utter_id+1) < len(utter_list) and 'utterance' in utter_list[utter_id+1] and 'Did you mean' in utter_list[utter_id+1]['utterance']:
                        utter_new = utter.copy()
                        utter_new['ques_type_id'] = 3
                        utter_new['type_list'] = get_type_list(utter_new)
                        utter_new['question-type'] = 'Clarification'
                        remove_unwanted_fields(utter_new)
                        dialog_list_new.append(utter_new)

                        utter_id += 1
                        utter = utter_list[utter_id]
                        utter_new = utter.copy()
                        del utter_new['ques_type_id']
                        remove_unwanted_fields(utter_new)
                        dialog_list_new.append(utter_new)

                        utter_id += 1
                        utter = utter_list[utter_id]
                        utter_new = utter.copy()
                        utter_new['ques_type_id'] = utter_list[utter_id-2]['ques_type_id']
                        utter_new['sec_ques_type'] = utter_list[utter_id-2]['sec_ques_type']
                        utter_new['sec_ques_sub_type'] = utter_list[utter_id-2]['sec_ques_sub_type']
                        utter_new['question-type'] = get_ques_type(utter_new)
                        dialog_list_new.append(utter_new)

                        utter_id += 1


                    elif 'ques_type_id' in utter and utter['ques_type_id'] == 7 and 'count_ques_sub_type' in utter and utter['count_ques_sub_type'] in [7,8,9] and (utter_id+1) < len(utter_list) and 'utterance' in utter_list[utter_id+1] and 'Did you mean' in utter_list[utter_id+1]['utterance']:
                        utter_new = utter.copy()
                        utter_new['ques_type_id'] = 3
                        utter_new['type_list'] = get_type_list(utter_new)
                        utter_new['question-type'] = 'Clarification'
                        remove_unwanted_fields(utter_new)
                        dialog_list_new.append(utter_new)

                        utter_id += 1
                        utter = utter_list[utter_id]
                        utter_new = utter.copy()
                        remove_unwanted_fields(utter_new)
                        dialog_list_new.append(utter_new)

                        utter_id += 1
                        utter = utter_list[utter_id]
                        utter_new = utter.copy()
                        utter_new['ques_type_id'] = utter_list[utter_id-2]['ques_type_id']
                        utter_new['count_ques_type'] = utter_list[utter_id-2]['count_ques_type']
                        utter_new['count_ques_sub_type'] = utter_list[utter_id-2]['count_ques_sub_type']
                        utter_new['is_incomplete'] = 0
                        utter_new['question-type'] = get_ques_type(utter_new)
                        dialog_list_new.append(utter_new)

                        utter_id += 1

                    elif 'ques_type_id' in utter and utter['ques_type_id'] == 8 and 'count_ques_sub_type' in utter and utter['count_ques_sub_type'] in [8,9,10] and (utter_id+1) < len(utter_list) and 'utterance' in utter_list[utter_id+1] and 'Did you mean' in utter_list[utter_id+1]['utterance']:
                        utter_new = utter.copy()
                        utter_new['ques_type_id'] = 3
                        utter_new['type_list'] = get_type_list(utter_new)
                        utter_new['question-type'] = 'Clarification'
                        remove_unwanted_fields(utter_new)
                        dialog_list_new.append(utter_new)

                        utter_id += 1
                        utter = utter_list[utter_id]
                        utter_new = utter.copy()
                        remove_unwanted_fields(utter_new)
                        dialog_list_new.append(utter_new)

                        utter_id += 1
                        utter = utter_list[utter_id]
                        utter_new = utter.copy()
                        utter_new['ques_type_id'] = utter_list[utter_id-2]['ques_type_id']
                        utter_new['count_ques_type'] = utter_list[utter_id-2]['count_ques_type']
                        utter_new['count_ques_sub_type'] = utter_list[utter_id-2]['count_ques_sub_type']
                        utter_new['is_incomplete'] = 0
                        utter_new['question-type'] = get_ques_type(utter_new)
                        dialog_list_new.append(utter_new)

                        utter_id += 1
                    else:
                        if 'ques_type_id' in utter:
                            utter_new = utter.copy()
                            utter_new['type_list'] = get_type_list(utter_new)
                            utter_new['question-type'] = get_ques_type(utter_new)
                            remove_unwanted_fields(utter_new)
                            dialog_list_new.append(utter_new)

                            utter_id += 1
                        else:
                            utter_new = utter.copy()
                            remove_unwanted_fields(utter_new)
                            dialog_list_new.append(utter_new)

                            utter_id += 1

                try:
                    assert is_valid_dialog(dialog_list_new)
                except:
                    print dialog_json_file
                    print 'Unequal number of utterances in dialog'

                try:
                    assert len(utter_list) == len(dialog_list_new)
                except:
                    print dialog_json_file
                    print 'len of source and dest list unequal'

                try:
                    assert check_unwanted_fields(dialog_list_new)
                except:
                    print dialog_json_file
                    print 'unwanted fields present in utter'

                with open(os.path.join(args.output_dir, dir_name, filename), 'wb') as outfile:
                    json.dump(dialog_list_new, outfile, indent = 1)

        except:
            print 'Issue with filename: %s' % dialog_json_file
            logging.exception('Something aweful happened')
            continue
