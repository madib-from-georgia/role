import '@testing-library/jest-dom/vitest'
import { beforeAll, afterEach, afterAll, vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import { server } from './mocks/server'
import React from 'react'

// Mock CSS imports
vi.mock('*.css', () => ({}))
vi.mock('*.scss', () => ({}))
vi.mock('*.sass', () => ({}))
vi.mock('*.less', () => ({}))

// Mock @gravity-ui/uikit components
vi.mock('@gravity-ui/uikit', () => ({
  Label: vi.fn(({ children, ...props }) => React.createElement('div', { 'data-testid': 'label', ...props }, children)),
  Text: vi.fn(({ children, ...props }) => React.createElement('div', { 'data-testid': 'text', ...props }, children)),
  Button: vi.fn(({ children, onClick, ...props }) => 
    React.createElement('button', { 'data-testid': 'button', onClick, ...props }, children)
  ),
  Radio: vi.fn(({ content, checked, onChange, ...props }) => 
    React.createElement('label', { 'data-testid': 'radio', ...props }, [
      React.createElement('input', { 
        key: 'input',
        type: 'radio', 
        checked, 
        onChange,
        'aria-label': content
      }),
      content
    ])
  ),
  Checkbox: vi.fn(({ content, checked, onChange, ...props }) => 
    React.createElement('label', { 'data-testid': 'checkbox', ...props }, [
      React.createElement('input', { 
        key: 'input',
        type: 'checkbox', 
        checked, 
        onChange,
        'aria-label': content
      }),
      content
    ])
  ),
  TextInput: vi.fn(({ value, onUpdate, placeholder, onFocus, ...props }) => 
    React.createElement('input', {
      'data-testid': 'text-input',
      type: 'text',
      value,
      onChange: (e) => onUpdate?.(e.target.value),
      onFocus,
      placeholder,
      ...props
    })
  ),
  TextArea: vi.fn(({ value, onUpdate, onBlur, placeholder, ...props }) => 
    React.createElement('textarea', {
      'data-testid': 'textarea',
      value,
      onChange: (e) => onUpdate?.(e.target.value),
      onBlur,
      placeholder,
      ...props
    })
  ),
  SegmentedRadioGroup: vi.fn(({ value, onUpdate, options, ...props }) => 
    React.createElement('div', { 'data-testid': 'segmented-radio-group', ...props },
      options?.map((option) => 
        React.createElement('label', { key: option.value }, [
          React.createElement('input', {
            key: 'input',
            type: 'radio',
            value: option.value,
            checked: value === option.value,
            onChange: () => onUpdate?.(option.value),
            title: option.title
          }),
          option.content
        ])
      )
    )
  ),
  Breadcrumbs: Object.assign(
    vi.fn(({ children, ...props }) =>
      React.createElement('nav', { 'data-testid': 'breadcrumbs', ...props }, children)
    ),
    {
      Item: vi.fn(({ children, ...props }) =>
        React.createElement('span', { 'data-testid': 'breadcrumb-item', ...props }, children)
      )
    }
  ),
  Progress: vi.fn(({ value, theme, ...props }) =>
    React.createElement('div', {
      'data-testid': 'progress',
      'data-value': value,
      'data-theme': theme,
      ...props
    }, `${value}%`)
  ),
  ArrowToggle: vi.fn(({ direction, ...props }) =>
    React.createElement('span', {
      'data-testid': 'arrow-toggle',
      'data-direction': direction,
      ...props
    }, direction === 'bottom' ? '▼' : '▶')
  )
}))

// Mock NavigationSidebar component
vi.mock('../../components/checklists/NavigationSidebar', () => ({
  NavigationSidebar: vi.fn(({ isOpen, onClose, ...props }) => 
    isOpen ? React.createElement('div', { 'data-testid': 'navigation-sidebar', ...props }, 'Navigation Sidebar') : null
  )
}))

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  disconnect: vi.fn(),
  unobserve: vi.fn(),
  root: null,
  rootMargin: '',
  thresholds: [],
  takeRecords: vi.fn(() => []),
}))

// Mock ResizeObserver
global.ResizeObserver = vi.fn(() => ({
  observe: vi.fn(),
  disconnect: vi.fn(),
  unobserve: vi.fn(),
}))

// Mock scrollTo
Object.defineProperty(window, 'scrollTo', { value: vi.fn(), writable: true })

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
}
global.localStorage = localStorageMock as Storage

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
}
global.sessionStorage = sessionStorageMock as Storage

// Establish API mocking before all tests
beforeAll(() => server.listen())

// Reset any request handlers that we may add during the tests,
// so they don't affect other tests
afterEach(() => {
  cleanup()
  server.resetHandlers()
  vi.clearAllMocks()
})

// Clean up after the tests are finished
afterAll(() => server.close())