#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <url>"
    exit 1
fi

URL="$1"

BASE_NAME=$(basename "$URL" | sed 's/\.[^.]*$//')
JSON_FILE="${BASE_NAME}_crawler.json"
TXT_FILE="${BASE_NAME}_urls.txt"
CONTENT_FILE="${BASE_NAME}_content.json"
QUESTIONS_FILE="${BASE_NAME}_questions.json"
FINAL_FILE="${BASE_NAME}_final_file.json"

python3 crawler.py --url "$URL" --write "$JSON_FILE"
python3 json_to_txt.py "$JSON_FILE" "$TXT_FILE"
python3 jina_ai.py --url "$TXT_FILE" --write "$CONTENT_FILE"
python3 generate_questions.py --content "$CONTENT_FILE" --write "$QUESTIONS_FILE"
python3 similar_links.py --content "$CONTENT_FILE" --questions "$QUESTIONS_FILE" --write "$FINAL_FILE"

echo "Process completed. Final output written to $FINAL_FILE"