from flask import Flask, render_template, url_for, redirect
import json
import os
import subprocess

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/plant_log')
def plant_log():
    json_path = os.path.join('data', 'sowing_history.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        sowing_data = json.load(f)  # This should be a list of dicts

    return render_template('plant_log.html', sowing_data=sowing_data)

@app.route('/take-photo')
def take_photo():
    # Construct the path to the script
    script_path = os.path.join(os.getcwd(), 'scripts', 'take_still.py')
    
    # Run the script: python3 scripts/take_still.py homepage.jpg
    # We use 'static/homepage.jpg' so the script saves it in the right place
    try:
        subprocess.run(['python3', script_path, 'static/homepage.jpg'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running script: {e}")
        
    return redirect(url_for('homepage'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

