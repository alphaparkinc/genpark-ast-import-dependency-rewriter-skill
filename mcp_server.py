import sys, json
from client import AstImportDependencyRewriter

def main():
    rewriter = AstImportDependencyRewriter()
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print(json.dumps(rewriter.run_benchmark_import_rewriter(), indent=2))
        return

    for line in sys.stdin:
        if not line.strip(): continue
        try:
            req = json.loads(line)
            method = req.get("method")
            params = req.get("params", {})
            rid = req.get("id")

            if method == "tools/list":
                res = {
                    "tools": [
                        {"name": "rewrite_imports", "description": "Safely rewrite import modules using AST mapping."},
                        {"name": "inspect_imports", "description": "List all imported packages and symbols."},
                        {"name": "run_benchmark_import_rewriter", "description": "Run import rewriting benchmark."}
                    ]
                }
            elif method == "tools/call":
                tname = params.get("name")
                args = params.get("arguments", {})
                if tname == "rewrite_imports":
                    out = rewriter.rewrite_imports(args.get("python_code", ""), args.get("migration_map", {}))
                elif tname == "inspect_imports":
                    out = rewriter.inspect_imports(args.get("python_code", ""))
                elif tname == "run_benchmark_import_rewriter":
                    out = rewriter.run_benchmark_import_rewriter()
                else:
                    out = {"error": f"Unknown tool {tname}"}
                res = {"content": [{"type": "text", "text": json.dumps(out)}]}
            else:
                res = {"error": "Unsupported method"}
            print(json.dumps({"jsonrpc": "2.0", "id": rid, "result": res}), flush=True)
        except Exception as e:
            print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}}), flush=True)

if __name__ == "__main__":
    main()
