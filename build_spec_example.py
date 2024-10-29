####
'''
This script is to build a spec file example and compile a new exe using pyinstaller
'''
####
import os
import subprocess
import sys
import importlib.util
from pathlib import Path

# List of hidden imports
hidden_imports = ['networkx', 'pyvis', 'collections', 'tkinter', 'argparse']

def check_and_install(package):
    """Check if a package is installed, and install it if it's not."""
    if importlib.util.find_spec(package) is None:
        print(f"{package} is not installed. Installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    else:
        print(f"{package} is already installed.")

def find_pyvis_paths():
    """Find all installation paths of the Pyvis library."""
    paths = []
    for p in sys.path:
        search_path = Path(p) / 'pyvis'
        if search_path.exists():
            paths.append(search_path)
    return paths

def create_spec_file(datas):
    """Create a .spec file with the specified datas."""
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-\n\nimport sys; sys.setrecursionlimit(sys.getrecursionlimit() * 5)\n\na = Analysis(\n    ['netlist.py'],\n    pathex=[],\n    binaries=[],\n    datas={datas},\n    hiddenimports={hidden_imports},\n    hookspath=[],\n    hooksconfig={{}},\n    runtime_hooks=[],\n    excludes=[],\n    noarchive=False,\n    optimize=0,\n)\npyz = PYZ(a.pure)\n\nexe = EXE(\n    pyz,\n    a.scripts,\n    a.binaries,\n    a.datas,\n    [],\n    name='netlist',\n    debug=False,\n    bootloader_ignore_signals=False,\n    strip=False,\n    upx=True,\n    upx_exclude=[],\n    runtime_tmpdir=None,\n    console=True,\n    disable_windowed_traceback=False,\n    argv_emulation=False,\n    target_arch=None,\n    codesign_identity=None,\n    entitlements_file=None,\n)"""
    
    with open('netlist.spec', 'w') as f:
        f.write(spec_content)
    print("Spec file 'netlist.spec' created successfully.")

def main():
    # Check and install hidden imports
    for package in hidden_imports:
        check_and_install(package)

    # Find all paths for Pyvis
    pyvis_paths = find_pyvis_paths()
    
    if not pyvis_paths:
        print("Pyvis is not installed anywhere in the Python paths.")
        return

    # Prompt the user to select a path if multiple are found
    if len(pyvis_paths) > 1:
        print("Multiple Pyvis installations found:")
        for i, path in enumerate(pyvis_paths):
            print(f"{i + 1}: {path}")
        choice = int(input("Select the number corresponding to the path you want to use: ")) - 1
        selected_path = pyvis_paths[choice]
    else:
        selected_path = pyvis_paths[0]

    # Prepare datas for the .spec file
    datas = [
        (str(selected_path / 'templates'), 'pyvis/templates'),
        (str(selected_path / 'templates/lib'), 'pyvis/templates/lib'),
    ]
    
    # Create the spec file
    create_spec_file(datas)

if __name__ == "__main__":
    main()
