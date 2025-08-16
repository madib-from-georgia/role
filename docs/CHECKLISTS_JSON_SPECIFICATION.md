
## JSON с данными

```typescript
interface Portrait {
    // id портрета: `<id портрета>`
    id: string;          
    // Название портрета: `Физический портрет`
    title: string;     
    // массив секций портрета 
    sections: Section[]; 
}

interface Section {
    // id секции: `<id секции>`
    id: string;      
    // Название секции портрета: `Внешность и физические данные`
    title: string; 
    // массив подсекций портрета 
    subsections: Subsection[]; 
}


interface Subsection {
    // id подсекции: `<id подсекции>`
    id: string;                
    // Название подсекции внутри секции: `Телосложение и антропометрия`
    title: string; 
    questionGroups: QuestionGroup[]; 
}

interface QuestionGroup {
    // id группы: `<id группы>`
    id: string;      
    // Название группы вопросов в подсекции: `Рост и пропорции тела`
    title: string; 
    questions: Question[]; 
}

interface Question {
    // id вопроса: `<id вопроса>`
    id: string;      
    // Название вопроса: `Какой у меня рост?`
    title: string; 
    answers: Answer[]; 
}

interface Answer {
    // id ответа: `<id ответа>`
    id: string;      
    // Ответ в зависимости от пола персонажа. 
    // Отображается в UI
    value: AnswerValue; 
    // Ответ в зависимости от пола персонажа. 
    // Отображается в экспортированном документе
    exportedValue: AnswerValue; 
    // Рекомендация актеру, как этот ответ влияет на технику актерской игры
    hint: string; 
    // Рекомендация актеру, какими упражнениями тренировать технику актерской игры
    exercise: string; 
}

interface AnswerValue {
    // Ответ для мужчины. Например, "Высокий"
    male: string;      
    // Ответ для женщины. Например, "Высокая" 
    female: string; 
}

const checklist: Portrait = {
    "id": "physical-portrait",
    "title": "Физический портрет",
    "sections": [
        {
            "id": "appearance",
            "title": "Внешность и физические данные",
            "subsections": [
                {
                    "id": "physique",
                    "title": "Телосложение и антропометрия",
                    "questionGroups": [
                        {
                            "id": "height-proportions",
                            "title": "Рост и пропорции тела",
                            "questions": [
                                {
                                    "id": "height",
                                    "title": "Какой у меня рост?",
                                    "answers": [
                                        {
                                            "id": "short",
                                            "value": {
                                                "male": "низкий",
                                                "female": "низкий"
                                            },
                                            "exportedValue": {
                                                 "male": "Я невысокого роста",
                                                 "female": "Я невысокого роста"
                                             },
                                            "hint": "Невысокий человек может компенсировать или комплексовать",
                                            "exercise": "Упражнение 1: делайте короткие шаги"
                                        },
                                        {
                                            "id": "average",
                                            "value": {
                                                "male": "средний",
                                                "female": "средний"
                                            },
                                            "exportedValue": {
                                                 "male": "Я среднего роста",
                                                 "female": "Я среднего роста"
                                             },
                                            "hint": "Человек среднего роста чувствует себя комфортно среди себе подобных",
                                            "exercise": "Упражнение 1: делайте средние шаги"
                                        },
                                        {
                                            "id": "tall",
                                            "value": {
                                                "male": "высокий",
                                                "female": "высокий"
                                            },
                                            "exportedValue": {
                                                 "male": "Я высокий",
                                                 "female": "Я высокая"
                                             },
                                             "hint": "Рост влияет на самооценку и поведение — высокие часто держатся увереннее",
                                            "exercise": "Упражнение 1: делайте большие шаги"
                                        }
                                    ],
                                    "answerType": "single",
                                    "source": "text"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
};
```   
  