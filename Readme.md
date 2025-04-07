# AI-Powered Code Review and Documentation Assistant

## Description

This project provides a command-line tool that leverages Large Language Models (LLMs) via the `pydantic-ai` library to perform automated code reviews and generate project documentation (README files). It uses `repomix` to package the target codebase into a single context file for the LLM and interacts with Model Context Protocol (MCP) servers for extended capabilities like file system operations or sequential thinking assistance during documentation generation.

The tool analyzes a given codebase, provides quality scores (overall, readability, maintainability, performance), identifies critical and minor issues, and generates a detailed markdown report. It can also generate or update a `README.md` file based on the current state of the codebase.

## Features

*   Automated code review using LLMs via `pydantic-ai`.
*   Generates scores for overall quality, readability, maintainability, and performance.
*   Identifies critical and minor issues with suggestions.
*   Outputs detailed review reports in Markdown format.
*   Generates or updates project `README.md` files based on the codebase using an LLM agent potentially enhanced with MCP servers.
*   Uses `repomix` to package repositories into a single XML file for analysis.
*   Configurable LLM model (`default_model` in `config.json`).
*   Configurable Model Context Protocol (MCP) server integration (`mcp_servers` in `config.json`) for enhanced agent capabilities (e.g., file system access, sequential thinking).
*   Supports logging via `logfire` (requires `LOGFIRE_KEY` environment variable).

## Installation

1.  **Prerequisites:**
    *   Python 3.12+ (as specified in `pyproject.toml`. `.python-version` suggests 3.13 for development).
    *   `pip` (Python package installer).
    *   `repomix`: Install globally or ensure it's in your PATH. Installation instructions: [repomix GitHub](https://github.com/smol-ai/repomix) (Typically `pip install repomix`).
    *   Node.js and `npx`: Required if using the default `stdio` MCP servers specified in `config.json` (e.g., `@wonderwhy-er/desktop-commander`, `@modelcontextprotocol/server-sequential-thinking`).

2.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

3.  **Install Python dependencies:**

    ```bash
    pip install .
    # or using poetry/pdm if preferred
    # poetry install
    # pdm install
    ```

