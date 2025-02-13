# codebase_analysis/scan_imports.py
"""
This script scans a project for external imports and prints them.

Methods:
    extract_imports: Extract all imports from a Python file.
    is_internal_import: Check if an import is internal to the project.
    find_project_packages: Find all potential Python packages in the project.
    scan_project_imports: Scan all Python files in a project and collect their imports.
    get_package_name: Convert import names to package names for common packages.
    main: Main function to run the import scanner.
"""

# Standard library imports
import ast
import os
from collections import defaultdict
from pathlib import Path
import sys


def extract_imports(file_path: str) -> set[str]:
    """Extract all imports from a Python file.

    Args:
        file_path (str): The path to the Python file.

    Returns:
        set: A set of import names.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            tree: ast.Module = ast.parse(file.read())
        except SyntaxError:
            print(f"Syntax error in {file_path}")
            return set()

    imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.add(name.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:  # Handles "from x import y"
                imports.add(node.module.split(".")[0])

    return imports


def is_internal_import(import_name: str, project_packages: set[str]) -> bool:
    """Check if an import is internal to the project.

    Args:
        import_name (str): The import name to check.
        project_packages (set): A set of project packages.

    Returns:
        bool: True if the import is internal to the project, False otherwise.
    """
    return import_name in project_packages


def find_project_packages(directory: str) -> set[str]:
    """Find all potential Python packages in the project.

    Args:
        directory (str): The directory to scan for packages.

    Returns:
        set: A set of package names.
    """
    packages = set()
    for root, dirs, files in os.walk(directory):
        if "__init__.py" in files:
            # Get the package name from the directory structure
            package_path: Path = Path(root).relative_to(directory)
            if str(package_path) == ".":
                continue
            packages.add(str(package_path).split(os.sep)[0])
    return packages


def scan_project_imports(directory: str) -> dict[str, set[str]]:
    """Scan all Python files in a project and collect their imports.

    Args:
        directory (str): The directory to scan for imports.

    Returns:
        dict: A dictionary of imports and their file paths.
    """
    project_packages: set[str] = find_project_packages(directory)
    external_imports: defaultdict[str, set[str]] = defaultdict(set)

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path: str = os.path.join(root, file)
                imports: set[str] = extract_imports(file_path)

                # Filter out internal imports and standard library
                for imp in imports:
                    if not is_internal_import(imp, project_packages):
                        external_imports[imp].add(file_path)

    return external_imports


def get_package_name(import_name: str) -> str:
    """Convert import names to package names for common packages.

    Args:
        import_name (str): The import name to convert.

    Returns:
        str: The package name.
    """
    package_mapping: dict[str, str] = {
        "PIL": "pillow",
        "cv2": "opencv-python",
        "sklearn": "scikit-learn",
        "yaml": "pyyaml",
        "bs4": "beautifulsoup4",
        "wx": "wxPython",
    }
    return package_mapping.get(import_name, import_name.lower())


def main(directory: str = ".") -> None:
    """Main function to run the import scanner.

    Args:
        directory (str): The directory to scan for imports.
    """
    print(f"Scanning directory: {directory}")
    external_imports: dict[str, set[str]] = scan_project_imports(directory)

    if not external_imports:
        print("No external imports found.")
        return

    print("\nExternal imports found:")
    for import_name, files in sorted(external_imports.items()):
        print(f"\n{import_name}:")
        for file in sorted(files):
            print(f"  - {file}")

    print("\nFor requirements.txt:")
    for import_name in sorted(external_imports.keys()):
        print(get_package_name(import_name))


if __name__ == "__main__":
    """Main entry point for the script."""
    directory: str = sys.argv[1] if len(sys.argv) > 1 else "."
    main(directory)
