import pymongo
from pymongo import MongoClient
from pymongo import Connection

## url:  https://www.youtube.com/watch?v=GSL8JpyAjsE

# connect to my server
# client = MongoClient('GRAHO2TEST', 27017)
client = Connection()


## Created a db in mongo
db = client.troy_test


# Creates collection of people - Do i have collection of people? - if not create it
people = db.people



# fill people with some data
people.insert({'name':'Mike' , 'food':'cheese'})
people.insert({'name':'John' , 'food':'ham', 'location' : 'UK'})
people.insert({'name':'michelle' , 'food':'cheese'})
people.insert({'name':'jamie' , 'food':'ham'})

# search for everyone in people - broad search
peeps = people.find()

for person in peeps:
    print person

client.drop_database('troy_test')


# refined search example - if you run ALL of the code again (insert the above people two times) then these people will show up multiple times...there is a way to clean this up.. (will come later on)
peeps = people.find({'food':'cheese'})
for person in peeps:
    print person



# lets use a "like" search (regular expressions)

peeps = people.find({'name':{'$regex' : '.*[Mm]i.*'}})
# to break this down:
# within the collection of people, look within the name collection for:
# any beginning (.) then either a capital M or lowercase m, followed by an i then ANY end (.) any number of times (*)
# (should return both mike anc michelle and jamie)
for person in peeps:
    print person


## what if I only want to look at people with names that START with and M and an i?
peeps = people.find({'name':{'$regex' : '\A[Mm]i.*'}})
# to break this down:
# within the collection of people, look within the name collection for:
# any beginning (*) then either a capital M or lowercase m, followed by an i then ANY end (*)
# (should return both mike anc michelle and jamie)
for person in peeps:
    print person





## what about record updates?
person = people.find_one({'food' :'ham'})
# find one will only return one item...if multiple items exist it will return the first record with the true criteria
person['food'] = 'eggs'
# it's been changed...now it needs to be saved back into the db
people.save(person)


peeps = people.find({'food':'eggs'})



for person in peeps:
    print person


# let's remove any people in the file
# for person in people.find():
#     people.remove(person)


# for person in peeps:
#     print person
