import sys
import time
import os

from smol_dev.prompts import plan, specify_file_paths, generate_code_sync
from smol_dev.utils import generate_folder, write_file
import argparse

# تعيين base_url لـ Groq
os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"

defaultmodel = "llama3-70b-8192"

def main(prompt, generate_folder_path="generated", debug=False, model: str = defaultmodel):
    generate_folder(generate_folder_path)

    if debug:
        print("--------shared_deps---------")
    with open(f"{generate_folder_path}/shared_deps.md", "wb") as f:
        start_time = time.time()
        def stream_handler(chunk):
            f.write(chunk)
            if debug:
                end_time = time.time()
                sys.stdout.write("\r \033[93mChars streamed\033[0m: {}. \033[93mChars per second\033[0m: {:.2f}".format(stream_handler.count, stream_handler.count / (end_time - start_time)))
                sys.stdout.flush()
                stream_handler.count += len(chunk)
        stream_handler.count = 0
        shared_deps = plan(prompt, stream_handler, model=model)
    if debug:
        print(shared_deps)
    write_file(f"{generate_folder_path}/shared_deps.md", shared_deps)

    if debug:
        print("--------specify_filePaths---------")
    file_paths = specify_file_paths(prompt, shared_deps, model=model)
    if debug:
        print(file_paths)

    for file_path in file_paths:
        file_path = f"{generate_folder_path}/{file_path}"
        if debug:
            print(f"--------generate_code: {file_path} ---------")
        start_time = time.time()
        def stream_handler(chunk):
            if debug:
                end_time = time.time()
                sys.stdout.write("\r \033[93mChars streamed\033[0m: {}. \033[93mChars per second\033[0m: {:.2f}".format(stream_handler.count, stream_handler.count / (end_time - start_time)))
                sys.stdout.flush()
                stream_handler.count += len(chunk)
        stream_handler.count = 0
        code = generate_code_sync(prompt, shared_deps, file_path, stream_handler, model=model)
        if debug:
            print(code)
        write_file(file_path, code)

    print("--------smol dev done!---------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, required=True, help="Prompt for the app to be created.")
    parser.add_argument("--generate_folder_path", type=str, default="generated", help="Path of the folder for generated code.")
    parser.add_argument("--debug", type=bool, default=False, help="Enable or disable debug mode.")
    args = parser.parse_args()
    main(prompt=args.prompt, generate_folder_path=args.generate_folder_path, debug=args.debug)
