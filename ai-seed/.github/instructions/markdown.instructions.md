---
file: markdown.instructions.md
description: Comprehensive Markdown writing standards and best practices for technical documentation
applyTo: "**/*.md,**/*.mdx"
author: "AI-Seed Team <team@ai-seed.org>"
created: "2025-07-19"
lastModified: "2025-07-19"
version: "1.0.0"

relatedIssues:
  - "N/A"

relatedEvolutions:
  - "N/A"

dependencies:
  - file: space.instructions.md
    description: Foundation principles and path-based development
  - file: docs.instructions.md
    description: Documentation standards and automation
  - file: project.instructions.md
    description: Project-specific context and requirements

containerRequirements:
  baseImage: node:18-alpine
  description: for documentation tools
  exposedPorts:
    - 3000
    - 4000
    - 8000
  portDescription: documentation servers
  volumes:
    - "/docs:rw"
    - "/content:rw"
    - "/output:rw"
  environment:
    NODE_ENV: development
    DOCS_ENV: development
  resources:
    cpu: "0.5-2.0"
    memory: "512MiB-2GiB"
  healthCheck: "/health endpoint on documentation server"

paths:
  content_creation_path:
    - planning
    - writing
    - review
    - formatting
    - publication
  markdown_processing_path:
    - raw_markdown
    - parsing
    - rendering
    - optimization
  documentation_workflow_path:
    - draft
    - review
    - approval
    - publication
    - maintenance

changelog:
  - date: "2025-07-19"
    description: "Initial creation"
    author: "AI-Seed Team"

usage: "Reference for all Markdown writing, formatting, and documentation tool integration"
notes: "Emphasizes semantic markup, accessibility, and cross-platform compatibility"
---

# Markdown Instructions

These instructions provide comprehensive guidance for writing high-quality Markdown documentation that follows industry best practices, ensures accessibility, and integrates seamlessly with popular documentation tools and static site generators.

## Markdown Philosophy and Standards

### Semantic Markup Principles

Markdown should be written with semantic meaning, not just visual appearance. This ensures compatibility across different renderers, accessibility tools, and future format migrations.

#### Core Semantic Principles
- **Structure over Style**: Use heading levels to indicate document hierarchy, not visual size
- **Meaning over Appearance**: Choose elements based on semantic meaning, not visual output
- **Accessibility First**: Write for screen readers and assistive technologies
- **Platform Agnostic**: Ensure compatibility across different Markdown processors
- **Future-Proof**: Use standard syntax that will remain valid as tools evolve

### Markdown Flavor Compatibility

Write Markdown that works across multiple processors while leveraging enhanced features when appropriate.

#### Compatibility Matrix
```yaml
# YAML representation of feature compatibility
markdown_features:
  tables:
    CommonMark: false
    GitHub: true
    GitLab: true
    Jekyll: true
    MkDocs: true
    Docusaurus: true
  
  task_lists:
    CommonMark: false
    GitHub: true
    GitLab: true
    Jekyll: true
    MkDocs: true
    Docusaurus: true
  
  strikethrough:
    CommonMark: false
    GitHub: true
    GitLab: true
    Jekyll: true
    MkDocs: true
    Docusaurus: true
  
  footnotes:
    CommonMark: false
    GitHub: false
    GitLab: true
    Jekyll: true
    MkDocs: true
    Docusaurus: true
  
  definition_lists:
    CommonMark: false
    GitHub: false
    GitLab: false
    Jekyll: true
    MkDocs: true
    Docusaurus: false
  
  math_expressions:
    CommonMark: false
    GitHub: true
    GitLab: true
    Jekyll: true
    MkDocs: true
    Docusaurus: true
  
  mermaid_diagrams:
    CommonMark: false
    GitHub: true
    GitLab: true
    Jekyll: true
    MkDocs: true
    Docusaurus: true
```

```markdown
| Feature | CommonMark | GitHub | GitLab | Jekyll | MkDocs | Docusaurus |
|---------|------------|--------|--------|--------|--------|------------|
| Tables | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Task Lists | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Strikethrough | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Footnotes | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Definition Lists | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| Math Expressions | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Mermaid Diagrams | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
```

## Document Structure and Organization

### File Naming Conventions

