# trie
Trie data structure implementation in python




The code test is all in one file, indexer.py

in the first time the script will run it will create two folders
/data
/db

it will then download the data from the api and save it into json files in the /data folder, after that
the script will load those json files and start indexing the games.
it will save some of the data in .pickle files in the /db folder.


## indexing

Each game name is split into a list of words, that list is then cleaned form stop words, so that:
'Game of Thrones'
becomes the list
['game', 'thrones']

Each word in the list is then indexed. The data structure that is used for the indexing is a dict
in which each letter of the word is a dict itself. so that:
'game'
becomes:
dict['g']['a']['m']['e']

the value that is stored at the last level of this dict is another dict that has a key called 'id',
that key stores a list of numeric ids. These ids are the id of the pickled files from the original
json file. Those files contain the game name, url, description and whatever other information
that is important to save from the original json load.

## Search time

Since this is using a dict, and a dict has a running time of O(1), searching for a word is O(len(word))
This makes searching really fast.
The idea to use this structure was to imitate a binary search tree. Though, since the keys are letters
and not numbers, it made more sense to use a dict.

## Scaling

The real issue with this approach is that dicts are heavy on memory. So the this approach is limited by
how much memory the machine can use before this dict becomes too big.
Another approach is to save the words as an ordered list to a file, that then can do a binary search for the value,
but that will be like building a database...

# Usage

its really simple to use, just run

python indexer.py

there are no packages to install, it should run just fine. it is written in python 3.
It will first download the files and index them. after that you can type any search terms you want.
to exit enter '-exit'

# ranked results

notice that if you search for 'dragon ball' the results that have both words in the name will appear before
entries that have just 'dragon' or 'ball'


