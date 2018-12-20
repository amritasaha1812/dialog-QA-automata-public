import sys, os, json, pickle, fnmatch, logging, nltk

data_dir = sys.argv[1]
count = 0

for root, dirnames, filenames in os.walk(data_dir):
    for filename in fnmatch.filter(filenames, '*.json'):
        try:
            json_file = os.path.join(root, filename)
            dialog_list = json.load(open(json_file,'r'))
        except:
            # logging.exception('Something aweful happened')
            continue
        count += 1
        if count % 100 == 0:
            print count
    	for utter in dialog_list:
            if 'ques_type_id' in utter and utter['ques_type_id'] == 8 and 'count_ques_sub_type' in utter and utter['count_ques_sub_type']==1:
            	if len(set(utter['entities'])) == 1:
            		print os.path.join(root, filename)
            		print utter['utterance']