#### Standard Naming Patterns
```
# Documentation files
README.md                    # Project overview and quick start
CONTRIBUTING.md             # Contribution guidelines
CHANGELOG.md                # Version history and changes
LICENSE.md                  # License information
CODE_OF_CONDUCT.md          # Community guidelines

# Guide files (lowercase with hyphens)
getting-started.md          # Initial setup and first steps
installation-guide.md       # Detailed installation instructions
user-manual.md             # Comprehensive user documentation
api-reference.md            # API documentation
troubleshooting.md          # Common issues and solutions

# Dated content (ISO 8601 format)
2025-07-19-release-notes.md # Release announcements
2025-07-19-tutorial-name.md # Tutorials and blog posts

# Numbered sequences
01-introduction.md          # Sequential content
02-setup.md                 # Ordered learning materials
03-advanced-topics.md       # Progressive disclosure

# Language-specific files
README.fr.md                # French translation
installation-guide.es.md    # Spanish installation guide
```

### Frontmatter Standards

#### Universal Frontmatter Template
```yaml
---
title: "Document Title: Clear and Descriptive"
description: "Brief description for search engines and social media (150-160 characters)"
author: "Author Name"
contributors:
  - "Contributor 1"
  - "Contributor 2"
created: "2025-07-19"
lastModified: "2025-07-19"
version: "1.0.0"
status: "draft"  # Options: draft|review|published|archived
tags:
  - "tag1"
  - "tag2"
  - "tag3"
categories:
  - "Category 1"
  - "Category 2"
difficulty: "beginner"  # Options: beginner|intermediate|advanced
estimatedTime: "15 minutes"
prerequisites:
  - "Basic knowledge of X"
  - "Completion of Y tutorial"
relatedDocs:
  - title: "Related Document 1"
    url: "./related-doc-1.md"
  - title: "Related Document 2"
    url: "./related-doc-2.md"
language: "en"
slug: "url-friendly-slug"
canonical: "https://example.com/canonical-url"
robots: "index,follow"
sitemap:
  priority: 0.8
  changefreq: "monthly"
---
```

#### Tool-Specific Frontmatter Extensions

**Jekyll/GitHub Pages**
```yaml
---
layout: default
permalink: /custom-url/
redirect_from:
  - /old-url/
  - /another-old-url/
excerpt: "Custom excerpt for post listings"
header:
  image: /assets/images/header.jpg
  teaser: /assets/images/teaser.jpg
sidebar:
  nav: "docs"
toc: true
toc_label: "Contents"
toc_icon: "list"
---
```

**MkDocs**
```yaml
---
template: custom-template.html
hide:
  - navigation
  - toc
icon: material/book
---
```

**Docusaurus**
```yaml
---
id: unique-id
sidebar_label: "Short Label"
sidebar_position: 2
hide_title: false
hide_table_of_contents: false
custom_edit_url: https://github.com/user/repo/edit/main/docs/file.md
keywords:
  - keyword1
  - keyword2
  - keyword3
image: /img/social-card.png
---
```

**GitBook**
```yaml
---
cover: .gitbook/assets/cover.png
coverY: 0
layout: editorial
---
```

## Content Structure and Hierarchy

### Heading Structure Best Practices

#### Semantic Heading Hierarchy
```markdown
# Document Title (H1 - Only one per document)

Brief introduction paragraph that explains the document's purpose and scope.

## Main Section (H2 - Primary sections)

### Subsection (H3 - Secondary topics)

#### Sub-subsection (H4 - Detailed topics)

##### Minor subsection (H5 - Use sparingly)

###### Rarely used (H6 - Avoid if possible)
```

#### Heading Guidelines
- **One H1 per document**: Use for the main title only
- **Sequential hierarchy**: Don't skip heading levels (H2 → H4 is incorrect)
- **Descriptive titles**: Make headings scannable and meaningful
- **Consistent style**: Use parallel structure in heading groups
- **Avoid deep nesting**: Limit to H4 in most cases

### Table of Contents Patterns

#### Manual TOC (Universal Compatibility)
```markdown
## Table of Contents

- [Introduction](#introduction)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Basic Examples](#basic-examples)
  - [Advanced Features](#advanced-features)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
```

#### Auto-Generated TOC Markers
```markdown
<!-- TOC -->
<!-- This comment will be replaced with auto-generated TOC -->
<!-- /TOC -->

<!-- For tools that support it -->
{:toc}

<!-- Docusaurus -->
import TOCInline from '@theme/TOCInline';

<TOCInline toc={toc} />
```

## Text Formatting and Style Guide

### Emphasis and Strong Text

#### Proper Usage Patterns
```markdown
Use *emphasis* (italics) for:
- New terms when first introduced
- Book titles, movie titles, publication names
- Variable names in technical writing
- Foreign words and phrases

Use **strong** (bold) for:
- Important warnings or critical information
- UI elements (buttons, menu items, field names)
- Keywords in definitions
- Section introductions and key concepts

Use ***both emphasis and strong*** very sparingly for:
- Critical warnings
- Emergency information
- Absolutely essential points

Avoid using ~~strikethrough~~ except for:
- Showing deletions in change logs
- Crossing out deprecated information
- Demonstrating text editing concepts
```

