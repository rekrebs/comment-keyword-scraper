import collections
import re
import requests
from bs4 import BeautifulSoup 
## using beautiful soup to help scrape
## get words
def clean_text(text):
    text = text.lower().strip() ## force lowercase
    text = re.sub(r"[^\w\s]", "", text)  ## remove punctuation 
    return text

## pretend not to be a script   ## stand in for now
def analyze_comments(url, target_keywords):
    headers = {
        "User-Agent": "Chrome/120.0.0.0"
    }

    keyword_counter = collections.Counter()  ##count my keywords
    matched_comments = []   ##show matches

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
    except Exception:
        return None

    soup = BeautifulSoup(response.text, "html.parser") ## parse response, get soup 

    comment_elements = soup.find_all("p")  ##looking for paragraphs for now.. need to fit to website structure

    for element in comment_elements:
        original_text = element.text.strip()
        if not original_text:
            continue
        cleaned = clean_text(original_text)
        words_in_comment = cleaned.split()

        found_in_this_comment = []
        for keyword in target_keywords:
            keyword_clean = keyword.lower().strip()
    
            if keyword_clean in words_in_comment:   ## find cleaned words
                keyword_counter[keyword_clean] += 1
                found_in_this_comment.append(keyword_clean)

            if found_in_this_comment:
                matched_comments.append(
                {
                    "text": original_text,
                    "matched_keywords": list(set(found_in_this_comment)),
                }
            )

    return matched_comments, keyword_counter