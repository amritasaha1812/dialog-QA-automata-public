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

def get_new_Qid():
    Qid_init = random.choice([q for q in wikidata_fanout_dict_list[:1000000] if q.keys()[0] in child_par_dict]).keys()[0]
    return Qid_init

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def random_shuffle(l1):
    if len(l1) == 0:
        return list()
    else:
        random.shuffle(l1)
        return l1

def print_memory_profile():
    print 'Total memory usage: %d KB' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    for var in globals():
        print '%s : %d KB' % (var, sys.getsizeof(var))

def get_multi_pphrase(obj_list):
    if len(obj_list) == 1:
        return obj_list[0]
        
    obj_list_pphrase = ', '.join(obj_list[:(len(obj_list)-1)])
    obj_list_pphrase += ' and %s' % obj_list[-1]
    return obj_list_pphrase

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

def get_sub_ques_filt_tuples(Qid):
    filt_tuples = list()

    for pid in [p for p in wikidata[Qid] if p in prop_data.keys() and p in sub_90_map and p in sing_sub_annot and p in plu_sub_annot]:
        for q in [item for item in wikidata[Qid][pid] if item in child_par_dict]: 
            filt_tuples.append((pid,child_par_dict[q]))


    return filt_tuples

def get_obj_ques_filt_tuples(Qid):
    filt_tuples = list()
    if Qid not in reverse_dict:
        return list()

    for pid in [p for p in reverse_dict[Qid] if p in prop_data.keys() and p in obj_90_map and p in sing_obj_annot and p in plu_obj_annot]:
        for q in [item for item in reverse_dict[Qid][pid] if item in child_par_dict]:
            filt_tuples.append((pid,child_par_dict[q]))

    return filt_tuples

def sing2plural(par):
    '''
    ques: should be in template format with YYY or XXX intact
    '''
    return pattern.en.pluralize(par)
    
def sing_basic2indirect(ques,obj,child_par_dict,prop_Qid_par,prop_res,sing=True):
    '''
    For object based ques (Answer is the subject):
    object: If the object is a person, so he/she/him/her can be assigned, o/w 'that <obj_par>' can be assigned
    ques: should be in template format with YYY intact
    put sing = True in order to get singular form, sing = False for plural form
    '''
    if 'XXX' in ques:
        var = 'XXX'
    elif 'YYY' in ques:
        var = 'YYY'

    ques_tokenized = ques.split(' ')
    ques_result = ques_tokenized 
    if child_par_dict[obj] != 'Q215627': # if the parent of object is not a person/human
        yyy_idx = ques_result.index(var)
        ques_result.remove(var)
        if sing:
            ques_result.insert(yyy_idx,'that')
            if child_par_dict[obj] != prop_Qid_par and not is_par_rel_overlap(child_par_dict[obj], prop_res, ques):
                ques_result.insert(yyy_idx+1,child_par_dict_name_2[child_par_dict[obj]])
            else:
                ques_result.insert(yyy_idx+1,'one')
        else: # plural
            ques_result.insert(yyy_idx,'those')
            if child_par_dict[obj] != prop_Qid_par and not is_par_rel_overlap(child_par_dict[obj], prop_res, ques):
                ques_result.insert(yyy_idx+1,pattern.en.pluralize(child_par_dict_name_2[child_par_dict[obj]])) # use plural form of object parent
            else:
                ques_result.insert(yyy_idx+1,'ones')

    else: # object is instance of human/person (Q5)
        if 'by' in ques_tokenized or 'with' in ques_tokenized or 'as' in ques_tokenized: # as, by, with
            if sing:  
                if wikidata[obj]['P21'][0] == 'Q6581097': # gender property has value 'male'
                    ques_result[ques_result.index(var)] = 'him'
                elif wikidata[obj]['P21'][0] == 'Q6581072': # gender property has value 'female'
                    ques_result[ques_result.index(var)] = 'her'
                else: # gender property has value other than male or female (LGBT)
                    yyy_idx = ques_result.index(var)
                    ques_result.remove(var)
                    ques_result.insert(yyy_idx,'that')
                    ques_result.insert(yyy_idx+1,'person')
            else:
                ques_result[ques_result.index(var)] = 'them'
        else: # Name a SPP whose source of inspiration is YYY.
            if sing:
                yyy_idx = ques_result.index(var)
                ques_result.remove(var)
                ques_result.insert(yyy_idx,'that')
                ques_result.insert(yyy_idx+1,'person')
            else:
                yyy_idx = ques_result.index(var)
                ques_result.remove(var)
                ques_result.insert(yyy_idx,'those')
                ques_result.insert(yyy_idx+1,'persons')
                # ques_result[ques_result.index('is')] = 'are'
                # ques_result[ques_result.index('was')] = 'were'
                # ques_result[ques_result.index('has')] = 'have'
    return ' '.join(ques_result)

def sing_basic2plural_basic(ques,obj_list):
    '''
    Converts singular basic ques. to Plural basic question
    ques: template form
    takes as argument the object list 
    '''
    if 'XXX' in ques:
        var = 'XXX'
    elif 'YYY' in ques:
        var = 'YYY'

    obj_list_pphrase = get_multi_pphrase(obj_list)
    ques_result = ques.replace(var,obj_list_pphrase)
    # ques_result = ques_result.replace('is','are')
    # ques_result = ques_result.replace('was','were')
    # ques_result = ques_result.replace('has','have')

    return ques_result

def sing_basic2set_basic(ques,setA_list,setB_list,set_op_choice):
    '''
    converts singular basic to set-based basic question when only the subject/object is changed (predicate remains same)
    '''
    if 'XXX' in ques:
        var = 'XXX'
    elif 'YYY' in ques:
        var = 'YYY'

    setA_pphrase = ', '.join(setA_list)
    setB_pphrase = ', '.join(setB_list)

    if set_op_choice == 1: # union
        ques_result = ques.replace(var,'%s or %s' % (setA_pphrase,setB_pphrase))
    elif set_op_choice == 2: # intersection
        comb_set = setA_list
        comb_set.extend(setB_list)
        comb_set_pphrase = get_multi_pphrase(comb_set)
        ques_result = ques.replace(var,comb_set_pphrase)
    elif set_op_choice == 3: # difference
        ques_result = ques.replace(var,'%s but not %s' % (get_multi_pphrase(setA_list),get_multi_pphrase(setB_list)))
    return ques_result

def sing_basic2set_basic_2(ques_1,ques_2,setA_list,setB_list,set_op_choice):
    '''
    converts singular basic to set-based basic question when both the subject/object and predicate are changed
    ques_2: SPP or OPP should be intact in the question template
    '''
    if 'XXX' in ques_1:
        var = 'XXX'
    elif 'YYY' in ques_1:
        var = 'YYY'

    setA_pphrase = get_multi_pphrase(setA_list)
    setB_pphrase = get_multi_pphrase(setB_list)
    ques_2_tokenized = ques_2.split(' ')

    if set_op_choice == 1: # union
        ques_result = '%s or %s' % (ques_1.replace(var,setA_pphrase).replace(' ?',''),' '.join(ques_2_tokenized[2:]).replace(var,setB_pphrase))
    elif set_op_choice == 2: # intersection
        ques_result = '%s and %s' % (ques_1.replace(var,setA_pphrase).replace(' ?',''),' '.join(ques_2_tokenized[2:]).replace(var,setB_pphrase))
    elif set_op_choice == 3: # difference
        # ques_2_neg = negate_ques(ques_2)
        ques_2_neg_tokenized = ques_2.split(' ')
        ques_result = '%s and %s' % (ques_1.replace(var,setA_pphrase).replace(' ?',''),' '.join(ques_2_neg_tokenized[2:]).replace(var,setB_pphrase))
    return ques_result

def booleanise_ques(ques,sub):
    ques_tokenized = ques.split(' ')

    if ques_tokenized[1].lower() in ['spp','opp','spps','opps']:
        ques_result = ques_tokenized[3:]
    else: # handles the case of what, whom, who etc.
        ques_tokenized.insert(1,'')
        ques_result = ques_tokenized[3:]
    # print ques_tokenized
    
    verb_list = ['is','was','were','are']
    adj_poss = ['has','have','had']
    prep_list = ['in','at','to','of','have','for','through','by','on','with','into']

    if ques_tokenized[-2] not in prep_list and ques_tokenized[2] not in ['does','did']: # word before ? is not a preposition
        if ques_tokenized[2] not in verb_list and ques_tokenized[2] not in adj_poss and 'present' in tenses(ques_tokenized[2]):
            ques_result.insert(0,ques_tokenized[2])
            ques_result.insert(0,item_data[sub])
            ques_result.insert(0,'Does')
            ques_result[2] = lemma(ques_result[2])
        elif ques_tokenized[2] not in verb_list and ques_tokenized[2] not in adj_poss and 'past' in tenses(ques_tokenized[2]):
            ques_result.insert(0,ques_tokenized[2])
            ques_result.insert(0,item_data[sub])
            ques_result.insert(0,'Did')
            ques_result[2] = lemma(ques_result[2])
        elif ques_tokenized[2] in adj_poss:
            if ques_tokenized[3] == 'been':
                ques_result.insert(0,item_data[sub])
                ques_result.insert(0,ques_tokenized[2].title())
            else:
                ques_result.insert(0,'have')
                ques_result.insert(0,item_data[sub])
                if ques_tokenized[2] == 'has':
                    ques_result.insert(0,'Does')
                elif ques_tokenized[2] == 'have':
                    ques_result.insert(0,'Do')
                elif ques_tokenized[2] == 'had':
                    ques_result.insert(0,'Did')
        elif ques_tokenized[2] in verb_list:
            ques_result.insert(0,item_data[sub])
            ques_result.insert(0,ques_tokenized[2].title())
    else: # word before ? is a preposition
        ques_result.insert(0,ques_tokenized[2].title())
        ques_result.insert(len(ques_result)-1,item_data[sub]) # insert just before qmark

    return ' '.join(ques_result)

