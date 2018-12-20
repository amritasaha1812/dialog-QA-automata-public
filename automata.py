#!/home/vardaan/anaconda2/bin/python
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
# from nltk.corpus import stopwords
import nltk
# from nltk import word_tokenize
import timeit
import time
import copy
sys.path.append(os.getcwd())

# stop_word_list = set(stopwords.words('english'))
stop_word_list = set([u'all', u'just', u'being', u'over', u'both', u'through', u'yourselves', u'its', u'before', u'o', u'hadn', u'herself', u'll', u'had', u'should', u'to', u'only', u'won', u'under', u'ours', u'has', u'do', u'them', u'his', u'very', u'they', u'not', u'during', u'now', u'him', u'nor', u'd', u'did', u'didn', u'this', u'she', u'each', u'further', u'where', u'few', u'because', u'doing', u'some', u'hasn', u'are', u'our', u'ourselves', u'out', u'what', u'for', u'while', u're', u'does', u'above', u'between', u'mustn', u't', u'be', u'we', u'who', u'were', u'here', u'shouldn', u'hers', u'by', u'on', u'about', u'couldn', u'of', u'against', u's', u'isn', u'or', u'own', u'into', u'yourself', u'down', u'mightn', u'wasn', u'your', u'from', u'her', u'their', u'aren', u'there', u'been', u'whom', u'too', u'wouldn', u'themselves', u'weren', u'was', u'until', u'more', u'himself', u'that', u'but', u'don', u'with', u'than', u'those', u'he', u'me', u'myself', u'ma', u'these', u'up', u'will', u'below', u'ain', u'can', u'theirs', u'my', u'and', u've', u'then', u'is', u'am', u'it', u'doesn', u'an', u'as', u'itself', u'at', u'have', u'in', u'any', u'if', u'again', u'no', u'when', u'same', u'how', u'other', u'which', u'you', u'shan', u'needn', u'haven', u'after', u'most', u'such', u'why', u'a', u'off', u'i', u'm', u'yours', u'so', u'y', u'the', u'having', u'once'])
stop_par_list = ['Q21025364', 'Q19361238', 'Q21027609', 'Q20088085', 'Q15184295', 'Q11266439', 'Q17362920', 'Q19798645', 'Q26884324', 'Q14204246', 'Q13406463', 'Q14827288', 'Q4167410', 'Q21484471', 'Q17442446', 'Q4167836', 'Q19478619', 'Q24017414', 'Q19361238', 'Q24027526', 'Q15831596', 'Q24027474', 'Q23958852', 'Q24017465', 'Q24027515', 'Q1924819']
# from load_wikidata2 import *
# ********************************************************************************************************* 

inf_eng = inflect.engine()
child_par_dict_val = child_par_dict.values()

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
        l2 = copy.copy(l1)
        random.shuffle(l2)
        return l2

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

# def negate_ques(ques):
#     ques_tokenized = ques.split(' ')
#     if 'is' in ques:
#         ques_result = ques.replace('is','is not')
#     elif 'has' in ques:
#         ques_result = ques.replace('has','has not')
#     elif 'have' in ques:
#         ques_result = ques.replace('have','have not')
#     elif 'was' in ques:
#         ques_result = ques.replace('was','was not')
#     elif 'were' in ques:
#         ques_result = ques.replace('were','were not')
#     else:
#         verb = ques_tokenized[2]
#         if verb[-1] == 's':
#             ques_result = ques.replace(verb,'does not %s' % verb[:-1])
#         else:
#             ques_result = ''
#             # print 'ERROR'
#     return ques_result

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
        if ques_tokenized[2] not in verb_list and ques_tokenized[2] not in adj_poss and 'present' in map(lambda x:x[0], tenses(ques_tokenized[2])):
            ques_result.insert(0,ques_tokenized[2])
            ques_result.insert(0,item_data[sub])
            ques_result.insert(0,'Does')
            ques_result[2] = lemma(ques_result[2])
        elif ques_tokenized[2] not in verb_list and ques_tokenized[2] not in adj_poss and 'past' in map(lambda x:x[0], tenses(ques_tokenized[2])):
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
        if ques_tokenized[2] not in verb_list and ques_tokenized[2] not in adj_poss and 'present' in map(lambda x:x[0], tenses(ques_tokenized[2])):
            ques_result.insert(0,ques_tokenized[2])
            ques_result.insert(0,child_par_dict_name_2[child_par_dict[sub]])
            ques_result.insert(0,'that')
            ques_result.insert(0,'Does')
            ques_result[2] = lemma(ques_result[2])
        elif ques_tokenized[2] not in verb_list and ques_tokenized[2] not in adj_poss and 'past' in map(lambda x:x[0], tenses(ques_tokenized[2])):
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


if 'true_label' in globals():
    del true_label # previous value of 'true_label' interferes with current value

# with open('wikidata_fanout_dict_list.pickle', 'rb') as handle:
#     wikidata_fanout_dict_list = pickle.load(handle)

def get_new_Qid():
    # This function is used to get a fresh Qid.
    # keys = wikidata.keys()
    # random.shuffle(keys)

    # for q in keys:
    #     base_cls = child_par_dict[q]
    #     if base_cls in base_class_list:
    #         Qid_init = q
    #         break
    # return Qid_init
    Qid_init = random.choice([q for q in wikidata_fanout_dict_list[:1000000] if ent_c[q.keys()[0]]<=args.entity_thresh and q.keys()[0] in child_par_dict]).keys()[0]
    return Qid_init

def isValidQid(Qid,prev_Qid):
    prev_Qid_filt = []

    prev_Qid_dict = {}

    
    for p in [pid for pid in wikidata[Qid] if pid in prop_data.keys()]:
        for q in [q for q in wikidata[Qid][p] if q in child_par_dict]:
            if Qid in d and p in d[Qid]:
                if child_par_dict[q] not in d[Qid][p]:
                    # if Qid not in prev_Qid_filt:
                    return True
            else:
                # if Qid not in prev_Qid_filt:
                return True

    return False

def get_sub_ques_filt_dict(Qid):
    filt_dict = {}

    for pid in [p for p in wikidata[Qid] if p in prop_data.keys() and p in sub_90_map and p in sing_sub_annot and p in plu_sub_annot]:
        for q in [item for item in wikidata[Qid][pid] if item in child_par_dict and ent_c[item]<=args.entity_thresh and tpl_c[(Qid,pid,item)]<=args.triple_thresh]:
            if Qid in d and pid in d[Qid] and child_par_dict[q] in sub_90_map[pid]:
                if child_par_dict[q] not in d[Qid][pid]:
                    if pid not in filt_dict:
                        filt_dict[pid] = [child_par_dict[q]]
                    else:
                        filt_dict[pid].append(child_par_dict[q])
            else:
                if pid not in filt_dict:
                    filt_dict[pid] = [child_par_dict[q]]
                else:
                    filt_dict[pid].append(child_par_dict[q])

    return filt_dict

def get_obj_ques_filt_dict(Qid):
    filt_dict = {}
    if Qid not in reverse_dict:
        return filt_dict
    for pid in [p for p in reverse_dict[Qid] if p in prop_data.keys() and p in obj_90_map and p in sing_obj_annot and p in plu_obj_annot]:
        for q in [item for item in reverse_dict[Qid][pid] if item in child_par_dict and ent_c[item]<=args.entity_thresh and tpl_c[(Qid,pid,item)]<=args.triple_thresh]:
            if Qid in d and pid in d[Qid] and child_par_dict[q] in obj_90_map[pid]:
                if child_par_dict[q] not in d[Qid][pid]:
                    if pid not in filt_dict:
                        filt_dict[pid] = [child_par_dict[q]]
                    else:
                        filt_dict[pid].append(child_par_dict[q])
            else:
                if pid not in filt_dict:
                    filt_dict[pid] = [child_par_dict[q]]
                else:
                    filt_dict[pid].append(child_par_dict[q])

    return filt_dict

def update_d_filt_dict(Qid,filt_dict):
    global d

    if Qid not in d:
        d[Qid] = filt_dict
    else:
        for pid in filt_dict:
            if pid in d[Qid]:
                d[Qid][pid].extend(filt_dict[pid])
            else:
                d[Qid][pid] = filt_dict[pid]


# HYPERPARAMETERS

parser = argparse.ArgumentParser(description='Hyper-parameter settings')
parser.add_argument('--min_iter', dest='min_iter', type=int, help="min. no. of hops in dialog", default = 7)
parser.add_argument('--max_iter', dest='max_iter', type=int, help="max. no. of hops in dialog", default = 14)
parser.add_argument('--n_dialog', dest='n_dialog', type=int, help="no. of dialogs to generate", default = 3000)
parser.add_argument('--max_hard_iter', dest='max_hard_iter', type=int, help="hard threshold on total no. of hops in dialog", default = 30)
parser.add_argument('--save_dir_id', dest='save_dir_id', type=str, help="The save_dir is QA_<save_dir_id>", default=3)
parser.add_argument('--entity_thresh', dest='entity_thresh', type=int, help="threshold on # of times an entity is repeated", default = 30)
parser.add_argument('--triple_thresh', dest='triple_thresh', type=int, help="threshold on # of times a triple is repeated", default = 10)
parser.add_argument('--counter_update_int', dest='counter_update_int', type=int, help="number of dialogs after which the counters are written and read again", default = 10)

parser.add_argument('--p_Qid_nochange', dest='p_Qid_nochange', type=float, help="prob. that Qid does not change and remains same as previous value", default = 0.5)
# parser.add_argument('--p_bc', dest='p_bc', type=float, help="prob. of transition from base ques. to clarification ques.", default = 0.1)
parser.add_argument('--p_sc', dest='p_sc', type=float, help="prob. of transition from secondary ques. to clarification ques.", default = 0.1)
# parser.add_argument('--p_bs', dest='p_bs', type=float, help="prob. of transition from base ques. to secondary ques.", default = 0.9)
parser.add_argument('--p_ss', dest='p_ss', type=float, help="prob. of transition from secondary ques. to secondary ques.", default = 0.2)
parser.add_argument('--p_sset', dest='p_sset', type=float, help="prob. of transition from secondary ques. to set based question", default = 0.2)
parser.add_argument('--p_sbool', dest='p_sbool', type=float, help="prob. of transition from secondary ques. to boolean question", default = 0.1)
parser.add_argument('--p_scount', dest='p_scount', type=float, help="prob. of transition from secondary ques. to count based question", default = 0.2)
parser.add_argument('--p_sset_count', dest='p_sset_count', type=float, help="prob. of transition from secondary ques. to count-set based question", default = 0.2)
parser.add_argument('--p_sub', dest='p_sub', type=float, help="prob. that secondary ques. is a subject based ques.", default = 0.5)
parser.add_argument('--p_obj', dest='p_obj', type=float, help="prob. that secondary ques. is a object based ques.", default = 0.5)
parser.add_argument('--p_basic', dest='p_basic', type=float, help="prob. that secondary ques. is a singular basic ques.", default = 0.3)
parser.add_argument('--p_sing', dest='p_sing', type=float, help="prob. that secondary ques. is a singular indirect ques.", default = 0.3)
parser.add_argument('--p_plu', dest='p_plu', type=float, help="prob. that secondary ques. is a plural indirect ques.", default = 0.2)
parser.add_argument('--p_basic_plu', dest='p_basic_plu', type=float, help="prob. that secondary ques. is a basic plural ques.", default = 0.2)
parser.add_argument('--p_bool_sing_dir', dest='p_bool_sing_dir', type=float, help="prob. that bool ques. is direct", default = 0.1)
parser.add_argument('--p_bool_sing_indir1', dest='p_bool_sing_indir1', type=float, help="prob. that bool ques. is singular indirect (sub. is indirect)", default = 0.2)
parser.add_argument('--p_bool_sing_indir2', dest='p_bool_sing_indir2', type=float, help="prob. that bool ques. is singular indirect (obj. is indirect)", default = 0.3)
parser.add_argument('--p_bool_plu_dir', dest='p_bool_plu_dir', type=float, help="prob. that bool ques. is plural direct (obj. is plural)", default = 0.1)
parser.add_argument('--p_bool_plu_indir1', dest='p_bool_plu_indir1', type=float, help="prob. that bool ques. is plural indirect (sub. is indirect, obj. is plural)", default = 0.3)
parser.add_argument('--p_not', dest='p_not', type=float, help="prob. that set-based ques. is a not ques.", default = 0.0)
parser.add_argument('--p_inc_ques_1', dest='p_inc_ques_1', type=float, help="prob. that in incomplete ques., obj. parent is changed", default = 0.5)
parser.add_argument('--p_inc_ques_2', dest='p_inc_ques_2', type=float, help="prob. that in incomplete ques., sub. is changed", default = 0.5)
parser.add_argument('--p_inc_set', dest='p_inc_set', type=float, help="prob. that set based ques is incomplete", default = 0.3)
parser.add_argument('--p_inc_count', dest='p_inc_count', type=float, help="prob. that count based ques (7) (sub-type = 1) is incomplete", default = 0.3)
parser.add_argument('--update_counter', dest='update_counter', type=str2bool, nargs='?', help="if True, both counters are updated", default = False)
parser.add_argument('--sync_counter', dest='sync_counter', type=str2bool, nargs='?', help="if True, both counters are synced between different jobs", default = False)

parser.add_argument('--global_ans_thresh', dest='global_ans_thresh', type=int, help="threshold on no. of ans of any ques., else ques. is discarded", default = 1000)
parser.add_argument('--plural_sub_ques_ans_thresh', dest='plural_sub_ques_ans_thresh', type=int, help="threshold on no. of ans of sub. based plural ques.", default = 3)
parser.add_argument('--plural_obj_ques_ans_thresh', dest='plural_obj_ques_ans_thresh', type=int, help="threshold on no. of ans of obj. based plural ques.", default = 3)
parser.add_argument('--set_ques_ans_thresh', dest='set_ques_ans_thresh', type=int, help="threshold on no. of ans of set based ques.", default = 10)
parser.add_argument('--set_obj_thresh', dest='set_obj_thresh', type=int, help="threshold on no. of candidates of obj. in set-based ques.", default = 1000)
parser.add_argument('--ps_tuple_thresh', dest='ps_tuple_thresh', type=int, help="threshold on no. of candidates of ps_tuple list", default = 100)
parser.add_argument('--pq_tuple_thresh', dest='pq_tuple_thresh', type=int, help="threshold on no. of candidates of pq_tuple list", default = 100)
parser.add_argument('--mode', dest='mode', type=str, help="mode = test or train for counter read", default = 'train')
parser.add_argument('--count_ques_sub_thresh', dest='count_ques_sub_thresh', type=int, help="threshold on no. of sub of count based ques.", default = 1000)
parser.add_argument('--regex_dir',dest='regex_dir', type=str, help = 'name of dir (wrt cwd) where regex patterns to ignore(ques-wise) are stored',default='no_such_dir')
parser.add_argument('--use_regex', dest='use_regex', type=str2bool, nargs='?', help="if True, regex filtering is ON", default = False)
parser.add_argument('--out_dir',dest='out_dir', type=str, help = 'name of dir (wrt cwd) where dialogue dirs are created',default='test') # should be required

args = parser.parse_args()
print(args)

try:
    assert os.path.exists(args.out_dir)
except:
    raise Exception('out dir not found')

try:
    assert os.path.exists(os.path.join(args.out_dir,'entity_counter.pickle'))
except:
    raise Exception('entity counter not found')

try:
    assert os.path.exists(os.path.join(args.out_dir,'triple_counter.pickle'))
except:
    raise Exception('triple counter not found')

try:
    assert os.path.exists(os.path.join(args.out_dir,'rel_counter.pickle'))
except:
    raise Exception('rel counter not found')

f1 = open(os.path.join(args.out_dir,'QA_%s_log.txt' % args.save_dir_id),'w')
f1.close()

if os.path.exists(args.regex_dir):
    f1 = open(os.path.join(args.out_dir,'QA_%s_log.txt' % args.save_dir_id),'a')
    f1.write('active set dir exists')
    f1.close()
    # with open(os.path.join(args.regex_dir,'regex_ques_1.pickle'),'r') as f1:
    #     regex_ques_1 = pickle.load(f1)

    # with open(os.path.join(args.regex_dir,'regex_ques_2.pickle'),'r') as f1:
    #     regex_ques_2 = pickle.load(f1)

    # with open(os.path.join(args.regex_dir,'regex_ques_4.pickle'),'r') as f1:
    #     regex_ques_4 = pickle.load(f1)

    # with open(os.path.join(args.regex_dir,'regex_ques_5.pickle'),'r') as f1:
    #     regex_ques_5 = pickle.load(f1)

    # with open(os.path.join(args.regex_dir,'regex_ques_6.pickle'),'r') as f1:
    #     regex_ques_6 = pickle.load(f1)

    # with open(os.path.join(args.regex_dir,'regex_ques_7.pickle'),'r') as f1:
    #     regex_ques_7 = pickle.load(f1)

    # with open(os.path.join(args.regex_dir,'regex_ques_8.pickle'),'r') as f1:
    #     regex_ques_8 = pickle.load(f1)

    with open(os.path.join(args.regex_dir,'regex_ques_all.pickle'),'r') as f1:
        regex_ques_all = pickle.load(f1)
else:
    f1 = open(os.path.join(args.out_dir,'QA_%s_log.txt' % args.save_dir_id),'a')
    f1.write('active set dir does not exist')
    f1.close()
    # regex_ques_1 = list()
    # regex_ques_2 = list()
    # regex_ques_4 = list()
    # regex_ques_5 = list()
    # regex_ques_6 = list()
    # regex_ques_7 = list()
    # regex_ques_8 = list()
    regex_ques_all = list()


niter = random.randint(args.min_iter,args.max_iter)
# niter = 50 # number of hops in the knowledge graph

# p_Qid_nochange = 0.5 # prob. that Qid does not change and remains same as previous value

# args.p_bc = 0.1 # prob. of transition from base ques. to clarification ques.
# # p_cs = 0.9 # prob. of transition from clarification ques. to secondary ques.
# args.p_sc = 0.2 # prob. of transition from secondary ques. to clarification ques.
# args.p_bs = 0.9 # prob. of transition from base ques. to secondary ques.
# p_ss = 0.3 # prob. of transition from secondary ques. to secondary ques.
# # p_cc = 0.1 # prob. of transition from clarification ques. to clarification ques.
# p_sset = 0.3 # prob. of transition from secondary ques. to set based question
# args.p_sbool = 0.2 # prob. of transition from secondary ques. to boolean question 

# args.p_sub = 0.5 # prob. that secondary ques. is a subject based ques.
# args.p_obj = 0.5 # prob. that secondary ques. is a object based ques.

# p_basic = 0.3 # prob. that secondary ques. is a basic ques.
# args.p_sing = 0.3 # prob. that secondary ques. is a singular indirect ques.
# args.p_plu = 0.2 # prob. that secondary ques. is a plural indirect ques.
# args.p_basic_plu = 0.2 # prob. that secondary ques. is a basic plural ques.

# args.p_bool_sing_dir = 0.2
# args.p_bool_sing_indir1 = 0.2
# args.p_bool_sing_indir2 = 0.2
# args.p_bool_plu_dir = 0.2
# args.p_bool_plu_indir1 = 0.2

# args.p_not = 0.15
# args.p_count = 0.15

# args.p_inc_ques_1 = 0.5
# args.p_inc_ques_2 = 0.5

# args.plural_sub_ques_ans_thresh = 7 # the no. of ans. of sub. based ques. is capped to this thresh based on top fanout criteria
# args.plural_obj_ques_ans_thresh = 7 # the no. of ans. of obj. based ques. is capped to this thresh based on top fanout criteria
# args.set_ques_ans_thresh = 10
# args.set_obj_thresh = 1000
# args.ps_tuple_thresh = 100

'''
1: base ques.(default:Direct subject based) 
2: secondary ques.
3: clarification ques.
4: Set based question
'''

'''
Secondary ques. type IDs
1: Subject based ques.
2: Object based ques. 

Secondary ques. sub-type IDs
1: Basic Question (Singular)
2: Singular Indirect
3: Plural Indirect
4. Plural Basic

'''
if not os.path.isdir(os.path.join(args.out_dir, 'QA_%s' % args.save_dir_id)):
    os.mkdir(os.path.join(args.out_dir, 'QA_%s' % args.save_dir_id),0775)

# with open('entity_counter.pickle','rb') as data_file:
#     for i in range(20):
        
#         try:
#             fcntl.flock(data_file, fcntl.LOCK_SH|LOCK_NB)
#             ent_c = pickle.load(data_file)
#             fcntl.flock(data_file, fcntl.LOCK_UN)
#             break
#         except:
#             pass
#     if 'ent_c' not in globals():
#         ent_c = collections.Counter()
    

# with open('triple_counter.pickle','rb') as data_file:
#     for i in range(20):
        
#         try:
#             fcntl.flock(data_file, fcntl.LOCK_SH|LOCK_NB)
#             tpl_c = pickle.load(data_file)
#             fcntl.flock(data_file, fcntl.LOCK_UN)
#             break
#         except:
#             pass
#     if 'tpl_c' not in globals():
#         tpl_c = collections.Counter()

if args.mode == 'test': # hard test
    # ent_c = collections.Counter()
    # tpl_c = collections.Counter()
    with open(os.path.join(args.out_dir,'entity_counter.pickle'),'rb') as data_file:
        for i in range(20):
            try:
                fcntl.flock(data_file, fcntl.LOCK_SH|LOCK_NB)
                ent_c = pickle.load(data_file)
            except:
                time.sleep(10)
                continue
            fcntl.flock(data_file, fcntl.LOCK_UN)
            break
        if 'ent_c' not in globals():
            raise Exception('Unable to load entity counter')

    with open(os.path.join(args.out_dir,'triple_counter.pickle'),'rb') as data_file:
        for i in range(20):        
            try:
                fcntl.flock(data_file, fcntl.LOCK_SH|LOCK_NB)
                tpl_c = pickle.load(data_file)
            except:
                time.sleep(10)
                continue
            fcntl.flock(data_file, fcntl.LOCK_UN)
            break
        if 'tpl_c' not in globals():
            raise Exception('Unable to load triple counter')

    with open(os.path.join(args.out_dir,'rel_counter.pickle'),'rb') as data_file:
        for i in range(20):        
            try:
                fcntl.flock(data_file, fcntl.LOCK_SH|LOCK_NB)
                rel_c = pickle.load(data_file)
            except:
                time.sleep(10)
                continue
            fcntl.flock(data_file, fcntl.LOCK_UN)
            break
        if 'rel_c' not in globals():
            raise Exception('Unable to load triple counter')

    ent_c_save = ent_c.copy()
    tpl_c_save = tpl_c.copy()
    rel_c_save = rel_c.copy()
else: # mode = train/easy test/val
    with open(os.path.join(args.out_dir,'entity_counter.pickle'),'rb') as data_file:
        for i in range(20):         
            try:
                fcntl.flock(data_file, fcntl.LOCK_SH|LOCK_NB)
                ent_c = pickle.load(data_file)
                fcntl.flock(data_file, fcntl.LOCK_UN)
                break
            except:
                time.sleep(10)
                pass
        if 'ent_c' not in globals():
            raise Exception('Unable to load entity counter')
            # ent_c = collections.Counter()
        

    with open(os.path.join(args.out_dir,'triple_counter.pickle'),'rb') as data_file:
        for i in range(20):       
            try:
                fcntl.flock(data_file, fcntl.LOCK_SH|LOCK_NB)
                tpl_c = pickle.load(data_file)
                fcntl.flock(data_file, fcntl.LOCK_UN)
                break
            except:
                time.sleep(10)
                pass
        if 'tpl_c' not in globals():
            raise Exception('Unable to load triple counter')
            # tpl_c = collections.Counter()

    with open(os.path.join(args.out_dir,'rel_counter.pickle'),'rb') as data_file:
        for i in range(20):       
            try:
                fcntl.flock(data_file, fcntl.LOCK_SH|LOCK_NB)
                rel_c = pickle.load(data_file)
                fcntl.flock(data_file, fcntl.LOCK_UN)
                break
            except:
                time.sleep(10)
                pass
        if 'tpl_c' not in globals():
            raise Exception('Unable to load rel counter')

    ent_c_save = ent_c.copy()
    tpl_c_save = tpl_c.copy()
    rel_c_save = rel_c.copy()

    # with open('entity_counter.pickle','rb') as data_file:
    #     ent_c = pickle.load(data_file)

    # with open('triple_counter.pickle','rb') as data_file:
    #     tpl_c = pickle.load(data_file)
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