### Code and Technical Content

#### Inline Code Guidelines
```markdown
Use `inline code` for:
- Variable names: `userName`, `apiKey`
- Function names: `getData()`, `processResults()`
- File names: `config.json`, `README.md`
- Command names: `git commit`, `npm install`
- Short code snippets: `const result = api.getData()`
- Technical terms: `HTTP`, `REST`, `JSON`
- Keyboard shortcuts: `Ctrl+C`, `Cmd+V`
- Menu paths: `File > Save As`
```

#### Code Block Best Practices
```markdown
# Always specify language for syntax highlighting
```javascript
function greetUser(name) {
    return `Hello, ${name}!`;
}
```

# Include comments for complex code
```python
# Calculate the factorial of a number
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

# Show command-line examples with prompts
```bash
$ npm install
$ npm run build
$ npm test
```

# Include expected output when helpful
```console
$ ls -la
total 24
drwxr-xr-x  6 user staff  192 Jul 19 10:30 .
drwxr-xr-x  3 user staff   96 Jul 19 10:29 ..
-rw-r--r--  1 user staff  123 Jul 19 10:30 README.md
```

# Use diff format for showing changes
```diff
- const oldValue = 'deprecated';
+ const newValue = 'updated';
  const unchangedValue = 'same';
```
```

### Lists and Organization

#### Unordered Lists
```markdown
Use unordered lists for:
- Items without specific order
- Feature lists
- Requirements or prerequisites
- Options or alternatives

Guidelines:
- Use consistent marker style (-, *, or +)
- Maintain parallel structure
- Keep items concise
- Use sub-lists sparingly
```

#### Ordered Lists
```markdown
Use ordered lists for:
1. Step-by-step instructions
2. Prioritized items
3. Sequential processes
4. Ranked recommendations

Guidelines:
1. Start with meaningful numbers (usually 1)
2. Use consistent numbering style
3. Break long procedures into sections
4. Include verification steps when appropriate
```

#### Task Lists (GitHub-Flavored Markdown)
```markdown
Project checklist:
- [x] Complete documentation
- [x] Write unit tests
- [ ] Implement feature X
- [ ] Review and merge PR
- [ ] Deploy to staging
- [ ] Conduct user testing

Guidelines:
- Use for tracking progress
- Ideal for project management
- Keep items actionable
- Update regularly
```

#### Definition Lists (Extended Markdown)
```markdown
API
: Application Programming Interface - a set of protocols and tools for building software applications

REST
: Representational State Transfer - an architectural style for distributed hypermedia systems

JSON
: JavaScript Object Notation - a lightweight data interchange format
```

## Tables and Data Presentation

### Table Structure and Formatting

#### Basic Table Syntax
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Row 1    | Data     | Values   |
| Row 2    | More     | Content  |
| Row 3    | Final    | Row      |
```

#### Enhanced Table Features
```markdown
| Feature | Supported | Notes |
|:--------|:---------:|:------|
| Left Aligned | ✅ | Default alignment |
| Center Aligned | ✅ | Use :---: |
| Right Aligned | ✅ | Use ---: |
| **Bold text** | ✅ | Formatting works |
| `Code snippets` | ✅ | Inline code works |
| [Links](url) | ✅ | Links are supported |
```

#### Complex Table Guidelines
```markdown
# For complex tables, consider alternatives:

## Option 1: Break into multiple tables
### User Permissions
| Role | Read | Write | Delete |
|------|------|-------|--------|
| Admin | ✅ | ✅ | ✅ |
| User | ✅ | ❌ | ❌ |

### System Permissions  
| Role | Config | Logs | Backup |
|------|--------|------|--------|
| Admin | ✅ | ✅ | ✅ |
| User | ❌ | ✅ | ❌ |

## Option 2: Use HTML for complex layouts
<table>
  <thead>
    <tr>
      <th rowspan="2">Feature</th>
      <th colspan="2">Browser Support</th>
    </tr>
    <tr>
      <th>Chrome</th>
      <th>Firefox</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>WebGL</td>
      <td>✅</td>
      <td>✅</td>
    </tr>
  </tbody>
</table>
```

## Links and References

### Link Types and Best Practices

#### Internal Links
```markdown
# Relative links (preferred for internal content)
[Getting Started](./getting-started.md)
[API Reference](../api/reference.md)
[Section Link](#section-heading)

# Absolute links (for external sites)
[GitHub](https://github.com)
[Documentation](https://docs.example.com)

# Reference-style links (for repeated URLs)
This is [example][1] of [reference][1] style links.

[1]: https://example.com "Example Website"
```

