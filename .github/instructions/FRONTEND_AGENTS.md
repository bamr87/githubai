# Kea-React Frontend Development Guide

## Frontend Architecture Overview

This guide covers a React-based Single Page Application (SPA) architecture with the following characteristics:

### Technology Stack

- **Framework**: React 18 with TypeScript 5.2
- **Build Tools**:
  - Primary: ESBuild via custom `build.mjs`
  - Development: Vite (experimental/optional via `pnpm start-vite`)
  - Bundler: Turbo for monorepo orchestration
- **State Management**: Kea (Redux-like state management with TypeScript codegen)
- **Routing**: kea-router (integrated with Kea state)
- **Styling**:
  - Tailwind CSS 4.0
  - SCSS for legacy/custom styles
  - Custom Lemon UI component library
- **UI Components**: Custom `@posthog/lemon-ui` design system
- **Package Manager**: pnpm with workspaces
- **Node Version**: >=22 <23

### Project Structure

```text
frontend/
├── @posthog/               # Internal packages
│   ├── lemon-ui/          # Design system components
│   └── ee/                # Enterprise edition exports
├── src/
│   ├── index.tsx          # Main app entry point
│   ├── initKea.ts         # Kea initialization & plugins
│   ├── layout/            # Layout components & navigation
│   ├── lib/               # Shared utilities, hooks, components
│   ├── models/            # Global Kea logics (data models)
│   ├── queries/           # Query system (HogQL, schema, runners)
│   ├── scenes/            # Page-level components (route handlers)
│   ├── stories/           # Storybook stories
│   ├── styles/            # Global styles
│   ├── taxonomy/          # Event/property definitions
│   ├── exporter/          # Insight export standalone app
│   ├── toolbar/           # PostHog toolbar standalone app
│   └── types.ts           # Global TypeScript types
├── public/                # Static assets
├── bin/                   # Build & utility scripts
└── dist/                  # Build output
```

### Product Modules (Monorepo - Optional)

If using a monorepo structure, product modules can be organized as:

- Workspace packages with scoped names (e.g., `@org/product-*`)
- Each product has its own `frontend/` directory with scenes/components
- Products integrate into main app via manifest and scene registration

## State Management with Kea

### Kea Philosophy

Kea is the **central nervous system** of this frontend architecture. All state, data fetching, and side effects flow through Kea logics. Kea provides Redux-like state management with automatic TypeScript type generation and plugin-based extensibility.

### Logic Structure

```typescript
import { kea, path, actions, reducers, listeners, selectors, loaders } from 'kea'
import type { myLogicType } from './myLogicType'

export const myLogic = kea<myLogicType>([
    path(['path', 'to', 'logic']),  // Required for TypeScript codegen
    
    actions({
        // Define actions (similar to Redux actions)
        setUser: (user: User) => ({ user }),
        loadData: true,
    }),
    
    loaders(({ actions, values }) => ({
        // Automatic loading state management
        data: {
            loadData: async () => {
                const response = await api.get('endpoint')
                return response.data
            },
        },
    })),
    
    reducers({
        // State reducers
        user: [
            null as User | null,
            {
                setUser: (_, { user }) => user,
            },
        ],
    }),
    
    selectors({
        // Derived state
        userName: [(s) => [s.user], (user) => user?.name ?? 'Anonymous'],
    }),
    
    listeners(({ actions, values }) => ({
        // Side effects
        loadData: async () => {
            // Called when loadData action fires
        },
    })),
])
```

### Kea Type Generation

**Critical**: Kea uses automatic TypeScript type generation.

- Types are generated as `*LogicType.ts` files alongside each logic
- Run `pnpm typegen:write` to generate types for all logics
- Run `pnpm typegen:watch` during development for auto-generation
- **NEVER** edit `*LogicType.ts` files manually
- **NEVER** commit changes without running typegen first
- Git ignores `*LogicType.ts` files via `.prettierignore`

### Kea Plugins

PostHog uses these Kea plugins (configured in `initKea.ts`):

