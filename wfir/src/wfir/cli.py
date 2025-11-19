import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from wfir.models import WorkflowIR
from wfir.compiler.langgraph.transpiler import LangGraphTranspiler

def compile_workflow(input_path: str, target: str = "langgraph") -> str:
    """
    Compile a WFIR JSON file to the target language.
    """
    try:
        with open(input_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON file '{input_path}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        workflow = WorkflowIR(**data)
    except Exception as e:
        print(f"Error: Invalid WFIR format: {e}", file=sys.stderr)
        sys.exit(1)

    if target == "langgraph":
        transpiler = LangGraphTranspiler()
        return transpiler.visit_workflow(workflow)
    else:
        print(f"Error: Unsupported target '{target}'. Currently only 'langgraph' is supported.", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="WFIR Compiler CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Compile command
    compile_parser = subparsers.add_parser("compile", help="Compile WFIR to target code")
    compile_parser.add_argument("input_file", help="Path to the input WFIR JSON file")
    compile_parser.add_argument("--target", default="langgraph", help="Target platform (default: langgraph)")

    args = parser.parse_args()

    if args.command == "compile":
        result = compile_workflow(args.input_file, args.target)
        print(result)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

