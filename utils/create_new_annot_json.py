import sys, os, json, pickle, fnmatch, logging, nltk
from xlrd import open_workbook

wb = open_workbook('../new_templates.xlsx')

sheet = wb.sheets()[0]

sing_sub_annot_wh = {}
sing_obj_annot_wh = {}

sing_sub_annot = {}
sing_obj_annot = {}

rows = []
for row in range(1, sheet.nrows):
    pid = sheet.cell(row,0).value
    # print pid
    sing_sub_annot_wh[pid] = []
    sing_obj_annot_wh[pid] = []
    sing_sub_annot[pid] = []
    sing_obj_annot[pid] = []

    for i in range(6,11):
        annot = sheet.cell(row,i).value
        # if 'xxx' not in annot.lower():
        #     print annot

        annot_t = nltk.word_tokenize(annot.lower())

        if len(annot)>0:
            try:
                assert 'xxx' in annot_t
            except:
                print annot
                print annot_t
                print 'flag1'
                # sys.exit(0)
            sing_sub_annot[pid].append(' '.join(nltk.word_tokenize(annot)))

            if ('spp' not in annot_t) and ('opp' not in annot_t):
                sing_sub_annot_wh[pid].append(' '.join(nltk.word_tokenize(annot)))
            elif 'spp' in annot_t and annot_t.index('spp')==1:
                sing_sub_annot_wh[pid].append(' '.join(nltk.word_tokenize(annot)))
            elif 'opp' in annot_t and annot_t.index('opp')==1:
                sing_sub_annot_wh[pid].append(' '.join(nltk.word_tokenize(annot)))

    for i in range(1,6):
        annot = sheet.cell(row,i).value
        # if 'yyy' not in annot.lower():
        #     print annot

        annot_t = nltk.word_tokenize(annot.lower())

        if len(annot)>0:
            try:
                assert 'yyy' in annot_t
            except:
                print annot
                print annot_t
                print 'flag2'
                # sys.exit(0)
            sing_obj_annot[pid].append(' '.join(nltk.word_tokenize(annot)))

            if ('spp' not in annot_t) and ('opp' not in annot_t):
                sing_obj_annot_wh[pid].append(' '.join(nltk.word_tokenize(annot)))
            elif 'spp' in annot_t and annot_t.index('spp')==1:
                sing_obj_annot_wh[pid].append(' '.join(nltk.word_tokenize(annot)))
            elif 'opp' in annot_t and annot_t.index('opp')==1:
                sing_obj_annot_wh[pid].append(' '.join(nltk.word_tokenize(annot)))

    if len(sing_sub_annot_wh[pid]) == 0:
        sing_sub_annot_wh.pop(pid,None)

    if len(sing_obj_annot_wh[pid]) == 0:
        sing_obj_annot_wh.pop(pid,None)

    if len(sing_sub_annot[pid]) == 0:
        sing_sub_annot_wh.pop(pid,None)

    if len(sing_obj_annot[pid]) == 0:
        sing_obj_annot_wh.pop(pid,None)

print 'len(sing_sub_annot_wh) = %d' % len(sing_sub_annot_wh)
print 'len(sing_obj_annot_wh) = %d' % len(sing_obj_annot_wh)
print 'len(sing_sub_annot) = %d' % len(sing_sub_annot)
print 'len(sing_obj_annot) = %d' % len(sing_obj_annot)

with open('sing_sub_annot_wh.json','w') as f1:
    json.dump(sing_sub_annot_wh, f1, indent=1)

with open('sing_obj_annot_wh.json','w') as f1:
    json.dump(sing_obj_annot_wh, f1, indent=1)

with open('sing_sub_annot.json','w') as f1:
    json.dump(sing_sub_annot, f1, indent=1)

with open('sing_obj_annot.json','w') as f1:
    json.dump(sing_obj_annot, f1, indent=1)



