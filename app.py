import pandas as pd
from shiny import render, reactive
from shiny.express import ui, input

# import scraper py
from scraper import analyze_comments

# 1. Global Page Styling
ui.page_opts(title="Keyword Comment Analyzer Dashboard", fillable=True)

# 2. Creating Navigator
with ui.sidebar(title="Scraper Parameters"):
    ui.input_text("url", "Target Webpage URL:", value="https://ycombinator.com")
    ui.input_text("keywords", "Keywords to count (comma-split):", value="Python, AI, Code")
    ui.input_action_button("run", "Run Analysis Engine", class_="btn-success w-100")

# 3. Reactive Processor Box
@reactive.calc
def get_scraped_data():
    # Stops the script from executing until the user presses the button the first time
    if input.run() == 0:
        return None

    # Splitting the user's input line by commas into a proper Python list
    keyword_list = [k.strip() for k in input.keywords().split(",")]

    # Run the background scraper function using the user inputs
    results = analyze_comments(input.url(), keyword_list)
    return results

# 4. Displaying the Grid Dashboard
with ui.layout_columns(col_widths=[4, 8]):
    
    # Grid1: The Metrics Counter Table
    with ui.card():
        ui.card_header("Keyword Tally Breakdown")

        @render.table
        def display_metrics_table():
            data = get_scraped_data()
            if not data:
                return pd.DataFrame(columns=["Keyword", "Count"])
            _, tallies = data
            return pd.DataFrame(tallies.items(), columns=["Keyword", "Count"])

    # Grid2: Output
    with ui.card():
        ui.card_header("📝 Matched Content Strings")

        @render.text
        def display_comments_log():
            data = get_scraped_data()
            if not data:
                return "Awaiting parameters. Enter a URL and press 'Run Analysis Engine'."
            
            matches, _ = data
            if not matches:
                return "The web server returned data, but no keywords matched any page text elements."

            output_string = ""
            for idx, match in enumerate(matches, 1):
                tags = f"Tags matched: {', '.join(match['matched_keywords'])}"
                output_string += f" Match #{idx} ({tags})\n\"{match['text']}\"\n\n"
            return output_string
