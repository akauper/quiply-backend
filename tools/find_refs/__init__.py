import ast
import os
import sys


def list_module_references(filename, unique_imports):
    """List non-relative module references."""
    with open(filename, "r", encoding='utf-8') as source:
        tree = ast.parse(source.read(), filename=filename)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                unique_imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and not node.module.startswith("."):
                # This is a non-relative import
                unique_imports.add(node.module)
                for alias in node.names:
                    unique_imports.add(f"{node.module}.{alias.name}")


def analyze_directory(directory_path):
    """Analyze all Python files in the given directory, collecting unique non-relative imports."""
    unique_imports = set()
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                list_module_references(filepath, unique_imports)
    return unique_imports


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python list_module_references.py <path_to_directory>")
        sys.exit(1)

    directory_path = sys.argv[1]

    if os.path.isdir(directory_path):
        unique_imports = analyze_directory(directory_path)
        for import_ in sorted(unique_imports):
            if import_.startswith("src"):
                print(import_)
    else:
        print(f"Error: {directory_path} is not a valid directory path.")
