# Incremental Processing Strategy

## Overview

The mart_commercial_daily model uses incremental materialisation to support efficient processing of new and updated booking transactions. Other Gold marts retain full-table materialisation.

## Implementation

- Materialisation: incremental
- Strategy: MERGE
- Unique key: COMMERCIAL_DAILY_KEY
- Grain: transaction date and product
- Watermark: SOURCE_UPDATED_AT_UTC
- Change detection: UPDATED_AT_UTC >= current watermark
- Processing: affected-grain reaggregation
- Stale-row handling: post-hook DELETE
- Schema change policy: fail

## Processing Logic

1. Identify new or updated booking items using the watermark.
2. Identify affected date and product groups.
3. Reaggregate all qualifying booking items within those groups.
4. Insert new groups or update existing groups using MERGE.
5. Remove groups that no longer contain positive gross sales.
6. Execute data quality and reconciliation tests.

## Validation Results

- Historical transaction updates: passed
- Late-arriving transactions: passed
- New aggregate group insertion: passed
- Stale-row detection and removal: passed
- Repeated-run aggregate consistency: passed
- Full-refresh equivalence: zero differences across 31 columns
- Original dataset restoration: passed
- Gold regression build: 366 passed, 11 warnings, 0 errors

## dbt State Optimisation

During controlled testing, dbt State optimisation skipped an incremental execution within its freshness tolerance. The reconciliation test detected the resulting discrepancy. State optimisation was disabled temporarily using DBT_ENGINE_MANAGE_STATE=0 to validate actual incremental execution.

## Known Limitations

- Partial hard deletes may not trigger affected-group reprocessing.
- Historical grouping-key changes may leave incorrect aggregates in previous groups.
- Dimension-only changes may not trigger reprocessing.
- The aggregate-based watermark can regress when groups are removed.
- Changes with timestamps older than the watermark may be missed.
- Boundary timestamps are intentionally reprocessed.
- The post-hook adds source and target checking overhead.
- Upstream fact models remain full-table models.
- Performance improvements have not been benchmarked.

## Recovery Strategy

Use reconciliation tests to detect discrepancies. Perform a full refresh when unsupported historical corrections or dimension changes occur.

Future production enhancements may include CDC, persistent watermark tracking, explicit freshness configuration and automated recovery workflows.