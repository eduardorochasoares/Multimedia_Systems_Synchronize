# -*- coding: utf-8 -*-
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import numpy as np
import  os, time
from sys import argv
from os.path import join, dirname
import glob
import re
from time import sleep
from PIL import Image # Importando o módulo Pillow para abrir a imagem no script
import pytesseract as ocr
from nltk import tokenize
from scipy.spatial.distance import cosine
from joblib import Parallel, delayed
import networkx as nx
import nltk
import multiprocessing
from sklearn.metrics.pairwise import cosine_similarity
import sys
import generate_ncl_application as g_ncl
import transfer_app
from sklearn.feature_extraction.text import HashingVectorizer
from scipy.spatial.distance import cosine, jaccard, correlation, canberra, euclidean, pdist, squareform, hamming


stemmer = nltk.stem.RSLPStemmer()

stopwordspt = nltk.corpus.stopwords.words('portuguese')
stopwordspt.append("aula")
stopwordspt.append("exemplo")
stopwordspt.append("curso")
stopwordspt.append("primeira")
stopwordspt.append("parte")
stopwordspt.append("início")
stopwordspt.append("terminando")
stopwordspt.append("próxima")
stopwordspt.append("introdução")


stopwordspt = [stemmer.stem(stopwords) for stopwords in stopwordspt]


'''Extract the text, through OCR, of each image of the database'''
def getSlidesKeyWords(slides_path):
	slides = []

	phrase = ocr.image_to_string(Image.open(slides_path), lang='por')
	words = tokenize.word_tokenize(phrase, language='portuguese')

	words=[word.lower() for word in words if word.isalpha() ]
	words=[stemmer.stem(word) for word in words ]
	slide_text = ' '.join(words)


	return slide_text

''' Get the pre-processed transcripts of each scene'''
def getTranscriptText(video_path, stem):
	scene_boundaries = []
	text = ''
	cenas=[]

	D = glob.glob(video_path+"[0-9]*")
	for x in  range(len(D)):
		l = D[x].split("/")
		#print(l[-1])
		D[x] = l[-1]

	D = [d for d in D if ".txt" not in d]
	D = [d for d in D if ".mp4" not in d]
	D = [d for d in D if ".sync" not in d]
	D = [d for d in D if ".index" not in d]
	tam = len(D)
	for x in range (0,tam):
		D[x] = int(D[x])
	D = sorted(D)
	for x in range (0,tam):
		D[x] = str(D[x])
	inicio_cena=[]


	tr=''
	for x in range(0 , tam):
		transcripts=[]
		text = ''
		tr = ''
		transcripts = glob.glob(video_path+D[x]+"/anotation*")

		for a in transcripts:
			tr += a
		auxiliar = re.findall("anotation\d\d*",tr)
		for b in range(0,len(auxiliar)):
			auxiliar[b] = int(auxiliar[b].replace("anotation",""))
		auxiliar = sorted(auxiliar)



		for tc in transcripts:
			text += open(tc,'r',encoding='utf-8').read()

		text = tokenize.word_tokenize(text, language='portuguese')
		if(stem):
			text = [stemmer.stem(token) for token in text]

		text = ' '.join(text)
		cenas.append(text)

		scene_boundaries.append(auxiliar)

	return cenas, scene_boundaries

'''Represents the texts from transcription and OCR in a bag-of-words model'''
'''Then a maximum bipartide graph match is done using the similarity between transcripts and texts from OCR'''
'''In the end, is generated a 1 to 1 relation between topics e images from the database'''
def matching(path, root_path_exec, stem):
	data_base_path = root_path_exec+'slides/'
	start_time = time.time()

	cenas, scene_boundaries = getTranscriptText(path, stem)
	slides_path = sorted(glob.glob(data_base_path+"*.png"))
	num_cores = multiprocessing.cpu_count()

	slides = Parallel(n_jobs=num_cores)(delayed(getSlidesKeyWords)(path)  for path in slides_path)


	cenas_size = len(cenas)
	slides_size = len(slides)
	texts = cenas + slides

	tfidf_vectorizer = TfidfVectorizer(stop_words = stopwordspt, ngram_range=(1,3), norm="l2", min_df = 3,
	sublinear_tf = True)

	tf = tfidf_vectorizer.fit_transform(texts)

	t  = cosine_similarity(tf)
	print(t)


	G = nx.DiGraph()
	slides_in = []
	edges = []
	for i in range(0, len(cenas)):
		for j in range(len(cenas), len(texts)):
			edges.append((i, j, t[i][j]))

	G.add_weighted_edges_from(edges)


	matching = list(nx.max_weight_matching(G))

	for i in range(len(matching)):
		if matching[i][0] > matching[i][1]:
			matching[i] = (matching[i][1], matching[i][0])


	matching = sorted(matching)

	print("--------------------------")
	for i in range(len(matching)):
		for j in range(len(matching) - 1):
			if matching[j][1] > matching[j+1][1]:
				aux = matching[j][1]
				matching[j] = (matching[j][0], matching[j+1][1])
				matching[j+1] = (matching[j+1][0], aux)




	print("--- %s seconds ---" % (time.time() - start_time))

	print(matching)

	return matching, scene_boundaries


if __name__ == "__main__":
	root_path_exec = "/home/eduardo/Trab_FSM/Multimedia_Systems_Synchronize/"

	root_path = sys.argv[1]
	ip = sys.argv[2]
	user = sys.argv[3]
	passw = sys.argv[4]
	try:
		stem = sys.argv[5]
	except IndexError:
		stem = False
		print('Don\'t stemmize transcripts')
	if stem:
		stem = True
	print("Processing...Wait")
	matching, scene_boundaries = matching(root_path, root_path_exec, stem)
	g_ncl.createNCLApplication(matching, scene_boundaries, root_path, root_path_exec)
	transfer_app.transferApp(ip, user, passw, root_path)
