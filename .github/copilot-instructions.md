# GitHub Copilot Instructions for ZappiToInflux

## Project Overview
This is a Python script that collects data from MyEnergi Zappi electric vehicle chargers via their API and sends it to InfluxDB for visualization in Grafana. The project monitors energy consumption, generation, and charging data.

## Key Technologies & Dependencies
- **Python 3.13+** - Main runtime
- **requests** - HTTP client for API calls
- **InfluxDB** - Time-series database for data storage
- **MyEnergi API** - Source of Zappi device data
- **Grafana** - Data visualization (external dependency)

## Code Style & Standards
- Follow **PEP 8** Python style guidelines
- Use **type hints** for function parameters and return values
- Write **docstrings** for all functions using Google style
- Keep functions focused and single-purpose
- Use meaningful variable names that describe their purpose
- Handle exceptions gracefully with specific error messages

## Project Structure
```
zappitoinflux.py          # Main script
settings.json.example     # Configuration template
settings.json            # User configuration (gitignored)
requirements.txt         # Python dependencies
pylintrc                 # Linting configuration
```

## Key Functions & Their Purposes

### `get_data_from_myenergi(url)`
- Fetches data from MyEnergi API using HTTP Digest authentication
- Handles authentication errors and timeouts
- Returns JSON response data

### `dayhour_results(year, month, day, hour=None)`
- Retrieves historical energy data for specific time periods
- Calculates daily/hourly totals for charge, import, export, and generation
- Converts raw values to kWh (dividing by 3600/1000)

### `parse_zappi_data()`
- Main data processing function
- Combines real-time Zappi data with historical day/hour data
- Filters fields based on configuration if specified
- Returns processed data dictionary

### `send_data_to_influx(data)`
- Formats data for InfluxDB line protocol
- Sends data via HTTP POST to InfluxDB
- Handles connection errors and timeouts
- Provides minimal visual feedback

## Configuration Management
- All settings stored in `settings.json` (not version controlled)
- Use `settings.json.example` as template
- Include validation for required fields
- Support for optional configuration parameters with sensible defaults

## Error Handling Patterns
- Use try/catch blocks for file operations and network requests
- Provide clear error messages for configuration issues
- Exit gracefully with appropriate exit codes
- Log errors but don't crash the main loop

## API Integration Details
- **MyEnergi API**: Uses HTTP Digest authentication
- **InfluxDB**: Uses HTTP basic authentication with line protocol
- **User-Agent**: Set to "Wget/1.14 (linux-gnu)" for MyEnergi compatibility
- **Timeouts**: Configurable per service (default 5 seconds)

## Data Processing
- Convert raw energy values from Wh to kWh
- Round values to 4 decimal places for precision
- Combine real-time and historical data
- Filter fields based on user configuration

## Command Line Interface
- `--dump`: Output raw Zappi data as JSON
- `--print`: Output processed data as JSON instead of sending to InfluxDB
- Support for graceful shutdown with Ctrl+C

## Development Guidelines
- When adding new features, maintain backward compatibility
- Test with both `--dump` and `--print` flags
- Ensure configuration changes are documented in README
- Add appropriate error handling for new API endpoints
- Consider rate limiting and API quotas

## Security Considerations
- Never commit `settings.json` with real credentials
- Use appropriate file permissions (600) for configuration files
- Validate all input data from external APIs
- Handle authentication failures gracefully

## Performance Considerations
- Use configurable intervals for data collection
- Implement proper sleep timing to avoid drift
- Handle network timeouts appropriately
- Provide minimal visual feedback to avoid performance impact

## Testing Approach
- Test with `--print` flag to verify data processing
- Use `--dump` to inspect raw API responses
- Test error conditions (network failures, invalid config)
- Verify InfluxDB data format and timestamps

## Common Patterns
- Use `datetime.now()` for timestamps
- Format time strings consistently
- Handle missing or null values in API responses
- Use dictionary comprehensions for data filtering
- Implement signal handlers for graceful shutdown

## When Making Changes
- Always test configuration changes with example data
- Ensure new fields are properly documented
- Consider impact on existing Grafana dashboards
- Validate InfluxDB line protocol format
- Test with different Zappi firmware versions if possible
