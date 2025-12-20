/**
 * API Client for Home Assistant Log Analysis Dashboard
 * Handles all communication with the backend REST API
 */

class APIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }

    /**
     * Generic request handler with error handling
     * @param {string} endpoint - API endpoint
     * @param {object} options - Fetch options
     * @returns {Promise<object>} - Response data
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
                ...options,
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({
                    error: 'Unknown error occurred',
                }));
                throw new Error(error.error || error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    /**
     * Build query string from parameters
     * @param {object} params - Query parameters
     * @returns {string} - Query string
     */
    buildQueryString(params) {
        const filtered = Object.entries(params)
            .filter(([_, value]) => value !== null && value !== undefined && value !== '')
            .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
            .join('&');
        return filtered ? `?${filtered}` : '';
    }

    /* ========================================================================
       Issues API
       ======================================================================== */

    /**
     * Get list of issues with optional filters
     * @param {object} filters - Filter parameters
     * @returns {Promise<object>} - Issues list response
     */
    async getIssues(filters = {}) {
        const query = this.buildQueryString(filters);
        return this.request(`/issues${query}`);
    }

    /**
     * Get single issue by ID
     * @param {string} issueId - Issue ID
     * @returns {Promise<object>} - Issue details
     */
    async getIssue(issueId) {
        return this.request(`/issues/${issueId}`);
    }

    /**
     * Create a new issue
     * @param {object} issueData - Issue data
     * @returns {Promise<object>} - Created issue
     */
    async createIssue(issueData) {
        return this.request('/issues', {
            method: 'POST',
            body: JSON.stringify(issueData),
        });
    }

    /**
     * Update an existing issue
     * @param {string} issueId - Issue ID
     * @param {object} updateData - Update data
     * @returns {Promise<object>} - Updated issue
     */
    async updateIssue(issueId, updateData) {
        return this.request(`/issues/${issueId}`, {
            method: 'PUT',
            body: JSON.stringify(updateData),
        });
    }

    /**
     * Delete an issue
     * @param {string} issueId - Issue ID
     * @returns {Promise<void>}
     */
    async deleteIssue(issueId) {
        return this.request(`/issues/${issueId}`, {
            method: 'DELETE',
        });
    }

    /**
     * Update issue status
     * @param {string} issueId - Issue ID
     * @param {string} status - New status
     * @param {string} reason - Reason for status change
     * @returns {Promise<object>} - Updated issue
     */
    async updateIssueStatus(issueId, status, reason = null) {
        return this.request(`/issues/${issueId}/status`, {
            method: 'PATCH',
            body: JSON.stringify({ status, reason }),
        });
    }

    /**
     * Add a note to an issue
     * @param {string} issueId - Issue ID
     * @param {object} noteData - Note data
     * @returns {Promise<object>} - Created note
     */
    async addIssueNote(issueId, noteData) {
        return this.request(`/issues/${issueId}/notes`, {
            method: 'POST',
            body: JSON.stringify(noteData),
        });
    }

    /**
     * Get all notes for an issue
     * @param {string} issueId - Issue ID
     * @returns {Promise<Array>} - List of notes
     */
    async getIssueNotes(issueId) {
        return this.request(`/issues/${issueId}/notes`);
    }

    /* ========================================================================
       Integrations API
       ======================================================================== */

    /**
     * Get list of integrations with optional filters
     * @param {object} filters - Filter parameters
     * @returns {Promise<object>} - Integrations list response
     */
    async getIntegrations(filters = {}) {
        const query = this.buildQueryString(filters);
        return this.request(`/integrations${query}`);
    }

    /**
     * Get single integration by name
     * @param {string} name - Integration name
     * @returns {Promise<object>} - Integration details
     */
    async getIntegration(name) {
        return this.request(`/integrations/${encodeURIComponent(name)}`);
    }

    /**
     * Get all issues for an integration
     * @param {string} name - Integration name
     * @param {object} filters - Filter parameters
     * @returns {Promise<object>} - Issues list response
     */
    async getIntegrationIssues(name, filters = {}) {
        const query = this.buildQueryString(filters);
        return this.request(`/integrations/${encodeURIComponent(name)}/issues${query}`);
    }

    /**
     * Get statistics for an integration
     * @param {string} name - Integration name
     * @returns {Promise<object>} - Integration statistics
     */
    async getIntegrationStatistics(name) {
        return this.request(`/integrations/${encodeURIComponent(name)}/statistics`);
    }

    /* ========================================================================
       Statistics API
       ======================================================================== */

    /**
     * Get overall statistics
     * @returns {Promise<object>} - Overall statistics
     */
    async getStatistics() {
        return this.request('/statistics');
    }

    /**
     * Get statistics grouped by severity
     * @param {boolean} includeResolved - Include resolved issues
     * @returns {Promise<Array>} - Severity statistics
     */
    async getStatisticsBySeverity(includeResolved = true) {
        const query = this.buildQueryString({ include_resolved: includeResolved });
        return this.request(`/statistics/by-severity${query}`);
    }

    /**
     * Get statistics grouped by integration
     * @param {object} options - Query options
     * @returns {Promise<Array>} - Integration statistics
     */
    async getStatisticsByIntegration(options = {}) {
        const query = this.buildQueryString(options);
        return this.request(`/statistics/by-integration${query}`);
    }

    /**
     * Get statistics grouped by status
     * @returns {Promise<Array>} - Status statistics
     */
    async getStatisticsByStatus() {
        return this.request('/statistics/by-status');
    }

    /**
     * Get trend data over time
     * @param {object} options - Query options
     * @returns {Promise<object>} - Trend statistics
     */
    async getTrendStatistics(options = {}) {
        const query = this.buildQueryString(options);
        return this.request(`/statistics/trend${query}`);
    }

    /**
     * Get dashboard summary
     * @returns {Promise<object>} - Dashboard summary
     */
    async getDashboardSummary() {
        return this.request('/statistics/summary');
    }

    /* ========================================================================
       Health & Configuration
       ======================================================================== */

    /**
     * Check API health
     * @returns {Promise<object>} - Health status
     */
    async getHealth() {
        return this.request('/health', { baseURL: '' });
    }

    /**
     * Get configuration
     * @returns {Promise<object>} - Configuration
     */
    async getConfig() {
        return this.request('/config', { baseURL: '' });
    }
}

// Create and export a singleton instance
const api = new APIClient();

// Also export the class for custom instances if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIClient, api };
}
