#! /usr/bin/env python3

import requests, pickle, json
import google.generativeai as genai
from multiprocessing import cpu_count, Pool, Lock
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from datetime import date
from optparse import OptionParser
from colorama import Fore, Back, Style
from time import strftime, localtime, time

status_color = {
    '+': Fore.GREEN,
    '-': Fore.RED,
    '*': Fore.YELLOW,
    ':': Fore.CYAN,
    ' ': Fore.WHITE,
}

lock = Lock()
thread_count = cpu_count()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.50 Safari/537.36",
    "Connection": "close",
    "DNT": "1"
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

api_key = "AIzaSyDo_8oLpUItu6NBzTQho6nxkw34AtObRQY"
model_name = "gemini-1.5-flash"
genai.configure(api_key=api_key)
model= genai.GenerativeModel(model_name)

def multithreadingHandler(contents):
    content_resposnes = {}
    for url, content in contents.items():
        try:
            content = content.replace('\\n', '\n')
            response = model.generate_content(f"This is a content of the URL : {url}\nGenerate 10 Questions from it. Each question should be less than 80 words.\nGive the Questions in this format 1.QUESTION_CONTENT\nAnd Print nothing else\n\n{content}").text
            questions = []
            for line in response.split('\n'):
                try:
                    if line.split('.')[0].strip().isdigit():
                        questions.append(line.split('.')[1].strip())
                except:
                    pass
            content_resposnes[url] = questions
        except Exception as error:
            pass
    return content_resposnes

if __name__ == "__main__":
    arguments = get_arguments(('-c', "--content", "content", "JSON File of URL Content"),
                              ('-w', "--write", "write", "Name of the File for the data to be dumped (default=current data and time)"))
    if not arguments.content:
        display('-', f"Please specify {Back.YELLOW}JSON File of URL Content{Back.RESET}")
        exit(0)
    else:
        try:
            with open(arguments.content, 'r') as file:
                arguments.content = json.load(file)
        except Exception as error:
            display('-', f"Error Occured while Reading File {Back.MAGENTA}{arguments.content}{Back.RESET} => {Back.YELLOW}{error}{Back.RESET}")
            exit(0)
    if not arguments.write:
        arguments.write = f"{date.today()} {strftime('%H_%M_%S', localtime())}.csv"
    urls = list(arguments.content.keys())
    pool = Pool(thread_count)
    total_urls = len(urls)
    url_divisions = [urls[group*total_urls//thread_count: (group+1)*total_urls//thread_count] for group in range(thread_count)]
    responses = {}
    threads = []
    for url_division in url_divisions:
        threads.append(pool.apply_async(multithreadingHandler, ({url: arguments.content[url] for url in url_division}, )))
    for thread in threads:
        responses.update(thread.get())
    pool.close()
    pool.join()
    with open(arguments.write, 'w') as file:
        json.dump(responses, file)