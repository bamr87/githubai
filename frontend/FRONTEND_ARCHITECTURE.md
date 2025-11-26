# Frontend Architecture Document

## Overview

This document describes a modern frontend architecture designed for Django-backed applications. It provides a comprehensive, vendor-neutral template that can be adapted for any project requiring a scalable, maintainable Single Page Application (SPA) with a Python/Django backend.

---

## Table of Contents

1. [Architecture Summary](#architecture-summary)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [State Management](#state-management)
5. [Routing System](#routing-system)
6. [Component Library](#component-library)
7. [API Integration](#api-integration)
8. [Build System](#build-system)
9. [Testing Strategy](#testing-strategy)
10. [Development Workflow](#development-workflow)
11. [Performance Optimization](#performance-optimization)
12. [Security Considerations](#security-considerations)
13. [Deployment Architecture](#deployment-architecture)

---

## Architecture Summary

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND SPA                                │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Scenes    │  │ Components  │  │   Models    │  │    Utils    │    │
│  │  (Pages)    │  │ (UI Library)│  │(Kea Logics) │  │  (Helpers)  │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │                │            │
│         └────────────────┼────────────────┼────────────────┘            │
│                          │                │                             │
│                    ┌─────▼─────┐    ┌─────▼─────┐                       │
│                    │  Router   │    │   Store   │                       │
│                    │(kea-router)│   │   (Kea)   │                       │
│                    └─────┬─────┘    └─────┬─────┘                       │
│                          │                │                             │
│                          └───────┬────────┘                             │
│                                  │                                      │
│                           ┌──────▼──────┐                               │
│                           │  API Client │                               │
│                           └──────┬──────┘                               │
└──────────────────────────────────┼──────────────────────────────────────┘
                                   │ HTTP/REST
┌──────────────────────────────────▼──────────────────────────────────────┐
│                           DJANGO BACKEND                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │    Views    │  │   Models    │  │ Serializers │  │    Tasks    │    │
│  │  (DRF API)  │  │   (ORM)     │  │   (DRF)     │  │  (Celery)   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Separation of Concerns**: Clear boundaries between UI, state, and data layers
2. **Type Safety**: Full TypeScript coverage with strict mode enabled
3. **Centralized State**: Single source of truth via Kea state management
4. **Component-Based UI**: Reusable, composable component architecture
5. **API-First Design**: Backend-agnostic API client with typed interfaces
6. **Progressive Enhancement**: Core functionality works, enhanced features layered on top
7. **Performance-First**: Lazy loading, code splitting, and memoization by default

---

## Technology Stack

### Core Technologies

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Framework** | React | 18.x | UI rendering and component model |
| **Language** | TypeScript | 5.x | Type safety and developer experience |
| **State Management** | Kea | 3.x | Centralized state with automatic TypeScript generation |
| **Routing** | kea-router | 3.x | URL-based routing integrated with state |
| **Styling** | Tailwind CSS | 4.x | Utility-first CSS framework |
| **Build Tool** | Vite / ESBuild | Latest | Fast development and production builds |
| **Package Manager** | pnpm | 9.x | Efficient dependency management |

### Kea Plugin Ecosystem

| Plugin | Purpose |
|--------|---------|
| `kea-loaders` | Automatic async data fetching with loading/error states |
| `kea-forms` | Form state management with validation |
| `kea-localstorage` | Persistent state in localStorage |
| `kea-subscriptions` | Reactive subscriptions to value changes |
| `kea-waitfor` | Wait for conditions before proceeding |
| `kea-window-values` | Reactive window/document properties |

### Supporting Libraries

| Category | Library | Purpose |
|----------|---------|---------|
| **HTTP Client** | fetch / axios | API communication |
| **Date/Time** | dayjs | Date manipulation (lightweight) |
| **Charts** | Chart.js / D3.js | Data visualization |
| **Forms** | kea-forms | Form handling with validation |
| **Modals** | Radix UI | Accessible modal primitives |
| **Icons** | Custom / Heroicons | Icon library |
| **Testing** | Jest + RTL | Unit and integration testing |
| **E2E Testing** | Playwright | End-to-end testing |

---

## Project Structure

### Directory Layout

```
frontend/
├── public/                     # Static assets (favicon, manifest, etc.)
│   ├── icons/                  # Application icons
│   └── images/                 # Static images
│
├── src/
│   ├── index.tsx              # Application entry point
│   ├── initKea.ts             # Kea initialization and plugin setup
│   ├── types.ts               # Global TypeScript type definitions
│   │
│   ├── @types/                # Custom TypeScript declarations
│   │   └── *.d.ts
│   │
│   ├── components/            # Shared/reusable components
│   │   ├── ui/               # Base UI components (Button, Input, etc.)
│   │   ├── forms/            # Form components and field wrappers
│   │   ├── layout/           # Layout components (Header, Sidebar, etc.)
│   │   └── common/           # Domain-agnostic shared components
│   │
│   ├── scenes/               # Page-level components (route handlers)
│   │   ├── App.tsx           # Root application component
│   │   ├── scenes.ts         # Scene/route configuration
│   │   ├── urls.ts           # Centralized URL helpers
│   │   ├── sceneLogic.ts     # Main routing logic
│   │   ├── dashboard/        # Dashboard scene
│   │   │   ├── Dashboard.tsx
│   │   │   ├── dashboardLogic.ts
│   │   │   └── components/
│   │   ├── settings/         # Settings scene
│   │   └── [feature]/        # Feature-specific scenes
│   │
│   ├── models/               # Global Kea logics (app-wide state)
│   │   ├── userLogic.ts      # Current user state
│   │   ├── organizationLogic.ts
│   │   └── [domain]Model.ts
│   │
│   ├── lib/                  # Utilities and helpers
│   │   ├── api.ts            # API client
│   │   ├── constants.ts      # Application constants
│   │   ├── utils.ts          # General utility functions
│   │   ├── dayjs.ts          # Date library wrapper
│   │   ├── hooks/            # Custom React hooks
│   │   │   ├── useDebounce.ts
│   │   │   ├── useEventListener.ts
│   │   │   └── useAsync.ts
│   │   └── logic/            # Shared Kea logics
│   │       ├── featureFlagLogic.ts
│   │       └── apiStatusLogic.ts
│   │
│   ├── queries/              # Data query definitions (optional)
│   │   ├── schema/           # Query type definitions
│   │   └── utils.ts          # Query helpers
│   │
│   ├── styles/               # Global styles
│   │   ├── index.scss        # Main stylesheet entry
│   │   ├── _variables.scss   # SCSS variables
│   │   └── _base.scss        # Base/reset styles
│   │
│   ├── mocks/                # Test mocks and fixtures
│   │   ├── handlers.ts       # MSW request handlers
│   │   └── fixtures/         # Test data fixtures
│   │
│   └── test/                 # Test utilities and setup
│       ├── setup.ts
│       └── utils.tsx
│
├── @org/                     # Internal packages (monorepo)
│   └── ui-library/           # Design system package
│       ├── src/
│       │   ├── index.ts
│       │   ├── Button/
│       │   ├── Input/
│       │   └── [Component]/
│       └── package.json
│
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── jest.config.ts
```

### File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| React Components | PascalCase | `Dashboard.tsx`, `UserProfile.tsx` |
| Kea Logics | camelCase + Logic suffix | `dashboardLogic.ts`, `userLogic.ts` |
| Utilities | camelCase | `formatDate.ts`, `api.ts` |
| Types | PascalCase | `UserType.ts`, `ApiTypes.ts` |
| Tests | Same name + .test | `Dashboard.test.tsx`, `api.test.ts` |
| Stories | Same name + .stories | `Button.stories.tsx` |
| Styles | Same name + .scss | `Dashboard.scss` |

---

## State Management

### Kea Architecture

Kea provides Redux-like state management with automatic TypeScript type generation, making it ideal for large-scale applications.

### Logic Structure

```typescript
// dashboardLogic.ts
import { kea, path, actions, reducers, selectors, loaders, listeners } from 'kea'
import type { dashboardLogicType } from './dashboardLogicType'

import { api } from 'lib/api'

export interface Dashboard {
    id: number
    name: string
    widgets: Widget[]
}

export const dashboardLogic = kea<dashboardLogicType>([
    // Path is required for TypeScript type generation
    path(['scenes', 'dashboard', 'dashboardLogic']),

    // Actions define what can happen
    actions({
        setDashboardName: (name: string) => ({ name }),
        addWidget: (widget: Widget) => ({ widget }),
        removeWidget: (widgetId: number) => ({ widgetId }),
    }),

    // Loaders handle async data fetching
    loaders(({ values }) => ({
        dashboard: [
            null as Dashboard | null,
            {
                loadDashboard: async ({ id }: { id: number }) => {
                    return await api.dashboards.get(id)
                },
                saveDashboard: async () => {
                    return await api.dashboards.update(values.dashboard!.id, values.dashboard!)
                },
            },
        ],
    })),

    // Reducers manage state changes
    reducers({
        dashboardName: [
            '',
            {
                setDashboardName: (_, { name }) => name,
                loadDashboardSuccess: (_, { dashboard }) => dashboard?.name ?? '',
            },
        ],
    }),

    // Selectors compute derived state
    selectors({
        widgetCount: [
            (s) => [s.dashboard],
            (dashboard): number => dashboard?.widgets?.length ?? 0,
        ],
        isLoading: [
            (s) => [s.dashboardLoading],
            (loading): boolean => loading,
        ],
    }),

    // Listeners handle side effects
    listeners(({ actions, values }) => ({
        saveDashboardSuccess: () => {
            // Show success notification
            toast.success('Dashboard saved')
        },
        loadDashboardFailure: ({ error }) => {
            // Handle error
            toast.error(`Failed to load dashboard: ${error.message}`)
        },
    })),
])
```

### Component Integration

```typescript
// Dashboard.tsx
import { useValues, useActions } from 'kea'
import { dashboardLogic } from './dashboardLogic'

export function Dashboard(): JSX.Element {
    // Subscribe to values
    const { dashboard, dashboardLoading, widgetCount } = useValues(dashboardLogic)
    
    // Get action dispatchers
    const { loadDashboard, setDashboardName, saveDashboard } = useActions(dashboardLogic)

    useEffect(() => {
        loadDashboard({ id: dashboardId })
    }, [dashboardId])

    if (dashboardLoading) {
        return <Spinner />
    }

    return (
        <div>
            <h1>{dashboard?.name}</h1>
            <p>{widgetCount} widgets</p>
            {/* ... */}
        </div>
    )
}
```

### Type Generation

Kea automatically generates TypeScript types for all logics:

```bash
# Generate types once
pnpm typegen:write

# Watch mode during development
pnpm typegen:watch
```

**Important Rules**:
- Never edit `*LogicType.ts` files manually
- Always run typegen before committing
- Include `path()` in every logic for proper type generation

### State Organization Patterns

| Pattern | Location | Purpose |
|---------|----------|---------|
| **Scene Logic** | `scenes/[feature]/[feature]Logic.ts` | Page-specific state |
| **Global Models** | `models/[domain]Logic.ts` | App-wide shared state |
| **Shared Logic** | `lib/logic/[feature]Logic.ts` | Reusable logic patterns |
| **Form Logic** | Co-located with scene | Form-specific state |

---

## Routing System

### Scene-Based Routing

The application uses a scene-based routing system where each "scene" represents a top-level page.

### Route Configuration

```typescript
// scenes/scenes.ts
export enum Scene {
    Dashboard = 'Dashboard',
    Settings = 'Settings',
    UserProfile = 'UserProfile',
    NotFound = '404',
}

export const routes: Record<Scene, string> = {
    [Scene.Dashboard]: '/dashboard/:id',
    [Scene.Settings]: '/settings/:section?',
    [Scene.UserProfile]: '/users/:userId',
    [Scene.NotFound]: '*',
}

export const sceneConfigurations: Record<Scene, SceneConfig> = {
    [Scene.Dashboard]: {
        name: 'Dashboard',
        requiresAuth: true,
        projectBased: true,
    },
    [Scene.Settings]: {
        name: 'Settings',
        requiresAuth: true,
    },
    // ...
}
```

### URL Helpers

```typescript
// scenes/urls.ts
export const urls = {
    dashboard: (id: number): string => `/dashboard/${id}`,
    settings: (section?: string): string => 
        section ? `/settings/${section}` : '/settings',
    userProfile: (userId: string): string => `/users/${userId}`,
    
    // With query parameters
    dashboardWithFilters: (id: number, filters: DashboardFilters): string => {
        const params = new URLSearchParams()
        if (filters.dateRange) params.set('date', filters.dateRange)
        return `/dashboard/${id}?${params.toString()}`
    },
}

// Usage
import { urls } from 'scenes/urls'
router.actions.push(urls.dashboard(123))
```

### Navigation Patterns

```typescript
// Programmatic navigation
import { router } from 'kea-router'

// Push new route
router.actions.push(urls.dashboard(123))

// Replace current route
router.actions.replace(urls.settings())

// Navigate with state
router.actions.push(urls.dashboard(123), {}, { fromWidget: true })

// Link component
import { Link } from '@org/ui-library'
<Link to={urls.dashboard(123)}>View Dashboard</Link>
```

### Route Guards

```typescript
// sceneLogic.ts
listeners(({ values }) => ({
    locationChanged: async ({ pathname }) => {
        const scene = getSceneFromPath(pathname)
        const config = sceneConfigurations[scene]

        // Authentication guard
        if (config.requiresAuth && !values.user) {
            router.actions.replace(urls.login())
            return
        }

        // Permission guard
        if (config.requiredPermission && !hasPermission(values.user, config.requiredPermission)) {
            router.actions.replace(urls.accessDenied())
            return
        }
    },
}))
```

---

## Component Library

### Design System Structure

A well-organized design system provides consistent, reusable UI components.

### Component Categories

```
@org/ui-library/src/
├── primitives/           # Base building blocks
│   ├── Button/
│   ├── Input/
│   ├── Select/
│   ├── Checkbox/
│   ├── Radio/
│   └── Switch/
│
├── feedback/             # User feedback components
│   ├── Toast/
│   ├── Alert/
│   ├── Progress/
│   ├── Spinner/
│   └── Skeleton/
│
├── layout/               # Layout components
│   ├── Card/
│   ├── Modal/
│   ├── Drawer/
│   ├── Tabs/
│   └── Accordion/
│
├── navigation/           # Navigation components
│   ├── Menu/
│   ├── Dropdown/
│   ├── Breadcrumb/
│   └── Pagination/
│
├── data-display/         # Data presentation
│   ├── Table/
│   ├── List/
│   ├── Badge/
│   ├── Tag/
│   └── Avatar/
│
├── forms/                # Form components
│   ├── Field/
│   ├── Form/
│   ├── FileInput/
│   └── DatePicker/
│
└── index.ts              # Public exports
```

### Component Interface Pattern

```typescript
// Button/Button.tsx
import { forwardRef } from 'react'
import clsx from 'clsx'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    /** Visual variant of the button */
    variant?: 'primary' | 'secondary' | 'tertiary' | 'danger'
    /** Size of the button */
    size?: 'small' | 'medium' | 'large'
    /** Shows loading spinner and disables button */
    loading?: boolean
    /** Icon to display before text */
    icon?: React.ReactNode
    /** Icon to display after text */
    iconRight?: React.ReactNode
    /** Tooltip text */
    tooltip?: string
    /** Reason why the button is disabled (shows in tooltip) */
    disabledReason?: string | null
    /** Makes button take full width */
    fullWidth?: boolean
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    function Button(
        {
            variant = 'primary',
            size = 'medium',
            loading = false,
            icon,
            iconRight,
            tooltip,
            disabledReason,
            fullWidth = false,
            disabled,
            className,
            children,
            ...props
        },
        ref
    ) {
        const isDisabled = disabled || !!disabledReason || loading

        const buttonElement = (
            <button
                ref={ref}
                disabled={isDisabled}
                className={clsx(
                    'btn',
                    `btn--${variant}`,
                    `btn--${size}`,
                    fullWidth && 'btn--full-width',
                    loading && 'btn--loading',
                    className
                )}
                {...props}
            >
                {loading && <Spinner size="small" />}
                {!loading && icon}
                {children && <span>{children}</span>}
                {iconRight}
            </button>
        )

        // Wrap with tooltip if needed
        if (tooltip || disabledReason) {
            return (
                <Tooltip content={disabledReason || tooltip}>
                    {buttonElement}
                </Tooltip>
            )
        }

        return buttonElement
    }
)
```

### Design Tokens

```typescript
// tokens.ts
export const colors = {
    primary: {
        50: '#f0f9ff',
        100: '#e0f2fe',
        500: '#0ea5e9',
        600: '#0284c7',
        700: '#0369a1',
    },
    neutral: {
        50: '#fafafa',
        100: '#f4f4f5',
        200: '#e4e4e7',
        // ...
    },
    success: { /* ... */ },
    warning: { /* ... */ },
    error: { /* ... */ },
}

export const spacing = {
    0: '0',
    1: '0.25rem',
    2: '0.5rem',
    3: '0.75rem',
    4: '1rem',
    // ...
}

export const typography = {
    fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
    },
    fontSize: {
        xs: '0.75rem',
        sm: '0.875rem',
        base: '1rem',
        lg: '1.125rem',
        // ...
    },
}
```

---

## API Integration

### API Client Architecture

```typescript
// lib/api.ts
import { getCookie } from 'lib/utils'

interface ApiConfig {
    baseUrl: string
    timeout?: number
    headers?: Record<string, string>
}

interface ApiResponse<T> {
    data: T
    status: number
    headers: Headers
}

interface ApiError {
    status: number
    statusText: string
    detail?: string
    code?: string
}

class ApiClient {
    private baseUrl: string
    private defaultHeaders: Record<string, string>

    constructor(config: ApiConfig) {
        this.baseUrl = config.baseUrl
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            ...config.headers,
        }
    }

    private async request<T>(
        method: string,
        endpoint: string,
        options?: {
            data?: unknown
            params?: Record<string, string>
            headers?: Record<string, string>
        }
    ): Promise<T> {
        const url = new URL(endpoint, this.baseUrl)
        
        if (options?.params) {
            Object.entries(options.params).forEach(([key, value]) => {
                url.searchParams.set(key, value)
            })
        }

        const response = await fetch(url.toString(), {
            method,
            headers: {
                ...this.defaultHeaders,
                'X-CSRFToken': getCookie('csrftoken') ?? '',
                ...options?.headers,
            },
            body: options?.data ? JSON.stringify(options.data) : undefined,
            credentials: 'include', // Include cookies for Django session auth
        })

        if (!response.ok) {
            const error: ApiError = {
                status: response.status,
                statusText: response.statusText,
            }
            
            try {
                const errorData = await response.json()
                error.detail = errorData.detail
                error.code = errorData.code
            } catch {
                // Response body is not JSON
            }

            throw error
        }

        // Handle 204 No Content
        if (response.status === 204) {
            return undefined as T
        }

        return response.json()
    }

    // HTTP method shortcuts
    get<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
        return this.request<T>('GET', endpoint, { params })
    }

    post<T>(endpoint: string, data?: unknown): Promise<T> {
        return this.request<T>('POST', endpoint, { data })
    }

    put<T>(endpoint: string, data?: unknown): Promise<T> {
        return this.request<T>('PUT', endpoint, { data })
    }

    patch<T>(endpoint: string, data?: unknown): Promise<T> {
        return this.request<T>('PATCH', endpoint, { data })
    }

    delete<T>(endpoint: string): Promise<T> {
        return this.request<T>('DELETE', endpoint)
    }
}

// Create singleton instance
export const api = new ApiClient({
    baseUrl: window.API_BASE_URL || '/api',
})

// Resource-specific API helpers
export const dashboardsApi = {
    list: () => api.get<Dashboard[]>('/dashboards/'),
    get: (id: number) => api.get<Dashboard>(`/dashboards/${id}/`),
    create: (data: CreateDashboard) => api.post<Dashboard>('/dashboards/', data),
    update: (id: number, data: Partial<Dashboard>) => 
        api.patch<Dashboard>(`/dashboards/${id}/`, data),
    delete: (id: number) => api.delete(`/dashboards/${id}/`),
}

export const usersApi = {
    me: () => api.get<User>('/users/me/'),
    update: (data: Partial<User>) => api.patch<User>('/users/me/', data),
}
```

### Integration with Kea

```typescript
// Using API in loaders
loaders(({ values }) => ({
    dashboards: [
        [] as Dashboard[],
        {
            loadDashboards: async () => {
                return await dashboardsApi.list()
            },
        },
    ],
}))
```

### Error Handling

```typescript
// lib/api/errorHandler.ts
export function handleApiError(error: ApiError): void {
    // Handle authentication errors
    if (error.status === 401) {
        // Redirect to login
        router.actions.push(urls.login())
        return
    }

    // Handle permission errors
    if (error.status === 403) {
        toast.error('You do not have permission to perform this action')
        return
    }

    // Handle validation errors
    if (error.status === 400) {
        toast.error(error.detail || 'Invalid request')
        return
    }

    // Handle server errors
    if (error.status >= 500) {
        toast.error('Server error. Please try again later.')
        captureException(error)
        return
    }

    // Generic error
    toast.error(error.detail || 'An error occurred')
}
```

### Streaming/SSE Support

```typescript
// lib/api/streaming.ts
import { fetchEventSource } from '@microsoft/fetch-event-source'

export async function streamResponse(
    endpoint: string,
    onMessage: (data: unknown) => void,
    onError?: (error: Error) => void
): Promise<void> {
    await fetchEventSource(`${api.baseUrl}${endpoint}`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken') ?? '',
        },
        credentials: 'include',
        onmessage(event) {
            if (event.data) {
                onMessage(JSON.parse(event.data))
            }
        },
        onerror(error) {
            onError?.(error)
            throw error // Stops reconnection
        },
    })
}
```

---

## Build System

### Vite Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig(({ mode }) => {
    const isDev = mode === 'development'

    return {
        plugins: [react()],

        resolve: {
            alias: {
                '~': resolve(__dirname, 'src'),
                '@': resolve(__dirname, 'src'),
                'lib': resolve(__dirname, 'src/lib'),
                'scenes': resolve(__dirname, 'src/scenes'),
                'models': resolve(__dirname, 'src/models'),
                'components': resolve(__dirname, 'src/components'),
                '@org/ui-library': resolve(__dirname, '@org/ui-library/src'),
            },
        },

        build: {
            outDir: 'dist',
            sourcemap: true,
            manifest: true, // Generate manifest for Django integration
            rollupOptions: {
                input: {
                    main: resolve(__dirname, 'src/index.tsx'),
                },
                output: {
                    entryFileNames: isDev 
                        ? '[name].js' 
                        : '[name]-[hash].js',
                    chunkFileNames: isDev 
                        ? 'chunk-[name].js' 
                        : 'chunk-[name]-[hash].js',
                    assetFileNames: isDev 
                        ? 'assets/[name].[ext]' 
                        : 'assets/[name]-[hash].[ext]',
                },
            },
        },

        server: {
            port: 3000,
            proxy: {
                '/api': {
                    target: 'http://localhost:8000',
                    changeOrigin: true,
                },
            },
        },

        define: {
            'process.env.NODE_ENV': JSON.stringify(mode),
        },
    }
})
```

### Django Integration

```python
# settings.py
VITE_MANIFEST_PATH = BASE_DIR / 'frontend/dist/.vite/manifest.json'

# Template context processor
def vite_assets(request):
    """Load Vite manifest and provide asset URLs to templates."""
    if settings.DEBUG:
        # Development: use Vite dev server
        return {
            'vite_dev_server': 'http://localhost:3000',
        }
    
    # Production: read manifest
    with open(settings.VITE_MANIFEST_PATH) as f:
        manifest = json.load(f)
    
    return {
        'vite_assets': manifest,
    }
```

```html
<!-- templates/base.html -->
{% if vite_dev_server %}
    <!-- Development -->
    <script type="module" src="{{ vite_dev_server }}/@vite/client"></script>
    <script type="module" src="{{ vite_dev_server }}/src/index.tsx"></script>
{% else %}
    <!-- Production -->
    <link rel="stylesheet" href="{% static vite_assets.main.css %}">
    <script type="module" src="{% static vite_assets.main.file %}"></script>
{% endif %}
```

### Build Scripts

```json
// package.json
{
    "scripts": {
        "dev": "vite",
        "build": "tsc && vite build",
        "preview": "vite preview",
        "typecheck": "tsc --noEmit",
        "typegen": "kea-typegen write",
        "typegen:watch": "kea-typegen watch",
        "lint": "eslint src --ext .ts,.tsx",
        "lint:fix": "eslint src --ext .ts,.tsx --fix",
        "format": "prettier --write 'src/**/*.{ts,tsx,json}'",
        "test": "jest",
        "test:watch": "jest --watch",
        "test:coverage": "jest --coverage"
    }
}
```

---

## Testing Strategy

### Testing Pyramid

```
         ┌───────────┐
         │   E2E     │  ← Playwright (few, critical paths)
         │  Tests    │
        ─┴───────────┴─
       ┌───────────────┐
       │  Integration  │  ← Jest + RTL (component + logic)
       │    Tests      │
      ─┴───────────────┴─
     ┌───────────────────┐
     │    Unit Tests     │  ← Jest (utilities, helpers)
     │                   │
    ─┴───────────────────┴─
```

### Unit Testing (Jest)

```typescript
// lib/utils.test.ts
import { formatCurrency, pluralize } from './utils'

describe('formatCurrency', () => {
    it.each([
        [1000, '$1,000.00'],
        [1234.56, '$1,234.56'],
        [0, '$0.00'],
    ])('formats %s as %s', (input, expected) => {
        expect(formatCurrency(input)).toBe(expected)
    })
})
```

### Component Testing (React Testing Library)

```typescript
// components/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'

describe('Button', () => {
    it('renders children', () => {
        render(<Button>Click me</Button>)
        expect(screen.getByText('Click me')).toBeInTheDocument()
    })

    it('calls onClick when clicked', () => {
        const handleClick = jest.fn()
        render(<Button onClick={handleClick}>Click</Button>)
        fireEvent.click(screen.getByRole('button'))
        expect(handleClick).toHaveBeenCalledTimes(1)
    })

    it('shows disabled reason in tooltip', () => {
        render(<Button disabledReason="Not allowed">Action</Button>)
        expect(screen.getByRole('button')).toBeDisabled()
    })
})
```

### Kea Logic Testing

```typescript
// dashboardLogic.test.ts
import { expectLogic } from 'kea-test-utils'
import { dashboardLogic } from './dashboardLogic'
import { api } from 'lib/api'

jest.mock('lib/api')

describe('dashboardLogic', () => {
    beforeEach(() => {
        jest.clearAllMocks()
    })

    it('loads dashboard data', async () => {
        const mockDashboard = { id: 1, name: 'Test Dashboard' }
        ;(api.dashboards.get as jest.Mock).mockResolvedValue(mockDashboard)

        await expectLogic(dashboardLogic, () => {
            dashboardLogic.actions.loadDashboard({ id: 1 })
        })
            .toDispatchActions(['loadDashboard', 'loadDashboardSuccess'])
            .toMatchValues({
                dashboard: mockDashboard,
                dashboardLoading: false,
            })
    })

    it('handles load failure', async () => {
        const error = new Error('Not found')
        ;(api.dashboards.get as jest.Mock).mockRejectedValue(error)

        await expectLogic(dashboardLogic, () => {
            dashboardLogic.actions.loadDashboard({ id: 999 })
        })
            .toDispatchActions(['loadDashboard', 'loadDashboardFailure'])
            .toMatchValues({
                dashboard: null,
                dashboardLoading: false,
            })
    })
})
```

### E2E Testing (Playwright)

```typescript
// e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/login')
        await page.fill('[name="email"]', 'test@example.com')
        await page.fill('[name="password"]', 'password')
        await page.click('button[type="submit"]')
        await page.waitForURL('/dashboard')
    })

    test('displays dashboard name', async ({ page }) => {
        await expect(page.locator('h1')).toContainText('Dashboard')
    })

    test('can create new widget', async ({ page }) => {
        await page.click('text=Add Widget')
        await page.fill('[name="widgetName"]', 'New Widget')
        await page.click('text=Save')
        await expect(page.locator('.widget-card')).toContainText('New Widget')
    })
})
```

### Mock Service Worker (MSW)

```typescript
// mocks/handlers.ts
import { rest } from 'msw'

export const handlers = [
    rest.get('/api/dashboards/', (req, res, ctx) => {
        return res(
            ctx.json([
                { id: 1, name: 'Dashboard 1' },
                { id: 2, name: 'Dashboard 2' },
            ])
        )
    }),

    rest.get('/api/dashboards/:id/', (req, res, ctx) => {
        const { id } = req.params
        return res(
            ctx.json({ id: Number(id), name: `Dashboard ${id}` })
        )
    }),

    rest.post('/api/dashboards/', async (req, res, ctx) => {
        const data = await req.json()
        return res(
            ctx.status(201),
            ctx.json({ id: 3, ...data })
        )
    }),
]
```

---

## Development Workflow

### Local Development

```bash
# Terminal 1: Django backend
python manage.py runserver

# Terminal 2: Frontend dev server
cd frontend && pnpm dev

# Terminal 3: Type generation (watch mode)
cd frontend && pnpm typegen:watch
```

### Code Quality Checks

```bash
# Run all checks before committing
pnpm typecheck      # TypeScript compilation
pnpm lint           # ESLint
pnpm format         # Prettier
pnpm test           # Jest tests
pnpm typegen        # Kea type generation
```

### Git Hooks (Husky + lint-staged)

```json
// package.json
{
    "lint-staged": {
        "*.{ts,tsx}": [
            "eslint --fix",
            "prettier --write"
        ],
        "*.{json,md}": [
            "prettier --write"
        ]
    }
}
```

### Environment Configuration

```typescript
// src/config.ts
interface AppConfig {
    apiBaseUrl: string
    environment: 'development' | 'staging' | 'production'
    sentryDsn?: string
    analyticsEnabled: boolean
}

// Injected by Django template
declare global {
    interface Window {
        APP_CONFIG: AppConfig
    }
}

export const config: AppConfig = window.APP_CONFIG ?? {
    apiBaseUrl: '/api',
    environment: 'development',
    analyticsEnabled: false,
}
```

---

## Performance Optimization

### Code Splitting

```typescript
// Lazy load scenes
const Dashboard = lazy(() => import('./scenes/dashboard/Dashboard'))
const Settings = lazy(() => import('./scenes/settings/Settings'))

// In router
<Suspense fallback={<PageLoader />}>
    <Routes>
        <Route path="/dashboard/:id" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
    </Routes>
</Suspense>
```

### Memoization Patterns

```typescript
// Memoize expensive computations
const processedData = useMemo(() => {
    return expensiveComputation(rawData)
}, [rawData])

// Memoize callbacks
const handleClick = useCallback((id: number) => {
    selectItem(id)
}, [selectItem])

// Memoize components
export const ExpensiveComponent = memo(function ExpensiveComponent({ data }) {
    return <ComplexVisualization data={data} />
})
```

### Virtual Scrolling

```typescript
// For large lists
import { FixedSizeList } from 'react-window'

function VirtualList({ items }: { items: Item[] }) {
    return (
        <FixedSizeList
            height={600}
            width={800}
            itemCount={items.length}
            itemSize={50}
        >
            {({ index, style }) => (
                <div style={style}>
                    <ListItem item={items[index]} />
                </div>
            )}
        </FixedSizeList>
    )
}
```

### Bundle Analysis

```bash
# Analyze bundle size
pnpm build && pnpm dlx vite-bundle-visualizer
```

---

## Security Considerations

### CSRF Protection

```typescript
// Include CSRF token in all requests
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
    ?? getCookie('csrftoken')

fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrfToken,
    },
    credentials: 'include',
})
```

### XSS Prevention

```typescript
// Use React's built-in escaping
<div>{userInput}</div>  // Safe: React escapes by default

// Avoid dangerouslySetInnerHTML
// If necessary, sanitize first:
import DOMPurify from 'dompurify'
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(htmlContent) }} />
```

### Authentication State

```typescript
// models/userLogic.ts
export const userLogic = kea([
    loaders({
        user: [
            null as User | null,
            {
                loadUser: async () => {
                    try {
                        return await api.get('/api/users/me/')
                    } catch (error) {
                        if (error.status === 401) {
                            return null // Not authenticated
                        }
                        throw error
                    }
                },
            },
        ],
    }),

    selectors({
        isAuthenticated: [(s) => [s.user], (user) => !!user],
    }),
])
```

---

## Deployment Architecture

### Build Pipeline

```yaml
# .github/workflows/frontend.yml
name: Frontend CI/CD

