#! /usr/bin/env python3

import requests, json
from multiprocessing import cpu_count, Pool, Lock
from datetime import date
from optparse import OptionParser
from colorama import Fore, Back, Style
from time import strftime, localtime, sleep

status_color = {
    '+': Fore.GREEN,
    '-': Fore.RED,
    '*': Fore.YELLOW,
    ':': Fore.CYAN,
    ' ': Fore.WHITE,
}

lock = Lock()
thread_count = cpu_count()
sleep_time = 100

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

api_key = "jina_c9d4dc8389de43508276ed745e1c1ff6qyZcKYSXgCZLTq4H33GLCYbiAE94"
jina_ai = "https://r.jina.ai/"

def getData(url):
    response = requests.get(f"{jina_ai}{url}", headers={"Authorization": f"Bearer {api_key}"})
    if response.status_code == 200:
        return response, response.status_code
    else:
        return False, response.status_code
def multithreadedHandler(urls):
    url_responses = {}
    for url in urls:
        while True:
            data, status_code = getData(url)
            if data:
                with lock:
                    display(':', f"Parsed => {Back.MAGENTA}{url}{Back.RESET}")
                url_responses[url] = data.text
                break
            else:
                with lock:
                    display('-', f"Failed to Parse => {Back.MAGENTA}{url}{Back.RESET} : {Back.YELLOW}{status_code}{Back.RESET}")
                if status_code == 402:
                    sleep(sleep_time)
                else:
                    break
    return url_responses

if __name__ == "__main__":
    arguments = get_arguments(('-u', "--url", "url", "URLs (Seperated by ',' or File Name)"),
                              ('-w', "--write", "write", "Name of the File for the data to be dumped (default=current data and time)"))
    if not arguments.url:
        display('-', f"Please specify {Back.YELLOW}URLs{Back.RESET}")
        exit(0)
    else:
        try:
            with open(arguments.url, 'r') as file:
                arguments.url = [url.strip() for url in file.read().split('\n') if url != '']
        except FileNotFoundError:
            arguments.url = arguments.url.split(',')
        except Exception as error:
            display('-', f"Error Occured while Reading File {Back.MAGENTA}{arguments.url}{Back.RESET} => {Back.YELLOW}{error}{Back.RESET}")
            exit(0)
    if not arguments.write:
        arguments.write = f"{date.today()} {strftime('%H_%M_%S', localtime())}.json"
    total_urls = len(arguments.url)
    url_divisions = [arguments.url[group*total_urls//thread_count: (group+1)*total_urls//thread_count] for group in range(thread_count)]
    pool = Pool(thread_count)
    responses = {}
    threads = []
    for url_division in url_divisions:
        threads.append(pool.apply_async(multithreadedHandler, (url_division, )))
    for thread in threads:
        responses.update(thread.get())
    pool.close()
    pool.join()
    with open(arguments.write, 'w') as file:
        json.dump(responses, file)