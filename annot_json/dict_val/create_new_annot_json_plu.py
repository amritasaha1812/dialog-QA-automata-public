import sys, os, json, pickle, fnmatch, logging, nltk
from xlrd import open_workbook

wb = open_workbook('../new_templates_plural.xlsx')

sheet = wb.sheets()[0]

plu_sub_annot_wh = {}
plu_obj_annot_wh = {}

plu_sub_annot = {}
plu_obj_annot = {}

rows = []
for row in range(1, sheet.nrows):
    pid = sheet.cell(row,0).value
    # print pid
    plu_sub_annot_wh[pid] = []
    plu_obj_annot_wh[pid] = []
    plu_sub_annot[pid] = []
    plu_obj_annot[pid] = []

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
            plu_sub_annot[pid].append(' '.join(nltk.word_tokenize(annot)))

            if ('spps' not in annot_t) and ('opps' not in annot_t):
                plu_sub_annot_wh[pid].append(' '.join(nltk.word_tokenize(annot)))
            elif 'spps' in annot_t and annot_t.index('spps')==1:
                plu_sub_annot_wh[pid].append(' '.join(nltk.word_tokenize(annot)))
            elif 'opps' in annot_t and annot_t.index('opps')==1:
                plu_sub_annot_wh[pid].append(' '.join(nltk.word_tokenize(annot)))

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
            plu_obj_annot[pid].append(' '.join(nltk.word_tokenize(annot)))

            if ('spps' not in annot_t) and ('opps' not in annot_t):
                plu_obj_annot_wh[pid].append(' '.join(nltk.word_tokenize(annot)))
            elif 'spps' in annot_t and annot_t.index('spps')==1:
                plu_obj_annot_wh[pid].append(' '.join(nltk.word_tokenize(annot)))
            elif 'opps' in annot_t and annot_t.index('opps')==1:
                plu_obj_annot_wh[pid].append(' '.join(nltk.word_tokenize(annot)))

    if len(plu_sub_annot_wh[pid]) == 0:
        plu_sub_annot_wh.pop(pid,None)

    if len(plu_obj_annot_wh[pid]) == 0:
        plu_obj_annot_wh.pop(pid,None)

    if len(plu_sub_annot[pid]) == 0:
        plu_sub_annot_wh.pop(pid,None)

    if len(plu_obj_annot[pid]) == 0:
        plu_obj_annot_wh.pop(pid,None)

print 'len(plu_sub_annot_wh) = %d' % len(plu_sub_annot_wh)
print 'len(plu_obj_annot_wh) = %d' % len(plu_obj_annot_wh)
print 'len(plu_sub_annot) = %d' % len(plu_sub_annot)
print 'len(plu_obj_annot) = %d' % len(plu_obj_annot)

with open('plu_sub_annot_wh.json','w') as f1:
    json.dump(plu_sub_annot_wh, f1, indent=1)

with open('plu_obj_annot_wh.json','w') as f1:
    json.dump(plu_obj_annot_wh, f1, indent=1)

with open('plu_sub_annot.json','w') as f1:
    json.dump(plu_sub_annot, f1, indent=1)

with open('plu_obj_annot.json','w') as f1:
    json.dump(plu_obj_annot, f1, indent=1)