on:
  push:
    branches: [main]
    paths: ['frontend/**']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: pnpm/action-setup@v2
        with:
          version: 9
      
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: 'pnpm'
          cache-dependency-path: frontend/pnpm-lock.yaml
      
      - name: Install dependencies
        run: cd frontend && pnpm install --frozen-lockfile
      
      - name: Type check
        run: cd frontend && pnpm typecheck
      
      - name: Lint
        run: cd frontend && pnpm lint
      
      - name: Test
        run: cd frontend && pnpm test --coverage
      
      - name: Build
        run: cd frontend && pnpm build
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: frontend-dist
          path: frontend/dist
```

### Static File Serving

**Django Configuration**:
```python
# settings.py
STATICFILES_DIRS = [
    BASE_DIR / 'frontend/dist',
]

# For production with whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

**Nginx Configuration** (alternative):
```nginx
location /static/ {
    alias /app/frontend/dist/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Environment-Specific Configuration

```typescript
// Injected via Django template
<script>
    window.APP_CONFIG = {
        apiBaseUrl: '{{ API_BASE_URL }}',
        environment: '{{ ENVIRONMENT }}',
        sentryDsn: '{{ SENTRY_DSN }}',
        analyticsEnabled: {{ ANALYTICS_ENABLED|yesno:"true,false" }},
    };
