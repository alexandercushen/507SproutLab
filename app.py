from flask import Flask, render_template, url_for, redirect
import json
import os
import subprocess
from flask_apscheduler import APScheduler
import time
from datetime import datetime, timedelta
import csv
import pandas as pd
import plotly.express as px
import plotly.offline as opy
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import glob
from PIL import Image

app = Flask(__name__)
scheduler = APScheduler()

COMMENTS_FILE = os.path.join('data', 'comments.json')

# --- FUNCTIONS ---
'''
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
'''

def get_homepage_image_time():
    
    meta_path = os.path.join('static', 'homepage_metadata.json')
    
    if os.path.exists(meta_path):
        
        with open(meta_path, 'r') as f:
            data = json.load(f)
            mtime =  data.get('homepage_jpg_mtime')
            
        # Convert Unix timestamp to a datetime object
        dt_obj = datetime.fromtimestamp(mtime)
        # Format it: e.g., "Feb 21, 10:30 PM"
        return dt_obj.strftime('%b %d, %I:%M %p')
            
    return "No homepage.jpg time data found"

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

def generate_gif(n_days=7):
    image_dir = os.path.join(os.path.dirname(__file__), "data/images")
    output_path = os.path.join(os.path.dirname(__file__), "static/timelapse.gif")

    cutoff = datetime.now() - timedelta(days=n_days)

    image_paths = sorted(glob.glob(os.path.join(image_dir, "img_*.jpg")))

    # Filter by parsing the date from the filename
    filtered_paths = []
    for path in image_paths:
        filename = os.path.basename(path)
        try:
            dt = datetime.strptime(filename, "img_%Y%m%d_%H%M%S.jpg")
            if dt >= cutoff:
                filtered_paths.append(path)
        except ValueError:
            continue

    if not filtered_paths:
        return

    frames = [Image.open(p) for p in filtered_paths]
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0
    )

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
    timestamp = os.path.getmtime('static/homepage.jpg')
    metadata = {"homepage_jpg_mtime": timestamp}
    with open('static/homepage_metadata.json', 'w') as f:
        json.dump(metadata, f)
    
    # 4. Check Homepage Image is Lit 
    print("Checking homepage image")
    subprocess.run(['python3','analysis_control.py'])

    # 5. Compile a gif (once a day, of the last week)
    if now.hour == 0 and now.minute < 10:
        print("Step 5: Generating GIF...")
        generate_gif(n_days=3)

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
    csv_path = 'data/temp_humi_log.csv'
    try:
        df = pd.read_csv(csv_path)
        df['dt'] = pd.to_datetime(df['Unix'], unit='s', utc=True).dt.tz_convert('America/New_York')

        # 1. Create a figure with a secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # 2. Add Temperature to the Left Axis (Primary)
        fig.add_trace(
            go.Scatter(x=df['dt'], y=df['Temp'], name="Temp (°C)", line=dict(color="red")),
            secondary_y=False,
        )

        # 3. Add Humidity to the Right Axis (Secondary)
        fig.add_trace(
            go.Scatter(x=df['dt'], y=df['Humidity'], name="Humidity (%)", line=dict(color="blue")),
            secondary_y=True,
        )

        # 4. Label your axes
        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="<b>Temperature</b> (°C)", color="red", secondary_y=False)
        fig.update_yaxes(title_text="<b>Humidity</b> (%)", color="blue", secondary_y=True)
        
        fig.update_layout(title_text="SproutLab Conditions", hovermode="x unified")

        plot_div = opy.plot(fig, auto_open=False, output_type='div')
    except Exception as e:
        plot_div = f"<p>Error: {e}</p>"

    return render_template('analysis.html', plot_div=plot_div)

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
        
    # Save the image timestamp to the static metadata file
    timestamp = os.path.getmtime('static/homepage.jpg')
    metadata = {"homepage_jpg_mtime": timestamp}
    with open('static/homepage_metadata.json', 'w') as f:
        json.dump(metadata, f)
   
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

