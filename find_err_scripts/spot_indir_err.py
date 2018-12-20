import sys, os, json, pickle, fnmatch, logging

# data_dir = sys.argv[1]
data_dir = '/home/vardaan/projects/rpp-bengioy/vardaan/CSQA_v7/'
n_dialog = 0

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
            if 'ques_type_id' in utter and utter['ques_type_id'] == 2 and utter['sec_ques_sub_type'] == 2:

                if 'entities' in dialog_list[utter_id-2] and len(dialog_list[utter_id-2]['entities'])>0 and dialog_list[utter_id-2]['entities'][0] in child_par_dict and child_par_dict[dialog_list[utter_id-2]['entities'][0]] in set([child_par_dict[x] for i,x in enumerate(dialog_list[utter_id-2]['entities']) if x in child_par_dict and i>0]) and 'ques_type_id' in dialog_list[utter_id-2] and utter['Qid'] in dialog_list[utter_id-2]['entities'] and (('ques_type_id' not in dialog_list[utter_id+1]) or ('ques_type_id' in dialog_list[utter_id+1] and dialog_list[utter_id+1]['ques_type_id']!=3)):
                    print 'ERROR!!!'
                    print json_file
                    print utter['utterance']

