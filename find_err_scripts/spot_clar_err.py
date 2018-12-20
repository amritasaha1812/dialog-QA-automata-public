import sys, os, json, pickle, fnmatch, logging

data_dir = sys.argv[1]

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

        for utter_id,utter in enumerate(dialog_list):
            if 'ques_type_id' in utter:
                ques_type_id = utter['ques_type_id']
                if ques_type_id == 3:
                    try:
                        if dialog_list[utter_id-1]['ques_type_id'] == 2 and dialog_list[utter_id-1]['sec_ques_sub_type'] == 2:
                            print 'pass'
                            pass
                        else:
                            print filename
                    except:
                        print filename
