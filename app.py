from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/plant_log')
def plant_log():
    return render_template('plant_log.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

'''
from flask import Flask, render_template, request

app = Flask(__name__)
data_log = []

@app.route('/')
def index():
    return render_template('index.html', log=data_log)

@app.route('/post-data')
def post_data():
    new_val = request.args.get('val', 'No data')
    data_log.append(new_val)
    return f"Data received: {new_val}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
'''
