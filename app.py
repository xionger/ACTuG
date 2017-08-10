from flask import Flask, render_template, url_for, request, flash
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap

from config import *

from models import Article, Oligo, ContactForm, SuggestForm

#app = Flask(__name__, static_folder=ASSETS_FOLDER, template_folder=TEMPLATE_FOLDER)
app = Flask(__name__, static_folder=ASSETS_FOLDER, template_folder=TEMPLATE_FOLDER)

app.secret_key = SECRET_KEY

app.config.from_object('config')

Bootstrap(app)

data = PyMongo(app, config_prefix='MONGO')
articles = Article(mongo=data)
oligos = Oligo(mongo=data)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/oligos', methods=['GET'])
def oligoes_index():
	#item = {'name': , 'title': }
	#return "RNAi sequences..."
	return oligos.oligos_index()

@app.route('/oligos/<gene_name>', methods=['GET'])
def oligo_show(gene_name):
	oligos_of_gene = oligos.oligo_show(gene=gene_name)
	return render_template("oligo_show.html", oligo=oligos_of_gene)

# Fetch articles
@app.route("/articles", methods=["GET"])
def articles_index():
    return articles.articles_index()

# Show articles
@app.route("/articles/<article_id>", methods=["GET"])
def article_show(article_id):
	articleId = long(article_id)
	article_data = articles.article_show(articleId)
	return render_template('article_show.html', article=article_data)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
	form = ContactForm()

	if request.method == 'POST':
		if form.validate() == False:
			flash('Please fille the required fields.')
			return render_template('contact.html', form=form)
		else:
			return 'Form posted.'

	elif request.method == 'GET':
		return render_template('contact.html', form=form)

@app.route('/suggest', methods=['GET', 'POST'])
def suggest():
	form = SuggestForm()

	if request.method == 'POST':
		return 'Form posted.'

	elif request.method == 'GET':
		return render_template('suggest_sequence.html', form=form)

if __name__ == "__main__":
	app.run(port=3000, debug=True)

"""
@app.route('/api', methods=["GET"])
def api():
    return "Welcome to our API!"
"""