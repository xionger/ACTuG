from flask import request, Response
import pymongo
import re
#from pymongo.objectid import ObjectId
from bson import json_util, ObjectId
from bson.objectid import ObjectId

from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, TextField, PasswordField, validators, StringField, SubmitField, TextAreaField
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
				'oligos': article['rnais'],
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

	def get_article_by_id(self, article_id):
		article = self.mongo.db.articles.find_one_or_404({'pubid': article_id})
		article_data = {}

		article_data['title'] = article['title']
		article_data['journal'] = article['journal']
		article_data['pubid'] = article['pubid']
		article_data['year'] = article['year']
		article_data['oligos'] = article['rnais']
		article_data['authors'] = format_author(article['authors'])
		article_data['link'] = format_link(article['pubid'])

		return article_data


class Oligo:

	def __init__(self, mongo=None):
		self.mongo = mongo

	def oligos_index(self):
		limit = 100000
		oligos = self.mongo.db.oligos.find().limit(limit)
		oligos_data = []

		for oligo in oligos:
			#print "str(oligo['_id'])", oligo['_id']
			oligos_data.append({
				'id': str(oligo['_id']),
				'gene': oligo['gene'],
				'sequence': oligo['sequence'],
				'type': oligo['type'],
				'species': oligo['species'],
				'cite_by': oligo['cite_by'],
				'accessionId': oligo['accessionId']
				})

		return Response(
			json_util.dumps({
				'data': oligos_data,
				'count': oligos.count(),
				'limit': limit
				}),
			status=200,
			mimetype='application/json')

	def get_oligos_by_gene(self, gene):
		oligos = self.mongo.db.oligos.find({'gene': gene}).limit(1000)
		#oligos_data = format_oligos(oligos)

		#return oligos_data

		new_oligos = []

		for oligo in oligos:
			new_oligo = {}

			new_oligo['id'] = oligo['_id']
			new_oligo['gene'] = oligo['gene']
			#new_oligo['accessionId'] = format_list_to_str(oligo, 'accessionId')

			if len(oligo['accessionId']) >= 1 and len(oligo['accessionId'][0]) == 1:
				new_oligo['accessionId'] = oligo['accessionId']
			else:
				new_oligo['accessionId'] = format_list_to_str(oligo, 'accessionId')

			new_oligo['type'] = format_list_to_str(oligo, 'type')
			new_oligo['species'] = format_list_to_str(oligo, 'species')
			new_oligo['sequence'] = format_sequence(oligo)
			new_oligo['cite_list'] = oligo['cite_by']
			new_oligo['cites'] = len(oligo['cite_by'])

			new_oligos.append(new_oligo)

		sorted_list = sorted(new_oligos, key=lambda k: k['cites'], reverse=True)

		return sorted_list

	def get_oligo_by_id(self, oligo_id):
		oligo = self.mongo.db.oligos.find_one_or_404({'_id': ObjectId(oligo_id)})

		oligo_data = {}

		oligo_data['id'] = oligo['_id']
		oligo_data['gene'] = oligo['gene']
		#oligo_data['accessionId'] = format_list_to_str(oligo, 'accessionId')

		if len(oligo['accessionId']) >= 1 and len(oligo['accessionId'][0]) == 1:
			new_oligo['accessionId'] = oligo['accessionId']
		else:
			new_oligo['accessionId'] = format_list_to_str(oligo, 'accessionId')

		oligo_data['type'] = format_list_to_str(oligo, 'type')
		oligo_data['species'] = format_list_to_str(oligo, 'species')
		oligo_data['sequence'] = format_sequence(oligo)
		oligo_data['cite_list'] = oligo['cite_by']
		oligo_data['cites'] = len(oligo['cite_by'])

		return oligo_data

class Gene:
	def __init__(self, mongo=None):
		self.mongo = mongo

	def get_genes(self):
		limit = 100000
		genes = self.mongo.db.genes.find().limit(limit)
		genes_data = []

		for gene in genes:
			genes_data.append({
				'symbol': gene['symbol'],
				'name': gene['name'],
				'description': gene['description']
				})

		return Response(
			json_util.dumps({
				'data': genes_data,
				'count': genes.count(),
				'limit': limit
				}),
			status=200,
			mimetype='application/json')

	def get_gene(self, gene_symbol):
		gene = self.mongo.db.genes.find_one_or_404({'symbol': gene_symbol})
		gene_data = {}

		names_str =""

		if len(gene['name']) >= 1:
			for i in range(len(gene['name'])):
				if i < len(gene['name']) - 1:
					names_str += gene['name'][i] + ", "

				else:
					names_str += gene['name'][i]

			names_str = " (" + names_str + ")"

		gene_data['symbol'] = gene['symbol']
		gene_data['names_str'] = names_str
		gene_data['description'] = gene['description']

		return gene_data

	def search_genes(self, query_str):
		limit = 10000
		genes = self.mongo.db.genes.find().limit(limit)

		q = query_str.upper()

		priory_gene = []
		priory_name = []
		priory_desc = []

		for gene in genes:
			symbol = gene['symbol'].upper()

			name_list = gene['name']
			name = []

			for n in name_list:
				name.append(n.upper())

			desc = gene['description'].upper()
			desc = desc.replace("\-", " ")
			desc = " ".join(re.findall("[A-Z0-9]+", desc))
			desc_list = desc.split()

			if q == symbol:
				priory_gene.append(symbol)

			elif q in name:
				priory_name.append(symbol)

			elif q in desc_list:
				priory_desc.append(symbol)

		results = priory_gene + priory_name + priory_desc

		return results

class ContactForm(FlaskForm):
	name = TextField("Name")
	email = TextField("E-Mail",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
	comment = TextAreaField("Message",  [validators.Required("Please enter a message.")])
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
	return "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC" + str(pubid)

def format_oligos(oligos):

	new_oligos = []

	for oligo in oligos:
		new_oligo = {}

		new_oligo['gene'] = oligo['gene']

		if len(oligo['accessionId']) >= 1:
			if len(oligo['accessionId'][0]) == 1:
				new_oligo['accessionId'] = oligo['accessionId']
		else:
			new_oligo['accessionId'] = format_list_to_str(oligo, 'accessionId')

		new_oligo['type'] = format_list_to_str(oligo, 'type')
		new_oligo['species'] = format_list_to_str(oligo, 'species')

		new_oligo['sequence'] = format_sequence(oligo)

		new_oligo['cite_list'] = oligo['cite_by']

		new_oligo['cites'] = len(oligo['cite_by'])

		new_oligos.append(new_oligo)

	sorted_list = sorted(new_oligos, key=lambda k: k['cites'], reverse=True)

	return sorted_list

def format_list_to_str(obj, idx_str):
	new_str = ""

	if len(obj[idx_str]) >= 1:
		for i in range(len(obj[idx_str])):
			if i < len(obj[idx_str]) - 1:
				new_str += obj[idx_str][i] + ", "

			else:
				new_str += obj[idx_str][i]

	return new_str

def format_sequence(obj):
	new_seq = obj['sequence']

	if len(obj['sequence']) > 40:
		half = len(obj['sequence'])/2

		left = obj['sequence'][0 : half]
		right = obj['sequence'][half :]

		new_seq = left + " " + right

	return new_seq
