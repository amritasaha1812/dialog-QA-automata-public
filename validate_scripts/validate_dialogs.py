#!/home/vardaan/anaconda2/bin/python
import codecs, random, pickle, json, math, logging, sys, os, resource, fcntl, collections
from fcntl import flock, LOCK_EX, LOCK_NB
from collections import defaultdict
from collections import Counter
import numpy as np

import argparse
import itertools
import inflect
import fnmatch
import codecs

import timeit
import time

sys.path.append(os.getcwd())

# from load_wikidata2 import *


'''
Validation for automata ques. except ALL kinds of incomplete ques.
'''
# HYPERPARAMETERS

parser = argparse.ArgumentParser(description='Hyper-parameter settings')
# parser.add_argument('--input_dir', dest='input_dir', type=str, help='directory in which dialogs are to be verified', required=True)
# parser.add_argument('--strict', action='store_true', help='enables strict matching of ans_list_full. Else, if subset of ans_list_full present, it passes')

args = parser.parse_args()

# args.input_dir = '/home/vardaan/projects/rpp-bengioy/vardaan/CSQA_v3/train/'
# args.input_dir = '/home/vardaan/dialog-QA-automata/test/'
args.input_dir = 'test/'
# args.strict = False
args.strict = True

print(args)

child_par_dict_key_set = set(child_par_dict.keys())
count = 0

var_list = ['N','Qid','Qid_1','Qid_2','prop_res','prop_res_1','prop_Qid_par', 'sub_par', 'sub_par_1', 'sub_par_2', 'obj_par', 'obj_par_1', 'obj_par_2', 'Z','obj','obj2','qualifier_choice','set_op']

flag = False

