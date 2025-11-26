/**
 * SettingsPage - Application settings placeholder
 */

import { Typography, Card, Alert, Space } from 'antd'
import { SettingOutlined } from '@ant-design/icons'

const { Title, Paragraph } = Typography

function SettingsPage() {
    return (
        <div>
            <Title level={3}>
                <SettingOutlined style={{ marginRight: 12 }} />
                Settings
            </Title>

            <Alert
                message="Coming Soon"
                description="Settings configuration will be available in a future release. This will include AI provider selection, API key management, and user preferences."
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
            />

            <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <Card title="AI Provider Configuration">
                    <Paragraph type="secondary">
                        Configure your preferred AI providers and models. Select default models for chat
                        and issue generation tasks.
                    </Paragraph>
                </Card>

                <Card title="GitHub Integration">
                    <Paragraph type="secondary">
                        Manage GitHub repository connections, access tokens, and webhook configurations.
                    </Paragraph>
                </Card>

                <Card title="User Preferences">
                    <Paragraph type="secondary">
                        Customize your experience with theme selection, notification preferences,
                        and default behaviors.
                    </Paragraph>
                </Card>
            </Space>
        </div>
    )
}

export default SettingsPage
