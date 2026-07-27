"""
Entry point for running the harness as a module.

Usage:
    python -m harness implement ABI-123
    python -m harness knowledge --repo runtime
    python -m harness test ABI-123
"""

from .cli import main

if __name__ == '__main__':
    main()
