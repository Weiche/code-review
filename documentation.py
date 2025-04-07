import logging
import os

from pydantic_ai import Agent

from prompt import get_doc_agent_sys_prompt

logger = logging.getLogger("Doc")


async def update_readme(repomix_str: str, model_name: str, code_path: str) -> None:
    """
    Update the README file with the analysis results.
    Args:
        repomix_str (str): The content of the repomix file.
        model_name (str): The name of the model used for the review.
    """
    doc_agent = Agent(
        model=model_name,
        system_prompt=get_doc_agent_sys_prompt(repomix_str),
        instrument=True,
        model_settings={"temperature": 0.0},
    )
    readme_path = os.path.join(code_path, "Readme.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()
            user_prompt = f"""
            Update the contents of readme file according to the new source code.
            If the old content of old readme is totally wrong, you should rewrite the readme.
            Below is the old readme contents
            {readme_content}
            """
    else:
        user_prompt = "Generate a new Readme.md"

    result = await doc_agent.run(user_prompt=user_prompt)
    logger.info(f"Token usage: {result.usage().total_tokens}")
    if result.data:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(result.data)
