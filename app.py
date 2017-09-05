import re
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap

from flask_mail import Mail, Message

from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, TextField, PasswordField, validators, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

from config import *

from models import Article, Oligo, Gene, ContactForm, SuggestForm

#app = Flask(__name__, static_folder=ASSETS_FOLDER, template_folder=TEMPLATE_FOLDER)
app = Flask(__name__, static_folder=ASSETS_FOLDER, template_folder=TEMPLATE_FOLDER)

app.secret_key = SECRET_KEY

app.config.from_object('config')

Bootstrap(app)

mail = Mail(app)

data = PyMongo(app, config_prefix='MONGO')
articles = Article(mongo=data)
oligos = Oligo(mongo=data)
genes = Gene(mongo=data)

@app.route('/', methods=['GET','POST'])
def index():

	if request.method == 'POST':
		term = request.form['search'].strip()

		return redirect(url_for('search_oligos_show', query_str=term))

	return render_template("index.html")

@app.route('/oligos/search_oligo/<query_str>', methods=['GET',"POST"])
def search_oligos_show(query_str):

	if request.method == 'POST':
		term = request.form['search'].strip()

		return redirect(url_for('search_oligos_show', query_str=term))

	matches = genes.search_genes(query_str)

	oligos_of_matches = []

	for gene in matches:
		match_dict = {}

		match_dict['gene'] = genes.get_gene(gene)

		match_dict['match_oligos'] = oligos.get_oligos_by_gene(gene)

		oligos_of_matches.append(match_dict)

	return render_template("search_oligos_show.html", searches=oligos_of_matches)


@app.route('/oligos', methods=['GET'])
def oligoes_index():
	#item = {'name': , 'title': }
	#return "RNAi sequences..."
	return oligos.oligos_index()

@app.route('/oligos/<gene_symbol>', methods=['GET',"POST"])
def oligos_of_gene_show(gene_symbol):

	if request.method == 'POST':
		term = request.form['search'].strip()

		return redirect(url_for('search_oligos_show', query_str=term))

	gene = gene_symbol.upper()
	oligos_of_gene = oligos.get_oligos_by_gene(gene)

	info_of_gene = genes.get_gene(gene)

	return render_template("oligos_show.html", oligos=oligos_of_gene, gene_info=info_of_gene)

@app.route('/oligo/<oligo_id>', methods=['GET',"POST"])
def oligo_of_id_show(oligo_id):

	if request.method == 'POST':
		term = request.form['search'].strip()

		return redirect(url_for('search_oligos_show', query_str=term))

	oligo_of_id = oligos.get_oligo_by_id(oligo_id)

	article_ids = oligo_of_id['cite_list']

	article_list = []

	for article_id in article_ids:
		article = articles.get_article_by_id(article_id)
		article_list.append(article)

	return render_template("oligo_show.html", oligo=oligo_of_id, article_list=article_list)

# Fetch articles
@app.route("/articles", methods=["GET"])
def articles_index():
    return articles.articles_index()

# Show articles
@app.route("/articles/<article_id>", methods=["GET","POST"])
def get_article(article_id):
	articleId = long(article_id)
	article_data = articles.get_article_by_id(articleId)

	if request.method == 'POST':
		term = request.form['search'].strip()

		return redirect(url_for('search_oligos_show', query_str=term))

	return render_template('article_show.html', article=article_data)

@app.route('/contact', methods=['GET', 'POST'])
def contact():

	sendout = False
	email_valid = True
	texts_valid = True

	if request.method == 'POST':

		EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

		name = request.form['name'].strip()
		email = request.form['email'].strip()
		texts = request.form['texts'].strip()

		if not EMAIL_REGEX.match(email):
			email_valid = False

		if len(texts) < 10:
			texts_valid =False

		if not (email_valid and texts_valid):
			return render_template('contact.html', sendout=sendout, email_valid=email_valid, texts_valid=texts_valid)

		else:
			contents = ""
			contents += "From: " + name + "\n"
			contents += "Email: " + email + "\n"
			contents += "Message: " + texts

			msg = Message('Message from Actug', sender = 'actug2017@gmail.com', recipients = ['xunhao.xiong@gmail.com'])
			msg.body = contents

			mail.send(msg)

			sendout = True

			return render_template('contact.html', sendout=sendout, email_valid=email_valid, texts_valid=texts_valid)

	return render_template('contact.html', sendout=sendout, email_valid=email_valid, texts_valid=texts_valid)

@app.route('/suggest', methods=['GET','POST'])
def suggest():

	sendout = False
	input_val = True

	if request.method == 'POST':
		name = request.form['name'].strip()
		email = request.form['email'].strip()
		gene = request.form['gene'].strip()
		sequence = request.form['sequence'].strip()
		accession = request.form['accession'].strip()
		rnai = request.form['rnai_type']
		pubid = request.form['pubid'].strip()
		fulltext = request.form['link'].strip()

		if len(gene) < 2 or len(sequence) < 15 or len(pubid) < 3:
			input_val = False

			return render_template('suggest_sequence.html', sendout=sendout, input_val=input_val)

		else:
			contents = ""
			contents += "Name: " + name + "\n"
			contents += "From: " + email + "\n"
			contents += "Gene: " + gene + "\n"
			contents += "Sequence: " + sequence + "\n"
			contents += "Accession No.: " + accession + "\n"
			contents += "RNAi type: " + rnai + "\n"
			contents += "PMID: " + pubid + "\n"
			contents += "Link: " + fulltext + "\n"

			msg = Message('Suggestion from Actug', sender = 'actug2017@gmail.com', recipients = ['xunhao.xiong@gmail.com'])
			msg.body = contents

			mail.send(msg)

			sendout = True

			return render_template('suggest_sequence.html', sendout=sendout, input_val=input_val)

	return render_template('suggest_sequence.html', sendout=sendout, input_val=input_val)

@app.route("/sendemail")
def email():
   msg = Message('Hello', sender = 'sender@gmail.com', recipients = ['recipient@gmail.com'])
   msg.body = "This is the email body"
   mail.send(msg)
   return "Sent"

if __name__ == "__main__":
	app.run(port=3000, debug=True)

"""
@app.route('/api', methods=["GET"])
def api():
    return "Welcome to our API!"
"""
