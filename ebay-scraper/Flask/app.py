from flask import Flask, render_template, request
import subprocess
import os
import pandas as pd
from finresult import printresponse
app = Flask(__name__)

@app.route('/',  methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/process_form', methods=['POST'])
def process_form():
    product = request.form['product']
    min_price = request.form['min_price']   
    parent_dir = os.path.dirname(os.path.abspath(__file__))  # Get the parent directory of caller.py
    other_program_path = os.path.join(parent_dir, "..", "run.py")  # Go up one level and then down to other_program.py
    subprocess.run(["python", other_program_path, product, min_price])
    Str = printresponse()
    print(Str)
    N = 30
    
    # print the string
    
    # get length of string
    length = len(Str)
    
    # create a new string of last N characters
    Str2 = Str[length - N:]
    
    # print Last N characters
    print(Str2)
    indices = list(map(int, Str2.split(', ')))

    data = search_data_by_indices(load_excel_file(), indices)
    return render_template('results.html', data=data)
@app.route('/readme', methods=['POST', 'GET'])
def readme():
    
    return render_template('readme.html')
def load_excel_file():
    # Update the path to your Excel file
    file_path = os.path.join(os.path.dirname(__file__), '../', 'results', 'ebay_data.xlsx')
    df = pd.read_excel(file_path)
    return df

def search_data_by_indices(df, indices):
    filtered_df = df.iloc[indices]
    filtered_df.reset_index(inplace=True)
    return filtered_df.to_dict(orient='records')

if __name__ == '__main__':
    app.run(debug=True)
