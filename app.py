import os
import shutil
import json
from flask_bootstrap import Bootstrap
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import subprocess
from predict_temp import chem_dis_func, drug2_func, gene_dis_func, return_result_ddi, return_result_gad, return_result_chemprot
from werkzeug.utils import redirect, secure_filename

UPLOAD_DIR = "./build/static/result/"
INPUT_DIR = "dl/User_input/ori_input"
app = Flask(__name__, static_folder='./build', static_url_path='/')
app.config['UPLOAD_DIR'] = UPLOAD_DIR
app.config['INPUT_DIR'] = INPUT_DIR
CORS(app)
Bootstrap(app)
file_path = "result/"
app.config['FLAG'] = 'not Ready'  
app.config['OUTPUT_DIR'] = 'static/result/'

@app.route('/')
def home():
    return app.send_static_file('index.html')

def predict_ddi(input_file):
    filename = input_file.split('.')[0]
    cmd = ["sh", "dl/predict_ddi.sh", "User_input/ori_input/"+input_file, filename]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         stdin=subprocess.PIPE)
    out, err = p.communicate()

def predict_chemprot(input_file):
    filename = input_file.split('.')[0]
    cmd = ["sh", "dl/predict_chemprot.sh", "User_input/ori_input/"+input_file, filename]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         stdin=subprocess.PIPE)
    out, err = p.communicate()
    
def predict_gad(input_file):
    filename = input_file.split('.')[0]+'.json'
    print("filename: "+filename)
    cmd = ["sh", "dl/predict_GAD.sh", "User_input/ori_input/"+input_file]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         stdin=subprocess.PIPE)
    out, err = p.communicate()

def model_performance_gad():
    with open('dl/model_result/gad_result.json') as json_file:
        json_data = json.load(json_file)
        model_performance = json_data['metrics']['PRF']
        f1 = model_performance.split('    ')[5]
    return str(f1)

def model_performance_chemprot():
    with open('dl/model_result/chemprot_result.json') as json_file:
        json_data = json.load(json_file)
        model_performance = json_data['metrics']['PRF']
        f1 = model_performance.split('    ')[5]
    return str(f1)

def model_performance_ddi():
    with open('dl/model_result/ddi_result.json') as json_file:
        json_data = json.load(json_file)
        model_performance = json_data['metrics']['PRF']
        f1 = model_performance.split('    ')[5]
    return str(f1)

def save_file(request):
    f = request.files['file']
    fname = secure_filename(f.filename)
    input_file_path = os.path.join(app.config['INPUT_DIR'], fname)
    f.save(input_file_path)

    return fname, input_file_path

@app.route('/api/chemical-disease', methods=['POST'])
def chemical_disease():
    fname, input_file_path = save_file(request)
    try:
        predict_chemprot(fname)
        output_file_name = "Chem_Dis_result_" + fname
        output_file_path = app.config['OUTPUT_DIR'] + output_file_name
        result = return_result_chemprot(input_file_path, output_file_path)  
        
        performance = model_performance_chemprot()
        data = {
            "result": result,
            "performance": performance,
            "file_path": output_file_path, 
            "file_name": output_file_name
        }

        return jsonify(data)
    except:
        return {"message": "An error eccurred inserting the item."}, 500 # Internal server error


@app.route('/api/drug-drug', methods=['POST'])
def drug_drug():
    fname, input_file_path = save_file(request)
    try:
        predict_ddi(fname)  
        output_file_name = "Drug_Drug_result_"+fname
        output_file_path = app.config['OUTPUT_DIR'] + output_file_name
        result = return_result_ddi(input_file_path, output_file_path)
        
        performance = model_performance_ddi()

        data = {
            "result": result,
            "performance": performance,
            "file_path": output_file_path, 
            "file_name": output_file_name
        }

        return jsonify(data)
    except:
        return {"message": "An error eccurred inserting the item."}, 500 # Internal server error

@app.route('/api/gene-disease', methods=['POST'])
def gene_disease():
    fname, input_file_path = save_file(request)
    try:
        predict_gad(fname)
        output_file_name = "Gene_Dis_result_"+fname
        output_file_path = app.config['OUTPUT_DIR'] + output_file_name
        result = return_result_gad(input_file_path, output_file_path)  
        
        performance = model_performance_gad()

        data = {
            "result": result,
            "performance": performance,
            "file_path": output_file_path, 
            "file_name": output_file_name
        }

        return jsonify(data)
    except:
        return {"message": "An error eccurred inserting the item."}, 500 # Internal server error


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
