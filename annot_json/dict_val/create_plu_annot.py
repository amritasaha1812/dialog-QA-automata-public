import sys, os, json, pickle, fnmatch, logging, nltk

with open('../dict_val_old/plu_sub_annot_wh.json','r') as f1:
	plu_sub_annot_wh = json.load(f1)

with open('../dict_val_old/plu_obj_annot_wh.json','r') as f1:
	plu_obj_annot_wh = json.load(f1)

with open('../dict_val_old/neg_plu_sub_annot_wh.json','r') as f1:
	neg_plu_sub_annot_wh = json.load(f1)

with open('../dict_val_old/neg_plu_obj_annot_wh.json','r') as f1:
	neg_plu_obj_annot_wh = json.load(f1)

plu_sub_annot_wh_new = {}
plu_obj_annot_wh_new = {}
neg_plu_sub_annot_wh_new = {}
neg_plu_obj_annot_wh_new = {}

for pid in plu_sub_annot_wh:
	plu_sub_annot_wh_new[pid] = [plu_sub_annot_wh[pid][0]]

for pid in plu_obj_annot_wh:
	plu_obj_annot_wh_new[pid] = [plu_obj_annot_wh[pid][0]]

for pid in neg_plu_sub_annot_wh:
	neg_plu_sub_annot_wh_new[pid] = [neg_plu_sub_annot_wh[pid][0]]

for pid in neg_plu_obj_annot_wh:
	neg_plu_obj_annot_wh_new[pid] = [neg_plu_obj_annot_wh[pid][0]]

with open('plu_sub_annot_wh.json','w') as f1:
    json.dump(plu_sub_annot_wh_new, f1, indent=1)

with open('plu_obj_annot_wh.json','w') as f1:
    json.dump(plu_obj_annot_wh_new, f1, indent=1)

with open('neg_plu_sub_annot_wh.json','w') as f1:
    json.dump(neg_plu_sub_annot_wh_new, f1, indent=1)

with open('neg_plu_obj_annot_wh.json','w') as f1:
    json.dump(neg_plu_obj_annot_wh_new, f1, indent=1)
