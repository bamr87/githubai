/**
 * HomePage - Landing page with overview and quick actions
 */

import { Card, Row, Col, Typography, Button, Space, Statistic } from 'antd'
import {
    MessageOutlined,
    IssuesCloseOutlined,
    FileTextOutlined,
    RocketOutlined,
    GithubOutlined,
    ThunderboltOutlined,
} from '@ant-design/icons'
import { Link } from 'react-router-dom'

const { Title, Paragraph } = Typography

/**
 * Feature card component for home page
 */
function FeatureCard({ icon, title, description, to, buttonText }) {
    return (
        <Card
            hoverable
            style={{ height: '100%' }}
            styles={{ body: { display: 'flex', flexDirection: 'column', height: '100%' } }}
        >
            <Space direction="vertical" size="middle" style={{ width: '100%', flex: 1 }}>
                <div style={{ fontSize: 32, color: '#1890ff' }}>{icon}</div>
                <Title level={4} style={{ margin: 0 }}>{title}</Title>
                <Paragraph type="secondary" style={{ flex: 1 }}>
                    {description}
                </Paragraph>
                <Link to={to}>
                    <Button type="primary" block>
                        {buttonText}
                    </Button>
                </Link>
            </Space>
        </Card>
    )
}

function HomePage() {
    const features = [
        {
            icon: <MessageOutlined />,
            title: 'AI Chat',
            description: 'Have conversations with AI assistants. Ask questions, get code help, and explore AI capabilities.',
            to: '/chat',
            buttonText: 'Start Chatting',
        },
        {
            icon: <IssuesCloseOutlined />,
            title: 'Issue Management',
            description: 'View, create, and manage GitHub issues. Use AI to auto-generate issues from code analysis.',
            to: '/issues',
            buttonText: 'View Issues',
        },
        {
            icon: <FileTextOutlined />,
            title: 'Templates',
            description: 'Browse and manage issue templates. Create consistent, well-structured issues every time.',
            to: '/templates',
            buttonText: 'Browse Templates',
        },
    ]

    return (
        <div>
            {/* Hero Section */}
            <div style={{ textAlign: 'center', marginBottom: 48 }}>
                <Title level={1}>
                    <RocketOutlined style={{ marginRight: 12, color: '#1890ff' }} />
                    GitHubAI
                </Title>
                <Paragraph style={{ fontSize: 18, color: '#666', maxWidth: 600, margin: '0 auto' }}>
                    AI-powered GitHub automation platform. Streamline your development workflow with
                    intelligent issue management, code analysis, and automated documentation.
                </Paragraph>
            </div>

            {/* Quick Stats */}
            <Row gutter={[16, 16]} style={{ marginBottom: 48 }}>
                <Col xs={24} sm={8}>
                    <Card>
                        <Statistic
                            title="AI Providers"
                            value="Multiple"
                            prefix={<ThunderboltOutlined />}
                            valueStyle={{ color: '#1890ff' }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={8}>
                    <Card>
                        <Statistic
                            title="GitHub Integration"
                            value="Active"
                            prefix={<GithubOutlined />}
                            valueStyle={{ color: '#52c41a' }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={8}>
                    <Card>
                        <Statistic
                            title="Auto Issue Types"
                            value={6}
                            prefix={<IssuesCloseOutlined />}
                            valueStyle={{ color: '#722ed1' }}
                        />
                    </Card>
                </Col>
            </Row>

            {/* Feature Cards */}
            <Title level={3}>Get Started</Title>
            <Row gutter={[24, 24]}>
                {features.map((feature) => (
                    <Col xs={24} sm={12} lg={8} key={feature.title}>
                        <FeatureCard {...feature} />
                    </Col>
                ))}
            </Row>

            {/* Quick Actions */}
            <Card style={{ marginTop: 48 }}>
                <Title level={4}>Quick Actions</Title>
                <Space wrap>
                    <Link to="/chat">
                        <Button icon={<MessageOutlined />}>New Chat</Button>
                    </Link>
                    <Link to="/issues/create">
                        <Button icon={<IssuesCloseOutlined />}>Create Issue</Button>
                    </Link>
                    <Link to="/issues/auto">
                        <Button icon={<ThunderboltOutlined />} type="primary">
                            Auto-Generate Issue
                        </Button>
                    </Link>
                </Space>
            </Card>
        </div>
    )
}

export default HomePage
