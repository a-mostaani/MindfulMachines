import configparser
import logging
import json
import base64
import wave
import requests
import os

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

def pcm_to_wav(pcm_data, sample_rate, channels=1, sample_width=2):
    """
    Converts raw PCM audio data to a WAV byte string.

    Args:
        pcm_data (bytes): The raw PCM audio data.
        sample_rate (int): The sample rate of the audio (e.g., 24000).
        channels (int): The number of audio channels.
        sample_width (int): The sample width in bytes (e.g., 2 for 16-bit).

    Returns:
        bytes: A byte string containing the WAV file data.
    """
    with wave.open('temp.wav', 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)

    with open('temp.wav', 'rb') as f:
        wav_data = f.read()

    os.remove('temp.wav')
    return wav_data

def generate_podcast_audio(script, config):
    """
    Generates a multi-speaker audio file from a structured script using a TTS API.

    Args:
        script (dict): A structured script containing dialogue and speaker info.
        config (configparser.ConfigParser): The loaded configuration object.

    Returns:
        bool: True if audio generation is successful, False otherwise.
    """
    logging.info("Starting audio generation...")

    tts_api_key = config.get('api_keys', 'tts_api_key')
    tts_api_url = config.get('tts', 'api_url')

    # To-Do:
    # 1. Map speaker names from the script to specific voice names from the API.
    #    You can store this mapping in the settings.ini file.
    speaker_voice_mapping = {
        config.get('podcast', 'expert_1'): 'Zephyr',
        config.get('podcast', 'expert_2'): 'Puck',
        config.get('podcast', 'expert_3'): 'Kore',
    }

    # To-Do:
    # 2. Build the multi-speaker payload for the TTS API. This will involve
    #    iterating through the script to create a single text string with speaker labels,
    #    and then defining the voice for each speaker in the `multiSpeakerVoiceConfig`.

    # Placeholder payload for demonstration
    payload = {
        "contents": [{
            "parts": [{"text": "Hello, everyone, and welcome to Mindful Machines."}]
        }],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "multiSpeakerVoiceConfig": {
                    "speakerVoiceConfigs": [
                        {"speaker": "expert_1", "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": speaker_voice_mapping[config.get('podcast', 'expert_1')]}}},
                        {"speaker": "expert_2", "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": speaker_voice_mapping[config.get('podcast', 'expert_2')]}}},
                        {"speaker": "expert_3", "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": speaker_voice_mapping[config.get('podcast', 'expert_3')]}}}
                    ]
                }
            }
        },
        "model": "gemini-2.5-flash-preview-tts"
    }

    try:
        response = requests.post(
            f"{tts_api_url}?key={tts_api_key}",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()

        audio_data = response.json()['candidates'][0]['content']['parts'][0]['inlineData']['data']
        audio_mime_type = response.json()['candidates'][0]['content']['parts'][0]['inlineData']['mimeType']

        # To-Do:
        # 3. Extract the sample rate from the mime type string.
        sample_rate = 24000 # Placeholder

        pcm_data = base64.b64decode(audio_data)
        wav_data = pcm_to_wav(pcm_data, sample_rate)

        # To-Do:
        # 4. Save the generated WAV file to the 'output/audio' directory.
        #    Make sure the directory exists first.
        output_dir = "output/audio"
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, "podcast_episode.wav")
        with open(output_file, 'wb') as f:
            f.write(wav_data)

        logging.info(f"Audio file saved successfully to {output_file}")
        return True

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to generate audio: {e}")
        return False
    except (KeyError, IndexError) as e:
        logging.error(f"Unexpected API response format: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return False

def main():
    """
    Main function to run the TTS generation process.
    """
    config = load_config('./config/settings.ini')

    # Mock script data for demonstration
    mock_script = {
        "title": "A new paper on memory networks",
        "dialogue": [
            {"speaker": "ML Expert", "text": "This new paper proposes a novel memory network architecture."},
            {"speaker": "Neuroscientist", "text": "That's fascinating. I wonder how this relates to hippocampal function."},
            {"speaker": "Psychologist", "text": "And what are the implications for human learning and memory?"}
        ]
    }

    if generate_podcast_audio(mock_script, config):
        logging.info("TTS generation process completed.")
    else:
        logging.error("TTS generation process failed.")

if __name__ == "__main__":
    main()
