# -*- coding: utf-8 -*-


from flask.ext.markdown import Markdown
from flask import Flask, render_template


app = Flask(__name__)
md = Markdown(app, extensions=['headerid'], output_format='html5')


@app.route('/')
def index():
    return render_template('index.html')
