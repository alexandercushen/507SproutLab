from flask import Flask, render_template, url_for, redirect
import json
import os
import subprocess
from flask_apscheduler import APScheduler
import time
from datetime import datetime
import csv

app = Flask(__name__)
scheduler = APScheduler()

COMMENTS_FILE = os.path.join('data', 'comments.json')

# --- FUNCTIONS ---

def get_homepage_image_time():
    path = os.path.join('static', 'homepage.jpg')
    
    if os.path.exists(path):
        # Get the time the file was last updated/written
        mtime = os.path.getmtime(path)
        # Convert Unix timestamp to a datetime object
        dt_obj = datetime.fromtimestamp(mtime)
        # Format it: e.g., "Feb 21, 10:30 PM"
        return dt_obj.strftime('%b %d, %I:%M %p')
    
    return "No image found"

def get_latest_temp_humi_reading():
    log_path = os.path.join('data', 'temp_humi_log.csv')
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            reader = list(csv.DictReader(f))
            if reader:
                return reader[-1] # Returns the last row as a dictionary
    return None

def get_comments():
    if os.path.exists(COMMENTS_FILE):
        with open(COMMENTS_FILE, 'r') as f:
            return json.load(f)
    return []

# --- PERIODIC TASKS ---

@scheduler.task('cron', id='do_everything', minute='0,30')
def scheduled_job():

    print(f"--- Task Started at {datetime.now().strftime('%H:%M:%S')} ---")

    # 1. Take Sensor Reading
    print("Step 1: Sensor Reading...")
    script_sensor = os.path.join(os.getcwd(), 'scripts', 'record_temperature_humidity.py')
    subprocess.run(['python3', script_sensor], stderr=subprocess.DEVNULL) # Supress output, there is a persistant "unable to set line 14 to input" message even when successful
    
    # 2. Wait 5 seconds for the GPIO bus to clear
    print("Step 2: GPIO bus sleep buffer...")
    time.sleep(2)
    
    # 3. Take Periodic Photo
    print("Step 3: Taking Photo...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"data/images/img_{timestamp}.jpg"
    script_photo = os.path.join(os.getcwd(), 'scripts', 'take_still.py')
    subprocess.run(['python3', script_photo, filename])
    subprocess.run(['cp', filename, 'static/homepage.jpg'])

    print(f"--- Task Finished at {datetime.now().strftime('%H:%M:%S')} ---")

# --- ROUTES ---

@app.route('/')
def homepage():
    img_time = get_homepage_image_time()
    latest = get_latest_temp_humi_reading()
    comments = get_comments()
    return render_template('homepage.html', image_time=img_time, latest=latest, comments=comments)

@app.route('/plant_log')
def plant_log():
    json_path = os.path.join('data', 'sowing_history.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        sowing_data = json.load(f)  # This should be a list of dicts
    return render_template('plant_log.html', sowing_data=sowing_data)

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/post-comment', methods=['POST'])
def post_comment():
    from flask import request
    name = request.form.get('name', 'Anonymous')
    text = request.form.get('comment', '').strip()

    if text:
        comments = get_comments()
        # Create the new comment entry
        new_comment = {
            "name": name if name else "Anonymous",
            "text": text,
            "time": datetime.now().strftime("%b %d, %I:%M %p")
        }
        # Add to the start of the list so newest is at the top
        comments.insert(0, new_comment)
        
        with open(COMMENTS_FILE, 'w') as f:
            json.dump(comments, f, indent=4)
            
    return redirect(url_for('homepage'))

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
   
    # Also save this image to data/images
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"data/images/img_{timestamp}.jpg"
    
    subprocess.run(['cp', 'static/homepage.jpg', filename], check=True)
 
    return redirect(url_for('homepage'))

if __name__ == "__main__":
    scheduler.init_app(app)
    scheduler.start()

    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    #app.run(host='0.0.0.0', port=5000, debug=True)

