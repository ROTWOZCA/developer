import sys
import argparse
from smol_dev.main import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, required=True, help="Prompt for the app to be created.")
    parser.add_argument("--generate_folder_path", type=str, default="generated", help="Path of the folder for generated code.")
    parser.add_argument("--debug", type=bool, default=False, help="Enable or disable debug mode.")
    args = parser.parse_args()
    main(prompt=args.prompt, generate_folder_path=args.generate_folder_path, debug=args.debug)
