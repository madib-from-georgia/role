import * as fs from 'fs';
import * as path from 'path';

// TypeScript интерфейсы согласно спецификации
interface AnswerValue {
    male: string;
    female: string;
}

interface Answer {
    id: string;
    value: AnswerValue;
    exportedValue: AnswerValue;
    hint: string;
    exercise: string;
}

interface Question {
    id: string;
    title: string;
    answers: Answer[];
    answerType: string;
    source: string;
}

interface QuestionGroup {
    id: string;
    title: string;
    questions: Question[];
}

interface Subsection {
    id: string;
    title: string;
    questionGroups: QuestionGroup[];
}

interface Section {
    id: string;
    title: string;
    subsections: Subsection[];
}

interface Portrait {
    id: string;
    title: string;
    sections: Section[];
}

class ConvertPortrait {
    private lines: string[] = [];
    private currentIndex: number = 0;

    constructor(private content: string) {
        this.lines = content.split('\n');
    }

    /**
     * Транслитерирует кириллицу в латиницу
     */
    private transliterate(text: string): string {
        const translitMap: { [key: string]: string } = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
        };

        return text.replace(/[а-яё]/g, (char) => translitMap[char] || char);
    }

    /**
     * Создает человеко-читаемый ID из текста
     */
    private createId(text: string): string {
        if (!text || text.trim() === '') {
            return `generated-id-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        }

        let processed = text.toLowerCase();

        // Убираем числовые префиксы типа "1.", "2.1", "3.2.1" и т.д.
        processed = processed.replace(/^\d+(\.\d+)*\.?\s*/, '');

        // Транслитерируем кириллицу
        processed = this.transliterate(processed);

        // Убираем специальные символы, оставляем только буквы, цифры, пробелы и дефисы
        processed = processed.replace(/[^\w\s-]/g, '');

        // Заменяем пробелы на дефисы
        processed = processed.replace(/\s+/g, '-');

        // Убираем множественные дефисы
        processed = processed.replace(/--+/g, '-');

        // Убираем дефисы в начале и конце
        processed = processed.replace(/^-+|-+$/g, '');

        // Ограничиваем длину
        processed = processed.substring(0, 50);

        // Если после обработки получилась пустая строка, генерируем уникальный ID
        if (!processed) {
            return `generated-id-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        }

        return processed;
    }

    /**
     * Извлекает варианты ответов из строки
     */
    private extractAnswerOptions(optionsLine: string): string[] {
        // Ищем паттерн "Варианты (...): ..."
        const match = optionsLine.match(/Варианты\s*\([^)]+\):\s*(.+)/);
        if (!match) return [];

        return match[1].split(',').map(option => option.trim());
    }

    /**
     * Создает ответы с учетом пола персонажа
     */
    private createAnswers(options: string[], hint: string = ''): Answer[] {
        return options.map((option, index) => {
            const id = this.createId(option);

            // Базовые варианты для мужского и женского пола
            const maleValue = option;
            const femaleValue = this.adaptAnswerForGender(option, 'female');

            // Экспортируемые значения (более развернутые)
            const maleExported = this.createExportedAnswer(option, 'male');
            const femaleExported = this.createExportedAnswer(option, 'female');

            return {
                id: id || `option-${index}`,
                value: {
                    male: maleValue,
                    female: femaleValue
                },
                exportedValue: {
                    male: maleExported,
                    female: femaleExported
                },
                hint: hint,
                exercise: '' // Пустое поле для упражнений
            };
        });
    }

    /**
     * Адаптирует ответ для конкретного пола
     */
    private adaptAnswerForGender(answer: string, gender: 'male' | 'female'): string {
        if (gender === 'female') {
            // Словарь для правильной адаптации окончаний
            const femaleMap: { [key: string]: string } = {
                'высокий': 'высокая',
                'низкий': 'низкая',
                'средний': 'средняя',
                'худощавый': 'худощавая',
                'полный': 'полная',
                'стройный': 'стройная',
                'мускулистый': 'мускулистая',
                'подтянутый': 'подтянутая',
                'дряблый': 'дряблая',
                'ловкий': 'ловкая',
                'неуклюжий': 'неуклюжая'
            };

            // Проверяем точные совпадения
            if (femaleMap[answer]) {
                return femaleMap[answer];
            }

            // Общие правила для окончаний
            return answer
                .replace(/ый$/, 'ая')
                .replace(/ий$/, 'ая') // исправлено с 'яя' на 'ая'
                .replace(/ой$/, 'ая')
                .replace(/ен$/, 'на');
        }
        return answer;
    }

    /**
     * Создает экспортируемый вариант ответа
     */
    private createExportedAnswer(answer: string, gender: 'male' | 'female'): string {
        if (answer === 'свой вариант') {
            return '';
        }

        const adaptedAnswer = this.adaptAnswerForGender(answer, gender);

        // Специфические правила для разных типов ответов
        if (answer.includes('высокий') || answer.includes('низкий') || answer.includes('средний')) {
            return `Я ${adaptedAnswer} роста`;
        }

        if (answer.includes('горжусь') || answer.includes('комплексую') || answer.includes('не обращаю внимания')) {
            return `Я ${adaptedAnswer} своему росту`;
        }

        if (answer.includes('длинноногий') || answer.includes('коротконогий') || answer.includes('пропорциональный')) {
            return `У меня ${adaptedAnswer} пропорции тела`;
        }

        if (answer.includes('астеническое') || answer.includes('нормостеническое') || answer.includes('гиперстеническое')) {
            return `У меня ${adaptedAnswer} телосложение`;
        }

        if (answer.includes('подтянутый') || answer.includes('дряблый') || answer.includes('средняя форма')) {
            return `Я в ${adaptedAnswer} физической форме`;
        }

        if (answer.includes('быстро устаю') || answer.includes('неутомим') || answer.includes('средняя выносливость')) {
            return `Я ${adaptedAnswer}`;
        }

        // Общий случай
        return `У меня ${adaptedAnswer}`;
    }

    /**
     * Парсит вопрос из markdown
     */
    private parseQuestion(questionLine: string): Question | null {
        // Убираем маркер списка и очищаем
        const questionText = questionLine.replace(/^-\s*/, '').trim();
        if (!questionText.endsWith('?')) return null;

        const questionId = this.createId(questionText);

        // Ищем следующие строки с вариантами и подсказкой
        let optionsLine = '';
        let hintLine = '';
        let foundOptionsIndex = -1;

        for (let i = this.currentIndex + 1; i < this.lines.length; i++) {
            const line = this.lines[i].trim();

            if (line.startsWith('- Варианты')) {
                optionsLine = line;
                foundOptionsIndex = i;
            } else if (line.startsWith('- Подсказка:')) {
                hintLine = line.replace(/^-\s*Подсказка:\s*/, '');
                // Если найдена подсказка, обновляем currentIndex до этой позиции
                this.currentIndex = i;
                break;
            } else if (line.startsWith('-') && line.includes('?') && foundOptionsIndex > -1) {
                // Начался новый вопрос, прекращаем поиск
                break;
            } else if (line.startsWith('#')) {
                // Начался новый раздел
                break;
            }
        }

        const options = this.extractAnswerOptions(optionsLine);
        const answers = this.createAnswers(options, hintLine);

        // Определяем тип ответа
        const answerType = optionsLine.includes('один ответ') ? 'single' : 'multiple';

        return {
            id: questionId,
            title: questionText,
            answers: answers,
            answerType: answerType,
            source: 'text'
        };
    }

    /**
     * Парсит группу вопросов
     */
    private parseQuestionGroup(groupLine: string): QuestionGroup {
        const groupTitle = groupLine.replace(/^#+\s*/, '').trim();
        const groupId = this.createId(groupTitle);

        const questions: Question[] = [];

        // Ищем вопросы в этой группе
        for (let i = this.currentIndex + 1; i < this.lines.length; i++) {
            const line = this.lines[i].trim();

            if (line.startsWith('#')) {
                // Начался новый заголовок
                break;
            }

            if (line.startsWith('- ') && line.includes('?')) {
                this.currentIndex = i;
                const question = this.parseQuestion(line);
                if (question) {
                    questions.push(question);
                }
            }
        }

        return {
            id: groupId,
            title: groupTitle,
            questions: questions
        };
    }



    /**
     * Парсит подсекцию
     */
    private parseSubsection(subsectionLine: string): Subsection {
        const subsectionTitle = subsectionLine.replace(/^#+\s*/, '').trim();
        const subsectionId = this.createId(subsectionTitle);

        const questionGroups: QuestionGroup[] = [];
        let startIndex = this.currentIndex + 1;
        let hasQuestionGroups = false;

        // Ищем группы вопросов (заголовки 5 уровня)
        for (let i = startIndex; i < this.lines.length; i++) {
            const line = this.lines[i].trim();

            if (line.startsWith('####') && !line.startsWith('#####')) {
                // Новая подсекция
                break;
            }

            if (line.startsWith('##### ') && !line.includes('Примеры') && !line.includes('Почему это важно')) {
                hasQuestionGroups = true;
                this.currentIndex = i;
                const group = this.parseQuestionGroup(line);
                questionGroups.push(group);
            }
        }

        // Если групп вопросов не найдено, создаем служебную группу
        if (!hasQuestionGroups) {
            // Сбрасываем currentIndex к началу подсекции для поиска вопросов
            this.currentIndex = startIndex - 1;
            
            const serviceGroup: QuestionGroup = {
                id: `service-group-${subsectionId}`,
                title: `Вопросы раздела "${subsectionTitle}"`,
                questions: []
            };

            // Ищем вопросы в подсекции
            for (let i = startIndex; i < this.lines.length; i++) {
                const line = this.lines[i].trim();

                if (line.startsWith('####') && !line.startsWith('#####')) {
                    // Новая подсекция
                    break;
                }

                if (line.startsWith('#####')) {
                    // Началась группа вопросов (хотя мы уже знаем, что их нет)
                    break;
                }

                if (line.startsWith('- ') && line.includes('?')) {
                    this.currentIndex = i;
                    const question = this.parseQuestion(line);
                    if (question) {
                        serviceGroup.questions.push(question);
                    }
                }
            }

            questionGroups.push(serviceGroup);
        }

        return {
            id: subsectionId,
            title: subsectionTitle,
            questionGroups: questionGroups
        };
    }

    /**
     * Парсит секцию
     */
    private parseSection(sectionLine: string): Section {
        const sectionTitle = sectionLine.replace(/^#+\s*/, '').trim();
        const sectionId = this.createId(sectionTitle);

        const subsections: Subsection[] = [];
        let startIndex = this.currentIndex + 1;

        // Ищем подсекции (заголовки 4 уровня)
        for (let i = startIndex; i < this.lines.length; i++) {
            const line = this.lines[i].trim();

            if (line.startsWith('###') && !line.startsWith('####')) {
                // Новая секция
                break;
            }

            if (line.startsWith('#### ')) {
                this.currentIndex = i;
                const subsection = this.parseSubsection(line);
                subsections.push(subsection);
            }
        }

        return {
            id: sectionId,
            title: sectionTitle,
            subsections: subsections
        };
    }

    /**
     * Основной метод конвертации
     */
    public convert(): Portrait {
        const portrait: Portrait = {
            id: '',
            title: '',
            sections: []
        };

                // Ищем заголовок первого уровня для начала
        for (let i = 0; i < this.lines.length; i++) {
            const line = this.lines[i].trim();

            if (line.startsWith('# ')) {
                const title = line.replace(/^#\s*/, '').trim();
                portrait.title = title.replace(/🎭\s*/, ''); // убираем эмодзи
                portrait.id = this.createId(title); // создаем ID на основе заголовка
                break;
            }
        }

        // Ищем секции (заголовки 3 уровня)
        for (let i = 0; i < this.lines.length; i++) {
            const line = this.lines[i].trim();

            if (line.startsWith('### ') && !line.startsWith('####')) {
                this.currentIndex = i;
                const section = this.parseSection(line);
                portrait.sections.push(section);
            }
        }

        return portrait;
    }
}

// Функция для запуска конвертера
function convertPortrait(inputPath: string, outputPath: string): void {
    try {
        console.log('Начинаю конвертацию файла:', inputPath);

        const content = fs.readFileSync(inputPath, 'utf-8');
        const converter = new ConvertPortrait(content);
        const result = converter.convert();

        const jsonContent = JSON.stringify(result, null, 2);
        fs.writeFileSync(outputPath, jsonContent, 'utf-8');

        console.log('Конвертация завершена успешно!');
        console.log('Результат сохранен в:', outputPath);
        console.log('Статистика:');
        console.log(`- Секций: ${result.sections.length}`);
        console.log(`- Подсекций: ${result.sections.reduce((sum, s) => sum + s.subsections.length, 0)}`);
        console.log(`- Групп вопросов: ${result.sections.reduce((sum, s) => sum + s.subsections.reduce((sum2, ss) => sum2 + ss.questionGroups.length, 0), 0)}`);
        console.log(`- Вопросов: ${result.sections.reduce((sum, s) => sum + s.subsections.reduce((sum2, ss) => sum2 + ss.questionGroups.reduce((sum3, qg) => sum3 + qg.questions.length, 0), 0), 0)}`);

    } catch (error) {
        console.error('Ошибка при конвертации:', error);
        process.exit(1);
    }
}

// Функция для вывода справки
function showHelp(): void {
    console.log(`
🎭 Конвертер чеклистов физического портрета в JSON

Использование:
  npx ts-node scripts/convert-portrait.ts <входной_файл> <выходной_файл>

Аргументы:
  входной_файл    Путь к MD файлу чеклиста
  выходной_файл   Путь для сохранения JSON файла

Примеры:
  npx ts-node scripts/convert-portrait.ts input.md output.json
  npx ts-node scripts/convert-portrait.ts checklist.md result.json

Описание:
  Конвертирует MD файл чеклиста физического портрета в структурированный JSON
  с автоматической генерацией человеко-читаемых ID и транслитерацией кириллицы.
`);
}

// Запуск если файл выполняется напрямую
if (require.main === module) {
    // Проверяем аргументы командной строки
    const args = process.argv.slice(2);

    if (args.includes('--help') || args.includes('-h') || args.length === 0) {
        showHelp();
        process.exit(0);
    }

    // Проверяем, что переданы оба аргумента
    if (args.length < 2) {
        console.error('❌ Ошибка: необходимо указать входной и выходной файлы');
        console.log('');
        showHelp();
        process.exit(1);
    }

    const inputFile = args[0];
    const outputFile = args[1];

    convertPortrait(inputFile, outputFile);
}

export { ConvertPortrait, convertPortrait as convertPhysicalPortrait };
