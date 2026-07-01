"""
Entry point for running orchestrator as a module.

Usage:
    python -m orchestrator implement ABI-123
    python -m orchestrator knowledge --repo runtime
    python -m orchestrator test ABI-123
"""

from .cli import main

if __name__ == '__main__':
    main()