4.  **Environment Variables:**
    *   Set the `LOGFIRE_KEY` environment variable if you want to use Logfire for enhanced logging and observability. Obtain a key from [Logfire](https://logfire.pydantic.dev/).

      ```bash
      export LOGFIRE_KEY="your_logfire_token"
      ```

    *   Ensure any necessary API keys for the chosen LLM (specified in `config.json`) are available in your environment (e.g., `GOOGLE_API_KEY` if using a Google model).

5.  **Configuration:**
    *   Review and potentially modify the `config.json` file to set your preferred LLM model, configure MCP servers, and adjust logging settings. See the [Configuration](#configuration) section below.

## Usage

Run the main script (`main.py`) from your terminal, providing the path to the codebase you want to analyze as an argument. If no path is provided, it defaults to the current working directory (`.`).

```bash
python main.py [path_to_your_codebase]
```

**Example:**

To analyze a project located at `../my-other-project`:

```bash
python main.py ../my-other-project
```

To analyze the project where this tool itself resides:

```bash
python main.py .
# or simply
python main.py
```

The script will perform the following steps:

1.  **Run `repomix`:** Executes the `repomix` command on the target codebase path (`[path_to_your_codebase]`). This generates a `repomix-output.xml` file in the *current working directory* (where you run the `python main.py` command), containing a packed representation of the target repository.
2.  **Perform Code Review:**
    *   Uses the configured LLM (`default_model` in `config.json`) via `pydantic-ai` to analyze the code represented in `repomix-output.xml`.
    *   Prints overall, readability, maintainability, and performance scores to the console.
    *   Prints critical issues identified during the review.
    *   Saves a detailed Markdown report (`ReviewResult.markdown_report`) to the `reports/` directory within the *current working directory* (e.g., `./reports/report_YYYY-MM-DD_HH_MM_SS.md`).
3.  **Generate/Update README:**
    *   Uses the configured LLM and any configured MCP servers (`mcp_servers` in `config.json`) via `pydantic-ai` to generate or update the `README.md` file.
    *   Reads the existing `Readme.md` from the *target codebase path* (`[path_to_your_codebase]/Readme.md`) if it exists, and prompts the LLM to update it based on the current codebase (`repomix-output.xml`). If no `Readme.md` exists, it prompts the LLM to generate a new one.
    *   Writes the generated/updated content back to `[path_to_your_codebase]/Readme.md`.

## Configuration

Configuration is managed through the `config.json` file in the project root.

```json
{
    // Specify the LLM model identifier for pydantic-ai
    "default_model": "google-gla:gemini-2.5-pro-exp-03-25",
    // Define Model Context Protocol servers for extended agent capabilities
    "mcp_servers": {
        // Example: Server for file system/command execution via stdio
        "desktop-commander" : {
            "type": "stdio", // Communication type (stdio or http)
            "command": "npx", // Command to start the server process
            "args": [         // Arguments for the command
                "-y",
                "@wonderwhy-er/desktop-commander@latest"
            ]
            // "env": { "VAR": "value" } // Optional environment variables for the server process
        },
        // Example: Server for structured thinking processes via stdio
        "sequential-thinking" : {
            "type": "stdio",
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-sequential-thinking"
            ]
        }
        // Example HTTP server configuration (requires defining HTTPConfig in config_manager/config.py)
        // "http_server_example": {
        //     "type": "http",
        //     "url": "http://localhost:8000/sse" // Example URL
        // }
    },
    // Basic logging configuration (used by Python's logging module)
    "logging": {
        "level": "INFO", // Logging level (e.g., DEBUG, INFO, WARNING, ERROR)
        "file": "mcp.log" // Log file name (created relative to the execution directory)
    }
}
```

*   **`default_model`**: The identifier for the LLM to be used by `pydantic-ai`. Ensure this model is accessible via your environment/API keys (e.g., set `GOOGLE_API_KEY` for Google models).
*   **`mcp_servers`**: A dictionary defining MCP servers. Each key is a user-defined name for the server (used internally), and the value is an object defining its configuration:
    *   **`type`**: Must be either `"stdio"` or `"http"`. This determines how the application communicates with the MCP server.
    *   **`stdio` type configuration (`StdioConfig` in `config_manager/config.py`):**
        *   `command`: The executable command to start the server (e.g., `npx`, `python`).
        *   `args`: A list of string arguments to pass to the command.
        *   `env` (Optional): A dictionary of environment variables to set for the server process.
    *   **`http` type configuration (`HTTPConfig` in `config_manager/config.py`):**
        *   `url`: The full URL of the MCP server endpoint (must be a valid `HttpUrl`, e.g., `"http://localhost:8000"` or `"http://example.com/mcp"`).
*   **`logging`**: Basic Python logging configuration.
    *   `level`: Minimum logging level to capture (e.g., `"INFO"`, `"DEBUG"`).
    *   `file`: Name of the log file where logs will be written (created in the execution directory).

**Note on `npx -y ...@latest`:** Using `@latest` for MCP servers (like in the default `config.json`) fetches the newest version on each run. While convenient for testing, for stability and security in production environments, consider pinning versions (e.g., `@wonderwhy-er/desktop-commander@1.0.0`) or managing these Node.js dependencies locally within the project.

## API Documentation

This tool does not expose a direct HTTP API for external consumption. It interacts with external services and protocols:

*   **LLM APIs:** Interaction is handled implicitly by the `pydantic-ai` library based on the `default_model` configured in `config.json`. Ensure necessary API keys (e.g., Google AI, OpenAI) are available in your environment as required by the chosen model provider.
*   **MCP Servers:** The tool communicates with MCP servers as defined in `config.json`. These servers adhere to the [Model Context Protocol Specification](https://github.com/modelcontextprotocol/specification) and provide specific tools/capabilities to the LLM agent during tasks like documentation generation (e.g., file system access via `desktop-commander`, structured thinking via `sequential-thinking`). The available tools depend entirely on the specific MCP servers configured and running.

## Project Structure

```
.
├── .gitignore          # Specifies intentionally untracked files by Git
├── .python-version     # Specifies the intended Python version (3.13) for tools like pyenv
├── config.json         # Configuration file for models, MCP servers, logging
├── config_manager/
│   └── config.py       # Loads config.json, validates config, creates MCP server instances
├── documentation.py    # Contains logic for generating/updating README.md using an LLM agent
├── main.py             # Main script entry point: orchestrates repomix, review, and documentation
├── prompt.py           # Functions to generate system prompts for the LLM agents (review & docs)
├── pyproject.toml      # Project metadata and dependencies (PEP 621 format)
├── Readme.md           # This file (potentially generated/updated by the tool itself)
├── reports/            # Directory where generated review reports are saved (created in execution dir)
└── review.py           # Contains logic for code review using an LLM agent and ReviewResult model
```

*   `reports/`: This directory is created in the directory where `main.py` is executed, *not* within the target codebase being analyzed. It stores the Markdown reports generated by the code review process.

## Dependencies

*   **Python:**
    *   `pydantic-ai[logfire]`: For LLM interaction, agent creation, and optional Logfire integration.
    *   `jsoncomment`: For parsing `config.json` which may contain comments.
    *   (See `pyproject.toml` for specific versions)
*   **External Tools:**
    *   `repomix`: Required for packaging the target repository. Must be installed and in PATH.
    *   `node` / `npx`: Required *only* if using `stdio` MCP servers that are run via `npx` (as per the default `config.json`).

## Contribution Guidelines

Contributions are welcome! Please follow these general steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix (`git checkout -b feature/your-feature-name`).
3.  Make your changes, adhering to Python best practices.
4.  Ensure code quality (consider using linters/formatters like Black, Ruff, or Flake8).
5.  Add tests for new functionality or bug fixes if applicable.
6.  Update documentation (`Readme.md`) if your changes affect usage, configuration, or features.
7.  Commit your changes with clear messages (`git commit -am 'Add some feature'`).
8.  Push your branch to your fork (`git push origin feature/your-feature-name`).
9.  Create a Pull Request against the main repository, providing a clear description of your changes.

## License

This project is intended to be licensed under the MIT License. However, a `LICENSE` file is not currently present in the repository. If you plan to use, distribute, or contribute to this code, it is recommended to add a file named `LICENSE` containing the full text of the MIT License:

```
MIT License

Copyright (c) [Year] [Copyright Holder]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Replace `[Year]` and `[Copyright Holder]` accordingly.