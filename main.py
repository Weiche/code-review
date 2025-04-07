import logging
import logging.config
import os
import shutil
import subprocess
import sys

import logfire

from config_manager.config import load_config
from documentation import update_readme
from review import review_code

logfire.configure(token=os.getenv("LOGFIRE_KEY"))
logger = logging.getLogger("CodeAnalyze")

async def generate_repomix(code_path: str) -> str | None:
    """
    Generate a repomix file for the given code path.
    Args:
        code_path (str): The path to the code directory.
    Returns:
        str | None: The content of the repomix file or None if an error occurred.
    """
    out_path = os.path.join(os.getcwd(), "repomix-output.xml")
    repomix_exe = shutil.which("repomix")
    if repomix_exe is None:
        return None
    
    subprocess.run(
        [repomix_exe, code_path, "-o", out_path], 
        stdout=sys.stdout,
        stderr=sys.stderr,
        check=True,
        encoding="utf-8"
    )

    # Read all contents from the file
    with open(out_path, "r", encoding="utf-8") as file:
        content = file.read()
        return content

async def main():
    try:
        if not shutil.which("repomix"):
            raise ModuleNotFoundError("Need repomix to work")
        cfg = load_config()

        if cfg is None:
            raise FileNotFoundError("Invalid config.json file or file not exist")
        
        default_model: str = cfg.default_model
        code_path = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
        if not os.path.exists(code_path):
            raise FileNotFoundError("Code path not exist")

    except FileNotFoundError as e:
        logger.error(f"Error occured while initializing: {e}")
        exit(1)

    try:
        # Generate repomix
        repomix_content = await generate_repomix(code_path=code_path)

        if not repomix_content:
            raise ValueError("Failed to generate repomix")

        await review_code(repomix_str=repomix_content, model_name=default_model)
        await update_readme(repomix_str=repomix_content, model_name=default_model, code_path=code_path)
    except subprocess.CalledProcessError as e:
        logger.error(f"Repomix subprocess failed: \n {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e


if __name__ == "__main__":
    import asyncio
    
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
