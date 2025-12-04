"""
Сервис для автоматического создания скриншотов Instagram профилей
"""
import os
import logging
from playwright.async_api import async_playwright
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class InstagramScreenshotService:
    """Сервис для создания скриншотов Instagram профилей"""
    
    def __init__(self):
        self.screenshots_dir = "screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
    
    async def take_profile_screenshot(self, username: str) -> str:
        """
        Создает скриншот главной страницы профиля Instagram
        
        Args:
            username: Username Instagram профиля (без @)
            
        Returns:
            str: Путь к сохраненному скриншоту
        """
        try:
            # Убираем @ если есть
            username = username.lstrip('@')
            
            # URL профиля Instagram
            profile_url = f"https://www.instagram.com/{username}/"
            
            logger.info(f"Создание скриншота для профиля: {username}")
            
            async with async_playwright() as p:
                # Запускаем браузер
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 390, 'height': 844},  # Размер мобильного экрана
                    user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
                )
                page = await context.new_page()
                
                try:
                    # Переходим на страницу профиля
                    await page.goto(profile_url, wait_until='networkidle', timeout=30000)
                    
                    # Ждем загрузки контента
                    await asyncio.sleep(3)
                    
                    # Прокручиваем страницу, чтобы загрузить весь контент
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(2)
                    
                    # Возвращаемся наверх
                    await page.evaluate("window.scrollTo(0, 0)")
                    await asyncio.sleep(1)
                    
                    # Создаем скриншот
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    screenshot_path = os.path.join(
                        self.screenshots_dir,
                        f"{username}_profile_{timestamp}.png"
                    )
                    
                    await page.screenshot(
                        path=screenshot_path,
                        full_page=True,
                        timeout=10000
                    )
                    
                    logger.info(f"Скриншот сохранен: {screenshot_path}")
                    
                    await browser.close()
                    
                    return screenshot_path
                    
                except Exception as e:
                    logger.error(f"Ошибка при создании скриншота: {e}")
                    await browser.close()
                    raise
                    
        except Exception as e:
            logger.error(f"Ошибка в take_profile_screenshot: {e}")
            raise
    
    async def take_professional_panel_screenshot(self, username: str) -> str:
        """
        Создает скриншот профессиональной панели Instagram (требует авторизации)
        
        Args:
            username: Username Instagram профиля
            
        Returns:
            str: Путь к сохраненному скриншоту
        """
        # Для профессиональной панели требуется авторизация
        # Это более сложная задача, так как нужен доступ к аккаунту
        raise NotImplementedError("Профессиональная панель требует авторизации в Instagram")

