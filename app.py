from flask import Flask, request, Response, render_template
import requests
import itertools
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Regexp, Optional
import re
from os import environ

class WordForm(FlaskForm):
    word_length = SelectField("Length", choices=[(-1, ''), (3, '3'),(4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10')], validators=[Optional()], coerce=int)
    avail_letters = StringField("Letters", validators= [
        Regexp(r'^[a-z]+$', message="Input string must contain letters only"), Optional()
    ])
    letters_pattern = StringField("Pattern", validators= [
        Regexp(r'^[a-z_.]+$', message="Pattern must contain letters and/or dots ('.') only"), Optional()
    ])
    submit = SubmitField("Go")


csrf = CSRFProtect()
app = Flask(__name__)
app.config["SECRET_KEY"] = "row"
csrf.init_app(app)

@app.route('/index')
@app.route('/')
def index():
    form = WordForm()
    return render_template("index.html", form=form)


@app.route('/words', methods=['POST','GET'])
def letters_2_words():

    form = WordForm()
    if form.validate_on_submit():
        letters = str(form.avail_letters.data)
        pattern = str(form.letters_pattern.data)
        length = int(form.word_length.data)

        # if letters was not set and pattern was not set, OR letters was not set, OR pattern was not set
        if ((letters == "" and pattern == "")):
            return render_template("index.html", form=form)
        elif (length > 0 and pattern != "" ): 
            if (len(pattern) != length):
                return render_template("index.html", form=form)

    else:
        return render_template("index.html", form=form)

    with open('sowpods.txt') as f:
        good_words = set(x.strip().lower() for x in f.readlines())

    word_set = set()
    # if length was set, then use the letters var
    if length > 0:
        # check if letters was set, if so, find permutations of word
        if letters != "":
            for l in range(3,length+1):
                for word in itertools.permutations(letters,l):
                    w = "".join(word)
                    if w in good_words:
                        word_set.add(w)
    else:
        # check if letters was set, if so, find permutations of word
        if letters != "":
            for l in range(3, 11):
                for word in itertools.permutations(letters, l):
                    w = "".join(word)
                    if w in good_words:
                        word_set.add(w)
    
    # if pattern is set, use this as a grep to filter all satisfying strings out of good_words
    if pattern != "":
        # use regexp to get all words in good_words that satisfy pattern var's regex... make sure to check if in set already
        regex = re.compile(pattern)
        patternSatisfiedList = list(filter(regex.match, good_words))

        for word in patternSatisfiedList:
            if word not in word_set:
                if len(word) <= length:
                    word_set.add(word)

    return render_template('wordlist.html',
        wordlist=sorted(word_set, key = key_sort), apiKey=environ.get('API_KEY', None),
        name="CS4131")

# create customized sort to sort based on length first, then alphabetically
def key_sort(str):
    return len(str), str.lower()




@app.route('/proxy')
def proxy():
    result = requests.get(request.args['url'])
    resp = Response(result.text)
    resp.headers['Content-Type'] = 'application/json'
    return resp




