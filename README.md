# loca

**Local, privacy-first semantic code search engine.**

loca is a blazing-fast, local-first tool that lets you search your codebase using natural language queries. It uses embeddings, syntax parsing, and vector search to help you instantly find relevant functions, classes, and files—without sending your code anywhere.

## Features
- 🔍 **Semantic code search**: Find code by meaning, not just keywords.
- 🛡️ **Privacy-first**: Your code never leaves your machine.
- ⚡ **Fast**: Indexes and searches even large codebases quickly.
- 🧠 **Natural language queries**: Search like you think.
- 🗂️ **Easy CLI**: Simple commands for indexing, querying, and managing your project.

## Installation

```sh
pip install .
```
Or build and install from source:
```sh
python -m build
pip install dist/loca-*.whl
```

## Usage


### 1. Set your project root

This tells loca where your codebase lives. Run this once per project:
```sh
loca set-root --path /path/to/your/project
```
If you omit `--path`, it uses the current directory.

---

### 2. Index your codebase

Scan and index all Python files in your project. Run this after setting the root, or whenever your code changes:
```sh
loca index
```
You’ll see progress bars and a summary of how many files/snippets were indexed.

---

### 3. Search with natural language

Find code by meaning, not just keywords! For example:
```sh
loca query "find all database connection functions"
loca query "class for user authentication"
loca query "function that parses json"
```
Results will show the most relevant code snippets, with file names and docstrings.

---

### 4. Clear all caches and the index

If you want to reset everything (e.g., after a big refactor):
```sh
loca clear
```
This removes all indexed data and cached files.

---

### 5. Show help and version

Get help for any command:
```sh
loca --help
loca index --help
loca query --help
```
Show the current version:
```sh
loca --version
```

## Commands
- `set-root` — Set the root directory of your project for all loca operations.
- `index` — Index your project’s Python files for fast semantic code search.
- `query` — Search your codebase using a natural language query.
- `clear` — Clear all loca caches and remove all indexed code from the database.

## Requirements
- Python 3.9+
- chromadb, xxhash, platformdirs, colorama (installed automatically)

## License
MIT

---

Made with ❤️ by Khalil Elemam
