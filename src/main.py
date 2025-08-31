import configparser
import logging
from datetime import datetime
import json
import os

# Import the main functions from the other project modules
from src.arxiv_scrapper import scrape_papers
from paper_ranker import rank_papers, select_top_paper
from llm_podcaster import generate_podcast_script
from src.script_to_audio import generate_podcast_audio

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

def main():
    """
    Main function to run the entire podcast generation pipeline.
    """
    logging.info("Starting the AI podcast generation pipeline.")

    # To-Do:
    # 1. Implement argument parsing with `argparse` to allow command-line options,
    #    e.g., `--test-run` to use mock data or `--schedule` to set up a cron job.

    try:
        config = load_config('./config/settings.ini')

        # --- Step 1: Scrape the latest research papers ---
        logging.info("Step 1: Scraping papers from arXiv.")
        papers = scrape_papers(config)

        if not papers:
            logging.warning("No new papers found. Exiting pipeline.")
            return

        # --- Step 2: Rank the papers for relevance ---
        logging.info(f"Step 2: Ranking {len(papers)} papers.")
        ranked_papers = rank_papers(papers, config)

        # --- Step 3: Select the top paper to feature ---
        logging.info("Step 3: Selecting the top paper.")
        selected_paper = select_top_paper(ranked_papers)

        if not selected_paper:
            logging.error("Could not select a top paper. Exiting pipeline.")
            return

        # To-Do:
        # 2. Add persistence. Save the selected paper's ID to a file or database
        #    to prevent re-running the same podcast. This is a crucial step to avoid
        #    duplicate content.

        # --- Step 4: Generate the podcast script ---
        logging.info("Step 4: Generating the podcast script.")
        podcast_script_content = generate_podcast_script(selected_paper, config)

        # The `llm_podcaster` module needs to be adapted to return a structured JSON object,
        # not just a raw string. This is a crucial next step for the pipeline to work.
        # As a placeholder, we will assume it returns a dict.

        if not podcast_script_content:
            logging.error("Failed to generate a podcast script. Exiting pipeline.")
            return

        # --- Step 4a: Save the generated script for review ---
        script_dir = "./output/scripts"
        os.makedirs(script_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        script_file_path = os.path.join(script_dir, f"script_{timestamp}.json")

        logging.info(f"Saving script to {script_file_path}")
        with open(script_file_path, "w", encoding="utf-8") as f:
            json.dump(podcast_script_content, f, indent=4)

        # --- Step 5: Generate the podcast audio ---
        logging.info("Step 5: Generating the podcast audio.")
        if generate_podcast_audio(podcast_script_content, config):
            logging.info("Pipeline completed successfully! Audio file generated.")
        else:
            logging.error("Audio generation failed. Pipeline aborted.")

    except Exception as e:
        logging.critical(f"An unhandled error occurred in the pipeline: {e}")

if __name__ == "__main__":
    main()