#### Link Accessibility
```markdown
# Good: Descriptive link text
[Download the installation guide](./install.md)
[View the API documentation](./api.md)

# Bad: Generic link text
[Click here](./install.md) for installation
[Read more](./api.md) about the API

# Include context for external links
[GitHub repository](https://github.com/user/repo) (external link)
[Download PDF](./file.pdf) (PDF, 2.3 MB)
```

#### Link Validation
```markdown
# Use meaningful anchor text
[Configuration Options](#configuration-options)

# Ensure heading compatibility
## Configuration Options  <!-- Works -->
## Configuration & Setup  <!-- Becomes #configuration--setup -->
## FAQ's and Tips        <!-- Becomes #faqs-and-tips -->
```

## Images and Media

### Image Standards and Optimization

#### Image Syntax and Attributes
```markdown
# Basic image syntax
![Alt text](./images/example.png)

# With title attribute
![Alt text](./images/example.png "Image title")

# Reference-style images
![Alt text][image-ref]

[image-ref]: ./images/example.png "Image title"

# HTML for advanced features
<img src="./images/example.png" 
     alt="Descriptive alt text" 
     title="Image title"
     width="600" 
     height="400" 
     loading="lazy" />
```

#### Accessibility Guidelines
```markdown
# Write meaningful alt text
![Screenshot showing the user dashboard with navigation menu on the left and main content area displaying recent activity](./images/dashboard-screenshot.png)

# For decorative images, use empty alt text
![](./images/decorative-border.png)

# For complex images, provide detailed descriptions
![Chart showing quarterly revenue growth](./images/revenue-chart.png)

**Chart Description**: The bar chart displays quarterly revenue growth from Q1 2024 to Q4 2024. Q1 shows $1.2M, Q2 shows $1.5M, Q3 shows $1.8M, and Q4 shows $2.1M, representing consistent growth throughout the year.
```

#### Image Organization
```markdown
# File naming conventions
images/
├── screenshots/
│   ├── 01-login-screen.png
│   ├── 02-dashboard-overview.png
│   └── 03-settings-panel.png
├── diagrams/
│   ├── architecture-overview.svg
│   └── data-flow-diagram.svg
├── icons/
│   ├── warning-icon.svg
│   └── success-icon.svg
└── assets/
    ├── logo.png
    └── banner.jpg

# Recommended formats and sizes
- Screenshots: PNG format, max 1200px width
- Diagrams: SVG format (vector graphics)
- Photos: JPEG format, optimized for web
- Icons: SVG format, 24x24 or 32x32 for inline use
```

### Diagrams and Visual Content

#### Mermaid Diagrams
```mermaid
# Flowchart example
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E

# Sequence diagram example
sequenceDiagram
    participant User
    participant App
    participant API
    participant DB
    
    User->>App: Login request
    App->>API: Authenticate
    API->>DB: Verify credentials
    DB-->>API: User data
    API-->>App: Auth token
    App-->>User: Login success

# Class diagram example
classDiagram
    class User {
        +String name
        +String email
        +login()
        +logout()
    }
    
    class Admin {
        +manageUsers()
        +systemConfig()
    }
    
    User <|-- Admin
```

#### ASCII Diagrams
```markdown
# Simple diagrams using ASCII art
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│   Server    │───▶│  Database   │
│             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

# File structure representation
```
project/
├── src/
│   ├── components/
│   │   ├── Header.js
│   │   └── Footer.js
│   └── utils/
│       └── helpers.js
├── tests/
│   └── unit/
└── docs/
    └── README.md
```
```

## Mathematical Expressions

### LaTeX Math Support

#### Inline Math
```markdown
The quadratic formula is $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$ where $a \neq 0$.

Einstein's mass-energy equivalence is expressed as $E = mc^2$.
```

#### Block Math
```markdown
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$

$$
\begin{align}
f(x) &= ax^2 + bx + c \\
f'(x) &= 2ax + b \\
f''(x) &= 2a
\end{align}
$$
```

#### Math Accessibility
```markdown
# Provide text descriptions for complex equations
The following equation represents the quadratic formula:

$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

**Description**: x equals negative b plus or minus the square root of b squared minus 4ac, all divided by 2a.
```

## Admonitions and Callouts

### Standard Admonition Types

