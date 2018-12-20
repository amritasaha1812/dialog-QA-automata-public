#!/home/vardaan/anaconda2/bin/python -u
import sys, os, json, pickle, fnmatch, logging

# data_dir = sys.argv[1]
data_dir = '/home/vardaan/projects/rpp-bengioy/vardaan/CSQA_v6/'
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
            if 'ques_type_id' in utter and 'is_incomplete' in utter and utter['is_incomplete'] == 1 and ((utter['ques_type_id'] == 7 and utter['count_ques_sub_type'] == 1) or (utter['ques_type_id'] == 8 and utter['count_ques_sub_type'] == 2)):
                try:
                    if utter['Qid'] == dialog_list[utter_id-2]['Qid']:
                        print 'ERROR!!!'
                        print json_file
                        print utter['utterance']
                        n_err += 1
                except:
                    print utter['utterance']
                    print ('Qid' in utter)
                    print ('Qid' in dialog_list[utter_id-2])

print n_err
print 'Total no. of ERROR = %d' % n_err

