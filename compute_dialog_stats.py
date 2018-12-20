import sys, os, json, pickle, fnmatch, logging, nltk
import xlsxwriter

data_dir = sys.argv[1]
outfile = sys.argv[2]

n_dialog = 0
kb_entity_set = set([])

n_utter_list = [] # per-dialog
n_dialog_state_list = [] # per-dialog

n_user_utter = 0 # per utterance
n_sys_utter = 0 # per utterance
n_user_ent_list = [] # per utterance
n_user_rel_list = [] # per utterance
n_sys_ent_list = [] # per utterance
n_sys_rel_list = [] # per utterance

n_user_word_list = []
n_sys_word_list = []

n_dir_basic_sing = 0
n_dir_basic_plu = 0
n_indir_basic_sing = 0
n_indir_basic_plu = 0
n_incomp_basic = 0
n_dir_set = 0
n_incomp_set = 0

n_incomp_count = 0

n_dir_bool = 0
n_indir_bool = 0
n_bool_multi_ans = 0
n_bool_plu_indir = 0
n_clari = 0

n_set_aff = 0
n_set_neg = 0

n_set_union = 0
n_set_inter = 0
n_set_diff = 0

ques_id_5_arr = [0,0,0,0,0,0,0]
ques_id_7_arr = [0,0,0,0,0,0,0,0,0,0]
ques_id_8_arr = [0,0,0,0,0,0,0,0,0,0,0]

ques_7_1_incomp = 0
ques_7_4_incomp = 0
ques_7_6_incomp = 0

ques_8_2_incomp = 0
ques_8_5_incomp = 0
ques_8_7_incomp = 0

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
        
        n_utter_list.append(len(dialog_list))

        dialog_state_set = set([])

        for utter in dialog_list:
            if 'speaker' in utter and utter['speaker'] == 'USER':
                n_user_utter += 1
                if 'entities' in utter:
                    n_user_ent_list.append(len(utter['entities']))
                    kb_entity_set.update(utter['entities'])
                if 'relations' in utter:
                    n_user_rel_list.append(len(utter['relations']))

                utterance = utter['utterance']
                n_words = len(nltk.word_tokenize(utterance))
                n_user_word_list.append(n_words)

            if 'speaker' in utter and utter['speaker'] == 'SYSTEM':
                n_sys_utter += 1
                if 'entities' in utter:
                    n_sys_ent_list.append(len(utter['entities']))
                    kb_entity_set.update(utter['entities'])
                if 'relations' in utter:
                    n_sys_rel_list.append(len(utter['relations']))

                utterance = utter['utterance']
                n_words = len(nltk.word_tokenize(utterance))
                n_sys_word_list.append(n_words)

            if 'ques_type_id' in utter:
                ques_type_id = utter['ques_type_id']
                dialog_state_set.add(ques_type_id)

                if ques_type_id == 1:
                    n_dir_basic_sing += 1
                elif ques_type_id == 2:
                    assert 'sec_ques_type' in utter and 'sec_ques_sub_type' in utter
                    sec_ques_type = utter['sec_ques_type']
                    sec_ques_sub_type = utter['sec_ques_sub_type']
                    if sec_ques_sub_type == 1:
                        n_dir_basic_sing += 1
                    elif sec_ques_sub_type == 2:
                        n_indir_basic_sing += 1
                    elif sec_ques_sub_type ==3:
                        n_indir_basic_plu += 1
                    else:
                        n_dir_basic_plu += 1
                elif ques_type_id == 3:
                    n_clari += 1
                elif ques_type_id == 4:
                    ques = utter['utterance']
                    
                    if utter['is_inc']==1:
                        n_incomp_set += 1
                    else:
                        n_dir_set += 1

                    assert 'set_op_choice' in utter
                    set_op_choice = utter['set_op_choice']
                    if set_op_choice == 1:
                        n_set_union += 1
                    elif set_op_choice == 2:
                        n_set_inter += 1
                    else:
                        n_set_diff += 1

                elif ques_type_id == 5:
                    assert 'bool_ques_type' in utter
                    bool_ques_type = utter['bool_ques_type']
                    if bool_ques_type in [1, 4]:
                        n_dir_bool += 1
                    else:
                        n_indir_bool += 1

                    if bool_ques_type in [4, 5]:
                        n_bool_multi_ans += 1
                    if bool_ques_type == 6:
                        n_bool_plu_indir += 1

                    ques_id_5_arr[bool_ques_type] += 1

                elif ques_type_id == 6:
                    assert 'inc_ques_type' in utter
                    inc_ques_type = utter['inc_ques_type']
                    if inc_ques_type == 3:
                        n_incomp_count += 1
                    else:
                        n_incomp_basic += 1
                elif ques_type_id == 7:
                    assert 'count_ques_sub_type' in utter
                    count_ques_sub_type = utter['count_ques_sub_type']
                    ques_id_7_arr[count_ques_sub_type] += 1
                    if utter['is_incomplete'] == 1:
                        if count_ques_sub_type == 1:
                            ques_7_1_incomp += 1
                        elif count_ques_sub_type == 4:
                            ques_7_4_incomp += 1
                        elif count_ques_sub_type == 6:
                            ques_7_6_incomp += 1


                elif ques_type_id == 8:
                    assert 'count_ques_sub_type' in utter
                    count_ques_sub_type = utter['count_ques_sub_type']
                    ques_id_8_arr[count_ques_sub_type] += 1
                    if utter['is_incomplete'] == 1:
                        if count_ques_sub_type == 2:
                            ques_8_2_incomp += 1
                        elif count_ques_sub_type == 5:
                            ques_8_5_incomp += 1
                        elif count_ques_sub_type == 7:
                            ques_8_7_incomp += 1

        # if len(dialog_state_set) == 0:
        #     print json_file
        n_dialog_state_list.append(len(dialog_state_set))

