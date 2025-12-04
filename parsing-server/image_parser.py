import cv2
import numpy as np
from PIL import Image
import pytesseract
import re
import logging

logger = logging.getLogger(__name__)


class InstagramScreenshotParser:
    """Парсер для извлечения данных из скриншота Instagram статистики"""
    
    def __init__(self):
        # Настройка Tesseract для русского и английского языков
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    
    def parse_screenshot(self, image_path: str) -> dict:
        """
        Парсит скриншот Instagram профиля и извлекает данные
        
        Args:
            image_path: Путь к изображению
            
        Returns:
            dict: Словарь с извлеченными данными
        """
        try:
            # Загружаем изображение
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Не удалось загрузить изображение: {image_path}")
            
            # Конвертируем в RGB для PIL
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            
            # Извлекаем текст с изображения
            text = pytesseract.image_to_string(pil_image, lang='rus+eng')
            
            logger.info(f"Извлеченный текст: {text[:200]}...")
            
            # Парсим данные
            data = self._extract_data_from_text(text)
            
            return data
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге изображения: {e}")
            raise
    
    def _extract_data_from_text(self, text: str) -> dict:
        """
        Извлекает числовые данные из текста
        
        Args:
            text: Текст, извлеченный из изображения
            
        Returns:
            dict: Словарь с извлеченными данными
        """
        data = {
            'followers': 0,
            'following': 0,
            'posts_count': 0,
            'bio': None,
            'engagement_rate': None,
            'views': 0,
            'interactions': 0,
            'new_followers': 0,
            'messages': 0,
            'shares': 0
        }
        
        text_lower = text.lower()
        
        # Ищем профессиональную панель данные
        # Просмотры
        views_match = re.search(r'просмотр[ыао]?[:\s]+([\d\s]+)', text_lower)
        if views_match:
            views_str = re.sub(r'[^\d]', '', views_match.group(1))
            if views_str:
                try:
                    data['views'] = int(views_str)
                except:
                    pass
        
        # Взаимодействия
        interactions_match = re.search(r'взаимодейств[ияе]+[:\s]+([\d\s]+)', text_lower)
        if interactions_match:
            int_str = re.sub(r'[^\d]', '', interactions_match.group(1))
            if int_str:
                try:
                    data['interactions'] = int(int_str)
                except:
                    pass
        
        # Новые подписчики
        new_followers_match = re.search(r'нов[ые]+ подписчик[и]+[:\s]+([\d\s]+)', text_lower)
        if new_followers_match:
            nf_str = re.sub(r'[^\d]', '', new_followers_match.group(1))
            if nf_str:
                try:
                    data['new_followers'] = int(nf_str)
                except:
                    pass
        
        # Сообщения
        messages_match = re.search(r'сообщени[йя]+[:\s]+([\d\s]+)', text_lower)
        if messages_match:
            msg_str = re.sub(r'[^\d]', '', messages_match.group(1))
            if msg_str:
                try:
                    data['messages'] = int(msg_str)
                except:
                    pass
        
        # Шеринги
        shares_match = re.search(r'поделил[ись]+[:\s]+([\d\s]+)', text_lower)
        if shares_match:
            sh_str = re.sub(r'[^\d]', '', shares_match.group(1))
            if sh_str:
                try:
                    data['shares'] = int(sh_str)
                except:
                    pass
        
        # Ищем основные числа (подписчики, подписки, публикации)
        # Сначала ищем конкретно подписчиков, подписки и публикации по контексту
        
        # Ищем подписчиков (followers) - самый важный показатель
        # Сначала ищем явные упоминания "followers" или "подписчик"
        followers_patterns = [
            r'(\d+[.,]?\d*)\s*(тыс|k|thousand|тысяч)\s*(подписчик|follower|followers)',
            r'(подписчик|follower|followers)[:\s]+(\d+[.,]?\d*)\s*(тыс|k|thousand|тысяч)?',
            r'(\d+[.,]?\d*)\s*(тыс|k|thousand|тысяч)\s*(followers|подписчик)',
            r'(\d{2,3})\s*(k|тыс|thousand|тысяч)\s*(followers|подписчик)',  # 102K followers
            r'(\d+)\s*(подписчик|follower|followers)',  # Просто число и слово
            r'(подписчик|follower|followers)\s*(\d+)',  # Слово и число
            r'(\d{1,3}[.,]\d+)\s*(тыс|k|thousand|тысяч)',  # 44.9K или 44,9K
            r'(\d{4,})\s*(подписчик|follower|followers)',  # Большие числа без суффикса (10000+)
        ]
        
        # Также ищем числа в формате "102K" рядом со словом "followers" или "подписчик"
        context_patterns = [
            r'(\d{2,3})\s*(k|тыс|thousand|тысяч)\b.*?(followers|подписчик)',
            r'(followers|подписчик).*?(\d{2,3})\s*(k|тыс|thousand|тысяч)\b',
        ]
        
        for pattern in followers_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    num_part = match.group(1) if match.lastindex >= 1 else match.group(2)
                    suffix = match.group(2) if match.lastindex >= 2 else (match.group(3) if match.lastindex >= 3 else '')
                    
                    # Очищаем число от запятых и точек
                    num_str = num_part.replace(',', '').replace('.', '')
                    num = float(num_str)
                    
                    # Если есть суффикс K/тыс, умножаем на 1000
                    if suffix and suffix.lower() in ['k', 'тыс', 'thousand', 'тысяч']:
                        num = int(num * 1000)
                    else:
                        num = int(num)
                    
                    # Убираем ограничение минимума для более точного парсинга
                    # Но все равно проверяем разумность значения
                    if num > 0:
                        data['followers'] = max(data['followers'], num)
                        logger.info(f"Найдено подписчиков: {num}")
                        if num > 1000:  # Если нашли большое число, можно прервать поиск
                            break
                except Exception as e:
                    logger.debug(f"Ошибка парсинга подписчиков: {e}")
                    continue
        
        # Если не нашли через основные паттерны, ищем через контекстные
        if data['followers'] == 0:
            for pattern in context_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        # Ищем число и суффикс в разных группах
                        groups = match.groups()
                        num_str = None
                        suffix = None
                        
                        for g in groups:
                            if g and g.isdigit():
                                num_str = g
                            elif g and g.lower() in ['k', 'тыс', 'thousand', 'тысяч']:
                                suffix = g
                        
                        if num_str and suffix:
                            num = float(num_str) * 1000
                            if num > 1000:
                                data['followers'] = max(data['followers'], int(num))
                                logger.info(f"Найдено подписчиков через контекст: {int(num)}")
                                break
                    except Exception as e:
                        logger.debug(f"Ошибка парсинга контекста: {e}")
                        continue
                
                if data['followers'] > 0:
                    break
        
        # Ищем подписки (following)
        following_patterns = [
            r'(подписк|following)[:\s]+(\d+[.,]?\d*)\s*(тыс|k|thousand|тысяч)?',
            r'(\d+[.,]?\d*)\s*(тыс|k|thousand|тысяч)?\s*(подписк|following)',
        ]
        
        for pattern in following_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    num_part = match.group(1) if match.lastindex >= 1 else match.group(2)
                    suffix = match.group(2) if match.lastindex >= 2 else (match.group(3) if match.lastindex >= 3 else '')
                    
                    num_str = num_part.replace(',', '').replace('.', '')
                    num = float(num_str)
                    
                    if suffix and suffix.lower() in ['k', 'тыс', 'thousand', 'тысяч']:
                        num = int(num * 1000)
                    else:
                        num = int(num)
                    
                    if num > 0 and num != data['followers']:
                        data['following'] = max(data['following'], num)
                        logger.info(f"Найдено подписок: {num}")
                        break
                except:
                    continue
        
        # Ищем публикации (posts)
        posts_patterns = [
            r'(публикац|post|posts)[:\s]+(\d+[.,]?\d*)\s*(тыс|k|thousand|тысяч)?',
            r'(\d+[.,]?\d*)\s*(тыс|k|thousand|тысяч)?\s*(публикац|post|posts)',
            r'\b(\d{1,4})\s*(post|posts|публикац)\b',  # Обычно публикаций меньше 10K
        ]
        
        for pattern in posts_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    num_part = match.group(1) if match.lastindex >= 1 else match.group(2)
                    suffix = match.group(2) if match.lastindex >= 2 else (match.group(3) if match.lastindex >= 3 else '')
                    
                    num_str = num_part.replace(',', '').replace('.', '')
                    num = float(num_str)
                    
                    if suffix and suffix.lower() in ['k', 'тыс', 'thousand', 'тысяч']:
                        num = int(num * 1000)
                    else:
                        num = int(num)
                    
                    if num > 0 and num < data['followers']:  # Публикаций обычно меньше подписчиков
                        data['posts_count'] = max(data['posts_count'], num)
                        logger.info(f"Найдено публикаций: {num}")
                        break
                except:
                    continue
        
        # Если не нашли через контекстные паттерны, используем старый метод
        if data['followers'] == 0:
            numbers = []
            number_patterns = [
                r'(\d+)[.,]?(\d+)\s*(тыс|k|thousand|тысяч)',
                r'(\d+)\s*(тыс|k|thousand|тысяч)',
                r'(\d{2,3})[.,](\d{3})',  # 102,000 или 44,500
                r'\b(\d{4,})\b'  # Большие числа без форматирования
            ]
            
            for pattern in number_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        # Обрабатываем случаи типа (102, 'K') или (102, 000)
                        parts = [str(m) for m in match if str(m)]
                        if len(parts) >= 2:
                            if parts[-1].lower() in ['k', 'тыс', 'thousand', 'тысяч']:
                                # Случай "102K"
                                num = float(parts[0].replace(',', '').replace('.', ''))
                                num = int(num * 1000)
                            else:
                                # Случай "102,000"
                                num_str = ''.join([p for p in parts if p.isdigit()])
                                num = int(num_str) if num_str else 0
                        else:
                            num_str = ''.join([p for p in parts if p.isdigit()])
                            num = int(num_str) if num_str else 0
                    else:
                        num_str = str(match).replace(',', '').replace('.', '')
                        num = int(num_str) if num_str.isdigit() else 0
                    
                    if num > 1000:
                        numbers.append(num)
            
            # Сортируем и берем самые большие
            if numbers:
                sorted_numbers = sorted(set(numbers), reverse=True)
                
                if len(sorted_numbers) >= 3:
                    data['followers'] = sorted_numbers[0] if data['followers'] == 0 else data['followers']
                    data['following'] = sorted_numbers[1] if data['following'] == 0 else data['following']
                    data['posts_count'] = sorted_numbers[2] if data['posts_count'] == 0 else data['posts_count']
                elif len(sorted_numbers) == 2:
                    data['followers'] = sorted_numbers[0] if data['followers'] == 0 else data['followers']
                    data['following'] = sorted_numbers[1] if data['following'] == 0 else data['following']
                elif len(sorted_numbers) == 1:
                    data['followers'] = sorted_numbers[0] if data['followers'] == 0 else data['followers']
        
        # Пытаемся найти биографию (текст между числами)
        lines = text.split('\n')
        bio_lines = []
        for line in lines:
            line_clean = line.strip()
            if line_clean and not re.match(r'^[\d\s,\.]+$', line_clean):
                if len(line_clean) > 10 and not any(word in line_clean.lower() for word in ['подписчик', 'публикац', 'просмотр', 'взаимодейств']):
                    bio_lines.append(line_clean)
        
        if bio_lines:
            data['bio'] = ' '.join(bio_lines[:5])  # Берем первые 5 строк
        
        # Вычисляем engagement rate
        if data['interactions'] > 0 and data['followers'] > 0:
            data['engagement_rate'] = round(data['interactions'] / data['followers'], 4)
        elif data['followers'] > 0 and data['posts_count'] > 0:
            # Примерная оценка на основе постов
            estimated_engagement = min(0.1, data['posts_count'] / (data['followers'] * 10))
            data['engagement_rate'] = round(estimated_engagement, 4)
        
        return data
    
    def preprocess_image(self, image_path: str) -> str:
        """
        Предобработка изображения для улучшения распознавания
        
        Args:
            image_path: Путь к исходному изображению
            
        Returns:
            str: Путь к обработанному изображению
        """
        try:
            # Загружаем изображение
            image = cv2.imread(image_path)
            
            # Конвертируем в grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Применяем бинаризацию
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Убираем шум
            denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
            
            # Сохраняем обработанное изображение
            processed_path = image_path.replace('.jpg', '_processed.jpg')
            cv2.imwrite(processed_path, denoised)
            
            return processed_path
            
        except Exception as e:
            logger.error(f"Ошибка при предобработке изображения: {e}")
            return image_path  # Возвращаем исходный путь при ошибке