#### Universal Patterns (HTML-based)
```html
<!-- Note -->
<div class="note">
<strong>Note:</strong> This is important information that readers should be aware of.
</div>

<!-- Warning -->
<div class="warning">
<strong>⚠️ Warning:</strong> This action cannot be undone.
</div>

<!-- Tip -->
<div class="tip">
<strong>💡 Tip:</strong> Here's a helpful suggestion to improve your workflow.
</div>

<!-- Danger -->
<div class="danger">
<strong>🚨 Danger:</strong> This could cause data loss or system damage.
</div>
```

#### Tool-Specific Admonitions

**MkDocs Material**
```markdown
!!! note "Custom Title"
    This is a note admonition with a custom title.

!!! warning
    This is a warning without a custom title.

!!! tip "Pro Tip"
    Use keyboard shortcuts to work faster!

??? info "Collapsible Section"
    This content is initially collapsed.

???+ example "Expanded by Default"
    This collapsible section starts expanded.
```

**Docusaurus**
```markdown
:::note
This is a note
:::

:::tip My Tip
Use this amazing feature!
:::

:::warning
Be careful with this setting
:::

:::danger Take care
This is extremely dangerous
:::

:::info Custom Title
Some **content** with _formatting_.
:::
```

**GitBook**
```markdown
{% hint style="info" %}
This is an info hint
{% endhint %}

{% hint style="warning" %}
This is a warning hint  
{% endhint %}

{% hint style="danger" %}
This is a danger hint
{% endhint %}

{% hint style="success" %}
This is a success hint
{% endhint %}
```

## Code Documentation Patterns

### API Documentation

#### Endpoint Documentation
```markdown
## POST /api/users

Creates a new user account.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | User's full name |
| `email` | string | Yes | Valid email address |
| `password` | string | Yes | Minimum 8 characters |
| `role` | string | No | User role (default: 'user') |

### Request Example

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securePassword123",
  "role": "admin"
}
```

### Response Examples

#### Success (201 Created)
```json
{
  "id": "user_123",
  "name": "John Doe",
  "email": "john@example.com",
  "role": "admin",
  "createdAt": "2025-07-19T10:30:00Z"
}
```

#### Error (400 Bad Request)
```json
{
  "error": "validation_failed",
  "message": "Invalid email format",
  "details": {
    "field": "email",
    "code": "INVALID_FORMAT"
  }
}
```

### cURL Examples
```bash
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securePassword123"
  }'
```
```

#### Function Documentation
```markdown
## `calculateDistance(point1, point2)`

Calculates the Euclidean distance between two points.

### Parameters

- **point1** `{x: number, y: number}` - First point coordinates
- **point2** `{x: number, y: number}` - Second point coordinates

### Returns

`number` - The distance between the two points

### Example

```javascript
const pointA = { x: 0, y: 0 };
const pointB = { x: 3, y: 4 };
const distance = calculateDistance(pointA, pointB);
console.log(distance); // Output: 5
```

### Notes

- Uses the standard Euclidean distance formula: √[(x₂-x₁)² + (y₂-y₁)²]
- Returns 0 if both points are identical
- Handles negative coordinates correctly
```

## Internationalization and Localization

### Multi-Language Documentation

#### Language-Specific Files
```markdown
# File structure for multi-language docs
docs/
├── en/
│   ├── README.md
│   ├── getting-started.md
│   └── api-reference.md
├── es/
│   ├── README.md
│   ├── primeros-pasos.md
│   └── referencia-api.md
├── fr/
│   ├── README.md
│   ├── guide-demarrage.md
│   └── reference-api.md
└── de/
    ├── README.md
    ├── erste-schritte.md
    └── api-referenz.md
```

#### Language Switcher Links
```markdown
# Language switcher in navigation
**Languages**: [English](./README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Deutsch](../de/README.md)

# Or as a table
| Language | File |
|----------|------|
| 🇺🇸 English | [README.md](./README.md) |
| 🇪🇸 Español | [README.md](../es/README.md) |
| 🇫🇷 Français | [README.md](../fr/README.md) |
| 🇩🇪 Deutsch | [README.md](../de/README.md) |
```

#### Cultural Considerations
```markdown
# Date formats
- US: MM/DD/YYYY (07/19/2025)
- EU: DD/MM/YYYY (19/07/2025)  
- ISO: YYYY-MM-DD (2025-07-19) ← Recommended

# Number formats
- US: 1,234.56
- EU: 1.234,56
- International: 1 234.56

# Currency
- Include currency codes: $100 USD, €85 EUR, £75 GBP
- Consider local payment methods
```

## SEO and Metadata

### Search Engine Optimization

#### Title and Description Optimization
```yaml
---
title: "Complete Guide to Markdown Documentation - Best Practices 2025"
description: "Learn professional Markdown writing techniques, tool integration, and accessibility standards for technical documentation. Includes examples for Jekyll, MkDocs, and Docusaurus."
keywords:
  - "markdown"
  - "documentation"
  - "technical writing"
  - "jekyll"
  - "mkdocs"