#***************************************************************************
n_utter_avg = sum(n_utter_list)*1.0/len(n_utter_list)
n_dialog_state_avg = sum(n_dialog_state_list)*1.0/len(n_dialog_state_list)

n_user_ent_avg = sum(n_user_ent_list)*1.0/len(n_user_ent_list)
n_user_rel_avg = sum(n_user_rel_list)*1.0/len(n_user_rel_list)
n_sys_ent_avg = sum(n_sys_ent_list)*1.0/len(n_sys_ent_list)
n_sys_rel_avg = sum(n_sys_rel_list)*1.0/len(n_sys_rel_list)
n_user_word_avg = sum(n_user_word_list)*1.0/len(n_user_word_list)
n_sys_word_avg = sum(n_sys_word_list)*1.0/len(n_sys_word_list)
#***************************************************************************
workbook = xlsxwriter.Workbook('%s.xlsx' % outfile)
worksheet = workbook.add_worksheet()

worksheet.write(0, 0, 'No. of dialogs')
worksheet.write(1, 0, 'Avg. no. of utterances per dialog')
worksheet.write(2, 0, 'Avg. no. of dialog states per dialog')
worksheet.write(3, 0, 'No. of user utterances')
worksheet.write(4, 0, 'No. of system utterances')
worksheet.write(5, 0, 'Avg. no. of KB entities in user utterance')
worksheet.write(6, 0, 'Avg. no. of KB relations in user utterance')
worksheet.write(7, 0, 'Avg. no. of KB entities in system utterance')
worksheet.write(8, 0, 'Avg. no. of KB relations in system utterance')
worksheet.write(9, 0, 'Avg. no. of words in user utterance')
worksheet.write(10, 0, 'Avg. no. of words in system utterance')

worksheet.write(11, 0, 'n_dir_basic_sing')
worksheet.write(12, 0, 'n_dir_basic_plu')
worksheet.write(13, 0, 'n_indir_basic_sing')
worksheet.write(14, 0, 'n_indir_basic_plu')
worksheet.write(15, 0, 'n_incomp_basic')
worksheet.write(16, 0, 'n_dir_set')
worksheet.write(17, 0, 'n_incomp_set')
worksheet.write(18, 0, 'n_incomp_count')
worksheet.write(19, 0, 'n_dir_bool')
worksheet.write(20, 0, 'n_clari')
worksheet.write(21, 0, 'n_bool_multi_ans')
worksheet.write(22, 0, 'n_bool_plu_indir')
worksheet.write(23, 0, 'n_set_union')
worksheet.write(24, 0, 'n_set_inter')
worksheet.write(25, 0, 'n_set_diff')

