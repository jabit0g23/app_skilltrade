#!/usr/bin/env python3
# export_project.py
# python -X utf8=1 ./export_project.py > proyecto.md

import os
import sys

def export_project(root_dir):
    """
    Recorre todo el directorio `root_dir` y genera un texto que incluye
    el path relativo y el contenido de cada archivo (en Markdown).
    """
    lines = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Omitir carpetas .git, node_modules, __pycache__
        dirnames[:] = [d for d in dirnames if d not in ('.git', 'node_modules', '__pycache__', 'venv', '.venv')]
        for fname in filenames:
            filepath = os.path.join(dirpath, fname)
            relpath = os.path.relpath(filepath, root_dir)
            lines.append(f"### FILE: `{relpath}`\n")
            try:
                # Solo leer archivos de texto
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                content = "<Binario o codificación no UTF-8 omitido>"
            except Exception as e:
                content = f"<No se pudo leer: {e}>"
            lines.append("```")
            lines.append(content)
            lines.append("```\n")
    return "\n".join(lines)

if __name__ == "__main__":
    project_root = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
    export_text = export_project(project_root)
    # IMPRESIÓN FINAL
    print(export_text)
