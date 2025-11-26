/**
 * ChatMessage - Single chat message bubble component
 * Displays user or assistant messages with appropriate styling
 */

import { Space, Avatar, Card } from 'antd'
import { UserOutlined, RobotOutlined } from '@ant-design/icons'

/**
 * ChatMessage component
 * @param {Object} props
 * @param {Object} props.message - Message object
 * @param {string} props.message.content - Message content
 * @param {string} props.message.role - 'user' or 'assistant'
 * @param {string} [props.message.provider] - AI provider name (for assistant messages)
 * @param {string} [props.message.model] - AI model name (for assistant messages)
 */
function ChatMessage({ message }) {
    const isUser = message.role === 'user'

    return (
        <div
            style={{
                display: 'flex',
                justifyContent: isUser ? 'flex-end' : 'flex-start',
                marginBottom: 16,
            }}
        >
            <Space
                direction="horizontal"
                align="start"
                style={{
                    maxWidth: '70%',
                    flexDirection: isUser ? 'row-reverse' : 'row',
                }}
            >
                <Avatar
                    icon={isUser ? <UserOutlined /> : <RobotOutlined />}
                    style={{
                        backgroundColor: isUser ? '#1890ff' : '#52c41a',
                        flexShrink: 0,
                    }}
                />
                <Card
                    size="small"
                    style={{
                        backgroundColor: isUser ? '#e6f7ff' : '#f6ffed',
                        border: isUser ? '1px solid #91d5ff' : '1px solid #b7eb8f',
                    }}
                    styles={{
                        body: { padding: '12px 16px' }
                    }}
                >
                    <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>
                    {message.provider && (
                        <div
                            style={{
                                fontSize: 12,
                                color: '#999',
                                marginTop: 8,
                                borderTop: '1px solid #e8e8e8',
                                paddingTop: 8,
                            }}
                        >
                            {message.provider} • {message.model}
                            {message.cached && ' • Cached'}
                        </div>
                    )}
                </Card>
            </Space>
        </div>
    )
}

export default ChatMessage
