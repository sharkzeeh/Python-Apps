from flask import Flask
from flask import render_template
from flask import request
from logic import InstaLoad

app = Flask(__name__, static_folder="static")

@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form['InstaURL']
        image, sidecar, video = InstaLoad(url).download_content()
        return render_template('home.html', image=image, sidecar=sidecar, video=video)
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html')