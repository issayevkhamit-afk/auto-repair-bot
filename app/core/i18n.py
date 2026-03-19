TRANSLATIONS = {
    "ru": {
        "draft_estimate": "Черновая смета",
        "confirm": "✅ Подтвердить смету",
        "regenerate": "🔄 Перегенерировать",
        "estimate_ready": "📄 Смета готова:",
        "preliminary_estimate": "Предварительная смета",
        "manual_review_required": "Требуется ручная проверка",
        "labor": "Работы",
        "parts": "Запчасти",
        "total": "Итого",
        "car": "Автомобиль",
        "date": "Дата",
        "phone": "Телефон",
        "address": "Адрес",
        "qty": "Кол-во",
        "price": "Цена",
        "sum": "Сумма",
        "disclaimer_market": "Предварительная оценка по средним ценам рынка. Окончательная стоимость может отличаться.",
        "welcome_shop_created": "Добро пожаловать! Ваш профиль автосервиса автоматически создан. Выберите язык:",
        "choose_language": "Выберите язык / Тілді таңдаңыз:",
        "lang_ru": "🇷🇺 Русский",
        "lang_kz": "🇰🇿 Қазақша",
        "language_set": "Язык установлен на Русский.",
        "record_voice": "Запишите голосовое сообщение или отправьте текст с описанием работ.",
        "admin_contact": "У вас нет прав администратора. Обратитесь к руководству."
    },
    "kz": {
        "draft_estimate": "Алдын ала смета",
        "confirm": "✅ Сметаны растау",
        "regenerate": "🔄 Қайта жасау",
        "estimate_ready": "📄 Смета дайын:",
        "preliminary_estimate": "Алдын ала смета",
        "manual_review_required": "Қолмен тексеру қажет",
        "labor": "Жұмыстар",
        "parts": "Қосалқы бөлшектер",
        "total": "Барлығы",
        "car": "Автомобиль",
        "date": "Күн",
        "phone": "Телефон",
        "address": "Мекенжай",
        "qty": "Саны",
        "price": "Бағасы",
        "sum": "Сомасы",
        "disclaimer_market": "Орташа нарықтық бағалар бойынша алдын ала бағалау. Түпкілікті құны өзгеше болуы мүмкін.",
        "welcome_shop_created": "Қош келдіңіз! Сіздің автосервис профиліңіз автоматты түрде жасалды. Тілді таңдаңыз:",
        "choose_language": "Тілді таңдаңыз / Выберите язык:",
        "lang_ru": "🇷🇺 Русский",
        "lang_kz": "🇰🇿 Қазақша",
        "language_set": "Тіл Қазақша болып орнатылды.",
        "record_voice": "Жұмыс сипаттамасы бар дауыстық хабарлама жазыңыз немесе мәтін жіберіңіз.",
        "admin_contact": "Сізде әкімші құқығы жоқ. Басшылыққа хабарласыңыз."
    }
}

def t(key: str, lang: str = "ru") -> str:
    """Returns the translated string for a given key and language."""
    if lang not in TRANSLATIONS:
        lang = "ru"
    return TRANSLATIONS[lang].get(key, key)