1. **loadersPlugin**: Automatic async data fetching with loading/error states
2. **formsPlugin**: Form state management
3. **routerPlugin**: URL routing integrated with state
4. **localStoragePlugin**: Persist state to localStorage
5. **windowValuesPlugin**: Reactive window properties
6. **subscriptionsPlugin**: React to value changes
7. **waitForPlugin**: Wait for conditions before proceeding

### Connecting Components to Kea

```typescript
import { useValues, useActions } from 'kea'
import { myLogic } from './myLogic'

export function MyComponent(): JSX.Element {
    const { data, dataLoading } = useValues(myLogic)
    const { loadData } = useActions(myLogic)
    
    return (
        <div>
            {dataLoading ? <Spinner /> : <div>{data}</div>}
        </div>
    )
}
```

### Global Models

Located in `src/models/`, these are app-wide Kea logics. Common patterns include:

- `userLogic`: Current user authentication and profile state
- `organizationLogic`: Organization/tenant context
- `featureFlagLogic`: Feature flag values and A/B test variants
- Domain-specific models: Entities shared across multiple scenes
- Configuration models: App settings, preferences, theme

## Routing & Scenes

### Scene System

This architecture uses a scene-based routing system:

- **Scene**: A top-level page/route (defined in `scenes/scenes.ts` or equivalent)
- **Scene Logic**: Main routing logic orchestrates scene loading and navigation
- **Lazy Loading**: Scenes are code-split and loaded on-demand
- **Tabs**: Optional multi-tab interface with persistence (sessionStorage/localStorage)

### Route Configuration

```typescript
// scenes/scenes.ts (or your routes configuration file)
export const routes: Record<Scene, string | undefined> = {
    [Scene.Dashboard]: '/dashboard/:id',
    [Scene.Analytics]: '/analytics',
    [Scene.Settings]: '/settings/:section?',
    // ... more routes
}

export const sceneConfigurations: Partial<Record<Scene, SceneConfig>> = {
    [Scene.Dashboard]: {
        name: 'Dashboard',
        requiresAuth: true,
        // Additional scene-specific configuration
    },
}
```

### URL Patterns

- Context-scoped URLs: `/workspace/:workspaceId/dashboard/123` or `/org/:orgId/resource/:id`
- Auto-inject context identifiers via router plugin configuration
- Use centralized URL helpers (e.g., `urls.ts`) for all URL generation (NEVER hardcode URLs)

### Navigation

```typescript
import { router } from 'kea-router'
import { urls } from 'scenes/urls'

// Navigate programmatically
router.actions.push(urls.dashboard(123))

// Link component (use your UI library's Link component)
import { Link } from '@your-org/ui-library'
<Link to={urls.analytics()}>Go to Analytics</Link>
```

## Custom UI Design System

### Component Library

The custom design system lives in `@your-org/ui-library/src/` or similar:

**Core Components Pattern**:

- `Button`: Primary button component with variants (primary, secondary, tertiary)
- `Input`: Text input with validation and error states
- `Select`: Dropdown select with search/filter capabilities
- `Table`: Data table with sorting/filtering/pagination
- `Modal`: Modal dialogs with header/content/footer sections
- `Dropdown`: Dropdown menus (often built with Radix UI or similar)
- `Tabs`: Tab interface for content organization
- `Tag/Chip`: Labels/badges for categorization
- `Badge`: Notification badges with counts
- `Switch/Toggle`: Toggle switches for binary options
- `Progress`: Progress bars and indicators

### Design Principles

1. **Sentence casing**: All UI text uses sentence casing ("Save as view", not "Save As View")
2. **Consistent spacing**: Use Tailwind spacing utilities
3. **Accessibility**: All components support ARIA attributes
4. **Tooltips**: Use `tooltip` prop for hints (NEVER `title` attribute directly)
5. **Disabled state**: Use `disabledReason` prop (not just `disabled`)

### Component Usage

```typescript
import { Button } from '@your-org/ui-library'

<Button
    variant="primary"
    onClick={handleClick}
    loading={isLoading}
    disabledReason={!canSave && "You don't have permission"}
    icon={<IconPlus />}
    tooltip="Create a new item"
>
    Create item
</Button>
```

### Styling Approach

1. **Prefer Tailwind**: Use utility classes for most styling
2. **Component SCSS**: Only for complex component-specific styles
3. **Global styles**: Minimal, in `src/styles/`
4. **CSS Modules**: Not used (use Tailwind or SCSS)

