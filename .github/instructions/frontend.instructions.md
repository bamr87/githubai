---
applyTo: "frontend/**"
description: "Frontend development guidelines for GitHubAI React application using Vite, Ant Design, Axios, and React Router. Covers component patterns, API integration, styling, and best practices."
---

# GitHubAI Frontend Development Guidelines

Instructions for GitHub Copilot when working with the GitHubAI frontend React application.

## Tech Stack

- **React 19** with JSX (not TypeScript currently)
- **Vite 7** for builds and dev server
- **Ant Design 6** for UI components
- **Axios** for HTTP requests
- **React Router 7** for client-side routing
- **ESLint 9** with React hooks plugin

## Project Structure

\`\`\`text
frontend/
├── src/
│   ├── App.jsx              # Main app with routing
│   ├── App.css              # Application styles
│   ├── main.jsx             # Entry point
│   ├── index.css            # Global styles
│   ├── components/          # Reusable components
│   │   ├── Chat/            # Chat interface components
│   │   │   ├── index.js
│   │   │   ├── ChatContainer.jsx
│   │   │   ├── ChatMessage.jsx
│   │   │   ├── MessageInput.jsx
│   │   │   └── MessageList.jsx
│   │   └── Layout/          # Layout components
│   │       ├── index.js
│   │       └── AppLayout.jsx
│   ├── pages/               # Page components (routes)
│   │   ├── index.js
│   │   ├── HomePage.jsx
│   │   ├── ChatPage.jsx
│   │   ├── IssuesPage.jsx
│   │   ├── IssueDetailPage.jsx
│   │   ├── CreateIssuePage.jsx
│   │   ├── AutoIssuePage.jsx
│   │   ├── TemplatesPage.jsx
│   │   └── SettingsPage.jsx
│   ├── services/            # API client layer
│   │   └── api.js
│   └── assets/              # Static assets
├── public/                  # Public static files
├── package.json             # Dependencies and scripts
├── vite.config.js           # Vite configuration
└── eslint.config.js         # ESLint configuration
\`\`\`

## Routing Structure

| Route | Page Component | Description |
|-------|----------------|-------------|
| \`/\` | HomePage | Landing page with overview |
| \`/chat\` | ChatPage | AI chat interface with provider selection |
| \`/issues\` | IssuesPage | Issue list/dashboard |
| \`/issues/create\` | CreateIssuePage | Manual issue creation |
| \`/issues/auto\` | AutoIssuePage | AI auto-issue generation |
| \`/issues/:id\` | IssueDetailPage | Single issue view |
| \`/templates\` | TemplatesPage | Template browser |
| \`/settings\` | SettingsPage | Settings (placeholder) |

## Component Patterns

### Use Ant Design Components

\`\`\`jsx
// ✅ Correct: Use Ant Design components
import { Layout, Button, Card, Input, List, Avatar, Space, Typography, message } from 'antd'
import { SendOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons'

const { Header, Content, Footer } = Layout
const { Title } = Typography
\`\`\`

### State Management with React Hooks

\`\`\`jsx
// ✅ Correct: Use useState for local state
const [messages, setMessages] = useState([])
const [inputValue, setInputValue] = useState('')
const [loading, setLoading] = useState(false)

// Update state immutably
setMessages(prev => [...prev, newMessage])
\`\`\`

### API Integration with API Client

\`\`\`jsx
// ✅ Correct: Use the centralized API client service
import { chatApi, issueApi, templateApi, providerApi, modelApi } from '../services/api'

// API calls with error handling
try {
  const response = await chatApi.sendMessage(inputValue, provider, model)
  // Handle success
} catch (error) {
  message.error(error.displayMessage || 'Failed to send message')
}
\`\`\`

### Loading States

\`\`\`jsx
// ✅ Correct: Track loading state for async operations
setLoading(true)
try {
  await asyncOperation()
} finally {
  setLoading(false)
}

// Use loading state in UI
<Button loading={loading} disabled={!inputValue.trim()}>
  Send
</Button>
\`\`\`

## API Client Usage

The API client is in \`src/services/api.js\` and provides typed methods for all endpoints:

\`\`\`jsx
import { chatApi, issueApi, templateApi, providerApi, modelApi, healthApi } from '../services/api'

// Chat
const response = await chatApi.sendMessage('Hello', provider, model)

// Issues
const issues = await issueApi.list({ state: 'open', issue_type: 'feature' })
const issue = await issueApi.get(123)
const newIssue = await issueApi.create({ title: '...', body: '...' })
const autoIssue = await issueApi.createAutoIssue({ chore_type: 'code_quality' })

// Templates
const templates = await templateApi.list()

// AI Providers & Models
const providers = await providerApi.list()
const models = await modelApi.list({ provider: providerId })

// Health
const status = await healthApi.check()
\`\`\`

## Styling Guidelines

### Prefer Ant Design Styling Props

\`\`\`jsx
// ✅ Correct: Use style props for component-specific styling
<Header style={{
  background: '#fff',
  padding: '0 24px',
  boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
}}>

// ✅ Correct: Use Ant Design color tokens
style={{ backgroundColor: '#1890ff' }}  // Primary blue
style={{ backgroundColor: '#52c41a' }}  // Success green
style={{ color: '#999' }}               // Secondary text
\`\`\`

### CSS Files for Global Styles

- \`index.css\` - Global resets and base styles
- \`App.css\` - Application-specific styles

## Development Commands

\`\`\`bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linting
npm run lint
\`\`\`

## API Endpoints

Backend API is at \`http://localhost:8000\` by default. Configure via \`VITE_API_URL\` environment variable.

| Endpoint | Method | Description |
|----------|--------|-------------|
| \`/api/chat/\` | POST | AI chat conversation |
| \`/api/issues/issues/\` | GET, POST | List/create issues |
| \`/api/issues/issues/{id}/\` | GET, PUT, DELETE | Issue CRUD |
| \`/api/issues/issues/create-auto-issue/\` | POST | Auto-generate issue |
| \`/api/templates/\` | GET, POST | Issue templates |
| \`/api/providers/\` | GET | List AI providers |
| \`/api/models/\` | GET | List AI models |
| \`/health/\` | GET | Health check |

## Best Practices

### DO

- ✅ Use Ant Design components for consistent UI
- ✅ Use \`message.error()\` and \`message.success()\` for user feedback
- ✅ Handle loading and error states for all async operations
- ✅ Use environment variables for configuration (\`import.meta.env.VITE_*\`)
- ✅ Destructure Ant Design sub-components (\`const { Header, Content } = Layout\`)
- ✅ Use semantic HTML within Ant Design components
- ✅ Keep components focused and single-responsibility
- ✅ Use the API client (\`src/services/api.js\`) for all backend calls
- ✅ Use React Router \`Link\` for internal navigation

### DON'T

- ❌ Install additional UI libraries (use Ant Design)
- ❌ Hardcode API URLs (use environment variables or API client)
- ❌ Ignore error handling in async operations
- ❌ Use inline styles for reusable patterns (create CSS classes)
- ❌ Mix styling approaches inconsistently
- ❌ Call axios directly (use the API client service)

## Event Handling

\`\`\`jsx
// ✅ Correct: Handle keyboard events
const handleKeyPress = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

<TextArea onKeyPress={handleKeyPress} />
\`\`\`

## Message/Notification Patterns

\`\`\`jsx
import { message } from 'antd'

// User feedback
message.error('Failed to send message. Please try again.')
message.success('Message sent successfully')
message.info('Processing your request...')
message.warning('Connection may be unstable')
\`\`\`

## Navigation Patterns

\`\`\`jsx
import { Link, useNavigate } from 'react-router-dom'

// Declarative navigation
<Link to="/issues">View Issues</Link>

// Programmatic navigation
const navigate = useNavigate()
navigate('/issues/123')
navigate(-1) // Go back
\`\`\`

## Future Considerations

When expanding the frontend:
- Consider TypeScript migration for type safety
- Add state management (Zustand/Context) for complex shared state
- Implement component testing with Vitest
- Add Storybook for component documentation
- Code splitting for large pages
