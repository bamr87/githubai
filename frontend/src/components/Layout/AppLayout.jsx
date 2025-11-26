/**
 * AppLayout - Main application layout with navigation
 * Provides consistent header, sidebar navigation, and content area
 */

import { useState } from 'react'
import { Layout, Menu, Typography, Space, Badge } from 'antd'
import {
    RobotOutlined,
    MessageOutlined,
    IssuesCloseOutlined,
    FileTextOutlined,
    SettingOutlined,
    HomeOutlined,
    MenuFoldOutlined,
    MenuUnfoldOutlined,
    GithubOutlined,
} from '@ant-design/icons'
import { Link, useLocation } from 'react-router-dom'

const { Header, Sider, Content, Footer } = Layout
const { Title } = Typography

/**
 * Navigation menu items configuration
 */
const menuItems = [
    {
        key: '/',
        icon: <HomeOutlined />,
        label: <Link to="/">Home</Link>,
    },
    {
        key: '/chat',
        icon: <MessageOutlined />,
        label: <Link to="/chat">AI Chat</Link>,
    },
    {
        key: '/issues',
        icon: <IssuesCloseOutlined />,
        label: <Link to="/issues">Issues</Link>,
    },
    {
        key: '/templates',
        icon: <FileTextOutlined />,
        label: <Link to="/templates">Templates</Link>,
    },
    {
        key: '/settings',
        icon: <SettingOutlined />,
        label: <Link to="/settings">Settings</Link>,
    },
]

/**
 * AppLayout component
 * @param {Object} props
 * @param {React.ReactNode} props.children - Page content to render
 */
function AppLayout({ children }) {
    const [collapsed, setCollapsed] = useState(false)
    const location = useLocation()

    // Determine the selected menu key from current path
    const selectedKey = location.pathname === '/'
        ? '/'
        : '/' + location.pathname.split('/')[1]

    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Sider
                collapsible
                collapsed={collapsed}
                onCollapse={setCollapsed}
                trigger={null}
                breakpoint="lg"
                collapsedWidth={80}
                style={{
                    overflow: 'auto',
                    height: '100vh',
                    position: 'fixed',
                    left: 0,
                    top: 0,
                    bottom: 0,
                    background: '#001529',
                }}
            >
                {/* Logo */}
                <div
                    style={{
                        height: 64,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: collapsed ? 'center' : 'flex-start',
                        padding: collapsed ? 0 : '0 24px',
                        borderBottom: '1px solid rgba(255,255,255,0.1)',
                    }}
                >
                    <RobotOutlined
                        style={{
                            fontSize: 28,
                            color: '#1890ff',
                        }}
                    />
                    {!collapsed && (
                        <Title
                            level={4}
                            style={{
                                margin: '0 0 0 12px',
                                color: '#fff',
                                whiteSpace: 'nowrap',
                            }}
                        >
                            GitHubAI
                        </Title>
                    )}
                </div>

                {/* Navigation Menu */}
                <Menu
                    theme="dark"
                    mode="inline"
                    selectedKeys={[selectedKey]}
                    items={menuItems}
                    style={{ borderRight: 0 }}
                />
            </Sider>

            <Layout style={{
                marginLeft: collapsed ? 80 : 200,
                transition: 'margin-left 0.2s',
                minHeight: '100vh',
            }}>
                {/* Header */}
                <Header
                    style={{
                        padding: '0 24px',
                        background: '#fff',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                        position: 'sticky',
                        top: 0,
                        zIndex: 1,
                    }}
                >
                    <Space>
                        {/* Collapse toggle button */}
                        <span
                            onClick={() => setCollapsed(!collapsed)}
                            style={{
                                fontSize: 18,
                                cursor: 'pointer',
                                padding: '0 12px',
                            }}
                        >
                            {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                        </span>
                    </Space>

                    <Space size="middle">
                        {/* GitHub link */}
                        <a
                            href="https://github.com/bamr87/githubai"
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ color: '#000', fontSize: 20 }}
                        >
                            <GithubOutlined />
                        </a>
                        {/* Status indicator */}
                        <Badge status="success" text="Connected" />
                    </Space>
                </Header>

                {/* Main Content */}
                <Content
                    style={{
                        margin: '24px',
                        padding: 24,
                        background: '#fff',
                        borderRadius: 8,
                        minHeight: 'calc(100vh - 64px - 70px - 48px)', // header + footer + margins
                    }}
                >
                    {children}
                </Content>

                {/* Footer */}
                <Footer
                    style={{
                        textAlign: 'center',
                        background: 'transparent',
                    }}
                >
                    GitHubAI ©{new Date().getFullYear()} - AI-Powered GitHub Automation
                </Footer>
            </Layout>
        </Layout>
    )
}

export default AppLayout
