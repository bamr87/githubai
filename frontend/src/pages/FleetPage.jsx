/**
 * FleetPage - DevOps cockpit fleet overview
 *
 * A single place to view the health of every tracked repository: aggregate
 * KPIs, a per-repo health grid, cross-cutting "needs attention" lists, and an
 * AI-distilled fleet digest.
 */

import { useEffect, useState } from 'react'
import {
    Card,
    Table,
    Typography,
    Row,
    Col,
    Statistic,
    Tag,
    Button,
    Space,
    Alert,
    List,
    Progress,
    Spin,
    message,
} from 'antd'
import {
    DashboardOutlined,
    ReloadOutlined,
    SafetyOutlined,
    BranchesOutlined,
    BulbOutlined,
} from '@ant-design/icons'
import { dashboardApi } from '../services/api'

const { Title, Paragraph, Text } = Typography

/**
 * Map a 0-100 health score to an Ant Design progress status colour.
 */
function healthStatus(score) {
    if (score === null || score === undefined) return 'normal'
    if (score >= 80) return 'success'
    if (score >= 50) return 'active'
    return 'exception'
}

function FleetPage() {
    const [loading, setLoading] = useState(true)
    const [overview, setOverview] = useState({ totals: {}, repositories: [] })
    const [attention, setAttention] = useState(null)
    const [digest, setDigest] = useState(null)
    const [digestLoading, setDigestLoading] = useState(false)

    const loadData = async () => {
        setLoading(true)
        try {
            const [overviewData, attentionData] = await Promise.all([
                dashboardApi.fleetOverview(),
                dashboardApi.fleetAttention(),
            ])
            setOverview(overviewData)
            setAttention(attentionData)
        } catch (err) {
            message.error(err.displayMessage || 'Failed to load fleet data')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        loadData()
    }, [])

    const handleGenerateDigest = async () => {
        setDigestLoading(true)
        try {
            // Rule-based by default so the cockpit works without AI configured.
            const result = await dashboardApi.generateFleetDigest(false)
            setDigest(result)
        } catch (err) {
            message.error(err.displayMessage || 'Failed to generate digest')
        } finally {
            setDigestLoading(false)
        }
    }

    const totals = overview.totals || {}

    const columns = [
        {
            title: 'Repository',
            dataIndex: 'full_name',
            key: 'full_name',
            render: (text, record) => (
                record.html_url
                    ? <a href={record.html_url} target="_blank" rel="noopener noreferrer">{text}</a>
                    : <Text strong>{text}</Text>
            ),
        },
        {
            title: 'Health',
            dataIndex: 'health_score',
            key: 'health_score',
            render: (score) => (
                score === null || score === undefined
                    ? <Tag>No data</Tag>
                    : <Progress percent={score} size="small" status={healthStatus(score)} style={{ width: 120 }} />
            ),
            sorter: (a, b) => (a.health_score ?? -1) - (b.health_score ?? -1),
        },
        {
            title: 'Open PRs',
            dataIndex: 'open_prs',
            key: 'open_prs',
            render: (v, r) => (r.has_metrics ? `${v} (${r.stale_prs} stale)` : '—'),
        },
        {
            title: 'Open Issues',
            dataIndex: 'open_issues',
            key: 'open_issues',
            render: (v, r) => (r.has_metrics ? v : '—'),
        },
        {
            title: 'CI',
            dataIndex: 'ci_success_rate',
            key: 'ci_success_rate',
            render: (rate) => {
                if (rate === null || rate === undefined) return '—'
                const pct = Math.round(rate * 100)
                const color = pct === 100 ? 'green' : pct >= 50 ? 'orange' : 'red'
                return <Tag color={color}>{pct}%</Tag>
            },
        },
        {
            title: 'Security',
            dataIndex: 'security_alerts',
            key: 'security_alerts',
            render: (count, r) => {
                if (!r.has_metrics) return '—'
                return count > 0
                    ? <Tag color="red"><SafetyOutlined /> {count}</Tag>
                    : <Tag color="green">0</Tag>
            },
        },
        {
            title: 'Last Release',
            dataIndex: 'last_release_tag',
            key: 'last_release_tag',
            render: (tag) => (tag ? <Tag>{tag}</Tag> : '—'),
        },
    ]

    return (
        <div>
            <Space style={{ justifyContent: 'space-between', width: '100%', marginBottom: 16 }}>
                <Title level={2} style={{ margin: 0 }}>
                    <DashboardOutlined /> Fleet Dashboard
                </Title>
                <Button icon={<ReloadOutlined />} onClick={loadData} loading={loading}>
                    Refresh
                </Button>
            </Space>
            <Paragraph type="secondary">
                One-glance triage across all tracked repositories. Register repositories and run
                ingestion (via the API or <Text code>manage.py ingest_metrics</Text>) to populate signals.
            </Paragraph>

            {/* Aggregate KPIs */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col xs={12} sm={8} md={4}>
                    <Card><Statistic title="Repositories" value={totals.repositories || 0} /></Card>
                </Col>
                <Col xs={12} sm={8} md={4}>
                    <Card><Statistic title="Open PRs" value={totals.open_prs || 0} /></Card>
                </Col>
                <Col xs={12} sm={8} md={4}>
                    <Card><Statistic title="Stale PRs" value={totals.stale_prs || 0} valueStyle={{ color: (totals.stale_prs || 0) > 0 ? '#faad14' : undefined }} /></Card>
                </Col>
                <Col xs={12} sm={8} md={4}>
                    <Card><Statistic title="Open Issues" value={totals.open_issues || 0} /></Card>
                </Col>
                <Col xs={12} sm={8} md={4}>
                    <Card><Statistic title="Failing CI" value={totals.failing_ci || 0} valueStyle={{ color: (totals.failing_ci || 0) > 0 ? '#cf1322' : undefined }} /></Card>
                </Col>
                <Col xs={12} sm={8} md={4}>
                    <Card><Statistic title="Security Alerts" value={totals.security_alerts || 0} valueStyle={{ color: (totals.security_alerts || 0) > 0 ? '#cf1322' : undefined }} /></Card>
                </Col>
            </Row>

            {/* Repo health grid */}
            <Card title="Repository Health" style={{ marginBottom: 24 }}>
                <Table
                    rowKey="id"
                    loading={loading}
                    columns={columns}
                    dataSource={overview.repositories || []}
                    pagination={{ pageSize: 10 }}
                    locale={{ emptyText: 'No repositories registered yet.' }}
                />
            </Card>

            {/* Cross-cutting attention lists */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col xs={24} md={8}>
                    <Card title={<span><BranchesOutlined /> Failing CI</span>} size="small">
                        <List
                            size="small"
                            dataSource={attention?.failing_ci || []}
                            locale={{ emptyText: 'All green' }}
                            renderItem={(item) => (
                                <List.Item>
                                    <Text>{item.full_name}</Text>
                                    <Tag color="red">{Math.round((item.ci_success_rate || 0) * 100)}%</Tag>
                                </List.Item>
                            )}
                        />
                    </Card>
                </Col>
                <Col xs={24} md={8}>
                    <Card title={<span><SafetyOutlined /> Security Alerts</span>} size="small">
                        <List
                            size="small"
                            dataSource={attention?.open_security_alerts || []}
                            locale={{ emptyText: 'No open alerts' }}
                            renderItem={(item) => (
                                <List.Item>
                                    <Text>{item.full_name}</Text>
                                    <Tag color="red">{item.security_alerts}</Tag>
                                </List.Item>
                            )}
                        />
                    </Card>
                </Col>
                <Col xs={24} md={8}>
                    <Card title={<span><BranchesOutlined /> Stale PRs</span>} size="small">
                        <List
                            size="small"
                            dataSource={attention?.stale_pull_requests || []}
                            locale={{ emptyText: 'No stale PRs' }}
                            renderItem={(item) => (
                                <List.Item>
                                    <Text>{item.full_name}</Text>
                                    <Tag color="orange">{item.stale_prs}</Tag>
                                </List.Item>
                            )}
                        />
                    </Card>
                </Col>
            </Row>

            {/* AI fleet digest */}
            <Card
                title={<span><BulbOutlined /> Fleet Digest</span>}
                extra={
                    <Button type="primary" onClick={handleGenerateDigest} loading={digestLoading}>
                        Generate Digest
                    </Button>
                }
            >
                {digestLoading && <Spin />}
                {!digestLoading && !digest && (
                    <Paragraph type="secondary">
                        Generate an AI-distilled "what needs attention" briefing across the fleet.
                    </Paragraph>
                )}
                {!digestLoading && digest && (
                    <Alert
                        type={digest.severity === 'critical' || digest.severity === 'high' ? 'error'
                            : digest.severity === 'medium' ? 'warning' : 'info'}
                        message={digest.title}
                        description={<pre style={{ whiteSpace: 'pre-wrap', margin: 0, fontFamily: 'inherit' }}>{digest.summary}</pre>}
                        showIcon
                    />
                )}
            </Card>
        </div>
    )
}

export default FleetPage
