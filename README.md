# Astro Scripts Repository 🚀

This repository contains my collection of automation and utility scripts used for local development and system management.

## Scripts Overview

### [clean-backups.ps1](https://github.com/zabido/astro/blob/main/clean-backups.ps1)
**Description:** Automatically identifies and removes outdated backup files from specified directories to save disk space while keeping the most recent versions.

### [collect-logs.ps1](https://github.com/zabido/astro/blob/main/collect-logs.ps1)
**Description:** Aggregates log files from multiple service folders into a single timestamped archive for easier troubleshooting and monitoring.

### [deploy-app.ps1](https://github.com/zabido/astro/blob/main/deploy-app.ps1)
**Description:** A deployment wrapper that automates the process of stopping services, copying build artifacts, and restarting the application environment.

### [sync-work.ps1](https://github.com/zabido/astro/blob/main/sync-work.ps1)
**Description:** Synchronizes local development folders with remote storage or cloud drives, ensuring that work-in-progress files are always backed up.

---

## How to use in PowerShell

To run these scripts easily, ensure your execution policy is set to allow local scripts:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser