/**
 * IssuesPage - Issue list and dashboard
 */

import { useState, useEffect } from 'react'
import { Table, Tag, Space, Button, Typography, Input, Select, Card, message, Tooltip } from 'antd'
import {
    PlusOutlined,
    ReloadOutlined,
    ThunderboltOutlined,
    GithubOutlined,
    SearchOutlined,
} from '@ant-design/icons'
import { Link, useNavigate } from 'react-router-dom'
import { issueApi } from '../services/api'

const { Title } = Typography
const { Search } = Input

// Issue type color mapping
const issueTypeColors = {
    feature: 'blue',
    bug: 'red',
    readme: 'green',
    sub_issue: 'purple',
    other: 'default',
}

// Issue state color mapping
const stateColors = {
    open: 'green',
    closed: 'default',
}

function IssuesPage() {
    const [issues, setIssues] = useState([])
    const [loading, setLoading] = useState(false)
    const [filters, setFilters] = useState({
        state: undefined,
        issue_type: undefined,
        search: '',
    })
    const navigate = useNavigate()

    const fetchIssues = async () => {
        setLoading(true)
        try {
            const params = {}
            if (filters.state) params.state = filters.state
            if (filters.issue_type) params.issue_type = filters.issue_type

            const data = await issueApi.list(params)
            setIssues(data.results || data)
        } catch (error) {
            message.error('Failed to fetch issues')
            console.error('Error fetching issues:', error)
        } finally {
            setLoading(false)
        }
    }

    // Fetch issues on mount and when filters change
    useEffect(() => {
        fetchIssues()
    }, [filters.state, filters.issue_type]) // eslint-disable-line react-hooks/exhaustive-deps

    // Filter issues by search term (client-side)
    const filteredIssues = issues.filter((issue) => {
        if (!filters.search) return true
        const searchLower = filters.search.toLowerCase()
        return (
            issue.title?.toLowerCase().includes(searchLower) ||
            issue.github_repo?.toLowerCase().includes(searchLower)
        )
    })

    const columns = [
        {
            title: 'ID',
            dataIndex: 'github_issue_number',
            key: 'number',
            width: 80,
            render: (num, record) => (
                <Link to={`/issues/${record.id}`}>#{num || record.id}</Link>
            ),
        },
        {
            title: 'Title',
            dataIndex: 'title',
            key: 'title',
            ellipsis: true,
            render: (title, record) => (
                <Space direction="vertical" size={0}>
                    <Link to={`/issues/${record.id}`} style={{ fontWeight: 500 }}>
                        {title}
                    </Link>
                    <span style={{ fontSize: 12, color: '#999' }}>
                        {record.github_repo}
                    </span>
                </Space>
            ),
        },
        {
            title: 'Type',
            dataIndex: 'issue_type',
            key: 'type',
            width: 100,
            render: (type) => (
                <Tag color={issueTypeColors[type] || 'default'}>
                    {type?.replace('_', ' ')}
                </Tag>
            ),
        },
        {
            title: 'State',
            dataIndex: 'state',
            key: 'state',
            width: 80,
            render: (state) => (
                <Tag color={stateColors[state] || 'default'}>
                    {state}
                </Tag>
            ),
        },
        {
            title: 'Labels',
            dataIndex: 'labels',
            key: 'labels',
            width: 200,
            render: (labels) => (
                <Space size={[0, 4]} wrap>
                    {labels?.slice(0, 3).map((label, idx) => (
                        <Tag key={idx} style={{ fontSize: 11 }}>
                            {typeof label === 'string' ? label : label.name}
                        </Tag>
                    ))}
                    {labels?.length > 3 && (
                        <Tooltip title={labels.slice(3).map(l => typeof l === 'string' ? l : l.name).join(', ')}>
                            <Tag style={{ fontSize: 11 }}>+{labels.length - 3}</Tag>
                        </Tooltip>
                    )}
                </Space>
            ),
        },
        {
            title: 'AI',
            dataIndex: 'ai_generated',
            key: 'ai',
            width: 60,
            align: 'center',
            render: (aiGenerated) => (
                aiGenerated ? (
                    <Tooltip title="AI Generated">
                        <ThunderboltOutlined style={{ color: '#1890ff' }} />
                    </Tooltip>
                ) : null
            ),
        },
        {
            title: 'Actions',
            key: 'actions',
            width: 100,
            render: (_, record) => (
                <Space>
                    {record.html_url && (
                        <Tooltip title="View on GitHub">
                            <a href={record.html_url} target="_blank" rel="noopener noreferrer">
                                <GithubOutlined />
                            </a>
                        </Tooltip>
                    )}
                </Space>
            ),
        },
    ]

    return (
        <div>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <Title level={3} style={{ margin: 0 }}>Issues</Title>
                <Space>
                    <Button icon={<ReloadOutlined />} onClick={fetchIssues} loading={loading}>
                        Refresh
                    </Button>
                    <Button
                        icon={<ThunderboltOutlined />}
                        onClick={() => navigate('/issues/auto')}
                    >
                        Auto-Generate
                    </Button>
                    <Button
                        type="primary"
                        icon={<PlusOutlined />}
                        onClick={() => navigate('/issues/create')}
                    >
                        Create Issue
                    </Button>
                </Space>
            </div>

            {/* Filters */}
            <Card style={{ marginBottom: 16 }}>
                <Space wrap>
                    <Search
                        placeholder="Search issues..."
                        allowClear
                        style={{ width: 250 }}
                        prefix={<SearchOutlined />}
                        value={filters.search}
                        onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                    />
                    <Select
                        placeholder="State"
                        allowClear
                        style={{ width: 120 }}
                        value={filters.state}
                        onChange={(value) => setFilters({ ...filters, state: value })}
                        options={[
                            { label: 'Open', value: 'open' },
                            { label: 'Closed', value: 'closed' },
                        ]}
                    />
                    <Select
                        placeholder="Type"
                        allowClear
                        style={{ width: 140 }}
                        value={filters.issue_type}
                        onChange={(value) => setFilters({ ...filters, issue_type: value })}
                        options={[
                            { label: 'Feature', value: 'feature' },
                            { label: 'Bug', value: 'bug' },
                            { label: 'README', value: 'readme' },
                            { label: 'Sub-issue', value: 'sub_issue' },
                            { label: 'Other', value: 'other' },
                        ]}
                    />
                </Space>
            </Card>

            {/* Table */}
            <Table
                columns={columns}
                dataSource={filteredIssues}
                rowKey="id"
                loading={loading}
                pagination={{
                    pageSize: 20,
                    showSizeChanger: true,
                    showTotal: (total) => `${total} issues`,
                }}
            />
        </div>
    )
}

export default IssuesPage
