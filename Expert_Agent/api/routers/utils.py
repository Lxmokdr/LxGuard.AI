from fastapi import APIRouter
from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator

router = APIRouter(prefix="/api/utils", tags=["utils"])

def detect_language(text: str) -> str:
    try:
        lang = detect(text)
        return lang if lang in ['en', 'fr'] else 'en'
    except LangDetectException:
        return 'en'

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    if source_lang == target_lang:
        return text
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

@router.get("/detect")
async def api_detect_language(text: str):
    return {"language": detect_language(text)}

@router.get("/health")
async def health_check():
    return {"status": "online"}
