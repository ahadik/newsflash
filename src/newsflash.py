#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import numpy as np
import csv
from collections import defaultdict
import pickle

from tokenizer import Tokenizer
from seconds import seconds
from place import trending_location, get_corners

'''
does things

created 2015-05-06 02:20h
'''


class Newsflash:
	def __init__(self):
		# just an inverse index, with list of tweet IDs per term
		# might be good to combine with ranks and add time/location s.t.
		# we're not looking up things as much.
		self.terms = defaultdict(list) 

		self.ranks = {} # contains ranking tuple per term
		self.tweets = {}


		self.first_tweet = None
		self.last_tweet = None


class Tweet:
	def __init__(self, time, loc, words, text):
		self.time = time # float (I think), Unix time, seconds
		self.loc = loc # 2-tuple (lat,lon), each is a float
		self.words = words # set of tokenized terms in the tweet
		self.text = text # raw text of the tweet


class Rank:
	def __init__(self, freq, dfreq, box, box_size, corners):
		self.freq = freq # number of tweets containing this term
		self.dfreq = dfreq # relative rate of related tweets (last 24h vs. overall)
		self.box = box # bounding box [[minlat, maxlat], [minlon,maxlon]]
		self.box_size = box_size # distance between two far corners of the bounding box

		# list of corners, progressively zooming in to display the process
		# of the trending_location function. each corner is a lisf of 4 
		# 2-tuples (lat,lon), with the order SW, NW, NE, SE
		# don't necessarily need this, progression of zooming in bounding box
		self.corners = corners






def remove_old(nf):
	'''
	remove all tweets older than X days?
	'''
	about_a_week_ago = nf.tweets[nf.last_tweet].time - 604800

	for tid in sorted(nf.tweets, key=lambda t: nf.tweets[t].time):
		if nf.tweets[tid].time < about_a_week_ago:
			# remove tweet ID from all inverse indices 
			for w in nf.tweets[tid].words:
				nf.terms[w].remove(tid)

			nf.tweets.pop(tid) # remove tweet entirely


	# NOT SURE IF WE SHOULD DO THIS NOW, it depends how often
	# we call remove_old and compute_rankings
	compute_rankings(nf) # recompute rankings now





def get_tweets_by_term(nf, term):
	'''
	returns a 2-tuple (box, tweets):
	- box = bounding box for this term. box is a list of 2-tuples, where each
			2-tuple is (lat,lon) for the SW, NW, NE, and SE corners (in that
			order, s.t. the list has length 4)
	- tweets = list of tweets containing this term. Each element in the list is
			a 2-tuple, with elements (location, text). location itself is a
			2-tuple of floats (lat,lon); text is a str with the text of 
			the tweet.
	'''

	if len(nf.ranks) == 0:
		e = 'ERROR - rankings have not been calculated yet'
		sys.stderr.write(e+'\n')
		return [e,[]] # idk just something in a similar format

	return (get_corners(nf.ranks[term].box), [((nf.tweets[tid].loc, 
				nf.tweets[tid].text) for tid in nf.terms[term])])


def find_related_tweets(nf, terms):
	'''
	takes in the top n terms and tries to find groups of related tweets
	at first we're using 100 but this can be changed
	'''
	level = 10 # go 10 deep before we stop

	explored_tweets = []








def parse_tweet(nf, tokenizer, t):
	'''
	takes in the tweet as a string. I'm thinking that initializing
	a new CSV reader for each tweet is prob inefficient but idk we'll see
	'''
	tid = t[0]

	words = tokenizer.tokenize(t[7])
	for word in words: nf.terms[word].append(tid) # add to inverse index

	nf.tweets[tid] = Tweet(seconds(t[1]), (float(t[5]), float(t[6])), words, t[7])

	return tid



def compute_rankings(nf):
	start = nf.tweets[nf.first_tweet].time
	end = nf.tweets[nf.last_tweet].time
	window = (end-start)/86400 # seconds per day = 86,400

	print 'tweet collection window = %f days' % window

	for term,tweets in nf.terms.items():
		freq = len(tweets)

		# now calculate the increase / rate of increase of freq somehow.
		# for now, I'll just compare freq in the last day to freq overall
		today_tweets = 0 # number of tweets w/ this term in the last 24h
		for tid in tweets:
			if end - nf.tweets[tid].time < 86400: today_tweets += 1 # seconds per day = 86,400

		dfreq = today_tweets / (freq/window)

		# now calculate the geography thing
		all_points = [nf.tweets[tid].loc for tid in tweets]
		box, box_size, num_points, corners = trending_location(all_points)
		today_points_ratio = num_points / float(len(all_points))
		
		# note that not everything being returned by trending_location
		# is actually given to Rank or even used.
		nf.ranks[term] = Rank(freq, dfreq, box, box_size, corners)



	# YO this whole section of code is p bloated and not great, but I'm just keeping
	# it for now while I'm changing the format to classes.
	sorter = lambda x: nf.ranks[x].freq*(nf.ranks[x].dfreq**2) # *(1+x[1][3])
	sorted_rankings = list(reversed(sorted(nf.ranks.keys(), key=sorter)))

	find_related_tweets(nf, [x for i,x in enumerate(sorted_rankings) if i<100])

	# code for the visual bounding box animation
	top_20 = sorted_rankings[:20]
	top_corners = []
	for term in top_20:
		rank = nf.ranks[term]
		top_corners.append(rank.corners)
		print '%s (%d, %f)\t%f' % (term, rank.freq, rank.dfreq, rank.box_size)

	return (top_20, top_corners)



def get_top_terms_boxes(tweet_data_file, pickle_file=None):
	nf = Newsflash()
	tokenizer = Tokenizer()

	# initialize things -- later we will read from tweets in real 
	# time but rn it's a static file
	with open(tweet_data_file) as f:
		r = csv.reader(f)
		next(r, None) # eliminate header row

		# need to catch first tweet for its timestamp
		nf.first_tweet = parse_tweet(nf, tokenizer, next(r, None))

		for row in r: nf.last_tweet = parse_tweet(nf, tokenizer, row)

	top_20, top_corners = compute_rankings(nf)

	if pickle_file:
		pickle.dump(nf, file(pickle_file, 'w'))

	return (top_20, top_corners)


def main(tweet_data_file, pickle_file=None):
	get_top_terms_boxes(tweet_data_file, pickle_file)


if __name__ == '__main__':
	if len(sys.argv) == 2:
		main(sys.argv[1])
	elif len(sys.argv) == 3:
		main(sys.argv[1], sys.argv[2])
	else:
		sys.exit('Usage: ./newsflash.py <tweet_data_file> [<pickle_file>]')

