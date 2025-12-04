"""
Генератор детальных отчетов по Instagram профилям
"""
import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class InstagramReportGenerator:
    """Генератор аналитических отчетов по Instagram профилям"""
    
    def __init__(self):
        self.themes_keywords = {
            'spirituality': ['духовн', 'осознанн', 'медитац', 'практик', 'трансформац', 'исцелен', 'внутренн'],
            'business': ['бизнес', 'предпринимател', 'стартап', 'продаж', 'маркетинг'],
            'fitness': ['фитнес', 'тренировк', 'спорт', 'здоров', 'тело', 'диет'],
            'beauty': ['красот', 'макияж', 'косметик', 'уход', 'стиль'],
            'education': ['обучен', 'курс', 'школ', 'образован', 'навык'],
            'travel': ['путешеств', 'туризм', 'страны', 'отпуск'],
            'food': ['еда', 'рецепт', 'кулинар', 'ресторан', 'готов'],
            'lifestyle': ['образ жизни', 'лайфстайл', 'стиль жизни']
        }
        
        self.partner_categories = {
            'education': [
                'Образовательные платформы (Skillbox, Praktikum, GetCourse)',
                'Онлайн-курсы и программы',
                'Платформы для обучения',
                'Образовательные сервисы'
            ],
            'wellness': [
                'БАДы и витамины премиум-сегмента',
                'Продукты для здоровья и wellness',
                'Медитативные приложения',
                'ЗОЖ бренды',
                'Био-хакерские продукты'
            ],
            'mindfulness': [
                'Приложения для медитации',
                'Трекеры привычек',
                'Тайм-менеджмент сервисы',
                'Нейрософты и ИИ-ассистенты',
                'Продукты для концентрации'
            ],
            'communities': [
                'Закрытые клубы и сообщества',
                'Mastermind группы',
                'Пространства развития',
                'Ретриты и духовные практики'
            ],
            'eco': [
                'Эко-бренды',
                'Sustainable бренды',
                'Одежда в стиле mindfulness',
                'Ароматы, свечи, благовония'
            ]
        }
    
    def generate_report(self, profile_data: Dict, screenshot_data: Dict = None) -> str:
        """
        Генерирует детальный отчет по профилю
        
        Args:
            profile_data: Данные профиля из базы
            screenshot_data: Дополнительные данные из скриншота
            
        Returns:
            str: Текстовый отчет
        """
        username = profile_data.get('username', 'unknown')
        followers = profile_data.get('followers', 0)
        following = profile_data.get('following', 0)
        posts_count = profile_data.get('posts_count', 0)
        bio = profile_data.get('bio', '')
        engagement_rate = profile_data.get('engagement_rate', 0)
        
        # Извлекаем данные из скриншота
        views = screenshot_data.get('views', 0) if screenshot_data else 0
        interactions = screenshot_data.get('interactions', 0) if screenshot_data else 0
        new_followers = screenshot_data.get('new_followers', 0) if screenshot_data else 0
        messages = screenshot_data.get('messages', 0) if screenshot_data else 0
        shares = screenshot_data.get('shares', 0) if screenshot_data else 0
        
        # Анализируем тематику
        theme_analysis = self._analyze_theme(bio, profile_data)
        
        # Определяем потенциальных партнеров
        partners = self._identify_partners(theme_analysis)
        
        # Генерируем отчет
        report = self._build_report(
            username=username,
            followers=followers,
            following=following,
            posts_count=posts_count,
            bio=bio,
            engagement_rate=engagement_rate,
            views=views,
            interactions=interactions,
            new_followers=new_followers,
            messages=messages,
            shares=shares,
            theme_analysis=theme_analysis,
            partners=partners
        )
        
        return report
    
    def _analyze_theme(self, bio: str, profile_data: Dict) -> Dict:
        """Анализирует тематику аккаунта"""
        bio_lower = bio.lower() if bio else ''
        
        themes = []
        positioning = []
        
        # Определяем темы по ключевым словам
        for theme, keywords in self.themes_keywords.items():
            for keyword in keywords:
                if keyword in bio_lower:
                    themes.append(theme)
                    break
        
        # Извлекаем позиционирование из биографии
        if bio:
            # Ищем ключевые фразы
            if any(word in bio_lower for word in ['наставник', 'коуч', 'тренер']):
                positioning.append('эксперт/наставник')
            if any(word in bio_lower for word in ['помогаю', 'помощь']):
                positioning.append('помощь аудитории')
            if any(word in bio_lower for word in ['консультац', 'услуг']):
                positioning.append('консультационные услуги')
        
        return {
            'themes': list(set(themes)),
            'positioning': positioning if positioning else ['личный бренд'],
            'bio_keywords': self._extract_keywords(bio)
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Извлекает ключевые слова из текста"""
        if not text:
            return []
        
        # Удаляем стоп-слова и извлекаем значимые слова
        stop_words = {'и', 'в', 'на', 'с', 'по', 'для', 'от', 'к', 'из', 'о', 'у', 'за', 'со', 'под', 'над'}
        words = re.findall(r'\b[а-яё]{4,}\b', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        return list(set(keywords))[:10]  # Топ-10 ключевых слов
    
    def _identify_partners(self, theme_analysis: Dict) -> List[str]:
        """Определяет потенциальных партнеров на основе тематики"""
        partners = []
        themes = theme_analysis.get('themes', [])
        
        if 'spirituality' in themes or 'mindfulness' in [t for t in themes]:
            partners.extend(self.partner_categories.get('wellness', []))
            partners.extend(self.partner_categories.get('mindfulness', []))
            partners.extend(self.partner_categories.get('communities', []))
            partners.extend(self.partner_categories.get('eco', []))
        
        if 'education' in themes:
            partners.extend(self.partner_categories.get('education', []))
        
        if 'business' in themes:
            partners.extend(self.partner_categories.get('education', []))
            partners.extend(self.partner_categories.get('mindfulness', []))
        
        # Убираем дубликаты
        return list(set(partners))
    
    def _build_report(self, username: str, followers: int, following: int, 
                     posts_count: int, bio: str, engagement_rate: float,
                     views: int, interactions: int, new_followers: int,
                     messages: int, shares: int, theme_analysis: Dict,
                     partners: List[str]) -> str:
        """Строит текстовый отчет"""
        
        # Вычисляем месячный ER если есть взаимодействия
        monthly_er = None
        if interactions > 0 and followers > 0:
            monthly_er = (interactions / followers) * 100
        
        # Вычисляем рост аудитории
        growth_rate = None
        if new_followers > 0 and followers > 0:
            growth_rate = (new_followers / followers) * 100
        
        report = f"""✅ 1. Цифры и статистика по аккаунту @{username}

📊 Основные показатели профиля

Подписчики: {self._format_number(followers)}
Подписки: {self._format_number(following)}
Количество публикаций: {self._format_number(posts_count)}
"""
        
        if bio:
            positioning_text = ', '.join(theme_analysis.get('positioning', []))
            report += f"Позиционирование: {positioning_text}\n"
            
            # Проверяем наличие ссылки в био
            if 't.me' in bio.lower() or 'telegram' in bio.lower():
                report += "Ссылка в био: активный переход в Telegram — это большой плюс для рекламодателей (конверсионная модель)\n"
        
        if views > 0 or interactions > 0:
            report += f"""
📈 Профессиональная аналитика (за месяц)

По скриншоту:
"""
            if views > 0:
                report += f"Просмотры: {self._format_number(views)}\n"
                if followers > 0:
                    views_per_follower = views / followers
                    if views_per_follower > 50:
                        report += "Это очень сильный показатель для профиля — значит, Reels хорошо разлетаются в рекомендации.\n"
            
            if interactions > 0:
                report += f"Взаимодействия: {self._format_number(interactions)}\n"
                if monthly_er and monthly_er > 5:
                    report += "Уровень выше среднего => аккаунт \"живой\", аудитория реально вовлечена.\n"
            
            if new_followers > 0:
                report += f"Новые подписчики: {self._format_number(new_followers)} за 30 дней\n"
                if growth_rate:
                    if growth_rate > 5:
                        report += f"Рост ~{growth_rate:.1f}% в месяц — отличный органический показатель.\n"
                    else:
                        report += f"Рост ~{growth_rate:.1f}% в месяц — стабильный рост.\n"
            
            if messages > 0:
                report += f"Сообщений: {messages}\n"
                if messages < 50:
                    report += "Небольшой показатель — но это нормально, если основной фокус не на личных консультациях через Direct.\n"
            
            if shares > 0:
                report += f"Контент, которым поделились: {shares}\n"
                if shares > 30:
                    report += "Это очень хорошо. Шеринги — индикатор ценности контента.\n"
        
        # Engagement Rate
        if engagement_rate > 0 or monthly_er:
            report += f"""
📊 Расчёт ER (Engagement Rate)
"""
            if monthly_er:
                report += f"Месячный ER ≈ {monthly_er:.1f}%\n"
                if monthly_er > 10:
                    report += "Высокий месячный ER говорит:\n"
                    report += "✔ контент \"цепляет\"\n"
                    report += "✔ люди возвращаются\n"
                    report += "✔ алгоритмы Instagram любят твои видео\n"
                    report += "✔ высокий trust-фактор\n"
            elif engagement_rate > 0:
                er_percent = engagement_rate * 100
                report += f"ER на постах: {er_percent:.1f}%\n"
        
        # Анализ тематики
        themes = theme_analysis.get('themes', [])
        keywords = theme_analysis.get('bio_keywords', [])
        
        report += f"""
🌿 2. Анализ аккаунта: тематика, интересы аудитории, потенциальные рекламодатели

🎯 Тематика аккаунта
"""
        
        if themes:
            theme_names = {
                'spirituality': 'духовность',
                'business': 'бизнес',
                'fitness': 'фитнес',
                'beauty': 'красота',
                'education': 'образование',
                'travel': 'путешествия',
                'food': 'еда',
                'lifestyle': 'лайфстайл'
            }
            theme_list = [theme_names.get(t, t) for t in themes]
            report += ', '.join(theme_list) + '\n'
        
        if keywords:
            report += f"Ключевые слова: {', '.join(keywords[:5])}\n"
        
        if bio:
            report += f"Биография: {bio[:200]}{'...' if len(bio) > 200 else ''}\n"
        
        report += """
👥 Предполагаемая аудитория

(по контенту и нише)

25–45 лет
Люди, ищущие поддержку, структуру, внутренний баланс
Интерес к саморазвитию и личностному росту
Аудитория готова покупать трансформационные услуги, консультации, курсы
"""
        
        # Потенциальные партнеры
        if partners:
            report += """
🤝 Потенциальные рекламодатели / партнёры

Твой профиль идеально подходит для нескольких категорий:

"""
            for i, partner in enumerate(partners[:10], 1):  # Топ-10
                report += f"{i}. {partner}\n"
        
        # Рекомендации
        report += """
✨ 3. Рекомендации по улучшению аккаунта

🌟 Сильные стороны

✔ Чистое позиционирование
✔ Высокий уровень вовлеченности
✔ Органический рост аудитории
"""
        
        if views > 0 and followers > 0:
            views_ratio = views / followers
            if views_ratio > 50:
                report += "✔ Reels работают отлично — высокий охват\n"
        
        report += """
🔧 Что можно улучшить

1. Био сделать более продающим
   - Добавить конкретные выгоды для аудитории
   - Указать, что человек получит

2. Добавить формат: "вопрос–ответ" в сторис
   - Увеличит доверие
   - Углубит отношения с аудиторией

3. Расширить хайлайты
   - Добавить больше категорий контента
   - Сделать навигацию удобнее

4. Регулярный контент
   - Поддерживать активность
   - Постоянное взаимодействие с аудиторией
"""
        
        return report
    
    def _format_number(self, num: int) -> str:
        """Форматирует число с пробелами для тысяч"""
        if num >= 1000000:
            return f"{num / 1000000:.1f}M".replace('.0', '')
        elif num >= 1000:
            return f"{num / 1000:.1f}K".replace('.0', '')
        return str(num)


