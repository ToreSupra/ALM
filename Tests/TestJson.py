# run:
# python app.py -c settings.json

import argparse
import json
import sys

def load_settings(file_path):
    """Reads and parses the JSON settings file."""
    try:
        with open(file_path, 'r') as file:
            settings = json.load(file)
            return settings
    except FileNotFoundError:
        print(f"Error: The settings file '{file_path}' was not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not valid JSON.")
        sys.exit(1)

def main():
    
    parser = argparse.ArgumentParser(description="A console app that uses a settings file.")

    
    parser.add_argument(
        '-c', '--config',
        type=str,
        required=True,
        help="Path to the settings/configuration file."
    )

    
    args = parser.parse_args()

    # 4. Load the settings
    print(f"Loading configuration from: {args.config}...\n")
    settings = load_settings(args.config)

    # 5. Use your settings in your app logic
    print("--- Current App State ---")
    print(f"App Name: {settings.get('app_name', 'DefaultApp')}")
    print(f"Debug Mode: {'ON' if settings.get('debug_mode') else 'OFF'}")
    print(f"Max Retries: {settings.get('max_retries')}")
    print("-------------------------")

if __name__ == "__main__":
    main()