def booleanise_ques_custom(ques,sub):
    ques_tokenized = ques.split(' ')
    if ques_tokenized[1].lower() in ['spp','opp','spps','opps']:
        ques_result = ques_tokenized[3:]
    else: # handles the case of what, whom, who etc.
        ques_tokenized.insert(1,'')
        ques_result = ques_tokenized[3:]
    # print ques_tokenized
    
    verb_list = ['is','was','were','are']
    adj_poss = ['has','have','had']
    prep_list = ['in','at','to','of','have','for','through','by','on','with','into']

    if ques_tokenized[-2] not in prep_list and ques_tokenized[2] not in ['does','did']: # word before ? is not a preposition
        if ques_tokenized[2] not in verb_list and ques_tokenized[2] not in adj_poss and 'present' in tenses(ques_tokenized[2]):
            ques_result.insert(0,ques_tokenized[2])
            ques_result.insert(0,child_par_dict_name_2[child_par_dict[sub]])
            ques_result.insert(0,'that')
            ques_result.insert(0,'Does')
            ques_result[2] = lemma(ques_result[2])
        elif ques_tokenized[2] not in verb_list and ques_tokenized[2] not in adj_poss and 'past' in tenses(ques_tokenized[2]):
            ques_result.insert(0,ques_tokenized[2])
            ques_result.insert(0,child_par_dict_name_2[child_par_dict[sub]])
            ques_result.insert(0,'that')
            ques_result.insert(0,'Did')
            ques_result[2] = lemma(ques_result[2])
        elif ques_tokenized[2] in adj_poss:
            if ques_tokenized[3] == 'been':
                ques_result.insert(0,child_par_dict_name_2[child_par_dict[sub]])
                ques_result.insert(0,'that')
                ques_result.insert(0,ques_tokenized[2].title())
            else:
                ques_result.insert(0,'have')
                ques_result.insert(0,child_par_dict_name_2[child_par_dict[sub]])
                ques_result.insert(0,'that')
                if ques_tokenized[2] == 'has':
                    ques_result.insert(0,'Does')
                elif ques_tokenized[2] == 'have':
                    ques_result.insert(0,'Do')
                elif ques_tokenized[2] == 'had':
                    ques_result.insert(0,'Did')
        elif ques_tokenized[2] in verb_list:
            ques_result.insert(0,child_par_dict_name_2[child_par_dict[sub]])
            ques_result.insert(0,'that')
            ques_result.insert(0,ques_tokenized[2].title())
    else: # word before ? is a preposition
        ques_result.insert(0,ques_tokenized[2].title())
        ques_result.insert(len(ques_result)-1,sub) # insert just before qmark

    return ' '.join(ques_result)

def sing_basic2count_based(ques, qualifier, count_ques_type=1):
    ques_tokenized = ques.split(' ')

    if 'XXX' in ques:
        var_1 = 'XXX'
    elif 'YYY' in ques:
        var_1 = 'YYY'

    if ques_tokenized[0].lower() == 'which' and ques_tokenized[1].lower() in ['spp','opp','spps','opps']:
        if 'OPPS' in ques:
            var_2 = 'OPPS'
        elif 'SPPS' in ques:
            var_2 = 'SPPS'
    else: # handles the case of what, whom, who etc
        if count_ques_type not in [2,3,4]: # 2,3,4 will go with 'Wh*' version (as annotated by new annotators)
            if var_1 == 'XXX':
                var_2 = 'OPPS'
            elif var_1 == 'YYY':
                var_2 = 'SPPS'
            ques_tokenized.pop(0)
            if ques_tokenized[0].lower() in ['spp','opp','spps','opps']:
                ques_tokenized.pop(0) # handle the case of 'What SPP ...'

            ques_tokenized.insert(0, var_2)
            ques_tokenized.insert(0, 'Which')
            ques = ' '.join(ques_tokenized)

    
    dict_1 = {'XXX':'SPPS', 'YYY':'OPPS'}

    if count_ques_type == 1:
        return ('How many %s ' % var_2) + ' '.join(ques_tokenized[2:])

    if count_ques_type == 2:
        return ques.replace(var_1, '%s number of %s' % (qualifier, dict_1[var_1]))

    if count_ques_type == 3:
        return ques.replace(var_1, '%s N %s' % (qualifier,dict_1[var_1]))

    if count_ques_type == 4:
        if qualifier in ['around the same', 'approximately the same']:
            return ques.replace(var_1, '%s number of %s' % (qualifier, dict_1[var_1])).replace('?','') + 'as Z ?'
        else:
            return ques.replace(var_1, '%s number of %s' % (qualifier, dict_1[var_1])).replace('?','') + 'than Z ?'

    if count_ques_type == 5:
        return ques.replace(var_1, '%s N %s' % (qualifier, dict_1[var_1])).replace(('Which %s' % var_2),'How many %s' % var_2)

    if count_ques_type == 6:
        if qualifier in ['around the same', 'approximately the same']:
            return ques.replace(var_1, '%s number of %s' % (qualifier, dict_1[var_1])).replace('?','').replace(('Which %s' % var_2),'How many %s' % var_2) + 'as Z ?'
        else:
            return ques.replace(var_1, '%s number of %s' % (qualifier, dict_1[var_1])).replace('?','').replace(('Which %s' % var_2),'How many %s' % var_2) + 'than Z ?'

def sing_basic2count_set_based(ques, qualifier, set_op_id=1, count_ques_type=1):
    ques_tokenized = ques.split(' ')

    if 'XXX' in ques:
        var_1 = 'XXX'
    elif 'YYY' in ques:
        var_1 = 'YYY'
    
    if ques_tokenized[0].lower() == 'which' and ques_tokenized[1].lower() in ['spp','opp','spps','opps']:
        if 'OPPS' in ques:
            var_2 = 'OPP'
        elif 'SPPS' in ques:
            var_2 = 'SPP'
    else: # handles the case of what, whom, who etc
        if count_ques_type not in [3,4,5]: # 3,4,5 will go with 'Wh*' version (as annotated by new annotators)
            if var_1 == 'XXX':
                var_2 = 'OPP'
            elif var_1 == 'YYY':
                var_2 = 'SPP'
            ques_tokenized.pop(0)
            if ques_tokenized[0].lower() in ['spp','opp','spps','opps']:
                ques_tokenized.pop(0)

            ques_tokenized.insert(0, '%sS' % var_2)
            ques_tokenized.insert(0, 'Which')
            ques = ' '.join(ques_tokenized)    

    dict_1 = {'XXX':'SPP', 'YYY':'OPP'}
    set_op_dict = {1:'and', 2:'or'}

    if count_ques_type == 1:
        return (('How many %sS ' % var_2) + ' '.join(ques_tokenized[2:])).replace(var_1,'%s_1 %s %s_2'%(var_1, set_op_dict[set_op_id], var_1))

    if count_ques_type == 2:
        return (('How many %s_1s %s %s_2s ' % (var_2, set_op_dict[set_op_id], var_2)) + ' '.join(ques_tokenized[2:]))

    if count_ques_type == 3:
        return ques.replace(var_1, '%s number of %s_1s %s %s_2s' % (qualifier, dict_1[var_1],set_op_dict[set_op_id],dict_1[var_1]))

    if count_ques_type == 4:
        return ques.replace(var_1, '%s N %s_1s %s %s_2s' % (qualifier, dict_1[var_1],set_op_dict[set_op_id],dict_1[var_1]))

    if count_ques_type == 5:
        if qualifier in ['around the same', 'approximately the same']:
            return ques.replace(var_1, '%s number of %s_1s %s %s_2s' % (qualifier, dict_1[var_1],set_op_dict[set_op_id],dict_1[var_1])).replace('?','') + 'as Z ?'
        else:
            return ques.replace(var_1, '%s number of %s_1s %s %s_2s' % (qualifier, dict_1[var_1],set_op_dict[set_op_id],dict_1[var_1])).replace('?','') + 'than Z ?'

    if count_ques_type == 6:
        return ques.replace(var_1, '%s N %s_1s %s %s_2s' % (qualifier, dict_1[var_1],set_op_dict[set_op_id],dict_1[var_1])).replace(('Which %sS' % var_2),'How many %sS' % var_2)

    if count_ques_type == 7:
        if qualifier in ['around the same', 'approximately the same']:
            return ques.replace(var_1, '%s number of %s_1s %s %s_2s' % (qualifier, dict_1[var_1],set_op_dict[set_op_id],dict_1[var_1])).replace('?','').replace(('Which %sS' % var_2),'How many %sS' % var_2) + 'as Z ?'
        else:
            return ques.replace(var_1, '%s number of %s_1s %s %s_2s' % (qualifier, dict_1[var_1],set_op_dict[set_op_id],dict_1[var_1])).replace('?','').replace(('Which %sS' % var_2),'How many %sS' % var_2) + 'than Z ?'
# ********************************************************************************************************* 
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


def rel_fw_fanout(qid):
    return (len([x for x in wikidata[qid] if len(wikidata[qid][x])>0]) if qid in wikidata else 0)

def rel_bw_fanout(qid):
    return (len([x for x in reverse_dict[qid] if len(reverse_dict[qid][x])>0]) if qid in reverse_dict else 0)

def get_rel_dist(rel_c):
    rel_prob_dict = {}
    for pid in prop_data:
        if rel_c[pid] > 0:
            rel_prob_dict[pid] = 1.0/(rel_c[pid]+1)
        else:
            rel_prob_dict[pid] = 1.0
    norm = sum(rel_prob_dict.values())
    for pid in prop_data:
        rel_prob_dict[pid] = rel_prob_dict[pid]*1.0/norm

    return rel_prob_dict

child_par_dict_key_set = set(child_par_dict.keys())
reverse_dict_key_set = set(reverse_dict.keys())

