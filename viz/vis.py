from flask import Flask, jsonify, render_template, url_for, send_from_directory
import json
import sys
import os

app = Flask(__name__,template_folder='.', static_folder='/project/6000167/vardaan/wikidata_dataset/', static_url_path='/project/6000167/vardaan/wikidata_dataset/')

@app.route('/<path:filename>', methods=['GET','POST'])
def download_file(filename):
    dir = os.path.dirname(filename)
    filename = os.path.basename(filename)
    return send_from_directory(dir, filename, as_attachment=True) 	



@app.route('/api/dialogue_qa/<dir>/<filename>')
def load_json(dir, filename):
	json_data = json.dumps(json.load(open(os.path.join('/project/6000167/vardaan/wikidata_dataset/'+dir, filename))))
	return render_template('vis.html',dialogues=json.loads(json_data))

if __name__=="__main__":
  	app.run(host='0.0.0.0', port=int(sys.argv[1]), debug=True)
