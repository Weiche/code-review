from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from pydantic_ai.mcp import MCPServer, MCPServerHTTP, MCPServerStdio
from jsoncomment import JsonComment


class StdioConfig(BaseModel):
    type: str = "stdio"
    command: str
    args: List[str]


class HTTPConfig(BaseModel):
    type: str = "http"
    host: str
    port: int
    api_version: str = "v1"
    timeout: Optional[int] = 30
    max_retries: Optional[int] = 3


MCPConfig = StdioConfig | HTTPConfig


class Config(BaseModel):
    default_model: str
    mcp_servers: Dict[str, MCPConfig]
    logging: Dict[str, Any]


def load_config() -> Config:
    config_path = Path(__file__).parent.parent / "config.json"
    try:
        parser = JsonComment()
        config_data = parser.loadf(config_path)
        return Config(**config_data)
    except Exception as e:
        raise RuntimeError(f"Failed to load config: {str(e)}")


def create_mcp_servers() -> List[MCPServer]:
    config = load_config()
    servers: List[MCPServer] = []

    for _, server_config in config.mcp_servers.items():
        if server_config.type == "stdio":
            servers.append(
                MCPServerStdio(server_config.command, args=server_config.args)
            )
        elif server_config.type == "http":
            servers.append(
                MCPServerHTTP(
                    host=server_config.host,
                    port=server_config.port,
                    api_version=server_config.api_version,
                    timeout=server_config.timeout,
                    max_retries=server_config.max_retries,
                )
            )

    return servers


if __name__ == "__main__":
    mcp_servers = create_mcp_servers()
    print(mcp_servers)
