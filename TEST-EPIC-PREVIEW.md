# Test Epic Preview - Batch Creation for ABI Project

This document shows what the `/create-epic --from-table` skill would create when processing the example CSV file.

---

## Epic 1 of 1

**Project:** ABI  
**Priority:** High  
**Labels:** data-connectors, infineon, csv-parquet  
**Assignee:** (not specified)

### Epic Title
CSV/Parquet API Connector for Large Dataset Ingestion

---

## Vision

Enable data scientists and engineers to programmatically upload and process large CSV/Parquet datasets (300 MB - 1 GB) through robust API-based connectors with automated quality validation, eliminating manual upload bottlenecks and enabling reliable data pipeline integration.

## Overview

Build API-based data connector workflows that enable programmatic ingestion, profiling, validation, and optimization of large CSV/Parquet datasets. The system will provide four core workflow types: (1) Ingestion Workflows that extract comprehensive metadata from CSV sources including schema, columns, data types, and constraints; (2) Profiling Workflows that generate column-level statistical profiles using Python/PySpark processing; (3) DQ Query Generation workflows that create data quality rule templates from CSV analysis; and (4) DQ Execution Workflows that validate data against quality rules end-to-end. Additionally, an ETL staging workflow will convert and optimize uploaded CSV/Parquet files for efficient large-scale data access.

## Problem Statement

### Current State

The em-data-readiness platform has connectors for databases (PostgreSQL, Snowflake) but lacks an API-based connector for CSV/Parquet files. The Infineon analog trimming workflow and Broadcom requires ingestion of large CSV/Parquet datasets (300 MB - 1 GB), but there's no standardized connector to handle file-based data sources. Without this connector, workflows cannot programmatically ingest, profile, validate, or optimize CSV/Parquet files through the same API-based interface used for database connectors.

### Desired State

- New CSV/Parquet API-based connector in em-data-readiness alongside existing database connectors
- Connector supports chunked/streaming upload of large files (300 MB - 1 GB) with progress tracking
- Implements standard connector workflows: Ingestion (metadata extraction), Profiling (statistical analysis), DQ Generation (rule templates), DQ Execution (validation)
- ETL staging workflow optimizes uploaded files (e.g., converts to partitioned Parquet) for efficient agent access
- Infineon analog trimming workflow can consume CSV/Parquet data through this connector using the same API patterns as database connectors
- All workflows follow eval-based development with automated quality gates
- Connector integrates with existing em-data-readiness architecture and observability

### Impact

Customer Impact: Enables Infineon and other customers to integrate file-based data sources into their workflows using the same reliable connector patterns they use for databases, eliminating custom integration work.

Business Impact: Unblocks Infineon analog trimming workflow deployment. Expands addressable data sources beyond databases to include file-based pipelines common in semiconductor manufacturing.

Strategic Impact: Completes the data connector ecosystem (database + file-based sources), enabling agent workflows to consume data from any source. Demonstrates consistent eval-based quality across all connector types.

## Success Criteria

Functional Criteria:
- CSV/Parquet API-based connector implemented in em-data-readiness with same architectural patterns as PostgreSQL/Snowflake connectors
- Connector supports chunked upload for files 300 MB - 1 GB with progress tracking and resumable uploads
- All four workflow types operational: Ingestion, Profiling, DQ Generation, DQ Execution
- ETL staging workflow converts CSV to optimized Parquet with appropriate partitioning strategy
- Infineon analog trimming workflow successfully consumes data through the connector with no regressions

Performance Criteria:
- 500 MB CSV file uploads complete in < 5 minutes with < 5% failure rate
- 1 GB Parquet file uploads complete in < 10 minutes with < 5% failure rate
- Profiling workflow completes for 1 GB dataset in < 15 minutes
- Optimized staging reduces query time by ≥ 50% vs. raw CSV

Eval-Based Validation (Automated Tests):
- Eval 1: Upload Integrity — Upload 500 MB CSV, verify row count and checksum match source (100% accuracy required)
- Eval 2: Schema Detection — Ingestion workflow correctly identifies all column types for 20-column CSV with mixed types (100% accuracy)
- Eval 3: Profile Completeness — Profiling workflow generates nulls, cardinality, min/max, distribution for all columns (100% coverage)
- Eval 4: DQ Rule Generation — DQ Generation creates valid rules for common patterns (NOT NULL, range checks, format validation) with ≥ 90% precision
- Eval 5: DQ Execution Accuracy — DQ Execution correctly flags known quality issues in test dataset (100% recall on planted defects)
- Eval 6: Parquet Optimization — Staged Parquet file size ≤ 70% of original CSV, query performance ≥ 2x faster
- Eval 7: Infineon Workflow Integration — End-to-end test: upload Infineon sample data → validate → consume in analog trimming workflow (0 errors)

Observability & Monitoring:
- All workflows emit metrics (duration, success rate, data volume) to existing observability stack
- Failed uploads provide clear error messages and recovery guidance

## Business Value

### User Value

Infineon data engineers can programmatically integrate CSV/Parquet data sources into their analog trimming workflows using the same reliable API patterns they use for database connectors, eliminating hours of custom integration work and manual file handling.

### Business Impact

- Unblocks Infineon analog trimming workflow deployment, enabling critical customer use case
- Reduces data onboarding time by ~80% through automated ingestion, profiling, and validation
- Expands addressable market to customers with file-based data pipelines (common in semiconductor manufacturing)
- Reduces support burden by providing standardized connector with automated quality gates

### Strategic Alignment

Completes the data connector ecosystem alongside database connectors, positioning the platform as a comprehensive data engineering solution. Demonstrates eval-based development methodology that builds customer confidence in platform reliability and quality. Enables the broader "Build Your Own Workflow" (BYOW) strategy by providing file-based data sources as foundational building blocks for custom workflows.

---

## What Would Happen Next

If this were running in the actual skill with MCP integration:

1. ✅ **Parse CSV** - Successfully read 1 epic from example-epics-template.csv
2. ✅ **Validate** - All required columns present
3. ✅ **Preview** - Show full epic content (above)
4. ⏸️ **Confirm** - Ask user: "Create this epic in ABI? [Y/n]"
5. 🔄 **Create** - Call `mcp__atlassian__jira_create_issue` with:
   - `project_key`: "ABI"
   - `summary`: "CSV/Parquet API Connector for Large Dataset Ingestion"
   - `issue_type`: "Epic"
   - `description`: [Full markdown above]
   - `additional_fields`: {"priority": {"name": "High"}, "labels": ["data-connectors", "infineon", "csv-parquet"]}
6. ✅ **Report** - Return issue key (e.g., ABI-123) and URL

## Testing Note

To fully test this skill in a real environment:
1. The plugin needs to be loaded in a repository (not in the plugin source itself)
2. MCP Atlassian server must be configured and connected
3. User must have permissions to create epics in the ABI project
4. Then run: `/create-epic --from-table skills/create-epic/example-epics-template.csv`
