/**
 * AutoIssuePage - AI-powered automatic issue generation
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    Card,
    Form,
    Select,
    Input,
    Button,
    Typography,
    Space,
    Alert,
    Checkbox,
    Result,
    Divider,
    message,
} from 'antd'
import {
    ArrowLeftOutlined,
    ThunderboltOutlined,
    RocketOutlined,
} from '@ant-design/icons'
import { issueApi } from '../services/api'

const { Title, Paragraph, Text } = Typography
const { TextArea } = Input

// Chore type descriptions
const choreTypes = [
    {
        value: 'code_quality',
        label: 'Code Quality',
        description: 'Analyze code for quality issues, anti-patterns, and improvements',
    },
    {
        value: 'todo_scan',
        label: 'TODO Scan',
        description: 'Find and track TODO, FIXME, and HACK comments in code',
    },
    {
        value: 'documentation',
        label: 'Documentation',
        description: 'Identify missing or outdated documentation',
    },
    {
        value: 'dependencies',
        label: 'Dependencies',
        description: 'Check for outdated or vulnerable dependencies',
    },
    {
        value: 'test_coverage',
        label: 'Test Coverage',
        description: 'Find areas lacking test coverage',
    },
    {
        value: 'general_review',
        label: 'General Review',
        description: 'Comprehensive codebase review and suggestions',
    },
]

function AutoIssuePage() {
    const navigate = useNavigate()
    const [form] = Form.useForm()
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)

    const handleSubmit = async (values) => {
        setLoading(true)
        setResult(null)
        try {
            const issue = await issueApi.createAutoIssue({
                chore_type: values.chore_type,
                repo: values.repo,
                context_files: values.context_files
                    ? values.context_files.split('\n').filter((f) => f.trim())
                    : null,
                auto_submit: values.auto_submit,
            })
            setResult(issue)
            message.success('Issue generated successfully!')
        } catch (error) {
            message.error(error.displayMessage || 'Failed to generate issue')
            console.error('Error generating issue:', error)
        } finally {
            setLoading(false)
        }
    }

    // Success result view
    if (result) {
        return (
            <div>
                <Button
                    icon={<ArrowLeftOutlined />}
                    onClick={() => navigate('/issues')}
                    style={{ marginBottom: 16 }}
                >
                    Back to Issues
                </Button>

                <Result
                    status="success"
                    icon={<ThunderboltOutlined style={{ color: '#1890ff' }} />}
                    title="Issue Generated Successfully!"
                    subTitle={`AI has analyzed your repository and created an issue`}
                    extra={[
                        <Button
                            type="primary"
                            key="view"
                            onClick={() => navigate(`/issues/${result.id}`)}
                        >
                            View Issue
                        </Button>,
                        <Button key="another" onClick={() => setResult(null)}>
                            Generate Another
                        </Button>,
                        result.html_url && (
                            <a
                                key="github"
                                href={result.html_url}
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                <Button>View on GitHub</Button>
                            </a>
                        ),
                    ]}
                />

                <Card style={{ marginTop: 24 }}>
                    <Title level={4}>{result.title}</Title>
                    <Divider />
                    <div
                        style={{
                            whiteSpace: 'pre-wrap',
                            backgroundColor: '#fafafa',
                            padding: 16,
                            borderRadius: 6,
                            fontFamily: 'monospace',
                            fontSize: 13,
                            maxHeight: 400,
                            overflow: 'auto',
                        }}
                    >
                        {result.body}
                    </div>
                </Card>
            </div>
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

            <Title level={3}>
                <ThunderboltOutlined style={{ marginRight: 8, color: '#1890ff' }} />
                Auto-Generate Issue
            </Title>

            <Alert
                message="AI-Powered Analysis"
                description="Our AI will analyze your repository and automatically generate a well-structured GitHub issue based on your selected analysis type."
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
            />

            <Card>
                <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleSubmit}
                    initialValues={{
                        repo: 'bamr87/githubai',
                        auto_submit: true,
                    }}
                >
                    {/* Chore Type Selection */}
                    <Form.Item
                        name="chore_type"
                        label="Analysis Type"
                        rules={[{ required: true, message: 'Please select analysis type' }]}
                    >
                        <Select placeholder="Select what to analyze">
                            {choreTypes.map((type) => (
                                <Select.Option key={type.value} value={type.value}>
                                    <Space direction="vertical" size={0}>
                                        <Text strong>{type.label}</Text>
                                        <Text type="secondary" style={{ fontSize: 12 }}>
                                            {type.description}
                                        </Text>
                                    </Space>
                                </Select.Option>
                            ))}
                        </Select>
                    </Form.Item>

                    {/* Repository */}
                    <Form.Item
                        name="repo"
                        label="Repository"
                        rules={[{ required: true, message: 'Please enter repository' }]}
                    >
                        <Input placeholder="owner/repo" />
                    </Form.Item>

                    {/* Context Files (Optional) */}
                    <Form.Item
                        name="context_files"
                        label="Context Files (Optional)"
                        extra="Enter file paths to focus the analysis on specific files (one per line)"
                    >
                        <TextArea
                            rows={4}
                            placeholder="src/services/ai_service.py&#10;apps/core/models.py&#10;..."
                        />
                    </Form.Item>

                    {/* Auto Submit */}
                    <Form.Item name="auto_submit" valuePropName="checked">
                        <Checkbox>
                            <Space>
                                Automatically create GitHub issue
                                <Text type="secondary">(uncheck to preview first)</Text>
                            </Space>
                        </Checkbox>
                    </Form.Item>

                    {/* Actions */}
                    <Form.Item>
                        <Space>
                            <Button
                                type="primary"
                                htmlType="submit"
                                icon={<RocketOutlined />}
                                loading={loading}
                                size="large"
                            >
                                {loading ? 'Analyzing...' : 'Generate Issue'}
                            </Button>
                            <Button onClick={() => navigate('/issues')}>Cancel</Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Card>

            {/* Analysis Types Explanation */}
            <Card title="Analysis Types Explained" style={{ marginTop: 24 }}>
                {choreTypes.map((type) => (
                    <div key={type.value} style={{ marginBottom: 16 }}>
                        <Text strong>{type.label}</Text>
                        <Paragraph type="secondary" style={{ margin: '4px 0 0 0' }}>
                            {type.description}
                        </Paragraph>
                    </div>
                ))}
            </Card>
        </div>
    )
}

export default AutoIssuePage
