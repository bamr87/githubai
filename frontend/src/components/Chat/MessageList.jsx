/**
 * MessageList - Displays list of chat messages with empty state
 */

import { RobotOutlined } from '@ant-design/icons'
import ChatMessage from './ChatMessage'

/**
 * MessageList component
 * @param {Object} props
 * @param {Array} props.messages - Array of message objects
 */
function MessageList({ messages }) {
    if (messages.length === 0) {
        return (
            <div
                style={{
                    textAlign: 'center',
                    padding: 48,
                    color: '#999',
                }}
            >
                <RobotOutlined style={{ fontSize: 48, marginBottom: 16 }} />
                <p>Start a conversation with the AI assistant</p>
                <p style={{ fontSize: 12 }}>
                    Ask questions about code, request help with GitHub issues, or explore AI features
                </p>
            </div>
        )
    }

    return (
        <div>
            {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
            ))}
        </div>
    )
}

export default MessageList
