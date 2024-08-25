#! /usr/bin/env python3

import sys, json

if __name__ == "__main__":
    with open(sys.argv[1], 'r') as file:
        data = json.load(file)
    urls = []
    for url, value in data.items():
        urls.extend(value["internal_urls"])
    with open(sys.argv[2], 'w') as file:
        file.write('\n'.join(urls))