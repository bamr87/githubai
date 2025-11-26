/**
 * API Client Layer for GitHubAI Frontend
 * Abstracts all backend API calls with error handling
 */

import axios from 'axios'

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance with default configuration
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 second timeout
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        const errorMessage = error.response?.data?.detail
            || error.response?.data?.message
            || error.message
            || 'An unexpected error occurred'

        console.error('API Error:', error)
        return Promise.reject({ ...error, displayMessage: errorMessage })
    }
)

/**
 * Chat API methods
 */
export const chatApi = {
    /**
     * Send a message to the AI chat endpoint
     * @param {string} messageText - The message to send
     * @param {string} [provider] - Optional AI provider override
     * @param {string} [model] - Optional model override
     * @returns {Promise<{response: string, provider: string, model: string, cached: boolean, timestamp: string}>}
     */
    sendMessage: async (messageText, provider = null, model = null) => {
        const payload = { message: messageText }
        if (provider) payload.provider = provider
        if (model) payload.model = model

        const response = await apiClient.post('/api/chat/', payload)
        return response.data
    },
}

/**
 * Issue API methods
 */
export const issueApi = {
    /**
     * List all issues with optional filters
     * @param {Object} params - Query parameters
     * @param {string} [params.state] - Filter by state (open, closed)
     * @param {string} [params.issue_type] - Filter by type (feature, bug, readme, sub_issue, other)
     * @param {string} [params.github_repo] - Filter by repository
     * @returns {Promise<Array>} List of issues
     */
    list: async (params = {}) => {
        const response = await apiClient.get('/api/issues/issues/', { params })
        return response.data
    },

    /**
     * Get a single issue by ID
     * @param {number} id - Issue ID
     * @returns {Promise<Object>} Issue details
     */
    get: async (id) => {
        const response = await apiClient.get(`/api/issues/issues/${id}/`)
        return response.data
    },

    /**
     * Create a new issue
     * @param {Object} issueData - Issue data
     * @returns {Promise<Object>} Created issue
     */
    create: async (issueData) => {
        const response = await apiClient.post('/api/issues/issues/', issueData)
        return response.data
    },

    /**
     * Update an existing issue
     * @param {number} id - Issue ID
     * @param {Object} issueData - Updated issue data
     * @returns {Promise<Object>} Updated issue
     */
    update: async (id, issueData) => {
        const response = await apiClient.put(`/api/issues/issues/${id}/`, issueData)
        return response.data
    },

    /**
     * Delete an issue
     * @param {number} id - Issue ID
     * @returns {Promise<void>}
     */
    delete: async (id) => {
        await apiClient.delete(`/api/issues/issues/${id}/`)
    },

    /**
     * Create a sub-issue from a parent issue
     * @param {number} parentId - Parent issue ID
     * @param {Object} data - Sub-issue data
     * @returns {Promise<Object>} Created sub-issue
     */
    createSubIssue: async (parentId, data) => {
        const response = await apiClient.post(`/api/issues/issues/${parentId}/create-sub-issue/`, data)
        return response.data
    },

    /**
     * Create an auto-generated issue from AI analysis
     * @param {Object} data - Auto issue configuration
     * @param {string} data.chore_type - Type: code_quality, todo_scan, documentation, dependencies, test_coverage, general_review
     * @param {string} [data.repo] - Repository (default: bamr87/githubai)
     * @param {Array<string>} [data.context_files] - Files to analyze
     * @param {boolean} [data.auto_submit] - Auto-submit to GitHub (default: true)
     * @returns {Promise<Object>} Created issue
     */
    createAutoIssue: async (data) => {
        const response = await apiClient.post('/api/issues/issues/create-auto-issue/', data)
        return response.data
    },

    /**
     * Create a README update issue
     * @param {Object} data - README issue data
     * @returns {Promise<Object>} Created issue
     */
    createReadmeUpdate: async (data) => {
        const response = await apiClient.post('/api/issues/issues/create-readme-update/', data)
        return response.data
    },

    /**
     * Create an issue from user feedback
     * @param {Object} data - Feedback data
     * @returns {Promise<Object>} Created issue
     */
    createFromFeedback: async (data) => {
        const response = await apiClient.post('/api/issues/issues/create-from-feedback/', data)
        return response.data
    },
}

/**
 * Issue Template API methods
 */
export const templateApi = {
    /**
     * List all issue templates
     * @returns {Promise<Array>} List of templates
     */
    list: async () => {
        const response = await apiClient.get('/api/issues/templates/')
        return response.data
    },

    /**
     * Get a single template by ID
     * @param {number} id - Template ID
     * @returns {Promise<Object>} Template details
     */
    get: async (id) => {
        const response = await apiClient.get(`/api/issues/templates/${id}/`)
        return response.data
    },

    /**
     * Create a new template
     * @param {Object} templateData - Template data
     * @returns {Promise<Object>} Created template
     */
    create: async (templateData) => {
        const response = await apiClient.post('/api/issues/templates/', templateData)
        return response.data
    },

    /**
     * Update an existing template
     * @param {number} id - Template ID
     * @param {Object} templateData - Updated template data
     * @returns {Promise<Object>} Updated template
     */
    update: async (id, templateData) => {
        const response = await apiClient.put(`/api/issues/templates/${id}/`, templateData)
        return response.data
    },

    /**
     * Delete a template
     * @param {number} id - Template ID
     * @returns {Promise<void>}
     */
    delete: async (id) => {
        await apiClient.delete(`/api/issues/templates/${id}/`)
    },
}

/**
 * AI Provider API methods
 */
export const providerApi = {
    /**
     * List all available AI providers
     * @returns {Promise<Array>} List of providers
     */
    list: async () => {
        const response = await apiClient.get('/api/providers/')
        return response.data
    },

    /**
     * Get a single provider by ID
     * @param {number} id - Provider ID
     * @returns {Promise<Object>} Provider details
     */
    get: async (id) => {
        const response = await apiClient.get(`/api/providers/${id}/`)
        return response.data
    },
}

/**
 * AI Model API methods
 */
export const modelApi = {
    /**
     * List all available AI models
     * @param {Object} params - Query parameters
     * @param {number} [params.provider] - Filter by provider ID
     * @returns {Promise<Array>} List of models
     */
    list: async (params = {}) => {
        const response = await apiClient.get('/api/models/', { params })
        return response.data
    },

    /**
     * Get a single model by ID
     * @param {number} id - Model ID
     * @returns {Promise<Object>} Model details
     */
    get: async (id) => {
        const response = await apiClient.get(`/api/models/${id}/`)
        return response.data
    },
}

/**
 * Health check API
 */
export const healthApi = {
    /**
     * Check API health status
     * @returns {Promise<Object>} Health status
     */
    check: async () => {
        const response = await apiClient.get('/health/')
        return response.data
    },
}

// Export the base client for advanced usage
export { apiClient, API_BASE_URL }
