from pathlib import Path
from typing import Literal, Any
import ast


class Snippet:

    def __init__(
        self,
        file_path: str,
        line_start: int,
        code: str,
        type: Literal["function", "class", "import", "global variable", "unknown"],
        name: str = "",
        line_end: int | None = None,
        docstring: str | None = None,
    ) -> None:
        self.file_path = file_path
        self.line_start = line_start
        self.line_end = line_end or self.line_start
        self.code = code
        self.type = type
        self.name = name
        self.docstring = docstring or ""

    @property
    def id(self) -> str:
        return f"{self.file_path}:{self.line_start}"

    def get_embedding_text(self) -> str:
        """
        Returns a text representation of the snippet for embedding.
        This includes the type, name, and code.
        """
        return f"code: {self.code}, filename: {Path(self.file_path).stem} type: {self.type}, {'name: ' + self.name if self.name else ''}, {'docstring: ' + self.docstring if self.docstring else ''}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "code": self.code,
            "type": self.type,
            "name": self.name,
            "docstring": self.docstring,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Snippet":
        return cls(
            file_path=data.get("file_path", ""),
            line_start=data.get("line_start", 0),
            line_end=data.get("line_end", 0),
            code=data.get("code", ""),
            type=data.get("type", "unknown"),
            name=data.get("name", ""),
            docstring=data.get("docstring", ""),
        )

    def __repr__(self) -> str:
        return f"Snippet({self.file_path}:{self.line_start}-{self.line_end}, type={self.type}, name={self.name})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Snippet):
            return False
        return (
            self.file_path == other.file_path
            and self.line_start == other.line_start
            and self.line_end == other.line_end
            and self.code == other.code
        )


def extract_import(node: ast.Import | ast.ImportFrom, file_path: str) -> Snippet:
    import_str = ast.unparse(node)
    return Snippet(
        file_path=file_path,
        line_start=node.lineno,
        line_end=node.end_lineno,
        code=import_str,
        type="import",
    )


def extract_global_variables(node: ast.Assign, file_path: str) -> list[Snippet]:

    var_names = [target.id for target in node.targets if isinstance(target, ast.Name)]
    snippets = []
    for var in var_names:
        snippets.append(
            Snippet(
                file_path=file_path,
                line_start=node.lineno,
                line_end=node.end_lineno,
                code=ast.unparse(node),
                type="global variable",
                name=var,
            )
        )
    return snippets


def extract_class(node: ast.ClassDef, file_path: str) -> Snippet:
    return Snippet(
        file_path=file_path,
        line_start=node.lineno,
        line_end=node.end_lineno,
        code=ast.unparse(node),
        type="class",
        name=node.name,
        docstring=ast.get_docstring(node),
    )


def extract_function(node: ast.FunctionDef, file_path: str) -> Snippet:

    return Snippet(
        file_path=file_path,
        line_start=node.lineno,
        line_end=node.end_lineno,
        code=ast.unparse(node),
        type="function",
        name=node.name,
        docstring=ast.get_docstring(node),
    )


def extract_snippets(file_path: str, content: str) -> list:
    tree = ast.parse(content)
    snippets = []

    for node in tree.body:

        if isinstance(node, (ast.Import, ast.ImportFrom)):
            snippets.append(extract_import(node, file_path))

        elif isinstance(node, ast.Assign):
            snippets.extend(extract_global_variables(node, file_path))

    for node in ast.walk(tree):

        if isinstance(node, ast.ClassDef):

            snippets.append(extract_class(node, file_path))

        elif isinstance(node, ast.FunctionDef):
            snippet = extract_function(node, file_path)

            if snippet:
                snippets.append(snippet)

    return snippets
