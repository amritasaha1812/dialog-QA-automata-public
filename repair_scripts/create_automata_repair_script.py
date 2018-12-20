import sys, os

input_dir = sys.argv[1] # /scatch/vardaan/final_dataset_filt_untrim/train/
output_dir = sys.argv[2] # /scatch/vardaan/final_dataset_filt_untrim_repair/train/
start_idx = int(sys.argv[3])
end_idx = int(sys.argv[4])
out_file = sys.argv[5]

interval = 7

f1 = open(out_file,'w')

for i in range(start_idx, end_idx, interval):
	f1.write('sbatch --time=11:59:00 --mem=60000M --output=logs/QA_%d-%d.log automata_repair_dirset.py --input_dir %s --output_dir %s --low %d --high %d\n' % (i, (i+interval), input_dir, output_dir, i, (i+interval)))

f1.close()

