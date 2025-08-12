import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { render } from '../../utils/test-utils'
import { QuestionCard } from '../../../components/checklists/QuestionCard'
import { createMockQuestion } from '../../utils/mock-data'

describe('QuestionCard', () => {
  const mockOnAnswerUpdate = vi.fn()
  const mockOnAnswerDelete = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllTimers()
  })

  describe('Basic rendering', () => {
    it('should render question not found when no question provided', () => {
      render(
        <QuestionCard
          question={null as any}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={false}
          allQuestions={[]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      expect(screen.getByText('Вопрос не найден')).toBeInTheDocument()
    })

    it('should render open text question', () => {
      const question = createMockQuestion({
        text: 'Опишите внешность персонажа',
        type: 'OPEN_TEXT',
        sectionTitle: 'Физический портрет',
        subsectionTitle: 'Основные черты'
      })

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      expect(screen.getByText('Опишите внешность персонажа')).toBeInTheDocument()
      expect(screen.getByText('Физический портрет')).toBeInTheDocument()
      expect(screen.getByText('Основные черты')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Введите ваш ответ...')).toBeInTheDocument()
    })

    it('should render single choice question with options', () => {
      const question = createMockQuestion({
        text: 'Выберите возраст персонажа',
        type: 'SINGLE_CHOICE',
        options: ['18-25', '26-35', '36-45', '45+']
      })

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      expect(screen.getByText('Выберите возраст персонажа')).toBeInTheDocument()
      expect(screen.getByLabelText('18-25')).toBeInTheDocument()
      expect(screen.getByLabelText('26-35')).toBeInTheDocument()
      expect(screen.getByLabelText('36-45')).toBeInTheDocument()
      expect(screen.getByLabelText('45+')).toBeInTheDocument()
    })

    it('should render multiple choice question with checkboxes', () => {
      const question = createMockQuestion({
        text: 'Выберите черты характера',
        type: 'MULTIPLE_CHOICE',
        options: ['Добрый', 'Злой', 'Умный', 'Хитрый']
      })

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      expect(screen.getByText('Выберите черты характера')).toBeInTheDocument()
      
      // Check that checkboxes are rendered (not radio buttons)
      const checkboxes = screen.getAllByRole('checkbox')
      expect(checkboxes).toHaveLength(4)
    })

    it('should render question hint when provided', () => {
      const question = createMockQuestion({
        text: 'Вопрос с подсказкой',
        hint: 'Это подсказка для ответа'
      })

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      expect(screen.getByText('Это подсказка для ответа')).toBeInTheDocument()
      expect(screen.getByText('💡')).toBeInTheDocument()
    })
  })

  describe('Text input functionality', () => {
    it('should handle text input changes', async () => {
      const user = userEvent.setup()
      const question = createMockQuestion({ type: 'OPEN_TEXT' })

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      const textarea = screen.getByPlaceholderText('Введите ваш ответ...')
      
      await user.type(textarea, 'Тестовый ответ')
      expect(textarea).toHaveValue('Тестовый ответ')
    })

    it('should call onAnswerUpdate when save button clicked', async () => {
      const user = userEvent.setup()
      const question = createMockQuestion({ type: 'OPEN_TEXT' })

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      const textarea = screen.getByPlaceholderText('Введите ваш ответ...')
      
      await user.type(textarea, 'Тестовый ответ')
      
      const saveButton = screen.getByRole('button', { name: 'Сохранить ответ' })
      await user.click(saveButton)

      expect(mockOnAnswerUpdate).toHaveBeenCalledWith(question.id, {
        answer: 'Тестовый ответ',
        comment: '',
        source_type: 'FOUND_IN_TEXT'
      })
    })
  })

  describe('Single choice functionality', () => {
    it('should handle single option selection', async () => {
      const user = userEvent.setup()
      const question = createMockQuestion({
        type: 'SINGLE_CHOICE',
        options: ['Вариант 1', 'Вариант 2', 'Вариант 3']
      })

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      const option1 = screen.getByLabelText('Вариант 1')
      await user.click(option1)

      expect(option1).toBeChecked()

      // Wait for auto-save with real timers
      await waitFor(() => {
        expect(mockOnAnswerUpdate).toHaveBeenCalledWith(question.id, {
          answer: 'Вариант 1',
          comment: '',
          source_type: 'FOUND_IN_TEXT'
        })
      }, { timeout: 2000 })
    })

    it('should unselect previous option when selecting new one', async () => {
      const user = userEvent.setup()
      const question = createMockQuestion({
        type: 'SINGLE_CHOICE',
        options: ['Вариант 1', 'Вариант 2']
      })

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      const option1 = screen.getByLabelText('Вариант 1')
      const option2 = screen.getByLabelText('Вариант 2')

      await user.click(option1)
      expect(option1).toBeChecked()

      await user.click(option2)
      expect(option2).toBeChecked()
      expect(option1).not.toBeChecked()
    })
  })

  describe('Multiple choice functionality', () => {
    it('should handle multiple option selection', async () => {
      const user = userEvent.setup()
      const question = createMockQuestion({
        type: 'MULTIPLE_CHOICE',
        options: ['Вариант 1', 'Вариант 2', 'Вариант 3']
      })

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      const option1 = screen.getByLabelText('Вариант 1')
      const option2 = screen.getByLabelText('Вариант 2')

      await user.click(option1)
      await user.click(option2)

      expect(option1).toBeChecked()
      expect(option2).toBeChecked()

      // Wait for auto-save with real timers
      await waitFor(() => {
        expect(mockOnAnswerUpdate).toHaveBeenCalledWith(question.id, {
          answer: 'Вариант 1, Вариант 2',
          comment: '',
          source_type: 'FOUND_IN_TEXT'
        })
      }, { timeout: 2000 })
    })

    it('should handle option deselection', async () => {
      const user = userEvent.setup()
      const question = createMockQuestion({
        type: 'MULTIPLE_CHOICE',
        options: ['Вариант 1', 'Вариант 2']
      })

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      const option1 = screen.getByLabelText('Вариант 1')

      // Select and then deselect
      await user.click(option1)
      expect(option1).toBeChecked()

      await user.click(option1)
      expect(option1).not.toBeChecked()
    })
  })

  describe('Comments functionality', () => {
    it('should handle comment input and manual save', async () => {
      const user = userEvent.setup()
      const question = createMockQuestion({ type: 'OPEN_TEXT' })

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      const commentField = screen.getByPlaceholderText('Добавьте заметки или обоснование...')
      
      await user.type(commentField, 'Тестовый комментарий')

      // Trigger manual save instead of waiting for debounced save
      const saveButton = screen.getByRole('button', { name: 'Сохранить ответ' })
      await user.click(saveButton)

      expect(mockOnAnswerUpdate).toHaveBeenCalledWith(question.id, {
        answer: '',
        comment: 'Тестовый комментарий',
        source_type: 'FOUND_IN_TEXT'
      })
    })
  })

  describe('Source type selection', () => {
    it('should handle source type changes', async () => {
      const user = userEvent.setup()
      const question = createMockQuestion({ type: 'OPEN_TEXT' })

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      // Find source type radio buttons by their icons/titles
      const logicallyDerivedOption = screen.getByTitle('Логически выведено')
      await user.click(logicallyDerivedOption)

      // Add some content to trigger save
      const textarea = screen.getByPlaceholderText('Введите ваш ответ...')
      await user.type(textarea, 'test')
      
      // Trigger save manually via save button instead of relying on blur
      const saveButton = screen.getByRole('button', { name: 'Сохранить ответ' })
      await user.click(saveButton)

      await waitFor(() => {
        expect(mockOnAnswerUpdate).toHaveBeenCalledWith(question.id, {
          answer: 'test',
          comment: '',
          source_type: 'LOGICALLY_DERIVED'
        })
      }, { timeout: 8000 })
    })
  })

  describe('Save and delete functionality', () => {
    it('should show loading state on save button', () => {
      const question = createMockQuestion()

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={true}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      const saveButton = screen.getByRole('button', { name: 'Сохранение...' })
      expect(saveButton).toBeDisabled()
    })

    it('should call manual save when save button clicked', async () => {
      const user = userEvent.setup()
      const question = createMockQuestion({ type: 'OPEN_TEXT' })

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      // Add some content
      const textarea = screen.getByPlaceholderText('Введите ваш ответ...')
      await user.type(textarea, 'Тестовый ответ')

      // Click save button
      const saveButton = screen.getByRole('button', { name: 'Сохранить ответ' })
      await user.click(saveButton)

      expect(mockOnAnswerUpdate).toHaveBeenCalledWith(question.id, {
        answer: 'Тестовый ответ',
        comment: '',
        source_type: 'FOUND_IN_TEXT'
      })
    })

    it('should show delete button when response exists', () => {
      const question = createMockQuestion({
        current_response: {
          id: 1,
          answer: 'Existing answer',
          comment: 'Comment',
          updated_at: '2023-01-01T00:00:00Z'
        }
      })

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          onAnswerDelete={mockOnAnswerDelete}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      const deleteButton = screen.getByRole('button', { name: '🗑 Удалить' })
      expect(deleteButton).toBeInTheDocument()
    })

    it('should call onAnswerDelete when delete button clicked', async () => {
      const user = userEvent.setup()
      const question = createMockQuestion({
        current_response: {
          id: 123,
          answer: 'Existing answer',
          comment: 'Comment',
          updated_at: '2023-01-01T00:00:00Z'
        }
      })

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          onAnswerDelete={mockOnAnswerDelete}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      const deleteButton = screen.getByRole('button', { name: '🗑 Удалить' })
      await user.click(deleteButton)

      expect(mockOnAnswerDelete).toHaveBeenCalledWith(123)
    })

    it('should show save status when response exists', () => {
      const question = createMockQuestion({
        current_response: {
          id: 1,
          answer: 'Existing answer',
          comment: 'Comment',
          updated_at: '2023-01-01T12:00:00Z'
        }
      })

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      expect(screen.getByText('Сохранено')).toBeInTheDocument()
      expect(screen.getByText('✓')).toBeInTheDocument()
    })
  })

  describe('Existing response handling', () => {
    it('should populate fields with existing response data', () => {
      const question = createMockQuestion({
        type: 'OPEN_TEXT',
        current_response: {
          id: 1,
          answer: 'Existing answer',
          comment: 'Existing comment',
          source_type: 'LOGICALLY_DERIVED',
          updated_at: '2023-01-01T00:00:00Z'
        }
      })

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      const textarea = screen.getByDisplayValue('Existing answer')
      const commentField = screen.getByDisplayValue('Existing comment')
      const sourceOption = screen.getByDisplayValue('LOGICALLY_DERIVED')

      expect(textarea).toBeInTheDocument()
      expect(commentField).toBeInTheDocument()
      expect(sourceOption).toBeChecked()
    })
  })

  describe('Accessibility', () => {
    it('should have proper labels for form elements', () => {
      const question = createMockQuestion({ type: 'OPEN_TEXT' })

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      // Check that labels exist (they're styled as labels but not form-associated)
      expect(screen.getByText('Источник информации:')).toBeInTheDocument()
      expect(screen.getByText('Заметки (опционально):')).toBeInTheDocument()
      
      // Check actual form controls
      expect(screen.getByPlaceholderText('Введите ваш ответ...')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Добавьте заметки или обоснование...')).toBeInTheDocument()
    })

    it('should have proper button roles and labels', () => {
      const question = createMockQuestion()

      render(
        <QuestionCard
          question={question}
          characterGender="male"
          onAnswerUpdate={mockOnAnswerUpdate}
          isLoading={false}
          allQuestions={[question]}
          currentQuestionIndex={0}
          onQuestionSelect={() => {}}
          completionPercentage={0}
        />
      )

      const saveButton = screen.getByRole('button', { name: 'Сохранить ответ' })
      expect(saveButton).toBeInTheDocument()
    })
  })
})