def random_sample_upto_n(input_list, n):
    if n > len(input_list):
        return input_list
    else:
        return random.sample(input_list, n)

def get_one_hop_ent_list(ent_list):
    result = []
    for q in [q1 for q1 in ent_list if q1 in wikidata]:
        for p in wikidata[q]:
            result.extend([x for x in wikidata[q][p] if x in child_par_dict])

    return result

def get_new_set_based_ques(utter_list):
    prev_ques_failed = True
    run_id = 0
    n_max_runs = 30
    is_inc = 0

    while run_id < n_max_runs and prev_ques_failed:
        run_id += 1 # increment the run_id
        # print 'run_id = %d' % run_id
        prev_ques_failed = False

        # if 'entities' in dialog_list[-1] and len(utter_list[utter_id-1]['entities'])>0:
        #     Qid = random.choice(utter_list[utter_id-1]['entities'])
        # elif 'entities' in dialog_list[-2] and len(utter_list[utter_id-2]['entities'])>0:
        #     Qid = random.choice(utter_list[utter_id-2]['entities'])
        # else:
        #     Qid = get_new_Qid()
        is_sub = np.random.choice([0, 1])
        

        ent_list = []
        for i in range(len(utter_list)):
            if 'entities' in utter_list[i]:
                ent_list.extend(utter_list[i]['entities'])

        ent_list = ent_list + get_one_hop_ent_list(ent_list)
        ent_list = list(set(ent_list))

        flag = False
        for idx,Qid in enumerate(ent_list):
            prev_ques_failed = False
            # print 'idx = %d' % idx
            if flag:
                break
            if Qid not in reverse_dict:
                is_sub = 1

            set_op_dict = {1:'OR',2:'AND',3:'DIFF'}
            set_op_choice = np.random.choice(set_op_dict.keys(),p=[0.2, 0.4, 0.4])
            # print 'set-op= %d' % set_op_choice
            try:
                if is_sub:
                    pq_tuple = get_sub_ques_filt_tuples(Qid)

                    if len(pq_tuple) > args.ps_tuple_thresh: # randomly sample args.ps_tuple_thresh # of entries from list if greater than threshold
                        pq_tuple = random.sample(pq_tuple,args.ps_tuple_thresh)

                    # pq_tuple_fanout = [sum([wikidata_fanout_dict[qid] for qid in wikidata[Qid][p] if qid in child_par_dict and child_par_dict[qid]==q]) for (p,q) in pq_tuple]
                    
                    # if sum(pq_tuple_fanout)==0: #blacklist the combination of Qid, pid, filt_dict[Qid][pid]
                    #     prev_ques_failed = True
                    #     continue

                    # pq_tuple_fanout_norm = [x*1.0/sum(pq_tuple_fanout) for x in pq_tuple_fanout]
                    # pq_tuple_choice = pq_tuple[np.random.choice(len(pq_tuple), p=pq_tuple_fanout_norm)]
                    if len(pq_tuple)==0:
                        prev_ques_failed = True
                        # print 'FLAG 1'
                        continue
                    pq_tuple_choice = random.choice(pq_tuple)
                    prop_res = pq_tuple_choice[0]
                    prop_Qid_par = pq_tuple_choice[1]
                    ans_list_A = list(set(wikidata[Qid][prop_res]) & child_par_dict_key_set & set(par_child_dict[prop_Qid_par]))
                else:
                    pq_tuple = get_obj_ques_filt_tuples(Qid) # filt_dict corr. to object based ques.

                    if len(pq_tuple) > args.ps_tuple_thresh: # randomly sample args.ps_tuple_thresh # of entries from list if greater than threshold
                        pq_tuple = random.sample(pq_tuple,args.ps_tuple_thresh)

                    # pq_tuple_fanout = [sum([wikidata_fanout_dict[qid] for qid in reverse_dict[Qid][p] if qid in child_par_dict and child_par_dict[qid]==q]) for (p,q) in pq_tuple]
                    # if sum(pq_tuple_fanout)==0:
                    #     prev_ques_failed = True
                    #     continue

                    # pq_tuple_fanout_norm = [x*1.0/sum(pq_tuple_fanout) for x in pq_tuple_fanout]
                    # pq_tuple_choice = pq_tuple[np.random.choice(len(pq_tuple), p=pq_tuple_fanout_norm)]
                    if len(pq_tuple)==0:
                        prev_ques_failed = True
                        # print 'FLAG 2'
                        continue
                    pq_tuple_choice = random.choice(pq_tuple)
                    prop_res = pq_tuple_choice[0]
                    prop_Qid_par = pq_tuple_choice[1]
                    ans_list_A = list(set(reverse_dict[Qid][prop_res]) & child_par_dict_key_set & set(par_child_dict[prop_Qid_par]))

                set_sub_oper = 1 # no NOT based ques

                if is_sub: # prev. secondary ques. is subject-based
                    obj_par = prop_Qid_par
                    # valid_obj = [q for q in reverse_dict if q in child_par_dict and child_par_dict[q]==obj_par]
                    # print obj_par
                    valid_obj = reverse_dict_key_set & child_par_dict_key_set & set(random_sample_upto_n(par_child_dict[obj_par], 100))
                    if len(valid_obj) > args.set_obj_thresh:
                        valid_obj = list(random.sample(valid_obj,args.set_obj_thresh))

                    ps_tuple = [(p,s) for q in valid_obj for p in reverse_dict[q] for s in reverse_dict[q][p] if s in wikidata and p in wikidata[s] and p in sub_90_map and prop_Qid_par in sub_90_map[p]]
                    ps_tuple = [(p,s) for (p,s) in ps_tuple if s!=Qid]

                    # try:
                    #     assert prop_res in [x[0] for x in ps_tuple]
                    # except:
                    #     prev_ques_failed = True
                    #     continue

                    if len(ps_tuple) > args.ps_tuple_thresh: # randomly sample args.ps_tuple_thresh # of entries from list if greater than threshold
                        ps_tuple = random.sample(ps_tuple,args.ps_tuple_thresh)

                    Qid_1 = Qid # save Qid of first operand of set operation
                    prop_res_1 = prop_res # save pid of first operand of set operation

                    ps_tuple_ans_len = []

                    for tup in ps_tuple:
                        pid = tup[0]
                        qid = tup[1]
                        set_B = [q for q in wikidata[qid][pid] if q in wikidata and q in child_par_dict and child_par_dict[q]==prop_Qid_par]

                        if set_op_choice == 1:
                            ans_list = list(set(ans_list_A).union(set_B)) # UNION
                        elif set_op_choice == 2:
                            ans_list = list(set(ans_list_A).intersection(set_B)) # INTERSECTION
                        elif set_op_choice == 3:
                            ans_list = list(set(ans_list_A).difference(set_B)) # DIFFERENCE

                        ps_tuple_ans_len.append(len(ans_list))

                    ps_tuple_ans_len_sum = sum(ps_tuple_ans_len)
                    if ps_tuple_ans_len_sum == 0:
                        prev_ques_failed = True
                        # print 'FLAG 3'
                        continue

                    ps_tuple_ans_len_norm = [x*1.0/ps_tuple_ans_len_sum for x in ps_tuple_ans_len] # prob. distribution of number of answers of set operation

                    ps_tuple_choice = ps_tuple[np.random.choice(len(ps_tuple), p = ps_tuple_ans_len_norm)]
                    prop_res = ps_tuple_choice[0]
                    Qid = ps_tuple_choice[1] # new subject

                    if prop_res == prop_res_1: # pid remains unchanged
                        if set_sub_oper == 1:
                            ques_1 = random.choice(plu_sub_annot_wh[prop_res_1])
                        else:
                            ques_1 = random.choice(neg_plu_sub_annot_wh[prop_res_1])                      

                        ques = sing_basic2set_basic(ques_1,[item_data[Qid_1]],[item_data[Qid]],set_op_choice)
                        if not is_par_rel_overlap(prop_Qid_par, prop_res, ques):
                            ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                        else:
                            if 'Which OPPS' in ques:
                                if prop_Qid_par != 'Q215627':
                                    ques = ques.replace('Which OPPS','What')
                                else:
                                    ques = ques.replace('Which OPPS','Who')
                            else:
                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))

                    else: # pid is different
                        if set_sub_oper == 1:
                            ques_1 = random.choice(plu_sub_annot_wh[prop_res_1])
                            if set_op_choice != 3:
                                ques_2 = random.choice(plu_sub_annot_wh[prop_res])
                            else:
                                ques_2 = random.choice(neg_plu_sub_annot_wh[prop_res])
                            set_op_choice_dem = set_op_choice
                        else:
                            ques_1 = random.choice(neg_plu_sub_annot_wh[prop_res_1])
                            ques_2 = random.choice(neg_plu_sub_annot_wh[prop_res])

                            if set_op_choice == 1:
                                set_op_choice_dem = 2
                            elif set_op_choice == 2:
                                set_op_choice_dem = 1

                        ques = sing_basic2set_basic_2(ques_1,ques_2,[item_data[Qid_1]],[item_data[Qid]],set_op_choice_dem)
                        if not is_par_rel_overlap(prop_Qid_par, prop_res, ques):
                            ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                        else:
                            if 'Which OPPS' in ques:
                                if prop_Qid_par != 'Q215627':
                                    ques = ques.replace('Which OPPS','What')
                                else:
                                    ques = ques.replace('Which OPPS','Who')
                            else:
                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))

                    ans_list_B = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                    

                else: # prev. secondary ques. is object-based
                    sub_par = prop_Qid_par
                    valid_sub = par_child_dict[sub_par]
                    if len(valid_sub) > args.set_obj_thresh:
                        valid_sub = random.sample(valid_sub,args.set_obj_thresh)

                    ps_tuple = [(p,s) for q in valid_sub for p in wikidata[q] for s in wikidata[q][p] if s in reverse_dict and p in reverse_dict[s] and p in obj_90_map and prop_Qid_par in obj_90_map[p] and p in plu_obj_annot_wh]
                    ps_tuple = [(p,s) for (p,s) in ps_tuple if s!=Qid and len(reverse_dict[s][p])<50]
                    # try:
                    #     assert prop_res in [x[0] for x in ps_tuple]
                    # except:
                    #     prev_ques_failed = True
                    #     print 'FLAG 4'
                    #     continue

                    if len(ps_tuple) > args.ps_tuple_thresh: # randomly sample args.ps_tuple_thresh # of entries from list if greater than threshold
                        ps_tuple = random.sample(ps_tuple,args.ps_tuple_thresh)

                    
                    Qid_1 = Qid # save Qid of first operand of set operation
                    prop_res_1 = prop_res # save pid of first operand of set operation

                    ps_tuple_ans_len = []

                    for tup in ps_tuple:
                        pid = tup[0]
                        qid = tup[1]
                        set_B = [q for q in reverse_dict[qid][pid] if q in wikidata and q in child_par_dict and child_par_dict[q]==prop_Qid_par]

                        if set_op_choice == 1:
                            ans_list = list(set(ans_list_A).union(set_B)) # UNION
                        elif set_op_choice == 2:
                            ans_list = list(set(ans_list_A).intersection(set_B)) # INTERSECTION
                        elif set_op_choice == 3:
                            ans_list = list(set(ans_list_A).difference(set_B)) # DIFFERENCE

                        ps_tuple_ans_len.append(len(ans_list))

                    ps_tuple_ans_len_sum = sum(ps_tuple_ans_len)
                    if ps_tuple_ans_len_sum == 0:
                        prev_ques_failed = True
                        # print 'FLAG 6'
                        continue

                    ps_tuple_ans_len_norm = [x*1.0/ps_tuple_ans_len_sum for x in ps_tuple_ans_len] # prob. distribution of number of answers of set operation

                    ps_tuple_choice = ps_tuple[np.random.choice(len(ps_tuple), p = ps_tuple_ans_len_norm)]
                    prop_res = ps_tuple_choice[0]
                    Qid = ps_tuple_choice[1] # new subject

                    if prop_res == prop_res_1: # pid remains unchanged
                        if set_sub_oper == 1:
                            ques_1 = random.choice(plu_obj_annot_wh[prop_res_1])
                        else:
                            ques_1 = random.choice(neg_plu_obj_annot_wh[prop_res_1])

                        ques = sing_basic2set_basic(ques_1,[item_data[Qid_1]],[item_data[Qid]],set_op_choice)
                        if not is_par_rel_overlap(prop_Qid_par, prop_res, ques):
                            ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                        else:
                            if 'Which SPPS' in ques:
                                if prop_Qid_par != 'Q215627':
                                    ques = ques.replace('Which SPPS','What')
                                else:
                                    ques = ques.replace('Which SPPS','Who')
                            else:
                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))

                    else: # pid is different
                        if set_sub_oper == 1:
                            ques_1 = random.choice(plu_obj_annot_wh[prop_res_1])
                            if set_op_choice != 3:
                                ques_2 = random.choice(plu_obj_annot_wh[prop_res])
                            else:
                                ques_2 = random.choice(neg_plu_obj_annot_wh[prop_res])
                            set_op_choice_dem = set_op_choice
                        else:
                            ques_1 = random.choice(neg_plu_obj_annot_wh[prop_res_1])
                            ques_2 = random.choice(neg_plu_obj_annot_wh[prop_res])

                            if set_op_choice == 1:
                                set_op_choice_dem = 2 # only affect the choice for the rule not the global var set_op_choice
                            elif set_op_choice == 2:
                                set_op_choice_dem = 1

                        ques = sing_basic2set_basic_2(ques_1,ques_2,[item_data[Qid_1]],[item_data[Qid]],set_op_choice_dem)
                        if not is_par_rel_overlap(prop_Qid_par, prop_res, ques):
                            ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                        else:
                            if 'Which SPPS' in ques:
                                if prop_Qid_par != 'Q215627':
                                    ques = ques.replace('Which SPPS','What')
                                else:
                                    ques = ques.replace('Which SPPS','Who')
                            else:
                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))

                    ans_list_B = [q for q in reverse_dict[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                    

                ans_list = [] # Result of set operation

                if set_op_choice == 1:
                    ans_list = list(set(ans_list_A).union(ans_list_B)) # UNION
                elif set_op_choice == 2:
                    ans_list = list(set(ans_list_A).intersection(ans_list_B)) # INTERSECTION
                elif set_op_choice == 3:
                    ans_list = list(set(ans_list_A).difference(ans_list_B)) # DIFFERENCE

                if set_op_choice == 3 and len(set(ans_list_A).intersection(ans_list_B))==0:
                    prev_ques_failed = True
                    # print 'FLAG 5'
                    continue
            except:
                prev_ques_failed = True
            # print prev_ques_failed
            if not prev_ques_failed:
                flag = True
                break

    if prev_ques_failed:
        print 'No set-based ques formed'
        return None, None
    # print 'run_id = %d' % run_id

    if is_sub:
        tpl_set = [(Qid_1,prop_res_1,q) for q in ans_list] + [(Qid,prop_res,q) for q in ans_list]
    else:
        tpl_set = [(q,prop_res_1,Qid_1) for q in ans_list] + [(q,prop_res,Qid) for q in ans_list]

    ans_list = list(set(ans_list))
    ans_list_full = ans_list

    ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # ques type_id of next question (Secondary)

    if is_sub:
        if set_op_choice == 1:
            tpl_regex = 'OR(%s, %s)' % ('(%s,%s,%s)' % (Qid_1,prop_res_1,'c(%s)' % prop_Qid_par), '(%s,%s,%s)' % (Qid,prop_res,'c(%s)' % prop_Qid_par))
        elif set_op_choice == 2:
            tpl_regex = 'AND(%s, %s)' % ('(%s,%s,%s)' % (Qid_1,prop_res_1,'c(%s)' % prop_Qid_par), '(%s,%s,%s)' % (Qid,prop_res,'c(%s)' % prop_Qid_par))
        elif set_op_choice == 3:
            tpl_regex = 'AND(%s, NOT(%s))' % ('(%s,%s,%s)' % (Qid_1,prop_res_1,'c(%s)' % prop_Qid_par), '(%s,%s,%s)' % (Qid,prop_res,'c(%s)' % prop_Qid_par))
    else:
        if set_op_choice == 1:
            tpl_regex = 'OR(%s, %s)' % ('(%s,%s,%s)' % ('c(%s)' % prop_Qid_par, prop_res_1, Qid_1), '(%s,%s,%s)' % ('c(%s)' % prop_Qid_par, prop_res, Qid))
        elif set_op_choice == 2:
            tpl_regex = 'AND(%s, %s)' % ('(%s,%s,%s)' % ('c(%s)' % prop_Qid_par, prop_res_1, Qid_1), '(%s,%s,%s)' % ('c(%s)' % prop_Qid_par, prop_res, Qid))
        elif set_op_choice == 3:
            tpl_regex = 'AND(%s, NOT(%s))' % ('(%s,%s,%s)' % ('c(%s)' % prop_Qid_par, prop_res_1, Qid_1), '(%s,%s,%s)' % ('c(%s)' % prop_Qid_par, prop_res, Qid))
    tpl_regex = [tpl_regex]

    dict1 = {}
    dict1['speaker'] = 'USER'
    dict1['utterance'] = ques
    dict1['ques_type_id'] = 4
    # dict1['last_ques_type_id_save'] = last_ques_type_id_save
    dict1['set_op_choice'] = set_op_choice
    dict1['set_sub_oper'] = set_sub_oper
    dict1['entities'] = [Qid, Qid_1]
    dict1['relations'] = list(set([prop_res, prop_res_1]))

    #***********************************************************
    dict1['is_inc'] = is_inc
    dict1['is_sub'] = is_sub
    dict1['is_mult_pid'] = (True if prop_res != prop_res_1 else False)
    dict1['prop_res'] = prop_res
    dict1['prop_res_1'] = prop_res_1
    dict1['Qid'] = Qid
    dict1['Qid_1'] = Qid_1
    dict1['prop_Qid_par'] = prop_Qid_par

    if set_op_choice == 1:
        if not dict1['is_mult_pid']:
            if not is_inc:
                dict1['description'] = 'Logical|Union|Single_Relation'
            else:
                dict1['description'] = 'Logical|Union|Single_Relation|Incomplete'
        else:
            dict1['description'] = 'Logical|Union|Multiple_Relation'
    elif set_op_choice == 2:
        if not dict1['is_mult_pid']:
            if not is_inc:
                dict1['description'] = 'Logical|Intersection|Single_Relation'
            else:
                dict1['description'] = 'Logical|Intersection|Single_Relation|Incomplete'
        else:
            dict1['description'] = 'Logical|Intersection|Multiple_Relation'
    elif set_op_choice == 3:
        if not dict1['is_mult_pid']:
            if not is_inc:
                dict1['description'] = 'Logical|Difference|Single_Relation'
            else:
                dict1['description'] = 'Logical|Difference|Single_Relation|Incomplete'
        else:
            dict1['description'] = 'Logical|Difference|Multiple_Relation'
    #***********************************************************
    dict1['signature'] = get_dict_signature(dict1.copy())

    dict_ques = dict1.copy()

    if len(ans_list) > 0:
        if len(ans_list) > args.set_ques_ans_thresh:
            ans_list = random.sample(ans_list,args.set_ques_ans_thresh)
            ans = 'Some of them are ' + ', '.join([item_data[q] for q in ans_list])
        else:
            ans = ', '.join([item_data[q] for q in ans_list])
        # print 'Ans: %s\n' % ans
        dict1 = {}
        dict1['speaker'] = 'SYSTEM'
        dict1['utterance'] = ans
        dict1['ans_list_full'] = ans_list_full
        dict1['entities'] = ans_list[:]
        dict1['active_set'] = tpl_regex[:]
        dict1['signature'] = get_dict_signature(dict1.copy())
        
    else:
        # print 'Ans: None'
        dict1 = {}
        dict1['speaker'] = 'SYSTEM'
        dict1['utterance'] = 'None'
        dict1['entities'] = ans_list[:]
        dict1['active_set'] = tpl_regex[:]
        dict1['ans_list_full'] = ans_list_full
        dict1['signature'] = get_dict_signature(dict1.copy())

    dict_ans = dict1.copy()
    return dict_ques, dict_ans

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

def convert_indir_to_direct(utter):
    assert is_indirect(utter)

    if 'ques_type_id' in utter and utter['ques_type_id']==2 and 'sec_ques_sub_type' in utter and utter['sec_ques_sub_type']==2: # Secondary question
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
        return new_utter_dict
        #*****************************************************************
        
    elif 'ques_type_id' in utter and utter['ques_type_id']==2 and 'sec_ques_sub_type' in utter and utter['sec_ques_sub_type']==3:
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
            sub_list = utter['sub_list']

            is_pphrase_ov = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in plu_sub_annot_wh[prop_res]]
            if False in is_pphrase_ov:
                ques = sing_basic2plural_basic(random.choice([plu_sub_annot_wh[prop_res][i] for i in range(len(plu_sub_annot_wh[prop_res])) if is_pphrase_ov[i] == False]),[item_data[q] for q in sub_list]) # to be modified: use appropiate dict
                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
            else:
                ques = sing_basic2plural_basic(random.choice(plu_sub_annot_wh[prop_res]),[item_data[q] for q in sub_list]) # to be modified: use appropiate dict
                if 'Which OPPS' in ques:
                    if prop_Qid_par != 'Q215627':
                        ques = ques.replace('Which OPPS','What')
                    else:
                        ques = ques.replace('Which OPPS','Who')
                else:
                    ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))

        elif sec_ques_type == 2: # Object based ques.
            Qid = utter['Qid']
            prop_res = utter['prop_res']
            prop_Qid_par = utter['prop_Qid_par']
            sub_list = utter['sub_list']

            is_pphrase_ov = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in plu_obj_annot_wh[prop_res]]
            if False in is_pphrase_ov:
                ques = sing_basic2plural_basic(random.choice([plu_obj_annot_wh[prop_res][i] for i in range(len(plu_obj_annot_wh[prop_res])) if is_pphrase_ov[i] == False]),[item_data[q] for q in sub_list]) # to be modified: use appropiate dict
                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
            else:
                ques = sing_basic2plural_basic(random.choice(plu_obj_annot_wh[prop_res]),[item_data[q] for q in sub_list]) # to be modified: use appropiate dict
                if 'Which SPPS' in ques:
                    if prop_Qid_par != 'Q215627':
                        ques = ques.replace('Which SPPS','What')
                    else:
                        ques = ques.replace('Which SPPS','Who')
                else:
                    ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
        #*****************************************************************
        new_utter_dict['utterance'] = ques
        new_utter_dict['sec_ques_sub_type'] = 4
        new_utter_dict['description'] = 'Simple Question|Mult. Entity'
        return new_utter_dict

    elif 'ques_type_id' in utter and utter['ques_type_id'] == 5 and 'bool_ques_type' in utter and utter['bool_ques_type'] in [2,3,5]: # Boolean (secondary) question (change if prev ques was a set-ques)
        bool_ques_type = utter['bool_ques_type']
        
        new_utter_dict = {}
        for field in utter:
            if field not in ['utterance','signature']:
                new_utter_dict[field] = utter[field]

        if bool_ques_type == 5:
            obj = utter['obj']
            obj2 = utter['obj2']
            Qid = utter['Qid']
            prop_res = utter['prop_res']
            prop_Qid_par = utter['prop_Qid_par']

            ques = booleanise_ques(random.choice(sing_obj_annot_wh[prop_res]),Qid)
            ques = ques.replace('YYY',get_multi_pphrase([item_data[obj], item_data[obj2]]))
            new_utter_dict['bool_ques_type'] = 4
            new_utter_dict['description'] = 'Verification|3 entities, all direct, 2 are query entities'
        elif bool_ques_type == 2:
            obj = utter['obj']
            Qid = utter['Qid']
            prop_res = utter['prop_res']
            prop_Qid_par = utter['prop_Qid_par']

            ques = booleanise_ques(random.choice(sing_sub_annot_wh[prop_res]),obj)
            ques = ques.replace('XXX',item_data[Qid])

            new_utter_dict['bool_ques_type'] = 1
            new_utter_dict['description'] = 'Verification|2 entities, both direct'
        elif bool_ques_type == 3:
            Qid = utter['Qid']
            prop_res = utter['prop_res']
            prop_Qid_par = utter['prop_Qid_par']
            sub = utter['sub']

            ques = random.choice(sing_obj_annot_wh[prop_res])
            ques = booleanise_ques(ques, sub)
            ques = ques.replace('YYY',item_data[Qid])

            new_utter_dict['bool_ques_type'] = 1
            new_utter_dict['description'] = 'Verification|2 entities, both direct'

        #*****************************************************************
        new_utter_dict['utterance'] = ques
        
        new_utter_dict['signature'] = get_dict_signature(new_utter_dict.copy())
        return new_utter_dict

    elif 'ques_type_id' in utter and utter['ques_type_id'] == 7 and 'is_incomplete' in utter and utter['is_incomplete'] == 0 and 'count_ques_sub_type' in utter and utter['count_ques_sub_type'] in [7,8,9]: # count-based question
        count_ques_type = utter['count_ques_type']
        count_ques_sub_type = utter['count_ques_sub_type']

        if count_ques_sub_type == 7:
            Qid = utter['Qid']
            prop_Qid_par = utter['prop_Qid_par']
            prop_res = utter['prop_res']
        elif count_ques_sub_type in [8,9]:
            obj_par = utter['obj_par']
            sub_par = utter['sub_par']
            prop_res = utter['prop_res']
            qualifier_choice = utter['qualifier_choice']
            Z = utter['Z']

        new_utter_dict = {}
        for field in utter:
            if field not in ['utterance','signature']:
                new_utter_dict[field] = utter[field]

        if count_ques_type == 1: # sub-based
            if count_ques_sub_type == 7: # basic form
                ques = random.choice(plu_sub_annot_wh[prop_res])
                ques = sing_basic2count_based(ques, '', 1)        
                ques = ques.replace('XXX',item_data[Qid])
                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                new_utter_dict['count_ques_sub_type'] = 1
                new_utter_dict['description'] = 'Quantitative|Count|Single entity type'
            else:
                ques = random.choice(plu_sub_annot_wh[prop_res])
                if count_ques_sub_type == 8:
                    ques = sing_basic2count_based(ques, qualifier_choice, 4)
                else:
                    ques = sing_basic2count_based(ques, qualifier_choice, 6)

                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))

                ques = ques.replace('Z', item_data[Z])
                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))

                if count_ques_sub_type == 8:
                    new_utter_dict['count_ques_sub_type'] = 4
                    new_utter_dict['description'] = 'Comparative|More/Less|Single entity type'
                else:
                    new_utter_dict['count_ques_sub_type'] = 6
                    new_utter_dict['description'] = 'Comparative|Count over More/Less|Single entity type'

        elif count_ques_type == 2: # obj-based
            if count_ques_sub_type == 7: # basic form         
                ques = random.choice(plu_obj_annot_wh[prop_res])
                ques = sing_basic2count_based(ques, '', 1)        
                ques = ques.replace('YYY',item_data[Qid])
                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                new_utter_dict['count_ques_sub_type'] = 1
                new_utter_dict['description'] = 'Quantitative|Count|Single entity type'
                
            else:
                ques = random.choice(plu_obj_annot_wh[prop_res])
                if count_ques_sub_type == 8:
                    ques = sing_basic2count_based(ques, qualifier_choice, 4)
                else:
                    ques = sing_basic2count_based(ques, qualifier_choice, 6)

                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))

                ques = ques.replace('Z', item_data[Z])
                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))

                if count_ques_sub_type == 8:
                    new_utter_dict['count_ques_sub_type'] = 4
                    new_utter_dict['description'] = 'Comparative|More/Less|Single entity type'
                else:
                    new_utter_dict['count_ques_sub_type'] = 6
                    new_utter_dict['description'] = 'Comparative|Count over More/Less|Single entity type'

        #*****************************************************************
        new_utter_dict['utterance'] = ques
        new_utter_dict['signature'] = get_dict_signature(new_utter_dict.copy())
        return new_utter_dict
        #*****************************************************************

    elif 'ques_type_id' in utter and utter['ques_type_id'] == 8 and 'is_incomplete' in utter and utter['is_incomplete'] == 0 and 'count_ques_sub_type' in utter and utter['count_ques_sub_type'] in [8,9,10]: # count-set-based question
        count_ques_type = utter['count_ques_type']
        count_ques_sub_type = utter['count_ques_sub_type']

        if count_ques_type == 1:
            if count_ques_sub_type == 8:
                Qid = utter['Qid']
                obj_par_1 = utter['obj_par_1']
                obj_par_2 = utter['obj_par_2']
                prop_res = utter['prop_res']
                set_op = utter['set_op']
            elif count_ques_sub_type in [9,10]:
                obj_par = utter['obj_par']
                sub_par_1 = utter['sub_par_1']
                sub_par_2 = utter['sub_par_2']
                prop_res = utter['prop_res']
                qualifier_choice = utter['qualifier_choice']
                set_op = utter['set_op']
                Z = utter['Z']
        else:
            if count_ques_sub_type == 8:
                Qid = utter['Qid']
                sub_par_1 = utter['sub_par_1']
                sub_par_2 = utter['sub_par_2']
                prop_res = utter['prop_res']
                set_op = utter['set_op']
            elif count_ques_sub_type in [9,10]:
                sub_par = utter['sub_par']
                obj_par_1 = utter['obj_par_1']
                obj_par_2 = utter['obj_par_2']
                prop_res = utter['prop_res']
                qualifier_choice = utter['qualifier_choice']
                set_op = utter['set_op']
                Z = utter['Z']

        new_utter_dict = {}
        for field in utter:
            if field not in ['utterance','signature']:
                new_utter_dict[field] = utter[field]

        if count_ques_type == 1: # sub-based
            if count_ques_sub_type == 8:
                ques = random.choice(plu_sub_annot_wh[prop_res])
                ques = sing_basic2count_set_based(ques, '', set_op, 2)        
                ques = ques.replace('XXX',item_data[Qid])
                ques = ques.replace('OPP_1s',sing2plural(child_par_dict_name_2[obj_par_1]))
                ques = ques.replace('OPP_2s',sing2plural(child_par_dict_name_2[obj_par_2]))
                new_utter_dict['count_ques_sub_type'] = 2
                new_utter_dict['description'] = 'Quantitative|Count|Logical operators'
            else:
                ques = random.choice(plu_sub_annot_wh[prop_res])
                if count_ques_sub_type == 9:
                    ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, 5)
                    new_utter_dict['count_ques_sub_type'] = 5
                    new_utter_dict['description'] = 'Comparative|More/Less|Mult. entity type'
                else:
                    ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, 7)
                    new_utter_dict['count_ques_sub_type'] = 7
                    new_utter_dict['description'] = 'Comparative|Count over More/Less|Mult. entity type'

                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))
                ques = ques.replace('SPP_1s',sing2plural(child_par_dict_name_2[sub_par_1]))
                ques = ques.replace('SPP_2s',sing2plural(child_par_dict_name_2[sub_par_2]))
                ques = ques.replace('Z', item_data[Z])
                    

        elif count_ques_type == 2: # obj-based
            if count_ques_sub_type == 8:
                ques = random.choice(plu_obj_annot_wh[prop_res])
                ques = sing_basic2count_set_based(ques, '', set_op, 2)        
                ques = ques.replace('YYY',item_data[Qid])
                ques = ques.replace('SPP_1s',sing2plural(child_par_dict_name_2[sub_par_1]))
                ques = ques.replace('SPP_2s',sing2plural(child_par_dict_name_2[sub_par_2]))   
                new_utter_dict['count_ques_sub_type'] = 2
                new_utter_dict['description'] = 'Quantitative|Count|Logical operators'         
            else:
                ques = random.choice(plu_obj_annot_wh[prop_res])
                if count_ques_sub_type == 9:
                    ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, 5)
                    new_utter_dict['count_ques_sub_type'] = 5
                    new_utter_dict['description'] = 'Comparative|More/Less|Mult. entity type'
                else:
                    ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, 7)
                    new_utter_dict['count_ques_sub_type'] = 7
                    new_utter_dict['description'] = 'Comparative|Count over More/Less|Mult. entity type'

                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))
                ques = ques.replace('OPP_1s',sing2plural(child_par_dict_name_2[obj_par_1]))
                ques = ques.replace('OPP_2s',sing2plural(child_par_dict_name_2[obj_par_2]))

                ques = ques.replace('Z', item_data[Z])

        #*****************************************************************
        new_utter_dict['utterance'] = ques
        new_utter_dict['signature'] = get_dict_signature(new_utter_dict.copy())
        return new_utter_dict

    return None # should not happen ideally


