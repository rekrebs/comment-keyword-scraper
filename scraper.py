import collections
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


def clean_text(text):
    """Converts text to lowercase and strips out punctuation."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return text


async def analyze_comments(url, target_keywords):
    keyword_counter = collections.Counter()
    matched_comments = []

    async with async_playwright() as p:
        try:
            #User-Agent     
            user_agent = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )

            # 2. Launch Chromium with automation bypass arguments
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-http2",  # Keeps connection handling on stable protocol rules
                ],
            )

            # 3. removes the "HeadlessChrome" text that triggers the CBC's firewall block
            extra_headers = {
                "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand)";v="24", "Google Chrome";v="122"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "upgrade-insecure-requests": "1",
            }

            context = await browser.new_context(
                user_agent=user_agent,
                viewport={"width": 1280, "height": 720},
                extra_http_headers=extra_headers,  # Inject the squeaky-clean headers here
            )
            
            page = await context.new_page()

            print(f"📡 Launching clean-signature browser to load: {url}...")

            await page.goto(url, wait_until="commit", timeout=30000)

  
            await page.wait_for_timeout(3000)

            # Gather up the clean HTML string 
            html_content = await page.content()
            await browser.close()

        except Exception as e:
            print(f"Browser execution failed: {e}")
            return None

    # 4. Extract data using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    potential_elements = soup.find_all(["p", "div", "span", "h3"])

    seen_texts = set()

    for element in potential_elements:
        original_text = element.text.strip()

        if (
            not original_text
            or len(original_text) < 12
            or original_text in seen_texts
        ):
            continue

        # Skip main site menu structures to keep research results highly relevant
        if any(skip in original_text for skip in ["Skip to Main Content", "Accessibility Help", "All rights reserved"]):
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
                    "text": original_text[:350] + ("..." if len(original_text) > 350 else ""),
                    "matched_keywords": list(set(found_in_this_comment)),
                }
            )

    return matched_comments, keyword_counter
