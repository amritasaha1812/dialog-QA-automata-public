#!/home/vardaan/anaconda2/bin/python -u
import codecs, random, pickle, json, math, logging, sys, os, resource, fcntl, collections
from fcntl import flock, LOCK_EX, LOCK_NB
from collections import defaultdict
from collections import Counter
import numpy as np
import pattern.en
from pattern.en import lemma, conjugate, tenses
import argparse
import itertools
import inflect
import fnmatch
# from nltk.corpus import stopwords
import nltk, codecs
# from nltk import word_tokenize
import timeit
import time

sys.path.append(os.getcwd())
from load_wikidata2 import *

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

def is_indirect(ques_utter_dict):
    utter = ques_utter_dict
    if 'ques_type_id' in utter and utter['ques_type_id']==2 and 'sec_ques_sub_type' in utter and utter['sec_ques_sub_type'] in [2,3]:
        return True
    elif 'ques_type_id' in utter and utter['ques_type_id']==5 and 'bool_ques_type' in utter and utter['bool_ques_type'] in [2,3,5,6]:
        return True
    elif 'ques_type_id' in utter and utter['ques_type_id']==7 and 'count_ques_sub_type' in utter and utter['count_ques_sub_type'] in [7,8,9]:
        return True
    elif 'ques_type_id' in utter and utter['ques_type_id']==8 and 'count_ques_sub_type' in utter and utter['count_ques_sub_type'] in [8,9,10]:
        return True
    return False

def is_valid_dialog(dialog_list):
    for idx, utter in enumerate(dialog_list):
        if idx >= len(dialog_list)-1:
            break
        if utter['speaker'] == 'USER':
            try:
                assert dialog_list[idx+1]['speaker'] == 'SYSTEM'
            except:
                return False
        elif utter['speaker'] == 'SYSTEM':
            try:
                assert dialog_list[idx+1]['speaker'] == 'USER'
            except:
                return False
    return True

def is_par_rel_overlap(par_id, pid, annot):
    try:
        assert par_id in child_par_dict_name_2 and pid in prop_data
    except:
        return False

    par_name = child_par_dict_name_2[par_id]
    pid_name = prop_data[pid]

    par_name_tokens = nltk.word_tokenize(par_name)
    pid_name_tokens = nltk.word_tokenize(pid_name)
    annot_tokens = nltk.word_tokenize(annot)

    overlap_tokens = list(set(par_name_tokens) & set(pid_name_tokens) & set(annot_tokens))

    for ot in overlap_tokens:
        if ot not in stop_word_list:
            return True

    return False

def sing2plural(par):
    '''
    ques: should be in template format with YYY or XXX intact
    '''
    return pattern.en.pluralize(par)


# stop_word_list = set(stopwords.words('english'))
stop_word_list = set([u'all', u'just', u'being', u'over', u'both', u'through', u'yourselves', u'its', u'before', u'o', u'hadn', u'herself', u'll', u'had', u'should', u'to', u'only', u'won', u'under', u'ours', u'has', u'do', u'them', u'his', u'very', u'they', u'not', u'during', u'now', u'him', u'nor', u'd', u'did', u'didn', u'this', u'she', u'each', u'further', u'where', u'few', u'because', u'doing', u'some', u'hasn', u'are', u'our', u'ourselves', u'out', u'what', u'for', u'while', u're', u'does', u'above', u'between', u'mustn', u't', u'be', u'we', u'who', u'were', u'here', u'shouldn', u'hers', u'by', u'on', u'about', u'couldn', u'of', u'against', u's', u'isn', u'or', u'own', u'into', u'yourself', u'down', u'mightn', u'wasn', u'your', u'from', u'her', u'their', u'aren', u'there', u'been', u'whom', u'too', u'wouldn', u'themselves', u'weren', u'was', u'until', u'more', u'himself', u'that', u'but', u'don', u'with', u'than', u'those', u'he', u'me', u'myself', u'ma', u'these', u'up', u'will', u'below', u'ain', u'can', u'theirs', u'my', u'and', u've', u'then', u'is', u'am', u'it', u'doesn', u'an', u'as', u'itself', u'at', u'have', u'in', u'any', u'if', u'again', u'no', u'when', u'same', u'how', u'other', u'which', u'you', u'shan', u'needn', u'haven', u'after', u'most', u'such', u'why', u'a', u'off', u'i', u'm', u'yours', u'so', u'y', u'the', u'having', u'once'])
stop_par_list = ['Q21025364', 'Q19361238', 'Q21027609', 'Q20088085', 'Q15184295', 'Q11266439', 'Q17362920', 'Q19798645', 'Q26884324', 'Q14204246', 'Q13406463', 'Q14827288', 'Q4167410', 'Q21484471', 'Q17442446', 'Q4167836', 'Q19478619', 'Q24017414', 'Q19361238', 'Q24027526', 'Q15831596', 'Q24027474', 'Q23958852', 'Q24017465', 'Q24027515', 'Q1924819']

