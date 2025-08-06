import * as fs from 'fs';
import * as path from 'path';

// Интерфейсы для структуры JSON
interface Question {
    question: string;
    options: string[];
    optionsType: 'single' | 'multiple';
    source: string[];
    hint?: string;
}

interface QuestionGroup {
    title: string;
    questions: Question[];
}

interface Subsection {
    title: string;
    groups: QuestionGroup[];
    examples: Example[];
    whyImportant: string;
}

interface Example {
    text: string;
    value: string;
}

interface Section {
    title: string;
    subsections: Subsection[];
}

interface Goal {
    title: string;
    description: string;
}

interface Checklist {
    title: string;
    goal: Goal;
    sections: Section[];
}

class MarkdownToJsonConverter {
    private lines: string[] = [];
    private currentLineIndex: number = 0;

    constructor(private markdownContent: string) {
        this.lines = markdownContent.split('\n');
    }

    convert(): Checklist {
        const checklist: Checklist = {
            title: '',
            goal: { title: '', description: '' },
            sections: []
        };

        while (this.currentLineIndex < this.lines.length) {
            const line = this.getCurrentLine();

            if (line.startsWith('# ')) {
                checklist.title = line.replace('# ', '').replace(/^🎭\s*/, '');
            } else if (line === '## Цель чеклиста') {
                checklist.goal = this.parseGoal();
            } else if (line.startsWith('### ') && line.includes('. ')) {
                const section = this.parseSection();
                if (section) {
                    checklist.sections.push(section);
                }
            }

            this.currentLineIndex++;
        }

        return checklist;
    }

    private getCurrentLine(): string {
        return this.currentLineIndex < this.lines.length ? this.lines[this.currentLineIndex].trim() : '';
    }

    private parseGoal(): Goal {
        this.currentLineIndex++; // пропускаем заголовок
        this.currentLineIndex++; // пропускаем пустую строку

        let description = '';
        while (this.currentLineIndex < this.lines.length) {
            const line = this.getCurrentLine();
            if (line.startsWith('###') || line.startsWith('##')) {
                break;
            }
            if (line.length > 0) {
                description += line + ' ';
            }
            this.currentLineIndex++;
        }

        this.currentLineIndex--; // возвращаемся на шаг назад

        return {
            title: 'Цель',
            description: description.trim()
        };
    }

    private parseSection(): Section | null {
        const sectionTitle = this.getCurrentLine().replace('### ', '');
        const section: Section = {
            title: sectionTitle,
            subsections: []
        };

        this.currentLineIndex++;

        while (this.currentLineIndex < this.lines.length) {
            const line = this.getCurrentLine();

            if (line.startsWith('### ')) {
                // Новая секция
                this.currentLineIndex--;
                break;
            } else if (line.startsWith('#### ')) {
                const subsection = this.parseSubsection();
                if (subsection) {
                    section.subsections.push(subsection);
                }
            } else {
                this.currentLineIndex++;
            }
        }

        return section;
    }

    private parseSubsection(): Subsection | null {
        const subsectionTitle = this.getCurrentLine().replace('#### ', '');

        const subsection: Subsection = {
            title: subsectionTitle,
            groups: [],
            examples: [],
            whyImportant: ''
        };

        this.currentLineIndex++;

        while (this.currentLineIndex < this.lines.length) {
            const line = this.getCurrentLine();

            if (line.startsWith('##### ')) {
                const groupTitle = line.replace('##### ', '');
                
                if (groupTitle === 'Примеры') {
                    // Примеры обрабатываем и добавляем к подсекции
                    subsection.examples = this.parseExamples();
                } else if (groupTitle.startsWith('Почему это важно')) {
                    // Важность тоже добавляем к подсекции
                    subsection.whyImportant = this.parseWhyImportant();
                } else {
                    // Обычная группа вопросов
                    const group = this.parseQuestionGroup(groupTitle);
                    if (group) {
                        subsection.groups.push(group);
                    }
                }
            } else if (line.startsWith('####') || line.startsWith('###')) {
                this.currentLineIndex--;
                break;
            } else {
                this.currentLineIndex++;
            }
        }

        return subsection;
    }

    private parseQuestionGroup(title: string): QuestionGroup | null {
        const group: QuestionGroup = {
            title,
            questions: []
        };

        this.currentLineIndex++;

        while (this.currentLineIndex < this.lines.length) {
            const line = this.getCurrentLine();

            if (line.startsWith('#####') || line.startsWith('####') || line.startsWith('###')) {
                this.currentLineIndex--;
                break;
            } else if (line.startsWith('- ')) {
                const question = this.parseQuestion();
                if (question) {
                    group.questions.push(question);
                }
            } else {
                this.currentLineIndex++;
            }
        }

        return group.questions.length > 0 ? group : null;
    }

    private parseQuestion(): Question | null {
        const questionLine = this.getCurrentLine();
        const questionText = questionLine.replace(/^- /, '').replace(/\?$/, '').trim();

        const question: Question = {
            question: questionText,
            options: [],
            optionsType: 'single',
            source: ['text', 'logic', 'imagination']
        };

        this.currentLineIndex++;

        // Парсим варианты ответов
        while (this.currentLineIndex < this.lines.length) {
            const line = this.getCurrentLine();

            if (line.startsWith('- Варианты ')) {
                const { options, optionsType } = this.parseVariants(line);
                question.options = options;
                question.optionsType = optionsType;
            } else if (line.startsWith('- Подсказка:')) {
                question.hint = line.replace('- Подсказка:', '').trim();
            } else if (line.startsWith('- ') || line.startsWith('#####') || line.startsWith('####') || line.startsWith('###')) {
                this.currentLineIndex--;
                break;
            }

            this.currentLineIndex++;
        }

        // Добавляем "свой вариант" если его нет
        if (!question.options.includes('свой вариант')) {
            question.options.push('свой вариант');
        }

        return question;
    }

