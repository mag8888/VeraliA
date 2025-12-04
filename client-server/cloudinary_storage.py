"""
Модуль для работы с Cloudinary хранилищем
"""
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url
import logging

logger = logging.getLogger(__name__)

# Инициализация Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)


def upload_image(file_path: str, folder: str = "verali", public_id: str = None) -> dict:
    """
    Загружает изображение в Cloudinary
    
    Args:
        file_path: Путь к локальному файлу
        folder: Папка в Cloudinary (по умолчанию "verali")
        public_id: Публичный ID файла (если не указан, генерируется автоматически)
        
    Returns:
        dict: Результат загрузки с URL изображения
    """
    try:
        options = {
            "folder": folder,
            "resource_type": "image",
            "format": "jpg"
        }
        
        if public_id:
            options["public_id"] = public_id
        
        result = cloudinary.uploader.upload(file_path, **options)
        
        logger.info(f"Изображение загружено в Cloudinary: {result.get('secure_url')}")
        
        return {
            "success": True,
            "url": result.get("secure_url"),
            "public_id": result.get("public_id"),
            "format": result.get("format"),
            "bytes": result.get("bytes")
        }
    except Exception as e:
        logger.error(f"Ошибка при загрузке в Cloudinary: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def upload_image_from_bytes(image_bytes: bytes, folder: str = "verali", public_id: str = None) -> dict:
    """
    Загружает изображение в Cloudinary из байтов
    
    Args:
        image_bytes: Байты изображения
        folder: Папка в Cloudinary
        public_id: Публичный ID файла
        
    Returns:
        dict: Результат загрузки с URL изображения
    """
    try:
        options = {
            "folder": folder,
            "resource_type": "image",
            "format": "jpg"
        }
        
        if public_id:
            options["public_id"] = public_id
        
        result = cloudinary.uploader.upload(image_bytes, **options)
        
        logger.info(f"Изображение загружено в Cloudinary: {result.get('secure_url')}")
        
        return {
            "success": True,
            "url": result.get("secure_url"),
            "public_id": result.get("public_id"),
            "format": result.get("format"),
            "bytes": result.get("bytes")
        }
    except Exception as e:
        logger.error(f"Ошибка при загрузке в Cloudinary: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_image_url(public_id: str, transformation: dict = None) -> str:
    """
    Получает URL изображения из Cloudinary
    
    Args:
        public_id: Публичный ID файла
        transformation: Опции трансформации (опционально)
        
    Returns:
        str: URL изображения
    """
    try:
        url, _ = cloudinary_url(public_id, transformation=transformation)
        return url
    except Exception as e:
        logger.error(f"Ошибка при получении URL: {e}")
        return None


def delete_image(public_id: str) -> bool:
    """
    Удаляет изображение из Cloudinary
    
    Args:
        public_id: Публичный ID файла
        
    Returns:
        bool: True если удалено успешно
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception as e:
        logger.error(f"Ошибка при удалении из Cloudinary: {e}")
        return False


def list_examples(folder: str = "verali/examples") -> list:
    """
    Получает список примеров изображений из Cloudinary
    
    Args:
        folder: Папка с примерами
        
    Returns:
        list: Список URL примеров
    """
    try:
        result = cloudinary.api.resources(
            type="upload",
            prefix=folder,
            max_results=10
        )
        
        examples = []
        for resource in result.get("resources", []):
            examples.append({
                "url": resource.get("secure_url"),
                "public_id": resource.get("public_id"),
                "format": resource.get("format")
            })
        
        return examples
    except Exception as e:
        logger.error(f"Ошибка при получении примеров: {e}")
        return []