inf_eng = inflect.engine()
# child_par_dict_val = child_par_dict.values()

# HYPERPARAMETERS

parser = argparse.ArgumentParser(description='Hyper-parameter settings')
parser.add_argument('--input_dir', dest='input_dir', type=str, help='directory in which dialogs are to be verified', required=True)
parser.add_argument('--output_dir',dest='output_dir', type=str, help = 'name of dir (wrt cwd) where dialogue dirs are created',required=True) # should be required

args = parser.parse_args()
print(args)
# args.input_dir = '/home/vardaan/projects/rpp-bengioy/vardaan/CSQA/train/'
# args.output_dir = '/home/vardaan/projects/rpp-bengioy/vardaan/train/'



if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

f1 = open(os.path.join(args.output_dir,'recons_log.txt'),'w')

count = 0

var_list = ['N','Qid','Qid_1','Qid_2','prop_res','prop_res_1','prop_Qid_par', 'sub_par', 'sub_par_1', 'sub_par_2', 'obj_par', 'obj_par_1', 'obj_par_2', 'Z','obj','obj2','qualifier_choice','set_op']

for dir_name in [d for d in os.listdir(args.input_dir) if os.path.isdir(os.path.join(args.input_dir, d))]:
    # if count > 500:
    #     break
    print dir_name
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
        except:
            f1.write('Issue with filename: %s' % dialog_json_file)
            continue
        try:
            dialog_list = []
            utter_id = 0

            while utter_id < len(utter_list):
                utter = utter_list[utter_id]

                for var in var_list:
                    if var in globals():
                        del var
                        
                if 'ques_type_id' in utter and utter['ques_type_id'] == 2 and utter['sec_ques_sub_type'] == 2 and 'entities' in utter_list[utter_id-2] and len(utter_list[utter_id-2]['entities'])>0 and utter_list[utter_id-2]['entities'][0] in child_par_dict and child_par_dict[utter_list[utter_id-2]['entities'][0]] in set([child_par_dict[x] for i,x in enumerate(utter_list[utter_id-2]['entities']) if x in child_par_dict and i>0]) and 'ques_type_id' in utter_list[utter_id-2] and utter['Qid'] in utter_list[utter_id-2]['entities'] and (('ques_type_id' not in utter_list[utter_id+1]) or ('ques_type_id' in utter_list[utter_id+1] and utter_list[utter_id+1]['ques_type_id']!=3)):
                    sec_ques_type = utter['sec_ques_type']
                    sec_ques_sub_type = utter['sec_ques_sub_type']

                    new_utter_dict = {}
                    for field in utter:
                        if field not in ['utterance','signature']:
                            new_utter_dict[field] = utter[field]

                    if sec_ques_type == 1: # Subject based ques.
                        Qid = utter['Qid']
                        prop_res = utter['prop_res']
                        prop_Qid_par = utter['prop_Qid_par']
                        is_ans_gt_1 = utter['len(ans_list) > 1']

                        if not is_ans_gt_1:
                            is_pphrase_ov = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in sing_sub_annot[prop_res]]
                            is_pphrase_ov_wh = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in sing_sub_annot_wh[prop_res]]

                            if False in is_pphrase_ov:
                                ques = random.choice([sing_sub_annot[prop_res][i] for i in range(len(sing_sub_annot[prop_res])) if is_pphrase_ov[i] == False])
                                ques = ques.replace('OPP',child_par_dict_name_2[prop_Qid_par])
                            else:
                                ques = random.choice(sing_sub_annot_wh[prop_res])

                                if 'Which OPP' in ques:
                                    if prop_Qid_par != 'Q215627':
                                        ques = ques.replace('Which OPP','What')
                                    else:
                                        ques = ques.replace('Which OPP','Who')
                                else:
                                    ques = ques.replace('OPP',child_par_dict_name_2[prop_Qid_par])
                        else:
                            is_pphrase_ov = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in plu_sub_annot[prop_res]]
                            is_pphrase_ov_wh = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in plu_sub_annot_wh[prop_res]]

                            if False in is_pphrase_ov:
                                ques = random.choice([plu_sub_annot[prop_res][i] for i in range(len(plu_sub_annot[prop_res])) if is_pphrase_ov[i] == False])
                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                            else:
                                ques = random.choice(plu_sub_annot_wh[prop_res])

                                if 'Which OPP' in ques:
                                    if prop_Qid_par != 'Q215627':
                                        ques = ques.replace('Which OPP','What')
                                    else:
                                        ques = ques.replace('Which OPP','Who')
                                else:
                                    ques = ques.replace('OPP',child_par_dict_name_2[prop_Qid_par])

                        ques = ques.replace('XXX',item_data[Qid])

                    elif sec_ques_type == 2: # Object based ques.
                        Qid = utter['Qid']
                        prop_res = utter['prop_res']
                        prop_Qid_par = utter['prop_Qid_par']
                        is_ans_gt_1 = utter['len(ans_list) > 1']

                        if not is_ans_gt_1:
                            is_pphrase_ov = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in sing_obj_annot[prop_res]]
                            is_pphrase_ov_wh = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in sing_obj_annot_wh[prop_res]]

                            if False in is_pphrase_ov:
                                ques = random.choice([sing_obj_annot[prop_res][i] for i in range(len(sing_obj_annot[prop_res])) if is_pphrase_ov[i] == False])
                                ques = ques.replace('SPP',child_par_dict_name_2[prop_Qid_par])
                            else:
                                ques = random.choice(sing_obj_annot_wh[prop_res])

                                if 'Which SPP' in ques:
                                    if prop_Qid_par != 'Q215627':
                                        ques = ques.replace('Which SPP','What')
                                    else:
                                        ques = ques.replace('Which SPP','Who')
                                else:
                                    ques = ques.replace('SPP',child_par_dict_name_2[prop_Qid_par])
                        else:
                            is_pphrase_ov = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in plu_obj_annot[prop_res]]
                            is_pphrase_ov_wh = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in plu_obj_annot_wh[prop_res]]

                            if False in is_pphrase_ov:
                                ques = random.choice([plu_obj_annot[prop_res][i] for i in range(len(plu_obj_annot[prop_res])) if is_pphrase_ov[i] == False])
                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                            else:
                                ques = random.choice(plu_obj_annot_wh[prop_res])

                                if 'Which SPP' in ques:
                                    if prop_Qid_par != 'Q215627':
                                        ques = ques.replace('Which SPP','What')
                                    else:
                                        ques = ques.replace('Which SPP','Who')
                                else:
                                    ques = ques.replace('SPP',child_par_dict_name_2[prop_Qid_par])

                        ques = ques.replace('YYY',item_data[Qid])

                    #*****************************************************************
                    new_utter_dict['utterance'] = ques
                    new_utter_dict['sec_ques_sub_type'] = 1
                    new_utter_dict['description'] = 'Simple Question|Single Entity'
                    new_utter_dict['signature'] = get_dict_signature(new_utter_dict)
                    dialog_list.append(new_utter_dict)
                    #*****************************************************************
                    
                else: # keep the utterance dict as-is
                    new_utter_dict = utter
                    dialog_list.append(new_utter_dict.copy())

                ##########################################################################################
                # new_utter_dict = {}
                # for field in utter:
                #     if field not in ['utterance','signature']:
                #         new_utter_dict[field] = utter[field]
                # new_utter_dict['utterance'] = ques
                # new_utter_dict['signature'] = get_dict_signature(new_utter_dict.copy())

                # dialog_list.append(new_utter_dict.copy())

                #**************
                utter_id += 1
                #**************

            try:
                assert is_valid_dialog(dialog_list)
            except:
                print 'Dialog list not valid'
            with open(os.path.join(args.output_dir, dir_name, filename), 'wb') as outfile:
                json.dump(dialog_list, outfile, indent = 1)

        except:
            logging.exception('Something aweful happened')

f1.close()
