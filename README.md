# Report Portal Alert Script

This Python script interacts with the Report Portal API to fetch and analyze test execution launches. It provides various output formats and filtering capabilities to help monitor and analyze test results.

## Features

- Fetch launches from Report Portal with advanced filtering
- Multiple output formats:
  - Table format (default)
  - JSON format
  - Summary format
  - Detailed format
- Failed test case retrieval with links
- Attribute-based filtering
- Caching support to improve performance
- Configurable through environment variables or config file

## Prerequisites

- Python 3.6 or higher
- Required Python packages (install via pip):
  ```bash
  pip install -r requirements.txt
  ```

## Configuration

The script can be configured in two ways:
1. Using a `config.json` file
2. Using environment variables

### Config File Structure
```json
{
    "base_url": "https://your-reportportal-instance",
    "token": "your-api-token"
}
```

### Environment Variables
- `REPORT_PORTAL_URL`: Base URL of your Report Portal instance
- `REPORT_PORTAL_TOKEN`: Your Report Portal authentication token

## Usage

Basic filtering for project:
```bash
python report_alert.py PROW
```

Disable SSL verification:
```bash
python report_alert.py PROW --no-verify
```

With --attr filters:
```bash
python report_alert.py PROW --attr version_installed=4.12.0-0.nightly-2025-01-25-135326   
```

View failed test cases:
```bash
python report_alert.py PROW --status FAILED 
```

With --attr, --test-name(-tn) and --status(-s) filters:
```bash
python ./report_alert.py prow --attr version_installed=4.12.0-0.nightly-2025-01-25-135326 --test-name installer --status FAILED  
```

With filters --attr, --test-name(-tn), --status(-s) and excluding --name(-n) filters:
```bash
python ./report_alert.py prow --attr version_installed=4.12.0-0.nightly-2025-01-25-135326 --test-name nstaller --status FAILED -n automated-release  
```

### Command Line Arguments

- `PROJECT`: (Required) Project name in Report Portal, only the name of the project is passed, it has no preceeding flag
- `--token`: Authentication token (overrides config file)
- `-n, --name`: Filter launches by name (partial match)
- `-s, --status`: Filter launches by status (PASSED, FAILED, STOPPED, INTERRUPTED, IN_PROGRESS)
- `-t, --tags`: Filter launches by tags
- `--start-from`: Fetch launches from this date (YYYY-MM-DD)
- `--start-to`: Fetch launches up to this date (YYYY-MM-DD)
- `--attr`: Filter by attributes in KEY=VALUE format
- `-p, --page`: Page number (default: 1)
- `-l, --limit`: Number of launches per page (default: 20)
- `-o, --output`: Output format (json, table, summary, detailed)
- `--failed-tests`: Fetch failed test cases with links from launches
- `-tn, --test-name`: Filter launches by test name
- `--reset-cache`: Clear the cache and fetch fresh data
- `--cache-hours`: Cache expiry time in hours (default: 24)
- `--no-verify`: Will disable SSL verification

## Output Formats

1. Table Format (Default)
   - Displays launches in a formatted table
   - Shows Launch ID, Name, Status, Start Time, and Failed Tests count

2. JSON Format
   - Outputs raw JSON data
   - Useful for programmatic processing

3. Summary Format
   - Shows total launches count
   - Displays status summary

4. Detailed Format
   - Shows detailed information for each launch
   - Includes launch ID, name, status, start time, tags, and attributes

## Caching

The script implements caching to improve performance:
- Cache duration: 24 hours by default
- Cache location: `~/.reportportal_cache`
- Use `--reset-cache` to clear existing cache
- Configure cache duration with `--cache-hours`
