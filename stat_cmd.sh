# Find relation stats
find . -name *.json -exec grep -A1 'relation' {} \;  | grep -v 'utterance' | grep '"P' | sed 's/"//g' | sed  's/,//g' | sed 's/ //g' | sed 's/^[ \t]*//g' | sort | uniq -c | wc -l 

ls * | grep json | wc -l

# find count of all json files in a dir
find . -name *.json | wc -l
