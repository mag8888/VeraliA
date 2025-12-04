import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import aiofiles
from dotenv import load_dotenv
from database import init_db, get_db, InstagramProfile
from image_parser import InstagramScreenshotParser
from screenshot_service import InstagramScreenshotService
from gpt_analyzer import GPTAnalyzer

load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация парсера
parser = InstagramScreenshotParser()

# Инициализация сервиса скриншотов
screenshot_service = InstagramScreenshotService()

# GPT анализатор будет инициализирован при первом использовании
gpt_analyzer = None

def get_gpt_analyzer():
    """Ленивая инициализация GPT анализатора"""
    global gpt_analyzer
    if gpt_analyzer is None:
        try:
            gpt_analyzer = GPTAnalyzer()
        except Exception as e:
            logger.error(f"Ошибка инициализации GPT анализатора: {e}")
            gpt_analyzer = None
    return gpt_analyzer

# Конфигурация
PORT = int(os.getenv("PORT", 8001))
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    logger.info("Database initialized")
    yield
    # Shutdown (если нужно что-то сделать при остановке)


# FastAPI приложение
app = FastAPI(title="Verali Parsing Server", lifespan=lifespan)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Verali Parsing Server",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/analyze")
async def analyze_instagram(
    username: str = Form(...),
    screenshot: UploadFile = File(...),
    screenshot_type: str = Form(None),  # Тип скриншота: main_page или stats
    db: Session = Depends(get_db)
):
    """
    Анализирует скриншот Instagram профиля и сохраняет данные в базу
    
    Args:
        username: Username Instagram пользователя
        screenshot: Файл скриншота статистики
        
    Returns:
        dict: Результат анализа
    """
    try:
        # Сохраняем загруженный файл
        screenshot_type_suffix = f"_{screenshot_type}" if screenshot_type else ""
        file_path = os.path.join(UPLOAD_DIR, f"{username}{screenshot_type_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await screenshot.read()
            await f.write(content)
        
        logger.info(f"Файл сохранен: {file_path}")
        
        # Парсим изображение
        try:
            parsed_data = parser.parse_screenshot(file_path)
            logger.info(f"Данные извлечены: {parsed_data}")
        except Exception as e:
            logger.error(f"Ошибка при парсинге: {e}")
            # Если парсинг не удался, создаем запись с базовыми данными
            parsed_data = {
                'followers': 0,
                'following': 0,
                'posts_count': 0,
                'bio': None,
                'engagement_rate': None
            }
        
        # Сохраняем или обновляем данные в базе
        profile = db.query(InstagramProfile).filter(
            InstagramProfile.username == username
        ).first()
        
        if profile:
            # Обновляем существующий профиль
            profile.followers = parsed_data.get('followers', 0)
            profile.following = parsed_data.get('following', 0)
            profile.posts_count = parsed_data.get('posts_count', 0)
            profile.bio = parsed_data.get('bio')
            profile.engagement_rate = parsed_data.get('engagement_rate')
            profile.screenshot_path = file_path
            # Сохраняем дополнительные данные из скриншота
            profile.views = parsed_data.get('views', 0)
            profile.interactions = parsed_data.get('interactions', 0)
            profile.new_followers = parsed_data.get('new_followers', 0)
            profile.messages = parsed_data.get('messages', 0)
            profile.shares = parsed_data.get('shares', 0)
            profile.analyzed_at = datetime.utcnow()
            profile.updated_at = datetime.utcnow()
        else:
            # Создаем новый профиль
            profile = InstagramProfile(
                username=username,
                followers=parsed_data.get('followers', 0),
                following=parsed_data.get('following', 0),
                posts_count=parsed_data.get('posts_count', 0),
                bio=parsed_data.get('bio'),
                engagement_rate=parsed_data.get('engagement_rate'),
                screenshot_path=file_path,
                # Сохраняем дополнительные данные из скриншота
                views=parsed_data.get('views', 0),
                interactions=parsed_data.get('interactions', 0),
                new_followers=parsed_data.get('new_followers', 0),
                messages=parsed_data.get('messages', 0),
                shares=parsed_data.get('shares', 0),
                analyzed_at=datetime.utcnow()
            )
            db.add(profile)
        
        try:
            db.commit()
            db.refresh(profile)
            
            # Генерируем детальный отчет
            profile_dict = {
                "username": profile.username,
                "followers": profile.followers,
                "following": profile.following,
                "posts_count": profile.posts_count,
                "bio": profile.bio,
                "engagement_rate": profile.engagement_rate,
                "analyzed_at": profile.analyzed_at.isoformat()
            }
            
            # Дополнительные данные из скриншота
            screenshot_data = {
                "views": parsed_data.get('views', 0),
                "interactions": parsed_data.get('interactions', 0),
                "new_followers": parsed_data.get('new_followers', 0),
                "messages": parsed_data.get('messages', 0),
                "shares": parsed_data.get('shares', 0)
            }
            
            # Генерируем отчет с помощью GPT (если доступен)
            analyzer = get_gpt_analyzer()
            if analyzer and analyzer.client:
                try:
                    gpt_reports = analyzer.generate_report(profile_dict, screenshot_data)
                except Exception as e:
                    logger.error(f"Ошибка генерации GPT отчета: {e}")
                    gpt_reports = {"ru": "", "en": ""}
            else:
                gpt_reports = {"ru": "", "en": ""}
            
            # Сохраняем GPT отчеты в базу
            if gpt_reports.get("ru") or gpt_reports.get("en"):
                profile.report_ru = gpt_reports.get("ru")
                profile.report_en = gpt_reports.get("en")
                profile.report_generated_at = datetime.utcnow()
                db.commit()
                db.refresh(profile)
                logger.info("GPT отчеты сохранены в базу данных")
            else:
                logger.warning(f"GPT отчет не был сгенерирован для {username}. Проверьте OPENAI_API_KEY.")
            
            return {
                "status": "success",
                "message": "Данные успешно сохранены",
                "data": profile_dict,
                "screenshot_data": screenshot_data,
                "report": {
                    "ru": gpt_reports.get("ru") or "",
                    "en": gpt_reports.get("en") or ""
                }
            }
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Ошибка целостности данных: {e}")
            raise HTTPException(status_code=400, detail="Ошибка при сохранении данных")
            
    except Exception as e:
        logger.error(f"Ошибка при анализе: {e}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")


@app.post("/api/screenshot/{username}")
async def create_screenshot(username: str, db: Session = Depends(get_db)):
    """
    Создает скриншот главной страницы Instagram профиля
    
    Args:
        username: Username Instagram профиля
        
    Returns:
        dict: Результат создания скриншота
    """
    try:
        # Извлекаем username из текста (может быть URL)
        if 'instagram.com' in username:
            import re
            match = re.search(r'instagram\.com/([^/?&#]+)', username)
            if match:
                username = match.group(1)
        
        username = username.lstrip('@').strip()
        
        logger.info(f"Создание скриншота для: {username}")
        
        # Создаем скриншот
        screenshot_path = await screenshot_service.take_profile_screenshot(username)
        
        # Парсим скриншот
        parsed_data = parser.parse_screenshot(screenshot_path)
        
        # Сохраняем в базу данных
        try:
            profile = db.query(InstagramProfile).filter(
                InstagramProfile.username == username
            ).first()
            
            if profile:
                # Обновляем существующий профиль
                profile.followers = parsed_data.get('followers', 0)
                profile.following = parsed_data.get('following', 0)
                profile.posts_count = parsed_data.get('posts_count', 0)
                profile.bio = parsed_data.get('bio')
                profile.engagement_rate = parsed_data.get('engagement_rate')
                profile.screenshot_path = screenshot_path
                profile.views = parsed_data.get('views', 0)
                profile.interactions = parsed_data.get('interactions', 0)
                profile.new_followers = parsed_data.get('new_followers', 0)
                profile.messages = parsed_data.get('messages', 0)
                profile.shares = parsed_data.get('shares', 0)
                profile.updated_at = datetime.utcnow()
            else:
                # Создаем новый профиль
                profile = InstagramProfile(
                    username=username,
                    followers=parsed_data.get('followers', 0),
                    following=parsed_data.get('following', 0),
                    posts_count=parsed_data.get('posts_count', 0),
                    bio=parsed_data.get('bio'),
                    engagement_rate=parsed_data.get('engagement_rate'),
                    screenshot_path=screenshot_path,
                    views=parsed_data.get('views', 0),
                    interactions=parsed_data.get('interactions', 0),
                    new_followers=parsed_data.get('new_followers', 0),
                    messages=parsed_data.get('messages', 0),
                    shares=parsed_data.get('shares', 0)
                )
                db.add(profile)
            
            db.commit()
            db.refresh(profile)
            
            # Генерируем GPT отчет
            profile_dict = {
                "username": profile.username,
                "followers": profile.followers,
                "following": profile.following,
                "posts_count": profile.posts_count,
                "bio": profile.bio,
                "engagement_rate": profile.engagement_rate
            }
            
            screenshot_data = {
                "views": profile.views,
                "interactions": profile.interactions,
                "new_followers": profile.new_followers,
                "messages": profile.messages,
                "shares": profile.shares
            }
            
            # Генерируем отчет с помощью GPT
            analyzer = get_gpt_analyzer()
            if analyzer and analyzer.client:
                try:
                    gpt_reports = analyzer.generate_report(profile_dict, screenshot_data)
                except Exception as e:
                    logger.error(f"Ошибка генерации GPT отчета: {e}")
                    gpt_reports = {"ru": "", "en": ""}
            else:
                gpt_reports = {"ru": "", "en": ""}
            
            # Сохраняем GPT отчеты в базу
            if gpt_reports.get("ru") or gpt_reports.get("en"):
                profile.report_ru = gpt_reports.get("ru")
                profile.report_en = gpt_reports.get("en")
                profile.report_generated_at = datetime.utcnow()
                db.commit()
                db.refresh(profile)
            
            return {
                "success": True,
                "message": "Скриншот создан и данные сохранены",
                "screenshot_path": screenshot_path,
                "data": {
                    "username": profile.username,
                    "followers": profile.followers,
                    "following": profile.following,
                    "posts_count": profile.posts_count,
                    "bio": profile.bio,
                    "engagement_rate": profile.engagement_rate,
                    "analyzed_at": profile.analyzed_at.isoformat() if profile.analyzed_at else None,
                    "report": {
                        "ru": gpt_reports.get("ru") or "",
                        "en": gpt_reports.get("en") or ""
                    },
                    "report_generated_at": profile.report_generated_at.isoformat() if profile.report_generated_at else None
                }
            }
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Ошибка при сохранении в БД: {e}")
            raise HTTPException(status_code=400, detail="Ошибка при сохранении данных")
            
    except Exception as e:
        logger.error(f"Ошибка при создании скриншота: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@app.get("/api/data/{username}")
async def get_user_data(username: str, db: Session = Depends(get_db)):
    """
    Получает данные пользователя из базы данных
    
    Args:
        username: Username Instagram пользователя
        
    Returns:
        dict: Данные пользователя
    """
    profile = db.query(InstagramProfile).filter(
        InstagramProfile.username == username
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile_dict = {
        "username": profile.username,
        "followers": profile.followers,
        "following": profile.following,
        "posts_count": profile.posts_count,
        "bio": profile.bio,
        "engagement_rate": profile.engagement_rate,
        "analyzed_at": profile.analyzed_at.isoformat() if profile.analyzed_at else None,
        "created_at": profile.created_at.isoformat() if profile.created_at else None,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
    }
    
    # Добавляем дополнительные данные из базы
    screenshot_data = {
        "views": profile.views,
        "interactions": profile.interactions,
        "new_followers": profile.new_followers,
        "messages": profile.messages,
        "shares": profile.shares
    }
    profile_dict["screenshot_data"] = screenshot_data
    
    # Добавляем отчеты из базы (если есть)
    if profile.report_ru or profile.report_en:
        profile_dict["report"] = {
            "ru": profile.report_ru or "",
            "en": profile.report_en or ""
        }
        profile_dict["report_generated_at"] = profile.report_generated_at.isoformat() if profile.report_generated_at else None
    else:
        # Генерируем отчет, если его нет в базе
        try:
            # Пытаемся сгенерировать через GPT
            analyzer = get_gpt_analyzer()
            if analyzer and analyzer.client:
                try:
                    gpt_reports = analyzer.generate_report(profile_dict, screenshot_data)
                except Exception as e:
                    logger.error(f"Ошибка генерации GPT отчета: {e}")
                    gpt_reports = {"ru": "", "en": ""}
            else:
                gpt_reports = {"ru": "", "en": ""}
            
            if gpt_reports.get("ru") or gpt_reports.get("en"):
                # Сохраняем в базу
                profile.report_ru = gpt_reports.get("ru")
                profile.report_en = gpt_reports.get("en")
                profile.report_generated_at = datetime.utcnow()
                db.commit()
                db.refresh(profile)
                
                profile_dict["report"] = {
                    "ru": gpt_reports.get("ru") or "",
                    "en": gpt_reports.get("en") or ""
                }
                profile_dict["report_generated_at"] = profile.report_generated_at.isoformat()
            else:
                # GPT недоступен - возвращаем пустой отчет
                logger.warning(f"GPT недоступен для генерации отчета для {username}")
                profile_dict["report"] = {
                    "ru": "",
                    "en": ""
                }
        except Exception as e:
            logger.error(f"Ошибка генерации отчета: {e}")
            profile_dict["report"] = {"ru": "", "en": ""}
    
    return profile_dict


@app.get("/api/users")
async def get_all_users(db: Session = Depends(get_db)):
    """
    Получает список всех пользователей
    
    Returns:
        dict: Список всех пользователей с дополнительными данными
    """
    profiles = db.query(InstagramProfile).all()
    
    return {
        "users": [
            {
                "username": p.username,
                "followers": p.followers,
                "following": p.following,
                "posts_count": p.posts_count,
                "bio": p.bio,
                "engagement_rate": p.engagement_rate,
                "views": p.views,
                "interactions": p.interactions,
                "new_followers": p.new_followers,
                "messages": p.messages,
                "shares": p.shares,
                "analyzed_at": p.analyzed_at.isoformat() if p.analyzed_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None
            }
            for p in profiles
        ]
    }


@app.delete("/api/data/{username}")
async def delete_user_data(username: str, db: Session = Depends(get_db)):
    """
    Удаляет данные пользователя из базы данных
    
    Args:
        username: Username Instagram пользователя
        
    Returns:
        dict: Результат удаления
    """
    profile = db.query(InstagramProfile).filter(
        InstagramProfile.username == username
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Удаляем файл скриншота, если он существует
    if profile.screenshot_path and os.path.exists(profile.screenshot_path):
        try:
            os.remove(profile.screenshot_path)
        except Exception as e:
            logger.warning(f"Не удалось удалить файл {profile.screenshot_path}: {e}")
    
    db.delete(profile)
    db.commit()
    
    return {"status": "success", "message": f"Данные пользователя {username} удалены"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

