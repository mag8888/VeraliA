"""
Сервис для извлечения данных Instagram профиля напрямую из HTML
"""
import os
import logging
import json
import re
from playwright.async_api import async_playwright
import asyncio

logger = logging.getLogger(__name__)


class InstagramProfileScraper:
    """Сервис для извлечения данных Instagram профиля из HTML"""
    
    def __init__(self):
        pass
    
    async def scrape_profile_data(self, username: str) -> dict:
        """
        Извлекает данные профиля Instagram напрямую из HTML страницы
        
        Args:
            username: Username Instagram профиля (без @)
            
        Returns:
            dict: Словарь с данными профиля
        """
        try:
            # Убираем @ если есть
            username = username.lstrip('@')
            
            # URL профиля Instagram
            profile_url = f"https://www.instagram.com/{username}/"
            
            logger.info(f"Извлечение данных профиля: {username}")
            
            async with async_playwright() as p:
                # Запускаем браузер
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = await context.new_page()
                
                try:
                    # Переходим на страницу профиля
                    await page.goto(profile_url, wait_until='networkidle', timeout=30000)
                    
                    # Ждем загрузки контента
                    await asyncio.sleep(3)
                    
                    # Пытаемся извлечь данные из JSON в HTML
                    data = await self._extract_from_page_data(page, username)
                    
                    # Если не получилось через JSON, пытаемся через DOM
                    if data.get('followers', 0) == 0:
                        logger.info("Попытка извлечения данных через DOM")
                        data = await self._extract_from_dom(page, username)
                    
                    await browser.close()
                    
                    logger.info(f"Данные извлечены для {username}: followers={data.get('followers')}, posts={data.get('posts_count')}")
                    return data
                    
                except Exception as e:
                    logger.error(f"Ошибка при извлечении данных: {e}")
                    await browser.close()
                    raise
                    
        except Exception as e:
            logger.error(f"Ошибка в scrape_profile_data: {e}")
            raise
    
    async def _extract_from_page_data(self, page, username: str) -> dict:
        """
        Извлекает данные из JSON данных, встроенных в страницу Instagram
        """
        data = {
            'followers': 0,
            'following': 0,
            'posts_count': 0,
            'bio': None,
            'engagement_rate': None
        }
        
        try:
            # Instagram хранит данные в window._sharedData или в script тегах
            # Пытаемся извлечь JSON данные из страницы
            page_data = await page.evaluate("""
                () => {
                    // Ищем данные в window._sharedData
                    if (window._sharedData) {
                        return window._sharedData;
                    }
                    
                    // Ищем данные в script тегах с type="application/json"
                    const scripts = document.querySelectorAll('script[type="application/json"]');
                    for (let script of scripts) {
                        try {
                            const jsonData = JSON.parse(script.textContent);
                            if (jsonData.entry_data || jsonData.require) {
                                return jsonData;
                            }
                        } catch(e) {}
                    }
                    
                    // Ищем данные в window.__additionalDataLoaded
                    if (window.__additionalDataLoaded) {
                        return window.__additionalDataLoaded;
                    }
                    
                    return null;
                }
            """)
            
            if page_data:
                # Парсим структуру данных Instagram
                data = self._parse_instagram_json(page_data, username)
            
        except Exception as e:
            logger.debug(f"Не удалось извлечь данные из JSON: {e}")
        
        return data
    
    def _parse_instagram_json(self, json_data: dict, username: str) -> dict:
        """
        Парсит JSON данные Instagram и извлекает информацию о профиле
        """
        data = {
            'followers': 0,
            'following': 0,
            'posts_count': 0,
            'bio': None,
            'engagement_rate': None
        }
        
        try:
            # Различные структуры данных Instagram
            profile_data = None
            
            # Вариант 1: entry_data.ProfilePage
            if 'entry_data' in json_data and 'ProfilePage' in json_data['entry_data']:
                pages = json_data['entry_data']['ProfilePage']
                if pages and len(pages) > 0:
                    profile_data = pages[0].get('graphql', {}).get('user', {})
            
            # Вариант 2: require
            elif 'require' in json_data:
                # Instagram использует модульную структуру
                # Пытаемся найти данные пользователя
                for key, value in json_data.get('require', {}).items():
                    if isinstance(value, dict) and 'user' in value:
                        profile_data = value['user']
                        break
            
            # Вариант 3: Прямой доступ к данным
            elif 'graphql' in json_data and 'user' in json_data['graphql']:
                profile_data = json_data['graphql']['user']
            
            if profile_data:
                # Извлекаем данные
                data['followers'] = profile_data.get('edge_followed_by', {}).get('count', 0)
                data['following'] = profile_data.get('edge_follow', {}).get('count', 0)
                data['posts_count'] = profile_data.get('edge_owner_to_timeline_media', {}).get('count', 0)
                data['bio'] = profile_data.get('biography', '')
                
                logger.info(f"Данные извлечены из JSON: followers={data['followers']}, posts={data['posts_count']}")
        
        except Exception as e:
            logger.debug(f"Ошибка парсинга JSON: {e}")
        
        return data
    
    async def _extract_from_dom(self, page, username: str) -> dict:
        """
        Извлекает данные напрямую из DOM элементов страницы
        """
        data = {
            'followers': 0,
            'following': 0,
            'posts_count': 0,
            'bio': None,
            'engagement_rate': None
        }
        
        try:
            # Извлекаем данные из DOM
            dom_data = await page.evaluate("""
                () => {
                    const data = {
                        followers: 0,
                        following: 0,
                        posts_count: 0,
                        bio: null
                    };
                    
                    // Ищем метрики в различных селекторах
                    // Instagram использует разные селекторы в зависимости от версии
                    
                    // Селекторы для подписчиков
                    const followersSelectors = [
                        'a[href*="/followers/"] span',
                        'span:contains("followers")',
                        '[data-testid="followers"]',
                        'li:has(a[href*="/followers/"]) span'
                    ];
                    
                    // Селекторы для постов
                    const postsSelectors = [
                        'span:contains("posts")',
                        '[data-testid="posts"]',
                        'li:has(span:contains("posts")) span'
                    ];
                    
                    // Селекторы для подписок
                    const followingSelectors = [
                        'a[href*="/following/"] span',
                        'span:contains("following")',
                        '[data-testid="following"]'
                    ];
                    
                    // Ищем биографию
                    const bioElement = document.querySelector('h1 + div, [data-testid="user-bio"]');
                    if (bioElement) {
                        data.bio = bioElement.textContent.trim();
                    }
                    
                    // Пытаемся найти все числа на странице и сопоставить их
                    const allText = document.body.innerText;
                    
                    // Ищем паттерны типа "102K followers" или "44,930 followers"
                    const followersMatch = allText.match(/(\\d+[.,]?\\d*)\\s*(K|тыс|thousand|тысяч)?\\s*(followers|подписчик)/i);
                    if (followersMatch) {
                        let num = parseFloat(followersMatch[1].replace(',', ''));
                        if (followersMatch[2] && ['K', 'тыс', 'thousand', 'тысяч'].includes(followersMatch[2])) {
                            num *= 1000;
                        }
                        data.followers = Math.floor(num);
                    }
                    
                    // Ищем посты
                    const postsMatch = allText.match(/(\\d+[.,]?\\d*)\\s*(posts|публикац|публикаций)/i);
                    if (postsMatch) {
                        data.posts_count = parseInt(postsMatch[1].replace(',', ''));
                    }
                    
                    // Ищем подписки
                    const followingMatch = allText.match(/(\\d+[.,]?\\d*)\\s*(following|подписк)/i);
                    if (followingMatch) {
                        let num = parseFloat(followingMatch[1].replace(',', ''));
                        if (followingMatch[2] && ['K', 'тыс'].includes(followingMatch[2])) {
                            num *= 1000;
                        }
                        data.following = Math.floor(num);
                    }
                    
                    return data;
                }
            """)
            
            if dom_data:
                data.update(dom_data)
                logger.info(f"Данные извлечены из DOM: followers={data['followers']}, posts={data['posts_count']}")
        
        except Exception as e:
            logger.debug(f"Ошибка извлечения из DOM: {e}")
        
        return data

