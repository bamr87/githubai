/**
 * ChatContainer - Main chat interface component
 * Manages chat state and orchestrates chat components
 */

import { useState, useRef, useEffect } from 'react'
import { Card, message } from 'antd'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import { chatApi } from '../../services/api'

/**
 * ChatContainer component
 * @param {Object} props
 * @param {string} [props.provider] - Optional AI provider override
 * @param {string} [props.model] - Optional AI model override
 */
function ChatContainer({ provider = null, model = null }) {
    const [messages, setMessages] = useState([])
    const [inputValue, setInputValue] = useState('')
    const [loading, setLoading] = useState(false)
    const messagesEndRef = useRef(null)

    // Auto-scroll to bottom when new messages arrive
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const sendMessage = async () => {
        if (!inputValue.trim()) return

        const userMessage = {
            id: Date.now(),
            content: inputValue,
            role: 'user',
            timestamp: new Date().toISOString(),
        }

        setMessages((prev) => [...prev, userMessage])
        const messageToSend = inputValue
        setInputValue('')
        setLoading(true)

        try {
            const response = await chatApi.sendMessage(messageToSend, provider, model)

            const aiMessage = {
                id: Date.now() + 1,
                content: response.response,
                role: 'assistant',
                timestamp: response.timestamp || new Date().toISOString(),
                provider: response.provider,
                model: response.model,
                cached: response.cached,
            }

            setMessages((prev) => [...prev, aiMessage])
        } catch (error) {
            message.error(error.displayMessage || 'Failed to send message. Please try again.')
            console.error('Error sending message:', error)
        } finally {
            setLoading(false)
        }
    }

    return (
        <Card
            style={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
            }}
            styles={{
                body: {
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    padding: 16,
                    overflow: 'hidden',
                }
            }}
        >
            {/* Messages Area */}
            <div
                style={{
                    flex: 1,
                    overflowY: 'auto',
                    marginBottom: 16,
                    paddingRight: 8,
                }}
            >
                <MessageList messages={messages} />
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <MessageInput
                value={inputValue}
                onChange={setInputValue}
                onSend={sendMessage}
                loading={loading}
            />
        </Card>
    )
}

export default ChatContainer
