# dialog-QA-automata
Code which simulates the automata for creating dialogues based on wikidata

## Post-proc steps
1. Run repair-scripts/automata_indir_repair.py 
2. Run post-proc/filter_json_field2.py (for parellelism, final_dataset/filter_json_field2_set.py could be used alternatively

Errata:
automata_simple_ques.py is no longer maintained. Therefore, don't use it.

## How to run this code

### Step 1 (create necessary directory structure) 
```
mkdir test/
mkdir train/
mkdir regex_save_dir/
cp counter_pickle/* test/
```

### Step 2 (create hard test)
```
python automata.py --save_dir_id SAVE_DIR_ID --update_counter True --sync_counter True --mode test --entity_thresh 10 --triple_thresh 5 --out_dir test/
```
Here, `SAVE_DIR_ID` is an integer for identifying the directory containing dialog JSONs generated by a single job. In practice, we run multiple such commmands in parallel (e.g. SAVE_DIR_ID=1-30)

### Step 3 (dump regex from hard test: to ensure strict test-train separation of triples)
```
python dump_regex_ques_wise.py test/ regex_save_dir/
```

### Step 4 (create train + val + easy_test)

```
python automata.py --save_dir_id SAVE_DIR_ID --update_counter True --sync_counter True --mode train --entity_thresh 150 --triple_thresh 50 --use_regex --regex_dir regex_save_dir/ --out_dir train/
```
Here, `SAVE_DIR_ID` is an integer for identifying the directory containing dialog JSONs generated by a single job. In practice, we run multiple such commmands in parallel (e.g. SAVE_DIR_ID=1-100)

### Step 5:
split train set generated in Step 4 into (train+val+easy_test) in desired ratio.
