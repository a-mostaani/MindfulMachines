import configparser
import logging
import json
import requests
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.llms.llama_cpp.llama_utils import (
    messages_to_prompt,
    completion_to_prompt,
)

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

def generate_podcast_script(paper, config):
    """
    Generates a podcast script based on a research paper using an LLM.

    Args:
        paper (dict): The dictionary for the selected research paper.
        config (configparser.ConfigParser): The loaded configuration object.

    Returns:
        str: The generated podcast script or an empty string if it fails.
    """
    logging.info(f"Generating podcast script for paper: '{paper['title']}'")

    # To-Do:
    # 1. Ensure Llama 3 is installed and configured. This will involve installing
    #    llama-cpp-python and downloading the model weights. The `model_path`
    #    in your config file should point to your local GGUF model file.

    # 2. To-Do: Refine the prompt to improve the script generation.
    #    You may need to experiment with different phrasings to get the
    #    desired conversational tone and speaker roles.

    # 3. To-Do: Consider using a `PromptTemplate` from llama_index to
    #    manage the prompt more cleanly.

    llm = LlamaCPP(
        model_url=None, # Not needed when using model_path
        model_path=config.get('llm', 'model_path'),
        temperature=0.7,
        max_new_tokens=2048,
        # Set a tokenizer and stop tokens if needed
        messages_to_prompt=messages_to_prompt,
        completion_to_prompt=completion_to_prompt,
        verbose=True,
    )

    # Combine title, authors, and summary into a single document for the LLM
    text_content = (
        f"Title: {paper['title']}\n"
        f"Authors: {', '.join(paper['authors'])}\n"
        f"Abstract: {paper['summary']}"
    )

    # Use a temporary file to hold the content for SimpleDirectoryReader
    temp_file_path = "temp_paper_content.txt"
    try:
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)

        documents = SimpleDirectoryReader(input_files=[temp_file_path]).load_data()

        # Create an index from the document
        index = VectorStoreIndex.from_documents(documents)

        # Create a query engine
        query_engine = index.as_query_engine(llm=llm)

        # Generate the script
        prompt = (
            "You are a podcast script generator. The podcast is a discussion between an "
            "ML Expert, a Neuroscientist, and a Psychologist. Your task is to generate "
            "a compelling, conversational script based on the provided research paper."
            "\n\n"
            "The script should be a discussion between:\n"
            "- A friendly ML expert, explaining the technical details.\n"
            "- An enthusiastic Neuroscientist, connecting the findings to brain function.\n"
            "- A pragmatic Psychologist, discussing the human implications."
        )

        response = query_engine.query(prompt)
        generated_text = str(response)

        # To-Do:
        # 4. Add post-processing logic to refine the generated script.
        #    For example, you might want to parse it if the LLM is instructed to
        #    output a specific format (e.g., JSON with speaker labels).

        return generated_text

    except Exception as e:
        logging.error(f"Failed to generate podcast script: {e}")
        return ""
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def main():
    """
    Main function to run the podcast generation process.
    """
    # This is a placeholder for how it would receive the selected paper.
    # In a real pipeline, `main.py` would pass this object directly.

    config = load_config('./config/settings.ini')

    # Mock paper object for demonstration
    mock_paper = {
        'title': 'Anatomical and Functional Connectivity of the Entorhinal Cortex',
        'authors': ['John Doe', 'Jane Smith'],
        'summary': 'This paper investigates the complex connections within the entorhinal cortex, a brain region critical for memory.',
        'link': 'http://arxiv.org/abs/1234.5678v1'
    }

    podcast_script = generate_podcast_script(mock_paper, config)

    if podcast_script:
        logging.info("Podcast script generated successfully!")
        # To-Do:
        # 5. Save the final script to a Markdown or text file in the `output/` directory.
        #    This makes the script easy to read and edit.
        print("\n--- Generated Podcast Script ---\n")
        print(podcast_script)
    else:
        logging.error("Could not generate a podcast script.")

if __name__ == "__main__":
    main()
