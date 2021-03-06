'''
based off of tokenizer.py in script_dev/1951/classification
'''

from porter_stemmer import PorterStemmer
import re

# 33-47, 58-64, 91-96, 123-126. Note that 35 is #, 64 is @
# digits 0-9 are 48-57
punct = ''.join(chr(x) for x in range(33,48)+range(58,65)+range(91,97)+range(123,127))
stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
       'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
       'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
       'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
       'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
       'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
       'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and',
       'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at',
       'by', 'for', 'with', 'about', 'against', 'between', 'into',
       'through', 'during', 'before', 'after', 'above', 'below', 'to',
       'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
       'again', 'further', 'then', 'once', 'here', 'there', 'when',
       'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
       'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
       'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will',
       'just', 'don', 'should', 'now', 'w/', 'like']

stopwords += ["it's", "it'll"]

# include common ends that don't begin with http:// or www., e.g. short
# links from Twitter, Vine, Youtube, and bitly.
links = ['www.', 'http://', 'https://', '.com/', '.org/', '.net/', '.co/', '.ly/', '.be/', '.ms/']


class Tokenizer:
	def __init__(self, ngrams=1):
		self.stemmer = PorterStemmer()
		self.ngrams = ngrams
		print ' -- initializing tokenizer with maximum ngram = %d' % ngrams

	def tokenize(self, tweet):
		words = set()
		ng = []

		# fix the most common HTML escapes
		tweet = tweet.replace('&quot;','').replace('&nbsp;',' ').replace('&amp;',' ')

		# replace certain word-splitting with spaces (e.g. 'foo...bar' should 
		# be split). do not include '.' because this will incorrectly split URLs 
		for c in ('...','..','&',','):
			tweet = tweet.replace(c,' ')


		for w in tweet.split():
			w = w.lower() # convert to lowercase
			
			# get rid of links and user mentions
			for s in links:
				if s in w: continue
			if w.startswith('@'): continue

			w = w.strip(punct) # strip punctuation (including hashtag)

			if len(w) == 0: continue  # ignore now-blank words

			if w in stopwords: continue # ignore stopwords
			
			# replace two or more occurrence of same char with two
			notrip = '' 
			for i,x in enumerate(w):
				if i < 2 or x != w[i-2] or x != w[i-1]: notrip += x

			notrip = self.stemmer.stem(notrip, 0, len(notrip)-1) # apply stemming using Porter Stemmer

			if not notrip[0].isalpha(): continue
			
			words.add(notrip) # ignore words that don't start with alphabet

			if self.ngrams>1: ng.append(notrip)


		# Generate all ngrams and add them
		if self.ngrams>1 and len(words)>1:
			if self.ngrams > len(words): self.ngrams = len(words)
			for i in range(len(ng)-self.ngrams+1):
				ngram = ng[i]
				for j in range(1,self.ngrams):
					ngram += ' '+ng[i+j]
					if ngram == 'madison squar garden': print 'msg'
					words.add(ngram)


		return words











