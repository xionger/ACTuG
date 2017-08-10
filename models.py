from flask import request, Response
import pymongo
from bson import json_util, ObjectId

from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, validators, TextAreaField
from wtforms.validators import DataRequired

class Article:

	def __init__(self, mongo=None):
		self.mongo = mongo

	def articles_index(self):
		limit = 100000
		articles = self.mongo.db.articles.find().limit(limit)
		articles_data = []

		for article in articles:
			articles_data.append({
				'title': article['title'],
				'journal': article['journal'],
				'pubid': article['pubid'],
				'year': article['year'],
				'oligos': article['oligoes'],
				'authors': format_author(article['authors']),
				'link': format_link(article['pubid']),
				'abstract': article['abstract']
				})

		return Response(
			json_util.dumps({
				'data': articles_data,
				'count': articles.count(),
				'limit': limit
				}),
			status=200,
			mimetype='application/json')

	def article_show(self, article_id):
		article = self.mongo.db.articles.find_one_or_404({'pubid': article_id})
		article_data = []

		article_data.append({
			'title': article['title'],
			'journal': article['journal'],
			'pubid': article['pubid'],
			'year': article['year'],
			'oligos': article['oligoes'],
			'authors': format_author(article['authors']),
			'link': format_link(article['pubid'])
			})

		#article_data = json_util.dumps(article_data)

		return article_data 

		"""
		return Response(
			json_util.dumps(article_data),
			status=200,
			mimetype='application/json')
		"""

class Oligo:

	def __init__(self, mongo=None):
		self.mongo = mongo

	def oligos_index(self):
		limit = 100000
		oligos = self.mongo.db.rnaiseqs.find().limit(limit)
		oligos_data = []

		for oligo in oligos:
			oligos_data.append({
				'name': oligo['gene'],
				'detail': oligo['sequences']
				})

		return Response(
			json_util.dumps({
				'data': oligos_data,
				'count': oligos.count(),
				'limit': limit
				}),
			status=200,
			mimetype='application/json')

	def oligo_show(self, gene):
		oligo = self.mongo.db.rnaiseqs.find_one_or_404({'gene': gene})

		return oligo
		"""
		return Response(
			json_util.dumps(oligo),
			status=200,
			mimetype='application/json')
		"""

class ContactForm(FlaskForm):
	name = TextField("Name")
	email = TextField("E-Mail",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
	message = TextAreaField("Message",  [validators.Required("Please enter a message.")])
	submit = SubmitField("Send")

class SuggestForm(FlaskForm):
	name = TextField("Name")
	email = TextField("E-Mail")
	gene = TextField("Gene",  [validators.Required("Please enter the gene symbol.")])
	sequence = TextField("Sequence",  [validators.Required("Please enter the oligo's sequence.")])
	accession = TextField("Accession No.")
	rnai_type = TextField("RNAi Type")
	pubid = TextField("PMID",  [validators.Required("Please enter a Pubmed id.")])
	fulltext = TextField("Link")
	submit = SubmitField("Send")

def format_author(author_list):
	firs_name_words_of_first_author = author_list[0]['first-name'].split()
	first_name_abr = ''
	for word in firs_name_words_of_first_author:
		first_name_abr += word[0] + '.'

	first_author = author_list[0]['last-name'] + ', ' + first_name_abr

	if len(author_list) > 1:
		return first_author + ', et al.'
	elif len(author_list) == 1:
		return first_author
	else:
		return ''

def format_link(pubid):
	return "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC" + str(3953817)

"""
'accession': oligo['accessionId'],
'article_ids': oligo['articleId'],
'oligo_type': oligo['type'],
'species': oligo['species'],
'sequence':oligo['sequence']
"""