for dir_name in [d for d in os.listdir(args.input_dir) if os.path.isdir(os.path.join(args.input_dir, d))]:
    # if count > 500:
    #     break
    # if dir_name != 'QA_3':
    #     continue

    if flag:
        break
    for filename in os.listdir(os.path.join(args.input_dir, dir_name)):
        count += 1

        # if count > 50:
        #     flag = True
        #     break
        if count % 10 == 0:
            print count

        dialog_json_file = os.path.join(args.input_dir, dir_name, filename)
        # print dialog_json_file
        if not dialog_json_file.endswith('.json'):
            continue
        try:
            with open(dialog_json_file,'r') as data_file:
                utter_list = json.load(data_file)
        except:
            # f1.write('Issue with filename: %s' % dialog_json_file)
            continue
        try:
            dialog_list = []

            for utter_id, utter in enumerate(utter_list):
                if 'ques_type_id' in utter: # ignore answer utterances
                    for var in var_list:
                        if var in globals():
                            del var
                            
                    ques_type_id = utter['ques_type_id']

                    if ques_type_id==1: # Basic Question

                        Qid = utter['Qid']
                        prop_res = utter['prop_res']
                        prop_Qid_par = utter['prop_Qid_par']
                        is_ans_gt_1 = utter['len(ans_list) > 1']

                        ans_list = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                        ans_list_full = list(set(ans_list))

                        try:
                            assert set(ans_list_full) == set(utter_list[utter_id+1]['ans_list_full'])
                        except:
                            print dialog_json_file
                            print "Error for ques_type_id = %d" % ques_type_id
                            n_similar = len(set(ans_list_full) & set(utter_list[utter_id+1]['ans_list_full']))
                            print 'n_similar = %d, len(gold) = %d, len(existing) = %d' % (n_similar, len(set(ans_list_full)), len(set(utter_list[utter_id+1]['ans_list_full'])))

                    elif ques_type_id==2: # Secondary question  

                        sec_ques_type = utter['sec_ques_type']
                        sec_ques_sub_type = utter['sec_ques_sub_type']

                        if sec_ques_type == 1: # Subject based ques.
                            if sec_ques_sub_type==1 or sec_ques_sub_type==2: # Direct (Singular) Question or Singular Indirect Question
                                Qid = utter['Qid']
                                prop_res = utter['prop_res']
                                prop_Qid_par = utter['prop_Qid_par']
                                is_ans_gt_1 = utter['len(ans_list) > 1']

                                ans_list = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                                ans_list_full = list(set(ans_list))
                                

                            elif sec_ques_sub_type==3 or sec_ques_sub_type == 4: # Plural Indirect Question or Plural Basic Question
                                Qid = utter['Qid']
                                prop_res = utter['prop_res']
                                prop_Qid_par = utter['prop_Qid_par']
                                sub_list = utter['sub_list']

                                ans_list_full = [q for sub in sub_list for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]

                        elif sec_ques_type == 2: # Object based ques.
                            if sec_ques_sub_type == 1 or sec_ques_sub_type == 2: # Basic Question (Singular) or Basic Question (Plural)
                                Qid = utter['Qid']
                                prop_res = utter['prop_res']
                                prop_Qid_par = utter['prop_Qid_par']
                                is_ans_gt_1 = utter['len(ans_list) > 1']

                                ans_list = [q for q in reverse_dict[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                                ans_list_full = list(set(ans_list))
                                
                            elif sec_ques_sub_type == 3 or sec_ques_sub_type == 4: # Object based Plural (Indirect/Basic) question
                                Qid = utter['Qid']
                                prop_res = utter['prop_res']
                                prop_Qid_par = utter['prop_Qid_par']
                                sub_list = utter['sub_list']

                                ans_list_full = [q for sub in sub_list for q in reverse_dict[sub][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]

                        try:
                            if 'Did you mean' in utter_list[utter_id+1]['utterance']:
                                assert set(ans_list_full) == set(utter_list[utter_id+3]['ans_list_full'])
                            else:
                                assert set(ans_list_full) == set(utter_list[utter_id+1]['ans_list_full'])
                            # print "Validation successful for ques_type_id = %d, sub-type=%d, sub-sub-type=%d" % (ques_type_id, sec_ques_type, sec_ques_sub_type)
                        except:
                            print "Error for ques_type_id = %d, sub-type=%d, sub-sub-type=%d" % (ques_type_id, sec_ques_type, sec_ques_sub_type)
                            print utter['utterance']
                            print dialog_json_file
                            if 'Did you mean' in utter_list[utter_id+1]['utterance']:
                                n_similar = len(set(ans_list_full) & set(utter_list[utter_id+3]['ans_list_full']))
                                print 'n_similar = %d, len(gold) = %d, len(existing) = %d' % (n_similar, len(set(ans_list_full)), len(set(utter_list[utter_id+3]['ans_list_full'])))
                            else:
                                print utter_list[utter_id+1]
                                print dialog_json_file
                                n_similar = len(set(ans_list_full) & set(utter_list[utter_id+1]['ans_list_full']))
                                print 'n_similar = %d, len(gold) = %d, len(existing) = %d' % (n_similar, len(set(ans_list_full)), len(set(utter_list[utter_id+1]['ans_list_full'])))


                    elif ques_type_id==3: #clarification ques. NO new question, just clarification of previous question
                        # Do Nothing
                        pass

                    elif ques_type_id == 4: # Set based questioning
                        is_inc = utter['is_inc']
                        is_sub = utter['is_sub']
                        is_mult_pid = utter['is_mult_pid']
                        prop_res = utter['prop_res']
                        prop_res_1 = utter['prop_res_1']
                        Qid = utter['Qid']
                        Qid_1 = utter['Qid_1']
                        prop_Qid_par = utter['prop_Qid_par']
                        set_op_choice = utter['set_op_choice']

                        set_op_dict = {1:'OR',2:'AND',3:'DIFF'}

                        if is_sub:
                            ans_list_A = list(set(wikidata[Qid_1][prop_res_1]) & child_par_dict_key_set & set(par_child_dict[prop_Qid_par]))
                            ans_list_B = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]

                        else:
                            ans_list_A = list(set(reverse_dict[Qid_1][prop_res_1]) & child_par_dict_key_set & set(par_child_dict[prop_Qid_par]))
                            ans_list_B = [q for q in reverse_dict[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]


                        if set_op_choice == 1:
                            ans_list = list(set(ans_list_A).union(ans_list_B)) # UNION
                        elif set_op_choice == 2:
                            ans_list = list(set(ans_list_A).intersection(ans_list_B)) # INTERSECTION
                        elif set_op_choice == 3:
                            ans_list = list(set(ans_list_A).difference(ans_list_B)) # DIFFERENCE

                        ans_list = list(set(ans_list))
                        ans_list_full = ans_list
                        
                        try:
                            if args.strict:
                                assert set(ans_list_full) == set(utter_list[utter_id+1]['ans_list_full'])
                            else:
                                assert (set(ans_list_full) & set(utter_list[utter_id+1]['ans_list_full'])) == set(ans_list_full)
                            # print 'Validation successful for ques_type_id = %d' % ques_type_id
                        except:
                            print "Error for ques_type_id = %d, is_inc = %d, is_sub=%d" % (ques_type_id, is_inc, is_sub)
                            n_similar = len(set(ans_list_full) & set(utter_list[utter_id+1]['ans_list_full']))
                            print 'n_similar = %d, len(gold) = %d, len(existing) = %d' % (n_similar, len(set(ans_list_full)), len(set(utter_list[utter_id+1]['ans_list_full'])))
                            # print utter

                            if 'ans_list_A' in utter_list[utter_id+1] and 'ans_list_B' in utter_list[utter_id+1]:
                                ans_list_A_new = utter_list[utter_id+1]['ans_list_A']
                                ans_list_B_new = utter_list[utter_id+1]['ans_list_B']

                                if set_op_choice == 1:
                                    ans_list_new = list(set(ans_list_A_new).union(ans_list_B_new)) # UNION
                                elif set_op_choice == 2:
                                    ans_list_new = list(set(ans_list_A_new).intersection(ans_list_B_new)) # INTERSECTION
                                elif set_op_choice == 3:
                                    ans_list_new = list(set(ans_list_A_new).difference(ans_list_B_new)) # DIFFERENCE

                                try:
                                    assert set(utter_list[utter_id+1]['ans_list_full']) == set(ans_list_full)
                                except:
                                    try:
                                        assert set(ans_list_A_new) == set(ans_list_A)
                                    except:
                                        print 'ans_list_A does not match'
                                        print 'Qid_1 = %s' % Qid_1
                                        print 'Qid = %s' % Qid
                                        print 'prop_res = %s' % prop_res
                                        print 'prop_res_1 = %s' % prop_res_1

                                    try:
                                        assert set(ans_list_B_new) == set(ans_list_B)
                                    except:
                                        print 'ans_list_B does not match'


                    elif ques_type_id == 5: # Boolean (secondary) question
                        bool_ques_type = utter['bool_ques_type']

                        if bool_ques_type in [1,2,4,5]:
                            
                            if bool_ques_type in [1,2]:
                                obj = utter['obj']
                                Qid = utter['Qid']
                                prop_res = utter['prop_res']
                                prop_Qid_par = utter['prop_Qid_par']

                                pos_list = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par and q != Qid]

                                if obj in pos_list:
                                    ans = 'YES'
                                else:
                                    ans = 'NO'
                            elif bool_ques_type in [4,5]:
                                obj = utter['obj']
                                obj2 = utter['obj2']
                                Qid = utter['Qid']
                                prop_res = utter['prop_res']
                                prop_Qid_par = utter['prop_Qid_par']

                                pos_list = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par and q != Qid]

                                if obj in pos_list and obj2 in pos_list:
                                    ans = 'YES'
                                elif obj not in pos_list and obj2 not in pos_list:
                                    ans = 'NO'
                                else:
                                    ans = '%s and %s respectively' % (('YES' if obj in pos_list else 'NO'),('YES' if obj2 in pos_list else 'NO'))
                            
                        elif bool_ques_type == 3:
                            Qid = utter['Qid']
                            prop_res = utter['prop_res']
                            prop_Qid_par = utter['prop_Qid_par']
                            sub = utter['sub']

                            pos_list = [q for q in reverse_dict[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]

                            if sub in pos_list:
                                ans = 'YES'
                            else:
                                ans = 'NO'
                            
                        elif bool_ques_type == 6:
                            prop_res = utter['prop_res']
                            prop_Qid_par = utter['prop_Qid_par']
                            sub = utter['sub']
                            sub_list = utter['sub_list']

                            bool_list = []

                            for x in sub_list:
                                if x in reverse_dict and prop_res in reverse_dict[x] and sub in reverse_dict[x][prop_res]:
                                    bool_list.append(1)
                                else:
                                    bool_list.append(0)

                            if sum(bool_list) == len(bool_list):
                                ans = 'YES'
                            else:
                                ans = 'NO'

                        #***************************************************************
                        try:
                            assert ans == utter_list[utter_id+1]['utterance']
                            # print 'Validation successful for ques_type_id = %d' % ques_type_id
                        except:
                            print "Error for ques_type_id = %d, bool_ques_type = %d" % (ques_type_id, bool_ques_type)
                            print 'obj = %s' % obj
                            print 'Qid = %s' % Qid
                            print 'prop_res = %s' % prop_res
                            print 'computed ans = %s' % ans
                            print 'actual ans = %s' % utter_list[utter_id+1]['utterance']
                        #***************************************************************


                    elif ques_type_id == 6: # Incomplete question
                        # do nothing
                        pass
                        # inc_ques_type = utter['inc_ques_type']

                        # if type_choice == 1: # object parent is changed, subject and predicate remain same
                        #     ans_list = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par_new]

                        # elif type_choice == 2: # only subject is changed, parent and predicate remains same
                        #     ans_list = [q for q in wikidata[sub_choice][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]

                        # elif type_choice == 3: # Incomplete count-based ques
                        #     ans_list = [q for q in wikidata[sub_choice][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]

                    elif ques_type_id == 7: # count-based question
                        count_ques_type = utter['count_ques_type']
                        count_ques_sub_type = utter['count_ques_sub_type']

                        # if utter['is_incomplete'] == 1: # no validation possible for incomplete dialogs beacuse meta-data not present
                        #     continue

                        # if count_ques_sub_type in [1,7]:
                        #     Qid = utter['Qid']
                        #     prop_Qid_par = utter['prop_Qid_par']
                        #     prop_res = utter['prop_res']

                        # elif count_ques_sub_type in [2,3,4,5,6,8,9]:
                        #     obj_par = utter['obj_par']
                        #     sub_par = utter['sub_par']
                        #     prop_res = utter['prop_res']
                        #     qualifier_choice = utter['qualifier_choice']
                        #     if count_ques_sub_type in [3,5]:
                        #         N = utter['N']
                        #     elif count_ques_sub_type in [4,6,8,9]:
                        #         Z = utter['Z']

                        if count_ques_type == 1: # sub-based
                            if count_ques_sub_type in [1,7]: # basic form
                                Qid = utter['Qid']
                                prop_Qid_par = utter['prop_Qid_par']
                                prop_res = utter['prop_res']

                                ans_list_full = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]

                            elif count_ques_sub_type in [2,3,4,5,6,8,9]:
                                obj_par = utter['obj_par']
                                sub_par = utter['sub_par']
                                prop_res = utter['prop_res']
                                qualifier_choice = utter['qualifier_choice']

                                cand_obj_list = list(set([q for q in par_child_dict[obj_par] if q in reverse_dict and prop_res in reverse_dict[q]]))

                                cand_obj_list_score = {}
                                for obj in cand_obj_list:
                                    cand_obj_list_score[obj] = len([q for q in reverse_dict[obj][prop_res] if q in child_par_dict and child_par_dict[q] == sub_par])

                                cand_obj_list_score_arr = np.asarray(cand_obj_list_score.values())

                                if count_ques_sub_type == 2:
                                    if qualifier_choice == 'min':
                                        ans_list_full = [x for x in cand_obj_list if cand_obj_list_score[x] == min(cand_obj_list_score.values())]
                                    elif qualifier_choice == 'max':
                                        ans_list_full = [x for x in cand_obj_list if cand_obj_list_score[x] == max(cand_obj_list_score.values())]

                                elif count_ques_sub_type in [3,5]:
                                    N = utter['N']
                                    if qualifier_choice == 'atleast':
                                        ans_list_full = [x for x in cand_obj_list if cand_obj_list_score[x] >= N]
                                    elif qualifier_choice == 'atmost':
                                        ans_list_full = [x for x in cand_obj_list if cand_obj_list_score[x] <= N]
                                    elif qualifier_choice == 'exactly':
                                        ans_list_full = [x for x in cand_obj_list if cand_obj_list_score[x] == N]
                                    elif qualifier_choice == 'around' or qualifier_choice == 'approximately':
                                        ans_list_full = [x for x in cand_obj_list if cand_obj_list_score[x] > (N - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[x] < (N + np.std(cand_obj_list_score_arr))]

                                elif count_ques_sub_type in [4,6,8,9]:
                                    Z = utter['Z']

                                    Z_score = cand_obj_list_score[Z]

                                    # print 'calcul z score = %d' % Z_score
                                    # print 'orig. z score = %d' % utter['Z_score']

                                    if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                        ans_list_full = [x for x in cand_obj_list if cand_obj_list_score[x] > Z_score]
                                    elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                        ans_list_full = [x for x in cand_obj_list if cand_obj_list_score[x] < Z_score]
                                    elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                        ans_list_full = [x for x in cand_obj_list if cand_obj_list_score[x] > (Z_score - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[x] < (Z_score + np.std(cand_obj_list_score_arr))]
                                        # ans_list_full = [cand_obj_list[i] for i in xrange(len(cand_obj_list)) if cand_obj_list_score[i] > (Z_score - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[i] < (Z_score + np.std(cand_obj_list_score_arr))]

                        elif count_ques_type == 2: # obj-based
                            if count_ques_sub_type in [1,7]: # basic form
                                Qid = utter['Qid']
                                prop_Qid_par = utter['prop_Qid_par']
                                prop_res = utter['prop_res']       
                                ans_list_full = [q for q in reverse_dict[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]

                            elif count_ques_sub_type in [2,3,4,5,6,8,9]:
                                obj_par = utter['obj_par']
                                sub_par = utter['sub_par']
                                prop_res = utter['prop_res']
                                qualifier_choice = utter['qualifier_choice']

                                cand_sub_list = list(set([q for q in par_child_dict[sub_par] if q in wikidata and prop_res in wikidata[q]]))
                                cand_sub_list_score = {}
                                for sub in cand_sub_list:
                                    cand_sub_list_score[sub] = len([q for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q] == obj_par])

                                cand_sub_list_score_arr = np.asarray(cand_sub_list_score.values())

                                if count_ques_sub_type == 2:
                                    if qualifier_choice == 'min':
                                        ans_list_full = [x for x in cand_sub_list if cand_sub_list_score[x]==min(cand_sub_list_score.values())]
                                    elif qualifier_choice == 'max':
                                        ans_list_full = [x for x in cand_sub_list if cand_sub_list_score[x]==max(cand_sub_list_score.values())]

                                elif count_ques_sub_type in [3,5]:
                                    N = utter['N']
                                    if qualifier_choice == 'atleast':
                                        ans_list_full = [x for x in cand_sub_list if cand_sub_list_score[x] >= N]
                                    elif qualifier_choice == 'atmost':
                                        ans_list_full = [x for x in cand_sub_list if cand_sub_list_score[x] <= N]
                                    elif qualifier_choice == 'exactly':
                                        ans_list_full = [x for x in cand_sub_list if cand_sub_list_score[x] == N]
                                    elif qualifier_choice == 'around' or qualifier_choice == 'approximately':
                                        ans_list_full = [x for x in cand_sub_list if cand_sub_list_score[x] > (N - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (N + np.std(cand_sub_list_score_arr))]

                                elif count_ques_sub_type in [4,6,8,9]:
                                    Z = utter['Z']
                                    Z_score = cand_sub_list_score[Z]                           

                                    if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                        ans_list_full = [x for x in cand_sub_list if cand_sub_list_score[x] > Z_score]
                                    elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                        ans_list_full = [x for x in cand_sub_list if cand_sub_list_score[x] < Z_score]
                                    elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                        ans_list_full = [x for x in cand_sub_list if cand_sub_list_score[x] > (Z_score - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (Z_score + np.std(cand_sub_list_score_arr))]

                        try:
                            if 'Did you mean' in utter_list[utter_id+1]['utterance']:
                                if args.strict:
                                    assert set(ans_list_full) == set(utter_list[utter_id+3]['ans_list_full'])
                                else:
                                    assert set(utter_list[utter_id+3]['ans_list_full']).issubset(set(ans_list_full))
                            else:
                                if args.strict:
                                    assert set(ans_list_full) == set(utter_list[utter_id+1]['ans_list_full'])
                                else:
                                    assert set(utter_list[utter_id+1]['ans_list_full']).issubset(set(ans_list_full))
                            # print 'Validation successful for ques_type_id = %d, sub-type=%d, sub-sub-type=%d' % (ques_type_id, count_ques_type, count_ques_sub_type)
                        except:
                            print "Error for ques_type_id = %d, sub-type=%d, sub-sub-type=%d" % (ques_type_id, count_ques_type, count_ques_sub_type)
                            print utter['utterance']
                            if 'Did you mean' in utter_list[utter_id+1]['utterance']:
                                n_similar = len(set(ans_list_full) & set(utter_list[utter_id+3]['ans_list_full']))
                                print 'n_similar = %d, len(gold) = %d, len(existing) = %d' % (n_similar, len(set(ans_list_full)), len(set(utter_list[utter_id+3]['ans_list_full'])))
                                # print set(ans_list_full)
                                # print set(utter_list[utter_id+3]['ans_list_full'])
                                # print (set(ans_list_full) - set(utter_list[utter_id+3]['ans_list_full']))
                                # print (set(utter_list[utter_id+3]['ans_list_full']) - set(ans_list_full))
                            else:
                                n_similar = len(set(ans_list_full) & set(utter_list[utter_id+1]['ans_list_full']))
                                print 'n_similar = %d, len(gold) = %d, len(existing) = %d' % (n_similar, len(set(ans_list_full)), len(set(utter_list[utter_id+1]['ans_list_full'])))
                                # print set(ans_list_full)
                                # print set(utter_list[utter_id+1]['ans_list_full'])
                                # print (set(ans_list_full) - set(utter_list[utter_id+1]['ans_list_full']))
                                # print (set(utter_list[utter_id+1]['ans_list_full']) - set(ans_list_full))

                    elif ques_type_id == 8: # count-set-based question
                        count_ques_type = utter['count_ques_type']
                        count_ques_sub_type = utter['count_ques_sub_type']

                        # if utter['is_incomplete'] == 1: # no validation possible for incomplete dialogs beacuse meta-data not present
                        #     continue
                        
                        # if count_ques_type == 1:
                        #     if count_ques_sub_type == 1:
                        #         Qid = utter['Qid']
                        #         Qid_2 = utter['Qid_2']
                        #         obj_par = utter['obj_par']
                        #         prop_res = utter['prop_res']
                        #         set_op = utter['set_op']
                        #     elif count_ques_sub_type in [2,8]:
                        #         Qid = utter['Qid']
                        #         obj_par_1 = utter['obj_par_1']
                        #         obj_par_2 = utter['obj_par_2']
                        #         prop_res = utter['prop_res']
                        #         set_op = utter['set_op']
                        #     elif count_ques_sub_type in [3,4,5,6,7,9,10]:
                        #         obj_par = utter['obj_par']
                        #         sub_par_1 = utter['sub_par_1']
                        #         sub_par_2 = utter['sub_par_2']
                        #         prop_res = utter['prop_res']
                        #         qualifier_choice = utter['qualifier_choice']
                        #         set_op = utter['set_op']
                        #         if count_ques_sub_type in [4,6]:
                        #             N = utter['N']
                        #         elif count_ques_sub_type in [5,7,9,10]:
                        #             Z = utter['Z']
                        # else:
                        #     if count_ques_sub_type == 1:
                        #         Qid = utter['Qid']
                        #         Qid_2 = utter['Qid_2']
                        #         sub_par = utter['sub_par']
                        #         prop_res = utter['prop_res']
                        #         set_op = utter['set_op']
                        #     elif count_ques_sub_type in [2,8]:
                        #         Qid = utter['Qid']
                        #         sub_par_1 = utter['sub_par_1']
                        #         sub_par_2 = utter['sub_par_2']
                        #         prop_res = utter['prop_res']
                        #         set_op = utter['set_op']
                        #     elif count_ques_sub_type in [3,4,5,6,7,9,10]:
                        #         sub_par = utter['sub_par']
                        #         obj_par_1 = utter['obj_par_1']
                        #         obj_par_2 = utter['obj_par_2']
                        #         prop_res = utter['prop_res']
                        #         qualifier_choice = utter['qualifier_choice']
                        #         set_op = utter['set_op']
                        #         if count_ques_sub_type in [4,6]:
                        #             N = utter['N']
                        #         elif count_ques_sub_type in [5,7,9,10]:
                        #             Z = utter['Z']

                        if count_ques_type == 1: # sub-based
                            if count_ques_sub_type == 1: # basic form
                                Qid = utter['Qid']
                                Qid_2 = utter['Qid_2']
                                obj_par = utter['obj_par']
                                prop_res = utter['prop_res']
                                set_op = utter['set_op']

                                set_A = list(set(wikidata[Qid][prop_res]) & set(par_child_dict[obj_par]))
                                set_B = list(set(wikidata[Qid_2][prop_res]) & set(par_child_dict[obj_par]))

                                if set_op == 1:
                                    ans_list_full = list(set(set_A).intersection(set_B))
                                elif set_op == 2:
                                    ans_list_full = list(set(set_A).union(set_B))

                            elif count_ques_sub_type in [2, 8]:
                                Qid = utter['Qid']
                                obj_par_1 = utter['obj_par_1']
                                obj_par_2 = utter['obj_par_2']
                                prop_res = utter['prop_res']
                                set_op = utter['set_op']

                                set_A = list(set(wikidata[Qid][prop_res]) & set(par_child_dict[obj_par_1]))
                                set_B = list(set(wikidata[Qid][prop_res]) & set(par_child_dict[obj_par_2]))
                                ans_list_full = list(set(set_A).union(set_B))

                            elif count_ques_sub_type in [3,4,5,6,7,8,9,10]:
                                obj_par = utter['obj_par']
                                sub_par_1 = utter['sub_par_1']
                                sub_par_2 = utter['sub_par_2']
                                prop_res = utter['prop_res']
                                qualifier_choice = utter['qualifier_choice']
                                set_op = utter['set_op']

                                cand_obj_list = list(set([q for q in par_child_dict[obj_par] if q in reverse_dict and prop_res in reverse_dict[q]]))

                                cand_obj_list_score = {}
                                for obj in cand_obj_list:
                                    cand_obj_list_score[obj] = len([q for q in reverse_dict[obj][prop_res] if q in child_par_dict and child_par_dict[q] in [sub_par_1, sub_par_2]])

                                cand_obj_list_score_arr = np.asarray(cand_obj_list_score.values())

                                if count_ques_sub_type == 3:
                                    if qualifier_choice == 'min':
                                        ans_list_full = [x for x in cand_obj_list if cand_obj_list_score[x] == min(cand_obj_list_score.values())]
                                    elif qualifier_choice == 'max':
                                        ans_list_full = [x for x in cand_obj_list if cand_obj_list_score[x] == max(cand_obj_list_score.values())]

                                elif count_ques_sub_type in [4, 6]:
                                    N = utter['N']

                                    if qualifier_choice == 'atleast':
                                        ans_list_full = [x for x in cand_obj_list if cand_obj_list_score[x] >= N]
                                    elif qualifier_choice == 'atmost':
                                        ans_list_full = [x for x in cand_obj_list if cand_obj_list_score[x] <= N]
                                    elif qualifier_choice == 'exactly':
                                        ans_list_full = [x for x in cand_obj_list if cand_obj_list_score[x] == N]
                                    elif qualifier_choice == 'around' or qualifier_choice == 'approximately':
                                        ans_list_full = [x for x in cand_obj_list if cand_obj_list_score[x] > (N - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[x] < (N + np.std(cand_obj_list_score_arr))]

                                elif count_ques_sub_type in [5, 7, 9, 10]:
                                    Z = utter['Z']
                                    Z_score = cand_obj_list_score[Z]
                            
                                    if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                        ans_list_full = [x for x in cand_obj_list if cand_obj_list_score[x] > Z_score]
                                    elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                        ans_list_full = [x for x in cand_obj_list if cand_obj_list_score[x] < Z_score]
                                    elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                        ans_list_full = [x for x in cand_obj_list if cand_obj_list_score[x] > (Z_score - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[x] < (Z_score + np.std(cand_obj_list_score_arr))]

                        elif count_ques_type == 2: # obj-based
                            if count_ques_sub_type == 1: # basic form
                                Qid = utter['Qid']
                                Qid_2 = utter['Qid_2']
                                sub_par = utter['sub_par']
                                prop_res = utter['prop_res']
                                set_op = utter['set_op']

                                set_A = list(set(reverse_dict[Qid][prop_res]) & set(par_child_dict[sub_par]))
                                set_B = list(set(reverse_dict[Qid_2][prop_res]) & set(par_child_dict[sub_par]))

                                if set_op == 1:
                                    ans_list_full = list(set(set_A).intersection(set_B))
                                elif set_op == 2:
                                    ans_list_full = list(set(set_A).union(set_B))

                            elif count_ques_sub_type in [2, 8]:
                                Qid = utter['Qid']
                                sub_par_1 = utter['sub_par_1']
                                sub_par_2 = utter['sub_par_2']
                                prop_res = utter['prop_res']
                                set_op = utter['set_op']

                                set_A = list(set(reverse_dict[Qid][prop_res]) & set(par_child_dict[sub_par_1]))
                                set_B = list(set(reverse_dict[Qid][prop_res]) & set(par_child_dict[sub_par_2]))
                                ans_list_full = list(set(set_A).union(set_B))

                            elif count_ques_sub_type in [3,4,5,6,7,8,9,10]:
                                sub_par = utter['sub_par']
                                obj_par_1 = utter['obj_par_1']
                                obj_par_2 = utter['obj_par_2']
                                prop_res = utter['prop_res']
                                qualifier_choice = utter['qualifier_choice']
                                set_op = utter['set_op']

                                cand_sub_list = list(set([q for q in par_child_dict[sub_par] if q in wikidata and prop_res in wikidata[q]]))
                                cand_sub_list_score = {}
                                for sub in cand_sub_list:
                                    cand_sub_list_score[sub] = len([q for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q] in [obj_par_1, obj_par_2]])
                                    
                                cand_sub_list_score_arr = np.asarray(cand_sub_list_score.values())

                                if count_ques_sub_type == 3:
                                    if qualifier_choice == 'min':
                                        ans_list_full = [x for x in cand_sub_list if cand_sub_list_score[x]==min(cand_sub_list_score.values())]
                                    elif qualifier_choice == 'max':
                                        ans_list_full = [x for x in cand_sub_list if cand_sub_list_score[x]==max(cand_sub_list_score.values())]

                                elif count_ques_sub_type in [4, 6]:
                                    N = utter['N']
                                    if qualifier_choice == 'atleast':
                                        ans_list_full = [x for x in cand_sub_list if cand_sub_list_score[x] >= N]
                                    elif qualifier_choice == 'atmost':
                                        ans_list_full = [x for x in cand_sub_list if cand_sub_list_score[x] <= N]
                                    elif qualifier_choice == 'exactly':
                                        ans_list_full = [x for x in cand_sub_list if cand_sub_list_score[x] == N]
                                    elif qualifier_choice == 'around' or qualifier_choice == 'approximately':
                                        ans_list_full = [x for x in cand_sub_list if cand_sub_list_score[x] > (N - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (N + np.std(cand_sub_list_score_arr))]

                                elif count_ques_sub_type in [5, 7, 9, 10]:
                                    Z = utter['Z']
                                    Z_score = cand_sub_list_score[Z]
                            
                                    if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                        ans_list_full = [x for x in cand_sub_list if cand_sub_list_score[x] > Z_score]
                                    elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                        ans_list_full = [x for x in cand_sub_list if cand_sub_list_score[x] < Z_score]
                                    elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                        ans_list_full = [x for x in cand_sub_list if cand_sub_list_score[x] > (Z_score - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (Z_score + np.std(cand_sub_list_score_arr))]

                        try:
                            if 'Did you mean' in utter_list[utter_id+1]['utterance']:
                                if args.strict:
                                    assert set(ans_list_full) == set(utter_list[utter_id+3]['ans_list_full'])
                                else:
                                    assert set(utter_list[utter_id+3]['ans_list_full']).issubset(set(ans_list_full))
                            else:
                                if args.strict:
                                    assert set(ans_list_full) == set(utter_list[utter_id+1]['ans_list_full'])
                                else:
                                    assert set(utter_list[utter_id+1]['ans_list_full']).issubset(set(ans_list_full))
                            # print 'Validation successful for ques_type_id = %d, sub-type=%d, sub-sub-type=%d' % (ques_type_id, count_ques_type, count_ques_sub_type)
                        except:
                            print 'Error for ques_type_id = %d, sub-type=%d, sub-sub-type=%d' % (ques_type_id, count_ques_type, count_ques_sub_type)
                            print utter['utterance']
                            if 'Did you mean' in utter_list[utter_id+1]['utterance']:
                                print dialog_json_file
                                n_similar = len(set(ans_list_full) & set(utter_list[utter_id+3]['ans_list_full']))
                                print 'n_similar = %d, len(gold) = %d, len(existing) = %d' % (n_similar, len(set(ans_list_full)), len(set(utter_list[utter_id+3]['ans_list_full'])))
                                # print (set(ans_list_full) - set(utter_list[utter_id+3]['ans_list_full']))
                                # print (set(utter_list[utter_id+3]['ans_list_full']) - set(ans_list_full))
                            else:
                                print dialog_json_file
                                print utter_list[utter_id+1]['ans_list_full']
                                n_similar = len(set(ans_list_full) & set(utter_list[utter_id+1]['ans_list_full']))
                                print 'n_similar = %d, len(gold) = %d, len(existing) = %d' % (n_similar, len(set(ans_list_full)), len(set(utter_list[utter_id+1]['ans_list_full'])))
                                # print (set(ans_list_full) - set(utter_list[utter_id+1]['ans_list_full']))
                                # print (set(utter_list[utter_id+1]['ans_list_full']) - set(ans_list_full))

                ##########################################################################################

        except:
            logging.exception('Something aweful happened')

f1.close()
