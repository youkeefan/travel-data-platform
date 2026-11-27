
# Travel Data Platform

An end-to-end cloud data engineering platform designed to simulate a modern travel e-commerce data ecosystem using AWS, Snowflake, dbt, Python and GitHub Actions.

The platform demonstrates environment isolation, automated data ingestion, layered data transformation, dimensional modelling, data quality management, role-based access control and CI/CD deployment. The platform also includes a DEV-only Snowflake semantic layer and Cortex Analyst integration for natural language analytics.

---

## Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. Technology Stack](#2-technology-stack)
- [3. System Architecture](#3-system-architecture)
- [4. Environment Management](#4-environment-management)
- [5. Security and Access Control](#5-security-and-access-control)
- [6. Data Domain](#6-data-domain)
- [7. Data Ingestion](#7-data-ingestion)
- [8. Medallion Architecture](#8-medallion-architecture)
- [9. Data Modelling](#9-data-modelling)
- [10. Data Quality Framework](#10-data-quality-framework)
- [11. CI/CD](#11-cicd)
- [12. Development and Implementation Workflow](#12-development-and-implementation-workflow)
- [13. Local Development](#13-local-development)
- [14. AI-Enabled Analytics — Semantic Layer & Cortex Analyst](#14-ai-enabled-analytics--semantic-layer--cortex-analyst)
- [15. Repository Structure](#15-repository-structure)
- [16. Implementation Results](#16-implementation-results)
- [17. Engineering Practices](#17-engineering-practices)
- [18. Monitoring and Observability](#18-monitoring-and-observability)
- [19. Project Status](#19-project-status)
- [20. Conclusion](#20-conclusion)
- [Author](#author)

---

## 1. Project Overview

The Travel Data Platform processes synthetic travel transaction, customer, product, payment and loyalty data into reliable, analytics-ready datasets.

The project follows an ELT architecture, where source data is extracted and loaded into a cloud data warehouse before being transformed into curated analytical models.

### Project Objectives

- Build a scalable cloud-based data platform.
- Establish isolated DEV, CI and PROD environments.
- Implement automated ingestion using AWS S3 and Snowpipe.
- Develop a Bronze, Silver and Gold data architecture.
- Implement reusable and modular dbt transformation models.
- Manage data quality through automated testing and validation.
- Apply dimensional modelling and Slowly Changing Dimensions.
- Implement secure, automated CI/CD deployment.
- Establish traceability, documentation and data lineage.
- Enable reliable downstream business intelligence and analytics.
- Define governed business metrics and enable natural language analytics.

---

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Synthetic data generation, dirty data injection and ingestion utilities |
| AWS S3 | Cloud object storage and ingestion landing zone |
| AWS IAM | Secure AWS resource access |
| Snowpipe | Automated file ingestion |
| Snowflake | Cloud data warehouse and compute |
| SQL | Data transformation and analytical modelling |
| dbt Core | Transformation, testing, documentation and lineage |
| Git | Version control |
| GitHub | Source code management and collaboration |
| GitHub Actions | Continuous integration and deployment |
| VS Code | Local development environment |
| YAML | Configuration, source definitions and data tests |
| Snowflake Semantic Views | Governed business dimensions, facts and metrics |
| Snowflake Cortex Analyst | Natural language to SQL analytics |

---

## 3. System Architecture

```mermaid
flowchart TD
    A[Python Synthetic Data Generator]
    B[CSV Source Data]
    C[Dirty Data Injection]
    D[AWS S3 Landing Zone]
    E[Snowpipe]
    F[Snowflake Bronze Layer]
    G[dbt Silver Layer]
    H[dbt Gold Layer]
    I[Business Intelligence and Analytics]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    H --> O[Semantic View - DEV]
    O --> P[Cortex Analyst]
    P --> Q[Natural Language Analytics]

    J[GitHub Repository]
    K[GitHub Actions CI/CD]
    L[DEV Environment]
    M[CI Environment]
    N[PROD Environment]

    J --> K
    J --> L
    K --> M
    M -->|Successful Validation and Merge| N
```

### Architectural Principles

- Environment isolation
- Separation of storage and compute
- ELT-based processing
- Layered data architecture
- Modular and reusable transformations
- Data quality by design
- Least-privilege access
- Automated validation and deployment
- Reproducibility and traceability

---

## 4. Environment Management

The platform uses three isolated Snowflake environments to separate development, automated validation and production workloads.

### 4.1 Environment Configuration

| Environment | Database | Purpose |
|---|---|---|
| DEV | TRAVEL_DEV_DB | Local development and model testing |
| CI | TRAVEL_CI_DB | Automated pull request validation |
| PROD | TRAVEL_DB | Production deployment and analytical consumption |

### 4.2 Schema Architecture

| Layer | DEV | CI | PROD |
|---|---|---|---|
| Bronze | Shared source access | Shared source access | Physical source tables |
| Silver | Views | Views | Views |
| Gold | Tables | Tables | Tables |
| Semantic | Implemented | Not deployed | Not deployed |

DEV and CI use controlled access to the existing Bronze source data while maintaining isolated transformation outputs.

This design avoids unnecessary duplication of raw data while ensuring that development and CI workloads cannot modify production transformation models.

### 4.3 Environment Promotion

```mermaid
flowchart LR
    A[Feature Branch]
    B[DEV Development]
    C[Pull Request]
    D[CI Validation]
    E[Merge to Main]
    F[PROD Deployment]

    A --> B --> C --> D --> E --> F
```

dbt transformation changes are developed and tested in DEV, automatically validated in CI and deployed to PROD following a successful merge. Semantic view SQL is version-controlled separately and is not yet included in automated deployment.

---

## 5. Security and Access Control

Security is established before pipeline and transformation development.

### 5.1 Snowflake RBAC

The platform uses role-based access control to separate development, CI and production deployment responsibilities.

Access permissions are assigned according to the principle of least privilege.

| Responsibility | Access Scope |
|---|---|
| Development | Development models and required source data |
| CI validation | CI transformation objects and read-only source access |
| Production deployment | Production transformation objects |
| Data consumption | Approved analytical datasets |

The CI service account is restricted to the permissions required for automated validation.

CI workloads must not create, modify or delete production transformation objects.

### 5.2 AWS IAM

AWS IAM manages access to S3 and the resources required for automated data ingestion.

Security considerations include:

- Restricted S3 bucket access.
- Controlled storage integration permissions.
- Separation of AWS and Snowflake authentication.
- Avoidance of hardcoded credentials.
- Least-privilege access policies.

### 5.3 Secrets Management

Sensitive credentials are managed through environment variables, local configuration and GitHub Actions secrets.

Credentials must not be committed to the repository.

Examples include:

- Snowflake account credentials.
- Service account authentication information.
- AWS access credentials.
- Environment-specific connection settings.

---

## 6. Data Domain

The platform simulates a travel e-commerce business covering customer activity, travel bookings, financial transactions, product information and loyalty membership.

### Core Business Domains

| Domain | Data Entities |
|---|---|
| Customers | Customer profiles and addresses |
| Customer Lifecycle | Customer status and membership tier history |
| Bookings | Booking headers and booking items |
| Products | Travel products and categories |
| Vendors | Travel suppliers and vendor information |
| Payments | Payment transactions |
| Refunds | Refund transactions |
| Loyalty | Points earning and redemption transactions |

### Business Use Cases

The analytical layer supports use cases including:

- Booking performance analysis.
- Gross sales and gross margin reporting.
- Customer segmentation.
- Customer lifecycle analysis.
- Membership tier progression.
- Payment and refund reconciliation.
- Product and vendor performance.
- Loyalty points earning and redemption analysis.
- Customer-level commercial performance.

---

## 7. Data Ingestion

### 7.1 Synthetic Data Generation

Python generates synthetic relational datasets representing realistic travel business transactions.

The generated datasets include:

- Primary and foreign key relationships.
- Customer and booking identifiers.
- Transaction timestamps.
- Product and vendor relationships.
- Financial transaction values.
- Historical customer attributes.
- Loyalty points transactions.

Synthetic data allows the platform to demonstrate engineering practices without exposing real customer or commercial information.

### 7.2 Dirty Data Injection

Controlled data quality issues are introduced to simulate realistic upstream data problems.

A consolidated Python script supports four batches of data quality scenarios.

| Batch | Data Quality Scenarios |
|---|---|
| Batch 1 | Missing values, duplicates and invalid business values |
| Batch 2 | Business duplicates, broken foreign keys, formatting issues, invalid date ranges and financial anomalies |
| Batch 3 | Additional invalid values and duplicate records |
| Batch 4 | Invalid numeric, date and timestamp data types |

Individual batches can be executed using:

```bash
python inject_dirty_data.py --batch 1
python inject_dirty_data.py --batch 2
python inject_dirty_data.py --batch 3
python inject_dirty_data.py --batch 4
```

To execute all batches sequentially against a fresh dataset:

```bash
python inject_dirty_data.py --batch all
```

The script retains the original batch-specific random seeds, manifests, backup logic and existing execution safeguards.

Dirty data injection must only be performed against disposable synthetic datasets.

Previously processed datasets must not be reinjected.

### 7.3 AWS S3 Landing Zone

AWS S3 serves as the cloud landing zone for source CSV files.

Python ingestion utilities upload generated datasets to S3 using the AWS SDK.

The landing zone decouples source file generation from warehouse ingestion.

### 7.4 Automated Snowpipe Ingestion

Snowpipe loads source files from S3 into Snowflake Bronze tables.

The ingestion architecture supports:

- Automated file ingestion.
- Asynchronous loading.
- Separation of ingestion and transformation.
- File-level load history.
- Investigation of ingestion failures.

Snowpipe handles source file loading, while dbt manages downstream transformations.

---

## 8. Medallion Architecture

The platform follows a three-layer Bronze, Silver and Gold architecture.

```mermaid
flowchart LR
    A[AWS S3]
    B[BRONZE<br/>Raw Source Data]
    C[SILVER<br/>Cleaned and Validated Data]
    D[GOLD<br/>Analytics-Ready Data]
    E[BI and Analytics]

    A --> B --> C --> D --> E
```

### 8.1 Bronze Layer

The Bronze layer stores raw source data ingested from S3.

Responsibilities include:

- Preserving source records.
- Retaining raw values for investigation.
- Supporting downstream reprocessing.
- Providing a consistent source for transformation.
- Maintaining separation between ingestion and business logic.

Bronze data is stored as physical Snowflake tables.

Data quality issues are intentionally retained at this layer.

### 8.2 Silver Layer

The Silver layer transforms raw source data into standardised and validated datasets.

Transformation responsibilities include:

- Data type conversion.
- String standardisation.
- Whitespace removal.
- Null handling.
- Duplicate detection and removal.
- Primary key validation.
- Foreign key validation.
- Accepted value validation.
- Date range validation.
- Financial value validation.
- Identification of invalid source records.

Snowflake TRY conversion functions support defensive transformation of malformed source values.

Silver models are implemented primarily as dbt views.

The Silver layer separates source data quality handling from downstream analytical business logic.

### 8.3 Gold Layer

The Gold layer contains curated datasets designed for reporting and analytical consumption.

Responsibilities include:

- Dimensional modelling.
- Fact and dimension construction.
- Business metric calculation.
- Historical customer analysis.
- Financial and transactional aggregation.
- Customer and loyalty analytics.

Gold models are materialised as Snowflake tables.

This provides a stable analytical interface for downstream consumers.

---

## 9. Data Modelling

### 9.1 Dimensional Modelling

The Gold layer applies dimensional modelling principles to separate measurable business events from descriptive business attributes.

Fact models represent transactional and measurable events, including:

- Bookings.
- Booking items.
- Payments.
- Refunds.
- Loyalty points transactions.

Dimension models provide descriptive context, including:

- Customers.
- Products.
- Vendors.
- Product categories.
- Customer membership attributes.

Model grain and key relationships are considered during development to reduce duplication and incorrect aggregation.

### 9.2 Slowly Changing Dimensions

The platform incorporates historical customer attributes through Slowly Changing Dimension concepts.

#### SCD Type 1

Type 1 modelling represents the latest available customer attributes.

Typical use cases include:

- Current customer profile information.
- Updated contact information.
- Current customer attributes.

#### SCD Type 2

Type 2 modelling preserves historical changes through effective date ranges.

Typical use cases include:

- Membership tier history.
- Customer status history.
- Historical address information.

Historical records support point-in-time analysis and customer lifecycle reporting.

### 9.3 Business Metrics

The analytical layer supports calculation and analysis of:

- Gross sales.
- Gross margin.
- Booking volume.
- Payment amounts.
- Refund amounts.
- Customer transaction activity.
- Loyalty points earned.
- Loyalty points redeemed.
- Membership tier activity.

Business calculations are centralised within transformation models to improve consistency and reusability.

---

## 10. Data Quality Framework

Data quality is integrated throughout the transformation lifecycle.

The platform uses dbt generic tests and custom SQL tests to validate structural integrity, business rules and relationships.

### 10.1 Structural Validation

- Primary key uniqueness.
- Required field completeness.
- Foreign key relationships.
- Accepted categorical values.
- Valid data types.

### 10.2 Business Rule Validation

- Non-negative financial values where applicable.
- Valid booking date ranges.
- Valid membership tiers.
- Valid transaction statuses.
- Refund amounts relative to associated payments.
- Valid customer and product relationships.

### 10.3 Historical Data Validation

- Effective date consistency.
- Historical customer attribute integrity.
- Valid membership tier history.
- Valid customer status history.

### 10.4 Data Quality Severity

Data quality tests distinguish between critical failures and warning-level issues.

| Severity | Purpose |
|---|---|
| Error | Prevent successful validation when a critical rule fails |
| Warning | Surface issues that require investigation without automatically blocking deployment |

This allows the platform to distinguish deployment-blocking defects from expected or non-critical data quality observations.

### 10.5 Test Execution

Run all models and associated tests:

```bash
dbt build
```

Run data tests independently:

```bash
dbt test
```

Run tests for a selected model:

```bash
dbt test --select model_name
```

---

## 11. CI/CD

CI/CD is established early in the project lifecycle and expanded as transformation models and data quality requirements grow.

GitHub Actions automates validation and production deployment.

### 11.1 Continuous Integration

CI is triggered through the pull request workflow.

The CI process includes:

1. Check out the repository.
2. Configure the Python environment.
3. Install required dependencies.
4. Configure Snowflake authentication.
5. Resolve dbt dependencies.
6. Execute dbt models and tests in the CI environment.
7. Report validation results.

CI uses the isolated TRAVEL_CI_DB environment.

Production transformation objects are not modified during pull request validation.

```mermaid
flowchart TD
    A[Pull Request]
    B[GitHub Actions]
    C[Install Dependencies]
    D[Configure CI Credentials]
    E[dbt Build - CI]
    F{Validation Successful?}
    G[CI Passed]
    H[CI Failed]
    I[Fix and Push Changes]

    A --> B --> C --> D --> E --> F
    F -->|Yes| G
    F -->|No| H --> I --> A
```

### 11.2 Continuous Deployment

CD is triggered following changes merged into the main branch.

The deployment workflow:

1. Checks out the merged code.
2. Configures production authentication.
3. Installs required dependencies.
4. Executes dbt models and tests against PROD.
5. Reports deployment results.

The production deployment command is:

```bash
dbt build --profiles-dir cd --target prod
```

Production models are deployed into TRAVEL_DB.

### 11.3 Deployment Controls

The deployment design incorporates:

- Environment-specific dbt targets.
- Isolated CI transformation objects.
- Environment-specific authentication.
- Restricted CI permissions.
- Automated data quality validation.
- Git-based change history.
- Pull request-based development.

### 11.4 CI Failure Handling

The CI workflow reports unsuccessful builds when critical validation fails.

Failed changes should be investigated and corrected in the feature branch before being merged.

Intentional CI failure testing has been performed to validate the failure-handling behaviour.

---

## 12. Development and Implementation Workflow

The platform follows an environment-first engineering approach.

Infrastructure, security and basic deployment automation are established before full pipeline development.

### Phase 1 — Requirements and Architecture

- Define business domains and analytical requirements.
- Identify source entities and relationships.
- Establish model grain and data contracts.
- Design the cloud ingestion architecture.
- Define Bronze, Silver and Gold responsibilities.
- Select the technology stack.

### Phase 2 — Repository and Development Foundation

- Initialise the Git repository.
- Establish the project directory structure.
- Configure Python virtual environments.
- Define dependency management.
- Configure Git ignore rules.
- Initialise the dbt project.
- Establish configuration and documentation conventions.

### Phase 3 — Environment and Security Setup

- Provision DEV, CI and PROD databases.
- Configure required schemas and compute resources.
- Establish Snowflake roles and service accounts.
- Configure environment-specific permissions.
- Configure dbt connection profiles and targets.
- Establish AWS IAM permissions.
- Configure secrets management.

Environment isolation is established before transformation development begins.

### Phase 4 — Basic CI/CD Foundation

- Configure GitHub Actions.
- Establish pull request validation.
- Configure CI authentication.
- Configure production deployment authentication.
- Create an initial dbt smoke-test model.
- Validate the CI execution environment.
- Validate the production deployment workflow.
- Establish the feature branch and pull request process.

The initial CI/CD framework is intentionally lightweight and expanded as the project grows.

### Phase 5 — Source Data and Ingestion Development

- Generate synthetic relational source datasets.
- Establish clean source data backups.
- Introduce controlled data quality issues.
- Configure the AWS S3 landing zone.
- Configure Snowflake storage integration.
- Configure external stages and file formats.
- Create Bronze source tables.
- Configure Snowpipe ingestion.
- Validate source file loading.

### Phase 6 — Silver Transformation Development

- Define dbt sources.
- Develop standardised transformation models.
- Implement defensive type conversion.
- Implement duplicate handling.
- Implement missing value handling.
- Validate source relationships.
- Develop data quality rules.
- Test transformations in DEV.
- Submit changes through CI.

### Phase 7 — Gold Analytical Development

- Define analytical model grain.
- Develop fact and dimension models.
- Implement historical customer modelling.
- Establish business metric definitions.
- Validate model relationships.
- Implement business rule tests.
- Promote validated models through CI/CD.

### Phase 8 — Data Quality and Deployment Hardening

- Expand generic and custom dbt tests.
- Validate critical business rules.
- Configure appropriate test severity.
- Validate environment isolation.
- Review service account permissions.
- Test CI failure scenarios.
- Validate production deployment.
- Document architecture and operational procedures.


### Phase 9 — Monitoring and Observability

- Establish Snowpipe ingestion monitoring.
- Monitor recent file loading activity.
- Identify failed and partially loaded files.
- Investigate ingestion error messages.
- Implement metadata-driven data quality evaluation.
- Store data quality evaluation results.
- Monitor dbt model and test execution.
- Monitor CI/CD execution through GitHub Actions.
- Document operational monitoring procedures.

Basic monitoring is implemented using Snowflake-native
metadata, SQL-based data quality evaluation, dbt tests
and GitHub Actions execution logs.

Advanced observability and automated operational alerting
remain future enhancements.

---

### Phase 10 — Semantic Layer and AI Analytics

- Define business metrics and aggregation rules using the Gold commercial mart.
- Create a native Snowflake Semantic View in DEV.
- Grant Cortex Analyst access to the development role.
- Reconcile semantic metrics against reference SQL.
- Test natural language queries and unsupported questions in Playground.
- Version-control the semantic view definition.

### Phase 11 — AI Evaluation (Planned)

- Establish benchmark questions and reference SQL.
- Evaluate baseline accuracy and unsupported-question handling.
- Add verified queries and compare results against the baseline.
- Document limitations and evaluation outcomes.

---

## 13. Local Development

### 13.1 Prerequisites

- Python
- Git
- AWS CLI
- Snowflake account
- AWS account
- dbt Core
- Snowflake dbt adapter

### 13.2 Clone the Repository

```bash
git clone https://github.com/youkeefan/travel-data-platform.git
cd travel-data-platform
```

### 13.3 Configure the Python Environment

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install project dependencies using the repository's dependency configuration.

### 13.4 Configure Environment Connections

Configure the required AWS and Snowflake credentials.

Ensure that:

- Local development uses the DEV target.
- CI uses the CI target.
- Production deployment uses the PROD target.
- Credentials are excluded from version control.

### 13.5 Generate Source Data

For a new synthetic dataset:

```bash
python generate_travel_data.py
```

Optionally introduce controlled data quality issues:

```bash
python inject_dirty_data.py --batch all
```

These commands are intended for initial dataset preparation or controlled testing.

Do not regenerate or reinject existing datasets unless intentionally resetting the local test environment.

### 13.6 Upload Source Data

Upload prepared source files to the configured S3 landing zone:

```bash
python ingestion/src/upload_to_s3.py
```

Snowpipe processes the uploaded files into the Bronze layer.

### 13.7 Execute dbt

Navigate to the dbt project directory:

```bash
cd dbt
```

Install dbt package dependencies:

```bash
dbt deps
```

Validate the development connection:

```bash
dbt debug --target dev
```

Build development models and execute tests:

```bash
dbt build --target dev
```

Generate dbt documentation:

```bash
dbt docs generate --target dev
```

Serve documentation locally:

```bash
dbt docs serve
```

### 13.8 Feature Development

Create a feature branch:

```bash
git checkout main
git pull origin main
git checkout -b feature/model-update
```

Develop and validate changes in DEV.

Stage and commit the changes:

```bash
git add .
git commit -m "feat: update transformation models"
```

Push the feature branch:

```bash
git push -u origin feature/model-update
```

Create a pull request targeting main.

GitHub Actions executes the CI workflow.

Review validation results before merging.

Following a successful merge, the CD workflow deploys the updated dbt models to PROD. Semantic view deployment remains manual and DEV-only.

---

## 14. AI-Enabled Analytics — Semantic Layer & Cortex Analyst

### 14.1 Architecture and Scope

The native Snowflake semantic layer extends the existing Gold layer without duplicating its data. The current implementation is deployed in DEV only.

```mermaid
flowchart LR
    A[GOLD.FACT_BOOKING_ITEMS] --> B[GOLD.MART_COMMERCIAL_DAILY]
    B --> C[SEMANTIC.COMMERCIAL_ANALYTICS]
    C --> D[Cortex Analyst]
    E[Business Question] --> D
    D --> F[Generated SQL and Results]
```

| Property | Definition |
|---|---|
| Deployed object | `TRAVEL_DEV_DB.SEMANTIC.COMMERCIAL_ANALYTICS` |
| Source | `GOLD.MART_COMMERCIAL_DAILY` |
| Grain | One row per transaction date and product |
| Source filter | Booking items with positive gross sales |
| Logical tables | 1 |
| Dimensions | 13 |
| Facts | 7 |
| Metrics | 9 |
| Development role | `TRAVEL_DEV_ROLE` |
| AI access | `SNOWFLAKE.CORTEX_ANALYST_USER` database role |
| Version-controlled definition | `snowflake/semantic/01_commercial_analytics.sql` |

### 14.2 Business Metric Governance

Dimensions cover transaction dates, calendar and financial periods, products, destinations, categories and vendors. Facts represent sales, margin, discounts, refunds, booking item counts, room nights and item-level traveller counts.

| Metric | Aggregation |
|---|---|
| Total sales | SUM of gross sales (AUD) |
| Total margin | SUM of gross margin (AUD) |
| Total discount | SUM of discounts (AUD) |
| Total refund | SUM of refunds (AUD) |
| Total booking items | SUM of booking item counts |
| Total room nights | SUM of room nights |
| Total travellers | SUM of item-level traveller counts, not unique individuals |
| Gross margin rate | SUM of margin / NULLIF(SUM of sales, 0) |
| Average booking item value | SUM of sales / NULLIF(SUM of booking item counts, 0) |

Ratios are recalculated from aggregate components rather than averaging precomputed row-level ratios. Distinct booking and customer counts are excluded because they are non-additive at the daily product grain. Accurate unique counts require a suitable lower-grain source.

### 14.3 Development and Reproducibility

The DEV semantic schema and permissions are configured before creating the view. The SQL definition uses schema-qualified names without hardcoding a database. Before executing it, explicitly select the intended database and ensure the target semantic schema, source objects and permissions exist.

For the existing DEV environment:

```sql
USE ROLE TRAVEL_DEV_ROLE;
USE DATABASE TRAVEL_DEV_DB;
USE SCHEMA SEMANTIC;
```

Execute the version-controlled SQL definition when intentionally creating or replacing the view. Do not replace the existing object merely to reproduce the initial tests.

Cortex Analyst is accessed through Snowsight Workspaces using the linked semantic view and Playground. The development role is used for testing. No external LLM API key or separate application is required for this implementation.

### 14.4 Semantic Metric Reconciliation

Five semantic metrics matched direct Gold mart SQL results in the initial DEV test:

| Metric | Reference result |
|---|---:|
| Total sales | AUD 11,468,646.04 |
| Total margin | AUD 2,137,825.03 |
| Booking items | 4,452 |
| Gross margin rate | 18.640605% |
| Average booking item value | AUD 2,576.06604672 |

These are observed synthetic-data results, not fixed expectations for future data refreshes.

### 14.5 Initial Cortex Analyst Functional Testing

| Test | Question | Result |
|---|---|---|
| 1 | What are the total sales? | Passed; exact sales match |
| 2 | What are the total gross sales, gross margin and gross margin rate? | Passed; all three metrics matched |
| 3 | What are the top 5 destinations by total gross sales? | Passed; all five destinations and values matched |
| 4 | Show monthly gross sales and gross margin for 2025. | Partial; seven visible months matched; reference SQL returned 12 months |
| 5 | Which product category has the highest gross margin rate? | Passed; Experiences, 27.429078% |
| 6 | How many unique customers do we have? | Passed; correctly identified unsupported metric |

Five of six functional tests are fully verified. The remaining test is partially verified. This small sample does not establish general AI accuracy. The first query also returned redundant date columns without affecting its sales result.

### 14.6 Limitations and Next Steps

- Semantic view deployment is currently DEV-only; CI and PROD semantic deployment are not implemented.
- Existing GitHub Actions workflows validate and deploy dbt models, not semantic view SQL.
- The portable SQL definition has not yet been tested in CI or PROD.
- The commercial semantic view does not support unique customer counts or all loyalty and financial use cases.
- Formal benchmark evaluation, verified query optimisation and regression testing are planned for Day 8.

---

## 15. Repository Structure

The following represents the main project components.

```text
travel-data-platform/
|
|-- .github/
|   |-- workflows/
|
|-- dbt/
|   |-- models/
|   |-- tests/
|   |-- scripts/
|   |-- dbt_project.yml
|
|-- ingestion/
|   |-- src/
|       |-- upload_to_s3.py
|       |-- upload_test_files.py
|
|-- snowflake/
|   |-- monitoring/
|   |   |-- 04_data_profiling.sql
|   |   |-- snowpipe_monitoring.sql
|   |-- semantic/
|       |-- 01_commercial_analytics.sql
|
|-- data/
|-- data_clean/
|-- docs/
|
|-- generate_travel_data.py
|-- generate_test_files.py
|-- inject_dirty_data.py
|-- .gitignore
|-- README.md
```

### Component Responsibilities

| Component | Responsibility |
|---|---|
| .github/workflows | Automated CI/CD workflows |
| dbt/models | Transformation and analytical models |
| dbt/tests | Custom data quality tests |
| dbt/scripts | Transformation development utilities |
| ingestion/src | Source file ingestion utilities |
| snowflake/monitoring | Ingestion monitoring, data profiling and data quality evaluation |
| snowflake/semantic | Version-controlled semantic views and business metric definitions |
| data | Generated source datasets |
| data_clean | Clean source data backups |
| docs | Data quality manifests and project documentation |
| generate_travel_data.py | Synthetic source data generation |
| generate_test_files.py | Controlled ingestion test file generation |
| inject_dirty_data.py | Consolidated dirty data injection |

---

## 16. Implementation Results

The platform has successfully implemented automated ingestion, isolated transformation environments and CI/CD deployment.

### 16.1 Warehouse Objects

| Environment | Bronze Tables | Silver Views | Gold Tables |
|---|---:|---:|---:|
| PROD | 15 | 21 | 16 |
| DEV | Shared source access | 21 | 16 |
| CI | Shared source access | 21 | 16 |

### 16.2 dbt Project

| Component | Count |
|---|---:|
| dbt Models | 37 |
| Data Tests | 387 |
| Source Definitions | 15 |

### 16.3 Latest Production Build

| Result | Count |
|---|---:|
| Passed | 413 |
| Warnings | 11 |
| Errors | 0 |
| Skipped | 0 |
| Total Executed Nodes | 424 |

The production build completed successfully with no errors.

Warning-level results remain visible for data quality investigation.

### 16.4 Engineering Capabilities

- Automated cloud ingestion.
- Layered ELT transformation.
- Isolated development environments.
- Automated pull request validation.
- Automated production deployment.
- Dimensional modelling.
- Historical customer modelling.
- Defensive data type conversion.
- Automated data quality testing.
- Role-based access control.
- Controlled synthetic data quality scenarios.
- Native semantic view and governed metrics in DEV.
- Natural language analytics with initial SQL reconciliation.

---

## 17. Engineering Practices

### Version Control

All transformation and configuration changes are managed through Git.

Feature branches and pull requests provide traceability and controlled integration.

### Modularity

Transformation logic is separated into reusable models with clearly defined responsibilities.

### Data Quality

Validation rules are implemented alongside transformation logic.

### Environment Isolation

Development, automated validation and production workloads operate in separate transformation environments.

### Security

Access permissions follow the principle of least privilege.

Sensitive credentials are managed outside version control.

### Reproducibility

Synthetic data generation, controlled dirty data injection and version-controlled transformations support repeatable development and testing.

### Documentation

dbt documentation, source definitions and model descriptions support discoverability and maintainability.

### Cost Awareness

The platform uses shared Bronze source access and separates transformation environments to reduce unnecessary raw data duplication.

---


## 18. Monitoring and Observability

Status: Basic monitoring implemented.

The platform provides operational visibility across
data ingestion, data quality, transformation execution
and automated deployment.

### 18.1 Ingestion Monitoring

Implemented in:

`snowflake/monitoring/snowpipe_monitoring.sql`

Snowflake ACCOUNT_USAGE.COPY_HISTORY provides file-level
ingestion visibility.

Monitoring capabilities include:

- Recent file loading activity over the previous 24 hours.
- Failed and partially loaded files over the previous 7 days.
- Snowpipe and target table identification.
- File-level ingestion status.
- Error counts and first error messages.
- Load timestamps for incident investigation.

These queries support operational troubleshooting
and ingestion failure investigation.

ACCOUNT_USAGE metadata may have reporting latency
and should not be treated as real-time monitoring.

### 18.2 Data Profiling and Quality Monitoring

Implemented in:

`snowflake/monitoring/04_data_profiling.sql`

The platform includes:

- Source data profiling.
- SQL-based automated data quality evaluation.
- A dedicated data quality results table.
- Identification of data quality issues.

These capabilities complement the dbt transformation
and business rule testing framework.

### 18.3 Transformation Monitoring

dbt provides execution-level visibility through:

- Model execution results.
- Data test results.
- Error and warning severity.
- Failed and skipped model identification.
- Execution logs.

The project contains 387 dbt data tests covering
structural integrity, relationships and business rules.

### 18.4 CI/CD Monitoring

GitHub Actions provides visibility into automated
validation and production deployment.

Monitoring capabilities include:

- Workflow execution status.
- Pull request validation results.
- Production deployment results.
- Step-level execution logs.
- Failed workflow investigation.

Critical CI failures prevent successful validation
and should be resolved before production deployment.

### 18.5 Monitoring Coverage

| Area | Implementation | Status |
|---|---|---|
| Ingestion history | Snowflake COPY_HISTORY | Implemented |
| Ingestion failure detection | SQL monitoring queries | Implemented |
| Data profiling | SQL profiling framework | Implemented |
| Data quality evaluation | SQL-based quality engine | Implemented |
| Data quality results | Dedicated results table | Implemented |
| Transformation validation | dbt models and tests | Implemented |
| CI/CD monitoring | GitHub Actions logs | Implemented |
| Automated freshness monitoring | Future enhancement | Planned |
| Compute and cost monitoring | Future enhancement | Planned |
| Centralised observability | Future enhancement | Planned |
| Automated operational alerting | Future enhancement | Planned |

### 18.6 Future Enhancements

Potential operational improvements include:

- Automated source freshness checks.
- Centralised operational monitoring views.
- Automated failure notifications.
- Data quality trend dashboards.
- Warehouse usage and cost monitoring.
- Pipeline scheduling and orchestration.
- Operational incident management procedures.

The current implementation provides a foundational
monitoring capability without introducing unnecessary
infrastructure complexity.

---

## 19. Project Status

| Component | Status |
|---|---|
| Architecture Design | Implemented |
| Synthetic Data Generation | Implemented |
| Dirty Data Injection | Implemented |
| AWS S3 Integration | Implemented |
| Snowpipe Ingestion | Implemented |
| Bronze Layer | Implemented |
| Silver Layer | Implemented |
| Gold Layer | Implemented |
| Dimensional Modelling | Implemented |
| Historical Data Modelling | Implemented |
| Data Quality Testing | Implemented |
| DEV / CI / PROD Isolation | Implemented |
| Role-Based Access Control | Implemented |
| Continuous Integration | Implemented |
| Continuous Deployment | Implemented |
| CI Failure Validation | Implemented |
| Basic Monitoring and Observability | Implemented |
| Advanced Observability and Alerting | Future Enhancement |
| Semantic View | Implemented in DEV |
| Cortex Analyst | Implemented in DEV |
| Initial AI Functional Testing | Five passed; one partially verified |
| Formal AI Evaluation and Verified Queries | Planned — Day 8 |
| Semantic CI/CD and PROD Deployment | Future Enhancement |

---

### Project Roadmap

| Day | Scope | Status |
|---|---|---|
| 1 | Architecture and data generation | Completed |
| 2 | Ingestion and Bronze | Completed |
| 3 | Silver and data cleaning | Completed |
| 4 | Data profiling and Gold | Completed |
| 5 | Environment management and CI/CD hardening | Completed |
| 6 | Lightweight monitoring and observability | Completed |
| 7 | Semantic Views and Cortex Analyst | DEV implementation completed; one functional test partially verified |
| 8 | AI accuracy evaluation and documentation | Planned |

The roadmap records learning milestones; Section 12 describes the recommended environment-first implementation sequence.

---

## 20. Conclusion

The Travel Data Platform demonstrates the design and implementation of an end-to-end cloud data engineering solution using modern data engineering technologies.

The project combines automated ingestion, modular ELT transformations, dimensional modelling, data quality management, environment isolation and CI/CD into a unified architecture.

Its design emphasises engineering reliability, maintainability, security and reproducibility while supporting scalable downstream business analytics. The DEV semantic layer extends these foundations to governed natural language analytics, with formal AI evaluation and production semantic deployment remaining future work.

---

## Author

Yujia Fan

Data Analytics | Analytics Engineering | Data Engineering
