import { useState } from 'react'
import { Layout, Input, Button, List, Avatar, Space, Typography, Card, message } from 'antd'
import { SendOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons'
import axios from 'axios'
import './App.css'

const { Header, Content, Footer } = Layout
const { Title } = Typography
const { TextArea } = Input

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)

  const sendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage = {
      id: Date.now(),
      content: inputValue,
      role: 'user',
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setLoading(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/api/chat/`, {
        message: inputValue
      })

      const aiMessage = {
        id: Date.now() + 1,
        content: response.data.response,
        role: 'assistant',
        timestamp: new Date().toISOString(),
        provider: response.data.provider,
        model: response.data.model
      }

      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      message.error('Failed to send message. Please try again.')
      console.error('Error sending message:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{
        background: '#fff',
        padding: '0 24px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        display: 'flex',
        alignItems: 'center'
      }}>
        <RobotOutlined style={{ fontSize: '24px', marginRight: '12px', color: '#1890ff' }} />
        <Title level={3} style={{ margin: 0 }}>GitHubAI Chat</Title>
      </Header>

      <Content style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        <Card
          style={{
            height: 'calc(100vh - 200px)',
            display: 'flex',
            flexDirection: 'column'
          }}
        >
          <div style={{ flex: 1, overflowY: 'auto', marginBottom: '16px' }}>
            {messages.length === 0 ? (
              <div style={{
                textAlign: 'center',
                padding: '48px',
                color: '#999'
              }}>
                <RobotOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
                <p>Start a conversation with the AI assistant</p>
              </div>
            ) : (
              <List
                dataSource={messages}
                renderItem={(msg) => (
                  <List.Item
                    style={{
                      justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                      border: 'none'
                    }}
                  >
                    <Space
                      direction="horizontal"
                      align="start"
                      style={{
                        maxWidth: '70%',
                        flexDirection: msg.role === 'user' ? 'row-reverse' : 'row'
                      }}
                    >
                      <Avatar
                        icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                        style={{
                          backgroundColor: msg.role === 'user' ? '#1890ff' : '#52c41a'
                        }}
                      />
                      <Card
                        size="small"
                        style={{
                          backgroundColor: msg.role === 'user' ? '#e6f7ff' : '#f6ffed',
                          border: msg.role === 'user' ? '1px solid #91d5ff' : '1px solid #b7eb8f'
                        }}
                      >
                        <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                        {msg.provider && (
                          <div style={{
                            fontSize: '12px',
                            color: '#999',
                            marginTop: '8px'
                          }}>
                            {msg.provider} • {msg.model}
                          </div>
                        )}
                      </Card>
                    </Space>
                  </List.Item>
                )}
              />
            )}
          </div>

          <Space.Compact style={{ width: '100%' }}>
            <TextArea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
              autoSize={{ minRows: 1, maxRows: 4 }}
              disabled={loading}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={sendMessage}
              loading={loading}
              disabled={!inputValue.trim()}
            >
              Send
            </Button>
          </Space.Compact>
        </Card>
      </Content>

      <Footer style={{ textAlign: 'center' }}>
        GitHubAI ©{new Date().getFullYear()} - Powered by AI
      </Footer>
    </Layout>
  )
}

export default App
