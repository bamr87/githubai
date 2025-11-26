/**
 * IssueDetailPage - Single issue detail view
 */

import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
    Card,
    Typography,
    Tag,
    Space,
    Button,
    Descriptions,
    Spin,
    Alert,
    List,
} from 'antd'
import {
    ArrowLeftOutlined,
    GithubOutlined,
    ThunderboltOutlined,
    EditOutlined,
    BranchesOutlined,
    FileTextOutlined,
} from '@ant-design/icons'
import { issueApi } from '../services/api'

const { Title, Paragraph, Text } = Typography

// Issue type color mapping
const issueTypeColors = {
    feature: 'blue',
    bug: 'red',
    readme: 'green',
    sub_issue: 'purple',
    other: 'default',
}

function IssueDetailPage() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [issue, setIssue] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        const loadIssue = async () => {
            setLoading(true)
            setError(null)
            try {
                const data = await issueApi.get(id)
                setIssue(data)
            } catch (err) {
                setError(err.displayMessage || 'Failed to fetch issue')
                console.error('Error fetching issue:', err)
            } finally {
                setLoading(false)
            }
        }
        loadIssue()
    }, [id])

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: 48 }}>
                <Spin size="large" />
            </div>
        )
    }

    if (error) {
        return (
            <Alert
                message="Error"
                description={error}
                type="error"
                showIcon
                action={
                    <Button onClick={() => navigate('/issues')}>
                        Back to Issues
                    </Button>
                }
            />
        )
    }

    if (!issue) {
        return (
            <Alert
                message="Not Found"
                description="Issue not found"
                type="warning"
                showIcon
                action={
                    <Button onClick={() => navigate('/issues')}>
                        Back to Issues
                    </Button>
                }
            />
        )
    }

    return (
        <div>
            {/* Back button */}
            <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate('/issues')}
                style={{ marginBottom: 16 }}
            >
                Back to Issues
            </Button>

            {/* Issue Header */}
            <Card style={{ marginBottom: 24 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                        <Space align="center" style={{ marginBottom: 8 }}>
                            <Title level={3} style={{ margin: 0 }}>
                                {issue.title}
                            </Title>
                            {issue.ai_generated && (
                                <Tag color="blue" icon={<ThunderboltOutlined />}>
                                    AI Generated
                                </Tag>
                            )}
                        </Space>
                        <Space size="middle">
                            <Tag color={issue.state === 'open' ? 'green' : 'default'}>
                                {issue.state}
                            </Tag>
                            <Tag color={issueTypeColors[issue.issue_type] || 'default'}>
                                {issue.issue_type?.replace('_', ' ')}
                            </Tag>
                            <Text type="secondary">
                                {issue.github_repo} #{issue.github_issue_number}
                            </Text>
                        </Space>
                    </div>
                    <Space>
                        {issue.html_url && (
                            <a href={issue.html_url} target="_blank" rel="noopener noreferrer">
                                <Button icon={<GithubOutlined />}>View on GitHub</Button>
                            </a>
                        )}
                    </Space>
                </div>
            </Card>

            {/* Issue Body */}
            <Card title="Description" style={{ marginBottom: 24 }}>
                <div
                    style={{
                        whiteSpace: 'pre-wrap',
                        backgroundColor: '#fafafa',
                        padding: 16,
                        borderRadius: 6,
                        fontFamily: 'monospace',
                        fontSize: 13,
                    }}
                >
                    {issue.body || 'No description provided'}
                </div>
            </Card>

            {/* Details */}
            <Card title="Details" style={{ marginBottom: 24 }}>
                <Descriptions column={2}>
                    <Descriptions.Item label="ID">{issue.id}</Descriptions.Item>
                    <Descriptions.Item label="GitHub Issue">
                        #{issue.github_issue_number}
                    </Descriptions.Item>
                    <Descriptions.Item label="Repository">
                        {issue.github_repo}
                    </Descriptions.Item>
                    <Descriptions.Item label="Type">
                        <Tag color={issueTypeColors[issue.issue_type] || 'default'}>
                            {issue.issue_type?.replace('_', ' ')}
                        </Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="State">
                        <Tag color={issue.state === 'open' ? 'green' : 'default'}>
                            {issue.state}
                        </Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="AI Generated">
                        {issue.ai_generated ? 'Yes' : 'No'}
                    </Descriptions.Item>
                    <Descriptions.Item label="Created">
                        {new Date(issue.created_at).toLocaleString()}
                    </Descriptions.Item>
                    <Descriptions.Item label="Updated">
                        {new Date(issue.updated_at).toLocaleString()}
                    </Descriptions.Item>
                </Descriptions>
            </Card>

            {/* Labels */}
            {issue.labels && issue.labels.length > 0 && (
                <Card title="Labels" style={{ marginBottom: 24 }}>
                    <Space wrap>
                        {issue.labels.map((label, idx) => (
                            <Tag key={idx}>
                                {typeof label === 'string' ? label : label.name}
                            </Tag>
                        ))}
                    </Space>
                </Card>
            )}

            {/* File References */}
            {issue.file_references && issue.file_references.length > 0 && (
                <Card
                    title={
                        <Space>
                            <FileTextOutlined />
                            File References
                        </Space>
                    }
                    style={{ marginBottom: 24 }}
                >
                    <List
                        size="small"
                        dataSource={issue.file_references}
                        renderItem={(file) => (
                            <List.Item>
                                <Text code>{file}</Text>
                            </List.Item>
                        )}
                    />
                </Card>
            )}

            {/* Parent Issue */}
            {issue.parent_issue && (
                <Card
                    title={
                        <Space>
                            <BranchesOutlined />
                            Parent Issue
                        </Space>
                    }
                    style={{ marginBottom: 24 }}
                >
                    <Link to={`/issues/${issue.parent_issue}`}>
                        View Parent Issue #{issue.parent_issue}
                    </Link>
                </Card>
            )}

            {/* Sub-issues count */}
            {issue.sub_issues_count > 0 && (
                <Card title="Sub-Issues" style={{ marginBottom: 24 }}>
                    <Text>This issue has {issue.sub_issues_count} sub-issue(s)</Text>
                </Card>
            )}
        </div>
    )
}

export default IssueDetailPage
