from html.parser import HTMLParser
from domain import *
import collections
import os


# words parser class
class WordsParser(HTMLParser):
    # tags to search text within
    search_tags = ['p', 'div', 'span', 'a', 'h1', 'h2', 'h2', 'h3', 'h4']
    
    # current tag
    current_tag = ''
    
    # common word list
    common_words = {}
    
    # handle starting tag
    def handle_starttag(self, tag, attr):
        # store current tag
        self.current_tag = tag        
            
    # handle tag's data
    def handle_data(self, data):
        # make sure current tag matches search tags
        if self.current_tag in self.search_tags:
            # loop over word list within current tag
            for word in data.strip().split():
                # convert word to lowercase and filter characters
                common_word = word.lower()
                common_word = common_word.replace('.', '')
                common_word = common_word.replace(':', '')
                common_word = common_word.replace(',', '')
                common_word = common_word.replace('"', '')
                
                # filter words
                if (
                       len(common_word) >= 2 and
                       common_word[0].isalpha()
                   ):

                    try:
                        # try to update count of a given word 
                        self.common_words[common_word] += 1
                    
                    except:
                        # store current common word
                        self.common_words.update({common_word: 1})


# main driver
if __name__ == '__main__':

    PROJECT_NAME = 'repository'
    DOMAIN_NAME = get_domain_name('https://www.gmarket.co.kr/')
    html_dir = os.path.join(PROJECT_NAME, DOMAIN_NAME)

    # create words parser instance
    words_parser = WordsParser()

    for file in os.listdir(html_dir):
        if file.endswith('.html'):
            with open(os.path.join(html_dir, file), 'r', encoding='utf-8') as html_file:
                html_string = html_file.read()
                # feed the HTML to words parser
                words_parser.feed(html_string)
    
    # count common words with counter
    words_count = collections.Counter(words_parser.common_words)
    
    # extract 100 most common words
    most_common = words_count.most_common(100)
    
    # loop over most common words
    with open(os.path.join(PROJECT_NAME, 'frequentWords.csv'), 'w', encoding='utf-8') as f:
        for word, count in most_common:
            print(word, str(count) + ' times', sep=", ", file = f)
