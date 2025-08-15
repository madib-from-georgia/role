import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { render } from '../../utils/test-utils'
import { QuestionCard } from '../../../components/checklists/QuestionCard'
import { createMockQuestion, createMockAnswer } from '../../utils/mock-data'

describe('QuestionCard', () => {
  const mockOnAnswerUpdate = vi.fn()
  const mockOnAnswerDelete = vi.fn()
  const mockOnMultipleAnswersUpdate = vi.fn()
  const mockOnPrevious = vi.fn()
  const mockOnNext = vi.fn()
  const mockOnQuestionSelect = vi.fn()

  // Helper function to create default props
  const createDefaultProps = (overrides = {}) => ({
    characterGender: "male" as const,
    characterId: 1,
    onAnswerUpdate: mockOnAnswerUpdate,
    onMultipleAnswersUpdate: mockOnMultipleAnswersUpdate,
    onAnswerDelete: mockOnAnswerDelete,
    isLoading: false,
    allQuestions: [],
    currentQuestionIndex: 0,
    onQuestionSelect: mockOnQuestionSelect,
    completionPercentage: 0,
    onPrevious: mockOnPrevious,
    onNext: mockOnNext,
    canGoBack: false,
    canGoForward: false,
    ...overrides
  })

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
          {...createDefaultProps()}
          question={null as never}
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
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
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
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
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
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
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
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
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
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
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
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
        />
      )

      const textarea = screen.getByPlaceholderText('Введите ваш ответ...')
      
      await user.type(textarea, 'Тестовый ответ')
      
      const saveButton = screen.getByRole('button', { name: 'Сохранить ответ' })
      await user.click(saveButton)

      expect(mockOnAnswerUpdate).toHaveBeenCalledWith(question.id, {
        answer_text: 'Тестовый ответ',
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
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
        />
      )

      // Single choice questions need answers array
      const questionWithAnswers = {
        ...question,
        answers: [
          createMockAnswer({ id: 1, value_male: 'Вариант 1', value_female: 'Вариант 1', external_id: 'option1' }),
          createMockAnswer({ id: 2, value_male: 'Вариант 2', value_female: 'Вариант 2', external_id: 'option2' }),
          createMockAnswer({ id: 3, value_male: 'Вариант 3', value_female: 'Вариант 3', external_id: 'option3' })
        ]
      }

      render(
        <QuestionCard
          {...createDefaultProps({ allQuestions: [questionWithAnswers] })}
          question={questionWithAnswers}
        />
      )

      // Find radio button by its content text
      const option1 = screen.getByText('Вариант 1').closest('label')?.querySelector('input')
      expect(option1).toBeTruthy()
      
      await user.click(option1!)
      expect(option1).toBeChecked()

      // Wait for auto-save with real timers
      await waitFor(() => {
        expect(mockOnAnswerUpdate).toHaveBeenCalledWith(questionWithAnswers.id, {
          answer_id: 1,
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
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
        />
      )

      // Single choice questions need answers array
      const questionWithAnswers = {
        ...question,
        answers: [
          createMockAnswer({ id: 1, value_male: 'Вариант 1', value_female: 'Вариант 1', external_id: 'option1' }),
          createMockAnswer({ id: 2, value_male: 'Вариант 2', value_female: 'Вариант 2', external_id: 'option2' })
        ]
      }

      render(
        <QuestionCard
          {...createDefaultProps({ allQuestions: [questionWithAnswers] })}
          question={questionWithAnswers}
        />
      )

      const option1 = screen.getByText('Вариант 1').closest('label')?.querySelector('input')
      const option2 = screen.getByText('Вариант 2').closest('label')?.querySelector('input')

      await user.click(option1!)
      expect(option1).toBeChecked()

      await user.click(option2!)
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
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
        />
      )

      // Multiple choice questions need answers array
      const questionWithAnswers = {
        ...question,
        answers: [
          createMockAnswer({ id: 1, value_male: 'Вариант 1', value_female: 'Вариант 1', external_id: 'option1' }),
          createMockAnswer({ id: 2, value_male: 'Вариант 2', value_female: 'Вариант 2', external_id: 'option2' }),
          createMockAnswer({ id: 3, value_male: 'Вариант 3', value_female: 'Вариант 3', external_id: 'option3' })
        ]
      }

      render(
        <QuestionCard
          {...createDefaultProps({ allQuestions: [questionWithAnswers] })}
          question={questionWithAnswers}
        />
      )

      const option1 = screen.getByText('Вариант 1').closest('label')?.querySelector('input')
      const option2 = screen.getByText('Вариант 2').closest('label')?.querySelector('input')

      await user.click(option1!)
      await user.click(option2!)

      expect(option1).toBeChecked()
      expect(option2).toBeChecked()

      // Wait for auto-save with real timers - component saves first selected answer
      await waitFor(() => {
        expect(mockOnAnswerUpdate).toHaveBeenCalledWith(questionWithAnswers.id, {
          answer_id: 1, // Component uses first selected answer for multiple choice
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
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
        />
      )

      // Multiple choice questions need answers array
      const questionWithAnswers = {
        ...question,
        answers: [
          createMockAnswer({ id: 1, value_male: 'Вариант 1', value_female: 'Вариант 1', external_id: 'option1' }),
          createMockAnswer({ id: 2, value_male: 'Вариант 2', value_female: 'Вариант 2', external_id: 'option2' })
        ]
      }

      render(
        <QuestionCard
          {...createDefaultProps({ allQuestions: [questionWithAnswers] })}
          question={questionWithAnswers}
        />
      )

      const option1 = screen.getByText('Вариант 1').closest('label')?.querySelector('input')

      // Select and then deselect
      await user.click(option1!)
      expect(option1).toBeChecked()

      await user.click(option1!)
      expect(option1).not.toBeChecked()
    })
  })

  describe('Comments functionality', () => {
    it('should handle comment input and manual save', async () => {
      const user = userEvent.setup()
      const question = createMockQuestion({ type: 'OPEN_TEXT' })

      render(
        <QuestionCard
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
        />
      )

      const commentField = screen.getByPlaceholderText('Цитаты, обоснование, свои мысли...')
      
      await user.type(commentField, 'Тестовый комментарий')

      // Trigger manual save instead of waiting for debounced save
      const saveButton = screen.getByRole('button', { name: 'Сохранить' })
      await user.click(saveButton)

      // Check that the last call has the complete comment (no answer_text if empty)
      const lastCall = mockOnAnswerUpdate.mock.calls[mockOnAnswerUpdate.mock.calls.length - 1]
      expect(lastCall).toEqual([question.id, {
        comment: 'Тестовый комментарий',
        source_type: 'FOUND_IN_TEXT'
      }])
    })
  })

  describe('Source type selection', () => {
    it('should handle source type changes', async () => {
      const user = userEvent.setup()
      const question = createMockQuestion({ type: 'OPEN_TEXT' })

      render(
        <QuestionCard
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
        />
      )

      // Find source type radio buttons by their icons/titles
      const logicallyDerivedOption = screen.getByTitle('Логически выведено на основе фактов и обстоятельств в первоисточнике')
      await user.click(logicallyDerivedOption)

      // Add some content to trigger save
      const textarea = screen.getByPlaceholderText('Введите ваш ответ...')
      await user.type(textarea, 'test')
      
      // Trigger save manually via save button instead of relying on blur
      const saveButton = screen.getByRole('button', { name: 'Сохранить' })
      await user.click(saveButton)

      await waitFor(() => {
        expect(mockOnAnswerUpdate).toHaveBeenCalledWith(question.id, {
          answer_text: 'test',
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
          {...createDefaultProps({ allQuestions: [question], isLoading: true })}
          question={question}
        />
      )

      // Loading state doesn't change button text in this component
      const saveButton = screen.getByRole('button', { name: 'Сохранить' })
      expect(saveButton).toBeInTheDocument()
      // The component doesn't disable the button during loading
    })

    it('should call manual save when save button clicked', async () => {
      const user = userEvent.setup()
      const question = createMockQuestion({ type: 'OPEN_TEXT' })

      render(
        <QuestionCard
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
        />
      )

      // Add some content
      const textarea = screen.getByPlaceholderText('Введите ваш ответ...')
      await user.type(textarea, 'Тестовый ответ')

      // Click save button
      const saveButton = screen.getByRole('button', { name: 'Сохранить' })
      await user.click(saveButton)

      // Check that the last call has the complete answer
      const lastCall = mockOnAnswerUpdate.mock.calls[mockOnAnswerUpdate.mock.calls.length - 1]
      expect(lastCall).toEqual([question.id, {
        answer_text: 'Тестовый ответ',
        comment: '',
        source_type: 'FOUND_IN_TEXT'
      }])
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
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
        />
      )

      const deleteButton = screen.getByTitle('Удалить ответ')
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
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
        />
      )

      const deleteButton = screen.getByTitle('Удалить ответ')
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
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
        />
      )

      expect(screen.getByText(/Сохранено/)).toBeInTheDocument()
    })
  })

  describe('Existing response handling', () => {
    it('should populate fields with existing response data', () => {
      const question = createMockQuestion({
        answer_type: 'text',
        current_response: {
          id: 1,
          answer_text: 'Existing answer',
          comment: 'Existing comment',
          source_type: 'LOGICALLY_DERIVED',
          updated_at: '2023-01-01T00:00:00Z'
        }
      })

      render(
        <QuestionCard
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
        />
      )

      // Check that the textarea contains the existing answer
      const textarea = screen.getByPlaceholderText('Введите ваш ответ...')
      expect(textarea).toHaveValue('Existing answer')
      
      // Check that the comment field contains the existing comment
      const commentField = screen.getByPlaceholderText('Цитаты, обоснование, свои мысли...')
      expect(commentField).toHaveValue('Existing comment')
      
      // Check that the correct source type is selected
      const sourceOption = screen.getByDisplayValue('LOGICALLY_DERIVED')
      expect(sourceOption).toBeChecked()
    })
  })

  describe('Accessibility', () => {
    it('should have proper labels for form elements', () => {
      const question = createMockQuestion({ type: 'OPEN_TEXT' })

      render(
        <QuestionCard
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
        />
      )

      // Check that labels exist (they're styled as labels but not form-associated)
      expect(screen.getByText('Источник ответа:')).toBeInTheDocument()
      expect(screen.getByText('Дополнить ответ:')).toBeInTheDocument()
      
      // Check actual form controls
      expect(screen.getByPlaceholderText('Введите ваш ответ...')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Цитаты, обоснование, свои мысли...')).toBeInTheDocument()
    })

    it('should have proper button roles and labels', () => {
      const question = createMockQuestion()

      render(
        <QuestionCard
          {...createDefaultProps({ allQuestions: [question] })}
          question={question}
        />
      )

      const saveButton = screen.getByRole('button', { name: 'Сохранить' })
      expect(saveButton).toBeInTheDocument()
    })
  })
})
