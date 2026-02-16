from flask import Flask, render_template, url_for
import json
import os

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