worksheet.write(26, 0, 'Quantitative|Count|Single entity type')
worksheet.write(27, 0, 'Quantitative|Min/Max|Single entity type')
worksheet.write(28, 0, 'Quantitative|Atleast/ Atmost/ Approx. the same/Equal|Single entity type')
worksheet.write(29, 0, 'Comparative|More/Less|Single entity type')
worksheet.write(30, 0, 'Quantitative|Count over Atleast/ Atmost/ Approx. the same/Equal|Single entity type')
worksheet.write(31, 0, 'Comparative|Count over More/Less|Single entity type')
worksheet.write(32, 0, 'Quantitative|Count|Single entity type|Indirect')
worksheet.write(33, 0, 'Comparative|More/Less|Single entity type|Indirect')
worksheet.write(34, 0, 'Comparative|Count over More/Less|Single entity type|Indirect')
worksheet.write(35, 0, 'Quantitative|Count|Single entity type|Incomplete')
worksheet.write(36, 0, 'Comparative|More/Less|Single entity type|Incomplete')
worksheet.write(37, 0, 'Comparative|Count over More/Less|Single entity type|Incomplete')

worksheet.write(38, 0, 'Quantitative|Count|Mult. entity type')
worksheet.write(39, 0, 'Quantitative|Count|Logical operators')
worksheet.write(40, 0, 'Quantitative|Min/Max|Mult. entity type')
worksheet.write(41, 0, 'Quantitative|Atleast/ Atmost/ Approx. the same/Equal|Mult. entity type')
worksheet.write(42, 0, 'Comparative|More/Less|Mult. entity type')
worksheet.write(43, 0, 'Quantitative|Count over Atleast/ Atmost/ Approx. the same/Equal|Mult. entity type')
worksheet.write(44, 0, 'Comparative|Count over More/Less|Mult. entity type')
worksheet.write(45, 0, 'Quantitative|Count|Logical operators|Indirect')
worksheet.write(46, 0, 'Comparative|More/Less|Mult. entity type|Indirect')
worksheet.write(47, 0, 'Comparative|Count over More/Less|Mult. entity type|Indirect')
worksheet.write(48, 0, 'Quantitative|Count|Mult. entity type|Clarification')
worksheet.write(49, 0, 'Comparative|More/Less|Mult. entity type|Clarification')
worksheet.write(50, 0, 'Comparative|Count over More/Less|Mult. entity type|Clarification')

worksheet.write(51, 0, 'Verification|2 entities, both direct')
worksheet.write(52, 0, 'Verification|2 entities, one direct and one indirect, subject is indirect')
worksheet.write(53, 0, 'Verification|2 entities, one direct and one indirect, object is indirect')
worksheet.write(54, 0, 'Verification|3 entities, all direct, 2 are query entities')
worksheet.write(55, 0, 'Verification|3 entities, 2 direct, 2(direct) are query entities, subject is indirect')
worksheet.write(56, 0, 'Verification|one entity, multiple entities (as object) referred indirectly')

worksheet.write(0, 1, n_dialog)
worksheet.write(1, 1, n_utter_avg)
worksheet.write(2, 1, n_dialog_state_avg)
worksheet.write(3, 1, n_user_utter)
worksheet.write(4, 1, n_sys_utter)
worksheet.write(5, 1, n_user_ent_avg)
worksheet.write(6, 1, n_user_rel_avg)
worksheet.write(7, 1, n_sys_ent_avg)
worksheet.write(8, 1, n_sys_rel_avg)
worksheet.write(9, 1, n_user_word_avg)
worksheet.write(10, 1, n_sys_word_avg)
worksheet.write(11, 1, n_dir_basic_sing)
worksheet.write(12, 1, n_dir_basic_plu)
worksheet.write(13, 1, n_indir_basic_sing)
worksheet.write(14, 1, n_indir_basic_plu)
worksheet.write(15, 1, n_incomp_basic)
worksheet.write(16, 1, n_dir_set)
worksheet.write(17, 1, n_incomp_set)
worksheet.write(18, 1, n_incomp_count)
worksheet.write(19, 1, n_dir_bool)
worksheet.write(20, 1, n_clari)
worksheet.write(21, 1, n_bool_multi_ans)
worksheet.write(22, 1, n_bool_plu_indir)
worksheet.write(23, 1, n_set_union)
worksheet.write(24, 1, n_set_inter)
worksheet.write(25, 1, n_set_diff)