```typescript
// Good: Tailwind utilities
<div className="flex items-center gap-2 p-4 bg-white rounded">

// Acceptable: Component-specific SCSS
<div className="MyComponent">  {/* See MyComponent.scss */}

// Avoid: Inline styles (unless dynamic)
<div style={{ color: 'red' }}>  {/* Only for dynamic values */}
```

## Data Fetching & API

### API Client

Centralized API client in `src/lib/api.ts`:

```typescript
import { api } from 'lib/api'

// Type-safe API calls
const dashboard = await api.dashboards.get(dashboardId)
const insights = await api.insights.list({ limit: 10 })
```

### Loader Pattern (Recommended)

Use Kea loaders for data fetching:

```typescript
loaders(({ actions }) => ({
    dashboard: [
        null as Dashboard | null,
        {
            loadDashboard: async ({ id }: { id: number }) => {
                return await api.dashboards.get(id)
            },
        },
    ],
})),

listeners(({ actions }) => ({
    loadDashboard: async ({ id }, breakpoint) => {
        // Can add side effects here
    },
})),
```

**Benefits**:

- Automatic `dashboardLoading` state
- Automatic error handling with toasts
- Cancellation support via breakpoints

### Query System (Optional)

If your application uses a structured query system:

- **Query Schema**: Define query types in `src/queries/schema/` or similar
- **Query Language**: SQL-like or custom query language (e.g., GraphQL, custom DSL)
- **Query Nodes**: Typed query structures for different query types
- **Query Runners**: Backend execution via dedicated API endpoint

```typescript
import type { Query } from '~/queries/schema'

const query: Query = {
    kind: 'DataQuery',
    // Query structure based on your schema
}

const response = await api.query(query)
```

## TypeScript Conventions

### Type Safety Rules

1. **Explicit return types**: Required for all functions
2. **No `any`**: Use `unknown` or proper types
3. **Strict mode**: Follow TypeScript strict rules
4. **Type imports**: Use `import type` for type-only imports

```typescript
// Good
import type { User } from '~/types'
export function getUser(id: number): User | null {
    return users[id] ?? null
}

// Bad
export function getUser(id) {  // Missing types
    return users[id]  // Missing return type
}
```

### Import Paths

Use absolute imports via path aliases:

```typescript
// Good
import { api } from 'lib/api'
import { urls } from 'scenes/urls'
import { LemonButton } from '@posthog/lemon-ui'

// Bad
import { api } from '../../lib/api'
import LemonButton from '../../../@posthog/lemon-ui/src/LemonButton'
```

**Configured aliases** (in `tsconfig.json` - adapt to your structure):

- `lib/*` → `frontend/src/lib/*` or `src/lib/*`
- `scenes/*` → `frontend/src/scenes/*` or `src/scenes/*`
- `components/*` → `frontend/src/components/*` or `src/components/*`
- `@your-org/ui-library` → Path to your UI library
- `@your-org/*` → Paths to your workspace packages
- `~/*` → `frontend/src/*` or `src/*` (project root alias)

### Import Sorting

Uses `prettier-plugin-sort-imports` (auto-applied on format):

```typescript
// Order: external, @your-org, absolute, relative
import React from 'react'
import { useValues } from 'kea'

import { Button } from '@your-org/ui-library'

import { api } from 'lib/api'
import { urls } from 'scenes/urls'

import { myLogic } from './myLogic'
```

## Testing

### Test Structure

- Unit tests: Co-located with source files (`*.test.ts(x)`)
- One top-level `describe` block per file
- Use parameterized tests (`it.each`) for multiple cases
- No docstrings in tests

### Running Tests

```bash
# All frontend tests
pnpm test

# Specific test file
pnpm jest path/to/test.test.ts

# Watch mode
pnpm jest --watch

# Single test
pnpm jest path/to/test.test.ts -t "test name pattern"
```

### Test Utilities

```typescript
import { expectLogic } from 'kea-test-utils'
import { render, screen } from '@testing-library/react'

// Testing Kea logics
await expectLogic(myLogic)
    .toDispatchActions(['loadData'])
    .toMatchValues({ data: expectedData })

// Testing React components
render(<MyComponent />)
expect(screen.getByText('Hello')).toBeInTheDocument()
```

