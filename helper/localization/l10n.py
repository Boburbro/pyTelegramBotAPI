import json
import os
import logging

logger = logging.getLogger(__name__)


class L10n:
    def __init__(self, lang_code: str = "uz"):
        self.translations = {}
        self.lang_code = lang_code
        self.load_translations()
        self.missing_keys = set()

    def load_translations(self):
        try:
            file_path = f"helper/localization/locales/{self.lang_code}.json"
            with open(file_path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
            logger.info(f"Translations loaded for language: {self.lang_code}")
        except FileNotFoundError:
            logger.error(f"Translation file not found for {self.lang_code}")
            self.translations = {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in translation file for {self.lang_code}: {e}")
            self.translations = {}
        except Exception as e:
            logger.error(f"Error loading translations for {self.lang_code}: {e}")
            self.translations = {}

    def t(self, key, **kwargs):
        """
        Tarjima kalitini qaytaradi va formatlashtiradi.
        Agar kalit topilmasa, missing_keys ro'yxatiga qo'shadi.
        """
        # Kalit mavjudligini tekshirish
        if key not in self.translations:
            logger.warning(f"Missing translation key: {key}")
            self.missing_keys.add(key)
            return key

        try:
            text = self.translations[key]
            return text.format(**kwargs) if kwargs else text
        except KeyError as e:
            logger.error(f"Missing format parameter for key '{key}': {e}")
            return self.translations[key]  # Format qilmasdan qaytaramiz
        except Exception as e:
            logger.error(f"Error formatting key '{key}': {e}")
            return self.translations[key]

    def get_missing_keys(self):
        """Topilmagan kalitlar ro'yxatini qaytaradi"""
        return list(self.missing_keys)

    def clear_missing_keys(self):
        """Topilmagan kalitlar ro'yxatini tozalaydi"""
        self.missing_keys.clear()

    def log_missing_keys(self):
        """Topilmagan kalitlarni log ga yozadi"""
        if self.missing_keys:
            logger.warning(f"Missing translation keys: {', '.join(self.missing_keys)}")
        else:
            logger.info("No missing translation keys")