for file_id in range(args.n_dialog):
    # print_memory_profile()
    f1 = open(os.path.join(args.out_dir,'QA_%s_log.txt' % args.save_dir_id),'a')
    f1.write('Dialog ID : %d\n' % file_id)
    f1.close()

    rel_list = []
    niter = random.randint(args.min_iter,args.max_iter)

    try:
        # ent_c_update = False
        # tpl_c_update = False
        # if args.sync_counter:
        #     if file_id % args.counter_update_int == 0:
        #         with open('entity_counter.pickle','rb') as data_file:
        #             for i in range(20):
                        
        #                 try:
        #                     fcntl.flock(data_file, fcntl.LOCK_SH|LOCK_NB)
        #                     ent_c = pickle.load(data_file)
        #                 except:
        #                     time.sleep(10)
        #                     continue
        #                 fcntl.flock(data_file, fcntl.LOCK_UN)
        #                 ent_c_update = True
        #                 break

        #         with open('triple_counter.pickle','rb') as data_file:
        #             for i in range(20):
                        
        #                 try:
        #                     fcntl.flock(data_file, fcntl.LOCK_SH|LOCK_NB)
        #                     tpl_c = pickle.load(data_file)
        #                 except:
        #                     time.sleep(10)
        #                     continue
        #                 fcntl.flock(data_file, fcntl.LOCK_UN)
        #                 tpl_c_update = True
        #                 break

        dialog_list = []
        Qid_init = get_new_Qid()
        # print 'Qid_init = %s' % Qid_init

        # print 'Initial Item Label: %s' % item_data[Qid_init]

        Qid = Qid_init
        prev_Qid=[Qid]
        prev_Qid_nest = [[Qid]]
        
        print prev_Qid

        prev_sec_ques_type = [0, 0] # contains sec-ques type of last ques. and last to last ques.; 0 is the concerned ques. was not a secondary ques.
        prev_sec_ques_sub_type = [0, 0] # contains sec-ques type of last ques. and last to last ques.; 0 is the concerned ques. was not a secondary ques.
        prev_ques_count = [0, 0] # contains count of number of answers of last ques. and last to last ques.

        # d = defaultdict(list) # for each key as Qid it stores the Pid s for which ques. has been asked already
        d = {} # outer index: Qid seen before, next inner: pid seen before, key; list of object parents of pid seen before
        prev_ques_failed = False
        in_clar_ques = False
        no_success_ques = 0
        iter_id = 0
        ans_list = []
        prev_prev_ans_list = []
        last_Qid = ''
        if 'ans_list_full' in globals():
            del ans_list_full

        ques_type_id = 1 
        sec_ques_type = 1
        sec_ques_sub_type = 1
        ques_type_id_save = -1

        prop_res = 'P999' # DUMMY pid
        prop_Qid_par = 'Q999999' #dummy QID       
        
        start_time = timeit.default_timer()

        while (no_success_ques < niter and iter_id < args.max_hard_iter) or in_clar_ques:
            # print '\nIteration ID: %d' % iter_id
            # print d
            if (timeit.default_timer() - start_time) > 300: # time elapsed > 5 mins
                break

            ent_c_plus = 0
            json_plus = 0

            iter_id += 1
            # f1 = open(os.path.join(args.out_dir,'QA_%s_log.txt' % args.save_dir_id),'a')
            # f1.write('Iter ID: %d\n' % iter_id)
            # f1.close()

            if not prev_ques_failed:
                last_Qid = Qid
                last_prop_res = prop_res
                last_par = prop_Qid_par

            if len(dialog_list) > 1 and 'entities' in dialog_list[-2] and len(dialog_list[-2]['entities'])==1 and 'ques_type_id' in dialog_list[-2]:
                last_Qid = dialog_list[-2]['entities'][0]

            prev_Qid_filt = []
            # ans_list = []
            # ans_list_t = []
            # sub_list = []

            for block in prev_Qid_nest:
                filt_block = []
                for QID in [item for item in block if ent_c[item]<=args.entity_thresh and item in child_par_dict]:
                    for p in [pid for pid in wikidata[QID] if pid in prop_data.keys()]:
                        for q in [qid for qid in wikidata[QID][p] if qid in child_par_dict and ent_c[qid]<=args.entity_thresh]:
                            if QID in d and p in d[QID]:
                                if child_par_dict[q] not in d[QID][p]:
                                    if QID not in filt_block:
                                        filt_block.append(QID)
                            else:
                                if QID not in filt_block:
                                    filt_block.append(QID)
                if len(filt_block) > 0:
                    prev_Qid_filt.append(filt_block)

            # print 'prev_Qid_filt = %s' % ', '.join(prev_Qid_filt)
            # prev_Qid_filt = prev_Qid_dict.keys()

            try:
                if ques_type_id == 3: # no Qid change for clarification question
                    Qid_nochange = 1
                elif isValidQid(Qid,prev_Qid):
                    Qid_nochange = np.random.choice(2,p=[(1-args.p_Qid_nochange), args.p_Qid_nochange]) # retain the last Qid with some p if it still has untraversed edges
                else:
                    Qid_nochange = 0 # else pick up new Qid from previous context

                if Qid_nochange == 0:
                    # index = int(math.floor(random.expovariate(0.4)))
                    lambd = 0.4
                    if Qid in wikidata and Qid in reverse_dict:
                        sec_ques_type = np.random.choice(np.array([1,2]),p=[args.p_sub, args.p_obj])
                    elif Qid not in reverse_dict:
                        sec_ques_type = 1
                    else:
                        sec_ques_type = 2

                    if sec_ques_type == 1:
                        prob = [lambd*np.exp(-1*lambd*i)*sum([rel_fw_fanout(qid) for qid in prev_Qid_filt[i]]) for i in range(len(prev_Qid_filt))]
                        if sum(prob)==0:
                            prob[0] += 1e-5
                        prob_norm = [x*1.0/sum(prob) for x in prob]
                    else:
                        prob = [lambd*np.exp(-1*lambd*i)*sum([rel_bw_fanout(qid) for qid in prev_Qid_filt[i]]) for i in range(len(prev_Qid_filt))]
                        if sum(prob)==0:
                            prob[0] += 1e-5
                        prob_norm = [x*1.0/sum(prob) for x in prob]
                    index = np.random.choice(range(len(prev_Qid_filt)), p=prob_norm)
                    block_qid = prev_Qid_filt[index]

                    if sec_ques_type == 1:
                        block_qid_score = [rel_fw_fanout(qid) for qid in block_qid]
                    else:
                        block_qid_score = [rel_bw_fanout(qid) for qid in block_qid]

                    ques_Qid = block_qid[np.argmax(block_qid_score)]

                else:
                    ques_Qid = Qid
            except:
                logging.exception('Something aweful happened')
                # print prev_Qid
                # print Qid
                # print prev_Qid_nest
                # print prev_Qid_filt
                # print d[Qid]
                # print 'prev_Qid_filt empty'
                # print prev_Qid_filt
                # print Qid

                if no_success_ques < 3:
                    Qid = get_new_Qid() # to be removed
                    prev_Qid=[Qid]
                    d = {}
                    dialog_list = []
                    print 'new Qid = %s' % Qid
                    continue
                else:
                    print 'prev_Qid_filt empty, truncating the dialogue'
                    break
                

            Qid = ques_Qid # exponential decay; may travel backwards on the tread knowledge graph
            # print 'Qid for current iteration = %s' % Qid

            if not prev_ques_failed:
                prev_sec_ques_sub_type[1] = prev_sec_ques_sub_type[0]
                prev_sec_ques_sub_type[0] = sec_ques_sub_type # this info. of secondary ques. will be used to decide whether the next question will be a clarification question

            if len(dialog_list) > 1 and len(dialog_list[-1]['entities']) > 1: # Plural Indirect ques. to be asked only if the previous ques. has multiple answers (all of which would now act as subjects)
                sec_ques_sub_type = np.random.choice(np.array([1, 2, 3, 4]), p=[args.p_basic, args.p_sing, args.p_plu, args.p_basic_plu]) # Actual question asked may not be a secondary question
            else:
                prob_list = [args.p_basic, args.p_sing]
                sec_ques_sub_type = np.random.choice(np.array([1, 2]), p=[x*1.0/sum(prob_list) for x in prob_list]) # Actual question asked may not be a secondary question

            # print ('sec ques. sub-type id=%d' %  sec_ques_sub_type)

            if not prev_ques_failed:
                prev_sec_ques_type[1] = prev_sec_ques_type[0]
                prev_sec_ques_type[0] = sec_ques_type # this info. of secondary ques. will be used to decide whether the next question will be a clarification question    
                last_ques_type_id_save = ques_type_id_save
            ques_type_id_save = ques_type_id

            if ques_type_id == 2 and sec_ques_sub_type == 2: # Singular Indirect Question (must be secondary); need change for bool ques. too
                active_set = [q for q in dialog_list[-1]['entities']]
                if last_ques_type_id_save in [1,4] or (last_ques_type_id_save == 2 and sec_ques_sub_type in [1,2]) or (last_ques_type_id_save == 5 and bool_ques_type != 6) or (last_ques_type_id_save == 6 and type_choice in [2,3]) or (last_ques_type_id_save == 7 and count_ques_sub_type == 1) or (last_ques_type_id_save == 8 and count_ques_sub_type in [1,2]):
                    if last_Qid in child_par_dict and child_par_dict[last_Qid] not in [child_par_dict[x] for x in active_set if x in child_par_dict]:
                        active_set.append(last_Qid)
                if len(active_set)>0:
                    Qid = random.choice(active_set) # choose subject based on answers in the previous question
                else:
                    sec_ques_sub_type = 1
               
            if Qid == last_Qid and ques_type_id == 2 and sec_ques_sub_type == 1 and len(dialog_list) > 1 and 'ques_type_id' in dialog_list[-2] and dialog_list[-2]['ques_type_id']==2 and dialog_list[-2]['sec_ques_sub_type'] in [1,2]:
                sec_ques_sub_type == 2 # switch to singular indirect if the Qid is same as last_Qid


            # print ('ques. type id=%d' %  ques_type_id_save)
            # try:
            if ques_type_id==1: # Basic Question

                sec_ques_type = sec_ques_sub_type = 0 # Direct ques. is not a secondary ques.

                # prop_res = random.choice(filt_dict.keys())
                # prop_Qid = random.choice([q for q in filt_dict[prop_res] if len(set(wikidata[q]['instance_of']) & set(sub_ques_dict[prop_res].keys()))>0])
                filt_dict = get_sub_ques_filt_dict(Qid)
                prop_list = [p for p in filt_dict.keys() if len(filt_dict[p])>0]
                prop_list = list(set(prop_list) - set(rel_list)) # remove the ones already used
                if len(prop_list) == 0:
                    update_d_filt_dict(Qid,filt_dict)
                    prev_ques_failed = True
                    continue
                p_freq_dict = get_rel_dist(rel_c)
                prop_list_prob = [p_freq_dict[p] for p in prop_list]
                prop_list_prob_norm = [x*1.0/sum(prop_list_prob) for x in prop_list_prob]
                prop_res = np.random.choice(prop_list, p=prop_list_prob_norm)
                prop_Qid_par = random.choice(filt_dict[prop_res])

                ans_list = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                ans_list = list(set(ans_list))
                # if not is_par_rel_overlap(prop_Qid_par, prop_res):
                #     if len(ans_list) == 1:
                #         ques = random.choice(sing_sub_annot[prop_res])
                #         ques = ques.replace('OPP',child_par_dict_name_2[prop_Qid_par])
                #     else:
                #         ques = random.choice(plu_sub_annot[prop_res])
                #         ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                # else:
                #     if len(ans_list) == 1:
                #         ques = random.choice(sing_sub_annot_wh[prop_res])
                #         if prop_Qid_par != 'Q215627':
                #             ques = ques.replace('Which OPP','What')
                #         else:
                #             ques = ques.replace('Which OPP','Who')
                #     else:
                #         ques = random.choice(plu_sub_annot_wh[prop_res])
                #         if prop_Qid_par != 'Q215627':
                #             ques = ques.replace('Which OPPS','What')
                #         else:
                #             ques = ques.replace('Which OPPS','Who')

                # is_pphrase_ov = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in sing_sub_annot[prop_res]]
                # if False in is_pphrase_ov:
                #     if len(ans_list) == 1:
                #         ques = random.choice([sing_sub_annot[prop_res][i] for i in range(5) if is_pphrase_ov[i] == False])
                #         ques = ques.replace('OPP',child_par_dict_name_2[prop_Qid_par])
                #     else:
                #         ques = random.choice([plu_sub_annot[prop_res][i] for i in range(5) if is_pphrase_ov[i] == False])
                #         ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                # else:
                #     if len(ans_list) == 1:
                #         ques = random.choice(sing_sub_annot_wh[prop_res])
                #         if prop_Qid_par != 'Q215627':
                #             ques = ques.replace('Which OPP','What')
                #         else:
                #             ques = ques.replace('Which OPP','Who')
                #     else:
                #         ques = random.choice(plu_sub_annot_wh[prop_res])
                #         if prop_Qid_par != 'Q215627':
                #             ques = ques.replace('Which OPPS','What')
                #         else:
                #             ques = ques.replace('Which OPPS','Who')

                if len(ans_list) == 1:
                    is_pphrase_ov = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in sing_sub_annot[prop_res]]
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

                # print 'Qid = %s' % Qid               
                # print 'Ques: '+ ques
                if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                    prev_ques_failed = True
                    ques_type_id = 2
                    continue

                ans_list_full = ans_list

                if len(ans_list) > args.plural_sub_ques_ans_thresh:
                    ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                    sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                    ans_list_t = [ans_list[i] for i in sort_index]
                    ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                
                if args.update_counter:
                    ent_c.update([Qid])
                    ent_c.update(ans_list)
                ent_c_plus += (len(ans_list)+1)
                tpl_set = [(Qid,prop_res,q) for q in ans_list]

                if args.update_counter:
                    tpl_c.update(tpl_set)
                tpl_regex = ['(%s,%s,%s)' % (Qid,prop_res,'|'.join(['c(%s)'% x for x in [prop_Qid_par]]))]

                # if args.use_regex and len(set(tpl_regex).intersection(set(regex_ques_1))) > 0:
                #     prev_ques_failed = True
                #     continue

                dict1 = {}
                dict1['speaker'] = 'USER'
                dict1['utterance'] = ques
                dict1['ques_type_id'] = ques_type_id_save
                dict1['entities'] = [Qid]
                dict1['relations'] = [prop_res]

                #****************************************
                dict1['Qid'] = Qid
                dict1['prop_res'] = prop_res
                dict1['prop_Qid_par'] = prop_Qid_par
                dict1['len(ans_list) > 1'] = (True if len(ans_list)>1 else False)
                dict1['description'] = 'Simple Question'
                #****************************************
                dict1['signature'] = get_dict_signature(dict1.copy())
                if dict1['signature'] in regex_ques_all:
                    prev_ques_failed = True
                    continue

                dialog_list.append(dict1.copy())
                
                prev_ques_count[1] = prev_ques_count[0]
                prev_ques_count[0] = len(ans_list)

                # ques_type_id = np.random.choice(np.array([2, 3]), p=[args.p_bs, args.p_bc]) # ques type_id of next question
                ques_type_id = 2 # next ques. is secondary ques.

                if ques_type_id != 3: # skip answer if the next question is a clarification question 
                    ans = ', '.join([item_data[q] for q in ans_list])
                    # print 'Ans: %s\n' % ans
                    dict1 = {}
                    dict1['speaker'] = 'SYSTEM'
                    dict1['utterance'] = ans
                    dict1['entities'] = [q for q in ans_list]
                    dict1['active_set'] = tpl_regex[:]
                    dict1['ans_list_full'] = ans_list_full
                    json_plus += len(dict1['entities'])
                    dict1['signature'] = get_dict_signature(dict1.copy())
                    dialog_list.append(dict1.copy())                    
                    
                    
                else:
                    # print 'Skipping answer next ques. is clarification ques.'
                    in_clar_ques = True

            elif ques_type_id==2: # Secondary question  

                if sec_ques_sub_type == 3 or sec_ques_sub_type == 4:
                    if not set(dialog_list[-1]['entities']).issubset(reverse_dict):
                        sec_ques_type = 1
                    elif not set(dialog_list[-1]['entities']).issubset(wikidata):
                        sec_ques_type = 2
                    else:
                        sec_ques_type = np.random.choice(np.array([1,2]),p=[args.p_sub, args.p_obj])
                elif Qid in wikidata and Qid in reverse_dict:
                    sec_ques_type = np.random.choice(np.array([1,2]),p=[args.p_sub, args.p_obj])
                elif Qid not in reverse_dict:
                    sec_ques_type = 1
                else:
                    sec_ques_type = 2

                if len(dialog_list)>1 and 'Qid' in dialog_list[-2]:
                    last_Qid = dialog_list[-2]['Qid']
                elif len(dialog_list)>3 and 'Did you mean' in dialog_list[-3]:
                    last_Qid = dialog_list[-4]['Qid']

                if Qid == last_Qid and sec_ques_sub_type == 1:
                    sec_ques_sub_type == 2 # switch to singular indirect if the Qid is same as last_Qid

                if len(dialog_list) > 1 and len(dialog_list[-1]['entities']) > 1 and ((sec_ques_type == 1 and sec_ques_sub_type == 2) or (sec_ques_type == 2 and sec_ques_sub_type == 2)) and Qid != last_Qid:
                    ques_type_id = 3 # if previous to previous question has multiple answers and previous ques. is a singular indirect ques., then definitely ask a clarification ques.
                    print 'clarification ques selected'
                else:
                    if ques_type_id == 2 and sec_ques_type == 1 and sec_ques_sub_type == 1:
                        ques_type_id = random.choice([2,6]) # randomly choose between secondary and incomplete ques
                    elif ques_type_id == 2 and (sec_ques_sub_type == 1 or sec_ques_sub_type == 3 or sec_ques_sub_type == 4):
                        ques_type_id = 2 # No clarification question follows a direct question or plural indirect question
                    else:
                        prob = [args.p_ss , args.p_sset, args.p_sbool, args.p_scount, args.p_sset_count]
                        prob_norm = [x*1.0/sum(prob) for x in prob]
                        ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=prob_norm) # ques type_id of next question
                
                # print 'sec_ques_type = %d' % sec_ques_type
                if len(dialog_list[-1]['entities'])==1 and dialog_list[-1]['entities'][0] == Qid and sec_ques_sub_type==1:
                    sec_ques_sub_type = 2

                if sec_ques_type == 1: # Subject based ques.
                    filt_dict = get_sub_ques_filt_dict(Qid)
                    if Qid == last_Qid and sec_ques_sub_type == 1:
                        sec_ques_sub_type == 2 # switch to singular indirect if the Qid is same as last_Qid
                        
                    if sec_ques_sub_type==1 or sec_ques_sub_type==2: # Direct (Singular) Question or Singular Indirect Question
                        # prop_res = random.choice(filt_dict.keys())
                        # prop_Qid = random.choice([q for q in filt_dict[prop_res] if len(set(wikidata[q]['instance_of']) & set(sub_ques_dict[prop_res].keys()))>0])
                        prop_list = [p for p in filt_dict.keys() if len(filt_dict[p])>0]
                        prop_list = list(set(prop_list) - set(rel_list)) # remove the ones already used
                        if len(prop_list) == 0:
                            update_d_filt_dict(Qid,filt_dict)
                            prev_ques_failed = True
                            continue
                        p_freq_dict = get_rel_dist(rel_c)
                        prop_list_prob = [p_freq_dict[p] for p in prop_list]
                        prop_list_prob_norm = [x*1.0/sum(prop_list_prob) for x in prop_list_prob]
                        prop_res = np.random.choice(prop_list, p=prop_list_prob_norm)
                        prop_Qid_par = random.choice(filt_dict[prop_res])

                        if last_ques_type_id_save == ques_type_id_save and prev_sec_ques_type[0] == sec_ques_type and prev_sec_ques_sub_type[0] == sec_ques_sub_type and prop_res == last_prop_res and prop_Qid_par == last_par:
                            prev_ques_failed = True
                            ques_type_id = 2 # No clarification question follows a failed question
                            # print d
                            continue

                        # if ques_type_id == 3: # next question is a clarification ques.
                        #     prev_prev_ans_list = ans_list

                        ans_list = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                        ans_list = list(set(ans_list))
                        # if sec_ques_sub_type==1:
                        #     if not is_par_rel_overlap(prop_Qid_par, prop_res):
                        #         if len(ans_list) == 1:
                        #             ques = random.choice(sing_sub_annot[prop_res])
                        #         else:
                        #             ques = random.choice(plu_sub_annot[prop_res])
                        #     else:
                        #         if len(ans_list) == 1:
                        #             ques = random.choice(sing_sub_annot_wh[prop_res])
                        #         else:
                        #             ques = random.choice(plu_sub_annot_wh[prop_res])
                        # else:
                        #     if len(ans_list) == 1:
                        #         ques = sing_basic2indirect(random.choice(sing_sub_annot_wh[prop_res]),Qid,child_par_dict, prop_Qid_par, prop_res)
                        #     else:
                        #         ques = sing_basic2indirect(random.choice(plu_sub_annot_wh[prop_res]),Qid,child_par_dict, prop_Qid_par, prop_res)

                        # ques = ques.replace('XXX',item_data[Qid])

                        # if not is_par_rel_overlap(prop_Qid_par, prop_res):
                        #     if len(ans_list) == 1:
                        #         ques = ques.replace('OPP',child_par_dict_name_2[prop_Qid_par])
                        #     else:
                        #         ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                        # else:
                        #     if len(ans_list) == 1:
                        #         if prop_Qid_par != 'Q215627':
                        #             ques = ques.replace('Which OPP','What')
                        #         else:
                        #             ques = ques.replace('Which OPP','Who')
                        #     else:
                        #         if prop_Qid_par != 'Q215627':
                        #             ques = ques.replace('Which OPPS','What')
                        #         else:
                        #             ques = ques.replace('Which OPPS','Who')

                        # is_pphrase_ov = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in sing_sub_annot[prop_res]]
                        # if False in is_pphrase_ov and sec_ques_sub_type==1:
                        #     if len(ans_list) == 1:
                        #         ques = random.choice([sing_sub_annot[prop_res][i] for i in range(5) if is_pphrase_ov[i] == False])
                        #         ques = ques.replace('OPP',child_par_dict_name_2[prop_Qid_par])
                        #     else:
                        #         ques = random.choice([plu_sub_annot[prop_res][i] for i in range(5) if is_pphrase_ov[i] == False])
                        #         ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                        # elif False in is_pphrase_ov[:3] and sec_ques_sub_type==2:
                        #     if len(ans_list) == 1:
                        #         ques = sing_basic2indirect(random.choice([sing_sub_annot[prop_res][i] for i in range(3) if is_pphrase_ov[i] == False]),Qid,child_par_dict, prop_Qid_par, prop_res)
                        #         ques = ques.replace('OPP',child_par_dict_name_2[prop_Qid_par])
                        #     else:
                        #         ques = sing_basic2indirect(random.choice([plu_sub_annot[prop_res][i] for i in range(3) if is_pphrase_ov[i] == False]),Qid,child_par_dict, prop_Qid_par, prop_res)
                        #         ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                        # else:
                        #     if len(ans_list) == 1:
                        #         if sec_ques_sub_type==1:
                        #             ques = random.choice(sing_sub_annot_wh[prop_res])
                        #         else:
                        #             ques = sing_basic2indirect(random.choice(sing_sub_annot_wh[prop_res]),Qid,child_par_dict, prop_Qid_par, prop_res)
                        #         if prop_Qid_par != 'Q215627':
                        #             ques = ques.replace('Which OPP','What')
                        #         else:
                        #             ques = ques.replace('Which OPP','Who')
                        #     else:
                        #         if sec_ques_sub_type==1:
                        #             ques = random.choice(plu_sub_annot_wh[prop_res])
                        #         else:
                        #             ques = sing_basic2indirect(random.choice(plu_sub_annot_wh[prop_res]),Qid,child_par_dict, prop_Qid_par, prop_res)
                        #         if prop_Qid_par != 'Q215627':
                        #             ques = ques.replace('Which OPPS','What')
                        #         else:
                        #             ques = ques.replace('Which OPPS','Who')

                        if len(ans_list) == 1:
                            is_pphrase_ov = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in sing_sub_annot[prop_res]]
                            is_pphrase_ov_wh = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in sing_sub_annot_wh[prop_res]]

                            if False in is_pphrase_ov and sec_ques_sub_type==1:
                                ques = random.choice([sing_sub_annot[prop_res][i] for i in range(len(sing_sub_annot[prop_res])) if is_pphrase_ov[i] == False])
                                ques = ques.replace('OPP',child_par_dict_name_2[prop_Qid_par])
                            elif False in is_pphrase_ov_wh and sec_ques_sub_type==2:
                                ques = sing_basic2indirect(random.choice([sing_sub_annot_wh[prop_res][i] for i in range(len(sing_sub_annot_wh[prop_res])) if is_pphrase_ov_wh[i] == False]),Qid,child_par_dict, prop_Qid_par, prop_res)
                                ques = ques.replace('OPP',child_par_dict_name_2[prop_Qid_par])
                            else:
                                if sec_ques_sub_type==1:
                                    ques = random.choice(sing_sub_annot_wh[prop_res])
                                else:
                                    ques = sing_basic2indirect(random.choice(sing_sub_annot_wh[prop_res]),Qid,child_par_dict, prop_Qid_par, prop_res)

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

                            if False in is_pphrase_ov and sec_ques_sub_type==1:
                                ques = random.choice([plu_sub_annot[prop_res][i] for i in range(len(plu_sub_annot[prop_res])) if is_pphrase_ov[i] == False])
                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                            elif False in is_pphrase_ov_wh and sec_ques_sub_type==2:
                                ques = sing_basic2indirect(random.choice([plu_sub_annot[prop_res][i] for i in range(len(plu_sub_annot_wh[prop_res])) if is_pphrase_ov_wh[i] == False]),Qid,child_par_dict, prop_Qid_par, prop_res)
                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                            else:
                                if sec_ques_sub_type==1:
                                    ques = random.choice(plu_sub_annot_wh[prop_res])
                                else:
                                    ques = sing_basic2indirect(random.choice(plu_sub_annot_wh[prop_res]),Qid,child_par_dict, prop_Qid_par, prop_res)

                                if 'Which OPP' in ques:
                                    if prop_Qid_par != 'Q215627':
                                        ques = ques.replace('Which OPP','What')
                                    else:
                                        ques = ques.replace('Which OPP','Who')
                                else:
                                    ques = ques.replace('OPP',child_par_dict_name_2[prop_Qid_par])

                        ques = ques.replace('XXX',item_data[Qid])
                        # print 'Qid = %s' % Qid

                        
                    elif sec_ques_sub_type==3 or sec_ques_sub_type == 4: # Plural Indirect Question or Plural Basic Question
                        ans_list = copy.copy(dialog_list[-1]['entities'])
                        sub_list = ans_list # All the answers of previous question are now subjects of Plural Indirect question
                        # if len(sub_list) > args.plural_sub_ques_ans_thresh:
                        #     sub_list = np.random.choice(sub_list,args.plural_sub_ques_ans_thresh)
                        sub_list = list(sub_list)

                        filt_plu_dict = {}

                        for sub in sub_list:
                            for pid in [p for p in wikidata[sub] if p in prop_data.keys() and p in sub_90_map]:
                                for q in [item for item in wikidata[sub][pid] if item in wikidata and item in child_par_dict]:
                                    if sub in d and pid in d[sub]:
                                        if child_par_dict[q] not in d[sub][pid]:
                                            if sub not in filt_plu_dict:
                                                filt_plu_dict[sub] = {}
                                                filt_plu_dict[sub][pid] = [child_par_dict[q]]
                                            else:
                                                if pid not in filt_plu_dict[sub]:
                                                    filt_plu_dict[sub][pid] = [child_par_dict[q]]
                                                else:
                                                    filt_plu_dict[sub][pid].append(child_par_dict[q])
                                    else:
                                        if sub not in filt_plu_dict:
                                            filt_plu_dict[sub] = {}
                                            filt_plu_dict[sub][pid] = [child_par_dict[q]]
                                        else:
                                            if pid not in filt_plu_dict[sub]:
                                                filt_plu_dict[sub][pid] = [child_par_dict[q]]
                                            else:
                                                filt_plu_dict[sub][pid].append(child_par_dict[q])

                        sub_pid_list = [filt_plu_dict[sub].keys() for sub in filt_plu_dict]
                        if len(sub_pid_list)==0 or len(sub_pid_list) != len(sub_list):
                            prev_ques_failed = True
                            ques_type_id = 2 # No clarification question follows a failed question
                            continue

                        valid_pid_list = list(set(sub_pid_list[0]).intersection(*sub_pid_list))
                        pq_tuple = []

                        if len(valid_pid_list) > 0:
                            # print 'Valid pid for Plural question found'
                            # print valid_pid_list

                            for pid in valid_pid_list:
                                pid_obj_par_list = [filt_plu_dict[sub][pid] for sub in filt_plu_dict]
                                pid_valid_obj_par_list = list(set(pid_obj_par_list[0]).intersection(*pid_obj_par_list))

                                for q in pid_valid_obj_par_list:
                                    if q in sub_90_map[pid]:
                                        pq_tuple.append((pid,q))

                            # print pq_tuple
                            if len(pq_tuple)==0:
                                prev_ques_failed = True
                                ques_type_id = 2 # No clarification question follows a failed question
                                continue
                            pq_tuple = list(set(pq_tuple))
                            pq_tuple_choice = random.choice(pq_tuple)

                            prop_res = pq_tuple_choice[0]
                            prop_Qid_par = pq_tuple_choice[1]
                            
                            ans_list = [q for sub in sub_list for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]

                            # if len(set(ans_list)) == 1:
                            #     ans_list = list(set(ans_list))
                            # if sec_ques_sub_type == 3:
                            #     ques = sing_basic2indirect(random.choice(plu_sub_annot_wh[prop_res]),sub_list[0],child_par_dict,prop_Qid_par, prop_res, False)  
                            # else:
                            #     ques = sing_basic2plural_basic(random.choice(plu_sub_annot_wh[prop_res]),[item_data[q] for q in sub_list]) # to be modified: use appropiate dict

                            # if not is_par_rel_overlap(prop_Qid_par, prop_res):
                            #     ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                            #     # ques = '%s %s' % (ques,', '.join([item_data[q] for q in sub_list]))
                            # else:
                            #     if prop_Qid_par != 'Q215627':
                            #         ques = ques.replace('Which OPPS','What')
                            #     else:
                            #         ques = ques.replace('Which OPPS','Who')
                            is_pphrase_ov = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in plu_sub_annot_wh[prop_res]]
                            if False in is_pphrase_ov:
                                if sec_ques_sub_type == 3:
                                    ques = sing_basic2indirect(random.choice([plu_sub_annot_wh[prop_res][i] for i in range(len(plu_sub_annot_wh[prop_res])) if is_pphrase_ov[i] == False]),sub_list[0],child_par_dict,prop_Qid_par, prop_res, False)  
                                else:
                                    ques = sing_basic2plural_basic(random.choice([plu_sub_annot_wh[prop_res][i] for i in range(len(plu_sub_annot_wh[prop_res])) if is_pphrase_ov[i] == False]),[item_data[q] for q in sub_list]) # to be modified: use appropiate dict

                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                            else:
                                if sec_ques_sub_type == 3:
                                    ques = sing_basic2indirect(random.choice(plu_sub_annot_wh[prop_res]),sub_list[0],child_par_dict,prop_Qid_par, prop_res, False)  
                                else:
                                    ques = sing_basic2plural_basic(random.choice(plu_sub_annot_wh[prop_res]),[item_data[q] for q in sub_list]) # to be modified: use appropiate dict
                                if 'Which OPPS' in ques:
                                    if prop_Qid_par != 'Q215627':
                                        ques = ques.replace('Which OPPS','What')
                                    else:
                                        ques = ques.replace('Which OPPS','Who')
                                else:
                                    ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
   
                        else:
                            prev_ques_failed = True
                            ques_type_id = 2 # No clarification question follows a failed question
                            continue
                        
                    if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                        prev_ques_failed = True
                        ques_type_id = 2
                        continue

                    ans_list_full = copy.copy(ans_list)
                    ans_list_full_cp = copy.copy(ans_list_full)
                    # common code for sub. based (secondary) ques.
                    if len(ans_list) > args.plural_sub_ques_ans_thresh:
                        ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                        sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                        ans_list_t = [ans_list[i] for i in sort_index]
                        ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]

                    # print 'Ques: '+ ques                    

                    prev_ques_count[1] = prev_ques_count[0]
                    prev_ques_count[0] = len(ans_list)

                    if sec_ques_sub_type==1 or sec_ques_sub_type==2:
                        if args.update_counter:
                            if sec_ques_sub_type==1:
                                ent_c.update([Qid])
                            ent_c.update(ans_list)
                        ent_c_plus += (len(ans_list)+1)
                        tpl_set = [(Qid,prop_res,q) for q in ans_list]
                        if sec_ques_sub_type==1:
                            tpl_regex = ['(%s,%s,%s)' % (Qid,prop_res,'|'.join(['c(%s)'% x for x in [prop_Qid_par]]))]
                        else:
                            tpl_regex = []
                            for ent in dialog_list[-1]['entities']:
                                tpl_regex.extend(['(%s,%s,%s)' % (ent,prop_res,'|'.join(['c(%s)'% x for x in [prop_Qid_par]]))])
                            tpl_regex_true = ['(%s,%s,%s)' % (Qid,prop_res,'|'.join(['c(%s)'% x for x in [prop_Qid_par]]))]
                        if args.update_counter:
                            tpl_c.update(tpl_set)
                    elif sec_ques_sub_type==3 or sec_ques_sub_type==4:
                        if args.update_counter:
                            if sec_ques_sub_type==4:
                                ent_c.update(sub_list)
                            ent_c.update(ans_list)
                        ent_c_plus += (len(ans_list)+len(sub_list))
                        # tpl_set = [(sub,prop_res,q) for sub in sub_list for q in ans_list]
                        tpl_set = []
                        for sub in sub_list:
                            tpl_set.extend([q for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par])
                        if args.update_counter:
                            tpl_c.update(tpl_set)

                        tpl_regex = []
                        for sub in sub_list:
                            tpl_regex.extend(['(%s,%s,%s)' % (sub,prop_res,'|'.join(['c(%s)'% x for x in [prop_Qid_par]]))])

                        # if args.use_regex and len(set(tpl_regex).intersection(set(regex_ques_2))) > 0:
                        #     ques_type_id = 2
                        #     prev_ques_failed = True
                        #     continue

                    dict1 = {}
                    dict1['speaker'] = 'USER'
                    dict1['utterance'] = ques
                    dict1['ques_type_id'] = ques_type_id_save
                    # dict1['last_ques_type_id_save'] = last_ques_type_id_save
                    dict1['sec_ques_type'] = sec_ques_type
                    dict1['sec_ques_sub_type'] = sec_ques_sub_type
                    dict1['relations'] = [prop_res]
                    if sec_ques_sub_type==1 or sec_ques_sub_type==2: 
                        dict1['entities'] = [Qid]
                        #****************************************
                        dict1['Qid'] = Qid
                        dict1['prop_res'] = prop_res
                        dict1['prop_Qid_par'] = prop_Qid_par
                        dict1['len(ans_list) > 1'] = (True if len(ans_list)>1 else False)
                        if sec_ques_sub_type==1:
                            dict1['description'] = 'Simple Question|Single Entity'
                        else:
                            dict1['description'] = 'Simple Question|Single Entity|Indirect'
                        #****************************************
                    else:
                        dict1['entities'] = sub_list[:]
                        #****************************************
                        dict1['Qid'] = Qid
                        dict1['prop_res'] = prop_res
                        dict1['prop_Qid_par'] = prop_Qid_par
                        dict1['sub_list'] = sub_list
                        if sec_ques_sub_type==4:
                            dict1['description'] = 'Simple Question|Mult. Entity|Indirect'
                        else:
                            dict1['description'] = 'Simple Question|Mult. Entity'
                        #****************************************
                    dict1['signature'] = get_dict_signature(dict1.copy())
                    if dict1['signature'] in regex_ques_all:
                        ques_type_id = 2
                        prev_ques_failed = True
                        continue

                    dialog_list.append(dict1.copy())
                    

                    if ques_type_id != 3: # skip answer if the next question is a clarification question 
                        if sec_ques_sub_type in [1, 2]:
                            ans = ', '.join([item_data[q] for q in ans_list])
                        else:
                            if len(set(ans_list)) == 1:
                                ans = item_data[ans_list[0]]
                            elif len(set(ans_list)) != len(ans_list):
                                dict2 = {} 
                                for item in list(set(ans_list)):
                                    dict2[item] = [(idx+1) for idx in xrange(len(ans_list)) if ans_list[idx]==item]
                                ans = ', '.join(['%s for %s' % (item_data[item], ', '.join([inf_eng.ordinal(x) for x in dict2[item]])) for item in list(set(ans_list))])
                            else:
                                ans = ', '.join([item_data[q] for q in ans_list])
                        # print 'Ans: %s\n' % ans
                        dict1 = {}
                        dict1['speaker'] = 'SYSTEM'
                        dict1['utterance'] = ans
                        dict1['ans_list_full'] = ans_list_full_cp
                        if sec_ques_sub_type==1 or sec_ques_sub_type==2: 
                            dict1['entities'] = [q for q in ans_list]
                        elif sec_ques_sub_type==3 or sec_ques_sub_type==4:
                            dict1['entities'] = [q for q in ans_list]
                        dict1['active_set'] = tpl_regex[:]
                        json_plus += len(dict1['entities'])
                        dict1['signature'] = get_dict_signature(dict1.copy())
                        dialog_list.append(dict1.copy())
                        
                        

                    else:
                        # print 'Skipping answer next ques. is clarification ques.'
                        in_clar_ques = True

                elif sec_ques_type == 2: # Object based ques.
                    if Qid == last_Qid and sec_ques_sub_type == 1:
                        sec_ques_sub_type == 2 # switch to singular indirect if the Qid is same as last_Qid

                    if sec_ques_sub_type == 1 or sec_ques_sub_type == 2: # Basic Question (Singular) or Basic Question (Plural)
                        filt_dict = get_obj_ques_filt_dict(Qid) # filt_dict corr. to object based ques.
                        prop_list = [p for p in filt_dict.keys() if len(filt_dict[p])>0]
                        prop_list = list(set(prop_list) - set(rel_list)) # remove the ones already used
                        if len(prop_list) == 0:
                            update_d_filt_dict(Qid,filt_dict)
                            prev_ques_failed = True
                            continue
                        p_freq_dict = get_rel_dist(rel_c)
                        prop_list_prob = [p_freq_dict[p] for p in prop_list]
                        prop_list_prob_norm = [x*1.0/sum(prop_list_prob) for x in prop_list_prob]
                        prop_res = np.random.choice(prop_list, p=prop_list_prob_norm)
                        prop_Qid_par = random.choice(filt_dict[prop_res])

                        if last_ques_type_id_save == ques_type_id_save and prev_sec_ques_type[0] == sec_ques_type and prev_sec_ques_sub_type[0] == sec_ques_sub_type and prop_res == last_prop_res and prop_Qid_par == last_par:
                            prev_ques_failed = True
                            ques_type_id = 2 # No clarification question follows a failed question
                            # print d
                            continue

                        # if ques_type_id == 3: # next question is a clarification ques.
                        #     prev_prev_ans_list = ans_list

                        ans_list = [q for q in reverse_dict[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                        ans_list = list(set(ans_list))
                        # if sec_ques_sub_type == 1:
                        #     if not is_par_rel_overlap(prop_Qid_par, prop_res):
                        #         if len(ans_list) == 1:
                        #             ques = random.choice(sing_obj_annot[prop_res])
                        #         else:
                        #             ques = random.choice(plu_obj_annot[prop_res])
                        #     else:
                        #         if len(ans_list) == 1:
                        #             ques = random.choice(sing_obj_annot_wh[prop_res])
                        #         else:
                        #             ques = random.choice(plu_obj_annot_wh[prop_res])
                        # else:
                        #     if len(ans_list) == 1:
                        #         ques = sing_basic2indirect(random.choice(sing_obj_annot_wh[prop_res]),Qid,child_par_dict,prop_Qid_par, prop_res)
                        #     else:
                        #         ques = sing_basic2indirect(random.choice(plu_obj_annot_wh[prop_res]),Qid,child_par_dict,prop_Qid_par, prop_res)

                        # ques = ques.replace('YYY',item_data[Qid])

                        # if not is_par_rel_overlap(prop_Qid_par, prop_res):
                        #     if len(ans_list) == 1:
                        #         ques = ques.replace('SPP',child_par_dict_name_2[prop_Qid_par])
                        #     else:
                        #         ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                        # else:
                        #     if len(ans_list) == 1:
                        #         if prop_Qid_par != 'Q215627':
                        #             ques = ques.replace('Which SPP','What')
                        #         else:
                        #             ques = ques.replace('Which SPP','Who')
                        #     else:
                        #         if prop_Qid_par != 'Q215627':
                        #             ques = ques.replace('Which SPPS','What')
                        #         else:
                        #             ques = ques.replace('Which SPPS','Who')

                        # is_pphrase_ov = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in sing_obj_annot[prop_res]]
                        # if False in is_pphrase_ov and sec_ques_sub_type==1:
                        #     if len(ans_list) == 1:
                        #         ques = random.choice([sing_obj_annot[prop_res][i] for i in range(5) if is_pphrase_ov[i] == False])
                        #         ques = ques.replace('SPP',child_par_dict_name_2[prop_Qid_par])
                        #     else:
                        #         ques = random.choice([plu_obj_annot[prop_res][i] for i in range(5) if is_pphrase_ov[i] == False])
                        #         ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                        # elif False in is_pphrase_ov[:3] and sec_ques_sub_type==2:
                        #     if len(ans_list) == 1:
                        #         ques = sing_basic2indirect(random.choice([sing_obj_annot[prop_res][i] for i in range(3) if is_pphrase_ov[i] == False]),Qid,child_par_dict, prop_Qid_par, prop_res)
                        #         ques = ques.replace('SPP',child_par_dict_name_2[prop_Qid_par])
                        #     else:
                        #         ques = sing_basic2indirect(random.choice([plu_obj_annot[prop_res][i] for i in range(3) if is_pphrase_ov[i] == False]),Qid,child_par_dict, prop_Qid_par, prop_res)
                        #         ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                        # else:
                        #     if len(ans_list) == 1:
                        #         if sec_ques_sub_type==1:
                        #             ques = random.choice(sing_obj_annot_wh[prop_res])
                        #         else:
                        #             sing_basic2indirect(random.choice(sing_obj_annot_wh[prop_res]),Qid,child_par_dict, prop_Qid_par, prop_res)
                        #         if prop_Qid_par != 'Q215627':
                        #             ques = ques.replace('Which SPP','What')
                        #         else:
                        #             ques = ques.replace('Which SPP','Who')
                        #     else:
                        #         if sec_ques_sub_type==1:
                        #             ques = random.choice(plu_obj_annot_wh[prop_res])
                        #         else:
                        #             ques = sing_basic2indirect(random.choice(plu_obj_annot_wh[prop_res]),Qid,child_par_dict, prop_Qid_par, prop_res)
                        #         if prop_Qid_par != 'Q215627':
                        #             ques = ques.replace('Which SPPS','What')
                        #         else:
                        #             ques = ques.replace('Which SPPS','Who')

                        if len(ans_list) == 1:
                            is_pphrase_ov = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in sing_obj_annot[prop_res]]
                            is_pphrase_ov_wh = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in sing_obj_annot_wh[prop_res]]

                            if False in is_pphrase_ov and sec_ques_sub_type==1:
                                ques = random.choice([sing_obj_annot[prop_res][i] for i in range(len(sing_obj_annot[prop_res])) if is_pphrase_ov[i] == False])
                                ques = ques.replace('SPP',child_par_dict_name_2[prop_Qid_par])
                            elif False in is_pphrase_ov_wh and sec_ques_sub_type==2:
                                ques = sing_basic2indirect(random.choice([sing_obj_annot_wh[prop_res][i] for i in range(len(sing_obj_annot_wh[prop_res])) if is_pphrase_ov_wh[i] == False]),Qid,child_par_dict, prop_Qid_par, prop_res)
                                ques = ques.replace('SPP',child_par_dict_name_2[prop_Qid_par])
                            else:
                                if sec_ques_sub_type==1:
                                    ques = random.choice(sing_obj_annot_wh[prop_res])
                                else:
                                    ques = sing_basic2indirect(random.choice(sing_obj_annot_wh[prop_res]),Qid,child_par_dict, prop_Qid_par, prop_res)

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

                            if False in is_pphrase_ov and sec_ques_sub_type==1:
                                ques = random.choice([plu_obj_annot[prop_res][i] for i in range(len(plu_obj_annot[prop_res])) if is_pphrase_ov[i] == False])
                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                            elif False in is_pphrase_ov_wh and sec_ques_sub_type==2:
                                ques = sing_basic2indirect(random.choice([plu_obj_annot[prop_res][i] for i in range(len(plu_obj_annot_wh[prop_res])) if is_pphrase_ov_wh[i] == False]),Qid,child_par_dict, prop_Qid_par, prop_res)
                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                            else:
                                if sec_ques_sub_type==1:
                                    ques = random.choice(plu_obj_annot_wh[prop_res])
                                else:
                                    ques = sing_basic2indirect(random.choice(plu_obj_annot_wh[prop_res]),Qid,child_par_dict, prop_Qid_par, prop_res)
                                if 'Which SPP' in ques:
                                    if prop_Qid_par != 'Q215627':
                                        ques = ques.replace('Which SPP','What')
                                    else:
                                        ques = ques.replace('Which SPP','Who')
                                else:
                                    ques = ques.replace('SPP',child_par_dict_name_2[prop_Qid_par])

                        ques = ques.replace('YYY',item_data[Qid])

                        # print 'Qid = %s' % Qid                

                    elif sec_ques_sub_type == 3 or sec_ques_sub_type == 4: # Object based Plural (Indirect/Basic) question
                        ans_list = copy.copy(dialog_list[-1]['entities'])
                        sub_list = ans_list # All the answers of previous question are now subjects of Plural Indirect question
                        # if len(sub_list) > args.plural_sub_ques_ans_thresh:
                        #     sub_list = np.random.choice(sub_list,args.plural_sub_ques_ans_thresh)
                        sub_list = list(sub_list)

                        filt_plu_dict = {}

                        for sub in sub_list:
                            for pid in [p for p in reverse_dict[sub] if p in prop_data.keys() and p in obj_90_map]:
                                for q in [item for item in reverse_dict[sub][pid] if item in wikidata and item in child_par_dict]:
                                    if sub in d and pid in d[sub]:
                                        if child_par_dict[q] not in d[sub][pid]:
                                            if sub not in filt_plu_dict:
                                                filt_plu_dict[sub] = {}
                                                filt_plu_dict[sub][pid] = [child_par_dict[q]]
                                            else:
                                                if pid not in filt_plu_dict[sub]:
                                                    filt_plu_dict[sub][pid] = [child_par_dict[q]]
                                                else:
                                                    filt_plu_dict[sub][pid].append(child_par_dict[q])
                                    else:
                                        if sub not in filt_plu_dict:
                                            filt_plu_dict[sub] = {}
                                            filt_plu_dict[sub][pid] = [child_par_dict[q]]
                                        else:
                                            if pid not in filt_plu_dict[sub]:
                                                filt_plu_dict[sub][pid] = [child_par_dict[q]]
                                            else:
                                                filt_plu_dict[sub][pid].append(child_par_dict[q])

                        sub_pid_list = [filt_plu_dict[sub].keys() for sub in filt_plu_dict]
                        if len(sub_pid_list)==0 or len(sub_pid_list) != len(sub_list):
                            prev_ques_failed = True
                            ques_type_id = 2 # No clarification question follows a failed question
                            continue

                        valid_pid_list = list(set(sub_pid_list[0]).intersection(*sub_pid_list))
                        pq_tuple = []

                        if len(valid_pid_list) > 0:
                            # print 'Valid pid for Plural question found'
                            # print valid_pid_list

                            for pid in valid_pid_list:
                                pid_obj_par_list = [filt_plu_dict[sub][pid] for sub in filt_plu_dict]
                                pid_valid_obj_par_list = list(set(pid_obj_par_list[0]).intersection(*pid_obj_par_list))

                                for q in pid_valid_obj_par_list:
                                    if q in obj_90_map[pid]:
                                        pq_tuple.append((pid,q))

                            # print pq_tuple
                            if len(pq_tuple)==0:
                                prev_ques_failed = True
                                ques_type_id = 2 # No clarification question follows a failed question
                                continue
                            pq_tuple = list(set(pq_tuple)) # remove duplicates
                            pq_tuple_choice = random.choice(pq_tuple)

                            prop_res = pq_tuple_choice[0]
                            prop_Qid_par = pq_tuple_choice[1]
                            
                            ans_list = [q for sub in sub_list for q in reverse_dict[sub][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]

                            if len(set(ans_list)) == 1:
                                ans_list = list(set(ans_list))

                            # if sec_ques_sub_type == 3:
                            #     ques = sing_basic2indirect(random.choice(plu_obj_annot_wh[prop_res]),sub_list[0],child_par_dict,prop_Qid_par, prop_res, False)
                            # else:
                            #     ques = sing_basic2plural_basic(random.choice(plu_obj_annot_wh[prop_res]),[item_data[q] for q in sub_list])

                            # if not is_par_rel_overlap(prop_Qid_par, prop_res):
                            #     ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                            # else:
                            #     if prop_Qid_par != 'Q215627':
                            #         ques = ques.replace('Which SPPS','What')
                            #     else:
                            #         ques = ques.replace('Which SPPS','Who')

                            is_pphrase_ov = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in plu_obj_annot_wh[prop_res]]
                            if False in is_pphrase_ov:
                                if sec_ques_sub_type == 3:
                                    ques = sing_basic2indirect(random.choice([plu_obj_annot_wh[prop_res][i] for i in range(len(plu_obj_annot_wh[prop_res])) if is_pphrase_ov[i] == False]),sub_list[0],child_par_dict,prop_Qid_par, prop_res, False)  
                                else:
                                    ques = sing_basic2plural_basic(random.choice([plu_obj_annot_wh[prop_res][i] for i in range(len(plu_obj_annot_wh[prop_res])) if is_pphrase_ov[i] == False]),[item_data[q] for q in sub_list]) # to be modified: use appropiate dict

                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                            else:
                                if sec_ques_sub_type == 3:
                                    ques = sing_basic2indirect(random.choice(plu_obj_annot_wh[prop_res]),sub_list[0],child_par_dict,prop_Qid_par, prop_res, False)  
                                else:
                                    ques = sing_basic2plural_basic(random.choice(plu_obj_annot_wh[prop_res]),[item_data[q] for q in sub_list]) # to be modified: use appropiate dict
                                if 'Which SPPS' in ques:
                                    if prop_Qid_par != 'Q215627':
                                        ques = ques.replace('Which SPPS','What')
                                    else:
                                        ques = ques.replace('Which SPPS','Who')
                                else:
                                    ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                            # ques = '%s %s' % (ques,', '.join([item_data[q] for q in sub_list]))                            

                        else:
                            prev_ques_failed = True
                            ques_type_id = 2 # No clarification question follows a failed question
                            continue
                        
                    if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                        prev_ques_failed = True
                        ques_type_id = 2
                        continue

                    ans_list_full = copy.copy(ans_list)
                    ans_list_full_cp = copy.copy(ans_list_full)
                    # common code for object based ques.
                    if len(ans_list) > args.plural_obj_ques_ans_thresh:
                        ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                        sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                        ans_list_t = [ans_list[i] for i in sort_index]
                        ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]

                    # print 'Ques: '+ ques                    

                    prev_ques_count[1] = prev_ques_count[0]
                    prev_ques_count[0] = len(ans_list)

                    if sec_ques_sub_type == 1 or sec_ques_sub_type == 2:
                        if args.update_counter:
                            if sec_ques_sub_type==1:
                                ent_c.update([Qid])
                            ent_c.update(ans_list)
                        ent_c_plus += (len(ans_list)+1)
                        tpl_set = [(q,prop_res,Qid) for q in ans_list]
                        if args.update_counter:
                            tpl_c.update(tpl_set)
                        if sec_ques_sub_type == 1:
                            tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [prop_Qid_par]]),prop_res,Qid)]
                        else:
                            tpl_regex = []
                            for ent in dialog_list[-1]['entities']:
                                tpl_regex.extend(['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [prop_Qid_par]]),prop_res,ent)])
                            tpl_regex_true = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [prop_Qid_par]]),prop_res,Qid)] # save for output in clari. ques.

                    elif sec_ques_sub_type == 3 or sec_ques_sub_type == 4:
                        if args.update_counter:
                            if sec_ques_sub_type==4:
                                ent_c.update(sub_list)
                            ent_c.update(ans_list)
                        ent_c_plus += (len(ans_list)+len(sub_list))
                        tpl_set = []
                        for sub in sub_list:
                            tpl_set.extend([(q, prop_res, sub) for q in reverse_dict[sub][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par])
                        
                        tpl_regex = []
                        for sub in sub_list:
                            tpl_regex.extend(['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [prop_Qid_par]]),prop_res,sub)])
                        if args.update_counter:
                            tpl_c.update(tpl_set)

                        # if args.use_regex and len(set(tpl_regex).intersection(set(regex_ques_2))) > 0:
                        #     ques_type_id = 2
                        #     prev_ques_failed = True
                        #     continue

                    dict1 = {}
                    dict1['speaker'] = 'USER'
                    dict1['utterance'] = ques
                    dict1['ques_type_id'] = ques_type_id_save
                    # dict1['last_ques_type_id_save'] = last_ques_type_id_save
                    dict1['sec_ques_type'] = sec_ques_type
                    dict1['sec_ques_sub_type'] = sec_ques_sub_type
                    dict1['relations'] = [prop_res]
                    if sec_ques_sub_type==1 or sec_ques_sub_type==2: 
                        dict1['entities'] = [Qid]
                        #****************************************
                        dict1['Qid'] = Qid
                        dict1['prop_res'] = prop_res
                        dict1['prop_Qid_par'] = prop_Qid_par
                        dict1['len(ans_list) > 1'] = (True if len(ans_list)>1 else False)

                        if sec_ques_sub_type==1:
                            dict1['description'] = 'Simple Question|Single Entity'
                        else:
                            dict1['description'] = 'Simple Question|Single Entity|Indirect'
                        #****************************************
                    else:
                        dict1['entities'] = sub_list[:]
                        #****************************************
                        dict1['Qid'] = Qid
                        dict1['prop_res'] = prop_res
                        dict1['prop_Qid_par'] = prop_Qid_par
                        dict1['sub_list'] = sub_list

                        if sec_ques_sub_type==4:
                            dict1['description'] = 'Simple Question|Mult. Entity|Indirect'
                        else:
                            dict1['description'] = 'Simple Question|Mult. Entity'
                        #****************************************
                    dict1['signature'] = get_dict_signature(dict1.copy())
                    if dict1['signature'] in regex_ques_all:
                        ques_type_id = 2
                        prev_ques_failed = True
                        continue
                    dialog_list.append(dict1.copy())
                    

                    if ques_type_id != 3: # skip answer if the next question is a clarification question 
                        if sec_ques_sub_type in [1, 2]:
                            ans = ', '.join([item_data[q] for q in ans_list])
                        else:
                            if len(set(ans_list)) == 1:
                                ans = item_data[ans_list[0]]
                            elif len(set(ans_list)) != len(ans_list):
                                dict2 = {} 
                                for item in list(set(ans_list)):
                                    dict2[item] = [(idx+1) for idx in xrange(len(ans_list)) if ans_list[idx]==item]
                                ans = ', '.join(['%s for %s' % (item_data[item], ', '.join([inf_eng.ordinal(x) for x in dict2[item]])) for item in list(set(ans_list))])
                            else:
                                ans = ', '.join([item_data[q] for q in ans_list])
                        # print 'Ans: %s\n' % ans
                        dict1 = {}
                        dict1['speaker'] = 'SYSTEM'
                        dict1['utterance'] = ans
                        dict1['ans_list_full'] = ans_list_full_cp

                        if sec_ques_sub_type==1 or sec_ques_sub_type==2: 
                            dict1['entities'] = [q for q in ans_list]
                        elif sec_ques_sub_type==3 or sec_ques_sub_type==4:
                            dict1['entities'] = [q for q in ans_list]
                        dict1['active_set'] = tpl_regex[:]
                        json_plus += len(dict1['entities'])
                        dict1['signature'] = get_dict_signature(dict1.copy())
                        dialog_list.append(dict1.copy())
                        
                        
                    else:
                        # print 'Skipping answer next ques. is clarification ques.'
                        in_clar_ques = True



            elif ques_type_id==3: #clarification ques. NO new question, just clarification of previous question

                try:
                    assert 'ques_type_id' in dialog_list[-1] and 'sec_ques_sub_type' in dialog_list[-1] and dialog_list[-1]['ques_type_id'] == 2 and dialog_list[-1]['sec_ques_sub_type'] == 2 and len(set(dialog_list[-2]['entities']))>1
                except:
                    # dialog_list = dialog_list[:-1]
                    ques_type_id = 2
                    prev_ques_failed = True
                    continue
                sec_ques_type = sec_ques_sub_type = 0 # Direct ques. is not a secondary ques.
                prev_ques_count[1] = prev_ques_count[0]
                prev_ques_count[0] = 0 # clarification ques. dummy answer count = 0

                # assert (len(prev_prev_ans_list) >= 1) # previous to previous question should have multiple answers (in MOST cases: genuine clarification ques.)
                # print 'No. of answers of previous to previous ques. = %d' % len(prev_prev_ans_list)

                # if not 'true_label' in globals():
                #     true_label = random.choice(prev_prev_ans_list) # true label which we refer to indirectly in the singular indirect ques. (previous question) 
                #     print true_label
                true_label = Qid
                if 'entities' in dialog_list[-2]:
                    prev_prev_ans_list = dialog_list[-2]['entities']
                else:
                    prev_prev_ans_list = []
                
                try:
                    assert (true_label in prev_prev_ans_list)
                    pred_label = random.choice(prev_prev_ans_list) # randomly guess an entity from the answer list as true label
                except:
                    pred_label = true_label # In case clarification question follows a direct question, there is only one option of pred_label i.e. true_label

                # print 'Ques (System): Did you mean %s ?' % item_data[pred_label] # Actual clarification question
                dict1 = {}
                dict1['speaker'] = 'SYSTEM'
                dict1['utterance'] = 'Did you mean %s ?' % item_data[pred_label]
                dict1['ques_type_id'] = ques_type_id_save
                # dict1['last_ques_type_id_save'] = last_ques_type_id_save
                dict1['active_set'] = tpl_regex[:] # see if last regex getting reflected
                dict1['ans_list_full'] = prev_prev_ans_list
                dict1['entities'] = [pred_label]
                dict1['relations'] = []
                dict1['description'] = 'Clarification for simple ques.'
                dict1['signature'] = get_dict_signature(dict1.copy())
                dialog_list.append(dict1.copy())
                

                if true_label == pred_label:
                    in_clar_ques = False
                    # print 'Ans (to System): Yes'
                    dict1 = {}
                    dict1['speaker'] = 'USER'
                    dict1['utterance'] = 'Yes'
                    dialog_list.append(dict1.copy())
                    
                    # print 'true label = %s, pred_label = %s' % (true_label,pred_label)
                    ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # Next question is a secondary question
                    del true_label # delete the variable from workspace in order to avoid conflict with future clarification ques.
                    # print 'Ans : %s' % ', '.join([item_data[q] for q in ans_list])
                    dict1 = {}
                    dict1['speaker'] = 'SYSTEM'
                    ans_list_full = ans_list_full_cp

                    if len(ans_list) > args.plural_obj_ques_ans_thresh:
                        ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                        sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                        ans_list_t = [ans_list[i] for i in sort_index]
                        ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]

                    ans_list = list(set(ans_list))
                    dict1['utterance'] = ', '.join([item_data[q] for q in ans_list])
                    dict1['entities'] = ans_list[:]
                    dict1['active_set'] = tpl_regex_true[:]
                    dict1['ans_list_full'] = ans_list_full
                    json_plus += len(dict1['entities'])
                    dict1['signature'] = get_dict_signature(dict1.copy())
                    dialog_list.append(dict1.copy())
                    
                    
                else:
                    # print 'Ans (to System): No\n'
                    in_clar_ques = False
                    dict1 = {}
                    dict1['speaker'] = 'USER'
                    dict1['utterance'] = 'No, I meant %s. Could you tell me the answer for that?' % item_data[true_label]
                    dict1['entities'] = [true_label]
                    dialog_list.append(dict1.copy())
                    
                    # print 'true label = %s, pred_label = %s' % (true_label,pred_label)
                    ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # Next question is again a clarification question (as response is not positive)
                    # prev_prev_ans_list.remove(pred_label) # Remove the wrongly guessed label from the answer list; this way we will eventualy guess the 'true_label'
                    
                    dict1 = {}
                    dict1['speaker'] = 'SYSTEM'

                    ans_list_full = ans_list_full_cp

                    if len(ans_list) > args.plural_obj_ques_ans_thresh:
                        ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                        sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                        ans_list_t = [ans_list[i] for i in sort_index]
                        ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                    ans_list = list(set(ans_list))
                    dict1['utterance'] = ', '.join([item_data[q] for q in ans_list])
                    dict1['entities'] = ans_list[:]
                    dict1['active_set'] = tpl_regex_true[:]
                    dict1['ans_list_full'] = ans_list_full
                    json_plus += len(dict1['entities'])
                    dict1['signature'] = get_dict_signature(dict1.copy())
                    dialog_list.append(dict1.copy())
                    
                    
            elif ques_type_id == 4: # Set based question
                sec_ques_type = sec_ques_sub_type = 0 # Set based ques. is not a secondary ques

                if len(dialog_list)>=2 and 'ques_type_id' in dialog_list[-2] and dialog_list[-2]['ques_type_id'] == 2 and 'sec_ques_sub_type' in dialog_list[-2] and dialog_list[-2]['sec_ques_sub_type'] in [1, 2]:
                    is_inc = np.random.choice([0, 1],p=[(1-args.p_inc_set), args.p_inc_set])
                else:
                    is_inc = 0

                if is_inc:
                    Qid = dialog_list[-2]['Qid'] # use Qid of last iteration
                else:
                    ent_list = []
                    for i in range(len(dialog_list)):
                        if 'entities' in dialog_list[i]:
                            ent_list.extend(dialog_list[i]['entities'])
                    Qid = random.choice(ent_list)

                if not is_inc:
                    is_sub = np.random.choice([0, 1])
                    if Qid not in reverse_dict:
                        is_sub = 1
                else:
                    if dialog_list[-2]['sec_ques_type'] == 1:
                        is_sub = 1
                    else:
                        is_sub = 0

                set_sub_oper = np.random.choice(np.array([1, 2]),p = [(1 - args.p_not), args.p_not])
                set_op_dict = {1:'OR',2:'AND',3:'DIFF'}
                if set_sub_oper == 1:
                    set_op_choice = random.choice(set_op_dict.keys())
                else:
                    set_op_choice = random.choice([1, 2])

                if not is_inc:
                    if is_sub:
                        filt_dict = get_sub_ques_filt_dict(Qid)
                        pq_tuple = [(p,q) for p in filt_dict.keys() for q in filt_dict[p] if p in sub_90_map and q in set(sub_90_map[p])]
                        pq_tuple = list(set(pq_tuple))
                        pq_tuple_fanout = [sum([wikidata_fanout_dict[qid] for qid in wikidata[Qid][p] if qid in child_par_dict and child_par_dict[qid]==q]) for (p,q) in pq_tuple]
                        
                        if sum(pq_tuple_fanout)==0: #blacklist the combination of Qid, pid, filt_dict[Qid][pid]
                            update_d_filt_dict(Qid,filt_dict)
                            prev_ques_failed = True
                            ques_type_id = 2
                            continue

                        pq_tuple_fanout_norm = [x*1.0/sum(pq_tuple_fanout) for x in pq_tuple_fanout]
                        pq_tuple_choice = pq_tuple[np.random.choice(len(pq_tuple), p=pq_tuple_fanout_norm)]
                        prop_res = pq_tuple_choice[0]
                        prop_Qid_par = pq_tuple_choice[1]
                        ans_list_A = list(set(wikidata[Qid][prop_res]) & child_par_dict_key_set & set(par_child_dict[prop_Qid_par]))
                    else:
                        filt_dict = get_obj_ques_filt_dict(Qid) # filt_dict corr. to object based ques.
                        pq_tuple = [(p,q) for p in filt_dict.keys() for q in filt_dict[p] if p in obj_90_map and q in set(obj_90_map[p])]
                        pq_tuple = list(set(pq_tuple))
                        pq_tuple_fanout = [sum([wikidata_fanout_dict[qid] for qid in reverse_dict[Qid][p] if qid in child_par_dict and child_par_dict[qid]==q]) for (p,q) in pq_tuple]
                        if sum(pq_tuple_fanout)==0:
                            update_d_filt_dict(Qid,filt_dict)
                            prev_ques_failed = True
                            ques_type_id = 2
                            continue

                        pq_tuple_fanout_norm = [x*1.0/sum(pq_tuple_fanout) for x in pq_tuple_fanout]
                        pq_tuple_choice = pq_tuple[np.random.choice(len(pq_tuple), p=pq_tuple_fanout_norm)]
                        prop_res = pq_tuple_choice[0]
                        prop_Qid_par = pq_tuple_choice[1]
                        ans_list_A = list(set(reverse_dict[Qid][prop_res]) & child_par_dict_key_set & set(par_child_dict[prop_Qid_par]))
                else:
                    prop_res = copy.copy(dialog_list[-2]['prop_res'])
                    prop_Qid_par = copy.copy(dialog_list[-2]['prop_Qid_par'])
                    ans_list_A = copy.copy(dialog_list[-1]['ans_list_full'])

                # if prop_Qid_par in wikidata_type_dict and prop_res in wikidata_type_dict[prop_Qid_par] and prop_res in obj_90_map:
                #     is_sub = False
                # elif prop_Qid_par in wikidata_type_rev_dict and prop_res in wikidata_type_rev_dict[prop_Qid_par] and prop_res in sub_90_map:
                #     is_sub = True
                # elif prev_sec_ques_type[0] == 1 and prop_res in sub_90_map:
                #     is_sub = True
                # else:
                #     prev_ques_failed = True
                #     ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # No clarification question follows a failed question
                #     continue

                Qid_1 = Qid # save Qid of first operand of set operation
                prop_res_1 = prop_res # save pid of first operand of set operation

                dict1 = {}
                dict1['prop_res_1'] = prop_res_1
                dict1['Qid_1'] = Qid_1

                if is_sub: # prev. secondary ques. is subject-based
                    obj_par = prop_Qid_par
                    # valid_obj = [q for q in reverse_dict if q in child_par_dict and child_par_dict[q]==obj_par]
                    valid_obj = list(set(reverse_dict.keys()) & set(child_par_dict.keys()) & set(par_child_dict[obj_par]))
                    if len(valid_obj) > args.set_obj_thresh:
                        valid_obj = random.sample(valid_obj,args.set_obj_thresh)

                    ps_tuple = [(p,s) for q in valid_obj for p in reverse_dict[q] for s in reverse_dict[q][p] if s in wikidata and p in wikidata[s] and p in sub_90_map and prop_Qid_par in sub_90_map[p]]
                    ps_tuple = [(p,s) for (p,s) in ps_tuple if s!=Qid]

                    try:
                        assert prop_res in [x[0] for x in ps_tuple]
                    except:
                        prev_ques_failed = True
                        ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # No clarification question follows a failed question
                        continue
                    # Remove the combination of (p,s) used in previous question
                    # if prev_sec_ques_sub_type == 1 or prev_sec_ques_sub_type == 2: # Direct or Singular Indirect question
                    #     if (prop_res,Qid) in ps_tuple:
                    #         ps_tuple.remove((prop_res,Qid))
                    # elif prev_sec_ques_sub_type == 3 or prev_sec_ques_sub_type == 4: # Plural indirect/basic question
                    #     for sub in sub_list:
                    #         if (prop_res,sub) in ps_tuple:
                    #             ps_tuple.remove((prop_res,sub))

                    if len(ps_tuple) > args.ps_tuple_thresh: # randomly sample args.ps_tuple_thresh # of entries from list if greater than threshold
                        ps_tuple = random.sample(ps_tuple,args.ps_tuple_thresh)

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
                        ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # No clarification question follows a failed question
                        continue

                    ps_tuple_ans_len_norm = [x*1.0/ps_tuple_ans_len_sum for x in ps_tuple_ans_len] # prob. distribution of number of answers of set operation

                    if prop_res_1 in [x[0] for x in ps_tuple] and random.random()>0.5:
                        prop_res = prop_res_1
                        Qid = random.choice([x[1] for x in ps_tuple if x[0]==prop_res])
                    else:
                        ps_tuple_choice = ps_tuple[np.random.choice(len(ps_tuple), p = ps_tuple_ans_len_norm)]
                        prop_res = ps_tuple_choice[0]
                        Qid = ps_tuple_choice[1] # new subject

                    if prop_res == prop_res_1: # pid remains unchanged
                        if set_sub_oper == 1:
                            ques_1 = random.choice(plu_sub_annot_wh[prop_res_1])
                        else:
                            ques_1 = random.choice(neg_plu_sub_annot_wh[prop_res_1])                      
                        if is_inc == 0:
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
                        else:
                            if set_op_choice == 1: # union
                                ques = 'Or %s?' % item_data[Qid]
                            elif set_op_choice == 2: # intersection
                                ques = 'And also %s' % item_data[Qid]
                            else: # difference
                                ques = 'But not %s' % item_data[Qid]

                        if args.update_counter:
                            ent_c.update([Qid])
                            ent_c.update([Qid_1])
                        ent_c_plus += 2

                    else: # pid is different
                        is_inc = 0
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
                        if args.update_counter:
                            ent_c.update([Qid])
                            ent_c.update([Qid_1])
                        ent_c_plus += 2

                    ans_list_B = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                    
                    # tpl_regex = ['(%s,%s,%s)' % (Qid,prop_res,'|'.join(['c(%s)'% x for x in [prop_Qid_par]]))]

                else: # prev. secondary ques. is object-based
                    sub_par = prop_Qid_par
                    valid_sub = par_child_dict[sub_par]
                    if len(valid_sub) > args.set_obj_thresh:
                        valid_sub = random.sample(valid_sub,args.set_obj_thresh)

                    ps_tuple = [(p,s) for q in valid_sub for p in wikidata[q] for s in wikidata[q][p] if s in reverse_dict and p in reverse_dict[s] and p in obj_90_map and prop_Qid_par in obj_90_map[p]]
                    ps_tuple = [(p,s) for (p,s) in ps_tuple if s!=Qid]
                    try:
                        assert prop_res in [x[0] for x in ps_tuple]
                    except:
                        prev_ques_failed = True
                        ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # No clarification question follows a failed question
                        continue
                    # Remove the combination of (p,s) used in previous question
                    # if prev_sec_ques_sub_type == 1 or prev_sec_ques_sub_type == 2: # Direct or Singular Indirect question
                    #     if (prop_res,Qid) in ps_tuple:
                    #         ps_tuple.remove((prop_res,Qid))
                    # elif prev_sec_ques_sub_type == 3 or prev_sec_ques_sub_type == 4: # Plural indirect or basic question
                    #     for sub in sub_list:
                    #         if (prop_res,sub) in ps_tuple:
                    #             ps_tuple.remove((prop_res,sub))

                    if len(ps_tuple) > args.ps_tuple_thresh: # randomly sample args.ps_tuple_thresh # of entries from list if greater than threshold
                        ps_tuple = random.sample(ps_tuple,args.ps_tuple_thresh)

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
                        ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # No clarification question follows a failed question
                        continue

                    ps_tuple_ans_len_norm = [x*1.0/ps_tuple_ans_len_sum for x in ps_tuple_ans_len] # prob. distribution of number of answers of set operation

                    if prop_res_1 in [x[0] for x in ps_tuple] and random.random()>0.5:
                        prop_res = prop_res_1
                        Qid = random.choice([x[1] for x in ps_tuple if x[0]==prop_res])
                    else:
                        ps_tuple_choice = ps_tuple[np.random.choice(len(ps_tuple), p = ps_tuple_ans_len_norm)]
                        prop_res = ps_tuple_choice[0]
                        Qid = ps_tuple_choice[1] # new subject

                    if prop_res == prop_res_1: # pid remains unchanged
                        if set_sub_oper == 1:
                            ques_1 = random.choice(plu_obj_annot_wh[prop_res_1])
                        else:
                            ques_1 = random.choice(neg_plu_obj_annot_wh[prop_res_1])
                        if is_inc == 0:
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
                        else:
                            if set_op_choice == 1: # union
                                ques = 'Or %s?' % item_data[Qid]
                            elif set_op_choice == 2: # intersection
                                ques = 'And also %s' % item_data[Qid]
                            else: # difference
                                ques = 'But not %s' % item_data[Qid]

                        if args.update_counter:
                            ent_c.update([Qid])
                            ent_c.update([Qid_1])
                        ent_c_plus += 2
                    else: # pid is different
                        is_inc = 0
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
                        if args.update_counter:
                            ent_c.update([Qid])
                            ent_c.update([Qid_1])
                        ent_c_plus += 2

                    ans_list_B = [q for q in reverse_dict[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                    
                    
                    # tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [prop_Qid_par]]),prop_res,Qid)]

                ans_list = [] # Result of set operation

                if set_op_choice == 1:
                    ans_list = list(set(ans_list_A).union(ans_list_B)) # UNION
                elif set_op_choice == 2:
                    ans_list = list(set(ans_list_A).intersection(ans_list_B)) # INTERSECTION
                elif set_op_choice == 3:
                    ans_list = list(set(ans_list_A).difference(ans_list_B)) # DIFFERENCE

                if set_op_choice == 3 and len(set(ans_list_A).intersection(ans_list_B))==0:
                    prev_ques_failed = True
                    ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # No clarification question follows a failed question
                    continue

                if is_sub:
                    tpl_set = [(Qid_1,prop_res_1,q) for q in ans_list] + [(Qid,prop_res,q) for q in ans_list]
                else:
                    tpl_set = [(q,prop_res_1,Qid_1) for q in ans_list] + [(q,prop_res,Qid) for q in ans_list]

                if args.update_counter:
                    tpl_c.update(tpl_set)

                ans_list = list(set(ans_list))
                ans_list_full = copy.copy(ans_list)
                ans_list_full_cp = copy.copy(ans_list_full)

                prev_ques_count[1] = prev_ques_count[0]
                prev_ques_count[0] = len(ans_list)

                ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # ques type_id of next question (Secondary)

                # print 'Ques: '+ ques

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

                # if args.use_regex and len(set(tpl_regex).intersection(set(regex_ques_4))) > 0:
                #     prev_ques_failed = True
                #     continue

                if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                    prev_ques_failed = True
                    ques_type_id = 2
                    continue

                # dict1 = {}
                dict1['speaker'] = 'USER'
                dict1['utterance'] = ques
                dict1['ques_type_id'] = ques_type_id_save
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
                # dict1['prop_res_1'] = prop_res_1
                dict1['Qid'] = Qid
                # dict1['Qid_1'] = Qid_1
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
                if dict1['signature'] in regex_ques_all:
                    ques_type_id = 2
                    prev_ques_failed = True
                    continue
                dialog_list.append(dict1.copy())

                if len(ans_list) > 0:
                    if len(ans_list) > args.set_ques_ans_thresh:
                        # print 'Ques (to System): The answer count is %d. Do you want to see all possibilities?' % len(ans_list)
                        # dict1 = {}
                        # dict1['speaker'] = 'SYSTEM'
                        # dict1['utterance'] = 'The answer count is %d. Do you want to see all possibilities?' % len(ans_list)
                        # dialog_list.append(dict1.copy())
                        

                        # # print 'Ans (System): No, show only a few of them'
                        # dict1 = {}
                        # dict1['speaker'] = 'USER'
                        # dict1['utterance'] = 'No, show only a few of them'
                        # dialog_list.append(dict1.copy())
                        

                        ans_list = random.sample(ans_list,args.set_ques_ans_thresh)
                        ans = 'Some of them are ' + ', '.join([item_data[q] for q in ans_list])
                    else:
                        ans = ', '.join([item_data[q] for q in ans_list])
                    # print 'Ans: %s\n' % ans
                    dict1 = {}
                    dict1['speaker'] = 'SYSTEM'
                    dict1['utterance'] = ans
                    dict1['ans_list_full'] = ans_list_full_cp
                    dict1['entities'] = ans_list[:]
                    dict1['active_set'] = tpl_regex[:]
                    json_plus += len(dict1['entities'])
                    # dict1['ans_list_A'] = ans_list_A
                    # dict1['ans_list_B'] = ans_list_B
                    dict1['signature'] = get_dict_signature(dict1.copy())
                    dialog_list.append(dict1.copy())
                    
                    
                else:
                    # print 'Ans: None'
                    dict1 = {}
                    dict1['speaker'] = 'SYSTEM'
                    dict1['utterance'] = 'None'
                    dict1['entities'] = ans_list[:]
                    dict1['active_set'] = tpl_regex[:]
                    dict1['ans_list_full'] = ans_list_full_cp
                    json_plus += len(dict1['entities'])
                    dict1['signature'] = get_dict_signature(dict1.copy())
                    dialog_list.append(dict1.copy())
                    
                    
                if args.update_counter:
                    ent_c.update(ans_list)
                ent_c_plus += (len(ans_list))
             

            elif ques_type_id == 5: # Boolean (secondary) question
                # print 'enter boolean ques.'
                sec_ques_type = sec_ques_sub_type = 0 # Set based ques. is not a secondary ques.
                ans_list = copy.copy(dialog_list[-1]['entities'])

                if last_ques_type_id_save != 5:
                    if len(ans_list) == 1:
                        prob_list = [args.p_bool_sing_dir, args.p_bool_sing_indir1, args.p_bool_sing_indir2, args.p_bool_plu_dir, args.p_bool_plu_indir1]
                        bool_ques_type = np.random.choice([1, 2, 3, 4, 5], p=[x*1.0/sum(prob_list) for x in prob_list])
                        Qid = ans_list[0]
                    elif len(ans_list) > 1:
                        bool_ques_type = 6 # p_bool_plu_indir2
                    else:
                        prev_ques_failed = True
                        ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23])
                        continue
                else:
                    prob_list = [args.p_bool_sing_dir, args.p_bool_plu_dir]
                    bool_ques_type = np.random.choice([1, 4], p=[x*1.0/sum(prob_list) for x in prob_list])
                    Qid = random.choice(list(set(prev_Qid) - set([last_Qid])))

                # print'bool_ques_type = %d' % bool_ques_type

                if bool_ques_type == 1 or bool_ques_type == 2 or bool_ques_type == 4 or bool_ques_type == 5:
                    filt_dict = get_sub_ques_filt_dict(Qid)
                    pq_tuple = [(p,q) for p in filt_dict.keys() for q in filt_dict[p] if p in sub_90_map and p in sing_sub_annot_wh and q in set(sub_90_map[p])]
                    pq_tuple = list(set(pq_tuple))
                    pq_tuple_fanout = [sum([wikidata_fanout_dict[qid] for qid in wikidata[Qid][p] if qid in child_par_dict and child_par_dict[qid]==q]) for (p,q) in pq_tuple]
                    if sum(pq_tuple_fanout)==0:
                        update_d_filt_dict(Qid,filt_dict)
                        prev_ques_failed = True
                        ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # No clarification question follows a failed question
                        # print d
                        # print 'boolean ques. failed'
                        continue

                    pq_tuple_fanout_norm = [x*1.0/sum(pq_tuple_fanout) for x in pq_tuple_fanout]

                    pq_tuple_choice = pq_tuple[np.random.choice(len(pq_tuple), p=pq_tuple_fanout_norm)]
                    prop_res = pq_tuple_choice[0]
                    prop_Qid_par = pq_tuple_choice[1]

                    pos_list = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par and q != Qid]
                    comp_list = list(set(par_child_dict[prop_Qid_par]) - set([Qid]))
                    if len(comp_list) > args.set_ques_ans_thresh:
                        comp_list = random.sample(comp_list, args.set_ques_ans_thresh)
                    obj = random.choice(pos_list) if (random.random()>0.5) else random.choice(comp_list)

                    if bool_ques_type == 4 or bool_ques_type == 5:
                        try:
                            obj2 = random.choice(list(set(pos_list) - set([obj]))) if (random.random()>0.5) else random.choice(list(set(comp_list) - set([obj])))
                        except:
                            bool_ques_type = random.choice([1, 2])

                    if bool_ques_type == 1:
                        ques = booleanise_ques(random.choice(sing_sub_annot_wh[prop_res]),obj)
                        ques = ques.replace('XXX',item_data[Qid])
                        if args.update_counter:
                            ent_c.update([Qid])
                            ent_c.update([obj])
                        ent_c_plus += 2
                        tpl_set = [(Qid,prop_res,obj)]
                        if args.update_counter:
                            tpl_c.update(tpl_set)
                    elif bool_ques_type == 2:
                        ques = booleanise_ques(sing_basic2indirect(random.choice(sing_sub_annot_wh[prop_res]),Qid,child_par_dict,prop_Qid_par, prop_res),obj)
                        ques = ques.replace('XXX',item_data[Qid])
                        if args.update_counter:
                            ent_c.update([Qid])
                            ent_c.update([obj])
                        ent_c_plus += 2
                        tpl_set = [(Qid,prop_res,obj)]
                        if args.update_counter:
                            tpl_c.update(tpl_set)
                    elif bool_ques_type == 4: # to be modified: plural form of ans. ques. required
                        ques = booleanise_ques(random.choice(sing_obj_annot_wh[prop_res]),Qid)
                        # print 'obj = %s, obj2 = %s, phrase = %s' % (obj, obj2, get_multi_pphrase([item_data[obj], item_data[obj2]]))
                        # sys.exit()
                        ques = ques.replace('YYY',get_multi_pphrase([item_data[obj], item_data[obj2]]))
                        if args.update_counter:
                            ent_c.update([Qid])
                            ent_c.update([obj])
                            ent_c.update([obj2])
                        ent_c_plus += 3
                        tpl_set = [(Qid,prop_res,obj), (Qid,prop_res,obj2)]
                        if args.update_counter:
                            tpl_c.update(tpl_set)
                    elif bool_ques_type == 5:
                        ques = booleanise_ques_custom(random.choice(sing_obj_annot_wh[prop_res]),Qid)
                        # print 'obj = %s, obj2 = %s, phrase = %s' % (obj, obj2, get_multi_pphrase([item_data[obj], item_data[obj2]]))
                        # sys.exit()
                        ques = ques.replace('YYY',get_multi_pphrase([item_data[obj], item_data[obj2]]))
                        if args.update_counter:
                            ent_c.update([Qid])
                            ent_c.update([obj])
                            ent_c.update([obj2])
                        ent_c_plus += 3
                        tpl_set = [(Qid,prop_res,obj), (Qid,prop_res,obj2)]
                        if args.update_counter:
                            tpl_c.update(tpl_set)

                    tpl_regex = tpl_set
                    # print 'Qid = %s' % Qid
                    # print 'Ques: %s' % ques
                    if len(tpl_regex) > 0 and (type(tpl_regex[0]) == type(list()) or type(tpl_regex[0]) == type(tuple())):
                        tpl_regex = ['(%s,%s,%s)' % (x[0],x[1],x[2]) for x in tpl_regex]
                            
                    # if args.use_regex and len(set(tpl_regex).intersection(set(regex_ques_5))) > 0:
                    #     ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23])
                    #     prev_ques_failed = True
                    #     continue

                    dict1 = {}
                    dict1['speaker'] = 'USER'
                    dict1['utterance'] = ques
                    dict1['ques_type_id'] = ques_type_id_save
                    # dict1['last_ques_type_id_save'] = last_ques_type_id_save
                    dict1['bool_ques_type'] = bool_ques_type
                    dict1['relations'] = [prop_res]

                    #****************************************************************
                    if bool_ques_type in [1,2]:
                        dict1['obj'] = obj
                        dict1['Qid'] = Qid
                        dict1['prop_res'] = prop_res
                        dict1['prop_Qid_par'] = prop_Qid_par
                    elif bool_ques_type in [4,5]:
                        dict1['obj'] = obj
                        dict1['obj2'] = obj2
                        dict1['Qid'] = Qid
                        dict1['prop_res'] = prop_res
                        dict1['prop_Qid_par'] = prop_Qid_par

                    if bool_ques_type == 1:
                        description = 'Verification|2 entities, both direct'
                    elif bool_ques_type == 2:
                        description = 'Verification|2 entities, one direct and one indirect, subject is indirect'
                    elif bool_ques_type == 4:
                        description = 'Verification|3 entities, all direct, 2 are query entities'
                    elif bool_ques_type == 5:
                        description = 'Verification|3 entities, 2 direct, 2(direct) are query entities, subject is indirect'
                    dict1['description'] = description

                    #****************************************************************



                    if bool_ques_type == 1 or bool_ques_type == 2:
                        dict1['entities'] = [Qid, obj]
                    if bool_ques_type == 4 or bool_ques_type == 5:
                        dict1['entities'] = [Qid, obj, obj2]
                    dict1['signature'] = get_dict_signature(dict1.copy())
                    if dict1['signature'] in regex_ques_all:
                        ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23])
                        prev_ques_failed = True
                        continue
                    dialog_list.append(dict1.copy())
                    

                    if bool_ques_type == 1 or bool_ques_type == 2: 
                        if obj in pos_list:
                            # print 'Ans: YES'
                            ans = 'YES'
                        else:
                            # print 'Ans: NO'
                            ans = 'NO'
                    else:
                        # print 'Ans: %s, %s' % (('YES' if obj in pos_list else 'NO'),('YES' if obj2 in pos_list else 'NO'))
                        if obj in pos_list and obj2 in pos_list:
                            ans = 'YES'
                        elif obj not in pos_list and obj2 not in pos_list:
                            ans = 'NO'
                        else:
                            ans = '%s and %s respectively' % (('YES' if obj in pos_list else 'NO'),('YES' if obj2 in pos_list else 'NO'))
                    dict1 = {}
                    dict1['speaker'] = 'SYSTEM'
                    dict1['utterance'] = ans
                    if bool_ques_type == 1 or bool_ques_type == 2:
                        dict1['entities'] = []
                    if bool_ques_type == 4 or bool_ques_type == 5:
                        dict1['entities'] = []
                    dict1['active_set'] = tpl_regex[:]
                    dict1['ans_list_full'] = []
                    json_plus += len(dict1['entities'])
                    dict1['signature'] = get_dict_signature(dict1.copy())
                    dialog_list.append(dict1.copy())
                    

                elif bool_ques_type == 3:
                    # Qid = ans_list[0]
                    filt_dict = get_obj_ques_filt_dict(Qid) # filt_dict corr. to object based ques.

                    pq_tuple = [(p,q) for p in filt_dict.keys() for q in filt_dict[p] if p in obj_90_map and q in set(obj_90_map[p])]
                    pq_tuple = list(set(pq_tuple))
                    pq_tuple_fanout = [sum([wikidata_fanout_dict[qid] for qid in reverse_dict[Qid][p] if qid in child_par_dict and child_par_dict[qid]==q]) for (p,q) in pq_tuple]
                    if sum(pq_tuple_fanout)==0:
                        update_d_filt_dict(Qid,filt_dict)

                        prev_ques_failed = True
                        ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # No clarification question follows a failed question
                        # print d
                        continue

                    pq_tuple_fanout_norm = [x*1.0/sum(pq_tuple_fanout) for x in pq_tuple_fanout]

                    pq_tuple_choice = pq_tuple[np.random.choice(len(pq_tuple), p=pq_tuple_fanout_norm)]
                    prop_res = pq_tuple_choice[0]
                    prop_Qid_par = pq_tuple_choice[1]

                    # print 'Qid = %s' % Qid

                    pos_list = [q for q in reverse_dict[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                    comp_list = par_child_dict[prop_Qid_par]
                    if len(comp_list) > args.set_ques_ans_thresh:
                        comp_list = random.sample(comp_list, args.set_ques_ans_thresh)

                    sub = random.choice(pos_list) if (random.random()>0.5) else random.choice(comp_list)

                    ques = sing_basic2indirect(random.choice(sing_obj_annot_wh[prop_res]),Qid,child_par_dict,prop_Qid_par, prop_res) # to be modified  
                    ques = booleanise_ques(ques,sub)
                    # print 'Ques: %s' % ques

                    if args.update_counter:
                        ent_c.update([Qid])
                        ent_c.update([sub])
                    ent_c_plus += 2
                    tpl_set = [(sub,prop_res,Qid)]
                    tpl_regex = tpl_set

                    if len(tpl_regex) > 0 and (type(tpl_regex[0]) == type(list()) or type(tpl_regex[0]) == type(tuple())):
                        tpl_regex = ['(%s,%s,%s)' % (x[0],x[1],x[2]) for x in tpl_regex]

                    if args.update_counter:
                        tpl_c.update(tpl_set)

                    # if args.use_regex and len(set(tpl_regex).intersection(set(regex_ques_5))) > 0:
                    #     ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23])
                    #     prev_ques_failed = True
                    #     continue

                    dict1 = {}
                    dict1['speaker'] = 'USER'
                    dict1['utterance'] = ques
                    dict1['ques_type_id'] = ques_type_id_save
                    # dict1['last_ques_type_id_save'] = last_ques_type_id_save
                    dict1['bool_ques_type'] = bool_ques_type
                    dict1['entities'] = [Qid, sub]
                    dict1['relations'] = [prop_res]

                    dict1['Qid'] = Qid
                    dict1['prop_res'] = prop_res
                    dict1['prop_Qid_par'] = prop_Qid_par
                    dict1['sub'] = sub

                    dict1['description'] = 'Verification|2 entities, one direct and one indirect, object is indirect'
                    dict1['signature'] = get_dict_signature(dict1.copy())
                    if dict1['signature'] in regex_ques_all:
                        ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23])
                        prev_ques_failed = True
                        continue
                    dialog_list.append(dict1.copy())
                    

                    if sub in pos_list:
                        # print 'Ans: YES'
                        ans = 'YES'
                    else:
                        # print 'Ans: NO'
                        ans = 'NO'

                    dict1 = {}
                    dict1['speaker'] = 'SYSTEM'
                    dict1['utterance'] = ans
                    dict1['entities'] = []
                    dict1['active_set'] = tpl_regex[:]
                    dict1['ans_list_full'] = []
                    json_plus += len(dict1['entities'])
                    dict1['signature'] = get_dict_signature(dict1.copy())
                    dialog_list.append(dict1.copy())
                    
                    

                elif bool_ques_type == 6:
                    sub_list = ans_list # All the answers of previous question are now subjects of Plural Indirect question

                    # if len(sub_list) > args.plural_sub_ques_ans_thresh:
                    #     sub_list = np.random.choice(sub_list,args.plural_sub_ques_ans_thresh)

                    if not set(sub_list).issubset(reverse_dict.keys()):
                        prev_ques_failed = True
                        ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # No clarification question follows a failed question
                        continue

                    filt_plu_dict = {}

                    for sub in sub_list:
                        for pid in [p for p in reverse_dict[sub] if p in prop_data.keys() and p in obj_90_map]:
                            for q in [item for item in reverse_dict[sub][pid] if item in wikidata and item in child_par_dict]:
                                if sub not in filt_plu_dict:
                                    filt_plu_dict[sub] = {}
                                    filt_plu_dict[sub][pid] = [q]
                                else:
                                    if pid not in filt_plu_dict[sub]:
                                        filt_plu_dict[sub][pid] = [q]
                                    else:
                                        filt_plu_dict[sub][pid].append(q)

                    sub_pid_list = [filt_plu_dict[sub].keys() for sub in filt_plu_dict]
                    if len(sub_pid_list)==0 or len(sub_pid_list) != len(sub_list):
                        prev_ques_failed = True
                        ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # No clarification question follows a failed question
                        f1 = open(os.path.join(args.out_dir,'QA_%s_log.txt' % args.save_dir_id),'a')
                        f1.write('flag 1')
                        f1.close()
                        continue

                    valid_pid_list = list(set(sub_pid_list[0]).intersection(*sub_pid_list))
                    pq_tuple = []
                    pid_valid_obj_dict = {}

                    if len(valid_pid_list) > 0:
                        # print 'Valid pid for Plural question found'
                        # print valid_pid_list

                        for pid in valid_pid_list:
                            pid_obj_par_list = [filt_plu_dict[sub][pid] for sub in filt_plu_dict]
                            pid_valid_obj_par_list = list(set(pid_obj_par_list[0]).intersection(*pid_obj_par_list))
                            pid_valid_obj_dict[pid] = pid_valid_obj_par_list

                            for q in pid_valid_obj_par_list:
                                pq_tuple.append((pid,q))

                        # print pq_tuple
                        if len(pq_tuple)==0:
                            prev_ques_failed = True
                            ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # No clarification question follows a failed question
                            f1 = open(os.path.join(args.out_dir,'QA_%s_log.txt' % args.save_dir_id),'a')
                            f1.write('flag 2')
                            f1.close()
                            continue
                        pq_tuple = list(set(pq_tuple)) # remove duplicates
                        pq_tuple_choice = random.choice(pq_tuple)

                        prop_res = pq_tuple_choice[0]
                        sub = pq_tuple_choice[1]
                        prop_Qid_par = child_par_dict[sub]

                        # ques = '%s %s' % (ques,', '.join([item_data[q] for q in sub_list])) # to be modified

                        # pos_list = [q for sub in sub_list for q in reverse_dict[sub][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par and tpl_c[(Qid,prop_res,q)]<=args.triple_thresh]
                        comp_list = list(set(par_child_dict[prop_Qid_par]) - set(pid_valid_obj_dict[prop_res]))
                        if len(comp_list) > args.set_ques_ans_thresh:
                            comp_list = random.sample(comp_list, args.set_ques_ans_thresh)

                        if random.random()>0.5:
                            sub = random.choice(comp_list)

                        is_pphrase_ov = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in plu_obj_annot_wh[prop_res]]
                        if False in is_pphrase_ov:
                            ques = sing_basic2indirect(random.choice([plu_obj_annot_wh[prop_res][i] for i in range(len(plu_obj_annot_wh[prop_res])) if is_pphrase_ov[i] == False]),sub_list[0],child_par_dict,prop_Qid_par, prop_res, False) # to be modified
                        else:
                            ques = sing_basic2indirect(random.choice(plu_obj_annot_wh[prop_res]),sub_list[0],child_par_dict,prop_Qid_par, prop_res, False)

                        ques = booleanise_ques(ques,sub)
                        # print 'Ques: %s' % ques

                        if args.update_counter:
                            # ent_c.update(sub_list)
                            ent_c.update([sub])
                        ent_c_plus += (len(sub_list)+1)
                        tpl_set = [(sub,prop_res,q) for q in sub_list]
                        tpl_regex = tpl_set

                        if len(tpl_regex) > 0 and (type(tpl_regex[0]) == type(list()) or type(tpl_regex[0]) == type(tuple())):
                            tpl_regex = ['(%s,%s,%s)' % (x[0],x[1],x[2]) for x in tpl_regex]

                        if args.update_counter:
                            tpl_c.update(tpl_set)

                        # if args.use_regex and len(set(tpl_regex).intersection(set(regex_ques_5))) > 0:
                        #     ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23])
                        #     prev_ques_failed = True
                        #     continue

                        dict1 = {}
                        dict1['speaker'] = 'USER'
                        dict1['utterance'] = ques
                        dict1['ques_type_id'] = ques_type_id_save
                        # dict1['last_ques_type_id_save'] = last_ques_type_id_save
                        dict1['bool_ques_type'] = bool_ques_type
                        dict1['entities'] = [sub]
                        dict1['relations'] = [prop_res]

                        dict1['prop_res'] = prop_res
                        dict1['prop_Qid_par'] = prop_Qid_par
                        dict1['sub'] = sub
                        dict1['sub_list'] = sub_list

                        dict1['description'] = 'Verification|one entity, multiple entities (as object) referred indirectly'
                        dict1['signature'] = get_dict_signature(dict1.copy())
                        if dict1['signature'] in regex_ques_all:
                            ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23])
                            prev_ques_failed = True
                            continue
                        dialog_list.append(dict1.copy())
                        

                        if sub == pq_tuple_choice[1]:
                            # print 'Ans: YES'
                            ans = 'YES'
                        else:
                            # print 'Ans: NO'
                            ans = 'NO'
                        dict1 = {}
                        dict1['speaker'] = 'SYSTEM'
                        dict1['utterance'] = ans
                        dict1['entities'] = []
                        dict1['active_set'] = tpl_regex[:]
                        dict1['ans_list_full'] = []
                        json_plus += len(dict1['entities'])
                        dict1['signature'] = get_dict_signature(dict1.copy())
                        dialog_list.append(dict1.copy())
                        
                    else:
                        prev_ques_failed = True
                        ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # No clarification question follows a failed question
                        f1 = open(os.path.join(args.out_dir,'QA_%s_log.txt' % args.save_dir_id),'a')
                        f1.write('flag 3')
                        f1.close()
                        continue
                                    
                ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # to be followed by a secondary ques.
                ans_list = [] # no ans_list required here
                ans_list_full = ans_list
                prev_ques_count[1] = prev_ques_count[0]
                prev_ques_count[0] = len(ans_list)

            elif ques_type_id == 6: # Incomplete question
                sec_ques_type = sec_ques_sub_type = 0 # Incomplete ques. is not a secondary ques.

                # assuming pervious question was a subject based ques (singular direct)
                # case-1: only subject is changed, predicate remains same
                # case-2: object parent is changed, subject and predicate remain same
                if last_ques_type_id_save == 7:
                    type_choice = 3
                else:
                    type_choice = np.random.choice([1, 2],p = [args.p_inc_ques_1, args.p_inc_ques_2])
                pprase_list = ['what about', 'also tell me about', 'how about']
                pp = random.choice(pprase_list)

                if type_choice == 1: # object parent is changed, subject and predicate remain same
                    Qid = last_Qid
                    try:
                        assert prop_res in wikidata[Qid]
                    except:
                        prev_ques_failed = True
                        ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # No clarification question follows a failed question
                        continue
                    prop_Qid_par_new_list = list(set([child_par_dict[q] for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q] != prop_Qid_par]))

                    if len(prop_Qid_par_new_list) == 0:
                        prev_ques_failed = True
                        ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # No clarification question follows a failed question
                        continue

                    prop_Qid_par_new = random.choice(prop_Qid_par_new_list)
                    ques = 'And which %s?' % (child_par_dict_name_2[prop_Qid_par_new])
                    ans_list = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par_new]
                    
                    if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                        prev_ques_failed = True
                        ques_type_id = 2
                        continue

                    ans_list_full = ans_list

                    if len(ans_list) > args.plural_obj_ques_ans_thresh:
                        ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                        sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                        ans_list_t = [ans_list[i] for i in sort_index]
                        ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]

                    prop_Qid_par = prop_Qid_par_new # used for updating d
                    if args.update_counter:
                        ent_c.update([Qid])
                        ent_c.update(ans_list)
                    ent_c_plus += (len(ans_list)+1)
                    tpl_set = [(Qid,prop_res,q) for q in ans_list]
                    tpl_regex = ['(%s,%s,%s)' % (Qid,prop_res,'|'.join(['c(%s)'% x for x in [prop_Qid_par_new]]))]
                    if args.update_counter:
                        tpl_c.update(tpl_set)
                    ans = ', '.join([item_data[q] for q in ans_list])

                elif type_choice == 2: # only subject is changed, parent and predicate remains same
                    valid_obj = [q for q in reverse_dict if q in child_par_dict and child_par_dict[q] == prop_Qid_par and prop_res in reverse_dict[q]]
                    valid_sub = [sub for qid in valid_obj for sub in reverse_dict[qid][prop_res] if sub != last_Qid and sub in wikidata]
                    
                    if len(valid_sub) == 0:
                        prev_ques_failed = True
                        ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # No clarification question follows a failed question
                        continue

                    sub_choice = random.choice(valid_sub)
                    Qid = sub_choice # for updating d

                    ques = 'And %s %s?' % (pp, item_data[sub_choice])
                    ans_list = [q for q in wikidata[sub_choice][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                    
                    if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                        prev_ques_failed = True
                        ques_type_id = 2
                        continue

                    ans_list_full = ans_list

                    if len(ans_list) > args.plural_obj_ques_ans_thresh:
                        ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                        sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                        ans_list_t = [ans_list[i] for i in sort_index]
                        ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]

                    if args.update_counter:
                        ent_c.update([Qid])
                        ent_c.update(ans_list)
                    ent_c_plus += (len(ans_list)+1)
                    tpl_set = [(Qid,prop_res,q) for q in ans_list]
                    tpl_regex = ['(%s,%s,%s)' % (sub_choice,prop_res,'|'.join(['c(%s)'% x for x in [prop_Qid_par]]))]
                    if args.update_counter:
                        tpl_c.update(tpl_set)
                    ans = ', '.join([item_data[q] for q in ans_list])

                elif type_choice == 3: # Incomplete count-based ques
                    valid_obj = [q for q in reverse_dict if q in child_par_dict and child_par_dict[q] == prop_Qid_par and prop_res in reverse_dict[q]]
                    valid_sub = [sub for qid in valid_obj for sub in reverse_dict[qid][prop_res] if sub != last_Qid and sub in wikidata]
                    
                    if len(valid_sub) == 0:
                        prev_ques_failed = True
                        ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # No clarification question follows a failed question
                        continue

                    sub_choice = random.choice(valid_sub)
                    Qid = sub_choice # for updating d

                    ques = 'And %s %s?' % (pp, item_data[sub_choice])
                    ans_list = [q for q in wikidata[sub_choice][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]

                    N = len(ans_list)

                    # if random.random() > 0.5:
                    #     ans = inf_eng.number_to_words(int(N))
                    # else:
                    #     ans = str(int(N))
                    ans = str(int(N))

                    if args.update_counter:
                        ent_c.update([Qid])

                    ent_c_plus += (len(ans_list)+1)
                    tpl_set = [(Qid, prop_res, q) for q in ans_list]
                    tpl_regex = ['(%s,%s,%s)' % (Qid,prop_res,'|'.join(['c(%s)'% x for x in [prop_Qid_par]]))]
                    ans_list = []
                    ans_list_full = ans_list

                    if args.update_counter:
                        tpl_c.update(tpl_set)

                # if args.use_regex and len(set(tpl_regex).intersection(set(regex_ques_6))) > 0:
                #     ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23])
                #     prev_ques_failed = True
                #     continue

                dict1 = {}
                dict1['speaker'] = 'USER'
                dict1['utterance'] = ques
                dict1['ques_type_id'] = ques_type_id_save
                # dict1['last_ques_type_id_save'] = last_ques_type_id_save
                dict1['inc_ques_type'] = type_choice
                dict1['entities'] = [Qid]
                dict1['relations'] = []

                if type_choice == 1:
                    description = 'Incomplete|object parent is changed, subject and predicate remain same'
                elif type_choice == 2:
                    description = 'only subject is changed, parent and predicate remains same'
                else:
                    description = 'Incomplete count-based ques'
                dict1['description'] = description

                if type_choice == 1:
                    dict1['Qid'] = Qid
                    dict1['prop_res'] = prop_res
                    dict1['prop_Qid_par_new'] = prop_Qid_par_new
                elif type_choice == 2:
                    dict1['Qid'] = Qid
                    dict1['prop_res'] = prop_res
                    dict1['prop_Qid_par'] = prop_Qid_par
                else:
                    dict1['Qid'] = Qid
                    dict1['prop_res'] = prop_res
                    dict1['prop_Qid_par'] = prop_Qid_par

                dict1['signature'] = get_dict_signature(dict1.copy())
                if dict1['signature'] in regex_ques_all:
                    ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23])
                    prev_ques_failed = True
                    continue
                dialog_list.append(dict1.copy())
                

                # print 'Ans: %s' % ', '.join([item_data[q] for q in ans_list])

                
                dict1 = {}
                dict1['speaker'] = 'SYSTEM'
                dict1['utterance'] = ans
                dict1['entities'] = ans_list[:]
                dict1['active_set'] = tpl_regex[:]
                dict1['ans_list_full'] = ans_list_full
                json_plus += len(dict1['entities'])
                dict1['signature'] = get_dict_signature(dict1.copy())
                dialog_list.append(dict1.copy())
                                
                

                prev_ques_count[1] = prev_ques_count[0]
                prev_ques_count[0] = len(ans_list)
                ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # ques type_id of next question (Secondary)


            elif ques_type_id == 7: # count-based question
                sec_ques_type = sec_ques_sub_type = 0

                count_ques_type = np.random.choice(np.array([1,2])) # sub-based or obj-based (add p)
                count_ques_sub_type = np.random.choice(np.array([1,2,3,4,5,6,7,8,9]),p=[0.12,0.11,0.11,0.11,0.11,0.11,0.11,0.11,0.11]) #(add p)
                # count_ques_sub_type = random.choice([8,9])

                if count_ques_type == 1 and count_ques_sub_type == 1:
                    ques_type_id = 6
                else:
                    ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # ques type_id of next question (Secondary)
                # print 'ques_type_id_save = %d' % ques_type_id_save

                if count_ques_type == 1: # sub-based
                    if count_ques_sub_type == 1: # basic form
                        sec_ques_type = sec_ques_sub_type = 0 # Direct ques. is not a secondary ques.

                        filt_dict = get_sub_ques_filt_dict(Qid)
                        pq_tuple = [(p,q) for p in filt_dict.keys() for q in filt_dict[p] if p in sub_90_map and q in set(sub_90_map[p])]
                        if len(pq_tuple) > args.pq_tuple_thresh:
                            pq_tuple = random.sample(pq_tuple, args.pq_tuple_thresh)
                        pq_tuple_fanout = [sum([wikidata_fanout_dict[qid] for qid in wikidata[Qid][p] if qid in child_par_dict and child_par_dict[qid]==q]) for (p,q) in pq_tuple]
                        if sum(pq_tuple_fanout)==0: #blacklist the combination of Qid, pid, filt_dict[Qid][pid]
                            update_d_filt_dict(Qid,filt_dict)
                            prev_ques_failed = True
                            continue
                        pq_tuple_fanout_norm = [x*1.0/sum(pq_tuple_fanout) for x in pq_tuple_fanout]
                        pq_tuple_choice = pq_tuple[np.random.choice(len(pq_tuple), p=pq_tuple_fanout_norm)]
                        prop_res = pq_tuple_choice[0]
                        prop_Qid_par = pq_tuple_choice[1]

                        ques = random.choice(plu_sub_annot_wh[prop_res])
                        ques = sing_basic2count_based(ques, '', count_ques_sub_type)        
                        ques = ques.replace('XXX',item_data[Qid])
                        ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))

                        ans_list = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                        ans_list_full = ans_list

                        N = len(ans_list)

                        # if random.random() > 0.5:
                        #     ans = inf_eng.number_to_words(int(N))
                        # else:
                        #     ans = str(int(N))
                        ans = str(int(N))

                        tpl_set = [(Qid, prop_res, q) for q in ans_list]
                        tpl_regex = ['(%s,%s,%s)' % (Qid,prop_res,'|'.join(['c(%s)'% x for x in [prop_Qid_par]]))]
                        if args.update_counter:
                            tpl_c.update(tpl_set)
                        ans_entity_list = []

                    elif count_ques_sub_type == 7:
                        if len(dialog_list[-1]['entities']) == 0:
                            prev_ques_failed = True
                            continue

                        Qid = random.choice(dialog_list[-1]['entities']) # true entity
                        pred_label = random.choice(dialog_list[-1]['entities'])

                        filt_dict = get_sub_ques_filt_dict(Qid)
                        pq_tuple = [(p,q) for p in filt_dict.keys() for q in filt_dict[p] if p in sub_90_map and q in set(sub_90_map[p])]
                        if len(pq_tuple) > args.pq_tuple_thresh:
                            pq_tuple = random.sample(pq_tuple, args.pq_tuple_thresh)
                        pq_tuple_fanout = [sum([wikidata_fanout_dict[qid] for qid in wikidata[Qid][p] if qid in child_par_dict and child_par_dict[qid]==q]) for (p,q) in pq_tuple]
                        if sum(pq_tuple_fanout)==0: #blacklist the combination of Qid, pid, filt_dict[Qid][pid]
                            update_d_filt_dict(Qid,filt_dict)
                            prev_ques_failed = True
                            continue
                        pq_tuple_fanout_norm = [x*1.0/sum(pq_tuple_fanout) for x in pq_tuple_fanout]
                        pq_tuple_choice = pq_tuple[np.random.choice(len(pq_tuple), p=pq_tuple_fanout_norm)]
                        prop_res = pq_tuple_choice[0]
                        prop_Qid_par = pq_tuple_choice[1]

                        ques = random.choice(plu_sub_annot_wh[prop_res])
                        ques = sing_basic2count_based(ques, '', 1)        
                        ques = ques.replace('XXX','that %s' % child_par_dict_name_2[child_par_dict[Qid]])
                        ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))

                        ans_list = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                        ans_list_full = ans_list

                        N = len(ans_list)

                        # if random.random() > 0.5:
                        #     ans = inf_eng.number_to_words(int(N))
                        # else:
                        #     ans = str(int(N))
                        ans = str(int(N))

                        tpl_set = [(Qid, prop_res, q) for q in ans_list]
                        tpl_regex = ['(%s,%s,%s)' % (Qid,prop_res,'|'.join(['c(%s)'% x for x in [prop_Qid_par]]))]
                        tpl_regex_extend = []

                        for q in dialog_list[-1]['entities']:
                            tpl_regex_extend.extend(['(%s,%s,%s)' % (q,prop_res,'|'.join(['c(%s)'% x for x in [prop_Qid_par]]))])

                        if args.update_counter:
                            tpl_c.update(tpl_set)
                        ans_entity_list = []

                    elif count_ques_sub_type in [8,9]:
                        if len(dialog_list[-1]['entities']) == 0:
                            prev_ques_failed = True
                            continue

                        obj_par = child_par_dict[dialog_list[-1]['entities'][0]]
                        flag = False

                        for p in [p1 for p1 in wikidata_type_rev_dict[obj_par] if p1 in sub_90_map and obj_par in sub_90_map[p1]]:
                            for q3 in wikidata_type_rev_dict[obj_par][p]:
                                if p in obj_90_map and q3 in obj_90_map[p] and q3 in par_child_dict and q3 in child_par_dict_val:
                                    ans_list = [q1 for q1 in par_child_dict[obj_par] if q1 in reverse_dict and p in reverse_dict[q1]]
                                    if len(ans_list) > 1 and len(set(ans_list) & set(dialog_list[-1]['entities']))>0:
                                        sub_par = q3
                                        prop_res = p
                                        Z = random.choice(list(set(dialog_list[-1]['entities']) & set(ans_list)))
                                        Qid = Z
                                        pred_label = random.choice(dialog_list[-1]['entities'])
                                        flag = True

                        if not flag:
                            prev_ques_failed = True
                            continue

                        cand_obj_list = list(set([q for q in par_child_dict[obj_par] if q in reverse_dict and prop_res in reverse_dict[q]]))

                        if len(cand_obj_list) > args.count_ques_sub_thresh:
                            prev_ques_failed = True
                            continue

                        cand_obj_list_score = {}
                        for obj in cand_obj_list:
                            cand_obj_list_score[obj] = len([q for q in reverse_dict[obj][prop_res] if q in child_par_dict and child_par_dict[q] == sub_par])

                        cand_obj_list_score_arr = np.asarray(cand_obj_list_score.values())

                        ques = random.choice(plu_sub_annot_wh[prop_res])
                        qualifier_dict = {2:['min','max'], 3:['atleast','atmost','exactly','around','approximately'], 4:['more','less','greater','lesser','around the same','approximately the same'],5:['atleast','atmost','exactly','around','approximately'],6:['more','less','greater','lesser','around the same','approximately the same']}
                        
                        if count_ques_sub_type == 8:
                            qualifier_choice = random.choice(qualifier_dict[4])
                            ques = sing_basic2count_based(ques, qualifier_choice, 4)
                        else:
                            qualifier_choice = random.choice(qualifier_dict[6])
                            ques = sing_basic2count_based(ques, qualifier_choice, 6)

                        ques = ques.replace('Z', 'that %s' % child_par_dict_name_2[child_par_dict[Z]])
                        ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))

                        Z_score = cand_obj_list_score[Z]
                        
                        if qualifier_choice == 'more' or qualifier_choice == 'greater':
                            ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > Z_score]
                        elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                            ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] < Z_score]
                        elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                            ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > (Z_score - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[x] < (Z_score + np.std(cand_obj_list_score_arr))]

                        if count_ques_sub_type == 8:
                            # ans_list = [q for q in ans_list if ent_c[q]<=args.entity_thresh]

                            if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                prev_ques_failed = True
                                ques_type_id = 2
                                continue

                            ans_list_full = ans_list

                            if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                ans_list_t = [ans_list[i] for i in sort_index]
                                ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                            ans_entity_list = ans_list
                            ans = ', '.join([item_data[x] for x in ans_list])

                            if len(ans_list) == 0:
                                ans = 'None'
                        elif count_ques_sub_type == 9:
                            # ans = str(len(ans_list))
                            ans_list_full = ans_list
                            n = len(ans_list)
                            # if random.random() > 0.5:
                            #     ans = inf_eng.number_to_words(int(n))
                            # else:
                            #     ans = str(int(n))
                            ans = str(int(n))
                            ans_entity_list = []

                        tpl_set = []

                        # try:
                        for obj in ans_list:
                            tpl_set.extend([(q, prop_res, obj) for q in reverse_dict[obj][prop_res] if q in child_par_dict and child_par_dict[q] == sub_par])

                        tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par]]),prop_res,'c(%s)' % obj_par)]
                        tpl_regex_extend = tpl_regex
                        # except:
                        #     f1 = open(os.path.join(args.out_dir,'QA_%s_log.txt' % args.save_dir_id),'a')
                        #     f1.write('obj = %s prop_res = %s\n' % (obj, prop_res))
                        #     f1.close()
                        #     prev_ques_failed = True
                        #     continue
                        if args.update_counter:
                            tpl_c.update(tpl_set)
                        ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))

                    else:
                        sec_ques_type = sec_ques_sub_type = 0
                        # sub_par = random.choice([child_par_dict[q] for q in prev_Qid if q in child_par_dict if child_par_dict[q] in wikidata_type_dict])
                        # pq_tuple = [(p,q) for p in wikidata_type_dict[sub_par] for q in wikidata_type_dict[sub_par][p] if p in sub_90_map and q in sub_90_map[p] and q in par_child_dict]
                        # if len(pq_tuple) > args.pq_tuple_thresh:
                        #     pq_tuple = random.sample(pq_tuple, args.pq_tuple_thresh)
                        # pq_tuple_fanout = [len([q1 for q1 in par_child_dict[q] if q1 in reverse_dict and p in reverse_dict[q1]]) for (p,q) in pq_tuple]
                        # pq_tuple_fanout_norm = [x*1.0/sum(pq_tuple_fanout) for x in pq_tuple_fanout]
                        # pq_tuple_choice = pq_tuple[np.random.choice(len(pq_tuple), p=pq_tuple_fanout_norm)]
                        # prop_res = pq_tuple_choice[0]
                        # obj_par = pq_tuple_choice[1]

                        flag = False
                        for q3 in [child_par_dict[q4] for q4 in prev_Qid if q4 in child_par_dict and child_par_dict[q4] in wikidata_type_dict]:
                            for p in [p1 for p1 in wikidata_type_dict[q3] if p1 in obj_90_map and q3 in obj_90_map[p1]]:
                                cand_obj_par_list = []
                                cand_obj_par_score_list = []
                                for q in wikidata_type_dict[q3][p]:
                                    if p in sub_90_map and q in sub_90_map[p] and q in par_child_dict and q in child_par_dict_val:
                                        ans_len = len([q1 for q1 in par_child_dict[q] if q1 in reverse_dict and p in reverse_dict[q1]])
                                        if ans_len > 1:
                                            sub_par = q3
                                            prop_res = p
                                            obj_par = q
                                            cand_obj_par_list.append(q)
                                            cand_obj_list = [q5 for q5 in par_child_dict[obj_par] if q5 in reverse_dict and prop_res in reverse_dict[q5]]
                                            cand_obj_list_score = list()
                                            for obj in cand_obj_list:
                                                cand_obj_list_score.append(len([q5 for q5 in reverse_dict[obj][prop_res] if q5 in child_par_dict and child_par_dict[q5] == sub_par]))
                                            cand_obj_par_score_list.append(len([x for x in cand_obj_list_score if x > 1]))
                                if len(cand_obj_par_list) > 0:
                                    sub_par = q3
                                    prop_res = p
                                    # obj_par = cand_obj_par_list[cand_obj_par_score_list.index(max(cand_obj_par_score_list))]
                                    obj_par = random.choice(cand_obj_par_list)
                                    flag = True
                                    break
                                if flag:
                                    break
                            if flag:
                                break

                        if not flag:
                            prev_ques_failed = True
                            # ques_type_id = 2
                            continue
                        ques = random.choice(plu_sub_annot_wh[prop_res])
                        qualifier_dict = {2:['min','max'], 3:['atleast','atmost','exactly','around','approximately'], 4:['more','less','greater','lesser','around the same','approximately the same'],5:['atleast','atmost','exactly','around','approximately'],6:['more','less','greater','lesser','around the same','approximately the same']}
                        qualifier_choice = random.choice(qualifier_dict[count_ques_sub_type])
                        ques = sing_basic2count_based(ques, qualifier_choice, count_ques_sub_type)
                        ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))
                        
                        cand_obj_list = list(set([q for q in par_child_dict[obj_par] if q in reverse_dict and prop_res in reverse_dict[q]]))
                        if len(cand_obj_list) > args.count_ques_sub_thresh:
                            prev_ques_failed = True
                            continue

                        cand_obj_list_score = {}
                        for obj in cand_obj_list:
                            cand_obj_list_score[obj] = len([q for q in reverse_dict[obj][prop_res] if q in child_par_dict and child_par_dict[q] == sub_par])

                        cand_obj_list_score_arr = np.asarray(cand_obj_list_score.values())

                        if count_ques_sub_type == 2:                       

                            if qualifier_choice == 'min':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] == min(cand_obj_list_score.values())]
                                
                            elif qualifier_choice == 'max':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] == max(cand_obj_list_score.values())]

                            ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))
                            tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par]]),prop_res,obj)]

                            for obj in ans_list:
                                tpl_set.extend([(q, prop_res, obj) for q in reverse_dict[obj][prop_res] if q in child_par_dict and child_par_dict[q] == sub_par])

                            if args.update_counter:
                                tpl_c.update(tpl_set)

                            if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                prev_ques_failed = True
                                ques_type_id = 2
                                continue
                            ans_list_full = ans_list

                            if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                ans_list_t = [ans_list[i] for i in sort_index]
                                ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                            ans = ', '.join([item_data[x] for x in ans_list])
                            ans_entity_list = ans_list

                        elif count_ques_sub_type == 3 or count_ques_sub_type == 5:

                            flag = True
                            for n in np.random.permutation(np.arange(1,max(cand_obj_list_score.values())+1)):
                                n = int(n)
                                if qualifier_choice == 'atleast':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] >= n]
                                elif qualifier_choice == 'atmost':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] <= n]
                                elif qualifier_choice == 'exactly':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] == n]
                                elif qualifier_choice == 'around' or qualifier_choice == 'approximately':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > (n - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[x] < (n + np.std(cand_obj_list_score_arr))]

                                if len(ans_list) > 1:
                                    N = n
                                    flag = False
                                    break
                            if flag:
                                prev_ques_failed = True
                                continue

                            # if random.random() > 0.5:
                            #     N_str = inf_eng.number_to_words(int(N))
                            # else:
                            #     N_str = str(int(N))
                            N_str = str(int(N))
                            ques = ques.replace(' N ',' %s ' % N_str)

                            if qualifier_choice == 'atleast':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] >= N]
                            elif qualifier_choice == 'atmost':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] <= N]
                            elif qualifier_choice == 'exactly':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] == N]
                            elif qualifier_choice == 'around' or qualifier_choice == 'approximately':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > (N - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[x] < (N + np.std(cand_obj_list_score_arr))]

                            if count_ques_sub_type == 3:
                                # ans_list = [q for q in ans_list if ent_c[q]<=args.entity_thresh]
                                if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                    prev_ques_failed = True
                                    ques_type_id = 2
                                    continue
                                ans_list_full = ans_list

                                if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                    ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                    sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                    ans_list_t = [ans_list[i] for i in sort_index]
                                    ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                                ans = ', '.join([item_data[x] for x in ans_list])
                                ans_entity_list = ans_list
                            elif count_ques_sub_type == 5:
                                n = len(ans_list)
                                ans_list_full = ans_list
                                # if random.random() > 0.5:
                                #     ans = inf_eng.number_to_words(int(n))
                                # else:
                                #     ans = str(int(n))
                                ans = str(int(n))
                                # ans = str(len(ans_list))
                                ans_entity_list = []

                            tpl_set = []

                            for obj in ans_list:
                                tpl_set.extend([(q, prop_res, obj) for q in reverse_dict[obj][prop_res] if q in child_par_dict and child_par_dict[q] == sub_par])

                            tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par]]),prop_res,'c(%s)' % obj_par)]
                            if args.update_counter:
                                tpl_c.update(tpl_set)

                            if N > 1:
                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))
                            else:
                                ques = ques.replace('SPPS',child_par_dict_name_2[sub_par])

                        elif count_ques_sub_type == 4 or count_ques_sub_type == 6:

                            flag = True
                            for z in random_shuffle(cand_obj_list):
                                Z_score = cand_obj_list_score[z]
                                if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > Z_score]
                                elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] < Z_score]
                                elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > (Z_score - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[x] < (Z_score + np.std(cand_obj_list_score_arr))]

                                if len(ans_list) > 1:
                                    Z = z
                                    flag = False
                                    break
                            if flag:
                                prev_ques_failed = True
                                continue

                            ques = ques.replace('Z', item_data[Z])

                            Z_score = cand_obj_list_score[Z]
                            
                            if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > Z_score]
                            elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] < Z_score]
                            elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > (Z_score - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[x] < (Z_score + np.std(cand_obj_list_score_arr))]

                            if count_ques_sub_type == 4:
                                # ans_list = [q for q in ans_list if ent_c[q]<=args.entity_thresh]
                                if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                    prev_ques_failed = True
                                    ques_type_id = 2
                                    continue
                                ans_list_full = ans_list

                                if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                    ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                    sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                    ans_list_t = [ans_list[i] for i in sort_index]
                                    ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                                ans_entity_list = ans_list
                                ans = ', '.join([item_data[x] for x in ans_list])

                                if len(ans_list) == 0:
                                    ans = 'None'
                            elif count_ques_sub_type == 6:
                                # ans = str(len(ans_list))
                                n = len(ans_list)
                                ans_list_full = ans_list
                                # if random.random() > 0.5:
                                #     ans = inf_eng.number_to_words(int(n))
                                # else:
                                #     ans = str(int(n))
                                ans = str(int(n))
                                ans_entity_list = []

                            tpl_set = []

                            # try:
                            for obj in ans_list:
                                tpl_set.extend([(q, prop_res, obj) for q in reverse_dict[obj][prop_res] if q in child_par_dict and child_par_dict[q] == sub_par])

                            tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par]]),prop_res,'c(%s)' % obj_par)]
                            # except:
                            #     f1 = open(os.path.join(args.out_dir,'QA_%s_log.txt' % args.save_dir_id),'a')
                            #     f1.write('obj = %s prop_res = %s\n' % (obj, prop_res))
                            #     f1.close()
                            #     prev_ques_failed = True
                            #     continue
                            if args.update_counter:
                                tpl_c.update(tpl_set)
                            ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))

                elif count_ques_type == 2: # obj-based
                    if count_ques_sub_type == 1: # basic form
                        sec_ques_type = sec_ques_sub_type = 0 # Direct ques. is not a secondary ques.

                        filt_dict = get_obj_ques_filt_dict(Qid)
                        pq_tuple = [(p,q) for p in filt_dict.keys() for q in filt_dict[p] if p in obj_90_map and q in set(obj_90_map[p])]
                        if len(pq_tuple) > args.pq_tuple_thresh:
                            pq_tuple = random.sample(pq_tuple, args.pq_tuple_thresh)
                        pq_tuple_fanout = [sum([wikidata_fanout_dict[qid] for qid in reverse_dict[Qid][p] if qid in child_par_dict and child_par_dict[qid]==q]) for (p,q) in pq_tuple]
                        if sum(pq_tuple_fanout)==0: #blacklist the combination of Qid, pid, filt_dict[Qid][pid]
                            update_d_filt_dict(Qid,filt_dict)
                            prev_ques_failed = True
                            continue
                        pq_tuple_fanout_norm = [x*1.0/sum(pq_tuple_fanout) for x in pq_tuple_fanout]
                        pq_tuple_choice = pq_tuple[np.random.choice(len(pq_tuple), p=pq_tuple_fanout_norm)]
                        prop_res = pq_tuple_choice[0]
                        prop_Qid_par = pq_tuple_choice[1]

                        ques = random.choice(plu_obj_annot_wh[prop_res])
                        ques = sing_basic2count_based(ques, '', count_ques_sub_type)        
                        ques = ques.replace('YYY',item_data[Qid])
                        ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))

                        ans_list = [q for q in reverse_dict[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                        ans_list_full = ans_list

                        N = len(ans_list)

                        # if random.random() > 0.5:
                        #     ans = inf_eng.number_to_words(int(N))
                        # else:
                        #     ans = str(int(N))
                        ans = str(int(N))

                        tpl_set = [(q, prop_res, Qid) for q in ans_list]
                        if args.update_counter:
                            tpl_c.update(tpl_set)
                        tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [prop_Qid_par]]),prop_res,Qid)]
                        ans_entity_list = []

                    elif count_ques_sub_type == 7:
                        if len(dialog_list[-1]['entities']) == 0:
                            prev_ques_failed = True
                            continue
                        Qid = random.choice(dialog_list[-1]['entities']) # true entity
                        pred_label = random.choice(dialog_list[-1]['entities'])

                        filt_dict = get_obj_ques_filt_dict(Qid)
                        pq_tuple = [(p,q) for p in filt_dict.keys() for q in filt_dict[p] if p in obj_90_map and q in set(obj_90_map[p])]
                        if len(pq_tuple) > args.pq_tuple_thresh:
                            pq_tuple = random.sample(pq_tuple, args.pq_tuple_thresh)
                        pq_tuple_fanout = [sum([wikidata_fanout_dict[qid] for qid in reverse_dict[Qid][p] if qid in child_par_dict and child_par_dict[qid]==q]) for (p,q) in pq_tuple]
                        if sum(pq_tuple_fanout)==0: #blacklist the combination of Qid, pid, filt_dict[Qid][pid]
                            update_d_filt_dict(Qid,filt_dict)
                            prev_ques_failed = True
                            continue
                        pq_tuple_fanout_norm = [x*1.0/sum(pq_tuple_fanout) for x in pq_tuple_fanout]
                        pq_tuple_choice = pq_tuple[np.random.choice(len(pq_tuple), p=pq_tuple_fanout_norm)]
                        prop_res = pq_tuple_choice[0]
                        prop_Qid_par = pq_tuple_choice[1]

                        ques = random.choice(plu_obj_annot_wh[prop_res])
                        ques = sing_basic2count_based(ques, '', 1)        
                        ques = ques.replace('YYY','that %s' % child_par_dict_name_2[child_par_dict[Qid]])
                        ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))

                        ans_list = [q for q in reverse_dict[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                        ans_list_full = ans_list
                        N = len(ans_list)

                        # if random.random() > 0.5:
                        #     ans = inf_eng.number_to_words(int(N))
                        # else:
                        #     ans = str(int(N))
                        ans = str(int(N))

                        tpl_set = [(q, prop_res, Qid) for q in ans_list]
                        if args.update_counter:
                            tpl_c.update(tpl_set)
                        tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [prop_Qid_par]]),prop_res,Qid)]

                        tpl_regex_extend = []
                        for q in dialog_list[-1]['entities']:
                            tpl_regex_extend.extend(['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [prop_Qid_par]]),prop_res,q)])
                        ans_entity_list = []

                    elif count_ques_sub_type in [8,9]:
                        if len(dialog_list[-1]['entities']) == 0:
                            prev_ques_failed = True
                            continue

                        sub_par = child_par_dict[dialog_list[-1]['entities'][0]]
                        if sub_par not in wikidata_type_dict:
                            prev_ques_failed = True
                            continue
                        flag = False

                        for p in [p1 for p1 in wikidata_type_dict[sub_par] if p1 in obj_90_map and sub_par in obj_90_map[p1]]:
                            for q3 in wikidata_type_dict[sub_par][p]:
                                if q3 in sub_90_map[p] and q3 in par_child_dict and q3 in child_par_dict_val:
                                    ans_list = [q1 for q1 in par_child_dict[sub_par] if q1 in wikidata and p in wikidata[q1]]
                                    if len(ans_list) > 1 and len(set(ans_list) & set(dialog_list[-1]['entities']))>0:
                                        obj_par = q3
                                        prop_res = p
                                        Z = random.choice(list(set(dialog_list[-1]['entities']) & set(ans_list)))
                                        Qid = Z
                                        pred_label = random.choice(dialog_list[-1]['entities'])
                                        flag = True

                        if not flag:
                            prev_ques_failed = True
                            continue

                        cand_sub_list = list(set([q for q in par_child_dict[sub_par] if q in wikidata and prop_res in wikidata[q]]))

                        if len(cand_sub_list) > args.count_ques_sub_thresh:
                            prev_ques_failed = True
                            continue

                        cand_sub_list_score = {}
                        for sub in cand_sub_list:
                            cand_sub_list_score[sub] = len([q for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q] == obj_par])

                        cand_sub_list_score_arr = np.asarray(cand_sub_list_score.values())

                        flag = True
                        for z in random_shuffle(cand_sub_list):
                            Z_score = cand_sub_list_score[z]

                            if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > Z_score]
                            elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] < Z_score]
                            elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > (Z_score - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (Z_score + np.std(cand_sub_list_score_arr))]

                            if len(ans_list) > 1:
                                Z = z
                                flag = False
                                break
                        if flag:
                            prev_ques_failed = True
                            continue

                        ques = random.choice(plu_obj_annot_wh[prop_res])
                        qualifier_dict = {2:['min','max'], 3:['atleast','atmost','exactly','around','approximately'], 4:['more','less','greater','lesser','around the same','approximately the same'],5:['atleast','atmost','exactly','around','approximately'],6:['more','less','greater','lesser','around the same','approximately the same']}
                        
                        if count_ques_sub_type == 8:
                            qualifier_choice = random.choice(qualifier_dict[4])
                            ques = sing_basic2count_based(ques, qualifier_choice, 4)
                        else:
                            qualifier_choice = random.choice(qualifier_dict[6])
                            ques = sing_basic2count_based(ques, qualifier_choice, 6)
                        ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))

                        ques = ques.replace('Z', 'that %s' % child_par_dict_name_2[child_par_dict[Z]])
                        
                        Z_score = cand_sub_list_score[Z]                           

                        if qualifier_choice == 'more' or qualifier_choice == 'greater':
                            ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > Z_score]
                        elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                            ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] < Z_score]
                        elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                            ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > (Z_score - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (Z_score + np.std(cand_sub_list_score_arr))]

                        if count_ques_sub_type == 8:
                            # ans_list = [q for q in ans_list if ent_c[q]<=args.entity_thresh]
                            if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                prev_ques_failed = True
                                ques_type_id = 2
                                continue
                            ans_list_full = ans_list

                            if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                ans_list_t = [ans_list[i] for i in sort_index]
                                ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                            ans = ', '.join([item_data[x] for x in ans_list])
                            ans_entity_list = ans_list
                            
                            if len(ans_list) == 0:
                                ans = 'None'
                        else:
                            # ans = str(len(ans_list))
                            n = len(ans_list)
                            ans_list_full = ans_list
                            # if random.random() > 0.5:
                            #     ans = inf_eng.number_to_words(int(n))
                            # else:
                            #     ans = str(int(n))
                            ans = str(int(n))
                            ans_entity_list = []

                        tpl_set = []

                        # try:
                        for sub in ans_list:
                            tpl_set.extend([(sub, prop_res, q) for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q] == obj_par])

                        tpl_regex = ['(%s,%s,%s)' % ('c(%s)' % sub_par, prop_res,'|'.join(['c(%s)'% x for x in [obj_par]]))]
                        tpl_regex_extend = tpl_regex

                        if args.update_counter:
                            tpl_c.update(tpl_set)
                        ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))

                    else:
                        sec_ques_type = sec_ques_sub_type = 0
                        # obj_par = random.choice([child_par_dict[q] for q in prev_Qid if q in child_par_dict if child_par_dict[q] in wikidata_type_rev_dict])
                        # pq_tuple = [(p,q) for p in wikidata_type_rev_dict[obj_par] for q in wikidata_type_rev_dict[obj_par][p] if p in obj_90_map and q in obj_90_map[p] and q in par_child_dict]
                        # if len(pq_tuple) > args.pq_tuple_thresh:
                        #     pq_tuple = random.sample(pq_tuple, args.pq_tuple_thresh)
                        # pq_tuple_fanout = [len([q1 for q1 in par_child_dict[q] if q1 in wikidata and p in wikidata[q1]]) for (p,q) in pq_tuple]
                        # pq_tuple_fanout_norm = [x*1.0/sum(pq_tuple_fanout) for x in pq_tuple_fanout]
                        # pq_tuple_choice = pq_tuple[np.random.choice(len(pq_tuple), p=pq_tuple_fanout_norm)]
                        # prop_res = pq_tuple_choice[0]
                        # sub_par = pq_tuple_choice[1]

                        flag = False
                        for q3 in [child_par_dict[q4] for q4 in prev_Qid if q4 in child_par_dict and child_par_dict[q4] in wikidata_type_rev_dict]:
                            for p in [p1 for p1 in wikidata_type_rev_dict[q3] if p1 in sub_90_map and q3 in sub_90_map[p1]]:
                                cand_sub_par_list = []
                                cand_sub_par_score_list = []
                                for q in wikidata_type_rev_dict[q3][p]:
                                    if p in obj_90_map and q in obj_90_map[p] and q in par_child_dict and q in child_par_dict_val:
                                        ans_len = len([q1 for q1 in par_child_dict[q] if q1 in wikidata and p in wikidata[q1]])
                                        if ans_len > 1:
                                            obj_par = q3
                                            prop_res = p
                                            sub_par = q
                                            cand_sub_par_list.append(q)
                                            cand_sub_list = [q5 for q5 in par_child_dict[sub_par] if q5 in wikidata and prop_res in wikidata[q5]]
                                            cand_sub_list_score = list()
                                            for sub in cand_sub_list:
                                                cand_sub_list_score.append(len([q5 for q5 in wikidata[sub][prop_res] if q5 in child_par_dict and child_par_dict[q5] == obj_par]))
                                            cand_sub_par_score_list.append(len([x for x in cand_sub_list_score if x > 1]))
                                if len(cand_sub_par_list) > 0 and np.count_nonzero(cand_sub_par_score_list) >= 1:
                                    obj_par = q3
                                    prop_res = p
                                    # sub_par = cand_sub_par_list[cand_sub_par_score_list.index(max(cand_sub_par_score_list))]
                                    sub_par = random.choice(cand_sub_par_list)
                                    flag = True
                                    break

                                if flag:
                                    break
                            if flag:
                                break

                        if not flag:
                            prev_ques_failed = True
                            # ques_type_id = 2
                            continue
                        ques = random.choice(plu_obj_annot_wh[prop_res])
                        qualifier_dict = {2:['min','max'], 3:['atleast','atmost','exactly','around','approximately'], 4:['more','less','greater','lesser','around the same','approximately the same'],5:['atleast','atmost','exactly','around','approximately'],6:['more','less','greater','lesser','around the same','approximately the same']}
                        qualifier_choice = random.choice(qualifier_dict[count_ques_sub_type])
                        ques = sing_basic2count_based(ques, qualifier_choice, count_ques_sub_type)
                        ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))
                        
                        cand_sub_list = list(set([q for q in par_child_dict[sub_par] if q in wikidata and prop_res in wikidata[q]]))
                        if len(cand_sub_list) > args.count_ques_sub_thresh:
                            prev_ques_failed = True
                            continue

                        cand_sub_list_score = {}
                        for sub in cand_sub_list:
                            cand_sub_list_score[sub] = len([q for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q] == obj_par])

                        cand_sub_list_score_arr = np.asarray(cand_sub_list_score.values())

                        if count_ques_sub_type == 2:                            

                            if qualifier_choice == 'min':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x]==min(cand_sub_list_score.values())]
                            elif qualifier_choice == 'max':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x]==max(cand_sub_list_score.values())]

                            ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))

                            tpl_set = []

                            for sub in ans_list:
                                tpl_set.extend([(sub, prop_res, q) for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q] == obj_par])

                            tpl_regex = ['(%s,%s,%s)' % ('c(%s)' % sub_par ,prop_res,'|'.join(['c(%s)'% x for x in [obj_par]]))]

                            if args.update_counter:
                                tpl_c.update(tpl_set)

                            if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                prev_ques_failed = True
                                ques_type_id = 2
                                continue
                            ans_list_full = ans_list

                            if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                ans_list_t = [ans_list[i] for i in sort_index]
                                ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                            ans = ', '.join([item_data[x] for x in ans_list])
                            ans_entity_list = ans_list

                        elif count_ques_sub_type == 3 or count_ques_sub_type == 5:

                            flag = True
                            for n in np.random.permutation(np.arange(1,max(cand_sub_list_score.values())+1)):
                                n = int(n)
                                if qualifier_choice == 'atleast':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] >= n]
                                elif qualifier_choice == 'atmost':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] <= n]
                                elif qualifier_choice == 'exactly':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] == n]
                                elif qualifier_choice == 'around' or qualifier_choice == 'approximately':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > (n - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (n + np.std(cand_sub_list_score_arr))]

                                if len(ans_list) > 0:
                                    N = n
                                    flag = False
                                    break
                            if flag:
                                prev_ques_failed = True
                                continue

                            # if random.random() > 0.5:
                            #     N_str = inf_eng.number_to_words(int(N))
                            # else:
                            #     N_str = str(int(N))
                            N_str = str(int(N))
                            ques = ques.replace(' N ',' %s ' % N_str)

                            if qualifier_choice == 'atleast':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] >= N]
                            elif qualifier_choice == 'atmost':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] <= N]
                            elif qualifier_choice == 'exactly':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] == N]
                            elif qualifier_choice == 'around' or qualifier_choice == 'approximately':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > (N - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (N + np.std(cand_sub_list_score_arr))]

                            if count_ques_sub_type == 3:  
                                # ans_list = [q for q in ans_list if ent_c[q]<=args.entity_thresh]
                                if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                    prev_ques_failed = True
                                    ques_type_id = 2
                                    continue
                                ans_list_full = ans_list

                                if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                    ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                    sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                    ans_list_t = [ans_list[i] for i in sort_index]
                                    ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                                ans = ', '.join([item_data[x] for x in ans_list])
                                ans_entity_list = ans_list
                            elif count_ques_sub_type == 5:
                                # ans = str(len(ans_list))
                                n = len(ans_list)
                                ans_list_full = ans_list
                                # if random.random() > 0.5:
                                #     ans = inf_eng.number_to_words(int(n))
                                # else:
                                #     ans = str(int(n))
                                ans = str(int(n))
                                ans_entity_list = []

                            tpl_set = []

                            for sub in ans_list:
                                tpl_set.extend([(sub, prop_res, q) for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q] == obj_par])

                            tpl_regex = ['(%s,%s,%s)' % ('c(%s)' % sub_par ,prop_res,'|'.join(['c(%s)'% x for x in [obj_par]]))]

                            if args.update_counter:
                                tpl_c.update(tpl_set)

                            if N > 1:
                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))
                            else:
                                ques = ques.replace('OPPS',child_par_dict_name_2[obj_par])
                            

                        elif count_ques_sub_type == 4 or count_ques_sub_type == 6:

                            flag = True
                            for z in random_shuffle(cand_sub_list):
                                Z_score = cand_sub_list_score[z]

                                if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > Z_score]
                                elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] < Z_score]
                                elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > (Z_score - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (Z_score + np.std(cand_sub_list_score_arr))]

                                if len(ans_list) > 1:
                                    Z = z
                                    flag = False
                                    break
                            if flag:
                                prev_ques_failed = True
                                continue

                            ques = ques.replace('Z', item_data[Z])
                            
                            Z_score = cand_sub_list_score[Z]                           

                            if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > Z_score]
                            elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] < Z_score]
                            elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > (Z_score - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (Z_score + np.std(cand_sub_list_score_arr))]

                            if count_ques_sub_type == 4:
                                # ans_list = [q for q in ans_list if ent_c[q]<=args.entity_thresh]
                                if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                    prev_ques_failed = True
                                    ques_type_id = 2
                                    continue
                                ans_list_full = ans_list

                                if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                    ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                    sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                    ans_list_t = [ans_list[i] for i in sort_index]
                                    ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                                ans = ', '.join([item_data[x] for x in ans_list])
                                ans_entity_list = ans_list
                                
                                if len(ans_list) == 0:
                                    ans = 'None'
                            else:
                                # ans = str(len(ans_list))
                                n = len(ans_list)
                                ans_list_full = ans_list
                                # if random.random() > 0.5:
                                #     ans = inf_eng.number_to_words(int(n))
                                # else:
                                #     ans = str(int(n))
                                ans = str(int(n))
                                ans_entity_list = []

                            tpl_set = []

                            # try:
                            for sub in ans_list:
                                tpl_set.extend([(sub, prop_res, q) for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q] == obj_par])

                            tpl_regex = ['(%s,%s,%s)' % ('c(%s)' % sub_par, prop_res,'|'.join(['c(%s)'% x for x in [obj_par]]))]

                            # except:
                            #     f1 = open(os.path.join(args.out_dir,'QA_%s_log.txt' % args.save_dir_id),'a')
                            #     f1.write('sub = %s prop_res = %s\n' % (sub, prop_res))
                            #     f1.close()
                            #     prev_ques_failed = True
                            #     continue

                            if args.update_counter:
                                tpl_c.update(tpl_set)
                            ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))

                # if args.use_regex and len(set(tpl_regex).intersection(set(regex_ques_7))) > 0:
                #     ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23])
                #     prev_ques_failed = True
                #     continue

                if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                    prev_ques_failed = True
                    ques_type_id = 2
                    continue

                dict1 = {}
                dict1['speaker'] = 'USER'
                dict1['utterance'] = ques
                dict1['ques_type_id'] = ques_type_id_save
                # dict1['last_ques_type_id_save'] = last_ques_type_id_save
                dict1['count_ques_type'] = count_ques_type
                dict1['count_ques_sub_type'] = count_ques_sub_type
                dict1['relations'] = [prop_res]
                dict1['is_incomplete'] = 0

                if count_ques_sub_type == 1:
                    dict1['entities'] = [Qid]
                    if args.update_counter:
                        ent_c.update([Qid])
                elif count_ques_sub_type in [4,6]:
                    dict1['entities'] = [Z]
                    if args.update_counter:
                        ent_c.update([Z])
                else:
                    dict1['entities'] = []
                    if args.update_counter:
                        ent_c.update(ans_entity_list)


                #**********************************************************
                if count_ques_sub_type in [1,7]:
                    dict1['Qid'] = Qid
                    dict1['prop_Qid_par'] = prop_Qid_par
                    dict1['prop_res'] = prop_res
                elif count_ques_sub_type in [2,3,4,5,6,8,9]:
                    dict1['obj_par'] = obj_par
                    dict1['sub_par'] = sub_par
                    dict1['prop_res'] = prop_res
                    dict1['qualifier_choice'] = qualifier_choice
                    if count_ques_sub_type in [3,5]:
                        dict1['N'] = N
                    elif count_ques_sub_type in [4,6,8,9]:
                        dict1['Z'] = Z
                        # dict1['Z_score'] = Z_score
                        # if count_ques_type == 1:
                        #     dict1['cand_obj_list_score'] = cand_obj_list_score
                        # else:
                        #     dict1['cand_sub_list_score'] = cand_sub_list_score

                if count_ques_sub_type == 1:
                    description = 'Quantitative|Count|Single entity type'
                elif count_ques_sub_type == 2:
                    description = 'Quantitative|Min/Max|Single entity type'
                elif count_ques_sub_type == 3:
                    description = 'Quantitative|Atleast/ Atmost/ Approx. the same/Equal|Single entity type'
                elif count_ques_sub_type == 4:
                    description = 'Comparative|More/Less|Single entity type'
                elif count_ques_sub_type == 5:
                    description = 'Quantitative|Count over Atleast/ Atmost/ Approx. the same/Equal|Single entity type'
                elif count_ques_sub_type == 6:
                    description = 'Comparative|Count over More/Less|Single entity type'
                elif count_ques_sub_type == 7:
                    description = 'Quantitative|Count|Single entity type|Indirect'
                elif count_ques_sub_type == 8:
                    description = 'Comparative|More/Less|Single entity type|Indirect'
                elif count_ques_sub_type == 9:
                    description = 'Comparative|Count over More/Less|Single entity type|Indirect'
                dict1['description'] = description
                #**********************************************************
                dict1['signature'] = get_dict_signature(dict1.copy())
                if dict1['signature'] in regex_ques_all:
                    ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23])
                    prev_ques_failed = True
                    continue
                dialog_list.append(dict1.copy())
                
                if count_ques_sub_type not in [7,8,9] or (count_ques_sub_type in [7,8,9] and len(dialog_list[-2]['entities'])==1):
                    dict1 = {}
                    dict1['speaker'] = 'SYSTEM'
                    dict1['utterance'] = ans
                    dict1['entities'] = ans_entity_list[:]
                    dict1['active_set'] = tpl_regex[:]
                    dict1['ans_list_full'] = ans_list_full
                    dict1['signature'] = get_dict_signature(dict1.copy())
                    dialog_list.append(dict1.copy())
                else:
                    dict1 = {}
                    dict1['speaker'] = 'SYSTEM'
                    dict1['utterance'] = 'Did you mean %s ?' % item_data[pred_label]
                    dict1['active_set'] = tpl_regex_extend[:] # see if last regex getting reflected
                    dict1['ans_list_full'] = copy.copy(dialog_list[-1]['entities'])
                    dict1['entities'] = [pred_label]
                    dict1['relations'] = []
                    if count_ques_sub_type == 7:
                        description = 'Quantitative|Count|Single entity type|Clarification'
                    elif count_ques_sub_type == 8:
                        description = 'Comparative|More/Less|Single entity type|Clarification'
                    elif count_ques_sub_type == 9:
                        description = 'Comparative|Count over More/Less|Single entity type|Clarification'
                    dict1['description'] = description
                    dict1['signature'] = get_dict_signature(dict1.copy())
                    dialog_list.append(dict1.copy())

                    if Qid == pred_label:
                        dict1 = {}
                        dict1['speaker'] = 'USER'
                        dict1['utterance'] = 'Yes'
                        dialog_list.append(dict1.copy())
                    else:
                        dict1 = {}
                        dict1['speaker'] = 'USER'
                        dict1['utterance'] = 'No, I meant %s. Could you tell me the answer for that?' % item_data[Qid]
                        dict1['entities'] = [Qid]
                        dialog_list.append(dict1.copy())

                    dict1 = {}
                    dict1['speaker'] = 'SYSTEM'
                    dict1['utterance'] = ans
                    dict1['entities'] = ans_entity_list[:]
                    dict1['active_set'] = tpl_regex[:]
                    dict1['ans_list_full'] = ans_list_full
                    dict1['signature'] = get_dict_signature(dict1.copy())
                    dialog_list.append(dict1.copy())

                
                # *******************************************************************
                if random.random() > 0.3: # change thresh later
                    if count_ques_type == 1:
                        if count_ques_sub_type in [4,6]:
                            cand_obj_list = list(set([q for q in par_child_dict[obj_par] if q in reverse_dict and prop_res in reverse_dict[q]]))

                            cand_obj_list_score = {}
                            for obj in cand_obj_list:
                                cand_obj_list_score[obj] = len([q for q in reverse_dict[obj][prop_res] if q in child_par_dict and child_par_dict[q] == sub_par])

                            cand_obj_list_score_arr = np.asarray(cand_obj_list_score.values())

                            flag = True
                            for z in random_shuffle(cand_obj_list):
                                Z_score = cand_obj_list_score[z]
                                if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > Z_score]
                                elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] < Z_score]
                                elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > (Z_score - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[x] < (Z_score + np.std(cand_obj_list_score_arr))]

                                if len(ans_list) > 1 and z != dialog_list[-2]['Z']:
                                    Z = z
                                    flag = False
                                    break
                            if flag:
                                # prev_ques_failed = True
                                continue

                            pprase_list = ['what about', 'also tell me about', 'how about']
                            pp = random.choice(pprase_list)
                            ques = 'And %s %s?' % (pp, item_data[Z])

                            Z_score = cand_obj_list_score[Z]
                            
                            if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > Z_score]
                            elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] < Z_score]
                            elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > (Z_score - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[x] < (Z_score + np.std(cand_obj_list_score_arr))]

                            if count_ques_sub_type == 4:
                                # ans_list = [q for q in ans_list if ent_c[q]<=args.entity_thresh]

                                if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                    prev_ques_failed = True
                                    ques_type_id = 2
                                    continue
                                ans_list_full = ans_list

                                if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                    ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                    sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                    ans_list_t = [ans_list[i] for i in sort_index]
                                    ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                                ans_entity_list = ans_list
                                ans = ', '.join([item_data[x] for x in ans_list])

                                if len(ans_list) == 0:
                                    ans = 'None'
                            elif count_ques_sub_type == 6:
                                # ans = str(len(ans_list))
                                n = len(ans_list)
                                ans_list_full = ans_list
                                # if random.random() > 0.5:
                                #     ans = inf_eng.number_to_words(int(n))
                                # else:
                                #     ans = str(int(n))
                                ans = str(int(n))
                                ans_entity_list = []

                            tpl_set = []

                            # try:
                            for obj in ans_list:
                                tpl_set.extend([(q, prop_res, obj) for q in reverse_dict[obj][prop_res] if q in child_par_dict and child_par_dict[q] == sub_par])

                            tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par]]),prop_res,'c(%s)' % obj_par)]
                            # except:
                            #     f1 = open(os.path.join(args.out_dir,'QA_%s_log.txt' % args.save_dir_id),'a')
                            #     f1.write('obj = %s prop_res = %s\n' % (obj, prop_res))
                            #     f1.close()
                            #     prev_ques_failed = True
                            #     continue
                            if args.update_counter:
                                tpl_c.update(tpl_set)

                        elif count_ques_sub_type == 1:
                            valid_obj = [q for q in par_child_dict[prop_Qid_par] if q in reverse_dict and prop_res in reverse_dict[q]]
                            valid_sub = [sub for qid in valid_obj for sub in reverse_dict[qid][prop_res] if sub != Qid]
                            
                            if len(valid_sub) == 0:
                                # prev_ques_failed = True
                                ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # No clarification question follows a failed question
                                continue

                            sub_choice = random.choice(valid_sub)
                            Qid = sub_choice # for updating d

                            pprase_list = ['what about', 'also tell me about', 'how about']
                            pp = random.choice(pprase_list)

                            ques = 'And %s %s?' % (pp, item_data[sub_choice])
                            ans_list = [q for q in wikidata[sub_choice][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                            ans_list_full = copy.copy(ans_list)

                            N = len(ans_list)

                            # if random.random() > 0.5:
                            #     ans = inf_eng.number_to_words(int(N))
                            # else:
                            #     ans = str(int(N))
                            ans = str(int(N))

                            if args.update_counter:
                                ent_c.update([Qid])

                            ent_c_plus += (len(ans_list)+1)
                            tpl_set = [(Qid, prop_res, q) for q in ans_list]
                            tpl_regex = ['(%s,%s,%s)' % (Qid,prop_res,'|'.join(['c(%s)'% x for x in [prop_Qid_par]]))]
                            ans_list = []

                            if args.update_counter:
                                tpl_c.update(tpl_set)

                    if count_ques_type == 2:
                        if count_ques_sub_type in [4,6]:
                            cand_sub_list = list(set([q for q in par_child_dict[sub_par] if q in wikidata and prop_res in wikidata[q]]))
                            cand_sub_list_score = {}
                            
                            for sub in cand_sub_list:
                                cand_sub_list_score[sub] = len([q for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q] == obj_par])

                            cand_sub_list_score_arr = np.asarray(cand_sub_list_score.values())

                            flag = True
                            for z in random_shuffle(cand_sub_list):
                                Z_score = cand_sub_list_score[z]

                                if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > Z_score]
                                elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] < Z_score]
                                elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > (Z_score - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (Z_score + np.std(cand_sub_list_score_arr))]

                                if len(ans_list) > 1 and z != dialog_list[-2]['Z']:
                                    Z = z
                                    flag = False
                                    break
                            if flag:
                                # prev_ques_failed = True
                                continue

                            pprase_list = ['what about', 'also tell me about', 'how about']
                            pp = random.choice(pprase_list)
                            ques = 'And %s %s?' % (pp, item_data[Z])
                            
                            Z_score = cand_sub_list_score[Z]                           

                            if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > Z_score]
                            elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] < Z_score]
                            elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > (Z_score - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (Z_score + np.std(cand_sub_list_score_arr))]

                            if count_ques_sub_type == 4:
                                # ans_list = [q for q in ans_list if ent_c[q]<=args.entity_thresh]

                                if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                    prev_ques_failed = True
                                    ques_type_id = 2
                                    continue
                                ans_list_full = ans_list

                                if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                    ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                    sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                    ans_list_t = [ans_list[i] for i in sort_index]
                                    ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                                ans = ', '.join([item_data[x] for x in ans_list])
                                ans_entity_list = ans_list
                                
                                if len(ans_list) == 0:
                                    ans = 'None'
                            else:
                                # ans = str(len(ans_list))
                                n = len(ans_list)
                                ans_list_full = ans_list
                                # if random.random() > 0.5:
                                #     ans = inf_eng.number_to_words(int(n))
                                # else:
                                #     ans = str(int(n))
                                ans = str(int(n))
                                ans_entity_list = []

                            tpl_set = []

                            # try:
                            for sub in ans_list:
                                tpl_set.extend([(sub, prop_res, q) for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q] == obj_par])

                            tpl_regex = ['(%s,%s,%s)' % ('c(%s)' % sub_par, prop_res,'|'.join(['c(%s)'% x for x in [obj_par]]))]

                            # except:
                            #     f1 = open(os.path.join(args.out_dir,'QA_%s_log.txt' % args.save_dir_id),'a')
                            #     f1.write('sub = %s prop_res = %s\n' % (sub, prop_res))
                            #     f1.close()
                            #     prev_ques_failed = True
                            #     continue

                            if args.update_counter:
                                tpl_c.update(tpl_set)

                        elif count_ques_sub_type == 1:
                            valid_sub = [q for q in par_child_dict[prop_Qid_par] if q in wikidata and prop_res in wikidata[q]]
                            valid_obj = [obj for qid in valid_sub for obj in wikidata[qid][prop_res] if obj != Qid]
                            
                            if len(valid_obj) == 0:
                                # prev_ques_failed = True
                                ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # No clarification question follows a failed question
                                continue

                            obj_choice = random.choice(valid_obj)
                            Qid = obj_choice # for updating d

                            pprase_list = ['what about', 'also tell me about', 'how about']
                            pp = random.choice(pprase_list)

                            ques = 'And %s %s?' % (pp, item_data[obj_choice])
                            ans_list = [q for q in reverse_dict[obj_choice][prop_res] if q in child_par_dict and child_par_dict[q]==prop_Qid_par]
                            ans_list_full = copy.copy(ans_list)

                            N = len(ans_list)

                            # if random.random() > 0.5:
                            #     ans = inf_eng.number_to_words(int(N))
                            # else:
                            #     ans = str(int(N))
                            ans = str(int(N))

                            if args.update_counter:
                                ent_c.update([Qid])

                            ent_c_plus += (len(ans_list)+1)
                            tpl_set = [(q, prop_res, Qid) for q in ans_list]
                            if args.update_counter:
                                tpl_c.update(tpl_set)

                            tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [prop_Qid_par]]),prop_res,Qid)]
                            ans_list = []

                    if count_ques_sub_type in [1,4,6]:
                        # if args.use_regex and len(set(tpl_regex).intersection(set(regex_ques_7))) > 0:
                        #     ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23])
                        #     # prev_ques_failed = True
                        #     continue

                        if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                            prev_ques_failed = True
                            ques_type_id = 2
                            continue

                        dict1 = {}
                        dict1['speaker'] = 'USER'
                        dict1['utterance'] = ques
                        dict1['ques_type_id'] = ques_type_id_save
                        # dict1['last_ques_type_id_save'] = 7
                        dict1['count_ques_type'] = count_ques_type
                        dict1['count_ques_sub_type'] = count_ques_sub_type
                        dict1['relations'] = [prop_res]
                        dict1['is_incomplete'] = 1

                        #**************************************************************************
                        if count_ques_sub_type == 1:
                            description = 'Quantitative|Count|Single entity type|Incomplete'
                        elif count_ques_sub_type == 4:
                            description = 'Comparative|More/Less|Single entity type|Incomplete'
                        elif count_ques_sub_type == 6:
                            description = 'Comparative|Count over More/Less|Single entity type|Incomplete'

                        dict1['description'] = description
                        #**************************************************************************

                        if count_ques_sub_type == 1:
                            dict1['entities'] = [Qid]
                            if args.update_counter:
                                ent_c.update([Qid])
                            dict1['Qid'] = Qid
                            dict1['prop_Qid_par'] = prop_Qid_par
                            dict1['prop_res'] = prop_res

                        elif count_ques_sub_type in [4,6]:
                            dict1['entities'] = [Z]
                            if args.update_counter:
                                ent_c.update([Z])

                            dict1['obj_par'] = obj_par
                            dict1['sub_par'] = sub_par
                            dict1['prop_res'] = prop_res
                            dict1['qualifier_choice'] = qualifier_choice
                            dict1['Z'] = Z

                        else:
                            dict1['entities'] = []
                            if args.update_counter:
                                ent_c.update(ans_entity_list)
                        dict1['signature'] = get_dict_signature(dict1.copy())
                        if dict1['signature'] in regex_ques_all:
                            ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23])
                            prev_ques_failed = True
                            continue
                        dialog_list.append(dict1.copy())
                        

                        dict1 = {}
                        dict1['speaker'] = 'SYSTEM'
                        dict1['utterance'] = ans
                        dict1['entities'] = ans_entity_list[:]
                        dict1['active_set'] = tpl_regex[:]
                        dict1['ans_list_full'] = ans_list_full
                        dict1['signature'] = get_dict_signature(dict1.copy())
                        dialog_list.append(dict1.copy())



            elif ques_type_id == 8: # count-set-based question
                sec_ques_type = sec_ques_sub_type = 0

                count_ques_type = np.random.choice(np.array([1,2])) # sub-based or obj-based (add p)
                count_ques_sub_type = np.random.choice(np.array([1,2,3,4,5,6,7,8,9,10]),p=[0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]) #(add p)

                # count_ques_sub_type = random.choice([9,10])
                set_op = np.random.choice(np.array([1,2])) # 1: and 2: or
                ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23]) # ques type_id of next question (Secondary)
                # print 'ques_type_id_save = %d' % ques_type_id_save

                if count_ques_type == 1: # sub-based
                    if count_ques_sub_type == 1: # basic form
                        sec_ques_type = sec_ques_sub_type = 0 # Direct ques. is not a secondary ques.

                        # Qid = last_Qid
                        # obj_par = prop_Qid_par
                        # valid_obj = [q for q in reverse_dict if q in child_par_dict and child_par_dict[q]==obj_par]
                        # if len(valid_obj) > args.set_obj_thresh:
                        #     valid_obj = random.sample(valid_obj,args.set_obj_thresh)

                        # ps_tuple = [(p,s) for q in valid_obj for p in reverse_dict[q] for s in reverse_dict[q][p] if p in wikidata[Qid] and p in sub_90_map and obj_par in sub_90_map[p] and s != Qid]

                        # if len(ps_tuple) > args.ps_tuple_thresh: # randomly sample args.ps_tuple_thresh # of entries from list if greater than threshold
                        #     ps_tuple = random.sample(ps_tuple,args.ps_tuple_thresh)

                        # ps_tuple_choice = random.choice(ps_tuple)
                        # prop_res = ps_tuple_choice[0]
                        # Qid_2 = ps_tuple_choice[1]
                        flag = False
                        for p in random_shuffle([p1 for p1 in wikidata[Qid] if p1 in sub_90_map and p1 in wikidata_type_dict[child_par_dict[Qid]]]):
                            for q in random_shuffle([q3 for q3 in wikidata_type_dict[child_par_dict[Qid]][p] if q3 in sub_90_map[p] and q3 in child_par_dict_val]):
                                for q1 in random_shuffle([q4 for q4 in wikidata_type_rev_dict[q][p] if q4 in par_child_dict and p in wikidata_type_dict[q4]]):
                                    try:
                                        l1 = [q5 for q5 in par_child_dict[q1] if q5 in wikidata and p in wikidata[q5] if q5 != Qid]
                                        if len(l1) == 0:
                                            continue
                                        x2 = random.choice(l1)
                                        # set_A = [q2 for q2 in wikidata[Qid][p] if q2 in child_par_dict and child_par_dict[q2]==q]
                                        # set_B = [q2 for q2 in wikidata[x2][p] if q2 in child_par_dict and child_par_dict[q2]==q]
                                        set_A = set(wikidata[Qid][p]) & set(par_child_dict[q])
                                        set_B = set(wikidata[x2][p]) & set(par_child_dict[q])
                                        if set_op == 1:
                                            ans_len = len(set(set_A).intersection(set_B))
                                        elif set_op == 2:
                                            ans_len = len(set(set_A).union(set_B))
                                        if ans_len > 1:
                                            prop_res = p
                                            obj_par = q
                                            Qid_2 = x2
                                            flag = True
                                            break
                                    except:
                                        logging.exception('Something aweful happened')
                                    if flag:
                                        break
                                if flag:
                                    break
                            if flag:
                                break

                        if not flag:
                            prev_ques_failed = True
                            # ques_type_id = 2
                            continue
                        ques = random.choice(plu_sub_annot_wh[prop_res])    
                        ques = sing_basic2count_set_based(ques, '', set_op, count_ques_sub_type)        
                        ques = ques.replace('XXX_1',item_data[Qid])
                        ques = ques.replace('XXX_2',item_data[Qid_2])
                        ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))
                        
                        # set_A = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==obj_par]
                        # set_B = [q for q in wikidata[Qid_2][prop_res] if q in child_par_dict and child_par_dict[q]==obj_par]

                        set_A = list(set(wikidata[Qid][prop_res]) & set(par_child_dict[obj_par]))
                        set_B = list(set(wikidata[Qid_2][prop_res]) & set(par_child_dict[obj_par]))

                        if set_op == 1:
                            ans_list = list(set(set_A).intersection(set_B))
                            N = len(set(set_A).intersection(set_B))
                        elif set_op == 2:
                            ans_list = list(set(set_A).union(set_B))
                            N = len(set(set_A).union(set_B))

                        # if random.random() > 0.5:
                        #     ans = inf_eng.number_to_words(int(N))
                        # else:
                        #     ans = str(int(N))
                        ans = str(int(N))
                        ans_list_full = ans_list

                        tpl_set = []
                        tpl_set.extend([(Qid, prop_res, q) for q in set_A])
                        tpl_set.extend([(Qid_2, prop_res, q) for q in set_B])

                        tpl_regex = ['(%s,%s,%s)' % (Qid,prop_res,'|'.join(['c(%s)'% x for x in [obj_par]]))]
                        tpl_regex.extend(['(%s,%s,%s)' % (Qid_2,prop_res,'|'.join(['c(%s)'% x for x in [obj_par]]))])

                        if args.update_counter:
                            tpl_c.update(tpl_set)
                        ans_entity_list = []

                    elif count_ques_sub_type == 2:
                        sec_ques_type = sec_ques_sub_type = 0 # Direct ques. is not a secondary ques.

                        ps_tuple = [(p, set([child_par_dict[qid] for qid in wikidata[Qid][p] if qid in child_par_dict])) for p in wikidata[Qid] if p in sub_90_map]
                        ps_tuple_filt = [t for t in ps_tuple if len(t[1])>=2]

                        if len(ps_tuple_filt) == 0:
                            prev_ques_failed = True
                            # ques_type_id = 2
                            continue
                        ps_tuple_choice = random.choice(ps_tuple_filt)
                        prop_res = ps_tuple_choice[0]
                        obj_pars = random.sample(ps_tuple_choice[1], 2)
                        obj_par_1 = obj_pars[0]
                        obj_par_2 = obj_pars[1]

                        prop_Qid_par = random.choice(plu_sub_annot_wh[prop_res])
                        ques = random.choice(plu_sub_annot_wh[prop_res])
                        ques = sing_basic2count_set_based(ques, '', set_op, count_ques_sub_type)        
                        ques = ques.replace('XXX',item_data[Qid])
                        ques = ques.replace('OPP_1s',sing2plural(child_par_dict_name_2[obj_par_1]))
                        ques = ques.replace('OPP_2s',sing2plural(child_par_dict_name_2[obj_par_2]))

                        # set_A = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==obj_par_1]
                        # set_B = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==obj_par_2]
                        set_A = list(set(wikidata[Qid][prop_res]) & set(par_child_dict[obj_par_1]))
                        set_B = list(set(wikidata[Qid][prop_res]) & set(par_child_dict[obj_par_2]))

                        if set_op == 1:
                            ans = '%s %s and %s %s' % (str(len(set_A)), sing2plural(child_par_dict_name_2[obj_par_1]), str(len(set_B)), sing2plural(child_par_dict_name_2[obj_par_2]))
                        elif set_op == 2:
                            N = len(set(set_A).union(set_B))

                            # if random.random() > 0.5:
                            #     ans = inf_eng.number_to_words(int(N))
                            # else:
                            #     ans = str(int(N))
                            ans = str(int(N))

                        #************************************************************
                        if child_par_dict_name_2[obj_par_1] == child_par_dict_name_2[obj_par_2]:
                            pattern_1 = '%s and %s' % (child_par_dict_name_2[obj_par_1], child_par_dict_name_2[obj_par_2])
                            pattern_2 = '%s or %s' % (child_par_dict_name_2[obj_par_1], child_par_dict_name_2[obj_par_2])
                            ques = ques.replace(pattern_1, child_par_dict_name_2[obj_par_1])
                            ques = ques.replace(pattern_2, child_par_dict_name_2[obj_par_1])
                            N = len(set(set_A).union(set_B))
                            ans = str(int(N))
                        #************************************************************


                        ans_list = list(set(set_A).union(set_B))
                        ans_list_full = ans_list

                        tpl_set = []
                        tpl_set.extend([(Qid, prop_res, q) for q in set_A])
                        tpl_set.extend([(Qid, prop_res, q) for q in set_B])

                        if args.update_counter:
                            tpl_c.update(tpl_set)

                        tpl_regex = ['(%s,%s,%s)' % (Qid,prop_res,'|'.join(['c(%s)'% x for x in [obj_par_1]]))]
                        tpl_regex.extend(['(%s,%s,%s)' % (Qid,prop_res,'|'.join(['c(%s)'% x for x in [obj_par_2]]))])
                        ans_entity_list = []

                    elif count_ques_sub_type == 8:
                        if len(dialog_list[-1]['entities']) == 0:
                            prev_ques_failed = True
                            continue

                        Qid = random.choice(dialog_list[-1]['entities']) # true entity
                        pred_label = random.choice(dialog_list[-1]['entities'])

                        ps_tuple = [(p, set([child_par_dict[qid] for qid in wikidata[Qid][p] if qid in child_par_dict])) for p in wikidata[Qid] if p in sub_90_map]
                        ps_tuple_filt = [t for t in ps_tuple if len(t[1])>=2]

                        if len(ps_tuple_filt) == 0:
                            prev_ques_failed = True
                            # ques_type_id = 2
                            continue
                        ps_tuple_choice = random.choice(ps_tuple_filt)
                        prop_res = ps_tuple_choice[0]
                        obj_pars = random.sample(ps_tuple_choice[1], 2)
                        obj_par_1 = obj_pars[0]
                        obj_par_2 = obj_pars[1]

                        prop_Qid_par = random.choice(plu_sub_annot_wh[prop_res])
                        ques = random.choice(plu_sub_annot_wh[prop_res])
                        ques = sing_basic2count_set_based(ques, '', set_op, 2)        
                        ques = ques.replace('XXX','that %s' % child_par_dict_name_2[child_par_dict[Qid]])
                        ques = ques.replace('OPP_1s',sing2plural(child_par_dict_name_2[obj_par_1]))
                        ques = ques.replace('OPP_2s',sing2plural(child_par_dict_name_2[obj_par_2]))

                        # set_A = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==obj_par_1]
                        # set_B = [q for q in wikidata[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==obj_par_2]
                        set_A = list(set(wikidata[Qid][prop_res]) & set(par_child_dict[obj_par_1]))
                        set_B = list(set(wikidata[Qid][prop_res]) & set(par_child_dict[obj_par_2]))

                        if set_op == 1:
                            ans = '%s %s and %s %s' % (str(len(set_A)), sing2plural(child_par_dict_name_2[obj_par_1]), str(len(set_B)), sing2plural(child_par_dict_name_2[obj_par_2]))
                        elif set_op == 2:
                            N = len(set(set_A).union(set_B))

                            # if random.random() > 0.5:
                            #     ans = inf_eng.number_to_words(int(N))
                            # else:
                            #     ans = str(int(N))
                            ans = str(int(N))

                        #************************************************************
                        if child_par_dict_name_2[obj_par_1] == child_par_dict_name_2[obj_par_2]:
                            pattern_1 = '%s and %s' % (child_par_dict_name_2[obj_par_1], child_par_dict_name_2[obj_par_2])
                            pattern_2 = '%s or %s' % (child_par_dict_name_2[obj_par_1], child_par_dict_name_2[obj_par_2])
                            ques = ques.replace(pattern_1, child_par_dict_name_2[obj_par_1])
                            ques = ques.replace(pattern_2, child_par_dict_name_2[obj_par_1])
                            N = len(set(set_A).union(set_B))
                            ans = str(int(N))
                        #************************************************************

                        ans_list = list(set(set_A).union(set_B))

                        ans_list_full = ans_list

                        tpl_set = []
                        tpl_set.extend([(Qid, prop_res, q) for q in set_A])
                        tpl_set.extend([(Qid, prop_res, q) for q in set_B])

                        if args.update_counter:
                            tpl_c.update(tpl_set)

                        tpl_regex = ['(%s,%s,%s)' % (Qid,prop_res,'|'.join(['c(%s)'% x for x in [obj_par_1]]))]
                        tpl_regex.extend(['(%s,%s,%s)' % (Qid,prop_res,'|'.join(['c(%s)'% x for x in [obj_par_2]]))])

                        tpl_regex_extend = []
                        for q in dialog_list[-1]['entities']:
                            tpl_regex.extend(['(%s,%s,%s)' % (q,prop_res,'|'.join(['c(%s)'% x for x in [obj_par_1]]))])
                            tpl_regex.extend(['(%s,%s,%s)' % (q,prop_res,'|'.join(['c(%s)'% x for x in [obj_par_2]]))])

                        ans_entity_list = []

                    elif count_ques_sub_type in [9,10]:
                        if len(dialog_list[-1]['entities']) == 0:
                            prev_ques_failed = True
                            continue

                        print 'In ques-id-8 (9,10)'
                        obj_par = child_par_dict[dialog_list[-1]['entities'][0]]
                        flag = False

                        for p in [p1 for p1 in wikidata_type_rev_dict[obj_par] if p1 in sub_90_map and obj_par in sub_90_map[p1]]:
                            cand_sub_par_list = list()
                            for q3 in wikidata_type_rev_dict[obj_par][p]:
                                if q3 in obj_90_map[p] and q3 in par_child_dict and q3 in child_par_dict_val:
                                    ans_list = [q1 for q1 in par_child_dict[obj_par] if q1 in reverse_dict and p in reverse_dict[q1]]
                                    if len(ans_list) > 1 and len(set(ans_list) & set(dialog_list[-1]['entities']))>0:
                                        cand_sub_par_list.append(q3)

                            if len(cand_sub_par_list) >= 2:
                                sub_pars_choice = np.random.choice(range(len(cand_sub_par_list)), 2, replace=False)
                                sub_par_1 = cand_sub_par_list[sub_pars_choice[0]]
                                sub_par_2 = cand_sub_par_list[sub_pars_choice[1]]
                                prop_res = p
                                flag = True

                        if not flag:
                            prev_ques_failed = True
                            print 'flag False'
                            continue

                        cand_obj_list = list(set([q for q in par_child_dict[obj_par] if q in reverse_dict and prop_res in reverse_dict[q]]))

                        if len(cand_obj_list) > args.count_ques_sub_thresh:
                            prev_ques_failed = True
                            continue

                        Z = random.choice(list(set(dialog_list[-1]['entities']) & set(cand_obj_list)))
                        Qid = Z
                        pred_label = random.choice(dialog_list[-1]['entities'])

                        cand_obj_list_score = {}
                        for obj in cand_obj_list:
                            cand_obj_list_score[obj] = len([q for q in reverse_dict[obj][prop_res] if q in child_par_dict and child_par_dict[q] in [sub_par_1, sub_par_2]])

                        cand_obj_list_score_arr = np.asarray(cand_obj_list_score.values())

                        ques = random.choice(plu_sub_annot_wh[prop_res])
                        qualifier_dict = {3:['min','max'], 4:['atleast','atmost','exactly','around','approximately'], 5:['more','less','greater','lesser','around the same','approximately the same'],6:['atleast','atmost','exactly','around','approximately'],7:['more','less','greater','lesser','around the same','approximately the same']}
                        
                        if count_ques_sub_type == 9:
                            qualifier_choice = random.choice(qualifier_dict[5])
                            ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, 5)
                        else:
                            qualifier_choice = random.choice(qualifier_dict[7])
                            ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, 7)

                        ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))

                        ques = ques.replace('Z', 'that %s' % child_par_dict_name_2[child_par_dict[Z]])
                        ques = ques.replace('SPP_1s',sing2plural(child_par_dict_name_2[sub_par_1]))
                        ques = ques.replace('SPP_2s',sing2plural(child_par_dict_name_2[sub_par_2]))

                        #************************************************************
                        if child_par_dict_name_2[sub_par_1] == child_par_dict_name_2[sub_par_2]:
                            pattern_1 = '%s and %s' % (child_par_dict_name_2[sub_par_1], child_par_dict_name_2[sub_par_2])
                            pattern_2 = '%s or %s' % (child_par_dict_name_2[sub_par_1], child_par_dict_name_2[sub_par_2])
                            ques = ques.replace(pattern_1, child_par_dict_name_2[sub_par_1])
                            ques = ques.replace(pattern_2, child_par_dict_name_2[sub_par_1])
                        #************************************************************

                        Z_score = cand_obj_list_score[Z]
                        
                        if qualifier_choice == 'more' or qualifier_choice == 'greater':
                            ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > Z_score]
                        elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                            ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] < Z_score]
                        elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                            ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > (Z_score - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[x] < (Z_score + np.std(cand_obj_list_score_arr))]

                        if count_ques_sub_type == 9:
                            # ans_list = [q for q in ans_list if ent_c[q]<=args.entity_thresh]

                            if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                prev_ques_failed = True
                                ques_type_id = 2
                                continue

                            ans_list_full = ans_list

                            if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                ans_list_t = [ans_list[i] for i in sort_index]
                                ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                            ans = ', '.join([item_data[x] for x in ans_list])
                            ans_entity_list = ans_list

                            if len(ans_list) == 0:
                                ans = 'None'
                        else:
                            # ans = str(len(ans_list))
                            n = len(ans_list)
                            ans_list_full = ans_list
                            # if random.random() > 0.5:
                            #     ans = inf_eng.number_to_words(int(n))
                            # else:
                            #     ans = str(int(n))
                            ans = str(int(n))
                            ans_entity_list = []

                        tpl_set = []

                        # try:
                        for obj in ans_list:
                            tpl_set.extend([(q, prop_res, obj) for q in reverse_dict[obj][prop_res] if q in child_par_dict and child_par_dict[q] in [sub_par_1, sub_par_2]])

                        tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par_1, sub_par_2]]),prop_res,'c(%s)' % obj_par)]
                        tpl_regex_extend = tpl_regex

                        if args.update_counter:
                            tpl_c.update(tpl_set)
                    else:
                        sec_ques_type = sec_ques_sub_type = 0

                        # flag = False
                        # for q in [child_par_dict[q3] for q3 in prev_Qid if q3 in child_par_dict and child_par_dict[q3] in wikidata_type_rev_dict]:
                        #     for p in [p1 for p1 in wikidata_type_rev_dict[q] if p1 in sub_90_map and q in sub_90_map[p1] and len(set(child_par_dict_val).intersection(wikidata_type_rev_dict[q][p1]))>=2]:
                        #         ans_len = len([q1 for q1 in par_child_dict[q] if q1 in reverse_dict and p in reverse_dict[q1]])
                        #         if ans_len > 1:
                        #             obj_par = q
                        #             prop_res = p
                        #             sub_pars = random.sample([q4 for q4 in wikidata_type_rev_dict[q][p] if q4 in child_par_dict_val],2)
                        #             sub_par_1 = sub_pars[0]
                        #             sub_par_2 = sub_pars[1]
                        #             flag = True
                        #             break
                        #     if flag:
                        #         break

                        flag = False
                        for q3 in random_shuffle([child_par_dict[q4] for q4 in prev_Qid if q4 in child_par_dict and child_par_dict[q4] in wikidata_type_rev_dict]):
                            for p in random_shuffle([p1 for p1 in wikidata_type_rev_dict[q3] if p1 in sub_90_map and q3 in sub_90_map[p1]]):
                                cand_sub_par_list = []
                                cand_sub_par_score_list = []
                                for q in random_shuffle(wikidata_type_rev_dict[q3][p]):
                                    if p in obj_90_map and q in obj_90_map[p] and q in par_child_dict and q in child_par_dict_val:
                                        ans_len = len([q1 for q1 in par_child_dict[q] if q1 in wikidata and p in wikidata[q1]])
                                        if ans_len > 1:
                                            obj_par = q3
                                            prop_res = p
                                            sub_par = q
                                            cand_sub_par_list.append(q)
                                            cand_sub_list = [q5 for q5 in par_child_dict[sub_par] if q5 in wikidata and prop_res in wikidata[q5]]
                                            cand_sub_list_score = list()
                                            for sub in cand_sub_list:
                                                cand_sub_list_score.append(len([q5 for q5 in wikidata[sub][prop_res] if q5 in child_par_dict and child_par_dict[q5] == obj_par]))
                                            cand_sub_par_score_list.append(len([x for x in cand_sub_list_score if x > 1]))
                                if len(cand_sub_par_list) > 1 and np.count_nonzero(cand_sub_par_score_list) >= 2:
                                    obj_par = q3
                                    prop_res = p
                                    # sub_pars_choice = np.random.choice(range(len(cand_sub_par_list)), 2, replace=False, p=[x*1.0/sum(cand_sub_par_score_list) for x in cand_sub_par_score_list])
                                    sub_pars_choice = np.random.choice(range(len(cand_sub_par_list)), 2, replace=False)
                                    sub_par_1 = cand_sub_par_list[sub_pars_choice[0]]
                                    sub_par_2 = cand_sub_par_list[sub_pars_choice[1]]
                                    flag = True
                                    break

                                if flag:
                                    break
                            if flag:
                                break

                        if not flag:
                            prev_ques_failed = True
                            # ques_type_id = 2
                            continue
                        # pq_tuple_choice = random.choice(pq_tuple)
                        # prop_res = pq_tuple_choice[0]
                        # sub_pars = random.sample(pq_tuple_choice[1],2)
                        # sub_par_1 = sub_pars[0]
                        # sub_par_2 = sub_pars[1]

                        ques = random.choice(plu_sub_annot_wh[prop_res])
                        qualifier_dict = {3:['min','max'], 4:['atleast','atmost','exactly','around','approximately'], 5:['more','less','greater','lesser','around the same','approximately the same'],6:['atleast','atmost','exactly','around','approximately'],7:['more','less','greater','lesser','around the same','approximately the same']}
                        qualifier_choice = random.choice(qualifier_dict[count_ques_sub_type])
                        ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, count_ques_sub_type)
                        ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))
                        ques = ques.replace('SPP_1s',sing2plural(child_par_dict_name_2[sub_par_1]))
                        ques = ques.replace('SPP_2s',sing2plural(child_par_dict_name_2[sub_par_2]))

                        #************************************************************
                        if child_par_dict_name_2[sub_par_1] == child_par_dict_name_2[sub_par_2]:
                            pattern_1 = '%s and %s' % (child_par_dict_name_2[sub_par_1], child_par_dict_name_2[sub_par_2])
                            pattern_2 = '%s or %s' % (child_par_dict_name_2[sub_par_1], child_par_dict_name_2[sub_par_2])
                            ques = ques.replace(pattern_1, child_par_dict_name_2[sub_par_1])
                            ques = ques.replace(pattern_2, child_par_dict_name_2[sub_par_1])
                        #************************************************************

                        cand_obj_list = list(set([q for q in par_child_dict[obj_par] if q in reverse_dict and prop_res in reverse_dict[q]]))
                        if len(cand_obj_list) > args.count_ques_sub_thresh:
                            prev_ques_failed = True
                            continue

                        cand_obj_list_score = {}
                        for obj in cand_obj_list:
                            cand_obj_list_score[obj] = len([q for q in reverse_dict[obj][prop_res] if q in child_par_dict and child_par_dict[q] in [sub_par_1, sub_par_2]])

                        cand_obj_list_score_arr = np.asarray(cand_obj_list_score.values())

                        if count_ques_sub_type == 3:                            
                            if qualifier_choice == 'min':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] == min(cand_obj_list_score.values())]
                                
                            elif qualifier_choice == 'max':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] == max(cand_obj_list_score.values())]

                            if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                prev_ques_failed = True
                                ques_type_id = 2
                                continue
                            ans_list_full = ans_list

                            if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                ans_list_t = [ans_list[i] for i in sort_index]
                                ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                            ans = ', '.join([item_data[x] for x in ans_list])
                            if len(ans_list) == 0:
                                ans = 'None'
                            ans_entity_list = ans_list

                            tpl_set = []

                            for obj in ans_list:
                                tpl_set.extend([(q, prop_res, obj) for q in reverse_dict[obj][prop_res] if q in child_par_dict and child_par_dict[q] in [sub_par_1, sub_par_2]])

                            tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par_1, sub_par_2]]),prop_res,'c(%s)' % obj_par)]
                            if args.update_counter:
                                tpl_c.update(tpl_set)

                        elif count_ques_sub_type == 4 or count_ques_sub_type == 6:
                            
                            flag = True
                            for n in np.random.permutation(np.arange(1,max(cand_obj_list_score.values())+1)):
                                n = int(n)
                                if qualifier_choice == 'atleast':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] >= n]
                                elif qualifier_choice == 'atmost':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] <= n]
                                elif qualifier_choice == 'exactly':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] == n]
                                elif qualifier_choice == 'around' or qualifier_choice == 'approximately':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > (n - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[x] < (n + np.std(cand_obj_list_score_arr))]

                                if len(ans_list) > 1:
                                    N = n
                                    flag = False
                                    break
                            if flag:
                                prev_ques_failed = True
                                continue

                            # if random.random() > 0.5:
                            #     N_str = inf_eng.number_to_words(int(N))
                            # else:
                            #     N_str = str(int(N))
                            N_str = str(int(N))
                            ques = ques.replace(' N ',' %s ' % N_str)

                            if qualifier_choice == 'atleast':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] >= N]
                            elif qualifier_choice == 'atmost':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] <= N]
                            elif qualifier_choice == 'exactly':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] == N]
                            elif qualifier_choice == 'around' or qualifier_choice == 'approximately':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > (N - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[x] < (N + np.std(cand_obj_list_score_arr))]

                            if count_ques_sub_type == 4:
                                # ans_list = [q for q in ans_list if ent_c[q]<=args.entity_thresh]
                                if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                    prev_ques_failed = True
                                    ques_type_id = 2
                                    continue
                                ans_list_full = ans_list

                                if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                    ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                    sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                    ans_list_t = [ans_list[i] for i in sort_index]
                                    ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                                ans = ', '.join([item_data[x] for x in ans_list])
                                if len(ans_list) == 0:
                                    ans = 'None'
                                ans_entity_list = ans_list

                            elif count_ques_sub_type == 6:
                                # ans = str(len(ans_list))
                                n = len(ans_list)
                                ans_list_full = ans_list
                                # if random.random() > 0.5:
                                #     ans = inf_eng.number_to_words(int(n))
                                # else:
                                #     ans = str(int(n))
                                ans = str(int(n))
                                ans_entity_list = []
                            tpl_set = []

                            for obj in ans_list:
                                tpl_set.extend([(q, prop_res, obj) for q in reverse_dict[obj][prop_res] if q in child_par_dict and child_par_dict[q] in [sub_par_1, sub_par_2]])

                            tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par_1, sub_par_2]]),prop_res,'c(%s)' % obj_par)]
                            if args.update_counter:
                                tpl_c.update(tpl_set)

                        elif count_ques_sub_type == 5 or count_ques_sub_type == 7:

                            flag = True
                            for z in random_shuffle(cand_obj_list):
                                Z_score = cand_obj_list_score[z]
                                if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > Z_score]
                                elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] < Z_score]
                                elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > (Z_score - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[x] < (Z_score + np.std(cand_obj_list_score_arr))]

                                if len(ans_list) > 1:
                                    Z = z
                                    flag = False
                                    break
                            if flag:
                                prev_ques_failed = True
                                continue

                            ques = ques.replace('Z', item_data[Z])

                            Z_score = cand_obj_list_score[Z]
                            
                            if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > Z_score]
                            elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] < Z_score]
                            elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > (Z_score - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[x] < (Z_score + np.std(cand_obj_list_score_arr))]

                            if count_ques_sub_type == 5:
                                # ans_list = [q for q in ans_list if ent_c[q]<=args.entity_thresh]
                                if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                    prev_ques_failed = True
                                    ques_type_id = 2
                                    continue
                                ans_list_full = ans_list

                                if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                    ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                    sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                    ans_list_t = [ans_list[i] for i in sort_index]
                                    ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                                ans = ', '.join([item_data[x] for x in ans_list])
                                ans_entity_list = ans_list

                                if len(ans_list) == 0:
                                    ans = 'None'
                            else:
                                # ans = str(len(ans_list))
                                n = len(ans_list)
                                ans_list_full = ans_list
                                # if random.random() > 0.5:
                                #     ans = inf_eng.number_to_words(int(n))
                                # else:
                                #     ans = str(int(n))
                                ans = str(int(n))
                                ans_entity_list = []

                            tpl_set = []

                            # try:
                            for obj in ans_list:
                                tpl_set.extend([(q, prop_res, obj) for q in reverse_dict[obj][prop_res] if q in child_par_dict and child_par_dict[q] in [sub_par_1, sub_par_2]])

                            tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par_1, sub_par_2]]),prop_res,'c(%s)' % obj_par)]
                            if args.update_counter:
                                tpl_c.update(tpl_set)
                            # except:
                            #     f1 = open(os.path.join(args.out_dir,'QA_%s_log.txt' % args.save_dir_id),'a')
                            #     f1.write('obj = %s prop_res = %s\n' % (obj, prop_res))
                            #     f1.close()
                            #     prev_ques_failed = True
                            #     continue
                            

                elif count_ques_type == 2: # obj-based
                    if count_ques_sub_type == 1: # basic form
                        sec_ques_type = sec_ques_sub_type = 0 # Direct ques. is not a secondary ques.
                        try:
                            assert Qid in reverse_dict
                        except:
                            Qid = random.choice([q for q in prev_Qid if q in reverse_dict and q in child_par_dict])
                        # Qid = last_Qid
                        # sub_par = prop_Qid_par
                        # valid_sub = [q for q in wikidata if q in child_par_dict and child_par_dict[q]==sub_par]
                        # if len(valid_sub) > args.set_obj_thresh:
                        #     valid_sub = random.sample(valid_sub,args.set_obj_thresh)

                        # ps_tuple = [(p,s) for q in valid_sub for p in wikidata[q] for s in wikidata[q][p] if p in wikidata[Qid] and p in sub_90_map and sub_par in sub_90_map[p] and s != Qid]

                        # if len(ps_tuple) > args.ps_tuple_thresh: # randomly sample args.ps_tuple_thresh # of entries from list if greater than threshold
                        #     ps_tuple = random.sample(ps_tuple,args.ps_tuple_thresh)

                        # ps_tuple_choice = random.choice(ps_tuple)
                        # prop_res = ps_tuple_choice[0]
                        # Qid_2 = ps_tuple_choice[1]

                        flag = False
                        for p in random_shuffle([p1 for p1 in reverse_dict[Qid] if p1 in obj_90_map and p1 in wikidata_type_rev_dict[child_par_dict[Qid]]]):
                            for q in random_shuffle([q3 for q3 in wikidata_type_rev_dict[child_par_dict[Qid]][p] if q3 in obj_90_map[p] and q3 in child_par_dict_val]):
                                for q1 in random_shuffle([q4 for q4 in wikidata_type_dict[q][p] if q4 in par_child_dict and p in wikidata_type_rev_dict[q4]]):
                                    try:
                                        l1 = [q5 for q5 in par_child_dict[q1] if q5 in reverse_dict and p in reverse_dict[q5] if q5 != Qid]
                                        if len(l1) == 0:
                                            continue
                                        y2 = random.choice(l1)
                                        # set_A = [q2 for q2 in reverse_dict[Qid][p] if q2 in child_par_dict and child_par_dict[q2]==q]
                                        # set_B = [q2 for q2 in reverse_dict[y2][p] if q2 in child_par_dict and child_par_dict[q2]==q]
                                        set_A = set(reverse_dict[Qid][p]) & set(par_child_dict[q])
                                        set_B = set(reverse_dict[y2][p]) & set(par_child_dict[q])
                                        if set_op == 1:
                                            ans_len = len(set(set_A).intersection(set_B))
                                        elif set_op == 2:
                                            ans_len = len(set(set_A).union(set_B))
                                        if ans_len > 1:
                                            prop_res = p
                                            sub_par = q
                                            Qid_2 = y2
                                            flag = True
                                            break   
                                    except:
                                        logging.exception('Something aweful happened')
                                    if flag:
                                        break
                                if flag:
                                    break
                            if flag:
                                break
                        if not flag:
                            prev_ques_failed = True
                            # ques_type_id = 2
                            continue
                        ques = random.choice(plu_obj_annot_wh[prop_res])
                        ques = sing_basic2count_set_based(ques, '', set_op, count_ques_sub_type)        
                        ques = ques.replace('YYY_1',item_data[Qid])
                        ques = ques.replace('YYY_2',item_data[Qid_2])
                        ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))
                        
                        # set_A = [q for q in reverse_dict[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==sub_par]
                        # set_B = [q for q in reverse_dict[Qid_2][prop_res] if q in child_par_dict and child_par_dict[q]==sub_par]
                        set_A = list(set(reverse_dict[Qid][prop_res]) & set(par_child_dict[sub_par]))
                        set_B = list(set(reverse_dict[Qid_2][prop_res]) & set(par_child_dict[sub_par]))

                        if set_op == 1:
                            ans_list = list(set(set_A).intersection(set_B))
                            N = len(set(set_A).intersection(set_B))
                        elif set_op == 2:
                            ans_list = list(set(set_A).union(set_B))
                            N = len(set(set_A).union(set_B))
                            
                        # if random.random() > 0.5:
                        #     ans = inf_eng.number_to_words(int(N))
                        # else:
                        #     ans = str(int(N))
                        ans = str(int(N))
                        ans_list_full = ans_list

                        tpl_set = []
                        tpl_set.extend([(q, prop_res, Qid) for q in set_A])
                        tpl_set.extend([(q, prop_res, Qid_2) for q in set_B])
                        if args.update_counter:
                            tpl_c.update(tpl_set)

                        tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par]]),prop_res,Qid)]
                        tpl_regex.extend(['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par]]),prop_res,Qid_2)])
                        ans_entity_list = []

                    elif count_ques_sub_type == 2:
                        sec_ques_type = sec_ques_sub_type = 0 # Direct ques. is not a secondary ques.

                        try:
                            assert Qid in reverse_dict
                        except:
                            Qid = random.choice([q for q in prev_Qid if q in reverse_dict])

                        ps_tuple = [(p, set([child_par_dict[qid] for qid in reverse_dict[Qid][p] if qid in child_par_dict])) for p in reverse_dict[Qid] if p in obj_90_map]
                        ps_tuple_filt = [t for t in ps_tuple if len(t[1])>=2]
                        if len(ps_tuple_filt) == 0:
                            prev_ques_failed = True
                            # ques_type_id = 2
                            continue

                        ps_tuple_choice = random.choice(ps_tuple_filt)
                        prop_res = ps_tuple_choice[0]
                        sub_pars = random.sample(ps_tuple_choice[1], 2)
                        sub_par_1 = sub_pars[0]
                        sub_par_2 = sub_pars[1]

                        ques = random.choice(plu_obj_annot_wh[prop_res])
                        ques = sing_basic2count_set_based(ques, '', set_op, count_ques_sub_type)        
                        ques = ques.replace('YYY',item_data[Qid])
                        ques = ques.replace('SPP_1s',sing2plural(child_par_dict_name_2[sub_par_1]))
                        ques = ques.replace('SPP_2s',sing2plural(child_par_dict_name_2[sub_par_2]))

                        # set_A = [q for q in reverse_dict[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==sub_par_1]
                        # set_B = [q for q in reverse_dict[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==sub_par_2]
                        set_A = list(set(reverse_dict[Qid][prop_res]) & set(par_child_dict[sub_par_1]))
                        set_B = list(set(reverse_dict[Qid][prop_res]) & set(par_child_dict[sub_par_2]))

                        if set_op == 1:
                            ans = '%s %s and %s %s' % (str(len(set_A)), sing2plural(child_par_dict_name_2[sub_par_1]), str(len(set_B)), sing2plural(child_par_dict_name_2[sub_par_2]))
                        elif set_op == 2:
                            N = len(set(set_A).union(set_B))
                            
                            # if random.random() > 0.5:
                            #     ans = inf_eng.number_to_words(int(N))
                            # else:
                            #     ans = str(int(N))
                            ans = str(int(N))

                        #************************************************************
                        if child_par_dict_name_2[sub_par_1] == child_par_dict_name_2[sub_par_2]:
                            pattern_1 = '%s and %s' % (child_par_dict_name_2[sub_par_1], child_par_dict_name_2[sub_par_2])
                            pattern_2 = '%s or %s' % (child_par_dict_name_2[sub_par_1], child_par_dict_name_2[sub_par_2])
                            ques = ques.replace(pattern_1, child_par_dict_name_2[sub_par_1])
                            ques = ques.replace(pattern_2, child_par_dict_name_2[sub_par_1])
                            N = len(set(set_A).union(set_B))
                            ans = str(int(N))
                        #************************************************************

                        ans_list = list(set(set_A).union(set_B))
                        ans_list_full = ans_list

                        tpl_set = []
                        tpl_set.extend([(q, prop_res, Qid) for q in set_A])
                        tpl_set.extend([(q, prop_res, Qid) for q in set_B])
                        tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par_1]]),prop_res,Qid)]
                        tpl_regex.extend(['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par_2]]),prop_res,Qid)])

                        if args.update_counter:
                            tpl_c.update(tpl_set)
                        ans_entity_list = []

                    elif count_ques_sub_type == 8:
                        if len(dialog_list[-1]['entities']) == 0:
                            prev_ques_failed = True
                            continue

                        Qid = random.choice(dialog_list[-1]['entities']) # true entity
                        pred_label = random.choice(dialog_list[-1]['entities'])

                        try:
                            assert Qid in reverse_dict
                        except:
                            prev_ques_failed = True
                            continue

                        ps_tuple = [(p, set([child_par_dict[qid] for qid in reverse_dict[Qid][p] if qid in child_par_dict])) for p in reverse_dict[Qid] if p in obj_90_map]
                        ps_tuple_filt = [t for t in ps_tuple if len(t[1])>=2]
                        if len(ps_tuple_filt) == 0:
                            prev_ques_failed = True
                            # ques_type_id = 2
                            continue

                        ps_tuple_choice = random.choice(ps_tuple_filt)
                        prop_res = ps_tuple_choice[0]
                        sub_pars = random.sample(ps_tuple_choice[1], 2)
                        sub_par_1 = sub_pars[0]
                        sub_par_2 = sub_pars[1]

                        ques = random.choice(plu_obj_annot_wh[prop_res])
                        ques = sing_basic2count_set_based(ques, '', set_op, 2)        
                        ques = ques.replace('YYY','that %s' % child_par_dict_name_2[child_par_dict[Qid]])
                        ques = ques.replace('SPP_1s',sing2plural(child_par_dict_name_2[sub_par_1]))
                        ques = ques.replace('SPP_2s',sing2plural(child_par_dict_name_2[sub_par_2]))

                        # set_A = [q for q in reverse_dict[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==sub_par_1]
                        # set_B = [q for q in reverse_dict[Qid][prop_res] if q in child_par_dict and child_par_dict[q]==sub_par_2]
                        set_A = list(set(reverse_dict[Qid][prop_res]) & set(par_child_dict[sub_par_1]))
                        set_B = list(set(reverse_dict[Qid][prop_res]) & set(par_child_dict[sub_par_2]))

                        if set_op == 1:
                            ans = '%s %s and %s %s' % (str(len(set_A)), sing2plural(child_par_dict_name_2[sub_par_1]), str(len(set_B)), sing2plural(child_par_dict_name_2[sub_par_2]))
                        elif set_op == 2:
                            N = len(set(set_A).union(set_B))
                            
                            # if random.random() > 0.5:
                            #     ans = inf_eng.number_to_words(int(N))
                            # else:
                            #     ans = str(int(N))
                            ans = str(int(N))

                        #************************************************************
                        if child_par_dict_name_2[sub_par_1] == child_par_dict_name_2[sub_par_2]:
                            pattern_1 = '%s and %s' % (child_par_dict_name_2[sub_par_1], child_par_dict_name_2[sub_par_2])
                            pattern_2 = '%s or %s' % (child_par_dict_name_2[sub_par_1], child_par_dict_name_2[sub_par_2])
                            ques = ques.replace(pattern_1, child_par_dict_name_2[sub_par_1])
                            ques = ques.replace(pattern_2, child_par_dict_name_2[sub_par_1])
                            N = len(set(set_A).union(set_B))
                            ans = str(int(N))
                        #************************************************************

                        ans_list = list(set(set_A).union(set_B))
                        ans_list_full = ans_list

                        tpl_set = []
                        tpl_set.extend([(q, prop_res, Qid) for q in set_A])
                        tpl_set.extend([(q, prop_res, Qid) for q in set_B])
                        tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par_1]]),prop_res,Qid)]
                        tpl_regex.extend(['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par_2]]),prop_res,Qid)])

                        tpl_regex_extend = []
                        for q in dialog_list[-1]['entities']:
                            tpl_regex.extend(['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par_1]]),prop_res,q)])
                            tpl_regex.extend(['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par_2]]),prop_res,q)])

                        if args.update_counter:
                            tpl_c.update(tpl_set)
                        ans_entity_list = []

                    elif count_ques_sub_type in [9,10]:
                        if len(dialog_list[-1]['entities']) == 0:
                            prev_ques_failed = True
                            continue

                        sub_par = child_par_dict[dialog_list[-1]['entities'][0]]
                        if sub_par not in wikidata_type_dict:
                            prev_ques_failed = True
                            continue
                        flag = False

                        for p in [p1 for p1 in wikidata_type_dict[sub_par] if p1 in obj_90_map and sub_par in obj_90_map[p1]]:
                            cand_obj_par_list = list()
                            for q3 in wikidata_type_dict[sub_par][p]:
                                if p in sub_90_map and q3 in sub_90_map[p] and q3 in par_child_dict and q3 in child_par_dict_val:
                                    ans_list = [q1 for q1 in par_child_dict[sub_par] if q1 in wikidata and p in wikidata[q1]]
                                    if len(ans_list) > 1 and len(set(ans_list) & set(dialog_list[-1]['entities']))>0:
                                        cand_obj_par_list.append(q3)
                            if len(cand_obj_par_list) >= 2:
                                obj_pars_choice = np.random.choice(range(len(cand_obj_par_list)), 2, replace=False)
                                obj_par_1 = cand_obj_par_list[obj_pars_choice[0]]
                                obj_par_2 = cand_obj_par_list[obj_pars_choice[1]]
                                prop_res = p     
                                flag = True

                        if not flag:
                            prev_ques_failed = True
                            continue

                        cand_sub_list = list(set([q for q in par_child_dict[sub_par] if q in wikidata and prop_res in wikidata[q]]))

                        if len(cand_sub_list) > args.count_ques_sub_thresh:
                            prev_ques_failed = True
                            continue
                            
                        Z = random.choice(list(set(dialog_list[-1]['entities']) & set(cand_sub_list)))
                        Qid = Z
                        pred_label = random.choice(dialog_list[-1]['entities'])

                        cand_sub_list_score = {}
                        for sub in cand_sub_list:
                            cand_sub_list_score[sub] = len([q for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q] in [obj_par_1, obj_par_2]])

                        cand_sub_list_score_arr = np.asarray(cand_sub_list_score.values())

                        flag = True
                        for z in random_shuffle(cand_sub_list):
                            Z_score = cand_sub_list_score[z]

                            if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > Z_score]
                            elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] < Z_score]
                            elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > (Z_score - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (Z_score + np.std(cand_sub_list_score_arr))]

                            if len(ans_list) > 1:
                                Z = z
                                flag = False
                                break
                        if flag:
                            prev_ques_failed = True
                            continue

                        ques = random.choice(plu_obj_annot_wh[prop_res])
                        qualifier_dict = {3:['min','max'], 4:['atleast','atmost','exactly','around','approximately'], 5:['more','less','greater','lesser','around the same','approximately the same'],6:['atleast','atmost','exactly','around','approximately'],7:['more','less','greater','lesser','around the same','approximately the same']}
                        
                        if count_ques_sub_type == 9:
                            qualifier_choice = random.choice(qualifier_dict[5])
                            ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, 5)
                        else:
                            qualifier_choice = random.choice(qualifier_dict[7])
                            ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, 7)
                        ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))

                        ques = ques.replace('Z', 'that %s' % child_par_dict_name_2[child_par_dict[Z]])
                        ques = ques.replace('OPP_1s',sing2plural(child_par_dict_name_2[obj_par_1]))
                        ques = ques.replace('OPP_2s',sing2plural(child_par_dict_name_2[obj_par_2]))

                        #************************************************************
                        if child_par_dict_name_2[obj_par_1] == child_par_dict_name_2[obj_par_2]:
                            pattern_1 = '%s and %s' % (child_par_dict_name_2[obj_par_1], child_par_dict_name_2[obj_par_2])
                            pattern_2 = '%s or %s' % (child_par_dict_name_2[obj_par_1], child_par_dict_name_2[obj_par_2])
                            ques = ques.replace(pattern_1, child_par_dict_name_2[obj_par_1])
                            ques = ques.replace(pattern_2, child_par_dict_name_2[obj_par_1])
                        #************************************************************
                        
                        Z_score = cand_sub_list_score[Z]
                        
                        if qualifier_choice == 'more' or qualifier_choice == 'greater':
                            ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > Z_score]
                        elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                            ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] < Z_score]
                        elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                            ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > (Z_score - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (Z_score + np.std(cand_sub_list_score_arr))]
                        #['around the same', 'approximately the same']

                        if count_ques_sub_type == 5:
                            # ans_list = [q for q in ans_list if ent_c[q]<=args.entity_thresh]
                            if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                prev_ques_failed = True
                                ques_type_id = 2
                                continue
                            ans_list_full = ans_list

                            if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                ans_list_t = [ans_list[i] for i in sort_index]
                                ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                            ans = ', '.join([item_data[x] for x in ans_list])
                            ans_entity_list = ans_list

                            if len(ans_list) == 0:
                                ans = 'None'
                        else:
                            # ans = str(len(ans_list))
                            n = len(ans_list)
                            ans_list_full = ans_list
                            # if random.random() > 0.5:
                            #     ans = inf_eng.number_to_words(int(n))
                            # else:
                            #     ans = str(int(n))
                            ans = str(int(n))
                            ans_entity_list = []

                        tpl_set = []

                        # try:
                        for sub in ans_list:
                            tpl_set.extend([(sub, prop_res, q) for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q] in [obj_par_1, obj_par_2]])

                        tpl_regex = ['(%s,%s,%s)' % ('c(%s)' % sub_par, prop_res,'|'.join(['c(%s)'% x for x in [obj_par_1, obj_par_2]]))]
                        tpl_regex_extend = tpl_regex

                        if args.update_counter:
                            tpl_c.update(tpl_set)

                    else:
                        sec_ques_type = sec_ques_sub_type = 0

                        # sub_par = random.choice([child_par_dict[q] for q in prev_Qid if q in child_par_dict and child_par_dict[q] in wikidata_type_dict])
                        # pq_tuple = [(p, wikidata_type_dict[sub_par][p]) for p in wikidata_type_dict[sub_par] if p in obj_90_map and len(wikidata_type_dict[sub_par][p])>=2 and q in par_child_dict]
                        # if len(pq_tuple) > args.pq_tuple_thresh:
                        #     pq_tuple = random.sample(pq_tuple, args.pq_tuple_thresh)
                        # pq_tuple_choice = random.choice(pq_tuple)
                        # prop_res = pq_tuple_choice[0]
                        # obj_pars = random.sample(pq_tuple_choice[1],2)
                        # obj_par_1 = obj_pars[0]
                        # obj_par_2 = obj_pars[1]

                        # flag = False
                        # for q in [child_par_dict[q3] for q3 in prev_Qid if q3 in child_par_dict and child_par_dict[q3] in wikidata_type_dict]:
                        #     for p in [p1 for p1 in wikidata_type_dict[q] if p1 in obj_90_map and q in obj_90_map[p1] and len(set(child_par_dict_val).intersection(wikidata_type_dict[q][p1]))>=2]:
                        #         ans_len = len([q1 for q1 in par_child_dict[q] if q1 in wikidata and p in wikidata[q1]])
                        #         if ans_len > 1:
                        #             sub_par = q
                        #             prop_res = p
                        #             obj_pars = random.sample([q4 for q4 in wikidata_type_dict[q][p] if q4 in child_par_dict_val],2)
                        #             obj_par_1 = obj_pars[0]
                        #             obj_par_2 = obj_pars[1]
                        #             flag = True
                        #             break
                        #     if flag:
                        #         break

                        flag = False
                        for q3 in random_shuffle([child_par_dict[q4] for q4 in prev_Qid if q4 in child_par_dict and child_par_dict[q4] in wikidata_type_dict]):
                            for p in random_shuffle([p1 for p1 in wikidata_type_dict[q3] if p1 in obj_90_map and q3 in obj_90_map[p1]]):
                                cand_obj_par_list = []
                                cand_obj_par_score_list = []
                                for q in random_shuffle(wikidata_type_dict[q3][p]):
                                    if p in sub_90_map and q in sub_90_map[p] and q in par_child_dict and q in child_par_dict_val:
                                        ans_len = len([q1 for q1 in par_child_dict[q] if q1 in reverse_dict and p in reverse_dict[q1]])
                                        if ans_len > 1:
                                            sub_par = q3
                                            prop_res = p
                                            obj_par = q
                                            cand_obj_par_list.append(q)
                                            cand_obj_list = [q5 for q5 in par_child_dict[obj_par] if q5 in reverse_dict and prop_res in reverse_dict[q5]]
                                            cand_obj_list_score = list()
                                            for obj in cand_obj_list:
                                                cand_obj_list_score.append(len([q5 for q5 in reverse_dict[obj][prop_res] if q5 in child_par_dict and child_par_dict[q5] == sub_par]))
                                            cand_obj_par_score_list.append(len([x for x in cand_obj_list_score if x > 1]))
                                if len(cand_obj_par_list) > 1 and np.count_nonzero(cand_obj_par_score_list) >= 2:
                                    sub_par = q3
                                    prop_res = p
                                    # obj_pars_choice = np.random.choice(range(len(cand_obj_par_list)), 2, replace=False, p=[x*1.0/sum(cand_obj_par_score_list) for x in cand_obj_par_score_list])
                                    obj_pars_choice = np.random.choice(range(len(cand_obj_par_list)), 2, replace=False)
                                    obj_par_1 = cand_obj_par_list[obj_pars_choice[0]]
                                    obj_par_2 = cand_obj_par_list[obj_pars_choice[1]]
                                    flag = True
                                    break
                                if flag:
                                    break
                            if flag:
                                break

                        if not flag:
                            prev_ques_failed = True
                            # ques_type_id = 2
                            continue
                        ques = random.choice(plu_obj_annot_wh[prop_res])
                        qualifier_dict = {3:['min','max'], 4:['atleast','atmost','exactly','around','approximately'], 5:['more','less','greater','lesser','around the same','approximately the same'],6:['atleast','atmost','exactly','around','approximately'],7:['more','less','greater','lesser','around the same','approximately the same']}
                        qualifier_choice = random.choice(qualifier_dict[count_ques_sub_type])
                        ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, count_ques_sub_type)
                        ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))
                        ques = ques.replace('OPP_1s',sing2plural(child_par_dict_name_2[obj_par_1]))
                        ques = ques.replace('OPP_2s',sing2plural(child_par_dict_name_2[obj_par_2]))

                        #************************************************************
                        if child_par_dict_name_2[obj_par_1] == child_par_dict_name_2[obj_par_2]:
                            pattern_1 = '%s and %s' % (child_par_dict_name_2[obj_par_1], child_par_dict_name_2[obj_par_2])
                            pattern_2 = '%s or %s' % (child_par_dict_name_2[obj_par_1], child_par_dict_name_2[obj_par_2])
                            ques = ques.replace(pattern_1, child_par_dict_name_2[obj_par_1])
                            ques = ques.replace(pattern_2, child_par_dict_name_2[obj_par_1])
                        #************************************************************

                        cand_sub_list = list(set([q for q in par_child_dict[sub_par] if q in wikidata and prop_res in wikidata[q]]))
                        if len(cand_sub_list) > args.count_ques_sub_thresh:
                            prev_ques_failed = True
                            continue

                        cand_sub_list_score = {}
                        for sub in cand_sub_list:
                            cand_sub_list_score[sub] = len([q for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q] in [obj_par_1, obj_par_2]])
                            
                        cand_sub_list_score_arr = np.asarray(cand_sub_list_score.values())

                        if count_ques_sub_type == 3:                            
                            if qualifier_choice == 'min':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x]==min(cand_sub_list_score.values())]
                            elif qualifier_choice == 'max':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x]==max(cand_sub_list_score.values())]

                            if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                prev_ques_failed = True
                                ques_type_id = 2
                                continue
                            ans_list_full = ans_list

                            if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                ans_list_t = [ans_list[i] for i in sort_index]
                                ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                            ans = ', '.join([item_data[x] for x in ans_list])
                            if len(ans_list) == 0:
                                ans = 'None'
                            ans_entity_list = ans_list

                            tpl_set = []

                            for sub in ans_list:
                                tpl_set.extend([(sub, prop_res, q) for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q] in [obj_par_1, obj_par_2]])

                            tpl_regex = ['(%s,%s,%s)' % ('c(%s)' % sub_par,prop_res,'|'.join(['c(%s)'% x for x in [obj_par_1, obj_par_2]]))]

                            if args.update_counter:
                                tpl_c.update(tpl_set)

                        elif count_ques_sub_type == 4 or count_ques_sub_type == 6:

                            flag = True
                            for n in np.random.permutation(np.arange(1,max(cand_sub_list_score.values())+1)):
                                n = int(n)
                                if qualifier_choice == 'atleast':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] >= n]
                                elif qualifier_choice == 'atmost':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] <= n]
                                elif qualifier_choice == 'exactly':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] == n]
                                elif qualifier_choice == 'around' or qualifier_choice == 'approximately':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > (n - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (n + np.std(cand_sub_list_score_arr))]

                                if len(ans_list) > 0:
                                    N = n
                                    flag = False
                                    break
                            if flag:
                                prev_ques_failed = True
                                continue

                            # if random.random() > 0.5:
                            #     N_str = inf_eng.number_to_words(int(N))
                            # else:
                            #     N_str = str(int(N))
                            N_str = str(int(N))

                            ques = ques.replace(' N ',' %s ' % N_str)

                            if N == 0:
                                prev_ques_failed = True
                                # ques_type_id = 2
                                continue

                            if qualifier_choice == 'atleast':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] >= N]
                            elif qualifier_choice == 'atmost':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] <= N]
                            elif qualifier_choice == 'exactly':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] == N]
                            elif qualifier_choice == 'around' or qualifier_choice == 'approximately':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > (N - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (N + np.std(cand_sub_list_score_arr))]

                            if count_ques_sub_type == 4:
                                # ans_list = [q for q in ans_list if ent_c[q]<=args.entity_thresh]
                                if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                    prev_ques_failed = True
                                    ques_type_id = 2
                                    continue
                                ans_list_full = ans_list

                                if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                    ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                    sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                    ans_list_t = [ans_list[i] for i in sort_index]
                                    ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                                ans = ', '.join([item_data[x] for x in ans_list])
                                if len(ans_list) == 0:
                                    ans = 'None'
                                ans_entity_list = ans_list
                            elif count_ques_sub_type == 6:
                                ans = str(len(ans_list))
                                ans_list_full = ans_list
                                ans_entity_list = []

                            tpl_set = []

                            for sub in ans_list:
                                tpl_set.extend([(sub, prop_res, q) for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q] in [obj_par_1, obj_par_2]])

                            tpl_regex = ['(%s,%s,%s)' % ('c(%s)' % sub_par,prop_res,'|'.join(['c(%s)'% x for x in [obj_par_1, obj_par_2]]))]

                            if args.update_counter:
                                tpl_c.update(tpl_set)

                        elif count_ques_sub_type == 5 or count_ques_sub_type == 7:

                            flag = True
                            for z in random_shuffle(cand_sub_list):
                                Z_score = cand_sub_list_score[z]

                                if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > Z_score]
                                elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] < Z_score]
                                elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > (Z_score - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (Z_score + np.std(cand_sub_list_score_arr))]

                                if len(ans_list) > 1:
                                    Z = z
                                    flag = False
                                    break
                            if flag:
                                prev_ques_failed = True
                                continue

                            ques = ques.replace('Z', item_data[Z])

                            Z_score = cand_sub_list_score[Z]
                            
                            if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > Z_score]
                            elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] < Z_score]
                            elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > (Z_score - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (Z_score + np.std(cand_sub_list_score_arr))]
                            #['around the same', 'approximately the same']

                            if count_ques_sub_type == 5:
                                # ans_list = [q for q in ans_list if ent_c[q]<=args.entity_thresh]
                                if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                    prev_ques_failed = True
                                    ques_type_id = 2
                                    continue
                                ans_list_full = ans_list

                                if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                    ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                    sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                    ans_list_t = [ans_list[i] for i in sort_index]
                                    ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                                ans = ', '.join([item_data[x] for x in ans_list])
                                ans_entity_list = ans_list

                                if len(ans_list) == 0:
                                    ans = 'None'
                            else:
                                # ans = str(len(ans_list))
                                n = len(ans_list)
                                ans_list_full = ans_list
                                # if random.random() > 0.5:
                                #     ans = inf_eng.number_to_words(int(n))
                                # else:
                                #     ans = str(int(n))
                                ans = str(int(n))
                                ans_entity_list = []

                            tpl_set = []

                            # try:
                            for sub in ans_list:
                                tpl_set.extend([(sub, prop_res, q) for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q] in [obj_par_1, obj_par_2]])

                            tpl_regex = ['(%s,%s,%s)' % ('c(%s)' % sub_par, prop_res,'|'.join(['c(%s)'% x for x in [obj_par_1, obj_par_2]]))]

                            if args.update_counter:
                                tpl_c.update(tpl_set)
                            # except:
                            #     f1 = open(os.path.join(args.out_dir,'QA_%s_log.txt' % args.save_dir_id),'a')
                            #     f1.write('sub = %s prop_res = %s\n' % (sub, prop_res))
                            #     f1.close()
                            #     prev_ques_failed = True
                            #     continue
                            
                # if args.use_regex and len(set(tpl_regex).intersection(set(regex_ques_8))) > 0:
                #     ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23])
                #     prev_ques_failed = True
                #     continue

                if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                    prev_ques_failed = True
                    ques_type_id = 2
                    continue

                dict1 = {}
                dict1['speaker'] = 'USER'
                dict1['utterance'] = ques
                dict1['ques_type_id'] = ques_type_id_save
                # dict1['last_ques_type_id_save'] = last_ques_type_id_save
                dict1['count_ques_type'] = count_ques_type
                dict1['count_ques_sub_type'] = count_ques_sub_type
                dict1['set_op'] = set_op
                dict1['relations'] = [prop_res]
                dict1['is_incomplete'] = 0

                #**********************************************************
                if count_ques_type == 1:
                    if count_ques_sub_type == 1:
                        dict1['Qid'] = Qid
                        dict1['Qid_2'] = Qid_2
                        dict1['obj_par'] = obj_par
                        dict1['prop_res'] = prop_res
                        dict1['set_op'] = set_op
                    elif count_ques_sub_type in [2,8]:
                        dict1['Qid'] = Qid
                        dict1['obj_par_1'] = obj_par_1
                        dict1['obj_par_2'] = obj_par_2
                        dict1['prop_res'] = prop_res
                        dict1['set_op'] = set_op
                    elif count_ques_sub_type in [3,4,5,6,7,9,10]:
                        dict1['obj_par'] = obj_par
                        dict1['sub_par_1'] = sub_par_1
                        dict1['sub_par_2'] = sub_par_2
                        dict1['prop_res'] = prop_res
                        dict1['qualifier_choice'] = qualifier_choice
                        dict1['set_op'] = set_op
                        if count_ques_sub_type in [4,6]:
                            dict1['N'] = N
                        elif count_ques_sub_type in [5,7,9,10]:
                            dict1['Z'] = Z
                            # dict1['Z_score'] = Z_score
                            # dict1['cand_obj_list_score'] = cand_obj_list_score
                else:
                    if count_ques_sub_type == 1:
                        dict1['Qid'] = Qid
                        dict1['Qid_2'] = Qid_2
                        dict1['sub_par'] = sub_par
                        dict1['prop_res'] = prop_res
                        dict1['set_op'] = set_op
                    elif count_ques_sub_type in [2,8]:
                        dict1['Qid'] = Qid
                        dict1['sub_par_1'] = sub_par_1
                        dict1['sub_par_2'] = sub_par_2
                        dict1['prop_res'] = prop_res
                        dict1['set_op'] = set_op
                    elif count_ques_sub_type in [3,4,5,6,7,9,10]:
                        dict1['sub_par'] = sub_par
                        dict1['obj_par_1'] = obj_par_1
                        dict1['obj_par_2'] = obj_par_2
                        dict1['prop_res'] = prop_res
                        dict1['qualifier_choice'] = qualifier_choice
                        dict1['set_op'] = set_op
                        if count_ques_sub_type in [4,6]:
                            dict1['N'] = N
                        elif count_ques_sub_type in [5,7,9,10]:
                            dict1['Z'] = Z
                            # dict1['Z_score'] = Z_score
                            # dict1['cand_sub_list_score'] = cand_sub_list_score
                #**********************************************************
                if count_ques_sub_type == 1:
                    description = 'Quantitative|Count|Mult. entity type'
                elif count_ques_sub_type == 2:
                    description = 'Quantitative|Count|Logical operators'
                elif count_ques_sub_type == 3:
                    description = 'Quantitative|Min/Max|Mult. entity type'
                elif count_ques_sub_type == 4:
                    description = 'Quantitative|Atleast/ Atmost/ Approx. the same/Equal|Mult. entity type'
                elif count_ques_sub_type == 5:
                    description = 'Comparative|More/Less|Mult. entity type'
                elif count_ques_sub_type == 6:
                    description = 'Quantitative|Count over Atleast/ Atmost/ Approx. the same/Equal|Mult. entity type'
                elif count_ques_sub_type == 7:
                    description = 'Comparative|Count over More/Less|Mult. entity type'
                elif count_ques_sub_type == 8:
                    description = 'Quantitative|Count|Logical operators|Indirect'
                elif count_ques_sub_type == 9:
                    description = 'Comparative|More/Less|Mult. entity type|Indirect'
                elif count_ques_sub_type == 10:
                    description = 'Comparative|Count over More/Less|Mult. entity type|Indirect'

                dict1['description'] = description
                #**********************************************************

                if count_ques_sub_type == 1:
                    dict1['entities'] = [Qid, Qid_2]
                    if args.update_counter:
                        ent_c.update([Qid, Qid_2])
                elif count_ques_sub_type == 2:
                    dict1['entities'] = [Qid]
                    if args.update_counter:
                        ent_c.update([Qid])
                elif count_ques_sub_type in [5,7]:
                    dict1['entities'] = [Z]
                    if args.update_counter:
                        ent_c.update([Z])
                else:
                    dict1['entities'] = []
                    if args.update_counter:
                        ent_c.update(ans_entity_list)
                dict1['signature'] = get_dict_signature(dict1.copy())
                if dict1['signature'] in regex_ques_all:
                    ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23])
                    prev_ques_failed = True
                    continue
                dialog_list.append(dict1.copy())
                
                if count_ques_sub_type not in [8,9,10] or (count_ques_sub_type in [8,9,10] and len(dialog_list[-2]['entities'])==1):
                    dict1 = {}
                    dict1['speaker'] = 'SYSTEM'
                    dict1['utterance'] = ans
                    dict1['entities'] = ans_entity_list[:]
                    dict1['active_set'] = tpl_regex[:]
                    dict1['ans_list_full'] = ans_list_full
                    dict1['signature'] = get_dict_signature(dict1.copy())
                    dialog_list.append(dict1.copy())
                else:
                    dict1 = {}
                    dict1['speaker'] = 'SYSTEM'
                    dict1['utterance'] = 'Did you mean %s ?' % item_data[pred_label]
                    dict1['active_set'] = tpl_regex_extend[:] # see if last regex getting reflected
                    dict1['ans_list_full'] = copy.copy(dialog_list[-1]['entities'])
                    dict1['entities'] = [pred_label]
                    dict1['relations'] = []
                    if count_ques_sub_type == 8:
                        dict1['description'] = 'Quantitative|Count|Mult. entity type|Clarification'
                    elif count_ques_sub_type == 9:
                        dict1['description'] = 'Comparative|More/Less|Mult. entity type|Clarification'
                    elif count_ques_sub_type == 10:
                        dict1['description'] = 'Comparative|Count over More/Less|Mult. entity type|Clarification'
                    dict1['signature'] = get_dict_signature(dict1.copy())
                    dialog_list.append(dict1.copy())

                    if Qid == pred_label:
                        dict1 = {}
                        dict1['speaker'] = 'USER'
                        dict1['utterance'] = 'Yes'
                        dialog_list.append(dict1.copy())
                    else:
                        dict1 = {}
                        dict1['speaker'] = 'USER'
                        dict1['utterance'] = 'No, I meant %s. Could you tell me the answer for that?' % item_data[Qid]
                        dict1['entities'] = [Qid]
                        dialog_list.append(dict1.copy())

                    dict1 = {}
                    dict1['speaker'] = 'SYSTEM'
                    dict1['utterance'] = ans
                    dict1['entities'] = ans_entity_list[:]
                    dict1['active_set'] = tpl_regex[:]
                    dict1['ans_list_full'] = ans_list_full
                    dict1['signature'] = get_dict_signature(dict1.copy())
                    dialog_list.append(dict1.copy())
                
                if random.random() > 0.3: # change later
                    if count_ques_type == 1:
                        if count_ques_sub_type in [5,7]:
                            cand_obj_list = list(set([q for q in par_child_dict[obj_par] if q in reverse_dict and prop_res in reverse_dict[q]]))
                            cand_obj_list_score = {}
                            for obj in cand_obj_list:
                                cand_obj_list_score[obj] = len([q for q in reverse_dict[obj][prop_res] if q in child_par_dict and child_par_dict[q] in [sub_par_1, sub_par_2]])

                            cand_obj_list_score_arr = np.asarray(cand_obj_list_score.values())

                            flag = True
                            for z in random_shuffle(cand_obj_list):
                                Z_score = cand_obj_list_score[z]
                                if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > Z_score]
                                elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] < Z_score]
                                elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                    ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > (Z_score - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[x] < (Z_score + np.std(cand_obj_list_score_arr))]

                                if len(ans_list) > 1 and z != dialog_list[-2]['Z']:
                                    Z = z
                                    flag = False
                                    break
                            if flag:
                                prev_ques_failed = True
                                continue

                            pprase_list = ['what about', 'also tell me about', 'how about']
                            pp = random.choice(pprase_list)
                            ques = 'And %s %s?' % (pp, item_data[Z])

                            Z_score = cand_obj_list_score[Z]
                            
                            if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > Z_score]
                            elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] < Z_score]
                            elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                ans_list = [x for x in cand_obj_list if cand_obj_list_score[x] > (Z_score - np.std(cand_obj_list_score_arr)) and cand_obj_list_score[x] < (Z_score + np.std(cand_obj_list_score_arr))]

                            if count_ques_sub_type == 5:
                                # ans_list = [q for q in ans_list if ent_c[q]<=args.entity_thresh]
                                if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                    prev_ques_failed = True
                                    ques_type_id = 2
                                    continue
                                ans_list_full = ans_list

                                if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                    ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                    sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                    ans_list_t = [ans_list[i] for i in sort_index]
                                    ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                                ans = ', '.join([item_data[x] for x in ans_list])
                                ans_entity_list = ans_list

                                if len(ans_list) == 0:
                                    ans = 'None'
                            else:
                                # ans = str(len(ans_list))
                                n = len(ans_list)
                                ans_list_full = ans_list
                                # if random.random() > 0.5:
                                #     ans = inf_eng.number_to_words(int(n))
                                # else:
                                #     ans = str(int(n))
                                ans = str(int(n))
                                ans_entity_list = []

                            tpl_set = []

                            # try:
                            for obj in ans_list:
                                tpl_set.extend([(q, prop_res, obj) for q in reverse_dict[obj][prop_res] if q in child_par_dict and child_par_dict[q] in [sub_par_1, sub_par_2]])

                            tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par_1, sub_par_2]]),prop_res,'c(%s)' % obj_par)]
                            if args.update_counter:
                                tpl_c.update(tpl_set)

                        elif count_ques_sub_type == 2:
                            valid_obj = [q for q in list(set(par_child_dict[obj_par_1]) & set(par_child_dict[obj_par_2])) if q in reverse_dict and prop_res in reverse_dict[q]]
                            valid_sub = [sub for qid in valid_obj for sub in reverse_dict[qid][prop_res] if sub != Qid]

                            if len(valid_sub) == 0:
                                continue
                            Qid = random.choice(valid_sub)

                            pprase_list = ['what about', 'also tell me about', 'how about']
                            pp = random.choice(pprase_list)
                            ques = 'And %s %s?' % (pp, item_data[Qid])

                            set_A = list(set(wikidata[Qid][prop_res]) & set(par_child_dict[obj_par_1]))
                            set_B = list(set(wikidata[Qid][prop_res]) & set(par_child_dict[obj_par_2]))

                            if set_op == 1:
                                ans = '%s %s and %s %s' % (str(len(set_A)), sing2plural(child_par_dict_name_2[obj_par_1]), str(len(set_B)), sing2plural(child_par_dict_name_2[obj_par_2]))
                            elif set_op == 2:
                                N = len(set(set_A).union(set_B))

                                # if random.random() > 0.5:
                                #     ans = inf_eng.number_to_words(int(N))
                                # else:
                                #     ans = str(int(N))
                                ans = str(int(N))
                            ans_list = list(set(set_A).union(set_B))
                            ans_list_full = ans_list

                            tpl_set = []
                            tpl_set.extend([(Qid, prop_res, q) for q in set_A])
                            tpl_set.extend([(Qid, prop_res, q) for q in set_B])

                            if args.update_counter:
                                tpl_c.update(tpl_set)

                            tpl_regex = ['(%s,%s,%s)' % (Qid,prop_res,'|'.join(['c(%s)'% x for x in [obj_par_1]]))]
                            tpl_regex.extend(['(%s,%s,%s)' % (Qid,prop_res,'|'.join(['c(%s)'% x for x in [obj_par_2]]))])
                            ans_entity_list = []

                    elif count_ques_type == 2:
                        if count_ques_sub_type in [5,7]:
                            cand_sub_list = list(set([q for q in par_child_dict[sub_par] if q in wikidata and prop_res in wikidata[q]]))
                            cand_sub_list_score = {}
                            for sub in cand_sub_list:
                                cand_sub_list_score[sub] = len([q for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q] in [obj_par_1, obj_par_2]])
                                
                            cand_sub_list_score_arr = np.asarray(cand_sub_list_score.values())

                            flag = True
                            for z in random_shuffle(cand_sub_list):
                                Z_score = cand_sub_list_score[z]

                                if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > Z_score]
                                elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] < Z_score]
                                elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                    ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > (Z_score - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (Z_score + np.std(cand_sub_list_score_arr))]

                                if len(ans_list) > 1 and z != dialog_list[-2]['Z']:
                                    Z = z
                                    flag = False
                                    break
                            if flag:
                                # prev_ques_failed = True
                                continue

                            pprase_list = ['what about', 'also tell me about', 'how about']
                            pp = random.choice(pprase_list)
                            ques = 'And %s %s?' % (pp, item_data[Z])

                            Z_score = cand_sub_list_score[Z]
                            
                            if qualifier_choice == 'more' or qualifier_choice == 'greater':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > Z_score]
                            elif qualifier_choice == 'less' or qualifier_choice == 'lesser':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] < Z_score]
                            elif qualifier_choice == 'around the same' or qualifier_choice == 'approximately the same':
                                ans_list = [x for x in cand_sub_list if cand_sub_list_score[x] > (Z_score - np.std(cand_sub_list_score_arr)) and cand_sub_list_score[x] < (Z_score + np.std(cand_sub_list_score_arr))]
                            #['around the same', 'approximately the same']

                            if count_ques_sub_type == 5:
                                # ans_list = [q for q in ans_list if ent_c[q]<=args.entity_thresh]
                                if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                                    prev_ques_failed = True
                                    ques_type_id = 2
                                    continue
                                ans_list_full = ans_list

                                if len(ans_list) > args.plural_obj_ques_ans_thresh:
                                    ans_list_fanout = [wikidata_fanout_dict[q] for q in ans_list]
                                    sort_index = sorted(range(len(ans_list_fanout)), key=ans_list_fanout.__getitem__,reverse=True)
                                    ans_list_t = [ans_list[i] for i in sort_index]
                                    ans_list = ans_list_t[:args.plural_sub_ques_ans_thresh]
                                ans = ', '.join([item_data[x] for x in ans_list])
                                ans_entity_list = ans_list

                                if len(ans_list) == 0:
                                    ans = 'None'
                            else:
                                # ans = str(len(ans_list))
                                n = len(ans_list)
                                ans_list_full = ans_list
                                # if random.random() > 0.5:
                                #     ans = inf_eng.number_to_words(int(n))
                                # else:
                                #     ans = str(int(n))
                                ans = str(int(n))
                                ans_entity_list = []

                            tpl_set = []

                            # try:
                            for sub in ans_list:
                                tpl_set.extend([(sub, prop_res, q) for q in wikidata[sub][prop_res] if q in child_par_dict and child_par_dict[q] in [obj_par_1, obj_par_2]])

                            tpl_regex = ['(%s,%s,%s)' % ('c(%s)' % sub_par, prop_res,'|'.join(['c(%s)'% x for x in [obj_par_1, obj_par_2]]))]

                            if args.update_counter:
                                tpl_c.update(tpl_set)

                        elif count_ques_sub_type == 2:
                            valid_sub = [q for q in list(set(par_child_dict[sub_par_1]) & set(par_child_dict[sub_par_2])) if q in wikidata and prop_res in wikidata[q]]
                            valid_obj = [obj for qid in valid_sub for obj in wikidata[qid][prop_res] if obj != Qid]

                            if len(valid_obj) == 0:
                                continue

                            Qid = random.choice(valid_obj)

                            pprase_list = ['what about', 'also tell me about', 'how about']
                            pp = random.choice(pprase_list)
                            ques = 'And %s %s?' % (pp, item_data[Qid])

                            set_A = list(set(reverse_dict[Qid][prop_res]) & set(par_child_dict[sub_par_1]))
                            set_B = list(set(reverse_dict[Qid][prop_res]) & set(par_child_dict[sub_par_2]))

                            if set_op == 1:
                                ans = '%s %s and %s %s' % (str(len(set_A)), sing2plural(child_par_dict_name_2[sub_par_1]), str(len(set_B)), sing2plural(child_par_dict_name_2[sub_par_2]))
                            elif set_op == 2:
                                N = len(set(set_A).union(set_B))
                                
                                # if random.random() > 0.5:
                                #     ans = inf_eng.number_to_words(int(N))
                                # else:
                                #     ans = str(int(N))
                                ans = str(int(N))

                            ans_list = list(set(set_A).union(set_B))
                            ans_list_full = ans_list

                            tpl_set = []
                            tpl_set.extend([(q, prop_res, Qid) for q in set_A])
                            tpl_set.extend([(q, prop_res, Qid) for q in set_B])
                            tpl_regex = ['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par_1]]),prop_res,Qid)]
                            tpl_regex.extend(['(%s,%s,%s)' % ('|'.join(['c(%s)'% x for x in [sub_par_2]]),prop_res,Qid)])

                            if args.update_counter:
                                tpl_c.update(tpl_set)
                            ans_entity_list = []

                    if count_ques_sub_type in [2,5,7]:
                        # if args.use_regex and len(set(tpl_regex).intersection(set(regex_ques_8))) > 0:
                        #     ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23])
                        #     # prev_ques_failed = True
                        #     continue

                        if len(ans_list) > args.global_ans_thresh or len(ans_list)==0::
                            prev_ques_failed = True
                            ques_type_id = 2
                            continue
                    
                        dict1 = {}
                        dict1['speaker'] = 'USER'
                        dict1['utterance'] = ques
                        dict1['ques_type_id'] = ques_type_id_save
                        # dict1['last_ques_type_id_save'] = 8
                        dict1['count_ques_type'] = count_ques_type
                        dict1['count_ques_sub_type'] = count_ques_sub_type
                        dict1['set_op'] = set_op
                        dict1['relations'] = [prop_res]
                        dict1['is_incomplete'] = 1

                        #**************************************************************************
                        if count_ques_sub_type == 2:
                            description = 'Quantitative|Count|Logical operators|Incomplete'
                        elif count_ques_sub_type == 5:
                            description = 'Comparative|More/Less|Mult. entity type|Incomplete'
                        elif count_ques_sub_type == 7:
                            description = 'Comparative|Count over More/Less|Mult. entity type|Incomplete'

                        dict1['description'] = description
                        #**************************************************************************
                        if count_ques_sub_type == 2:
                            dict1['entities'] = [Qid]
                            if args.update_counter:
                                ent_c.update([Qid])

                            dict1['Qid'] = Qid
                            dict1['prop_res'] = prop_res
                            dict1['set_op'] = set_op
                            if count_ques_type == 1:
                                dict1['obj_par_1'] = obj_par_1
                                dict1['obj_par_2'] = obj_par_2
                            else:
                                dict1['sub_par_1'] = sub_par_1
                                dict1['sub_par_2'] = sub_par_2

                        elif count_ques_sub_type in [5,7]:
                            dict1['entities'] = [Z]
                            if args.update_counter:
                                ent_c.update([Z])

                            dict1['Z'] = Z
                            if count_ques_type == 1:
                                dict1['obj_par'] = obj_par
                                dict1['sub_par_1'] = sub_par_1
                                dict1['sub_par_2'] = sub_par_2
                            else:    
                                dict1['sub_par'] = sub_par
                                dict1['obj_par_1'] = obj_par_1
                                dict1['obj_par_2'] = obj_par_2
                            dict1['prop_res'] = prop_res
                            dict1['qualifier_choice'] = qualifier_choice
                            dict1['set_op'] = set_op

                            # if count_ques_type == 1:
                            #     dict1['cand_obj_list_score'] = cand_obj_list_score
                            # else:
                            #     dict1['cand_sub_list_score'] = cand_sub_list_score
                        else:
                            dict1['entities'] = []
                            if args.update_counter:
                                ent_c.update(ans_entity_list)

                        dict1['signature'] = get_dict_signature(dict1.copy())
                        if dict1['signature'] in regex_ques_all:
                            ques_type_id = np.random.choice(np.array([2, 4, 5, 7, 8]), p=[0.08, 0.23, 0.23, 0.23, 0.23])
                            prev_ques_failed = True
                            continue
                        dialog_list.append(dict1.copy())
                        
                        dict1 = {}
                        dict1['speaker'] = 'SYSTEM'
                        dict1['utterance'] = ans
                        dict1['entities'] = ans_entity_list[:]
                        dict1['active_set'] = tpl_regex[:]
                        dict1['ans_list_full'] = ans_list_full
                        dict1['signature'] = get_dict_signature(dict1.copy())
                        dialog_list.append(dict1.copy())


            if ques_type_id_save == 1 or ques_type_id_save == 6 or (ques_type_id_save == 2 and (sec_ques_sub_type == 1 or sec_ques_sub_type == 2)):
                if Qid not in d:
                    d[Qid] = {prop_res : [prop_Qid_par]}
                else:
                    if prop_res not in d[Qid]:
                        d[Qid][prop_res] = [prop_Qid_par]
                    elif prop_Qid_par not in d[Qid][prop_res]:
                        d[Qid][prop_res].append(prop_Qid_par)
            elif ques_type_id_save == 2 and (sec_ques_sub_type == 3 or sec_ques_sub_type == 4):
                for q in sub_list:
                    if q not in d:
                        d[q] = {prop_res : [prop_Qid_par]}
                    else:
                        if prop_res not in d[q]:
                            d[q][prop_res] = [prop_Qid_par]
                        elif prop_Qid_par not in d[q][prop_res]:
                            d[q][prop_res].append(prop_Qid_par)
         

            prev_Qid = copy.copy(dialog_list[-1]['entities']) + prev_Qid
            prev_Qid_nest =  [copy.copy(dialog_list[-1]['entities'])] + prev_Qid_nest
            # append all entities in the answer in front of prev_Qid context
            prev_ques_failed = False
            no_success_ques += 1

            if 'relations' in dialog_list[-2]:
                rel_list.extend(dialog_list[-2]['relations'])
                rel_c.update(dialog_list[-2]['relations'])
            
            try:
                assert json_plus == ent_c_plus
            except:
                f1 = open(os.path.join(args.out_dir,'QA_%s_log.txt' % args.save_dir_id),'a')
                # f1.write('json_plus = %d\n' % json_plus)
                # f1.write('ent_c_plus = %d\n' % ent_c_plus)
                # f1.write('ques_type_id = %d\n' % ques_type_id_save)
                # f1.write('sec_ques_type = %d\n' % sec_ques_type)
                # f1.write('sec_ques_sub_type = %d\n' % sec_ques_sub_type)
                f1.close()

        # try:
        try:
            assert is_valid_dialog(dialog_list)
            with open(os.path.join(args.out_dir,'QA_%s/QA_%d.json' % (args.save_dir_id,file_id)), 'wb') as outfile:
                json.dump(dialog_list, outfile,indent = 1)
        except:
            pass
        # except:
        #     print 'Dialog ID: %d' % file_id
        #     print dialog_list

        if args.sync_counter: # sync counters only if required
            if file_id % args.counter_update_int == 0:
                # with open('entity_counter.pickle','wb') as data_file:
                #     for i in range(20):
                #         try:
                #             fcntl.flock(data_file, fcntl.LOCK_EX|LOCK_NB)
                #             pickle.dump(ent_c,data_file)
                #         except:
                #             time.sleep(10)
                #             continue
                #         fcntl.flock(data_file, fcntl.LOCK_UN)
                #         f1 = open(os.path.join(args.out_dir,'QA_%s_log.txt' % args.save_dir_id),'a')
                #         f1.write('ent_c written successfully\n')
                #         f1.close()
                #         break

                # with open('triple_counter.pickle','wb') as data_file:
                #     for i in range(20):
                #         try:
                #             fcntl.flock(data_file, fcntl.LOCK_EX|LOCK_NB)
                #             pickle.dump(tpl_c,data_file)
                #         except:
                #             time.sleep(10)
                #             continue
                #         fcntl.flock(data_file, fcntl.LOCK_UN)
                #         f1 = open(os.path.join(args.out_dir,'QA_%s_log.txt' % args.save_dir_id),'a')
                #         f1.write('tpl_c written successfully\n')
                #         f1.close()
                #         break
                with open(os.path.join(args.out_dir,'entity_counter.pickle'),'r+') as data_file:
                    for i in range(20):
                        try:
                            fcntl.flock(data_file, fcntl.LOCK_EX|LOCK_NB)
                            ent_c_global = pickle.load(data_file)
                            ent_c_global.update(ent_c - ent_c_save)
                            pickle.dump(ent_c_global, data_file)
                            ent_c = ent_c_global.copy()
                            ent_c_save = ent_c.copy()
                        except:
                            time.sleep(10)
                            continue
                        fcntl.flock(data_file, fcntl.LOCK_UN)
                        break

                with open(os.path.join(args.out_dir,'QA_%s/entity_counter.pickle' % args.save_dir_id),'w') as data_file:
                    pickle.dump(ent_c, data_file)

                with open(os.path.join(args.out_dir,'triple_counter.pickle'),'r+') as data_file:
                    for i in range(20):
                        try:
                            fcntl.flock(data_file, fcntl.LOCK_EX|LOCK_NB)
                            tpl_c_global = pickle.load(data_file)
                            tpl_c_global.update(tpl_c - tpl_c_save)
                            pickle.dump(tpl_c_global, data_file)
                            tpl_c = tpl_c_global.copy()
                            tpl_c_save = tpl_c.copy()
                        except:
                            time.sleep(10)
                            continue
                        fcntl.flock(data_file, fcntl.LOCK_UN)
                        break

                with open(os.path.join(args.out_dir,'QA_%s/triple_counter.pickle' % args.save_dir_id),'w') as data_file:
                    pickle.dump(tpl_c, data_file)

                with open(os.path.join(args.out_dir,'rel_counter.pickle'),'r+') as data_file:
                    for i in range(20):
                        try:
                            fcntl.flock(data_file, fcntl.LOCK_EX|LOCK_NB)
                            rel_c_global = pickle.load(data_file)
                            rel_c_global.update(rel_c - rel_c_save)
                            pickle.dump(rel_c_global, data_file)
                            rel_c = rel_c_global.copy()
                            rel_c_save = rel_c.copy()
                        except:
                            time.sleep(10)
                            continue
                        fcntl.flock(data_file, fcntl.LOCK_UN)
                        break

                with open(os.path.join(args.out_dir,'QA_%s/rel_counter.pickle' % args.save_dir_id),'w') as data_file:
                    pickle.dump(tpl_c, data_file)


    except:
        logging.exception('Something aweful happened')
        try:
            assert is_valid_dialog(dialog_list)
            with open(os.path.join(args.out_dir,'QA_%s/QA_%d.json' % (args.save_dir_id,file_id)), 'wb') as outfile:
                json.dump(dialog_list, outfile,indent = 1)
        except:
            pass
        continue