---
```

# Search-Friendly Content Guidelines

## Use Semantic Headings
- H1: Main topic (only one per page)
- H2: Major sections (primary keywords)
- H3: Subsections (secondary keywords)
- H4+: Detailed topics (long-tail keywords)

## Include Target Keywords Naturally
Write content for humans first, search engines second:
- Use keywords in headings
- Include synonyms and related terms
- Maintain natural reading flow
- Avoid keyword stuffing
```

#### Schema Markup for Technical Documentation
```html
<!-- JSON-LD structured data -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "Markdown Documentation Best Practices",
  "author": {
    "@type": "Person",
    "name": "AI-Seed Team"
  },
  "datePublished": "2025-07-19",
  "dateModified": "2025-07-19",
  "description": "Comprehensive guide to writing technical documentation in Markdown",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://example.com/markdown-guide"
  }
}
</script>
```

## Accessibility and Inclusive Design

### Screen Reader Compatibility

#### Accessible Heading Structure
```markdown
# Main Document Title (H1)

Brief introduction explaining what this document covers.

## Primary Section (H2)

Content for the first major section.

### Subsection (H3)

More detailed information within the primary section.

### Another Subsection (H3)

Additional details at the same level.

## Second Primary Section (H2)

Starting a new major topic.
```

#### Alternative Text for Images
```markdown
# Descriptive alt text for functional images
![Screenshot of the login form showing username and password fields with a blue "Sign In" button](./images/login-form.png)

# Context-appropriate descriptions
![Bar chart displaying quarterly sales data from Q1 to Q4 2024, showing steady growth from $1.2M to $2.1M](./images/sales-chart.png)

# Empty alt for decorative images
![](./images/decorative-divider.png)
```

#### Accessible Tables
```markdown
| Feature | Support Level | Notes |
|---------|---------------|-------|
| Screen Readers | Full | Works with NVDA, JAWS, VoiceOver |
| Keyboard Navigation | Full | Tab through all interactive elements |
| High Contrast | Partial | Some themes may need adjustment |
| Font Scaling | Full | Responsive at 200% zoom |
```

#### Inclusive Language Guidelines
```markdown
# Use inclusive terminology

## Preferred Language
- Use "people with disabilities" not "disabled people"
- Use "they/them" for unknown pronouns
- Use "click" instead of "see" for links
- Use "navigate to" instead of "go to"

## Technical Writing
- Explain acronyms: API (Application Programming Interface)
- Define technical terms when first used
- Use active voice when possible
- Keep sentences concise and clear

## Avoid These Terms
- ❌ "Simply" or "just" (minimizes difficulty)
- ❌ "Obviously" or "clearly" (assumes knowledge)
- ❌ "Easy" or "straightforward" (subjective)
- ✅ Use specific, objective language instead
```

## Tool Integration and Automation

### Static Site Generators

#### Jekyll Configuration
```yaml
# _config.yml
markdown: kramdown
highlighter: rouge
kramdown:
  input: GFM
  syntax_highlighter: rouge
  syntax_highlighter_opts:
    block:
      line_numbers: true

plugins:
  - jekyll-feed
  - jekyll-sitemap
  - jekyll-seo-tag
  - jekyll-toc
```

#### MkDocs Configuration
```yaml
# mkdocs.yml
site_name: Documentation
theme:
  name: material
  features:
    - navigation.sections
    - navigation.top
    - search.highlight
    - content.code.copy

markdown_extensions:
  - toc:
      permalink: true
  - admonition
  - pymdownx.details
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.tasklist:
      custom_checkbox: true

plugins:
  - search
  - git-revision-date-localized
```

#### Docusaurus Configuration
```yaml
# docusaurus.config.js (as YAML comments for configuration reference)
# title: 'Documentation'
# tagline: 'Comprehensive project documentation'
# url: 'https://docs.example.com'
# baseUrl: '/'
# 
# presets:
#   - name: 'classic'
#     config:
#       docs:
#         sidebarPath: './sidebars.js'
#         editUrl: 'https://github.com/user/repo/tree/main/'
#         showLastUpdateTime: true
#         showLastUpdateAuthor: true
#       theme:
#         customCss: './src/css/custom.css'
# 
# themeConfig:
#   navbar:
#     title: 'Docs'
#     items:
#       - type: 'doc'
#         docId: 'intro'
#         position: 'left'
#         label: 'Tutorial'
#       - href: 'https://github.com/user/repo'
#         label: 'GitHub'
#         position: 'right'
```

