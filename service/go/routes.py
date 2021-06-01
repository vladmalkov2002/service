from flask import render_template, redirect, url_for, request, flash
#from flask_login import login_user, login_required, logout_user
#from werkzeug.security import check_password_hash, generate_password_hash

from go import app, db
from go.models import Message


@app.route('/', methods=['GET'])
def st():
    return render_template('index.html')

@app.route('/hello', methods=['GET'])
def hello():
    return render_template('index.html')


@app.route('/go')
def test():
    return redirect("http://localhost:8080")



@app.route('/chat', methods=['GET'])
def chat():
    return render_template('main.html', messages=Message.query.all())


@app.route('/add_text', methods=['POST'])
def add_text():
    usertext = request.form['text']
    go = request.form['tag']
    db.session.add(Message(usertext, go))
    db.session.commit()
    return redirect(url_for('chat'))