### Mocking

- API mocks: Use MSW (Mock Service Worker) in `src/mocks/handlers.ts`
- PostHog mocks: Auto-mocked in `src/mocks/jest.ts`
- Browser APIs: Use `jest.spyOn` or fake implementations

## Development Workflow

### Starting Development

```bash
# Full stack (recommended)
./bin/start

# Minimal services (faster)
./bin/start --minimal

# Frontend only with Vite (experimental)
pnpm start-vite
```

**Services typically started**:

- Backend API server: <http://localhost:8000> (or configured port)
- Frontend dev server: <http://localhost:8234> (Vite/ESBuild) or served by backend
- Background workers/jobs: If applicable
- Additional microservices: As needed for your architecture

### Build Commands

```bash
# Production build
pnpm build

# Build specific products
pnpm build:products

# Tailwind CSS
pnpm build:tailwind
pnpm watch:tailwind  # Watch mode

# Type generation
pnpm typegen:write
pnpm typegen:watch
```

### Code Quality

```bash
# Format code
pnpm format  # oxlint + prettier

# Check formatting
pnpm prettier:check

# Type checking
pnpm typescript:check

# Lint (JS + CSS)
pnpm lint
pnpm lint:js
pnpm lint:css
```

**Pre-commit**: Uses `husky` + `lint-staged` for auto-formatting

### Hot Reload

- ESBuild: Fast incremental builds (~100-500ms)
- Vite: Instant HMR for most changes
- Kea: Logic changes require full page reload
- Components: Fast refresh preserves React state

## Common Patterns

### Form Handling

Use `kea-forms` plugin:

```typescript
import { kea } from 'kea'
import { forms } from 'kea-forms'

export const myLogic = kea([
    forms(({ actions }) => ({
        userForm: {
            defaults: { name: '', email: '' } as UserForm,
            errors: ({ name, email }) => ({
                name: !name ? 'Required' : undefined,
                email: !email?.includes('@') ? 'Invalid email' : undefined,
            }),
            submit: async (values) => {
                await api.users.create(values)
                actions.resetUserForm()
            },
        },
    })),
])

// In component
const { userForm } = useValues(myLogic)
const { setUserFormValue, submitUserForm } = useActions(myLogic)

<Input
    value={userForm.name}
    onChange={(value) => setUserFormValue('name', value)}
    error={userForm.errors.name}
/>
```

### Feature Flags

```typescript
import { useValues } from 'kea'
import { featureFlagLogic } from 'lib/logic/featureFlagLogic'

const { featureFlags } = useValues(featureFlagLogic)

if (featureFlags['new-feature']) {
    // Show new feature
}
```

### Error Handling

```typescript
// In loaders (automatic toast)
loaders({
    data: {
        loadData: async () => {
            // Errors automatically show toast via loadersPlugin
            return await api.get('endpoint')
        },
    },
})

// Manual error handling
try {
    await api.dangerous.operation()
} catch (error) {
    lemonToast.error(`Operation failed: ${error.detail}`)
    posthog.captureException(error)
}
```

### Responsive Design

Use Tailwind breakpoints:

```typescript
<div className="flex flex-col md:flex-row lg:gap-4">
    {/* Mobile: column, Desktop: row */}
</div>
```

Breakpoints: `sm:640px`, `md:768px`, `lg:1024px`, `xl:1280px`, `2xl:1536px`

## Performance Considerations

### Code Splitting

- Scenes are automatically lazy-loaded
- Use dynamic imports for heavy components:

```typescript
const HeavyChart = lazy(() => import('./HeavyChart'))

<Suspense fallback={<Spinner />}>
    <HeavyChart data={data} />
</Suspense>
```

### Memoization

```typescript
import { useMemo, memo } from 'react'

// Memoize expensive computations
const processedData = useMemo(() => {
    return heavyComputation(data)
}, [data])

// Memoize components
export const MyComponent = memo(function MyComponent({ data }) {
    return <div>{data}</div>
})
```

### Virtual Scrolling

For large lists, use `react-virtualized`:

