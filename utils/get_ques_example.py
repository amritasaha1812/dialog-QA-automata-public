import sys, os, json, pickle, fnmatch, logging, nltk

data_dir = sys.argv[1]
ques_type = int(sys.argv[2])
set_op = int(sys.argv[3])

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
            if 'ques_type_id' in utter:
                ques_type_id = utter['ques_type_id']
                if ques_type == ques_type_id and 'set_op' in utter and utter['set_op']==set_op:
                	print utter['utterance']
                        print filename
