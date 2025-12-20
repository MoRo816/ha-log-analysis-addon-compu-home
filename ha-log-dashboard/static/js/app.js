/**
 * Main Application JavaScript for Home Assistant Log Analysis Dashboard
 * Handles UI interactions, data loading, and view management
 */

class DashboardApp {
    constructor() {
        this.currentView = 'dashboard';
        this.currentPage = 1;
        this.pageSize = 20;
        this.filters = {};
        this.init();
    }

    /**
     * Initialize the application
     */
    async init() {
        this.setupEventListeners();
        await this.loadDashboard();
    }

    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = e.target.dataset.view;
                this.switchView(view);
            });
        });

        // Issues view
        const createIssueBtn = document.getElementById('btn-create-issue');
        if (createIssueBtn) {
            createIssueBtn.addEventListener('click', () => this.showCreateIssueModal());
        }

        const applyFiltersBtn = document.getElementById('btn-apply-filters');
        if (applyFiltersBtn) {
            applyFiltersBtn.addEventListener('click', () => this.applyFilters());
        }

        const clearFiltersBtn = document.getElementById('btn-clear-filters');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => this.clearFilters());
        }

        // Pagination
        const prevPageBtn = document.getElementById('btn-prev-page');
        if (prevPageBtn) {
            prevPageBtn.addEventListener('click', () => this.previousPage());
        }

        const nextPageBtn = document.getElementById('btn-next-page');
        if (nextPageBtn) {
            nextPageBtn.addEventListener('click', () => this.nextPage());
        }

        // Modal
        const closeModalBtn = document.getElementById('btn-close-modal');
        if (closeModalBtn) {
            closeModalBtn.addEventListener('click', () => this.closeModal());
        }

        const cancelModalBtn = document.getElementById('btn-modal-cancel');
        if (cancelModalBtn) {
            cancelModalBtn.addEventListener('click', () => this.closeModal());
        }

        // Close modal when clicking outside
        const modal = document.getElementById('issue-modal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal();
                }
            });
        }
    }

    /**
     * Switch between views
     * @param {string} viewName - Name of the view to switch to
     */
    async switchView(viewName) {
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.view === viewName) {
                link.classList.add('active');
            }
        });

        // Update views
        document.querySelectorAll('.view').forEach(view => {
            view.classList.remove('active');
        });
        const targetView = document.getElementById(`${viewName}-view`);
        if (targetView) {
            targetView.classList.add('active');
        }

        this.currentView = viewName;

        // Load data for the view
        switch (viewName) {
            case 'dashboard':
                await this.loadDashboard();
                break;
            case 'issues':
                await this.loadIssues();
                break;
            case 'integrations':
                await this.loadIntegrations();
                break;
            case 'statistics':
                await this.loadStatistics();
                break;
        }
    }

    /**
     * Load dashboard data
     */
    async loadDashboard() {
        try {
            this.showLoading();

            // Load overall statistics
            const stats = await api.getStatistics();
            this.updateDashboardStats(stats);

            // Load recent issues
            const issues = await api.getIssues({ limit: 5, sort: 'updated_at', order: 'desc' });
            this.displayRecentIssues(issues.items || []);

            // Load chart data
            await this.loadDashboardCharts();

            this.hideLoading();
        } catch (error) {
            this.showNotification('Failed to load dashboard data: ' + error.message, 'error');
            this.hideLoading();
        }
    }

    /**
     * Update dashboard statistics cards
     * @param {object} stats - Statistics data
     */
    updateDashboardStats(stats) {
        document.getElementById('stat-total-issues').textContent = stats.total_issues || 0;
        document.getElementById('stat-critical-issues').textContent = stats.critical_issues || 0;
        document.getElementById('stat-warning-issues').textContent = stats.warning_issues || 0;
        document.getElementById('stat-resolved-issues').textContent = stats.resolved_issues || 0;
    }

    /**
     * Display recent issues
     * @param {Array} issues - List of recent issues
     */
    displayRecentIssues(issues) {
        const container = document.getElementById('recent-issues-list');
        
        if (issues.length === 0) {
            container.innerHTML = '<div class="loading">No recent issues found</div>';
            return;
        }

        container.innerHTML = issues.map(issue => `
            <div class="issue-item" onclick="app.showIssueDetail('${issue.id}')">
                <div class="issue-header">
                    <h4 class="issue-title">${this.escapeHtml(issue.title)}</h4>
                    <div class="issue-badges">
                        <span class="badge badge-${issue.severity}">${issue.severity}</span>
                        <span class="badge badge-${issue.status}">${issue.status}</span>
                    </div>
                </div>
                <p class="issue-description">${this.escapeHtml(issue.description || '')}</p>
                <div class="issue-meta">
                    <span>Updated: ${this.formatDate(issue.updated_at)}</span>
                </div>
            </div>
        `).join('');
    }

    /**
     * Load dashboard charts
     */
    async loadDashboardCharts() {
        try {
            const [severityStats, statusStats] = await Promise.all([
                api.getStatisticsBySeverity(),
                api.getStatisticsByStatus()
            ]);

            this.displaySeverityChart(severityStats);
            this.displayStatusChart(statusStats);
        } catch (error) {
            console.error('Failed to load charts:', error);
        }
    }

    /**
     * Display severity chart (simple bar representation)
     * @param {Array} data - Severity statistics
     */
    displaySeverityChart(data) {
        const container = document.getElementById('severity-chart');
        
        if (!data || data.length === 0) {
            container.innerHTML = '<div class="chart-placeholder">No data available</div>';
            return;
        }

        container.innerHTML = data.map(item => `
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-weight: 500; text-transform: capitalize;">${item.severity}</span>
                    <span>${item.count} (${item.percentage.toFixed(1)}%)</span>
                </div>
                <div style="background-color: #e0e0e0; height: 24px; border-radius: 4px; overflow: hidden;">
                    <div style="background-color: var(--color-${item.severity}); width: ${item.percentage}%; height: 100%;"></div>
                </div>
            </div>
        `).join('');
    }

    /**
     * Display status chart (simple bar representation)
     * @param {Array} data - Status statistics
     */
    displayStatusChart(data) {
        const container = document.getElementById('status-chart');
        
        if (!data || data.length === 0) {
            container.innerHTML = '<div class="chart-placeholder">No data available</div>';
            return;
        }

        container.innerHTML = data.map(item => `
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-weight: 500; text-transform: capitalize;">${item.status.replace('_', ' ')}</span>
                    <span>${item.count} (${item.percentage.toFixed(1)}%)</span>
                </div>
                <div style="background-color: #e0e0e0; height: 24px; border-radius: 4px; overflow: hidden;">
                    <div style="background-color: var(--color-primary); width: ${item.percentage}%; height: 100%;"></div>
                </div>
            </div>
        `).join('');
    }

    /**
     * Load issues list
     */
    async loadIssues() {
        try {
            this.showLoading();

            const params = {
                skip: (this.currentPage - 1) * this.pageSize,
                limit: this.pageSize,
                ...this.filters
            };

            const response = await api.getIssues(params);
            this.displayIssues(response);

            this.hideLoading();
        } catch (error) {
            this.showNotification('Failed to load issues: ' + error.message, 'error');
            this.hideLoading();
        }
    }

    /**
     * Display issues list
     * @param {object} response - Issues response
     */
    displayIssues(response) {
        const container = document.getElementById('issues-list');
        const items = response.items || [];

        if (items.length === 0) {
            container.innerHTML = '<div class="loading">No issues found</div>';
            return;
        }

        container.innerHTML = items.map(issue => `
            <div class="issue-item" onclick="app.showIssueDetail('${issue.id}')">
                <div class="issue-header">
                    <h4 class="issue-title">${this.escapeHtml(issue.title)}</h4>
                    <div class="issue-badges">
                        <span class="badge badge-${issue.severity}">${issue.severity}</span>
                        <span class="badge badge-${issue.status}">${issue.status}</span>
                    </div>
                </div>
                <p class="issue-description">${this.escapeHtml(issue.description || '')}</p>
                <div class="issue-meta">
                    <span>Category: ${this.escapeHtml(issue.category || 'N/A')}</span>
                    <span>Created: ${this.formatDate(issue.created_at)}</span>
                    <span>Updated: ${this.formatDate(issue.updated_at)}</span>
                </div>
            </div>
        `).join('');

        // Update pagination
        this.updatePagination(response);
    }

    /**
     * Update pagination controls
     * @param {object} response - API response with pagination info
     */
    updatePagination(response) {
        const pageInfo = document.getElementById('page-info');
        const prevBtn = document.getElementById('btn-prev-page');
        const nextBtn = document.getElementById('btn-next-page');

        if (pageInfo) {
            pageInfo.textContent = `Page ${response.page || 1}`;
        }

        if (prevBtn) {
            prevBtn.disabled = this.currentPage <= 1;
        }

        if (nextBtn) {
            const hasMore = (response.page * response.page_size) < response.total;
            nextBtn.disabled = !hasMore;
        }
    }

    /**
     * Apply filters
     */
    applyFilters() {
        this.filters = {
            status: document.getElementById('filter-status').value,
            severity: document.getElementById('filter-severity').value,
            search: document.getElementById('filter-search').value,
        };
        this.currentPage = 1;
        this.loadIssues();
    }

    /**
     * Clear filters
     */
    clearFilters() {
        document.getElementById('filter-status').value = '';
        document.getElementById('filter-severity').value = '';
        document.getElementById('filter-search').value = '';
        this.filters = {};
        this.currentPage = 1;
        this.loadIssues();
    }

    /**
     * Go to previous page
     */
    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.loadIssues();
        }
    }

    /**
     * Go to next page
     */
    nextPage() {
        this.currentPage++;
        this.loadIssues();
    }

    /**
     * Load integrations
     */
    async loadIntegrations() {
        try {
            this.showLoading();

            const response = await api.getIntegrations({ limit: 50, sort_by: 'issue_count', order: 'desc' });
            this.displayIntegrations(response.items || []);

            this.hideLoading();
        } catch (error) {
            this.showNotification('Failed to load integrations: ' + error.message, 'error');
            this.hideLoading();
        }
    }

    /**
     * Display integrations grid
     * @param {Array} integrations - List of integrations
     */
    displayIntegrations(integrations) {
        const container = document.getElementById('integrations-grid');

        if (integrations.length === 0) {
            container.innerHTML = '<div class="loading">No integrations found</div>';
            return;
        }

        container.innerHTML = integrations.map(integration => `
            <div class="integration-card" onclick="app.showIntegrationDetail('${integration.name}')">
                <h3 class="integration-name">${this.escapeHtml(integration.display_name || integration.name)}</h3>
                <div class="integration-stats">
                    <div class="integration-stat">Total: <strong>${integration.issue_count}</strong></div>
                    <div class="integration-stat">Critical: <strong>${integration.critical_count}</strong></div>
                    <div class="integration-stat">Warning: <strong>${integration.warning_count}</strong></div>
                    <div class="integration-stat">Info: <strong>${integration.info_count}</strong></div>
                </div>
            </div>
        `).join('');
    }

    /**
     * Load statistics
     */
    async loadStatistics() {
        try {
            this.showLoading();

            const [integrationStats, trendData] = await Promise.all([
                api.getStatisticsByIntegration({ limit: 20 }),
                api.getTrendStatistics({ period: 'day', days: 30 })
            ]);

            this.displayIntegrationStats(integrationStats);
            this.displayTrendChart(trendData);

            this.hideLoading();
        } catch (error) {
            this.showNotification('Failed to load statistics: ' + error.message, 'error');
            this.hideLoading();
        }
    }

    /**
     * Display integration statistics table
     * @param {Array} data - Integration statistics
     */
    displayIntegrationStats(data) {
        const container = document.getElementById('integration-stats');

        if (!data || data.length === 0) {
            container.innerHTML = '<div class="loading">No statistics available</div>';
            return;
        }

        container.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Integration</th>
                        <th>Total Issues</th>
                        <th>Critical</th>
                        <th>Warning</th>
                        <th>Info</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map(item => `
                        <tr>
                            <td>${this.escapeHtml(item.display_name || item.integration_name)}</td>
                            <td>${item.total_issues}</td>
                            <td>${item.critical_count}</td>
                            <td>${item.warning_count}</td>
                            <td>${item.info_count}</td>
                            <td>${item.percentage.toFixed(1)}%</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    /**
     * Display trend chart
     * @param {object} data - Trend data
     */
    displayTrendChart(data) {
        const container = document.getElementById('trend-chart');

        if (!data || !data.data_points || data.data_points.length === 0) {
            container.innerHTML = '<div class="chart-placeholder">No trend data available</div>';
            return;
        }

        // Simple line representation
        container.innerHTML = '<div class="chart-placeholder">Trend chart visualization would be here</div>';
    }

    /**
     * Show issue detail modal
     * @param {string} issueId - Issue ID
     */
    async showIssueDetail(issueId) {
        try {
            this.showLoading();
            const issue = await api.getIssue(issueId);
            
            const modalBody = document.getElementById('modal-body');
            modalBody.innerHTML = `
                <div class="form-group">
                    <strong>Title:</strong> ${this.escapeHtml(issue.title)}
                </div>
                <div class="form-group">
                    <strong>Description:</strong><br>
                    ${this.escapeHtml(issue.description || 'No description')}
                </div>
                <div class="form-group">
                    <strong>Severity:</strong> <span class="badge badge-${issue.severity}">${issue.severity}</span>
                </div>
                <div class="form-group">
                    <strong>Status:</strong> <span class="badge badge-${issue.status}">${issue.status}</span>
                </div>
                <div class="form-group">
                    <strong>Category:</strong> ${this.escapeHtml(issue.category || 'N/A')}
                </div>
                <div class="form-group">
                    <strong>Created:</strong> ${this.formatDate(issue.created_at)}
                </div>
                <div class="form-group">
                    <strong>Updated:</strong> ${this.formatDate(issue.updated_at)}
                </div>
            `;

            this.showModal();
            this.hideLoading();
        } catch (error) {
            this.showNotification('Failed to load issue details: ' + error.message, 'error');
            this.hideLoading();
        }
    }

    /**
     * Show integration detail modal
     * @param {string} name - Integration name
     */
    async showIntegrationDetail(name) {
        try {
            this.showLoading();
            const integration = await api.getIntegration(name);
            
            const modalBody = document.getElementById('modal-body');
            modalBody.innerHTML = `
                <div class="form-group">
                    <strong>Name:</strong> ${this.escapeHtml(integration.display_name || integration.name)}
                </div>
                <div class="form-group">
                    <strong>Description:</strong><br>
                    ${this.escapeHtml(integration.description || 'No description available')}
                </div>
                <div class="form-group">
                    <strong>Total Issues:</strong> ${integration.issue_count}
                </div>
                <div class="form-group">
                    <strong>Critical:</strong> ${integration.critical_count}
                </div>
                <div class="form-group">
                    <strong>Warning:</strong> ${integration.warning_count}
                </div>
                <div class="form-group">
                    <strong>Info:</strong> ${integration.info_count}
                </div>
            `;

            this.showModal();
            this.hideLoading();
        } catch (error) {
            this.showNotification('Integration not found or error loading details', 'error');
            this.hideLoading();
        }
    }

    /**
     * Show create issue modal
     */
    showCreateIssueModal() {
        const modalBody = document.getElementById('modal-body');
        modalBody.innerHTML = `
            <div class="form-group">
                <label class="form-label" for="issue-title">Title *</label>
                <input type="text" id="issue-title" class="form-input" required>
            </div>
            <div class="form-group">
                <label class="form-label" for="issue-description">Description</label>
                <textarea id="issue-description" class="form-textarea"></textarea>
            </div>
            <div class="form-group">
                <label class="form-label" for="issue-severity">Severity</label>
                <select id="issue-severity" class="form-select">
                    <option value="low">Low</option>
                    <option value="medium" selected>Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label" for="issue-category">Category</label>
                <input type="text" id="issue-category" class="form-input">
            </div>
        `;

        const saveBtn = document.getElementById('btn-modal-save');
        saveBtn.onclick = () => this.saveNewIssue();

        this.showModal();
    }

    /**
     * Save new issue
     */
    async saveNewIssue() {
        const title = document.getElementById('issue-title').value;
        const description = document.getElementById('issue-description').value;
        const severity = document.getElementById('issue-severity').value;
        const category = document.getElementById('issue-category').value;

        if (!title) {
            this.showNotification('Title is required', 'error');
            return;
        }

        try {
            this.showLoading();
            await api.createIssue({
                title,
                description,
                severity,
                category,
                source: 'manual'
            });

            this.showNotification('Issue created successfully', 'success');
            this.closeModal();
            this.loadIssues();
            this.hideLoading();
        } catch (error) {
            this.showNotification('Failed to create issue: ' + error.message, 'error');
            this.hideLoading();
        }
    }

    /**
     * Show modal
     */
    showModal() {
        const modal = document.getElementById('issue-modal');
        modal.classList.add('active');
    }

    /**
     * Close modal
     */
    closeModal() {
        const modal = document.getElementById('issue-modal');
        modal.classList.remove('active');
    }

    /**
     * Show loading overlay
     */
    showLoading() {
        const overlay = document.getElementById('loading-overlay');
        overlay.classList.add('active');
    }

    /**
     * Hide loading overlay
     */
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        overlay.classList.remove('active');
    }

    /**
     * Show notification toast
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, error, warning)
     */
    showNotification(message, type = 'info') {
        const toast = document.getElementById('notification-toast');
        toast.textContent = message;
        toast.className = `notification-toast ${type} active`;

        setTimeout(() => {
            toast.classList.remove('active');
        }, 3000);
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} - Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Format date for display
     * @param {string} dateString - ISO date string
     * @returns {string} - Formatted date
     */
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString();
    }
}

// Initialize the application when DOM is ready
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new DashboardApp();
});
