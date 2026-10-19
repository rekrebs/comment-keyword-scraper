import collections
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def clean_text(text): ##define clean text
    text = text.lower().strip() ## make lower case
    text = re.sub(r"[^\w\s]", "", text) ## get rid of ! . etc
    return text


def analyze_comments(url, target_keywords): ##building a functiom
    keyword_counter = collections.Counter()
    matched_comments = []

    #ENGAGE JS PLAYWRIGHT TOOL ---
    with sync_playwright() as p:
        try:
            # Run headless=True means no physical popup window
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print(f"📡 Launching automated browser to load: {url}...")
            # Go to the URL and wait up to 30 seconds
            page.goto(url, wait_until="networkidle", timeout=30000)

            # Force comments to render
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)  # Wait 2 seconds for visual updates

            # Extract rendered HTML code
            html_content = page.content()
            browser.close()
        except Exception as e:
            print(f"Browser execution failed: {e}") ##feedback
            return None

    # --- PROCESS THE EXTRACTED HTML FOR KEYWORDS ---
    soup = BeautifulSoup(html_content, "html.parser")
    comment_elements = soup.find_all(["p", "span", "div", "li"]) ## grab all containers (paragraph, spans, lists, divisions)
    seen_texts = set()

    for element in comment_elements:
        original_text = element.text.strip()
        if (
            not original_text
            or len(original_text) < 5
            or original_text in seen_texts
        ):
            continue

        seen_texts.add(original_text)
        cleaned = clean_text(original_text)
        words_in_comment = cleaned.split()

        found_in_this_comment = []
        for keyword in target_keywords:
            keyword_clean = keyword.lower().strip()
            if keyword_clean in words_in_comment:
                keyword_counter[keyword_clean] += 1
                found_in_this_comment.append(keyword_clean)

        if found_in_this_comment:
            matched_comments.append(
                {
                    "text": original_text,
                    "matched_keywords": list(set(found_in_this_comment)),
                }
            )

    # shiny app
    return matched_comments, keyword_counter