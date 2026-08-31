# GramArtha — Downloaded Product Quick Start

This folder is copied into the verified **GramArtha Judge Package** attached to the versioned GitHub software release.

The primary evaluator asset is deliberately named:

`GramArtha-v0.7.2-Judge-Package.zip`

so a reviewer does not need to guess which release file to download.

## Fastest option

If you only want to evaluate the product, use the hosted application:

https://gramartha-west-bengal.onrender.com/ui/

## Run the downloaded Judge Package locally

The Judge Package already contains GramArtha's **public-safe prepared SQLite runtime databases**. Restricted HCES/ASUSE respondent microdata and raw acquisition workspaces are not included.

Requirements:

- Python 3.12+
- Internet access on the first launch so Python dependencies can be installed
- A modern browser

### macOS

Double-click `START_GRAMARTHA.command`.

If macOS blocks the first launch, right-click the file, choose **Open**, and confirm once.

### Linux

Run:

```bash
chmod +x start_gramartha.sh
./start_gramartha.sh
```

### Windows

Double-click `START_GRAMARTHA.bat`.

The launcher creates a private `.gramartha-venv` inside the extracted package on first use, installs the released project dependencies, starts the local service at `127.0.0.1:8765`, waits for `/health`, and opens the product UI.

## Local endpoints

- Product: http://127.0.0.1:8765/ui/
- API docs: http://127.0.0.1:8765/docs
- Health: http://127.0.0.1:8765/health

## What is included

The judge package contains:

- the released backend and frontend;
- prepared public-safe economic and OSM runtime databases;
- architecture, validation, limitations and implementation-status documents;
- launchers for macOS, Linux and Windows;
- license and third-party data notices.

The GitHub release also publishes the Python wheel, source distribution, reproducible public-runtime archive, CycloneDX SBOM, release manifest and SHA-256 checksums as separate audit artifacts.

## Integrity

Before publication, GitHub Actions reruns linting, compilation, all automated tests, a minimum coverage gate, dependency vulnerability audit, SQLite integrity checks, a clean-wheel install test and a release-boundary scan designed to prevent raw/restricted evidence surfaces from entering the public product archive.
