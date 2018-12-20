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
# from load_wikidata2 import *

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

# stop_word_list = set(stopwords.words('english'))
stop_word_list = set([u'all', u'just', u'being', u'over', u'both', u'through', u'yourselves', u'its', u'before', u'o', u'hadn', u'herself', u'll', u'had', u'should', u'to', u'only', u'won', u'under', u'ours', u'has', u'do', u'them', u'his', u'very', u'they', u'not', u'during', u'now', u'him', u'nor', u'd', u'did', u'didn', u'this', u'she', u'each', u'further', u'where', u'few', u'because', u'doing', u'some', u'hasn', u'are', u'our', u'ourselves', u'out', u'what', u'for', u'while', u're', u'does', u'above', u'between', u'mustn', u't', u'be', u'we', u'who', u'were', u'here', u'shouldn', u'hers', u'by', u'on', u'about', u'couldn', u'of', u'against', u's', u'isn', u'or', u'own', u'into', u'yourself', u'down', u'mightn', u'wasn', u'your', u'from', u'her', u'their', u'aren', u'there', u'been', u'whom', u'too', u'wouldn', u'themselves', u'weren', u'was', u'until', u'more', u'himself', u'that', u'but', u'don', u'with', u'than', u'those', u'he', u'me', u'myself', u'ma', u'these', u'up', u'will', u'below', u'ain', u'can', u'theirs', u'my', u'and', u've', u'then', u'is', u'am', u'it', u'doesn', u'an', u'as', u'itself', u'at', u'have', u'in', u'any', u'if', u'again', u'no', u'when', u'same', u'how', u'other', u'which', u'you', u'shan', u'needn', u'haven', u'after', u'most', u'such', u'why', u'a', u'off', u'i', u'm', u'yours', u'so', u'y', u'the', u'having', u'once'])
stop_par_list = ['Q21025364', 'Q19361238', 'Q21027609', 'Q20088085', 'Q15184295', 'Q11266439', 'Q17362920', 'Q19798645', 'Q26884324', 'Q14204246', 'Q13406463', 'Q14827288', 'Q4167410', 'Q21484471', 'Q17442446', 'Q4167836', 'Q19478619', 'Q24017414', 'Q19361238', 'Q24027526', 'Q15831596', 'Q24027474', 'Q23958852', 'Q24017465', 'Q24027515', 'Q1924819']

inf_eng = inflect.engine()
# child_par_dict_val = child_par_dict.values()

# HYPERPARAMETERS

parser = argparse.ArgumentParser(description='Hyper-parameter settings')
# parser.add_argument('--input_dir', dest='input_dir', type=str, help='directory in which dialogs are to be verified', required=True)
# parser.add_argument('--output_dir',dest='output_dir', type=str, help = 'name of dir (wrt cwd) where dialogue dirs are created',required=True) # should be required
# parser.add_argument('--low',dest='low',type=int, help='lower index of QA')
# parser.add_argument('--high',dest='high',type=int, help='higher index of QA')

