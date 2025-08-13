"""
Сервис для определения пола персонажа по имени и контексту.
"""

import re
from typing import Optional, Dict, List
from ..nlp.models import Gender


class GenderDetector:
    """Класс для определения пола персонажа."""
    
    def __init__(self):
        # Мужские имена и окончания
        self.male_names = {
            'александр', 'алексей', 'андрей', 'антон', 'артем', 'борис', 'вадим', 'валентин',
            'василий', 'виктор', 'владимир', 'владислав', 'вячеслав', 'геннадий', 'георгий',
            'григорий', 'дмитрий', 'евгений', 'егор', 'иван', 'игорь', 'илья', 'кирилл',
            'константин', 'леонид', 'максим', 'михаил', 'николай', 'олег', 'павел', 'петр',
            'роман', 'сергей', 'станислав', 'степан', 'федор', 'юрий', 'ярослав'
        }
        
        # Женские имена и окончания
        self.female_names = {
            'александра', 'алла', 'анастасия', 'анна', 'валентина', 'вера', 'виктория',
            'галина', 'дарья', 'екатерина', 'елена', 'жанна', 'зоя', 'инна', 'ирина',
            'кристина', 'лариса', 'лидия', 'любовь', 'людмила', 'марина', 'мария',
            'наталья', 'нина', 'ольга', 'полина', 'раиса', 'светлана', 'татьяна',
            'ульяна', 'юлия', 'яна'
        }
        
        # Мужские окончания имен
        self.male_endings = {
            'ич', 'ович', 'евич', 'ич', 'ей', 'ий', 'ин', 'он', 'ан', 'ен'
        }
        
        # Женские окончания имен
        self.female_endings = {
            'а', 'я', 'на', 'ина', 'ова', 'ева', 'ская', 'цкая'
        }
        
        # Мужские титулы и обращения
        self.male_titles = {
            'господин', 'мистер', 'сэр', 'барон', 'граф', 'князь', 'царь', 'король',
            'отец', 'батюшка', 'дядя', 'дедушка', 'брат', 'сын', 'муж', 'жених'
        }
        
        # Женские титулы и обращения
        self.female_titles = {
            'госпожа', 'мисс', 'миссис', 'леди', 'баронесса', 'графиня', 'княгиня',
            'царица', 'королева', 'мать', 'матушка', 'тетя', 'бабушка', 'сестра',
            'дочь', 'жена', 'невеста'
        }
        
        # Мужские профессии и роли
        self.male_roles = {
            'король', 'царь', 'князь', 'граф', 'барон', 'рыцарь', 'воин', 'солдат',
            'капитан', 'генерал', 'офицер', 'купец', 'торговец', 'мастер', 'кузнец',
            'плотник', 'охотник', 'пастух', 'монах', 'священник', 'учитель', 'доктор'
        }
        
        # Женские профессии и роли
        self.female_roles = {
            'королева', 'царица', 'княгиня', 'графиня', 'баронесса', 'дама', 'леди',
            'служанка', 'горничная', 'кухарка', 'няня', 'учительница', 'монахиня',
            'ведьма', 'целительница', 'швея', 'прачка'
        }

    def detect_gender(self, name: str, description: Optional[str] = None, context: Optional[str] = None) -> Gender:
        """
        Определяет пол персонажа по имени, описанию и контексту.
        
        Args:
            name: Имя персонажа
            description: Описание персонажа из текста
            context: Дополнительный контекст (речь персонажа, упоминания)
            
        Returns:
            Пол персонажа
        """
        name_lower = name.lower().strip()
        
        # Убираем отчества и фамилии, оставляем только имя
        first_name = self._extract_first_name(name_lower)
        
        # 1. Проверяем по известным именам
        gender_by_name = self._detect_by_name(first_name)
        if gender_by_name != Gender.UNKNOWN:
            return gender_by_name
            
        # 2. Проверяем по окончаниям имени
        gender_by_ending = self._detect_by_ending(first_name)
        if gender_by_ending != Gender.UNKNOWN:
            return gender_by_ending
            
        # 3. Проверяем по описанию
        if description:
            gender_by_description = self._detect_by_description(description.lower())
            if gender_by_description != Gender.UNKNOWN:
                return gender_by_description
                
        # 4. Проверяем по контексту
        if context:
            gender_by_context = self._detect_by_context(context.lower())
            if gender_by_context != Gender.UNKNOWN:
                return gender_by_context
                
        return Gender.UNKNOWN

    def _extract_first_name(self, full_name: str) -> str:
        """Извлекает первое имя из полного имени."""
        # Убираем титулы
        for title in list(self.male_titles) + list(self.female_titles):
            full_name = full_name.replace(title, '').strip()
            
        # Берем части имени
        parts = full_name.split()
        if not parts:
            return full_name
            
        # Если есть фамилия и имя отчество (русский формат)
        # Например: "Астров Михаил Львович" -> берем "Михаил"
        if len(parts) >= 2:
            # Проверяем, не является ли первое слово фамилией
            first_part = parts[0].lower()
            second_part = parts[1].lower() if len(parts) > 1 else ""
            
            # Если второе слово - известное имя, используем его
            if second_part in self.male_names or second_part in self.female_names:
                return second_part
            
            # Если первое слово заканчивается на типичные фамильные окончания
            if (first_part.endswith(('ов', 'ев', 'ин', 'ын', 'ский', 'цкий', 'енко', 'ко')) and
                len(parts) >= 2):
                return parts[1]  # Возвращаем второе слово (имя)
        
        # По умолчанию берем первое слово
        return parts[0]

    def _detect_by_name(self, name: str) -> Gender:
        """Определяет пол по известным именам."""
        if name in self.male_names:
            return Gender.MALE
        elif name in self.female_names:
            return Gender.FEMALE
        return Gender.UNKNOWN

    def _detect_by_ending(self, name: str) -> Gender:
        """Определяет пол по окончанию имени."""
        # Проверяем женские окончания (они обычно более специфичны)
        for ending in sorted(self.female_endings, key=len, reverse=True):
            if name.endswith(ending):
                return Gender.FEMALE
                
        # Проверяем мужские окончания
        for ending in sorted(self.male_endings, key=len, reverse=True):
            if name.endswith(ending):
                return Gender.MALE
                
        return Gender.UNKNOWN

    def _detect_by_description(self, description: str) -> Gender:
        """Определяет пол по описанию персонажа."""
        # Ищем мужские маркеры
        male_score = 0
        female_score = 0
        
        # Проверяем титулы и обращения
        for title in self.male_titles:
            if title in description:
                male_score += 2
                
        for title in self.female_titles:
            if title in description:
                female_score += 2
                
        # Проверяем профессии и роли
        for role in self.male_roles:
            if role in description:
                male_score += 1
                
        for role in self.female_roles:
            if role in description:
                female_score += 1
                
        # Проверяем местоимения и прилагательные
        male_pronouns = ['он', 'его', 'ему', 'им', 'нем', 'молодой', 'старый', 'красивый']
        female_pronouns = ['она', 'ее', 'ей', 'ею', 'ней', 'молодая', 'старая', 'красивая']
        
        for pronoun in male_pronouns:
            male_score += description.count(pronoun)
            
        for pronoun in female_pronouns:
            female_score += description.count(pronoun)
            
        if male_score > female_score:
            return Gender.MALE
        elif female_score > male_score:
            return Gender.FEMALE
            
        return Gender.UNKNOWN

    def _detect_by_context(self, context: str) -> Gender:
        """Определяет пол по контексту (речь, упоминания)."""
        # Аналогично описанию, но с меньшим весом
        male_score = 0
        female_score = 0
        
        # Ищем обращения к персонажу
        male_references = ['господин', 'сэр', 'мистер', 'он сказал', 'он ответил']
        female_references = ['госпожа', 'мисс', 'миссис', 'она сказала', 'она ответила']
        
        for ref in male_references:
            if ref in context:
                male_score += 1
                
        for ref in female_references:
            if ref in context:
                female_score += 1
                
        if male_score > female_score:
            return Gender.MALE
        elif female_score > male_score:
            return Gender.FEMALE
            
        return Gender.UNKNOWN

    def get_confidence_score(self, name: str, description: Optional[str] = None) -> float:
        """
        Возвращает уверенность в определении пола (0.0-1.0).
        
        Args:
            name: Имя персонажа
            description: Описание персонажа
            
        Returns:
            Уверенность в определении пола
        """
        first_name = self._extract_first_name(name.lower())
        
        # Высокая уверенность для известных имен
        if first_name in self.male_names or first_name in self.female_names:
            return 0.9
            
        # Средняя уверенность для окончаний
        for ending in self.female_endings:
            if first_name.endswith(ending):
                return 0.7
                
        for ending in self.male_endings:
            if first_name.endswith(ending):
                return 0.6
                
        # Низкая уверенность для контекстных подсказок
        if description:
            male_markers = sum(1 for title in self.male_titles if title in description.lower())
            female_markers = sum(1 for title in self.female_titles if title in description.lower())
            
            if male_markers > 0 or female_markers > 0:
                return 0.5
                
        return 0.1  # Очень низкая уверенность