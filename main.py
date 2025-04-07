import logging
import os
import shutil
import subprocess
import sys
from plistlib import InvalidFileException

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
    try:
        ret, output = subprocess.getstatusoutput(
            ["repomix", code_path, "-o", "repomix-output.xml"], encoding="utf-8"
        )
        if ret != 0:
            logger.error(f"repomix failed with return code {ret}")
            return None

        logger.info(f"Repomix created:{output}")
        # Assuming repomix generates a file named repomix_output.txt in the code_path directory
        # Read all contents from the file
        with open("repomix-output.xml", "r", encoding="utf-8") as file:
            content = file.read()
            return content

    except Exception as e:
        logger.error(f"Failed to create repomix, {e}")
        return None


async def main():
    try:
        if not shutil.which("repomix"):
            raise ModuleNotFoundError("Need repomix to work")
        cfg = load_config()

        if cfg is None:
            raise InvalidFileException("Invalid config.json file or file not exist")
        
        default_model: str = cfg.default_model
        code_path = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
        if not os.path.exists(code_path):
            raise FileNotFoundError("Code path not exist")
        # MCP Servers
        # mcp_servers: list[MCPServer] = create_mcp_servers()

    except Exception as e:
        logger.error(f"Error occured while initializing: {e}")
        exit(1)

    try:
        # Change the working directory to the code path
        os.chdir(code_path)
        logger.info(f"Current working directory: {os.getcwd()}")

        # Generate repomix
        repomix_content = await generate_repomix(code_path=code_path)

        if not repomix_content:
            raise ValueError("Failed to generate repomix")

        await review_code(repomix_str=repomix_content, model_name=default_model)
        await update_readme(repomix_str=repomix_content, model_name=default_model)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
