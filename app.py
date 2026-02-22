from flask import Flask, render_template, url_for, redirect
import json
import os
import subprocess
from flask_apscheduler import APScheduler
import time
from datetime import datetime

app = Flask(__name__)
scheduler = APScheduler()

# --- PERIODIC TASKS ---

@scheduler.task('interval', id='do_everything', seconds=30)
def scheduled_job():

    print(f"--- Task Started at {datetime.now().strftime('%H:%M:%S')} ---")

    # 1. Take Sensor Reading
    print("Step 1: Sensor Reading...")
    script_sensor = os.path.join(os.getcwd(), 'scripts', 'record_temperature_humidity.py')
    subprocess.run(['python3', script_sensor], stderr=subprocess.DEVNULL) # Supress output, there is a persistant "unable to set line 14 to input" message even when successful
    
    # 2. Wait 5 seconds for the GPIO bus to clear
    print("Step 2: Buffer Sleep...")
    time.sleep(2)
    
    # 3. Take Periodic Photo
    print("Step 3: Taking Photo...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f"static/archive/still_{timestamp}.jpg"
    script_photo = os.path.join(os.getcwd(), 'scripts', 'take_still.py')
    subprocess.run(['python3', script_photo, filename])

    print(f"--- Task Finished at {datetime.now().strftime('%H:%M:%S')} ---")

# --- ROUTES ---

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
    scheduler.init_app(app)
    scheduler.start()

    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    #app.run(host='0.0.0.0', port=5000, debug=True)

