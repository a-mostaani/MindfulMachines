import feedparser
import time
from datetime import datetime, timedelta
import configparser


##Structure:
"""
main.py: This acts as the orchestrator. It initiates the process by calling the functions from arxiv_scraper.py in a specific order.

load_config: This function is called first to get all the necessary settings, such as the search query and the number of results, from your settings.ini file.

fetch_recent_papers: This is the core scraping function. It takes the query from the configuration and retrieves the raw paper data from the arXiv API.

filter_papers_by_timeframe: The raw list of papers is then passed to this function, which refines the list by keeping only the most recent entries, as per the logic you've already defined.

paper_ranker.py: This is the crucial next step in your pipeline. The filter_papers_by_timeframe function's output, a list of filtered papers, becomes the input for the paper_ranker.py module. Its job will be to analyze these papers and select the most promising one for the next stage of your podcast generation process.

"""


def load_config(config_file):
    """
    Loads configuration settings from the specified INI file.

    Args:
        config_file (str): The path to the configuration file.

    Returns:
        configparser.ConfigParser: The loaded configuration object.
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def fetch_recent_papers(query, max_results=10, sort_by='relevance'):
    """
    Fetches recent research papers from arXiv.org using the arXiv API.

    Args:
        query (str): The search query (e.g., 'LLMs', 'reinforcement learning').
        max_results (int): The maximum number of papers to retrieve.
        sort_by (str): The sorting criterion ('relevance', 'submittedDate', 'lastUpdatedDate').

    Returns:
        list: A list of dictionaries, where each dictionary represents a paper.
    """
    # The arXiv API URL for a search query
    base_url = 'http://export.arxiv.org/api/query?'
    search_query = f'search_query=all:{query}&start=0&max_results={max_results}&sortBy={sort_by}'

    print(f"Fetching papers with query: {query}...")

    try:
        response = feedparser.parse(base_url + search_query)
        if response.bozo:
            raise Exception("Failed to parse feed. Is the arXiv API reachable?")

        papers = []
        for entry in response.entries:
            paper_details = {
                'title': entry.title,
                'authors': [author.name for author in entry.authors],
                'summary': entry.summary,
                'link': entry.link,
                'published': datetime(*entry.published_parsed[:6]),
                'updated': datetime(*entry.updated_parsed[:6]),
            }
            papers.append(paper_details)
        return papers

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def filter_papers_by_timeframe(papers, days=7):
    """
    Filters a list of papers to include only those published or updated
    within a specified number of days.

    Args:
        papers (list): A list of paper dictionaries.
        days (int): The number of days to look back.

    Returns:
        list: A filtered list of paper dictionaries.
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    filtered_papers = [
        p for p in papers if p['published'] > cutoff_date or p['updated'] > cutoff_date
    ]
    print(f"Filtered to {len(filtered_papers)} papers published in the last {days} days.")
    return filtered_papers

def scrape_papers(config):
    """
    Main function to run the scraping process.
    """
    # Load configuration
    config = load_config('./config/settings.ini')

    # Get parameters from config
    query = config.get('arxiv', 'query')
    max_results = config.getint('arxiv', 'max_results')

    # Step 1: Fetch papers from arXiv
    all_papers = fetch_recent_papers(query, max_results)

    if not all_papers:
        print("No papers found. Exiting.")
        return

    # Step 2: Filter papers by a recent timeframe (e.g., last 7 days)
    recent_papers = filter_papers_by_timeframe(all_papers)

    # In a real pipeline, the 'recent_papers' list would be passed
    # to the `paper_ranker.py` module.
    print("\n-- Fetched Papers --")
    for paper in recent_papers:
        print(f"Title: {paper['title']}")
        print(f"Authors: {', '.join(paper['authors'])}")
        print(f"Link: {paper['link']}\n")

    # To-Do:
    # 1. Implement robust error handling for API failures and network issues.
    # 2. Add support for more complex queries with logical operators (AND, OR).
    # 3. Create a logging mechanism to record the scraping activity.
    # 4. Store fetched paper data in a temporary JSON file in the `data/temp/` directory.
    # 5. Add a simple caching mechanism to avoid re-fetching the same papers.

# if __name__ == "__main__":
#     scrape_papers(config)
