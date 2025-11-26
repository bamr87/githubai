/**
 * CreateIssuePage - Manual issue creation form
 */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    Card,
    Form,
    Input,
    Select,
    Button,
    Typography,
    Space,
    message,
    Alert,
} from 'antd'
import { ArrowLeftOutlined, SaveOutlined } from '@ant-design/icons'
import { issueApi, templateApi } from '../services/api'

const { Title, Text } = Typography
const { TextArea } = Input

function CreateIssuePage() {
    const navigate = useNavigate()
    const [form] = Form.useForm()
    const [loading, setLoading] = useState(false)
    const [templates, setTemplates] = useState([])
    const [loadingTemplates, setLoadingTemplates] = useState(false)

    useEffect(() => {
        fetchTemplates()
    }, [])

    const fetchTemplates = async () => {
        setLoadingTemplates(true)
        try {
            const data = await templateApi.list()
            setTemplates(data.results || data)
        } catch (error) {
            console.error('Error fetching templates:', error)
        } finally {
            setLoadingTemplates(false)
        }
    }

    const handleTemplateSelect = (templateId) => {
        const template = templates.find((t) => t.id === templateId)
        if (template) {
            form.setFieldsValue({
                title: template.title_template || '',
                body: template.body_template || '',
                issue_type: template.issue_type || 'other',
                labels: template.default_labels || [],
            })
        }
    }

    const handleSubmit = async (values) => {
        setLoading(true)
        try {
            const issue = await issueApi.create(values)
            message.success('Issue created successfully!')
            navigate(`/issues/${issue.id}`)
        } catch (error) {
            message.error(error.displayMessage || 'Failed to create issue')
            console.error('Error creating issue:', error)
        } finally {
            setLoading(false)
        }
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

            <Title level={3}>Create New Issue</Title>

            <Alert
                message="GitHub Integration"
                description="Issues created here will be synced to GitHub. Make sure you have the correct repository configured."
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
                        github_repo: 'bamr87/githubai',
                        issue_type: 'other',
                        state: 'open',
                    }}
                >
                    {/* Template Selection */}
                    <Form.Item label="Use Template (Optional)">
                        <Select
                            placeholder="Select a template to pre-fill"
                            allowClear
                            loading={loadingTemplates}
                            onChange={handleTemplateSelect}
                            options={templates.map((t) => ({
                                label: t.name,
                                value: t.id,
                            }))}
                        />
                    </Form.Item>

                    {/* Repository */}
                    <Form.Item
                        name="github_repo"
                        label="Repository"
                        rules={[{ required: true, message: 'Please enter repository' }]}
                    >
                        <Input placeholder="owner/repo" />
                    </Form.Item>

                    {/* Title */}
                    <Form.Item
                        name="title"
                        label="Title"
                        rules={[{ required: true, message: 'Please enter issue title' }]}
                    >
                        <Input placeholder="Issue title" />
                    </Form.Item>

                    {/* Body */}
                    <Form.Item
                        name="body"
                        label="Description"
                        rules={[{ required: true, message: 'Please enter description' }]}
                    >
                        <TextArea
                            rows={10}
                            placeholder="Describe the issue in detail..."
                        />
                    </Form.Item>

                    {/* Issue Type */}
                    <Form.Item
                        name="issue_type"
                        label="Issue Type"
                        rules={[{ required: true }]}
                    >
                        <Select
                            options={[
                                { label: 'Feature', value: 'feature' },
                                { label: 'Bug', value: 'bug' },
                                { label: 'README Update', value: 'readme' },
                                { label: 'Sub-issue', value: 'sub_issue' },
                                { label: 'Other', value: 'other' },
                            ]}
                        />
                    </Form.Item>

                    {/* Labels */}
                    <Form.Item name="labels" label="Labels">
                        <Select
                            mode="tags"
                            placeholder="Add labels (press enter to create)"
                            tokenSeparators={[',']}
                        />
                    </Form.Item>

                    {/* Actions */}
                    <Form.Item>
                        <Space>
                            <Button
                                type="primary"
                                htmlType="submit"
                                icon={<SaveOutlined />}
                                loading={loading}
                            >
                                Create Issue
                            </Button>
                            <Button onClick={() => navigate('/issues')}>Cancel</Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Card>
        </div>
    )
}

export default CreateIssuePage
