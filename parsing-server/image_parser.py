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
            'engagement_rate': None
        }
        
        # Очищаем текст от лишних символов
        text_clean = re.sub(r'[^\d\s\n]', ' ', text)
        
        # Ищем числа в тексте
        numbers = re.findall(r'\d+', text)
        
        # Конвертируем в числа
        numbers = [int(n) for n in numbers if len(n) > 0]
        
        # Обычно в Instagram статистике:
        # - Первое большое число - подписчики
        # - Второе большое число - подписки
        # - Третье большое число - публикации
        
        if len(numbers) >= 3:
            # Сортируем числа по убыванию
            sorted_numbers = sorted(numbers, reverse=True)
            
            # Берем три самых больших числа
            # (предполагаем, что это подписчики, подписки, публикации)
            data['followers'] = sorted_numbers[0] if len(sorted_numbers) > 0 else 0
            data['following'] = sorted_numbers[1] if len(sorted_numbers) > 1 else 0
            data['posts_count'] = sorted_numbers[2] if len(sorted_numbers) > 2 else 0
        
        # Пытаемся найти биографию (текст между числами)
        lines = text.split('\n')
        bio_lines = []
        for line in lines:
            line_clean = line.strip()
            if line_clean and not re.match(r'^\d+$', line_clean):
                if len(line_clean) > 10:  # Игнорируем короткие строки
                    bio_lines.append(line_clean)
        
        if bio_lines:
            data['bio'] = ' '.join(bio_lines[:3])  # Берем первые 3 строки
        
        # Вычисляем engagement rate (примерная формула)
        if data['followers'] > 0 and data['posts_count'] > 0:
            # Примерная оценка: engagement = (лайки + комментарии) / подписчики
            # Для упрощения используем формулу на основе количества постов
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

