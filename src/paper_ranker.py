import configparser
import logging
from src.arxiv_scrapper import fetch_recent_papers, filter_papers_by_timeframe

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def rank_papers(papers, ranking_strategy='simple'):
    """
    Ranks a list of papers based on a given strategy.

    Args:
        papers (list): A list of dictionaries, where each dictionary represents a paper.
        ranking_strategy (str): The strategy to use for ranking ('simple' or 'llm-based').

    Returns:
        list: The sorted list of papers, with the highest-ranked paper first.
    """
    if not papers:
        logging.warning("No papers provided to rank.")
        return []

    logging.info(f"Ranking {len(papers)} papers using the '{ranking_strategy}' strategy.")

    if ranking_strategy == 'simple':
        # Simple ranking based on a combination of keywords and recency.
        # This is a good starting point before adding a more complex LLM-based system.
        scored_papers = []
        for paper in papers:
            score = 0
            # Higher score for more recent papers
            recency_score = (datetime.now() - paper['published']).days
            score += max(0, 30 - recency_score) # Penalize older papers

            # To-Do:
            # 1. Add logic to give a score boost based on keywords found in the title and summary
            #    that are relevant to the podcast's theme (e.g., 'neuroscience', 'cognition',
            #    'human-like', 'consciousness'). This is critical for connecting ML research
            #    to the psychological and neuroscientific aspects of your podcast.
            # 2. To implement this, you could define a list of keywords in your `settings.ini`.

            paper['score'] = score
            scored_papers.append(paper)

        # Sort papers by their calculated score in descending order
        ranked_papers = sorted(scored_papers, key=lambda p: p['score'], reverse=True)
        return ranked_papers

    # To-Do:
    # 3. Implement an 'llm-based' ranking strategy. This would involve a new function that
    #    sends the abstracts of the top N papers to an LLM with a specific prompt.
    #    The prompt would ask the LLM to score or rank the papers based on their
    #    potential to generate an interesting interdisciplinary discussion between
    #    an ML expert, a neuroscientist, and a psychologist.

    else:
        logging.error(f"Unknown ranking strategy: {ranking_strategy}")
        return papers

def select_top_paper(ranked_papers, top_n=1):
    """
    Selects the top N papers from a ranked list.

    Args:
        ranked_papers (list): A list of papers, already sorted by rank.
        top_n (int): The number of top papers to select.

    Returns:
        list: A list containing the top N selected papers.
    """
    if not ranked_papers:
        logging.warning("No papers to select from.")
        return []

    # To-Do:
    # 4. Add a check here to ensure the top-ranked paper's abstract is long enough for the
    #    LLM to generate a coherent podcast episode.

    return ranked_papers[:top_n]

def main():
    """
    Main function to run the paper ranking process.
    """
    # This is a placeholder for how it would connect to the scraper.
    # In practice, `main.py` would handle this connection.


    config = load_config('./config/settings.ini')
    query = config.get('arxiv', 'query')
    max_results = config.getint('arxiv', 'max_results')

    papers = fetch_recent_papers(query, max_results)
    recent_papers = filter_papers_by_timeframe(papers)

    ranked_papers = rank_papers(recent_papers)

    if ranked_papers:
        selected_paper = select_top_paper(ranked_papers, top_n=1)
        logging.info(f"Selected paper for podcast: {selected_paper[0]['title']}")
        # This selected_paper object will then be passed to llm_podcaster.py
    else:
        logging.info("No suitable papers found to select.")

if __name__ == "__main__":
    from datetime import datetime, timedelta
    main()
