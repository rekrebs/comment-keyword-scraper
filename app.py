import pandas as pd
from shiny import render, reactive
from shiny.express import ui, input

# import scraper.py
from scraper import analyze_comments


ui.page_opts(title="Keyword Comment Analyzer Dashboard", fillable=True)

# Navigator─────────────
with ui.sidebar(title="Scraper Parameters"):
    ui.input_text(
        "url", 
        "Target Webpage URL:", 
        value="https://www.cbc.ca"
    )
    ui.input_text(
        "keywords", 
        "Keywords to count (comma-split):", 
        value="Canada, Tax, Alberta"
    )
    ui.input_action_button(
        "run", 
        "Run Analysis Engine", 
        class_="btn-success w-100"
    )

# ─── REACTIVE CALCULATION ENGINE ──────────────────────────────────────────────
@reactive.calc
async def get_scraped_data():
    """Triggers and caches scraper execution after user interaction clicks."""
    if input.run() == 0:
        return None

    # Parse comma separated to array
    keyword_list = [k.strip() for k in input.keywords().split(",")]

    # Await web browser engine
    results = await analyze_comments(input.url(), keyword_list)
    return results

# ─── Dashboard─
with ui.layout_columns(col_widths=(4, 8)):
    
    # COLUMN BLOCK 1: Data Table ### building on this later
    with ui.card():
        ui.card_header("Keyword Tally Breakdown")

        @render.table
        async def display_metrics_table():
            # Await the coroutine calculation 
            data = await get_scraped_data()
            if not data:
                return pd.DataFrame(columns=["Keyword", "Count"]) ##get count
            
            _, tallies = data
            return pd.DataFrame(tallies.items(), columns=["Keyword", "Count"])

    # COL2: Live Filtered Log Stream Outputs
    with ui.card():
        ui.card_header("Matched Content Strings")

        @render.text
        async def display_comments_log():
            # Await the coroutine calculation safely to extract matched strings
            data = await get_scraped_data()
            if not data:
                return "Awaiting parameters. Enter a URL and press 'Run Analysis Engine'."
            
            matches, _ = data
            if not matches:
                return "The web server returned data, but no target keywords matched any page elements."

            output_string = ""
            for idx, match in enumerate(matches, 1):
                tags = f"Tags matched: {', '.join(match['matched_keywords'])}"
                output_string += f"Match #{idx} ({tags})\n\"{match['text']}\"\n\n"
            return output_string
