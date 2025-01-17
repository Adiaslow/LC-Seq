import ast
import os
from collections import defaultdict
from pathlib import Path

def extract_imports(file_path):
    """Extract all imports from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            tree = ast.parse(file.read())
        except SyntaxError:
            print(f"Syntax error in {file_path}")
            return set()

    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.add(name.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:  # Handles "from x import y"
                imports.add(node.module.split('.')[0])

    return imports

def is_internal_import(import_name, project_packages):
    """Check if an import is internal to the project."""
    return import_name in project_packages

def find_project_packages(directory):
    """Find all potential Python packages in the project."""
    packages = set()
    for root, dirs, files in os.walk(directory):
        if '__init__.py' in files:
            # Get the package name from the directory structure
            package_path = Path(root).relative_to(directory)
            if str(package_path) == '.':
                continue
            packages.add(str(package_path).split(os.sep)[0])
    return packages

def scan_project_imports(directory):
    """Scan all Python files in a project and collect their imports."""
    project_packages = find_project_packages(directory)
    external_imports = defaultdict(set)

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                imports = extract_imports(file_path)

                # Filter out internal imports and standard library
                for imp in imports:
                    if not is_internal_import(imp, project_packages):
                        external_imports[imp].add(file_path)

    return external_imports

def get_package_name(import_name):
    """Convert import names to package names for common packages."""
    package_mapping = {
        'PIL': 'pillow',
        'cv2': 'opencv-python',
        'sklearn': 'scikit-learn',
        'yaml': 'pyyaml',
        'bs4': 'beautifulsoup4',
        'wx': 'wxPython',
    }
    return package_mapping.get(import_name, import_name.lower())

def main(directory='.'):
    """Main function to run the import scanner."""
    print(f"Scanning directory: {directory}")
    external_imports = scan_project_imports(directory)

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

if __name__ == '__main__':
    import sys
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    main(directory)
