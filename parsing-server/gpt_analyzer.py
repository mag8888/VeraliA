"""
Модуль для анализа Instagram профилей с помощью GPT
"""
import os
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
import json

logger = logging.getLogger(__name__)


class GPTAnalyzer:
    """Класс для анализа Instagram профилей с помощью GPT"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY не установлен. GPT анализ будет недоступен.")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
        
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Можно использовать gpt-4o-mini или gpt-4
    
    def generate_report(self, profile_data: Dict[str, Any], screenshot_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Генерирует отчет на русском и английском языках с помощью GPT
        
        Args:
            profile_data: Основные данные профиля
            screenshot_data: Дополнительные данные из скриншота
            
        Returns:
            dict: {"ru": "отчет на русском", "en": "отчет на английском"}
        """
        if not self.client:
            logger.error("GPT клиент не инициализирован. Проверьте OPENAI_API_KEY.")
            return {"ru": "", "en": ""}
        
        # Формируем промпт с данными
        prompt = self._build_prompt(profile_data, screenshot_data)
        
        try:
            # Генерируем отчет на английском (оригинал)
            response_en = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Instagram account analyst specializing in influencer marketing and brand partnerships. Generate detailed, professional reports for advertisers and brands."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            report_en = response_en.choices[0].message.content.strip()
            
            # Переводим на русский
            response_ru = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional translator. Translate the following Instagram account analysis report from English to Russian. Maintain the structure, formatting, and professional tone. Keep all numbers, metrics, and technical terms intact."
                    },
                    {
                        "role": "user",
                        "content": f"Translate this report to Russian:\n\n{report_en}"
                    }
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            report_ru = response_ru.choices[0].message.content.strip()
            
            logger.info("GPT отчет успешно сгенерирован")
            return {
                "ru": report_ru,
                "en": report_en
            }
            
        except Exception as e:
            logger.error(f"Ошибка при генерации GPT отчета: {e}")
            return {"ru": "", "en": ""}
    
    def _build_prompt(self, profile_data: Dict[str, Any], screenshot_data: Dict[str, Any]) -> str:
        """
        Строит промпт для GPT на основе данных профиля
        
        Args:
            profile_data: Данные профиля
            screenshot_data: Данные из скриншота
            
        Returns:
            str: Промпт для GPT
        """
        followers = profile_data.get('followers', 0)
        posts_count = profile_data.get('posts_count', 0)
        bio = profile_data.get('bio', 'Not specified')
        views = screenshot_data.get('views', 0)
        interactions = screenshot_data.get('interactions', 0)
        new_followers = screenshot_data.get('new_followers', 0)
        messages = screenshot_data.get('messages', 0)
        shares = screenshot_data.get('shares', 0)
        
        prompt = f"""Analyze the Instagram account based on the provided data.

Generate a structured report as if you are preparing it for advertisers, brands, or an influencer-marketing platform.

Here are the input details:

– Followers: {followers:,}
– Number of posts: {posts_count:,}
– Bio / positioning: {bio}
– Views in the last 30 days: {views:,}
– Interactions in the last 30 days (likes + comments + saves + reactions): {interactions:,}
– New followers last month: {new_followers:,}
– Number of messages: {messages:,}
– Number of shares (content shared): {shares:,}

Produce the analysis in the following structure:

1. OVERALL ACCOUNT METRICS & PERFORMANCE

Include:
– General health of the account
– Engagement Rate (ER) calculation
– Growth dynamics
– Evaluation of audience activity
– Strength of the account compared to industry averages

2. AUDIENCE & CONTENT ANALYSIS

Identify:
– Niche/theme
– Content type and style
– Expected demographics
– Audience interests
– Level of trust & loyalty
– Emotional tone in comments
– What types of people the content attracts

3. POTENTIAL PARTNERS & ADVERTISERS

Break down by categories:
– Brands
– Services
– Digital platforms
– Wellness/self-development products
– Relevant commercial niches
– Potential collaborations and sponsorship fits

4. COMPLIMENTS — STRONG POINTS OF THE ACCOUNT

Highlight what is already working well:
– Style
– Expertise
– Visual appeal
– Messaging clarity
– Content formats that perform best
– Any unique selling points

5. SPECIFIC RECOMMENDATIONS FOR IMPROVEMENT

Provide actionable suggestions for:
– Bio optimization
– Content strategy
– Reels
– Stories
– Conversion flow
– Increasing trust and authority
– Improving highlights, structure, visual identity
– Increasing reach & engagement

6. ADDITIONAL INSIGHTS (if possible)

Include:
– Reels ideas
– New content rubrics
– Suggested storytelling angles
– How to increase ER
– How to boost sales via Instagram
– Any growth accelerators or strategic opportunities

Generate a comprehensive, professional report that would be valuable for brands considering partnerships with this account."""
        
        return prompt

