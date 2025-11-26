/**
 * TemplatesPage - Issue template browser and manager
 */

import { useState, useEffect } from 'react'
import {
    Table,
    Card,
    Typography,
    Tag,
    Space,
    Button,
    message,
    Modal,
    Tooltip,
} from 'antd'
import {
    ReloadOutlined,
    EyeOutlined,
    FileTextOutlined,
} from '@ant-design/icons'
import { templateApi } from '../services/api'

const { Title, Text, Paragraph } = Typography

// Issue type color mapping
const issueTypeColors = {
    feature: 'blue',
    bug: 'red',
    readme: 'green',
    sub_issue: 'purple',
    other: 'default',
}

function TemplatesPage() {
    const [templates, setTemplates] = useState([])
    const [loading, setLoading] = useState(false)
    const [selectedTemplate, setSelectedTemplate] = useState(null)
    const [previewVisible, setPreviewVisible] = useState(false)

    useEffect(() => {
        fetchTemplates()
    }, [])

    const fetchTemplates = async () => {
        setLoading(true)
        try {
            const data = await templateApi.list()
            setTemplates(data.results || data)
        } catch (error) {
            message.error('Failed to fetch templates')
            console.error('Error fetching templates:', error)
        } finally {
            setLoading(false)
        }
    }

    const handlePreview = (template) => {
        setSelectedTemplate(template)
        setPreviewVisible(true)
    }

    const columns = [
        {
            title: 'Name',
            dataIndex: 'name',
            key: 'name',
            render: (name, record) => (
                <Space direction="vertical" size={0}>
                    <Text strong>
                        <FileTextOutlined style={{ marginRight: 8 }} />
                        {name}
                    </Text>
                    {record.description && (
                        <Text type="secondary" style={{ fontSize: 12 }}>
                            {record.description}
                        </Text>
                    )}
                </Space>
            ),
        },
        {
            title: 'Issue Type',
            dataIndex: 'issue_type',
            key: 'type',
            width: 120,
            render: (type) => (
                <Tag color={issueTypeColors[type] || 'default'}>
                    {type?.replace('_', ' ')}
                </Tag>
            ),
        },
        {
            title: 'Default Labels',
            dataIndex: 'default_labels',
            key: 'labels',
            width: 200,
            render: (labels) => (
                <Space size={[0, 4]} wrap>
                    {labels?.slice(0, 3).map((label, idx) => (
                        <Tag key={idx} style={{ fontSize: 11 }}>
                            {label}
                        </Tag>
                    ))}
                    {labels?.length > 3 && (
                        <Tooltip title={labels.slice(3).join(', ')}>
                            <Tag style={{ fontSize: 11 }}>+{labels.length - 3}</Tag>
                        </Tooltip>
                    )}
                </Space>
            ),
        },
        {
            title: 'Active',
            dataIndex: 'is_active',
            key: 'active',
            width: 80,
            render: (active) => (
                <Tag color={active ? 'green' : 'default'}>
                    {active ? 'Active' : 'Inactive'}
                </Tag>
            ),
        },
        {
            title: 'Actions',
            key: 'actions',
            width: 100,
            render: (_, record) => (
                <Button
                    icon={<EyeOutlined />}
                    size="small"
                    onClick={() => handlePreview(record)}
                >
                    Preview
                </Button>
            ),
        },
    ]

    return (
        <div>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <Title level={3} style={{ margin: 0 }}>
                    <FileTextOutlined style={{ marginRight: 12 }} />
                    Issue Templates
                </Title>
                <Space>
                    <Button icon={<ReloadOutlined />} onClick={fetchTemplates} loading={loading}>
                        Refresh
                    </Button>
                </Space>
            </div>

            <Paragraph type="secondary" style={{ marginBottom: 24 }}>
                Issue templates help you create consistent, well-structured GitHub issues.
                Select a template when creating an issue to pre-fill the title and body.
            </Paragraph>

            {/* Table */}
            <Table
                columns={columns}
                dataSource={templates}
                rowKey="id"
                loading={loading}
                pagination={{
                    pageSize: 10,
                    showTotal: (total) => `${total} templates`,
                }}
            />

            {/* Preview Modal */}
            <Modal
                title={selectedTemplate?.name}
                open={previewVisible}
                onCancel={() => setPreviewVisible(false)}
                footer={[
                    <Button key="close" onClick={() => setPreviewVisible(false)}>
                        Close
                    </Button>,
                ]}
                width={700}
            >
                {selectedTemplate && (
                    <div>
                        {/* Description */}
                        {selectedTemplate.description && (
                            <Paragraph type="secondary">
                                {selectedTemplate.description}
                            </Paragraph>
                        )}

                        {/* Metadata */}
                        <Space wrap style={{ marginBottom: 16 }}>
                            <Tag color={issueTypeColors[selectedTemplate.issue_type] || 'default'}>
                                {selectedTemplate.issue_type?.replace('_', ' ')}
                            </Tag>
                            {selectedTemplate.default_labels?.map((label, idx) => (
                                <Tag key={idx}>{label}</Tag>
                            ))}
                        </Space>

                        {/* Title Template */}
                        <Card size="small" title="Title Template" style={{ marginBottom: 16 }}>
                            <Text code>{selectedTemplate.title_template || 'No title template'}</Text>
                        </Card>

                        {/* Body Template */}
                        <Card size="small" title="Body Template">
                            <pre
                                style={{
                                    whiteSpace: 'pre-wrap',
                                    backgroundColor: '#fafafa',
                                    padding: 12,
                                    borderRadius: 4,
                                    fontSize: 12,
                                    margin: 0,
                                    maxHeight: 300,
                                    overflow: 'auto',
                                }}
                            >
                                {selectedTemplate.body_template || 'No body template'}
                            </pre>
                        </Card>
                    </div>
                )}
            </Modal>
        </div>
    )
}

export default TemplatesPage
