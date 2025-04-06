import logging
import os

from pydantic_ai import Agent

from mcp_manager.mcp_preset import create_mcp_servers
from prompt import get_doc_agent_sys_prompt

logger = logging.getLogger("Doc")


async def update_readme(repomix_str: str, model_name: str) -> None:
    """
    Update the README file with the analysis results.
    Args:
        repomix_str (str): The content of the repomix file.
        model_name (str): The name of the model used for the review.
    """
    mcp_servers = create_mcp_servers()
    doc_agent = Agent(
        model=model_name,
        system_prompt=get_doc_agent_sys_prompt(repomix_str),
        instrument=True,
        model_settings={"temperature": 0.0},
        mcp_servers=mcp_servers,
    )
    if os.path.exists("Readme.md"):
        with open("Readme.md", "r", encoding="utf-8") as f:
            readme_content = f.read()
            user_prompt = f"""
            Update the contents of readme file according to the new source code.
            If the old content of old readme is totally wrong, you should rewrite the readme.
            Below is the old readme contents
            {readme_content}
            """
    else:
        user_prompt = "Generate a new Readme.md"

    async with doc_agent.run_mcp_servers():
        result = await doc_agent.run(user_prompt=user_prompt)
    logger.info(f"Token usage: {result.usage().total_tokens}")
    if result.data:
        with open("Readme.md", "w", encoding="utf-8") as f:
            f.write(result.data)
