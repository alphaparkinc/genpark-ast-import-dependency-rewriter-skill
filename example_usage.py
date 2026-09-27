import sys, json
from client import AstImportDependencyRewriter

def main():
    print("Testing AstImportDependencyRewriter...")
    rewriter = AstImportDependencyRewriter()
    res = rewriter.run_benchmark_import_rewriter()
    print(json.dumps(res, indent=2))
    assert res["benchmark_status"] == "PASSED"
    assert res["syntax_valid"] is True
    assert res["has_modern_logger"] is True
    assert res["has_modern_auth"] is True
    print("All AST Import Dependency Rewriter tests passed successfully!")

if __name__ == "__main__":
    main()
