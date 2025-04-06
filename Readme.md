# AI-Powered Code Review and Documentation Assistant

## Description

This project provides a command-line tool that leverages Large Language Models (LLMs) via the `pydantic-ai` library to perform automated code reviews and generate project documentation (README files). It uses `repomix` to package the target codebase into a single context file for the LLM and interacts with Model Context Protocol (MCP) servers for extended capabilities like file system operations or sequential thinking assistance during documentation generation.

The tool analyzes a given codebase, provides quality scores (overall, readability, maintainability, performance), identifies critical and minor issues, and generates a detailed markdown report. It can also generate or update a `README.md` file based on the current state of the codebase.

## Features

*   Automated code review using LLMs.
*   Generates scores for overall quality, readability, maintainability, and performance.
*   Identifies critical and minor issues with suggestions.
*   Outputs detailed review reports in Markdown format.
*   Generates or updates project `README.md` files based on the codebase.
*   Uses `repomix` to package repositories for analysis.
*   Configurable LLM model and MCP server integration.
*   Supports logging via `logfire`.

## Installation

1.  **Prerequisites:**
    *   Python 3.12+ (as specified in `.python-version` and `pyproject.toml`)
    *   `pip` (Python package installer)
    *   `repomix`: Install globally or ensure it's in your PATH. Installation instructions: [repomix GitHub](https://github.com/smol-ai/repomix) (Typically `pip install repomix`)
    *   Node.js and `npx`: Required if using the default `stdio` MCP servers specified in `config.json`.

2.  **Clone the repository:**
    ```

bash
    git clone <repository-url>
    cd <repository-directory>
    

```

3.  **Install Python dependencies:**
    ```

bash
    pip install .
    # or using poetry/pdm if preferred
    # poetry install
    # pdm install
    

```

4.  **Environment Variables:**
    *   Set the `LOGFIRE_KEY` environment variable if you want to use Logfire for enhanced logging and observability. Obtain a key from [Logfire](https://logfire.pydantic.dev/).
      ```

bash
      export LOGFIRE_KEY="your_logfire_token"
      

```

5.  **Configuration:**
    *   Review and potentially modify the `config.json` file to set your preferred LLM model, configure MCP servers, and adjust logging settings. See the [Configuration](#configuration) section below.

## Usage

Run the main script from your terminal, providing the path to the codebase you want to analyze as an argument. If no path is provided, it defaults to the current working directory.

```

bash
python main.py [path_to_your_codebase]


```

**Example:**

To analyze a project located at `../my-project`:

```

bash
python main.py ../my-project


```

To analyze the project where the tool itself resides:

```

bash
python main.py .
# or simply
python main.py


```

The script will:

1.  Change the working directory to the target codebase path.
2.  Run `repomix` to generate a `repomix-output.xml` file (in the target directory).
3.  Perform code review using the configured LLM.
    *   Print scores and critical issues to the console.
    *   Save a detailed Markdown report to the `reports/` directory within the target codebase path (e.g., `../my-project/reports/report_YYYY-MM-DD_HH_MM_SS.md`).
4.  Generate or update the `README.md` file in the target codebase path using the configured LLM and MCP servers.

## Configuration

Configuration is managed through the `config.json` file in the project root.

```

json
{
    "default_model": "google-gla:gemini-2.5-pro-exp-03-25", // Specify the LLM model identifier for pydantic-ai
    "mcp_servers": { // Define Model Context Protocol servers for extended agent capabilities
        "desktop-commander" : { // Example: Server for file system/command execution
            "type": "stdio", // Communication type (stdio or http)
            "command": "npx", // Command to start the server
            "args": [         // Arguments for the command
                "-y",
                "@wonderwhy-er/desktop-commander@latest"
            ]
        },
        // Example HTTP server configuration (commented out)
        // {
        //     "type": "http",
        //     "host": "localhost",
        //     "port": 5000,
        //     "api_version": "v1",
        //     "timeout": 30,
        //     "max_retries": 3
        // },
        "sequential-thinking" : { // Example: Server for structured thinking processes
            "type": "stdio",
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-sequential-thinking"
            ]
        }
    },
    "logging": { // Logging configuration
        "level": "INFO", // Logging level (e.g., DEBUG, INFO, WARNING, ERROR)
        "file": "mcp.log" // Log file name (relative to the execution directory)
    }
}


```

*   **`default_model`**: The identifier for the LLM to be used by `pydantic-ai`. Ensure this model is accessible via your environment/API keys.
*   **`mcp_servers`**: A dictionary defining MCP servers. Each key is a name for the server (used internally), and the value is an object defining its configuration:
    *   **`type`**: `stdio` or `http`.
    *   **`stdio` type**:
        *   `command`: The executable to run (e.g., `npx`, `python`).
        *   `args`: A list of arguments for the command.
    *   **`http` type**:
        *   `host`: Hostname or IP address of the server.
        *   `port`: Port number.
        *   `api_version`: API version (default: `v1`).
        *   `timeout`: Request timeout in seconds (default: 30).
        *   `max_retries`: Maximum number of retries on failure (default: 3).
*   **`logging`**: Standard Python logging configuration.
    *   `level`: Minimum logging level to capture.
    *   `file`: Name of the log file.

**Note on `npx -y ...@latest`:** Using `@latest` for MCP servers fetches the newest version on each run. For stability and security, consider pinning versions (e.g., `@wonderwhy-er/desktop-commander@1.0.0`) or managing these Node.js dependencies locally.

## API Documentation

This tool does not expose a direct HTTP API for external consumption. It interacts with:

*   **LLM APIs:** Implicitly via the `pydantic-ai` library based on the `default_model` configured. Ensure necessary API keys (e.g., OpenAI, Google AI) are available in your environment if required by the chosen model.
*   **MCP Servers:** As defined in `config.json`. These servers follow the [Model Context Protocol](https://github.com/modelcontextprotocol/specification) and provide specific tools/capabilities to the LLM agent (e.g., file system access, command execution, structured thinking).

## Project Structure

```


.
├── .gitignore          # Specifies intentionally untracked files
├── .python-version     # Specifies the intended Python version (e.g., for pyenv)
├── config.json         # Configuration file for models, MCP servers, logging
├── main.py             # Main script entry point
├── mcp_manager/        # Code related to MCP server management
│   └── mcp_preset.py   # Functions to load config and create MCP server instances
├── prompt.py           # Functions to generate system prompts for the LLM
├── prompt_preset.py    # Default user prompt components
├── pyproject.toml      # Project metadata and dependencies (PEP 621)
├── reports/            # Directory where generated review reports are saved (created in the target repo)
└── README.md           # This file (potentially generated/updated by the tool)


```

## Dependencies

*   **Python:** `pydantic-ai[logfire]`, `jsoncomment` (see `pyproject.toml`)
*   **External Tools:** `repomix`, `node`/`npx` (if using default stdio MCP servers)

## Contribution Guidelines

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Ensure code quality (linting, formatting).
5.  Write tests for new features or bug fixes if applicable.
6.  Commit your changes (`git commit -am 'Add some feature'`).
7.  Push to the branch (`git push origin feature/your-feature-name`).
8.  Create a new Pull Request.

Please provide a clear description of your changes in the Pull Request.

## License

This project is licensed under the MIT License. See the LICENSE file for details (Note: A LICENSE file is not present in the provided codebase structure, consider adding one).