    private parseVariants(line: string): { options: string[], optionsType: 'single' | 'multiple' } {
        // Извлекаем тип ответа и варианты
        const match = line.match(/Варианты \((.*?)\): (.+)/);
        if (!match) {
            return { options: [], optionsType: 'single' };
        }

        const typeText = match[1];
        const optionsText = match[2];

        // Определяем тип ответа
        const optionsType: 'single' | 'multiple' = 
            typeText.includes('много') ? 'multiple' : 'single';

        // Разбираем варианты
        const options = optionsText.split(',').map(option => option.trim());

        return { options, optionsType };
    }

    private parseExamples(): Example[] {
        this.currentLineIndex++;
        const examples: Example[] = [];

        while (this.currentLineIndex < this.lines.length) {
            const line = this.getCurrentLine();

            if (line.startsWith('#####') || line.startsWith('####')) {
                this.currentLineIndex--;
                break;
            }

            if (line.startsWith('- *') && line.includes('* →')) {
                // Парсим пример в формате: - *текст* → вопрос
                const match = line.match(/- \*(.+?)\* → (.+)/);
                if (match) {
                    examples.push({
                        text: match[1],
                        value: match[2]
                    });
                }
            }

            this.currentLineIndex++;
        }

        return examples;
    }

    private parseWhyImportant(): string {
        const line = this.getCurrentLine();
        
        // Извлекаем текст после "Почему это важно "
        const importanceText = line.replace(/^##### Почему это важно\s*/, '');
        
        this.currentLineIndex++;
        
        // Читаем дополнительные строки если есть
        let fullText = importanceText;
        while (this.currentLineIndex < this.lines.length) {
            const nextLine = this.getCurrentLine();
            
            if (nextLine.startsWith('#####') || nextLine.startsWith('####') || nextLine.startsWith('---')) {
                this.currentLineIndex--;
                break;
            }
            
            if (nextLine.trim().length > 0) {
                fullText += ' ' + nextLine.trim();
            }
            
            this.currentLineIndex++;
        }

        return fullText.trim();
    }
}

// Функция для конвертации файла
export function convertMarkdownToJson(inputFilePath: string, outputFilePath: string): void {
    try {
        // Проверяем существование входного файла
        if (!fs.existsSync(inputFilePath)) {
            throw new Error(`Входной файл не найден: ${inputFilePath}`);
        }

        const markdownContent = fs.readFileSync(inputFilePath, 'utf-8');
        const converter = new MarkdownToJsonConverter(markdownContent);
        const result = converter.convert();
        
        // Создаем директорию для выходного файла если её нет
        const outputDir = path.dirname(outputFilePath);
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        const jsonContent = JSON.stringify(result, null, 4);
        fs.writeFileSync(outputFilePath, jsonContent, 'utf-8');
        
        console.log(`✅ Конвертация завершена успешно!`);
        console.log(`📁 Результат сохранен в: ${outputFilePath}`);
        console.log(`📊 Статистика:`);
        console.log(`   - Секций: ${result.sections.length}`);
        
        // Подсчитываем общее количество вопросов
        let totalQuestions = 0;
        result.sections.forEach(section => {
            section.subsections.forEach(subsection => {
                subsection.groups.forEach(group => {
                    totalQuestions += group.questions.length;
                });
            });
        });
        console.log(`   - Вопросов: ${totalQuestions}`);
        
    } catch (error) {
        console.error('❌ Ошибка при конвертации:', error);
        process.exit(1);
    }
}

// Функция для отображения справки
function showHelp(): void {
    console.log(`
📋 Markdown to JSON Converter

Использование:
  npx ts-node scripts/md-to-json-converter.ts <input-file> <output-file>
  npx ts-node scripts/md-to-json-converter.ts --help

Аргументы:
  input-file    Путь к входному Markdown файлу
  output-file   Путь к выходному JSON файлу

Опции:
  --help        Показать эту справку

Примеры:
  npx ts-node scripts/md-to-json-converter.ts docs/modules/01-physical-portrait/ACTOR_PHYSICAL_CHECKLIST.md output.json
  npx ts-node scripts/md-to-json-converter.ts input.md ./output/result.json
`);
}

// Функция для парсинга аргументов командной строки
function parseArguments(): { inputFile: string; outputFile: string } | null {
    const args = process.argv.slice(2);
    
    // Показываем справку если запрошена
    if (args.includes('--help') || args.includes('-h')) {
        showHelp();
        return null;
    }
    
    // Проверяем количество аргументов
    if (args.length !== 2) {
        console.error('❌ Ошибка: Необходимо указать входной и выходной файлы');
        console.error('Используйте --help для получения справки');
        process.exit(1);
    }
    
    const [inputFile, outputFile] = args;
    
    return { inputFile, outputFile };
}

// Главная функция
function main(): void {
    const args = parseArguments();
    if (!args) {
        return; // Справка уже показана
    }
    
    const { inputFile, outputFile } = args;
    
    console.log(`🔄 Конвертация файла: ${inputFile} → ${outputFile}`);
    convertMarkdownToJson(inputFile, outputFile);
}

// Запуск утилиты если файл выполняется напрямую
if (require.main === module) {
    main();
} 
