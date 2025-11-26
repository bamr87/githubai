/**
 * MessageInput - Chat input field with send button
 */

import { Input, Button, Space } from 'antd'
import { SendOutlined } from '@ant-design/icons'

const { TextArea } = Input

/**
 * MessageInput component
 * @param {Object} props
 * @param {string} props.value - Current input value
 * @param {Function} props.onChange - Input change handler
 * @param {Function} props.onSend - Send message handler
 * @param {boolean} props.loading - Loading state
 * @param {boolean} [props.disabled] - Disabled state
 */
function MessageInput({ value, onChange, onSend, loading, disabled = false }) {
    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            if (value.trim() && !loading) {
                onSend()
            }
        }
    }

    const handleSend = () => {
        if (value.trim() && !loading) {
            onSend()
        }
    }

    return (
        <Space.Compact style={{ width: '100%' }}>
            <TextArea
                value={value}
                onChange={(e) => onChange(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
                autoSize={{ minRows: 1, maxRows: 4 }}
                disabled={loading || disabled}
                style={{ resize: 'none' }}
            />
            <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleSend}
                loading={loading}
                disabled={!value.trim() || disabled}
            >
                Send
            </Button>
        </Space.Compact>
    )
}

export default MessageInput