```javascript
// docusaurus.config.js
module.exports = {
  title: 'Documentation',
  tagline: 'Comprehensive project documentation',
  url: 'https://docs.example.com',
  baseUrl: '/',
  
  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/user/repo/tree/main/',
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
  
  themeConfig: {
    navbar: {
      title: 'Docs',
      items: [
        {
          type: 'doc',
          docId: 'intro',
          position: 'left',
          label: 'Tutorial',
        },
        {
          href: 'https://github.com/user/repo',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
  },
};
```

### Automated Quality Checks

#### Markdown Linting Configuration
```yaml
# .markdownlint.yml
default: true
line-length:
  line_length: 100
  code_blocks: false
  tables: false
  headings: false
no-duplicate-heading:
  siblings_only: true
no-inline-html:
  allowed_elements:
    - 'br'
    - 'sub'
    - 'sup'
    - 'kbd'
    - 'mark'
```

#### Vale Style Guide
```yaml
# .vale.ini
StylesPath: styles
MinAlertLevel: suggestion

[*.md]:
  BasedOnStyles:
    - Vale
    - Microsoft
  Microsoft.Contractions: NO
  Vale.Spelling: YES
```

#### GitHub Actions Workflow
```yaml
# .github/workflows/docs-quality.yml
name: Documentation Quality Check

on:
  pull_request:
    paths:
      - 'docs/**'
      - '*.md'

jobs:
  markdown-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Lint Markdown files
        uses: articulate/actions-markdownlint@v1
        
  link-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check links
        uses: gaurav-nelson/github-action-markdown-link-check@v1
        
  spell-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check spelling
        uses: streetsidesoftware/cspell-action@v2
```

## Performance and Optimization

### Image Optimization

#### Responsive Images
```html
<!-- Multiple sizes for different devices -->
<picture>
  <source media="(max-width: 768px)" srcset="./images/mobile-screenshot.png">
  <source media="(max-width: 1200px)" srcset="./images/tablet-screenshot.png">
  <img src="./images/desktop-screenshot.png" 
       alt="Application dashboard interface" 
       loading="lazy">
</picture>

<!-- WebP with fallback -->
<picture>
  <source srcset="./images/diagram.webp" type="image/webp">
  <source srcset="./images/diagram.png" type="image/png">
  <img src="./images/diagram.png" alt="System architecture diagram">
</picture>
```

#### Image Compression Guidelines
```markdown
# Recommended compression settings

## Screenshots (PNG)
- Use PNG for screenshots with text
- Compress with tools like TinyPNG
- Target: < 500KB per image
- Max width: 1200px

## Photographs (JPEG)
- Use JPEG for photos and complex images
- Quality: 80-85% for web
- Target: < 300KB per image

## Diagrams (SVG)
- Use SVG for logos and diagrams
- Optimize with SVGO
- Inline small SVGs (< 2KB)
- External files for larger graphics

## Modern Formats
- WebP: 25-35% smaller than JPEG
- AVIF: 50% smaller than JPEG (newer)
- Provide fallbacks for compatibility
```

### Content Delivery Optimization

#### Asset Organization
```markdown
# Efficient asset structure
assets/
├── images/
│   ├── optimized/          # Compressed versions
│   ├── originals/          # Source files (not served)
│   └── thumbnails/         # Small preview images
├── videos/
│   ├── compressed/         # Web-optimized videos
│   └── captions/           # Subtitle files
└── downloads/
    ├── pdfs/               # Documentation PDFs
    └── archives/           # Downloadable packages
```

#### CDN Integration
```markdown
# Using CDN for assets
![Diagram](https://cdn.example.com/docs/images/architecture.svg)

# Local fallback
<img src="https://cdn.example.com/docs/images/screenshot.webp" 
     onerror="this.src='./images/screenshot.png'"
     alt="Application interface">
```

## Version Control and Collaboration

### Git Workflow for Documentation

#### Commit Message Standards
```bash
# Use conventional commit format
docs: add markdown style guide
docs(api): update endpoint documentation
fix(docs): correct broken internal links
feat(docs): add multi-language support
```

#### Branch Strategy
```bash
# Documentation branches
main                    # Production documentation
develop                # Development documentation
docs/feature-name       # Feature-specific documentation
docs/translation-es     # Translation branches
hotfix/docs-typo       # Quick fixes
```

