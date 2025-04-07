from pathlib import Path
from plistlib import InvalidFileException
from typing import Any, Dict, List, Optional

from jsoncomment import JsonComment
from pydantic import BaseModel, HttpUrl
from pydantic_ai.mcp import MCPServer, MCPServerHTTP, MCPServerStdio
from pydantic_settings import BaseSettings


class StdioConfig(BaseModel):
    type: str = "stdio"
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None


class HTTPConfig(BaseModel):
    type: str = "http"
    url: HttpUrl


MCPConfig = StdioConfig | HTTPConfig


class Config(BaseSettings):
    default_model: str
    mcp_servers: Dict[str, Any]
    logging: Dict[str, Any]

def load_config() -> Config | None:
    config_path = Path(__file__).parent.parent / "config.json"
    try:
        parser = JsonComment()
        config_data: dict[str, Any] | None = parser.loadf(config_path)
        if config_data is not None:
            return Config(**config_data)

    except Exception as e:
        raise RuntimeError(f"Failed to load config: {str(e)}")


def create_mcp_servers() -> List[MCPServer]:
    config = load_config()
    servers: List[MCPServer] = []
    if config is None:
        raise InvalidFileException("File is not parsable")

    for _, server_config in config.mcp_servers.items():
        if server_config.get("command", False):
            stdio_config = StdioConfig(**server_config)
            servers.append(
                MCPServerStdio(
                    command=stdio_config.command,
                    args=stdio_config.args,
                    env=stdio_config.env,
                )
            )
        elif server_config.get("url", False):
            http_config = HTTPConfig(**server_config)
            servers.append(
                MCPServerHTTP(
                    url= str(http_config.url)
                )
            )

    return servers


if __name__ == "__main__":
    mcp_servers = create_mcp_servers()
    print(mcp_servers)