</script>
```

---

## Appendix

### TypeScript Configuration

```jsonc
// tsconfig.json
{
    "compilerOptions": {
        "target": "ES2021",
        "lib": ["DOM", "DOM.Iterable", "ES2021"],
        "module": "ESNext",
        "moduleResolution": "bundler",
        "jsx": "react-jsx",
        "strict": true,
        "noEmit": true,
        "isolatedModules": true,
        "esModuleInterop": true,
        "skipLibCheck": true,
        "forceConsistentCasingInFileNames": true,
        "noUnusedLocals": true,
        "noUnusedParameters": true,
        "noFallthroughCasesInSwitch": true,
        "baseUrl": ".",
        "paths": {
            "~/*": ["src/*"],
            "lib/*": ["src/lib/*"],
            "scenes/*": ["src/scenes/*"],
            "models/*": ["src/models/*"],
            "components/*": ["src/components/*"],
            "@org/ui-library": ["@org/ui-library/src"]
        }
    },
    "include": ["src/**/*"],
    "exclude": ["node_modules", "dist"]
}
```

### ESLint Configuration

```javascript
// .eslintrc.js
module.exports = {
    root: true,
    parser: '@typescript-eslint/parser',
    parserOptions: {
        project: './tsconfig.json',
    },
    plugins: ['@typescript-eslint', 'react', 'react-hooks'],
    extends: [
        'eslint:recommended',
        'plugin:@typescript-eslint/recommended',
        'plugin:react/recommended',
        'plugin:react-hooks/recommended',
        'prettier',
    ],
    rules: {
        'react/react-in-jsx-scope': 'off',
        '@typescript-eslint/explicit-function-return-type': 'warn',
        '@typescript-eslint/no-explicit-any': 'error',
        'react-hooks/rules-of-hooks': 'error',
        'react-hooks/exhaustive-deps': 'warn',
    },
    settings: {
        react: {
            version: 'detect',
        },
    },
}
```

### Quick Reference Commands

| Command | Purpose |
|---------|---------|
| `pnpm dev` | Start development server |
| `pnpm build` | Production build |
| `pnpm typecheck` | TypeScript type checking |
| `pnpm typegen` | Generate Kea types |
| `pnpm lint` | Run ESLint |
| `pnpm format` | Format with Prettier |
| `pnpm test` | Run Jest tests |
| `pnpm test:e2e` | Run Playwright tests |

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11 | Initial document |

---

**Architecture Pattern**: React + TypeScript + Kea + Tailwind + Django REST
**Document Type**: Technical Architecture Specification
**Audience**: Frontend Developers, Full-Stack Engineers, Technical Architects