```typescript
import { List } from 'react-virtualized'

<List
    width={800}
    height={600}
    rowCount={items.length}
    rowHeight={40}
    rowRenderer={({ index, key, style }) => (
        <div key={key} style={style}>{items[index]}</div>
    )}
/>
```

## Debugging

### Browser DevTools

- React DevTools: Inspect component hierarchy
- Redux DevTools: **DISABLED** (use Kea logger instead)
- PostHog DevTools: `window.posthog.debug()`

### Kea Debugging

Enable Kea logging:

```javascript
// In browser console
localStorage.setItem('ph-kea-debug', 'true')
// Reload page

// Or set in code (for sampling)
window.JS_KEA_VERBOSE_LOGGING = true
```

### Common Issues

1. **"Cannot read property of undefined"**
   - Check if data is loaded: `dataLoading` state
   - Use optional chaining: `user?.name`

2. **State not updating**
   - Ensure action is dispatched: Check Kea logs
   - Check if reducer handles the action

3. **Infinite loops**
   - Check `listeners` dependencies
   - Avoid dispatching actions that trigger the same listener

4. **Type errors after pulling**
   - Run `pnpm typegen:write`
   - Delete `node_modules/.cache` and rebuild

## Critical Rules

### DO

- Use Kea for all state management
- Use your design system components consistently
- Follow TypeScript strict mode
- Use absolute imports via configured path aliases
- Run `pnpm typegen:write` (or equivalent) before committing
- Use sentence casing for all UI text (or follow your style guide)
- Handle loading and error states explicitly
- Add tooltips/help text for non-obvious UI elements
- Provide reasons for disabled states (e.g., `disabledReason` prop)

### DON'T

- Use Redux or other state libraries
- Create inline styles unless dynamic
- Use `any` type
- Edit `*LogicType.ts` files
- Hardcode URLs (use `urls.ts`)
- Use direct dayjs imports (use `lib/dayjs`)
- Use Title Casing for UI text
- Ignore TypeScript errors
- Commit without running format/lint
- Use `disabled` without `disabledReason`

## Integration with Backend

### Backend Communication

- REST API via centralized API client (e.g., `lib/api.ts`)
- WebSocket: Optional (or use polling/server-sent events)
- Authentication: Session cookies, JWT, or OAuth tokens
- CSRF: Handled by backend framework (Django, Express, etc.)

### Static Assets

- Served by backend in production (or CDN)
- Dev server (Vite/webpack) in development
- Asset URL generation handled by build tool manifest

### Environment Variables

Accessed via `window.*` globals (injected by backend template) or `import.meta.env` (Vite):

```typescript
// Server-injected globals
window.APP_CONFIG
window.API_BASE_URL
window.FEATURE_FLAGS

// Or Vite/bundler environment variables
import.meta.env.VITE_API_URL
import.meta.env.VITE_APP_NAME
```

## Storybook

PostHog uses Storybook v7 for component development:

```bash
# Start Storybook
pnpm storybook

# Build static Storybook
pnpm build-storybook
```

Stories location: Co-located with components (`*.stories.tsx`)

## Accessibility

### Requirements

- All interactive elements keyboard accessible
- Proper ARIA labels
- Focus management in modals/dropdowns
- Color contrast meets WCAG AA
- Screen reader friendly

### Accessibility Testing

```typescript
import { axe, toHaveNoViolations } from 'jest-axe'

expect.extend(toHaveNoViolations)

const { container } = render(<MyComponent />)
const results = await axe(container)
expect(results).toHaveNoViolations()
```

## Additional Resources

- **Kea Docs**: <https://kea.js.org>
- **React Docs**: <https://react.dev>
- **TypeScript Handbook**: <https://www.typescriptlang.org/docs>
- **Tailwind CSS**: <https://tailwindcss.com/docs>
- **Radix UI**: <https://www.radix-ui.com/> (for accessible primitives)

## Questions & Support

Adapt these channels to your organization:

- **Code questions**: Engineering support channel
- **Design questions**: Design team channel
- **Bug reports**: Issue tracking system
- **Feature requests**: Product feedback channel

---

**Architecture Pattern**: Kea + React + TypeScript + Tailwind
**Last Updated**: November 2025
