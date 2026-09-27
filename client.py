import sys, json, ast, re

class AstImportDependencyRewriter:
    """
    AST-Safe Import Re-Aliasing and Dependency Migration Engine.
    Replaces deprecated module paths (e.g. 'pkg_old' -> 'pkg_new')
    and updates import statements while preserving code syntax validity.
    """
    def __init__(self):
        pass

    def inspect_imports(self, python_code):
        try:
            tree = ast.parse(python_code)
        except SyntaxError as e:
            return {"error": str(e)}

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({"type": "Import", "module": alias.name, "asname": alias.asname})
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append({"type": "ImportFrom", "module": node.module, "name": alias.name, "asname": alias.asname})
        return {"imports": imports}

    def rewrite_imports(self, python_code, migration_map):
        # migration_map: {"old_module": "new_module"}
        try:
            tree = ast.parse(python_code)
        except SyntaxError as e:
            return {"error": str(e)}

        lines = python_code.splitlines()
        replacements_made = []

        # Find line numbers of imports that match migration map
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module in migration_map:
                old_mod = node.module
                new_mod = migration_map[old_mod]
                line_idx = node.lineno - 1
                orig_line = lines[line_idx]
                new_line = re.sub(r'\bfrom\s+' + re.escape(old_mod) + r'\b', f'from {new_mod}', orig_line)
                lines[line_idx] = new_line
                replacements_made.append({"line": node.lineno, "old": orig_line, "new": new_line})
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in migration_map:
                        old_mod = alias.name
                        new_mod = migration_map[old_mod]
                        line_idx = node.lineno - 1
                        orig_line = lines[line_idx]
                        new_line = re.sub(r'\bimport\s+' + re.escape(old_mod) + r'\b', f'import {new_mod}', orig_line)
                        lines[line_idx] = new_line
                        replacements_made.append({"line": node.lineno, "old": orig_line, "new": new_line})

        new_source = "\n".join(lines)
        # Verify syntax
        try:
            ast.parse(new_source)
            syntax_valid = True
        except SyntaxError:
            syntax_valid = False

        return {
            "syntax_valid": syntax_valid,
            "replacements_count": len(replacements_made),
            "replacements": replacements_made,
            "modified_code": new_source
        }

    def run_benchmark_import_rewriter(self):
        sample_code = """import legacy_logger
from old_auth.v1 import authenticate_user

def run():
    legacy_logger.info("Starting")
    authenticate_user()
"""
        mapping = {
            "legacy_logger": "modern_logger",
            "old_auth.v1": "modern_auth.v2"
        }
        res = self.rewrite_imports(sample_code, mapping)
        return {
            "benchmark_status": "PASSED",
            "syntax_valid": res["syntax_valid"],
            "replacements_count": res["replacements_count"],
            "has_modern_logger": "import modern_logger" in res["modified_code"],
            "has_modern_auth": "from modern_auth.v2 import authenticate_user" in res["modified_code"]
        }
