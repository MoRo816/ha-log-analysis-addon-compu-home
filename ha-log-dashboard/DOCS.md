# Log Analysis Dashboard - Documentation

## Overview

The Log Analysis Dashboard is a web-based interface for managing issues detected in Home Assistant error logs. It integrates with the Home Assistant Log Analysis tool to provide a centralized place to view, filter, and manage issues.

## Installation & Setup

### Prerequisites

- Home Assistant 2023.12 or later
- The Home Assistant Log Analysis custom component installed
- Network access to Home Assistant

### Installation Steps

1. **Add the Repository**
   - In Home Assistant, go to Settings → Add-ons → Add-on Store
   - Click the menu (⋮) and select "Repositories"
   - Paste: `https://github.com/ncecowboy/ha-log-analysis-addon`
   - Click "Add"

2. **Install the Add-on**
   - Search for "Log Analysis Dashboard"
   - Click "Install"
   - Wait for installation to complete

3. **Configure the Add-on**
   - Go to the add-on's Configuration tab
   - Adjust settings as needed (log_level, port)
   - Click "Save"

4. **Start the Add-on**
   - Click the "Start" button
   - Wait for it to start (check logs if it fails)
   - Click "Open Web UI" to access the dashboard

## Configuration

### Available Options

```yaml
log_level: debug|info|warning|error
port: 8080  # Port to run the web server on
```

### Environment Variables

The add-on automatically sets:
- `HA_CONFIG_PATH`: Path to Home Assistant config directory
- `HA_DATA_PATH`: Path to add-on data directory
- `LOG_LEVEL`: Logging level
- `PORT`: Web server port

## Usage Guide

### Dashboard Overview

The main dashboard displays:
- **Issue Statistics**: Total issues, critical count, resolved count
- **Recent Issues**: Latest detected issues
- **Integration Distribution**: Issues by integration
- **Severity Breakdown**: Issues grouped by severity level

### Filtering Issues

Use the filter panel to narrow down issues:

1. **By Integration**
   - Select one or more integrations from the dropdown
   - Shows only issues from selected integrations

2. **By Status**
   - New: Recently detected issues
   - Investigating: Issues being looked into
   - Ignored: Dismissed issues
   - Resolved: Fixed issues

3. **By Severity**
   - Critical: Requires immediate attention
   - Warning: Should be addressed
   - Info: For reference

4. **By Date Range**
   - First detected: When the issue first appeared
   - Last seen: Most recent occurrence

5. **Search**
   - Free-text search across issue descriptions
   - Searches integration names and recommendations

### Issue Details

Click an issue to view:
- **Full Description**: Complete error message
- **Integration**: Which integration caused the issue
- **Timeline**: When first detected and last seen
- **Count**: How many times this error has occurred
- **Recommendation**: Suggested action to resolve
- **Log Excerpts**: Related log entries
- **Related Issues**: Similar or connected issues

### Managing Issues

From an issue detail view:

1. **Change Status**
   - Set to: New, Investigating, Ignored, or Resolved
   - Status persists across sessions

2. **Add Notes**
   - Document investigation progress
   - Store solutions or workarounds
   - Add reminders or follow-up actions

3. **Mark as Resolved**
   - Quick button to mark issue as resolved
   - Optionally add a resolution note

4. **Export/Share**
   - Export issue as JSON
   - Share issue URL with others
   - Generate a report of related issues

### Dashboard Actions

**Export Issues**
- Export all visible issues (after filters) as CSV or JSON
- Useful for reports or sharing with team

**Clear History**
- Remove resolved issues from dashboard
- Can be filtered before clearing

**Refresh Data**
- Manually refresh from the log analysis data source

## API Endpoints

The add-on provides REST API endpoints for integration with other tools:

```
GET  /api/issues              - List all issues (with filtering)
GET  /api/issues/{id}         - Get issue details
POST /api/issues/{id}/status  - Update issue status
POST /api/issues/{id}/notes   - Add notes to issue
GET  /api/integrations        - List all integrations with issues
GET  /api/statistics          - Get dashboard statistics
GET  /api/export              - Export issues
```

See API documentation at `/api/docs` once the add-on is running.

## Data Storage

Issues and notes are stored in:
- `/data/issues.json` - Issue data and metadata
- `/data/notes.json` - User notes on issues

These files persist across add-on restarts and are backed up by Home Assistant.

## Troubleshooting

### Dashboard Won't Load

1. Check add-on logs for errors:
   - Go to Add-ons → Log Analysis Dashboard → Logs
   - Look for connection or startup errors

2. Verify network access:
   - Ensure you're using the correct IP and port
   - Check firewall settings

3. Try restarting the add-on:
   - Click "Stop" then "Start" on the add-on page

### No Issues Appearing

1. Run the Home Assistant Log Analysis tool first:
   - It must generate the issues data
   - Check that it has found and processed logs

2. Verify file permissions:
   - Log Analysis Dashboard needs read access to Home Assistant data
   - Check add-on logs for permission errors

3. Refresh the dashboard:
   - Press F5 or click the Refresh button
   - Clear browser cache if needed

### Performance Issues

1. Reduce the number of issues displayed:
   - Use filters to narrow down
   - Archive/resolve old issues

2. Check browser console for errors:
   - Right-click → Inspect → Console tab
   - Report any JavaScript errors

3. Check system resources:
   - Ensure Home Assistant has sufficient RAM
   - Check available disk space

## Advanced Configuration

### Custom Port

To use a different port (e.g., 9000):

1. Go to Configuration → yaml
2. Modify the `port` option to desired value
3. Save and restart the add-on
4. Access at new port: `http://[IP]:9000`

### Reverse Proxy Setup

To access through a reverse proxy:

1. Configure your reverse proxy to forward to `http://addon_host:8080`
2. Set appropriate headers:
   ```
   X-Forwarded-For: [client_ip]
   X-Forwarded-Proto: https
   X-Forwarded-Host: [your_domain]
   ```
3. Access through your proxy URL

## Development & Contributing

To contribute to the add-on:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally using Home Assistant dev environment
5. Submit a pull request

See the main repository for development guidelines.

## Support & Issues

For problems or feature requests:
- GitHub Issues: https://github.com/ncecowboy/ha-log-analysis-addon/issues
- Home Assistant Community: https://community.home-assistant.io

## License

GNU General Public License v3.0 - See LICENSE file in repository.