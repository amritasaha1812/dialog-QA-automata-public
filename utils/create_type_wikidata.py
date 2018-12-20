# from load_wikidata2 import *
import logging

wikidata_type_dict = {}

count = 0


for QID in child_par_dict:
	count += 1

	if count % 100000 == 0:
		print count
	if QID not in item_data:
		continue
		
	for pid in [p for p in wikidata[QID] if p in prop_data]:
		for qid in [q for q in wikidata[QID][pid] if q in child_par_dict]:
			if child_par_dict[QID] not in wikidata_type_dict:
				wikidata_type_dict[child_par_dict[QID]] = {pid:[child_par_dict[qid]]}
			else:
				if pid not in wikidata_type_dict[child_par_dict[QID]]:
					wikidata_type_dict[child_par_dict[QID]][pid] = [child_par_dict[qid]]
				else:
					if child_par_dict[qid] not in wikidata_type_dict[child_par_dict[QID]][pid]:
						wikidata_type_dict[child_par_dict[QID]][pid].append(child_par_dict[qid])
			try:
				assert child_par_dict[QID] in wikidata_type_dict and pid in wikidata_type_dict[child_par_dict[QID]] and child_par_dict[qid] in wikidata_type_dict[child_par_dict[QID]][pid]
			except:
				logging.exception('Something aweful happened')
				print 'QID = %s pid = %s qid = %s' % (QID,pid,qid)

print 'len(wikidata_type_dict) = %d' % len(wikidata_type_dict)


json_dump1 = json.dumps(wikidata_type_dict,indent=4)

f1 = open('wikidata_type_dict.json', 'w')

print >> f1, json_dump1

f1.close()