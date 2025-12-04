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
        # Ищем паттерны типа "44,5 тыс" или "44500"
        numbers = []
        
        # Ищем числа с разделителями тысяч
        number_patterns = [
            r'(\d+)[,\s]+(\d+)\s*(тыс|k|thousand)',
            r'(\d+)\s*(тыс|k|thousand)',
            r'(\d+)[,\s]*(\d+)[,\s]*(\d+)',  # 44,500
            r'\b(\d{4,})\b'  # Большие числа
        ]
        
        for pattern in number_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    num_str = ''.join([str(m) for m in match if str(m).isdigit()])
                else:
                    num_str = match
                
                if num_str and len(num_str) >= 3:
                    try:
                        num = int(num_str)
                        if num > 10:  # Игнорируем маленькие числа
                            numbers.append(num)
                    except:
                        pass
        
        # Если не нашли через паттерны, ищем все числа
        if not numbers:
            all_numbers = re.findall(r'\d+', text)
            numbers = [int(n) for n in all_numbers if len(n) >= 3 and int(n) > 10]
        
        # Сортируем и берем три самых больших
        if numbers:
            sorted_numbers = sorted(set(numbers), reverse=True)
            
            # Обычно: подписчики > подписки > публикации
            if len(sorted_numbers) >= 3:
                data['followers'] = sorted_numbers[0]
                data['following'] = sorted_numbers[1]
                data['posts_count'] = sorted_numbers[2]
            elif len(sorted_numbers) == 2:
                data['followers'] = sorted_numbers[0]
                data['following'] = sorted_numbers[1]
            elif len(sorted_numbers) == 1:
                data['followers'] = sorted_numbers[0]
        
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