# stop_word_list = set(stopwords.words('english'))
stop_word_list = set([u'all', u'just', u'being', u'over', u'both', u'through', u'yourselves', u'its', u'before', u'o', u'hadn', u'herself', u'll', u'had', u'should', u'to', u'only', u'won', u'under', u'ours', u'has', u'do', u'them', u'his', u'very', u'they', u'not', u'during', u'now', u'him', u'nor', u'd', u'did', u'didn', u'this', u'she', u'each', u'further', u'where', u'few', u'because', u'doing', u'some', u'hasn', u'are', u'our', u'ourselves', u'out', u'what', u'for', u'while', u're', u'does', u'above', u'between', u'mustn', u't', u'be', u'we', u'who', u'were', u'here', u'shouldn', u'hers', u'by', u'on', u'about', u'couldn', u'of', u'against', u's', u'isn', u'or', u'own', u'into', u'yourself', u'down', u'mightn', u'wasn', u'your', u'from', u'her', u'their', u'aren', u'there', u'been', u'whom', u'too', u'wouldn', u'themselves', u'weren', u'was', u'until', u'more', u'himself', u'that', u'but', u'don', u'with', u'than', u'those', u'he', u'me', u'myself', u'ma', u'these', u'up', u'will', u'below', u'ain', u'can', u'theirs', u'my', u'and', u've', u'then', u'is', u'am', u'it', u'doesn', u'an', u'as', u'itself', u'at', u'have', u'in', u'any', u'if', u'again', u'no', u'when', u'same', u'how', u'other', u'which', u'you', u'shan', u'needn', u'haven', u'after', u'most', u'such', u'why', u'a', u'off', u'i', u'm', u'yours', u'so', u'y', u'the', u'having', u'once'])
stop_par_list = ['Q21025364', 'Q19361238', 'Q21027609', 'Q20088085', 'Q15184295', 'Q11266439', 'Q17362920', 'Q19798645', 'Q26884324', 'Q14204246', 'Q13406463', 'Q14827288', 'Q4167410', 'Q21484471', 'Q17442446', 'Q4167836', 'Q19478619', 'Q24017414', 'Q19361238', 'Q24027526', 'Q15831596', 'Q24027474', 'Q23958852', 'Q24017465', 'Q24027515', 'Q1924819']

