import sys, os, json, fnmatch, logging

data_dir = sys.argv[1]
n_dialog = 0

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
            if 'ques_type_id' in utter and utter['ques_type_id']==4:
                # if 'that' in dialog_list[utter_id+1]['utterance']:
                # print filename
                # if (utter_id+2)<len(dialog_list) and 'sec_ques_sub_type' in dialog_list[utter_id+2] and dialog_list[utter_id+2]['sec_ques_sub_type'] == 1:
                    # print filename
                # if (utter_id+2)<len(dialog_list) and 'that' in dialog_list[utter_id+2]['utterance']:
                #     print 'ERROR!!!'
                #     print dialog_list[utter_id+2]['utterance']
                #     if 'bool_ques_type' in dialog_list[utter_id+2]:
                #         print dialog_list[utter_id+2]['bool_ques_type']
                # if (utter_id+2)<len(dialog_list):
                #     # print 'ERROR!!!'
                #     # print dialog_list[utter_id+2]['utterance']
                #     if 'bool_ques_type' in dialog_list[utter_id+2] and dialog_list[utter_id+2]['bool_ques_type']==6:
                #         print json_file
                # if utter['is_inc'] == 1 and dialog_list[utter_id-2]['ques_type_id']!=2:
                #     print 'ERROR!!!'
                #     print json_file
                # if len(dialog_list[utter_id-1]['entities'])<2:
                #     print 'ERROR!!!'
                #     print utter['utterance']
                #     print dialog_list[utter_id-1]['utterance']
                # if (utter_id+2)<len(dialog_list) and 'sec_ques_sub_type' in dialog_list[utter_id+2] and dialog_list[utter_id+2]['sec_ques_sub_type'] == 3:
                #     print 'ERROR!!!'
                #     print json_file
                #     print dialog_list[utter_id+2]['utterance']
                # if (utter_id+3)<len(dialog_list) and 'Did you mean' in dialog_list[utter_id+3]['utterance']:
                #     print 'ERROR!!!'
                # print utter['utterance']
                # print json_file
                # if (utter_id+2)<len(dialog_list):
                #     print dialog_list[utter_id+2]['utterance']
                # if (utter_id+2)<len(dialog_list) and ('that' in dialog_list[utter_id+2]['utterance'] or 'those' in dialog_list[utter_id+2]['utterance'] or 'these' in dialog_list[utter_id+2]['utterance']):
                #     print 'ERROR!!!'
                #     print dialog_list[utter_id+2]['utterance']
                if (utter_id+2)<len(dialog_list) and is_indirect(dialog_list[utter_id+2]):
                    print 'ERROR!!!'
                    print json_file
                    # print dialog_list[utter_id+2]['utterance']
                # if (utter_id+3)<len(dialog_list) and 'Did you mean' in dialog_list[utter_id+3]['utterance']:
                #     print 'ERROR!!!'
                #     print dialog_list[utter_id+2]['utterance']


