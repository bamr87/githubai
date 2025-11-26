/**
 * ChatPage - AI Chat interface page with provider/model selection
 */

import { useState, useEffect } from 'react'
import { Typography, Select, Space } from 'antd'
import { SettingOutlined } from '@ant-design/icons'
import { ChatContainer } from '../components/Chat'
import { providerApi, modelApi } from '../services/api'

const { Title, Text } = Typography

function ChatPage() {
    const [providers, setProviders] = useState([])
    const [models, setModels] = useState([])
    const [selectedProvider, setSelectedProvider] = useState(null)
    const [selectedModel, setSelectedModel] = useState(null)
    const [loadingProviders, setLoadingProviders] = useState(false)
    const [loadingModels, setLoadingModels] = useState(false)

    // Fetch providers on mount
    useEffect(() => {
        fetchProviders()
    }, [])

    // Fetch models when provider changes
    useEffect(() => {
        if (selectedProvider) {
            fetchModels(selectedProvider)
        } else {
            setModels([])
            setSelectedModel(null)
        }
    }, [selectedProvider])

    const fetchProviders = async () => {
        setLoadingProviders(true)
        try {
            const data = await providerApi.list()
            setProviders(data.results || data)
        } catch (error) {
            console.error('Error fetching providers:', error)
            // Silently fail - providers dropdown will just be empty
        } finally {
            setLoadingProviders(false)
        }
    }

    const fetchModels = async (providerId) => {
        setLoadingModels(true)
        try {
            const data = await modelApi.list({ provider: providerId })
            const modelList = data.results || data
            setModels(modelList)
            // Auto-select default model if available
            const defaultModel = modelList.find((m) => m.is_default)
            if (defaultModel) {
                setSelectedModel(defaultModel.name)
            }
        } catch (error) {
            console.error('Error fetching models:', error)
        } finally {
            setLoadingModels(false)
        }
    }

    const handleProviderChange = (providerId) => {
        setSelectedProvider(providerId)
        setSelectedModel(null) // Reset model when provider changes
    }

    // Get provider name for chat
    const getProviderName = () => {
        if (!selectedProvider) return null
        const provider = providers.find((p) => p.id === selectedProvider)
        return provider?.name
    }

    return (
        <div style={{ height: 'calc(100vh - 64px - 70px - 96px)', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <Title level={3} style={{ margin: 0 }}>AI Chat</Title>

                {/* Provider/Model Selection */}
                <Space>
                    <SettingOutlined style={{ color: '#999' }} />
                    <Select
                        placeholder="Select Provider"
                        style={{ width: 160 }}
                        loading={loadingProviders}
                        value={selectedProvider}
                        onChange={handleProviderChange}
                        allowClear
                        options={providers.map((p) => ({
                            label: p.display_name,
                            value: p.id,
                        }))}
                    />
                    <Select
                        placeholder="Select Model"
                        style={{ width: 180 }}
                        loading={loadingModels}
                        value={selectedModel}
                        onChange={setSelectedModel}
                        disabled={!selectedProvider}
                        allowClear
                        options={models.map((m) => ({
                            label: (
                                <Space>
                                    {m.display_name}
                                    {m.is_default && <Text type="secondary" style={{ fontSize: 10 }}>(default)</Text>}
                                </Space>
                            ),
                            value: m.name,
                        }))}
                    />
                </Space>
            </div>

            <div style={{ flex: 1, minHeight: 0 }}>
                <ChatContainer
                    provider={getProviderName()}
                    model={selectedModel}
                />
            </div>
        </div>
    )
}

export default ChatPage
