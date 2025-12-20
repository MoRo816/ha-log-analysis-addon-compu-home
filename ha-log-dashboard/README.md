# Log Analysis Dashboard Add-on

A Home Assistant add-on providing a web-based dashboard for managing and filtering issues extracted from Home Assistant error logs.

## Features

- 📊 Visual dashboard for issue management
- 🔍 Filter issues by integration, status, severity, and more
- 📝 View detailed issue information and recommendations
- 🏷️ Tag and categorize issues
- 📈 Track issue history and trends
- 🔗 Integration with Home Assistant API
- 📱 Responsive web interface

## Installation

1. Add this repository to your Home Assistant:
   - Navigate to **Settings** → **Add-ons** → **Add-on Store**
   - Click the **⋮** menu and select **Repositories**
   - Add: `https://github.com/ncecowboy/ha-log-analysis-addon`
   - Click **Add**

2. Install the add-on:
   - Find "Log Analysis Dashboard" in the add-on store
   - Click **Install**
   - Start the add-on
   - Open the web interface from the add-on info page

## Configuration

Basic configuration options are available in the add-on settings:
- **log_level**: Set logging level (debug, info, warning, error)
- **port**: Web interface port (default: 8080)

See [DOCS.md](DOCS.md) for detailed configuration and usage information.

## Usage

Once started, access the dashboard at:
```
http://[YOUR_HOME_ASSISTANT_IP]:8080
```

The dashboard provides:
- **Issues List**: View all detected issues from log analysis
- **Filters**: Filter by integration, status, severity, date range
- **Issue Details**: Click an issue to see full details and recommendations
- **Issue Management**: Mark as resolved, change status, add notes
- **Export**: Download issue reports

## Support

For issues, feature requests, or documentation, visit the [repository](https://github.com/ncecowboy/ha-log-analysis-addon).

## License

See LICENSE file in the repository.