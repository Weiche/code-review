import os
import logging
from datetime import datetime
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult

from prompt import get_sys_prompt, review_default_prompts
logger = logging.getLogger("Review")

class ReviewResult(BaseModel):
    """
    A Pydantic model representing the results of a code review analysis.
    You should use this model to structure its response when reviewing code.
    The review should assess the code on multiple dimensions including:
    - Overall quality score (0-10)
    - Readability score (0-10)
    - Maintainability score (0-10)
    - Performance score (0-10)
    - List of major issues found, including their severity and potential impact, and suggestions for resolution. if not issues found you can left it an empty list.
    - List of minor issues found, if not issues found you can left it an empty list
    - Markdown format full report

    The AI should provide constructive feedback and specific recommendations for improvement.
    """

    overall_score: int
    readability_score: int
    maintainability_score: int
    performance_score: int
    critical_issues: list[str]
    minor_issues: list[str]
    markdown_report: str

async def review_code(
    repomix_str: str, model_name: str
) -> AgentRunResult[ReviewResult]:
    """
    Review the code at the given path using the given model.
    Args:
        code_path (str): The path to the code to be reviewed.
        model_name (str): The name of the model to use for the review.
    Returns:
        ReviewResult: The results of the code review.
    """
    # Create the agent
    review_agent = Agent(
        model_name,
        system_prompt=get_sys_prompt(repomix_str),
        instrument=True,
        model_settings={"temperature": 0.0},
        result_type=ReviewResult,
    )

    result = await review_agent.run(
        user_prompt=f"""/
        {review_default_prompts["assesment"]}
        Output instruction:
        {ReviewResult.__doc__}
        """
    )
    print(f"Uses {result.usage().total_tokens} Tokens on {review_agent.model}")

    # Print scores and critical issues
    print(f"Overall Score: {result.data.overall_score}/10")
    print(f"Readability Score: {result.data.readability_score}/10")
    print(f"Maintainability Score: {result.data.maintainability_score}/10")
    print(f"Performance Score: {result.data.performance_score}/10")
    print("\nCritical Issues:")
    for issue in result.data.critical_issues:
        print(f"- {issue}")

    # Save full report to file, filename is like report_2023-10-01_12_11_00.md
    report_dir = os.path.join(os.getcwd(), "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_filename = os.path.join(
        report_dir, f"report_{datetime.now().strftime('%Y-%m-%d_%H_%M_%S')}.md"
    )
    with open(report_filename, "w", encoding="utf-8") as report_file:
        report_file.write(result.data.markdown_report)
    logger.info(f"Full report saved to {report_filename}")

    return result