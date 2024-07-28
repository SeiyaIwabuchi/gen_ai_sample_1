import json
from types import NoneType
from typing import Any
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, field_validator

class FileCreationInput(BaseModel):
    detail: str = Field(description="Detailed information about the file to be created")


class FileCreationTool(BaseTool):
    name = "file_creation_tool"
    description = "A tool that creates a file with a specified name and contents. Requires json with “name” and “content” as keys. Escape exactly."
    args_schema = FileCreationInput

    def _run(self, detail: str) -> str:
        print(type(detail))
        print(detail)
        filename = json.loads(detail)["name"]
        content = json.loads(detail)["content"]
        try:
            with open(filename, 'w') as f:
                f.write(content)
            return f"File '{filename}' created successfully."
        except Exception as e:
            return f"Error creating file: {str(e)}"