worksheet.write(26, 1, ques_id_7_arr[1])
worksheet.write(27, 1, ques_id_7_arr[2])
worksheet.write(28, 1, ques_id_7_arr[3])
worksheet.write(29, 1, ques_id_7_arr[4])
worksheet.write(30, 1, ques_id_7_arr[5])
worksheet.write(31, 1, ques_id_7_arr[6])
worksheet.write(32, 1, ques_id_7_arr[7])
worksheet.write(33, 1, ques_id_7_arr[8])
worksheet.write(34, 1, ques_id_7_arr[9])
worksheet.write(35, 1, ques_7_1_incomp)
worksheet.write(36, 1, ques_7_4_incomp)
worksheet.write(37, 1, ques_7_6_incomp)
worksheet.write(38, 1, ques_id_8_arr[1])
worksheet.write(39, 1, ques_id_8_arr[2])
worksheet.write(40, 1, ques_id_8_arr[3])
worksheet.write(41, 1, ques_id_8_arr[4])
worksheet.write(42, 1, ques_id_8_arr[5])
worksheet.write(43, 1, ques_id_8_arr[6])
worksheet.write(44, 1, ques_id_8_arr[7])
worksheet.write(45, 1, ques_id_8_arr[8])
worksheet.write(46, 1, ques_id_8_arr[9])
worksheet.write(47, 1, ques_id_8_arr[10])
worksheet.write(48, 1, ques_8_2_incomp)
worksheet.write(49, 1, ques_8_5_incomp)
worksheet.write(50, 1, ques_8_7_incomp)

worksheet.write(51, 1, ques_id_5_arr[1])
worksheet.write(52, 1, ques_id_5_arr[2])
worksheet.write(53, 1, ques_id_5_arr[3])
worksheet.write(54, 1, ques_id_5_arr[4])
worksheet.write(55, 1, ques_id_5_arr[5])
worksheet.write(56, 1, ques_id_5_arr[6])

workbook.close()
# f1.write('No. of dialogs = %d\n' % n_dialog)
# f1.write('Avg. no. of utterances per dialog = %f\n' % n_utter_avg)
# f1.write('Avg. no. of dialog states per dialog = %f\n' % n_dialog_state_avg)

# f1.write('No. of user utterances = %d\n' % n_user_utter)
# f1.write('No. of system utterances = %d\n' % n_sys_utter)

# f1.write('Avg. no. of KB entities in user utterance = %f\n' % n_user_ent_avg)
# f1.write('Avg. no. of KB relations in user utterance = %f\n' % n_user_rel_avg)

# f1.write('Avg. no. of KB entities in system utterance = %f\n' % n_sys_ent_avg)
# f1.write('Avg. no. of KB relations in system utterance = %f\n' % n_sys_rel_avg)

# f1.write('Avg. no. of words in user utterance = %f\n' % n_user_word_avg)
# f1.write('Avg. no. of words in system utterance = %f\n' % n_sys_word_avg)

# f1.write('n_dir_basic_sing= %d\n' % n_dir_basic_sing)
# f1.write('n_dir_basic_plu= %d\n' % n_dir_basic_plu)
# f1.write('n_indir_basic_sing= %d\n' % n_indir_basic_sing)
# f1.write('n_indir_basic_plu= %d\n' % n_indir_basic_plu)
# f1.write('n_incomp_basic= %d\n' % n_incomp_basic)
# f1.write('n_dir_set= %d\n' % n_dir_set)
# f1.write('n_incomp_set= %d\n' % n_incomp_set)
# f1.write('n_dir_count= %d\n' % n_dir_count)
# f1.write('n_dir_comp_count= %d\n' % n_dir_comp_count)
# f1.write('n_incomp_count= %d\n' % n_incomp_count)
# f1.write('n_dir_count_set= %d\n' % n_dir_count_set)
# f1.write('n_dir_comp_count_set= %d\n' % n_dir_comp_count_set)
# f1.write('n_dir_bool= %d\n' % n_dir_bool)
# f1.write('n_indir_bool= %d\n' % n_indir_bool)
# f1.write('n_clari= %d\n' % n_clari)
# f1.write('n_bool_multi_ans= %d\n' % n_bool_multi_ans)
# f1.write('n_bool_plu_indir= %d\n' % n_bool_plu_indir)

# f1.write('n_set_aff= %d\n' % n_set_aff)
# f1.write('n_set_neg= %d\n' % n_set_neg)

# f1.write('n_set_union= %d\n' % n_set_union)
# f1.write('n_set_inter= %d\n' % n_set_inter)
# f1.write('n_set_diff= %d\n' % n_set_diff)

# f1.close()

# with open('entity_set_%s.pickle' % mode,'w') as f1:
#     pickle.dump(kb_entity_set, f1)

# with open('n_dialog_state_list.pickle','w') as f1:
#     pickle.dump(n_dialog_state_list, f1)