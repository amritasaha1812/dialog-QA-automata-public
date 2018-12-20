import sys, os, json, pickle, fnmatch, logging

data_dir = sys.argv[1]
ques_type_id = int(sys.argv[2])
count_ques_type = int(sys.argv[3])
count_ques_sub_type = int(sys.argv[4])

for root, dirnames, filenames in os.walk(data_dir):
    for filename in fnmatch.filter(filenames, '*.json'):
        try:
            json_file = os.path.join(root, filename)
            dialog_list = json.load(open(json_file,'r'))
        except:
            # logging.exception('Something aweful happened')
            continue

        # n_dialog += 1

        # if n_dialog % 100 == 0:
        #     print 'n_dialog = %d' % n_dialog

        for utter in dialog_list:
            if 'ques_type_id' in utter and utter['ques_type_id'] == ques_type_id and 'count_ques_type' in utter and utter['count_ques_type'] == count_ques_type and 'count_ques_sub_type' in utter and utter['count_ques_sub_type'] == count_ques_sub_type:
                print '%s %s' % (utter['utterance'], os.path.join(root, filename))
