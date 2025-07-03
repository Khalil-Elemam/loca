from pathlib import Path
from typing import Optional, Callable
import sys
from chromadb import QueryResult
import lazy_import
from xxhash import xxh3_64_hexdigest
from colorama import init, Fore, Style


from .snippet import Snippet, extract_snippets
from .utils import get_project_root, read_file, starts_with_any, scan_python_files
from .constants import CURRENT_PROJECT_ROOT_KEY
from .progress import ProgressBar, Spinner
from .config import add_to_config


chroma = lazy_import.lazy_module("loca.chroma")

from .cache import (
    get_file_cache,
    get_snippet_cache,
    save_file_cache,
    save_snippet_cache,
)

init(autoreset=True)

commands: dict[str, Callable] = {}


def command(name: Optional[str] = None):
    def decorator(f: Callable) -> Callable:
        command_name = name or f.__name__
        commands[command_name] = f
        return f

    return decorator


@command("set-root")
def set_project_root(path: str = "."):
    print(f"{Style.BRIGHT}📂 Setting project root...{Style.RESET_ALL}\n")
    project_root = Path(path).resolve()
    if not project_root.is_dir():
        print(
            f"{Fore.RED}❌ Invalid project root path: {project_root}{Style.RESET_ALL}\n"
        )
        sys.exit(1)
    add_to_config(CURRENT_PROJECT_ROOT_KEY, str(project_root))
    print(f"{Fore.GREEN}✔ Project root set to: {project_root}{Style.RESET_ALL}\n")


@command()
def query(q: str, n_results: int = 5):
    print(f"{Style.BRIGHT}🔍 Searching for: {q}{Style.RESET_ALL}\n")
    try:
        with Spinner("Searching database"):
            results = chroma.query(q, n_results)
    except RuntimeError as e:
        print(f"{Fore.RED}{e}{Style.RESET_ALL}\n")
        return

    print_results(q, results)


@command()
def index() -> None:
    print(f"{Style.BRIGHT}📂 Starting indexing process...{Style.RESET_ALL}\n")
    try:
        path = get_project_root()
        file_cache = get_file_cache()
        new_file_cache = {}
        snippet_cache = get_snippet_cache()
        new_snippet_cache = {}
        un_updated_files_prefixes = set()
        snippets: list[Snippet] = []

        print(f"{Style.BRIGHT}📁 Scanning Python files in: {path}{Style.RESET_ALL}\n")

        python_files = scan_python_files(path)

        if not python_files:
            print(f"{Fore.YELLOW}⚠️  No Python files found!{Style.RESET_ALL}\n")

        progress = ProgressBar(len(python_files), "Indexing files")

        for file in python_files:
            is_cached, file_snippets, file_hash = process_python_file(
                file, file_cache, snippet_cache, new_snippet_cache, path
            )
            new_file_cache[str(file.relative_to(path))] = file_hash
            if is_cached:
                un_updated_files_prefixes.add(str(file.relative_to(path)))
                progress.update(item_name=f"{file.name} (cached)")
            else:
                snippets.extend(file_snippets)
                progress.update(
                    item_name=f"{file.name} ({len(file_snippets)} snippets)"
                )

        # Database operations with spinner
        update_database(
            snippet_cache, new_snippet_cache, un_updated_files_prefixes, chroma
        )
        if snippets:
            with Spinner(f"Adding {len(snippets)} new snippets"):
                chroma.add(snippets)
        save_caches_and_print(new_file_cache, new_snippet_cache, python_files, snippets)
    except RuntimeError as e:
        print(f"{Fore.RED}{e}{Style.RESET_ALL}\n")
        return 1


@command()
def clear() -> None:
    """
    Clear the caches and the ChromaDB collection.
    """
    print(f"{Style.BRIGHT}🧹 Clearing all caches and database...{Style.RESET_ALL}\n")
    try:
        with Spinner("Clearing database and caches"):
            chroma.clear()
            save_file_cache({})
            save_snippet_cache({})
        print(f"{Fore.GREEN}✅ All data cleared successfully!{Style.RESET_ALL}\n")
    except RuntimeError as e:
        print(f"{Fore.RED}{e}{Style.RESET_ALL}\n")
        return


