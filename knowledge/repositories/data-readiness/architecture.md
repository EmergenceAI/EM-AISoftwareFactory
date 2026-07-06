<!--
AUTO-GENERATED from data-readiness
Last sync: 2026-06-29 06:53:28 UTC
Source commit: 20b4b407771b7e789c7e79bd35f38514e6a9ca44
DO NOT EDIT MANUALLY - Run ./sync_knowledge.sh to update
-->

# data-readiness Architecture

## Overview

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development](#development)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Repository Setup (Maintainers)](#repository-setup-maintainers)

## Prerequisites
## Quick Start

### Kubernetes deployment (recommended)

Deploys the full platform — em-runtime, Prefect, and data-readiness service — with a single command on a local Kind cluster.

**Prerequisites:** Docker Desktop running, tools installed via `make install-prereqs`. See [Prerequisites](#prerequisites).

```bash
# Create Kind cluster and deploy everything