inf_eng = inflect.engine()
# child_par_dict_val = child_par_dict.values()

# HYPERPARAMETERS

parser = argparse.ArgumentParser(description='Hyper-parameter settings')
parser.add_argument('--input_dir', dest='input_dir', type=str, help='directory in which dialogs are to be verified', required=True)
parser.add_argument('--output_dir',dest='output_dir', type=str, help = 'name of dir (wrt cwd) where dialogue dirs are created',required=True) # should be required
parser.add_argument('--low',dest='low',type=int, help='lower index of QA')
parser.add_argument('--high',dest='high',type=int, help='higher index of QA')

args = parser.parse_args()
print(args)
# args.input_dir = '/scratch/vardaan/final_dataset_filt_untrim/train/'
# args.output_dir = '/home/vardaan/projects/rpp-bengioy/vardaan/train/'
# args.low = 0
# args.high = 1

args.p_inc_set = 0.3
args.set_obj_thresh=1000
args.ps_tuple_thresh=30
args.set_ques_ans_thresh=10


if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

f1 = open(os.path.join(args.output_dir,'recons_log.txt'),'w')

count = 0

var_list = ['N','Qid','Qid_1','Qid_2','prop_res','prop_res_1','prop_Qid_par', 'sub_par', 'sub_par_1', 'sub_par_2', 'obj_par', 'obj_par_1', 'obj_par_2', 'Z','obj','obj2','qualifier_choice','set_op']