def process_file_snippets(
    file_path: str,
    file_content: str,
    snippet_cache: dict[str, str],
    new_snippet_cache: dict[str, str],
) -> list[Snippet]:
    file_snippets = extract_snippets(file_path, file_content)
    snippets: list[Snippet] = []
    for snippet in file_snippets:
        snippet_hash = xxh3_64_hexdigest(snippet.code)
        if (
            snippet.id in snippet_cache
            and snippet_cache.get(snippet.id) == snippet_hash
        ):
            new_snippet_cache[snippet.id] = snippet_hash
            del snippet_cache[snippet.id]
        else:
            new_snippet_cache[snippet.id] = snippet_hash
            snippets.append(snippet)
    return snippets


def process_python_file(
    file: Path,
    file_cache: dict,
    snippet_cache: dict,
    new_snippet_cache: dict,
    project_root: Path,
) -> tuple[bool, list[Snippet], str]:
    """
    Process a single Python file: hash, extract snippets, update caches.
    Returns (is_cached, file_snippets, file_hash)
    """
    file_content = read_file(file)
    file_path = str(file.relative_to(project_root))
    file_hash = xxh3_64_hexdigest(file_content)
    if file_path in file_cache and file_cache.get(file_path) == file_hash:
        new_snippet_cache[file_path] = file_hash
        return True, [], file_hash
    else:
        new_snippet_cache[file_path] = file_hash
        file_snippets = process_file_snippets(
            file_path, file_content, snippet_cache, new_snippet_cache
        )
        return False, file_snippets, file_hash


def update_database(
    snippet_cache, new_snippet_cache, un_updated_files_prefixes, chroma
) -> None:
    """
    Update the database: remove old snippets, add new ones.
    """
    old_snippets = snippet_cache.keys() - new_snippet_cache.keys()
    for old_snippet_key in list(old_snippets):
        if starts_with_any(old_snippet_key, un_updated_files_prefixes):
            val = snippet_cache.get(old_snippet_key)
            old_snippets.remove(old_snippet_key)
            new_snippet_cache[old_snippet_key] = val
    if old_snippets:
        with Spinner(f"Removing {len(old_snippets)} old snippets"):
            chroma.delete(ids=list(old_snippets))


def save_caches_and_print(
    new_file_cache, new_snippet_cache, python_files, snippets
) -> None:
    """
    Save caches and print the final summary message.
    """
    with Spinner("Saving caches"):
        save_file_cache(new_file_cache)
        save_snippet_cache(new_snippet_cache)
    print(
        f"{Fore.GREEN}✅ Indexing complete! Processed {len(python_files)} files, found {len(snippets)} new/updated snippets.{Style.RESET_ALL}\n"
    )


def print_results(q: str, results: QueryResult) -> None:
    """
    Print the results of the query in a formatted way.
    """
    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    result_count = len(ids)
    print(f"{Fore.BLUE}✅ Found {result_count} results for: '{q}'{Style.RESET_ALL}\n")
    if result_count == 0:
        print(f"{Fore.YELLOW}No matching code snippets found.{Style.RESET_ALL}\n")
        return
    for idx, (id_, doc, meta) in enumerate(zip(ids, docs, metadatas), 1):
        print(f"{Fore.CYAN}{Style.BRIGHT}{idx}. {id_}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{doc}{Style.RESET_ALL}")
        if meta.get("name"):
            print(f"   {Fore.MAGENTA}Name: {meta['name']}{Style.RESET_ALL}")
        if meta.get("type"):
            print(f"   {Fore.GREEN}Type: {meta['type']}{Style.RESET_ALL}")
        if meta.get("docstring"):
            print(f"   {Fore.YELLOW}Docstring: {meta['docstring']}{Style.RESET_ALL}")
        print()