#### Review Checklist
```markdown
# Documentation Review Checklist

## Content Quality
- [ ] Information is accurate and up-to-date
- [ ] Writing is clear and concise
- [ ] Examples work as demonstrated
- [ ] Links are functional and relevant

## Structure and Format
- [ ] Proper heading hierarchy (H1 → H2 → H3)
- [ ] Consistent formatting throughout
- [ ] Table of contents is updated
- [ ] Code blocks have language specification

## Accessibility
- [ ] Images have meaningful alt text
- [ ] Headings create logical document structure
- [ ] Tables have proper headers
- [ ] Content is readable without images

## Technical Validation
- [ ] All code examples are tested
- [ ] API documentation matches implementation
- [ ] Installation instructions work on target platforms
- [ ] External links are accessible

## SEO and Metadata
- [ ] Page title is descriptive and unique
- [ ] Meta description summarizes content
- [ ] Keywords are included naturally
- [ ] Canonical URL is set if needed
```

### Collaborative Writing

#### Documentation Templates
```markdown
# Feature Documentation Template

## Overview
Brief description of the feature and its purpose.

## Prerequisites
- Requirement 1
- Requirement 2

## Step-by-Step Guide

### Step 1: Initial Setup
Detailed instructions for the first step.

```bash
# Example command
command --with-options
```

### Step 2: Configuration
Instructions for configuration.

## Examples

### Basic Example
Simple usage example with explanation.

### Advanced Example
Complex scenario with detailed walkthrough.

## Troubleshooting

### Common Issue 1
**Problem**: Description of the issue
**Solution**: How to resolve it

### Common Issue 2
**Problem**: Another common problem
**Solution**: Resolution steps

## Related Resources
- [Related Feature 1](./related-feature-1.md)
- [API Reference](./api-reference.md)
- [External Documentation](https://external-docs.example.com)
```

#### Style Guide Enforcement
```markdown
# Team Style Guide

## Writing Style
- Use active voice when possible
- Write in second person ("you") for instructions
- Use present tense for current features
- Keep sentences under 25 words

## Formatting Conventions
- Use `code formatting` for UI elements
- Use **bold** for important concepts
- Use *italics* for emphasis and new terms
- Use numbered lists for procedures

## Terminology
- API (not Api or api)
- JavaScript (not Javascript)
- Markdown (not markdown)
- GitHub (not Github)

## File Organization
- Use lowercase with hyphens for file names
- Group related content in subdirectories
- Include README.md in each directory
- Maintain consistent navigation structure
```

## Integration with Other Instructions

This Markdown instruction file works in conjunction with:
- **space.instructions.md**: Foundational path-based principles and container-first development
- **docs.instructions.md**: Documentation standards, automation, and AI-assisted content generation
- **project.instructions.md**: AI-seed specific requirements and documentation structure
- **ci-cd.instructions.md**: Automated documentation deployment and quality checks

### YAML Configuration Examples

#### Path-Based Documentation Configuration
```yaml
# docs-config.yml
documentation:
  paths:
    content_creation:
      - planning
      - writing
      - review
      - formatting
      - publication
    processing:
      - raw_markdown
      - parsing
      - rendering
      - optimization
    workflow:
      - draft
      - review
      - approval
      - publication
      - maintenance

  standards:
    format: "markdown"
    accessibility: true
    seo_optimized: true
    multi_language: true
    
  tools:
    static_generators:
      - name: "jekyll"
        config_file: "_config.yml"
        features:
          - liquid_templating
          - github_pages
      - name: "mkdocs"
        config_file: "mkdocs.yml"
        features:
          - material_theme
          - search_integration
      - name: "docusaurus"
        config_file: "docusaurus.config.js"
        features:
          - react_components
          - versioning
```

#### Quality Assurance Configuration
```yaml
# quality-config.yml
quality_checks:
  markdown_lint:
    enabled: true
    rules:
      line_length: 100
      heading_style: "atx"
      no_duplicate_headings: true
    
  link_validation:
    enabled: true
    check_external: true
    timeout: 30
    
  spell_check:
    enabled: true
    dictionaries:
      - "en_US"
      - "technical_terms"
    
  accessibility:
    alt_text_required: true
    heading_structure: true
    color_contrast: true
    
  seo:
    meta_description: true
    title_optimization: true
    keyword_density: true
```

## Future Evolution

### Advanced Markdown Features
- **Interactive Documentation**: Executable code blocks and live demonstrations
- **AI-Powered Content Enhancement**: Automated grammar checking, style improvements, and content suggestions
- **Real-Time Collaboration**: Live editing capabilities with conflict resolution
- **Adaptive Content**: Personalized documentation based on user expertise and preferences
- **Automated Translation**: AI-powered translation with human review workflows
- **Analytics Integration**: Content performance metrics and user engagement tracking
