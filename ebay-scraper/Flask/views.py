from flask import Blueprint, render_template, request    
import subprocess
import os

views = Blueprint(__name__, "views")
@views.route("/")
def home():
    return render_template("index.html")

@views.route('/process_form', methods=['POST'])
def process_form():
    # Logic to run when the form is submitted
    # This function will run when the button is pressed
    # For example, you can add code here to perform some action
    textbox_input = request.form['textbox_input']
    textbox_input2 = request.form['textbox_input2']
    run_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../run.py'))
    print("Button pressed!")
    subprocess.call(['python', run_script_path, textbox_input, textbox_input2])
    return 'Form processed successfully!'

@views.route('/readme', methods=['POST', 'GET'])
def readme():
    # Assuming the readme file is in the same directory as this script
    content = """
    This is the README for the Product Scraper application.
    Developed by Mohammed Ayesh.
    """
    return render_template('readme.html', content=content)