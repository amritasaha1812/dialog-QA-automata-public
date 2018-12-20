import sys

low = int(sys.argv[1])
n = int(sys.argv[2])
out_file = sys.argv[3]

f1 = open(out_file,'w')

for i in range(low, low + n):
	f1.write('sbatch --time=8:00:00 --mem=80000M --output=logs/QA_%d.log automata.py --save_dir_id %d --update_counter True --sync_counter True --mode test --entity_thresh 10 --triple_thresh 5\n' %(i,i))

f1.close()

