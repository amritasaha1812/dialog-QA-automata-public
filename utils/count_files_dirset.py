import codecs, random, pickle, json, math, logging, sys, os, resource, fcntl, collections
import argparse

parser = argparse.ArgumentParser(description='Hyper-parameter settings')
parser.add_argument('--input_dir', dest='input_dir', type=str, help='directory in which dialogs are to be verified', required=True)
parser.add_argument('--low',dest='low',type=int, help='lower index of QA')
parser.add_argument('--high',dest='high',type=int, help='higher index of QA')
args = parser.parse_args()
print(args)

count = 0

for dir_name in [('QA_%d' % i) for i in range(args.low, args.high) if os.path.isdir(os.path.join(args.input_dir, ('QA_%d' % i)))]:
	# print dir_name
	count += len(os.listdir(os.path.join(args.input_dir, dir_name)))

print count