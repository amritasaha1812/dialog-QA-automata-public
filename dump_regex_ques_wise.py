import sys, os, json, pickle, fnmatch, logging, nltk
import collections

dir_name = sys.argv[1]
regex_save_dir = sys.argv[2]

n_dialog = 0

regex_ques_all = list()

if not os.path.exists(regex_save_dir):
    os.makedirs(regex_save_dir)

for root, dirnames, filenames in os.walk(dir_name):
    for filename in fnmatch.filter(filenames, '*.json'):
        try:
            json_file = os.path.join(root, filename)
        except:
            logging.exception('Something aweful happened')
            continue

        n_dialog += 1

        if n_dialog % 100 == 0:
            print 'n_dialog = %d' % n_dialog

        dialog_list = json.load(open(json_file,'r'))

        for utter_id, utter in enumerate(dialog_list):
	    if 'ques_type_id' in dialog_list[utter_id]:
                ques_type_id = dialog_list[utter_id]['ques_type_id']
                if 'signature' in utter:
                    regex = utter['signature']
                else:
                    continue
                regex_ques_all.append(regex)
            else:
                continue

            
with open(os.path.join(regex_save_dir,'regex_ques_all.pickle'),'w') as f1:
    pickle.dump(regex_ques_all, f1)

# with open('n_dialog_state_list.pickle','w') as f1:
#     pickle.dump(n_dialog_state_list, f1)
