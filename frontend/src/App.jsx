/**
 * App - Main application component with routing
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import { AppLayout } from './components/Layout'
import { HomePage, ChatPage, SettingsPage } from './pages'
import IssuesPage from './pages/IssuesPage'
import IssueDetailPage from './pages/IssueDetailPage'
import CreateIssuePage from './pages/CreateIssuePage'
import AutoIssuePage from './pages/AutoIssuePage'
import TemplatesPage from './pages/TemplatesPage'
import './App.css'

// Ant Design theme configuration
const theme = {
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
  },
}

function App() {
  return (
    <ConfigProvider theme={theme}>
      <BrowserRouter>
        <AppLayout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/issues" element={<IssuesPage />} />
            <Route path="/issues/create" element={<CreateIssuePage />} />
            <Route path="/issues/auto" element={<AutoIssuePage />} />
            <Route path="/issues/:id" element={<IssueDetailPage />} />
            <Route path="/templates" element={<TemplatesPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </AppLayout>
      </BrowserRouter>
    </ConfigProvider>
  )
}

export default App
