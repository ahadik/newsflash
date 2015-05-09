'''
slightly modified from tokenizer.py in script_dev/1951/classification
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
       'just', 'don', 'should', 'now']

# include common ends that don't begin with http:// or www., e.g. short
# links from Twitter, Vine, Youtube, and bitly.
links = ['www.', 'http://', 'https://', '.com/', '.org/', '.net/', '.co/', '.ly/', '.be/', '.ms/']



class Tokenizer:
	def __init__(self):
		self.stemmer = PorterStemmer()

	def reduce_char(self, w):
		'''
		replace two or more occurrences of the same char (in a row)
		with two occurrences
		'''
		r = ''
		for i,x in enumerate(w):
			if i < 2 or x != w[i-2] or x != w[i-1]: r += x

		return r
		# return re.sub(r'(.)\1+', r'\1\1', w)	


	def tokenize(self, tweet):
		words = set()

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

			if w in stopwords: continue # ignore stopwords
			
			# replace two or more occurrence of same char with two
			notrip = '' 
			for i,x in enumerate(w):
				if i < 2 or x != w[i-2] or x != w[i-1]: notrip += x

			w = self.stemmer.stem(w, 0, len(w)-1) # apply stemming using Porter Stemmer

			if len(w) == 0: continue  # ignore now-blank words

			if not w[0].isalpha(): continue
			
			words.add(w) # ignore words that don't start with alphabet

			


		return words











