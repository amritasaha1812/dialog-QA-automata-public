#!/home/vardaan/anaconda2/bin/python -u
import sys, os, json, pickle, fnmatch, logging

# data_dir = sys.argv[1]
data_dir = '/home/vardaan/projects/rpp-bengioy/vardaan/CSQA_v7/'

# with codecs.open('proc_json/child_par_dict_save.json','r','utf-8') as data_file:
#     child_par_dict = json.load(data_file)
# print 'Successfully loaded child_par_dict json'

child_par_dict_keys = set(child_par_dict.keys())

n_dialog = 0
n_err = 0

for root, dirnames, filenames in os.walk(data_dir):
    for filename in fnmatch.filter(filenames, '*.json'):
        try:
            json_file = os.path.join(root, filename)
            dialog_list = json.load(open(json_file,'r'))
        except:
            # logging.exception('Something aweful happened')
            continue

        n_dialog += 1

        if n_dialog % 100 == 0:
            print 'n_dialog = %d' % n_dialog

        for utter_id, utter in enumerate(dialog_list):
            if 'ques_type_id' in utter and 'entities_in_utterance' in utter:
                try:
                    assert len(child_par_dict_keys & set(utter['entities_in_utterance'])) == len(set(utter['entities_in_utterance']))
                except:
                    print 'ERROR!!!'
                    try:
                        print (set(utter['entities_in_utterance']) - child_par_dict_keys)
                    except:
                        print utter['utterance']
                    # print json_file
                    # print utter['utterance']
                    n_err += 1

print n_err
print 'Total no. of ERROR = %d' % n_err

