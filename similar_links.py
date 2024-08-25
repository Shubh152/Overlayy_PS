#! /usr/bin/env python3

import json
from datetime import date
from optparse import OptionParser
from colorama import Fore, Back, Style
from time import strftime, localtime
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

status_color = {
    '+': Fore.GREEN,
    '-': Fore.RED,
    '*': Fore.YELLOW,
    ':': Fore.CYAN,
    ' ': Fore.WHITE,
}

def get_time():
    return strftime("%H:%M:%S", localtime())
def display(status, data, start='', end='\n'):
    print(f"{start}{status_color[status]}[{status}] {Fore.BLUE}[{date.today()} {strftime('%H:%M:%S', localtime())}] {status_color[status]}{Style.BRIGHT}{data}{Fore.RESET}{Style.RESET_ALL}", end=end)

def get_arguments(*args):
    parser = OptionParser()
    for arg in args:
        parser.add_option(arg[0], arg[1], dest=arg[2], help=arg[3])
    return parser.parse_args()[0]

def getTitle(content):
    for line in content.split('\n'):
        if line.startswith("Title"):
            try:
                return line.split(':')[1].strip()
            except:
                pass
    return ""

if __name__ == "__main__":
    arguments = get_arguments(('-c', "--content", "content", "Content JSON File"),
                              ('-q', "--questions", "questions", "Question JSON File"),
                              ('-w', "--write", "write", "Name of the File for the data to be dumped (default=current data and time)"))
    if not arguments.content:
        display('-', f"Please specify {Back.YELLOW}Content JSON File{Back.RESET}")
        exit(0)
    else:
        try:
            with open(arguments.content, 'r') as file:
                arguments.content = json.load(file)
        except Exception as error:
            display('-', f"Error Occured while Reading File {Back.MAGENTA}{arguments.content}{Back.RESET} => {Back.YELLOW}{error}{Back.RESET}")
            exit(0)
    if not arguments.questions:
        display('-', f"Please specify {Back.YELLOW}Questions JSON File{Back.RESET}")
        exit(0)
    else:
        try:
            with open(arguments.questions, 'r') as file:
                arguments.questions = json.load(file)
        except Exception as error:
            display('-', f"Error Occured while Reading File {Back.MAGENTA}{arguments.questions}{Back.RESET} => {Back.YELLOW}{error}{Back.RESET}")
            exit(0)
    if not arguments.write:
        arguments.write = f"{date.today()} {strftime('%H_%M_%S', localtime())}.json"
    urls = list(arguments.content.keys())
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(list(arguments.content.values()))
    similarity_matrix = cosine_similarity(tfidf_matrix)
    similarity_dict = {}
    for i, url in enumerate(urls):
        similar_scores = list(enumerate(similarity_matrix[i]))
        sorted_similarities = sorted(similar_scores, key=lambda x: x[1], reverse=True)[1:]
        similarity_dict[url] = sorted_similarities
    final_data = []
    for url in urls:
        current_url = {}
        current_url["url"] = url
        current_url["questions"] = arguments.questions[url]
        current_url["relevant_links"] = [{"url": urls[j], "title": getTitle(arguments.content[urls[j]])} for j in [i[0]-1 for i in similarity_dict[url][:5%len(similarity_dict[url])]]]
        final_data.append(current_url)
    with open(arguments.write, 'w') as file:
        json.dump(final_data, file)