for dir_name in [('QA_%d' % i) for i in range(args.low, args.high) if os.path.isdir(os.path.join(args.input_dir, ('QA_%d' % i)))]:
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

                if 'ques_type_id' not in utter: # ignore answer utterances
                    if 'The answer count is' in utter['utterance']:
                        pass
                    elif 'No, show only a few of them' in utter['utterance']:
                        pass
                    else:
                        dialog_list.append(utter)

                else:
                    for var in var_list:
                        if var in globals():
                            del var
                            
                    ques_type_id = utter['ques_type_id']

                    if len(dialog_list)>=2 and ques_type_id==2 and 'ques_type_id' in dialog_list[-2] and dialog_list[-2]['ques_type_id'] == 4 and 'sec_ques_sub_type' in utter and utter['sec_ques_sub_type']==2: # Secondary question
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
                        dialog_list.append(new_utter_dict)
                        print 'flag-2'
                        if (utter_id+1) < len(utter_list) and 'utterance' in utter_list[utter_id+1] and 'Did you mean' in utter_list[utter_id+1]['utterance']:
                            utter_id += 2
                        #*****************************************************************
                        
                    elif len(dialog_list)>=2 and ques_type_id==2 and 'ques_type_id' in dialog_list[-2] and dialog_list[-2]['ques_type_id'] == 4 and 'sec_ques_sub_type' in utter and utter['sec_ques_sub_type']==3:
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
                            sub_list = utter['sub_list']

                            is_pphrase_ov = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in plu_sub_annot_wh[prop_res]]
                            if False in is_pphrase_ov:
                                ques = sing_basic2plural_basic(random.choice([plu_sub_annot_wh[prop_res][i] for i in range(len(plu_sub_annot_wh[prop_res])) if is_pphrase_ov[i] == False]),[item_data[q] for q in sub_list]) # to be modified: use appropiate dict
                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                            else:
                                ques = sing_basic2plural_basic(random.choice(plu_sub_annot_wh[prop_res]),[item_data[q] for q in sub_list]) # to be modified: use appropiate dict
                                if 'Which OPPS' in ques:
                                    if prop_Qid_par != 'Q215627':
                                        ques = ques.replace('Which OPPS','What')
                                    else:
                                        ques = ques.replace('Which OPPS','Who')
                                else:
                                    ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))

                        elif sec_ques_type == 2: # Object based ques.
                            Qid = utter['Qid']
                            prop_res = utter['prop_res']
                            prop_Qid_par = utter['prop_Qid_par']
                            sub_list = utter['sub_list']

                            is_pphrase_ov = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in plu_obj_annot_wh[prop_res]]
                            if False in is_pphrase_ov:
                                ques = sing_basic2plural_basic(random.choice([plu_obj_annot_wh[prop_res][i] for i in range(len(plu_obj_annot_wh[prop_res])) if is_pphrase_ov[i] == False]),[item_data[q] for q in sub_list]) # to be modified: use appropiate dict
                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                            else:
                                ques = sing_basic2plural_basic(random.choice(plu_obj_annot_wh[prop_res]),[item_data[q] for q in sub_list]) # to be modified: use appropiate dict
                                if 'Which SPPS' in ques:
                                    if prop_Qid_par != 'Q215627':
                                        ques = ques.replace('Which SPPS','What')
                                    else:
                                        ques = ques.replace('Which SPPS','Who')
                                else:
                                    ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                        #*****************************************************************
                        new_utter_dict['utterance'] = ques
                        new_utter_dict['sec_ques_sub_type'] = 4
                        new_utter_dict['description'] = 'Simple Question|Mult. Entity'
                        dialog_list.append(new_utter_dict)
                        #*****************************************************************


                    elif ques_type_id == 4 and utter['is_inc']==0: # Set based questioning
                        new_utter_ques, new_utter_ans = get_new_set_based_ques(utter_list)
                        if new_utter_ques is not None:
                            dialog_list.append(new_utter_ques)
                            dialog_list.append(new_utter_ans)
                        else:
                            pass

                        if 'The answer count is' in utter_list[utter_id+1]['utterance']:
                            utter_id += 3 # compensate for answer utterance, 2 middle utterances
                        else:
                            utter_id += 1 # compensate for answer utterance (answer already appended)
                        #*****************************************************************
                        # V IMP: handle the case of indirect ques following

                        utter_id += 1 # move to the next ques.

                        flag = True # flag indicates whether a non-convertible indirect ques. has been encountered
                        while utter_id < len(utter_list):
                            if is_indirect(utter_list[utter_id]):
                                new_ques_utter = convert_indir_to_direct(utter_list[utter_id])

                                if new_ques_utter is not None and flag:
                                    dialog_list.append(new_ques_utter)
                                else:
                                    flag = False
                                    
                                if (utter_id+1)<len(utter_list) and 'Did you mean' in utter_list[utter_id+1]['utterance']:
                                    utter_id += 3
                                else:
                                    utter_id += 1

                                # Now the pointer is at answer utterance
                                if flag:
                                    dialog_list.append(utter_list[utter_id])

                                utter_id += 1 # moev to the next ques.
                            else:
                                break # because we reached a direct ques.
                        #*****************************************************************
                        #************
                        utter_id -= 1 # move to the answer pointer (as utter_id += 1 occurs in end also)
                        #************

                    elif ques_type_id == 4 and utter['is_inc']==1: # remove the set-based ques NOT preceded by sec. ques
                        if len(dialog_list)>=2 and 'ques_type_id' in dialog_list[-2] and dialog_list[-2]['ques_type_id'] != 2:
                            new_utter_ques, new_utter_ans = get_new_set_based_ques(utter_list)
                            if new_utter_ques is not None:
                                dialog_list.append(new_utter_ques)
                                dialog_list.append(new_utter_ans)
                            else:
                                pass
                            if 'The answer count is' in utter_list[utter_id+1]['utterance']:
                                utter_id += 3 # compensate for answer utterance, 2 middle utterances
                            else:
                                utter_id += 1 # compensate for answer utterance (answer already appended)
                            #*****************************************************************
                            # V IMP: handle the case of indirect ques following
                            utter_id += 1 # move to the next ques.

                            flag = True # flag indicates whether a non-convertible indirect ques. has been encountered
                            while utter_id < len(utter_list):
                                if is_indirect(utter_list[utter_id]):
                                    new_ques_utter = convert_indir_to_direct(utter_list[utter_id])

                                    if new_ques_utter is not None and flag:
                                        dialog_list.append(new_ques_utter)
                                    else:
                                        flag = False
                                        
                                    if (utter_id+1)<len(utter_list) and 'Did you mean' in utter_list[utter_id+1]['utterance']:
                                        utter_id += 3
                                    else:
                                        utter_id += 1

                                    # Now the pointer is at answer utterance
                                    if flag:
                                        dialog_list.append(utter_list[utter_id])

                                    utter_id += 1 # moev to the next ques.
                                else:
                                    break # because we reached a direct ques.
                            #*****************************************************************
                            #************
                            utter_id -= 1 # move to the answer pointer (as utter_id += 1 occurs in end also)
                            #************
                        else:
                            dialog_list.append(utter) # keep the set-incomplete ques unchanged (answer will be appended later)

                            # re-compute the ans. of incomplete set-based ques.
                            is_inc = utter['is_inc']
                            is_sub = utter['is_sub']
                            is_mult_pid = utter['is_mult_pid']
                            prop_res = utter['prop_res']
                            prop_res_1 = utter['prop_res_1']
                            Qid = utter['Qid']
                            Qid_1 = utter['Qid_1']
                            prop_Qid_par = utter['prop_Qid_par']
                            set_op_choice = utter['set_op_choice']

                            #*****************************************************************
                            utter_id += 1 # move pointer to answer utterance
                            if 'The answer count is' in utter_list[utter_id]['utterance']:
                                utter_id += 2 # skip clar and its response
                            #*****************************************************************

                            new_ans_dict = {}
                            if 'active_set' in utter_list[utter_id]:
                                new_ans_dict['active_set'] = utter_list[utter_id]['active_set']

                            try:
                                ans_list_A = list(set(wikidata[Qid_1][prop_res_1]) & child_par_dict_key_set & set(par_child_dict[prop_Qid_par]))
                            except:
                                ans_list_A = []
                            try:
                                ans_list_B = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                            except:
                                ans_list_B = []

                            if set_op_choice == 1:
                                ans_list = list(set(ans_list_A).union(ans_list_B)) # UNION
                            elif set_op_choice == 2:
                                ans_list = list(set(ans_list_A).intersection(ans_list_B)) # INTERSECTION
                            elif set_op_choice == 3:
                                ans_list = list(set(ans_list_A).difference(ans_list_B)) # DIFFERENCE

                            ans_list = list(set(ans_list))
                            ans_list_full = ans_list

                            if len(ans_list) > 0:
                                if len(ans_list) > args.set_ques_ans_thresh:
                                    ans_list = random.sample(ans_list,args.set_ques_ans_thresh)
                                    ans = 'Some of them are ' + ', '.join([item_data[q] for q in ans_list])
                                else:
                                    ans = ', '.join([item_data[q] for q in ans_list])

                                new_ans_dict['speaker'] = 'SYSTEM'
                                new_ans_dict['utterance'] = ans
                                new_ans_dict['ans_list_full'] = ans_list_full
                                new_ans_dict['entities'] = ans_list[:]
                                new_ans_dict['signature'] = get_dict_signature(new_ans_dict.copy())
                            else:
                                new_ans_dict['speaker'] = 'SYSTEM'
                                new_ans_dict['utterance'] = 'None'
                                new_ans_dict['entities'] = ans_list[:]
                                new_ans_dict['ans_list_full'] = ans_list_full
                                new_ans_dict['signature'] = get_dict_signature(new_ans_dict.copy())
                            dialog_list.append(new_ans_dict)

                    elif len(dialog_list)>=2 and ques_type_id == 5 and 'ques_type_id' in dialog_list[-2] and dialog_list[-2]['ques_type_id'] == 4 and 'bool_ques_type' in utter and utter['bool_ques_type'] in [2,3,5]: # Boolean (secondary) question (change if prev ques was a set-ques)
                        bool_ques_type = utter['bool_ques_type']
                        
                        new_utter_dict = {}
                        for field in utter:
                            if field not in ['utterance','signature']:
                                new_utter_dict[field] = utter[field]

                        if bool_ques_type == 5:
                            obj = utter['obj']
                            obj2 = utter['obj2']
                            Qid = utter['Qid']
                            prop_res = utter['prop_res']
                            prop_Qid_par = utter['prop_Qid_par']

                            ques = booleanise_ques(random.choice(sing_obj_annot_wh[prop_res]),Qid)
                            ques = ques.replace('YYY',get_multi_pphrase([item_data[obj], item_data[obj2]]))
                            new_utter_dict['bool_ques_type'] = 4
                            new_utter_dict['description'] = 'Verification|3 entities, all direct, 2 are query entities'
                        elif bool_ques_type == 2:
                            obj = utter['obj']
                            Qid = utter['Qid']
                            prop_res = utter['prop_res']
                            prop_Qid_par = utter['prop_Qid_par']

                            ques = booleanise_ques(random.choice(sing_sub_annot_wh[prop_res]),obj)
                            ques = ques.replace('XXX',item_data[Qid])

                            new_utter_dict['bool_ques_type'] = 1
                            new_utter_dict['description'] = 'Verification|2 entities, both direct'
                        elif bool_ques_type == 3:
                            Qid = utter['Qid']
                            prop_res = utter['prop_res']
                            prop_Qid_par = utter['prop_Qid_par']
                            sub = utter['sub']

                            ques = random.choice(sing_obj_annot_wh[prop_res])
                            ques = booleanise_ques(ques, sub)
                            ques = ques.replace('YYY',item_data[Qid])

                            new_utter_dict['bool_ques_type'] = 1
                            new_utter_dict['description'] = 'Verification|2 entities, both direct'

                        #*****************************************************************
                        new_utter_dict['utterance'] = ques
                        
                        new_utter_dict['signature'] = get_dict_signature(new_utter_dict.copy())
                        dialog_list.append(new_utter_dict)
                        print 'flag-5'
                        #*****************************************************************

                    elif len(dialog_list)>=2 and ques_type_id == 5 and 'ques_type_id' in dialog_list[-2] and dialog_list[-2]['ques_type_id'] == 4 and 'bool_ques_type' in utter and utter['bool_ques_type']==6:
                        utter_id += 2 # compensate for ignoring the answer utterance

                        flag = True # flag indicates whether a non-convertible indirect ques. has been encountered
                        while utter_id < len(utter_list):
                            if is_indirect(utter_list[utter_id]):
                                new_ques_utter = convert_indir_to_direct(utter_list[utter_id])

                                if new_ques_utter is not None and flag:
                                    dialog_list.append(new_ques_utter)
                                else:
                                    flag = False

                                if (utter_id+1)<len(utter_list) and 'Did you mean' in utter_list[utter_id+1]['utterance']:
                                    utter_id += 3
                                else:
                                    utter_id += 1

                                # Now the pointer is at answer utterance
                                if flag:
                                    dialog_list.append(utter_list[utter_id])

                                utter_id += 1 # moev to the next ques.
                            else:
                                break # because we reached a direct ques.

                        #************
                        utter_id -= 1 # move to the answer pointer (as utter_id += 1 occurs in end also)
                        #************

                    elif len(dialog_list)>=2 and ques_type_id == 7 and 'ques_type_id' in dialog_list[-2] and dialog_list[-2]['ques_type_id'] == 4 and 'is_incomplete' in utter and utter['is_incomplete'] == 0 and 'count_ques_sub_type' in utter and utter['count_ques_sub_type'] in [7,8,9]: # count-based question
                        count_ques_type = utter['count_ques_type']
                        count_ques_sub_type = utter['count_ques_sub_type']

                        if count_ques_sub_type == 7:
                            Qid = utter['Qid']
                            prop_Qid_par = utter['prop_Qid_par']
                            prop_res = utter['prop_res']
                        elif count_ques_sub_type in [8,9]:
                            obj_par = utter['obj_par']
                            sub_par = utter['sub_par']
                            prop_res = utter['prop_res']
                            qualifier_choice = utter['qualifier_choice']
                            Z = utter['Z']

                        new_utter_dict = {}
                        for field in utter:
                            if field not in ['utterance','signature']:
                                new_utter_dict[field] = utter[field]

                        if count_ques_type == 1: # sub-based
                            if count_ques_sub_type == 7: # basic form
                                ques = random.choice(plu_sub_annot_wh[prop_res])
                                ques = sing_basic2count_based(ques, '', 1)        
                                ques = ques.replace('XXX',item_data[Qid])
                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                                new_utter_dict['count_ques_sub_type'] = 1
                                new_utter_dict['description'] = 'Quantitative|Count|Single entity type'
                            else:
                                ques = random.choice(plu_sub_annot_wh[prop_res])
                                if count_ques_sub_type == 8:
                                    ques = sing_basic2count_based(ques, qualifier_choice, 4)
                                else:
                                    ques = sing_basic2count_based(ques, qualifier_choice, 6)

                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))

                                ques = ques.replace('Z', item_data[Z])
                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))

                                if count_ques_sub_type == 8:
                                    new_utter_dict['count_ques_sub_type'] = 4
                                    new_utter_dict['description'] = 'Comparative|More/Less|Single entity type'
                                else:
                                    new_utter_dict['count_ques_sub_type'] = 6
                                    new_utter_dict['description'] = 'Comparative|Count over More/Less|Single entity type'

                        elif count_ques_type == 2: # obj-based
                            if count_ques_sub_type == 7: # basic form         
                                ques = random.choice(plu_obj_annot_wh[prop_res])
                                ques = sing_basic2count_based(ques, '', 1)        
                                ques = ques.replace('YYY',item_data[Qid])
                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                                new_utter_dict['count_ques_sub_type'] = 1
                                new_utter_dict['description'] = 'Quantitative|Count|Single entity type'
                                
                            else:
                                ques = random.choice(plu_obj_annot_wh[prop_res])
                                if count_ques_sub_type == 8:
                                    ques = sing_basic2count_based(ques, qualifier_choice, 4)
                                else:
                                    ques = sing_basic2count_based(ques, qualifier_choice, 6)

                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))

                                ques = ques.replace('Z', item_data[Z])
                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))

                                if count_ques_sub_type == 8:
                                    new_utter_dict['count_ques_sub_type'] = 4
                                    new_utter_dict['description'] = 'Comparative|More/Less|Single entity type'
                                else:
                                    new_utter_dict['count_ques_sub_type'] = 6
                                    new_utter_dict['description'] = 'Comparative|Count over More/Less|Single entity type'

                        #*****************************************************************
                        new_utter_dict['utterance'] = ques
                        new_utter_dict['signature'] = get_dict_signature(new_utter_dict.copy())
                        dialog_list.append(new_utter_dict)
                        print 'flag-7'
                        if (utter_id+1) < len(utter_list) and 'utterance' in utter_list[utter_id+1] and 'Did you mean' in utter_list[utter_id+1]['utterance']:
                            utter_id += 2
                        #*****************************************************************

                    elif len(dialog_list)>=2 and ques_type_id == 8 and 'ques_type_id' in dialog_list[-2] and dialog_list[-2]['ques_type_id'] == 4 and 'is_incomplete' in utter and utter['is_incomplete'] == 0 and 'count_ques_sub_type' in utter and utter['count_ques_sub_type'] in [8,9,10]: # count-set-based question
                        count_ques_type = utter['count_ques_type']
                        count_ques_sub_type = utter['count_ques_sub_type']

                        if count_ques_type == 1:
                            if count_ques_sub_type == 8:
                                Qid = utter['Qid']
                                obj_par_1 = utter['obj_par_1']
                                obj_par_2 = utter['obj_par_2']
                                prop_res = utter['prop_res']
                                set_op = utter['set_op']
                            elif count_ques_sub_type in [9,10]:
                                obj_par = utter['obj_par']
                                sub_par_1 = utter['sub_par_1']
                                sub_par_2 = utter['sub_par_2']
                                prop_res = utter['prop_res']
                                qualifier_choice = utter['qualifier_choice']
                                set_op = utter['set_op']
                                Z = utter['Z']
                        else:
                            if count_ques_sub_type == 8:
                                Qid = utter['Qid']
                                sub_par_1 = utter['sub_par_1']
                                sub_par_2 = utter['sub_par_2']
                                prop_res = utter['prop_res']
                                set_op = utter['set_op']
                            elif count_ques_sub_type in [9,10]:
                                sub_par = utter['sub_par']
                                obj_par_1 = utter['obj_par_1']
                                obj_par_2 = utter['obj_par_2']
                                prop_res = utter['prop_res']
                                qualifier_choice = utter['qualifier_choice']
                                set_op = utter['set_op']
                                Z = utter['Z']

                        new_utter_dict = {}
                        for field in utter:
                            if field not in ['utterance','signature']:
                                new_utter_dict[field] = utter[field]

                        if count_ques_type == 1: # sub-based
                            if count_ques_sub_type == 8:
                                ques = random.choice(plu_sub_annot_wh[prop_res])
                                ques = sing_basic2count_set_based(ques, '', set_op, 2)        
                                ques = ques.replace('XXX',item_data[Qid])
                                ques = ques.replace('OPP_1s',sing2plural(child_par_dict_name_2[obj_par_1]))
                                ques = ques.replace('OPP_2s',sing2plural(child_par_dict_name_2[obj_par_2]))
                                new_utter_dict['count_ques_sub_type'] = 2
                                new_utter_dict['description'] = 'Quantitative|Count|Logical operators'
                            else:
                                ques = random.choice(plu_sub_annot_wh[prop_res])
                                if count_ques_sub_type == 9:
                                    ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, 5)
                                    new_utter_dict['count_ques_sub_type'] = 5
                                    new_utter_dict['description'] = 'Comparative|More/Less|Mult. entity type'
                                else:
                                    ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, 7)
                                    new_utter_dict['count_ques_sub_type'] = 7
                                    new_utter_dict['description'] = 'Comparative|Count over More/Less|Mult. entity type'

                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))
                                ques = ques.replace('SPP_1s',sing2plural(child_par_dict_name_2[sub_par_1]))
                                ques = ques.replace('SPP_2s',sing2plural(child_par_dict_name_2[sub_par_2]))
                                ques = ques.replace('Z', item_data[Z])
                                    

                        elif count_ques_type == 2: # obj-based
                            if count_ques_sub_type == 8:
                                ques = random.choice(plu_obj_annot_wh[prop_res])
                                ques = sing_basic2count_set_based(ques, '', set_op, 2)        
                                ques = ques.replace('YYY',item_data[Qid])
                                ques = ques.replace('SPP_1s',sing2plural(child_par_dict_name_2[sub_par_1]))
                                ques = ques.replace('SPP_2s',sing2plural(child_par_dict_name_2[sub_par_2]))   
                                new_utter_dict['count_ques_sub_type'] = 2
                                new_utter_dict['description'] = 'Quantitative|Count|Logical operators'         
                            else:
                                ques = random.choice(plu_obj_annot_wh[prop_res])
                                if count_ques_sub_type == 9:
                                    ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, 5)
                                    new_utter_dict['count_ques_sub_type'] = 5
                                    new_utter_dict['description'] = 'Comparative|More/Less|Mult. entity type'
                                else:
                                    ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, 7)
                                    new_utter_dict['count_ques_sub_type'] = 7
                                    new_utter_dict['description'] = 'Comparative|Count over More/Less|Mult. entity type'

                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))
                                ques = ques.replace('OPP_1s',sing2plural(child_par_dict_name_2[obj_par_1]))
                                ques = ques.replace('OPP_2s',sing2plural(child_par_dict_name_2[obj_par_2]))

                                ques = ques.replace('Z', item_data[Z])

                        #*****************************************************************
                        new_utter_dict['utterance'] = ques
                        new_utter_dict['signature'] = get_dict_signature(new_utter_dict.copy())
                        dialog_list.append(new_utter_dict)
                        print 'flag-8'
                        if (utter_id+1) < len(utter_list) and 'utterance' in utter_list[utter_id+1] and 'Did you mean' in utter_list[utter_id+1]['utterance']:
                            utter_id += 2
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