args = parser.parse_args()
# print(args)
# args.input_dir = '/home/vardaan/projects/rpp-bengioy/vardaan/CSQA/train/'
# args.output_dir = '/home/vardaan/projects/rpp-bengioy/vardaan/train/'
args.input_dir = '/data/milatmp1/pahujava/wikidata/CSQA_v6/test'
args.output_dir = '/data/milatmp1/pahujava/wikidata/CSQA_v8/test'
args.low = 0
args.high= 1600

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

    start_time = time.time()

    for filename in os.listdir(os.path.join(args.input_dir, dir_name)):
        count += 1
        if count % 100 == 0:
            print count

        # print('%d files in %f sec.' % (count, (time.time() - start_time)))

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

            for utter_id in range(len(utter_list)):
                utter = utter_list[utter_id]
                # print(utter_id)

                if 'ques_type_id' not in utter: # ignore answer utterances
                    dialog_list.append(utter)
                elif 'is_incomplete' in utter and utter['is_incomplete'] == 1:
                    dialog_list.append(utter)
                else:
                    for var in var_list:
                        if var in globals():
                            del var
                    
                    if utter['ques_type_id'] == 4:
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

                        if is_sub: # prev. secondary ques. is subject-based
                            if prop_res == prop_res_1: # pid remains unchanged
                                ques_1 = random.choice(plu_sub_annot_wh[prop_res_1])
                       
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

                            else: # pid is different
                                is_inc = 0
                                ques_1 = random.choice(plu_sub_annot_wh[prop_res_1])
                                if set_op_choice != 3:
                                    ques_2 = random.choice(plu_sub_annot_wh[prop_res])
                                else:
                                    ques_2 = random.choice(neg_plu_sub_annot_wh[prop_res])
                                set_op_choice_dem = set_op_choice

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

                        else: # prev. secondary ques. is object-based
                            if prop_res == prop_res_1: # pid remains unchanged
                                ques_1 = random.choice(plu_obj_annot_wh[prop_res_1])

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

                            else: # pid is different
                                is_inc = 0
                                ques_1 = random.choice(plu_obj_annot_wh[prop_res_1])
                                if set_op_choice != 3:
                                    ques_2 = random.choice(plu_obj_annot_wh[prop_res])
                                else:
                                    ques_2 = random.choice(neg_plu_obj_annot_wh[prop_res])
                                set_op_choice_dem = set_op_choice

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

                        #*****************************************************************
                        new_utter_dict = {}
                        for field in utter:
                            if field not in ['utterance','signature']: # copy all fields except ('utterance','signature')
                                new_utter_dict[field] = utter[field]

                        new_utter_dict['utterance'] = ques
                        new_utter_dict['signature'] = get_dict_signature(new_utter_dict)
                        dialog_list.append(new_utter_dict)
                        #*****************************************************************
                        
                    elif utter['ques_type_id'] == 5: # Boolean (secondary) question
                        bool_ques_type = utter['bool_ques_type']

                        if bool_ques_type == 1 or bool_ques_type == 2 or bool_ques_type == 4 or bool_ques_type == 5:
                            if bool_ques_type in [1,2]:
                                obj = utter['obj']
                                Qid = utter['Qid']
                                prop_res = utter['prop_res']
                                prop_Qid_par = utter['prop_Qid_par']
                            elif bool_ques_type in [4,5]:
                                obj = utter['obj']
                                obj2 = utter['obj2']
                                Qid = utter['Qid']
                                prop_res = utter['prop_res']
                                prop_Qid_par = utter['prop_Qid_par']

                            if bool_ques_type == 1:
                                ques = booleanise_ques(random.choice(sing_sub_annot_wh[prop_res]),obj)
                                ques = ques.replace('XXX',item_data[Qid])

                            elif bool_ques_type == 2:
                                ques = booleanise_ques(sing_basic2indirect(random.choice(sing_sub_annot_wh[prop_res]),Qid,child_par_dict,prop_Qid_par, prop_res),obj)
                                ques = ques.replace('XXX',item_data[Qid])

                            elif bool_ques_type == 4: # to be modified: plural form of ans. ques. required
                                ques = booleanise_ques(random.choice(sing_obj_annot_wh[prop_res]),Qid)
                                ques = ques.replace('YYY',get_multi_pphrase([item_data[obj], item_data[obj2]]))

                            elif bool_ques_type == 5:
                                ques = booleanise_ques_custom(random.choice(sing_obj_annot_wh[prop_res]),Qid)
                                ques = ques.replace('YYY',get_multi_pphrase([item_data[obj], item_data[obj2]]))

                        elif bool_ques_type == 3:
                            Qid = utter['Qid']
                            prop_res = utter['prop_res']
                            prop_Qid_par = utter['prop_Qid_par']
                            sub = utter['sub']

                            ques = sing_basic2indirect(random.choice(sing_obj_annot_wh[prop_res]),Qid,child_par_dict,prop_Qid_par, prop_res) # to be modified  
                            ques = booleanise_ques(ques,sub)

                        elif bool_ques_type == 6:
                            prop_res = utter['prop_res']
                            prop_Qid_par = utter['prop_Qid_par']
                            sub = utter['sub']
                            sub_list = utter['sub_list']

                            is_pphrase_ov = [is_par_rel_overlap(prop_Qid_par, prop_res, x) for x in plu_obj_annot_wh[prop_res]]
                            if False in is_pphrase_ov:
                                ques = sing_basic2indirect(random.choice([plu_obj_annot_wh[prop_res][i] for i in range(len(plu_obj_annot_wh[prop_res])) if is_pphrase_ov[i] == False]),sub_list[0],child_par_dict,prop_Qid_par, prop_res, False) # to be modified
                            else:
                                ques = sing_basic2indirect(random.choice(plu_obj_annot_wh[prop_res]),sub_list[0],child_par_dict,prop_Qid_par, prop_res, False)

                            ques = booleanise_ques(ques,sub)

                        #*****************************************************************
                        new_utter_dict = {}
                        for field in utter:
                            if field not in ['utterance','signature']: # copy all fields except ('utterance','signature')
                                new_utter_dict[field] = utter[field]

                        new_utter_dict['utterance'] = ques
                        new_utter_dict['signature'] = get_dict_signature(new_utter_dict)
                        dialog_list.append(new_utter_dict)
                        #*****************************************************************

                    elif utter['ques_type_id'] == 7: # count-based question
                        count_ques_type = utter['count_ques_type']
                        count_ques_sub_type = utter['count_ques_sub_type']

                        if utter['is_incomplete'] == 1:
                            continue

                        if count_ques_sub_type in [1,7]:
                            Qid = utter['Qid']
                            prop_Qid_par = utter['prop_Qid_par']
                            prop_res = utter['prop_res']
                        elif count_ques_sub_type in [2,3,4,5,6,8,9]:
                            obj_par = utter['obj_par']
                            sub_par = utter['sub_par']
                            prop_res = utter['prop_res']
                            qualifier_choice = utter['qualifier_choice']
                            if count_ques_sub_type in [3,5]:
                                N = utter['N']
                            elif count_ques_sub_type in [4,6,8,9]:
                                Z = utter['Z']

                        if count_ques_type == 1: # sub-based
                            if count_ques_sub_type == 1: # basic form
                                ques = random.choice(plu_sub_annot_wh[prop_res])
                                ques = sing_basic2count_based(ques, '', count_ques_sub_type)        
                                ques = ques.replace('XXX',item_data[Qid])
                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))

                            elif count_ques_sub_type == 7:
                                ques = random.choice(plu_sub_annot_wh[prop_res])
                                ques = sing_basic2count_based(ques, '', 1)        
                                ques = ques.replace('XXX','that %s' % child_par_dict_name_2[child_par_dict[Qid]])
                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))

                            elif count_ques_sub_type in [8,9]:
                                ques = random.choice(plu_sub_annot_wh[prop_res])
                                
                                if count_ques_sub_type == 8:
                                    ques = sing_basic2count_based(ques, qualifier_choice, 4)
                                else:
                                    ques = sing_basic2count_based(ques, qualifier_choice, 6)

                                ques = ques.replace('Z', 'that %s' % child_par_dict_name_2[child_par_dict[Z]])
                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))
                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))

                            else:
                                ques = random.choice(plu_sub_annot_wh[prop_res])
                                ques = sing_basic2count_based(ques, qualifier_choice, count_ques_sub_type)
                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))

                                if count_ques_sub_type == 2:
                                    ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))
                                elif count_ques_sub_type == 3 or count_ques_sub_type == 5:
                                    N_str = str(int(N))
                                    ques = ques.replace(' N ',' %s ' % N_str)

                                    if N > 1:
                                        ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))
                                    else:
                                        ques = ques.replace('SPPS',child_par_dict_name_2[sub_par])

                                elif count_ques_sub_type == 4 or count_ques_sub_type == 6:
                                    ques = ques.replace('Z', item_data[Z])
                                    ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))

                        elif count_ques_type == 2: # obj-based
                            if count_ques_sub_type == 1: # basic form         
                                ques = random.choice(plu_obj_annot_wh[prop_res])
                                ques = sing_basic2count_based(ques, '', count_ques_sub_type)        
                                ques = ques.replace('YYY',item_data[Qid])
                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))
                                
                            elif count_ques_sub_type == 7:
                                ques = random.choice(plu_obj_annot_wh[prop_res])
                                ques = sing_basic2count_based(ques, '', 1)        
                                ques = ques.replace('YYY','that %s' % child_par_dict_name_2[child_par_dict[Qid]])
                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[prop_Qid_par]))

                            elif count_ques_sub_type in [8,9]:
                                ques = random.choice(plu_obj_annot_wh[prop_res])
                                
                                if count_ques_sub_type == 8:
                                    ques = sing_basic2count_based(ques, qualifier_choice, 4)
                                else:
                                    ques = sing_basic2count_based(ques, qualifier_choice, 6)
                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))

                                ques = ques.replace('Z', 'that %s' % child_par_dict_name_2[child_par_dict[Z]])
                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))

                            else:
                                ques = random.choice(plu_obj_annot_wh[prop_res])
                                ques = sing_basic2count_based(ques, qualifier_choice, count_ques_sub_type)
                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))

                                if count_ques_sub_type == 2:                            
                                    ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))

                                elif count_ques_sub_type == 3 or count_ques_sub_type == 5:
                                    N_str = str(int(N))
                                    ques = ques.replace(' N ',' %s ' % N_str)

                                    if N > 1:
                                        ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))
                                    else:
                                        ques = ques.replace('OPPS',child_par_dict_name_2[obj_par])                           

                                elif count_ques_sub_type == 4 or count_ques_sub_type == 6:
                                    ques = ques.replace('Z', item_data[Z])
                                    ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))

                        #*****************************************************************
                        new_utter_dict = {}
                        for field in utter:
                            if field not in ['utterance','signature']: # copy all fields except ('utterance','signature')
                                new_utter_dict[field] = utter[field]

                        new_utter_dict['utterance'] = ques
                        new_utter_dict['signature'] = get_dict_signature(new_utter_dict)
                        dialog_list.append(new_utter_dict)
                        #*****************************************************************


                    elif utter['ques_type_id'] == 8: # count-set-based question
                        count_ques_type = utter['count_ques_type']
                        count_ques_sub_type = utter['count_ques_sub_type']

                        if utter['is_incomplete'] == 1:
                            continue
                        
                        if count_ques_type == 1:
                            if count_ques_sub_type == 1:
                                Qid = utter['Qid']
                                Qid_2 = utter['Qid_2']
                                obj_par = utter['obj_par']
                                prop_res = utter['prop_res']
                                set_op = utter['set_op']
                            elif count_ques_sub_type in [2,8]:
                                Qid = utter['Qid']
                                obj_par_1 = utter['obj_par_1']
                                obj_par_2 = utter['obj_par_2']
                                prop_res = utter['prop_res']
                                set_op = utter['set_op']
                            elif count_ques_sub_type in [3,4,5,6,7,9,10]:
                                obj_par = utter['obj_par']
                                sub_par_1 = utter['sub_par_1']
                                sub_par_2 = utter['sub_par_2']
                                prop_res = utter['prop_res']
                                qualifier_choice = utter['qualifier_choice']
                                set_op = utter['set_op']
                                if count_ques_sub_type in [4,6]:
                                    N = utter['N']
                                elif count_ques_sub_type in [5,7,9,10]:
                                    Z = utter['Z']
                        else:
                            if count_ques_sub_type == 1:
                                Qid = utter['Qid']
                                Qid_2 = utter['Qid_2']
                                sub_par = utter['sub_par']
                                prop_res = utter['prop_res']
                                set_op = utter['set_op']
                            elif count_ques_sub_type in [2,8]:
                                Qid = utter['Qid']
                                sub_par_1 = utter['sub_par_1']
                                sub_par_2 = utter['sub_par_2']
                                prop_res = utter['prop_res']
                                set_op = utter['set_op']
                            elif count_ques_sub_type in [3,4,5,6,7,9,10]:
                                sub_par = utter['sub_par']
                                obj_par_1 = utter['obj_par_1']
                                obj_par_2 = utter['obj_par_2']
                                prop_res = utter['prop_res']
                                qualifier_choice = utter['qualifier_choice']
                                set_op = utter['set_op']
                                if count_ques_sub_type in [4,6]:
                                    N = utter['N']
                                elif count_ques_sub_type in [5,7,9,10]:
                                    Z = utter['Z']

                        if count_ques_type == 1: # sub-based
                            if count_ques_sub_type == 1: # basic form           
                                ques = random.choice(plu_sub_annot_wh[prop_res])    
                                ques = sing_basic2count_set_based(ques, '', set_op, count_ques_sub_type)        
                                ques = ques.replace('XXX_1',item_data[Qid])
                                ques = ques.replace('XXX_2',item_data[Qid_2])
                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))

                            elif count_ques_sub_type == 2:
                                ques = random.choice(plu_sub_annot_wh[prop_res])
                                ques = sing_basic2count_set_based(ques, '', set_op, count_ques_sub_type)        
                                ques = ques.replace('XXX',item_data[Qid])
                                ques = ques.replace('OPP_1s',sing2plural(child_par_dict_name_2[obj_par_1]))
                                ques = ques.replace('OPP_2s',sing2plural(child_par_dict_name_2[obj_par_2]))

                            elif count_ques_sub_type == 8:
                                ques = random.choice(plu_sub_annot_wh[prop_res])
                                ques = sing_basic2count_set_based(ques, '', set_op, 2)        
                                ques = ques.replace('XXX','that %s' % child_par_dict_name_2[child_par_dict[Qid]])
                                ques = ques.replace('OPP_1s',sing2plural(child_par_dict_name_2[obj_par_1]))
                                ques = ques.replace('OPP_2s',sing2plural(child_par_dict_name_2[obj_par_2]))

                            elif count_ques_sub_type in [9,10]:
                                ques = random.choice(plu_sub_annot_wh[prop_res])
                                
                                if count_ques_sub_type == 9:
                                    ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, 5)
                                else:
                                    ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, 7)

                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))

                                ques = ques.replace('Z', 'that %s' % child_par_dict_name_2[child_par_dict[Z]])
                                ques = ques.replace('SPP_1s',sing2plural(child_par_dict_name_2[sub_par_1]))
                                ques = ques.replace('SPP_2s',sing2plural(child_par_dict_name_2[sub_par_2]))

                            else:
                                ques = random.choice(plu_sub_annot_wh[prop_res])
                                ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, count_ques_sub_type)
                                ques = ques.replace('OPPS',sing2plural(child_par_dict_name_2[obj_par]))
                                ques = ques.replace('SPP_1s',sing2plural(child_par_dict_name_2[sub_par_1]))
                                ques = ques.replace('SPP_2s',sing2plural(child_par_dict_name_2[sub_par_2]))

                                if count_ques_sub_type == 3:                            
                                    # do nothing
                                    pass
                                elif count_ques_sub_type == 4 or count_ques_sub_type == 6:
                                    N_str = str(int(N))
                                    ques = ques.replace(' N ',' %s ' % N_str)

                                elif count_ques_sub_type == 5 or count_ques_sub_type == 7:
                                    ques = ques.replace('Z', item_data[Z])
                                    

                        elif count_ques_type == 2: # obj-based
                            if count_ques_sub_type == 1: # basic form
                                ques = random.choice(plu_obj_annot_wh[prop_res])
                                ques = sing_basic2count_set_based(ques, '', set_op, count_ques_sub_type)        
                                ques = ques.replace('YYY_1',item_data[Qid])
                                ques = ques.replace('YYY_2',item_data[Qid_2])
                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))

                            elif count_ques_sub_type == 2:

                                ques = random.choice(plu_obj_annot_wh[prop_res])
                                ques = sing_basic2count_set_based(ques, '', set_op, count_ques_sub_type)        
                                ques = ques.replace('YYY',item_data[Qid])
                                ques = ques.replace('SPP_1s',sing2plural(child_par_dict_name_2[sub_par_1]))
                                ques = ques.replace('SPP_2s',sing2plural(child_par_dict_name_2[sub_par_2]))

                            elif count_ques_sub_type == 8:
                                ques = random.choice(plu_obj_annot_wh[prop_res])
                                ques = sing_basic2count_set_based(ques, '', set_op, 2)        
                                ques = ques.replace('YYY','that %s' % child_par_dict_name_2[child_par_dict[Qid]])
                                ques = ques.replace('SPP_1s',sing2plural(child_par_dict_name_2[sub_par_1]))
                                ques = ques.replace('SPP_2s',sing2plural(child_par_dict_name_2[sub_par_2]))

                            elif count_ques_sub_type in [9,10]:
                                ques = random.choice(plu_obj_annot_wh[prop_res])
                                
                                if count_ques_sub_type == 9:
                                    ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, 5)
                                else:
                                    ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, 7)
                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))

                                ques = ques.replace('Z', 'that %s' % child_par_dict_name_2[child_par_dict[Z]])
                                ques = ques.replace('OPP_1s',sing2plural(child_par_dict_name_2[obj_par_1]))
                                ques = ques.replace('OPP_2s',sing2plural(child_par_dict_name_2[obj_par_2]))

                            else:
                                ques = random.choice(plu_obj_annot_wh[prop_res])
                                ques = sing_basic2count_set_based(ques, qualifier_choice, set_op, count_ques_sub_type)
                                ques = ques.replace('SPPS',sing2plural(child_par_dict_name_2[sub_par]))
                                ques = ques.replace('OPP_1s',sing2plural(child_par_dict_name_2[obj_par_1]))
                                ques = ques.replace('OPP_2s',sing2plural(child_par_dict_name_2[obj_par_2]))

                                if count_ques_sub_type == 3:                            
                                   # do nothing
                                   pass
                                elif count_ques_sub_type == 4 or count_ques_sub_type == 6:
                                    N_str = str(int(N))

                                    ques = ques.replace(' N ',' %s ' % N_str)

                                elif count_ques_sub_type == 5 or count_ques_sub_type == 7:
                                    ques = ques.replace('Z', item_data[Z])

                        #*****************************************************************
                        new_utter_dict = {}
                        for field in utter:
                            if field not in ['utterance','signature']: # copy all fields except ('utterance','signature')
                                new_utter_dict[field] = utter[field]

                        new_utter_dict['utterance'] = ques
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
                # utter_id += 1
                #**************

            try:
                assert is_valid_dialog(dialog_list)
            except:
                print 'Dialog list not valid'
            try:
                assert len(dialog_list) == len(utter_list)
            except:
                print 'lengths unequal src and dest'

            outfile = open(os.path.join(args.output_dir, dir_name, filename), 'wb')
            json.dump(dialog_list, outfile, indent = 1)
            outfile.flush()


        except:
            logging.exception('Something aweful happened')

f1.close()