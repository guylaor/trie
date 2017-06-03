import urllib.request
import json, pickle, re, os

# this is the in-memory database
root_chain = {}


def wordchain(word, chain, data_id):
    """ data structure builder - user recursiveness to build a dict in the format
    chain['w']['o']['r']['d'] for the string word """

    key = word[:1]
    if key not in chain:
        chain[key] = {}

    if len(word) > 1:
        wordchain(word[1:], chain[key], data_id)
    else:
        if 'id' in chain[key]:
            chain[key]['id'].append(data_id)
        else:
            chain[key]['id'] = [data_id]

    return chain


def get_data_files():
    """ loads data from api and saves to json files """

    BASE_URL = 'http://www.giantbomb.com/api/games/?api_key=84e4fdf8957ddf84247c3ea012a4773ffead8156&'

    offset = 0
    for i in range(1,15): # this is hardcoded to the number of results of this category
        offset = i * 100
        url = '{}format=json&offset={}&platforms=21'.format(BASE_URL, offset)
        localfile = 'data/data-{}.json'.format(offset)
        print('Saving json file {}'.format(localfile))
        urllib.request.urlretrieve (url, localfile)


def load_json_file(filename, counter):
    """ loads one json files and indexes it """

    with open(filename) as data_file:
        data = json.load(data_file)

        num_results = len(data['results'])
        for i in range(num_results):
            item = data['results'][i]
            name_list = create_clean_word_list(item['name'])
            # we make a new dict with just the items we care about
            item_d = {'name': item['name'], 'description': item['description'], 'url': item['site_detail_url'], 'name_list': name_list}
            # we use pickle to save this dict to file, for later use. counter is an auto-increment id for the record
            pickle_name = 'db/{}.pickle'.format(counter)
            with open(pickle_name, 'wb') as f:
                pickle.dump(item_d, f, pickle.HIGHEST_PROTOCOL)
            # this is where we add the words from the name of the game to the index
            for word in name_list:
                wordchain(word, root_chain, counter)
            print ('Loading: ', counter, item_d['name'])
            counter += 1

    return counter

def build_database():
    """ loads all json files from data folder """

    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists('db'):
        os.makedirs('db')

    source = 'data/'
    counter = 1
    for root, dirs, filenames in os.walk(source):
        # if this is the first run, check the data folder. if there are no files, get them form the api
        if not filenames:
            get_data_files()
            build_database()
        for f in filenames:
            print (f)
            filepath = 'data/{}'.format(f)
            counter = load_json_file(filepath, counter)


def create_clean_word_list(line):
    """ cleans name of game from stop words """

     # a list of stop words to be removed
    stop_words = ['the', 'that', 'to', 'as', 'there', 'has', 'and', 'or', 'is', 'not', 'a', 'of', 'but', 'in', 'by', 'on', 'are', 'it', 'if'] + ["'n", "&", "that's"]

    words = line.lower().split()
    no_stop_words = [w for w in words if w not in stop_words]
    # clean1 = [w[:-1] for w in no_stop_words if ':' in w]
    # clean2 = [w for w in no_stop_words if ':' not in w]
    # return clean1 + clean2
    clean = list(map(lambda w: w[:-1] if ':' in w else w ,no_stop_words))
    # this lamdba expression does the same as the previous 3 lines, not sure what is faster.  kept it for reference.
    return clean


def load_results_from_db(ind):
    """ loads the result record from the pickeld file """

    pickle_file = 'db/{}.pickle'.format(ind)
    with open(pickle_file, 'rb') as f:
        data = pickle.load(f)
        return data

def search_word(word):
    """ performs the search on the index """

    d = root_chain
    for i in range(len(word)):
        if word[i] in d:
            d = d[word[i]]
        else:
            d = {}
    if 'id' in d:
        return d['id']
    else:
        return []

def rank_results(result_set, search_words):
    """ ranking is based on how many search words appear in the game name """

    max_rank = len(search_words)
    ranked_result = []
    for res in result_set:
        d = load_results_from_db(res)
        rank = len(set(d['name_list']) & set(search_words))
        ranked_result.append({'rank': rank, 'name': d['name'], 'url':d['url']})

    for i in reversed(range(max_rank+1)):
        r = i
        for res in ranked_result:
            if res['rank'] == r:
                print ("### name: {}".format(res['name']))
                print ("    url : {}".format(res['url']))
                print ("    rank: {}".format(res['rank']))
    print('  ')

def search(input_str):
    """ run the search from input string """

    search_words = input_str.split()
    results = []
    for word in search_words:
            results = results + search_word(word)
    unique = set(results)
    print('  ')
    print("Search input: {}".format(input_str))
    print("Found {} results.".format(len(unique)))
    rank_results(unique, search_words)

def main():
    build_database()
    run = True
    print('Enter search term (or type -exit to terminate)')
    while run:
        input_var = input("Search: ")
        if input_var == '-exit':
            run = False
        else:
            search(input_var)


if __name__ == "__main__":
    main()
