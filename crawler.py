import bs4
import urllib2
import pymongo
import threading
import time
from datetime import datetime
from pymongo import MongoClient, Connection

# Connect to a mongoDB database
# client = MongoClient('GRAHO2TEST', 27017)
client = Connection()

db = client.Wikipedia

# String a list of exceptions
others = ['.jpg', 'File:', 'Category:', 'Wikipedia:', 'Help:', 'Special:', 'Portal:', 'Template:', 'Template_talk:', '(disambiguation)', 'Talk:', 'User:']

def ScrapePage(wiki):
	"""
	Open a wikipedia page and add the information to the database
	Links table has the two pages that are linked
	History table tracks when the page was last updated
	Queue table contains tables that will be updated next
	"""

	if db.Lookup.find( {'PageName': wiki} ).count() == 0:
		db.Lookup.insert( {'PageName': wiki} )

	webpage = urllib2.urlopen('https://en.wikipedia.org/wiki/' + wiki)

	# Parse the html for all links
	soup = bs4.BeautifulSoup(webpage.read().decode('utf8'))
	anchors = soup.find_all('a')

	a_cnt = 0
	for anchor in anchors:
		skip = False
		link_check = anchor.get('href', '')

		# Make sure it isn't in our list of exceptions
		if link_check[:6] == '/wiki/'and link_check[6:] != wiki:
			a_cnt += 1
			for check in others:
				if check in link_check:
					skip = True
					break

			if skip:
				continue

			# Clean up the name
			link_name = link_check[6:]

			# Check to see if it is already in the db
			if db.Lookup.find_one( {'PageName': link_name} ) == None:
				db.Lookup.insert( {'PageName': link_name} )

			# Read the id (used for quicker indexing)
			wiki_code = db.Lookup.find_one( {'PageName': wiki} )['_id']
			link_code = db.Lookup.find_one( {'PageName': link_name} )['_id']

			# Add to db if it doesn't already exist
			if db.Links.find_one( {'Page1': wiki_code, 'Page2': link_code} ) == None:
				links_add = {'Page1': wiki_code, 'Page2': link_code}
				db.Links.insert(links_add)

			# Document the page scraped and the time
			hist_add = {'_id': wiki_code, 'Date': datetime.now()}
			db.History.insert(hist_add)

			q_add = {'_id': link_code}
			db.Queue.insert(q_add)
	pass


def ClearData(database):
	"""
	Remove all data in the database
	"""
	coll_names = [name for name in database.collection_names() if name != 'system.indexes']
	
	for coll in coll_names:
		database.drop_collection(coll)
	pass


def ScrapeLoop(database):
	"""
	Loop through 100 queued pages
	"""

	stop = 0
	while stop < 100:
		wiki_code = database.Queue.find_one()['_id']
		wiki_name = database.Lookup.find_one( {'_id': wiki_code} )['PageName']

		if database.History.find_one({'_id': wiki_name}) == None:
			try:
				ScrapePage(wiki_name)
				stop += 1
			except Exception as e:
				print e
				pass
		database.Queue.remove({'_id': wiki_code})


## Scrape main page to build a starting queue
wiki = 'Main_Page'
ScrapePage(wiki)

# stop = False
# th = threading.Thread(target = ScrapeLoop, args = (db,))
# th.start()
# 
# raw_input('Press enter to stop scraping')
# stop = True

# Loop through and pull some links
for i in range(10):
	start = time.time()
	ScrapeLoop(db)
	end = time.time()

	print end - start

# client.Close()
# client.drop_database('Wikipedia')
# ClearData(db)

# Pull some test links to make sure everything is working
test_dict = {}
check = db.Links.find()
for ent in check:
	key = str(ent['Page1']) + ' ' + str(ent['Page2'])

	if key in test_dict:
		test_dict[key] += 1
	else:
		test_dict[key] = 1

print set(test_dict.values())
