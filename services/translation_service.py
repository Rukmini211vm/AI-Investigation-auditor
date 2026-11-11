import re
from typing import Dict, Any

LANGUAGES = {
    "en": "English",
    "kn": "ಕನ್ನಡ (Kannada)",
    "hi": "हिन्दी (Hindi)",
    "ta": "தமிழ் (Tamil)",
    "te": "తెలుగు (Telugu)",
    "ml": "മലയാളം (Malayalam)",
    "bn": "বাংলা (Bengali)",
    "mr": "मराठी (Marathi)",
    "es": "Español (Spanish)",
    "fr": "Français (French)"
}

TRANSLATION_MAP = {
    "kn": {
        "AI Investigation Auditor": "ಎಐ ತನಿಖಾ ಲೆಕ್ಕಪರಿಶೋಧಕ (AI Investigation Auditor)",
        "AI-Assisted Second-Level Audit for Investigation Records": "ತನಿಖಾ ದಾಖಲೆಗಳಿಗಾಗಿ ಎಐ-ಸಹಾಯದ ಎರಡನೇ ಹಂತದ ಆಡಿಟ್",
        "Potential Inconsistency Detected": "ಸಂಭಾವ್ಯ ಅಸಂಗತತೆ ಪತ್ತೆಯಾಗಿದೆ",
        "Requires Human Review": "ಮಾನವ ಪರಿಶೀಲನೆ ಅಗತ್ಯವಿದೆ",
        "Timeline Conflict": "ಸಮಯರೇಖೆ ಸಂಘರ್ಷ",
        "Missing Evidence Reference": "ಕಾಣೆಯಾದ ಪುರಾವೆ ಉಲ್ಲೇಖ",
        "Chain of Custody Documentation Gap": "ಕಸ್ಟಡಿ ಸರಪಳಿ ದಾಖಲಾತಿ ಅಂತರ",
        "Incomplete Investigative Record": "ಅಪೂರ್ಣ ತನಿಖಾ ದಾಖಲೆ",
        "Records appear consistent based on the available data": "ಲಭ್ಯವಿರುವ ದತ್ತಾಂಶದ ಆಧಾರದ ಮೇಲೆ ದಾಖಲೆಗಳು ಸ್ಥಿರವಾಗಿವೆ",
        "Run AI Audit": "ಎಐ ಆಡಿಟ್ ಚಲಾಯಿಸಿ",
        "Audit Findings": "ಆಡಿಟ್ ಸಂಶೋಧನೆಗಳು",
        "Consistency Score": "ಸ್ಥಿರತೆಯ ಅಂಕ",
        "Mark Reviewed": "ಪರಿಶೀಲಿಸಲಾಗಿದೆ ಎಂದು ಗುರುತಿಸಿ",
        "Needs Further Investigation": "ಹೆಚ್ಚಿನ ತನಿಖೆ ಅಗತ್ಯವಿದೆ",
        "False Positive": "ತಪ್ಪು ಸಂಕೇತ (False Positive)",
        "Audit Report": "ಆಡಿಟ್ ವರದಿ"
    },
    "hi": {
        "AI Investigation Auditor": "एआई जांच लेखापरीक्षक (AI Investigation Auditor)",
        "AI-Assisted Second-Level Audit for Investigation Records": "जांच अभिलेखों के लिए एआई-सहायक द्वितीय-स्तरीय ऑडिट",
        "Potential Inconsistency Detected": "संभावित विसंगति का पता चला",
        "Requires Human Review": "मानव समीक्षा आवश्यक है",
        "Timeline Conflict": "समय-सीमा में विरोधाभास",
        "Missing Evidence Reference": "लापता साक्ष्य संदर्भ",
        "Chain of Custody Documentation Gap": "हिरासत श्रृंखला (Chain of Custody) दस्तावेज़ अंतर",
        "Incomplete Investigative Record": "अपूर्ण जांच अभिलेख",
        "Records appear consistent based on the available data": "उपलब्ध आंकड़ों के आधार पर रिकॉर्ड सुसंगत प्रतीत होते हैं",
        "Run AI Audit": "एआई ऑडिट चलाएं",
        "Audit Findings": "ऑडिट निष्कर्ष",
        "Consistency Score": "संगतता स्कोर",
        "Mark Reviewed": "समीक्षित चिह्नित करें",
        "Needs Further Investigation": "अतिरिक्त जांच आवश्यक",
        "False Positive": "गलत चेतावनी (False Positive)",
        "Audit Report": "ऑडिट रिपोर्ट"
    },
    "ta": {
        "AI Investigation Auditor": "AI புலனாய்வு தணிக்கையாளர் (AI Investigation Auditor)",
        "AI-Assisted Second-Level Audit for Investigation Records": "புலனாய்வு ஆவணங்களுக்கான இரண்டாம் நிலை AI தணிக்கை",
        "Potential Inconsistency Detected": "சாத்தியமான முரண்பாடு கண்டறியப்பட்டது",
        "Requires Human Review": "மனித மறுஆய்வு தேவைப்படுகிறது",
        "Timeline Conflict": "காலவரிசை முரண்பாடு",
        "Missing Evidence Reference": "விடுபட்ட ஆதாரக் குறிப்பு",
        "Chain of Custody Documentation Gap": "பாதுகாப்பு சங்கிலி ஆவண இடைவெளி",
        "Incomplete Investigative Record": "முழுமையடையாத புலனாய்வு பதிவு",
        "Records appear consistent based on the available data": "கிடைக்கக்கூடிய தரவுகளின் அடிப்படையில் பதிவுகள் சீராக உள்ளன",
        "Run AI Audit": "AI தணிக்கையை இயக்கவும்",
        "Audit Findings": "தணிக்கை முடிவுகள்",
        "Consistency Score": "நிலைத்தன்மை மதிப்பெண்",
        "Mark Reviewed": "மறுஆய்வு செய்யப்பட்டது",
        "Needs Further Investigation": "கூடுதல் விசாரணை தேவை",
        "False Positive": "தவறான எச்சரிக்கை",
        "Audit Report": "தணிக்கை அறிக்கை"
    },
    "te": {
        "AI Investigation Auditor": "AI దర్యాప్తు ఆడిటర్ (AI Investigation Auditor)",
        "AI-Assisted Second-Level Audit for Investigation Records": "దర్యాప్తు రికార్డుల కోసం AI రెండవ స్థాయి ఆడిట్",
        "Potential Inconsistency Detected": "సంభావ్య అసమానత కనుగొనబడింది",
        "Requires Human Review": "మానవ సమీక్ష అవసరం",
        "Timeline Conflict": "కాలక్రమ వివాదం",
        "Missing Evidence Reference": "తప్పిపోయిన సాక్ష్యాల సూచన",
        "Chain of Custody Documentation Gap": "కస్టడీ రికార్డుల అంతరం",
        "Incomplete Investigative Record": "అసంపూర్ణ దర్యాప్తు రికార్డు",
        "Records appear consistent based on the available data": "అందుబాటులో ఉన్న సమాచారం ఆధారంగా రికార్డులు స్థిరంగా ఉన్నాయి",
        "Run AI Audit": "AI ఆడిట్ ప్రారంభించండి",
        "Audit Findings": "ఆడిట్ ఫలితాలు",
        "Consistency Score": "స్థిరత్వ స్కోరు",
        "Mark Reviewed": "సమీక్షించినట్లు గుర్తించండి",
        "Needs Further Investigation": "మరింత దర్యాప్తు అవసరం",
        "False Positive": "తప్పుడు అలారం",
        "Audit Report": "ఆడిట్ నివేదిక"
    },
    "ml": {
        "AI Investigation Auditor": "AI അന്വേഷണ ഓഡിറ്റർ (AI Investigation Auditor)",
        "AI-Assisted Second-Level Audit for Investigation Records": "അന്വേഷണ രേഖകൾക്കായുള്ള AI രണ്ടാമത്തെ ലെവൽ ഓഡിറ്റ്",
        "Potential Inconsistency Detected": "പൊരുത്തക്കേട് കണ്ടെത്തി",
        "Requires Human Review": "മനുഷ്യ പരിശോധന ആവശ്യമാണ്",
        "Timeline Conflict": "സമയക്രമത്തിലെ പൊരുത്തക്കേട്",
        "Missing Evidence Reference": "നഷ്ടപ്പെട്ട തെളിവ് പരാമർശം",
        "Chain of Custody Documentation Gap": "കസ്റ്റഡി ചെയിൻ വിടവ്",
        "Incomplete Investigative Record": "അപൂർണ്ണമായ അന്വേഷണ രേഖ",
        "Records appear consistent based on the available data": "രേഖകൾ ലഭ്യമായ വിവരങ്ങളുടെ അടിസ്ഥാനത്തിൽ അനുയോജ്യമാണ്",
        "Run AI Audit": "AI ഓഡിറ്റ് പ്രവർത്തിപ്പിക്കുക",
        "Audit Findings": "ഓഡിറ്റ് കണ്ടെത്തലുകൾ",
        "Consistency Score": "സ്ഥിരത സ്കോർ",
        "Mark Reviewed": "പരിശോധിച്ചതായി അടയാളപ്പെടുത്തുക",
        "Needs Further Investigation": "കൂടുതൽ അന്വേഷണം ആവശ്യമാണ്",
        "False Positive": "തെറ്റായ അലാറം",
        "Audit Report": "ഓഡിറ്റ് റിപ്പോർട്ട്"
    },
    "bn": {
        "AI Investigation Auditor": "এআই তদন্ত অডিটর (AI Investigation Auditor)",
        "AI-Assisted Second-Level Audit for Investigation Records": "তদন্ত রেকর্ডের জন্য এআই দ্বিতীয় স্তরের অডিট",
        "Potential Inconsistency Detected": "সম্ভাব্য অসঙ্গতি সনাক্ত হয়েছে",
        "Requires Human Review": "মানব পর্যালোচনা প্রয়োজন",
        "Timeline Conflict": "সময়রেখার দ্বন্দ্ব",
        "Missing Evidence Reference": "অনুপস্থিত প্রমাণের রেফারেন্স",
        "Chain of Custody Documentation Gap": "হেফাজত শৃঙ্খল ঘাটতি",
        "Incomplete Investigative Record": "অসম্পূর্ণ তদন্ত রেকর্ড",
        "Records appear consistent based on the available data": "উপলব্ধ তথ্যের ভিত্তিতে রেকর্ডগুলি সামঞ্জস্যপূর্ণ",
        "Run AI Audit": "এআই অডিট চালান",
        "Audit Findings": "অডিট ফলাফল",
        "Consistency Score": "ধারাবাহিকতা স্কোর",
        "Mark Reviewed": "পর্যালোচিত চিহ্নিত করুন",
        "Needs Further Investigation": "আরও তদন্ত প্রয়োজন",
        "False Positive": "ভুল সংকেত",
        "Audit Report": "অডিট রিপোর্ট"
    },
    "mr": {
        "AI Investigation Auditor": "एआय तपासणी लेखापरीक्षक (AI Investigation Auditor)",
        "AI-Assisted Second-Level Audit for Investigation Records": "तपास नोंदींसाठी एआय-सहाय्यित द्वितीय-स्तरीय ऑडिट",
        "Potential Inconsistency Detected": "संभाव्य विसंगती आढळली",
        "Requires Human Review": "मानवी पुनरावलोकन आवश्यक आहे",
        "Timeline Conflict": "वेळरेषेतील विसंगती",
        "Missing Evidence Reference": "गहाळ पुराव्याचा संदर्भ",
        "Chain of Custody Documentation Gap": "ताब्यातील साखळी नोंद अंतर",
        "Incomplete Investigative Record": "अपूर्ण तपास नोंद",
        "Records appear consistent based on the available data": "उपलब्ध माहितीच्या आधारे नोंदी सुसंगत दिसतात",
        "Run AI Audit": "एआय ऑडिट चालवा",
        "Audit Findings": "ऑडिट निष्कर्ष",
        "Consistency Score": "सुसंगतता गुण",
        "Mark Reviewed": "तपासले म्हणून चिन्हांकित करा",
        "Needs Further Investigation": "पुढील तपास आवश्यक आहे",
        "False Positive": "चुकीचा इशारा",
        "Audit Report": "ऑडिट अहवाल"
    },
    "es": {
        "AI Investigation Auditor": "Auditor de Investigación IA",
        "AI-Assisted Second-Level Audit for Investigation Records": "Auditoría de segundo nivel asistida por IA para expedientes de investigación",
        "Potential Inconsistency Detected": "Posible inconsistencia detectada",
        "Requires Human Review": "Requiere revisión humana",
        "Timeline Conflict": "Conflicto en la línea de tiempo",
        "Missing Evidence Reference": "Referencia de evidencia faltante",
        "Chain of Custody Documentation Gap": "Brecha documental en la cadena de custodia",
        "Incomplete Investigative Record": "Registro de investigación incompleto",
        "Records appear consistent based on the available data": "Los registros parecen consistentes según los datos disponibles",
        "Run AI Audit": "Ejecutar auditoría IA",
        "Audit Findings": "Hallazgos de auditoría",
        "Consistency Score": "Puntuación de consistencia",
        "Mark Reviewed": "Marcar como revisado",
        "Needs Further Investigation": "Requiere mayor investigación",
        "False Positive": "Falso positivo",
        "Audit Report": "Informe de auditoría"
    },
    "fr": {
        "AI Investigation Auditor": "Auditeur d'Enquête par IA",
        "AI-Assisted Second-Level Audit for Investigation Records": "Audit de second niveau assisté par IA pour dossiers d'enquête",
        "Potential Inconsistency Detected": "Incohérence potentielle détectée",
        "Requires Human Review": "Nécessite un examen humain",
        "Timeline Conflict": "Conflit chronologique",
        "Missing Evidence Reference": "Référence de preuve manquante",
        "Chain of Custody Documentation Gap": "Lacune dans la chaîne de traçabilité",
        "Incomplete Investigative Record": "Dossier d'enquête incomplet",
        "Records appear consistent based on the available data": "Les dossiers semblent cohérents d'après les données disponibles",
        "Run AI Audit": "Lancer l'audit IA",
        "Audit Findings": "Résultats de l'audit",
        "Consistency Score": "Score de cohérence",
        "Mark Reviewed": "Marquer comme examiné",
        "Needs Further Investigation": "Nécessite un complément d'enquête",
        "False Positive": "Faux positif",
        "Audit Report": "Rapport d'audit"
    }
}

class TranslationService:
    @staticmethod
    def get_supported_languages() -> Dict[str, str]:
        return LANGUAGES

    @staticmethod
    def translate_phrase(text: str, lang_code: str) -> str:
        if not text or lang_code == "en" or lang_code not in TRANSLATION_MAP:
            return text
        mapping = TRANSLATION_MAP[lang_code]
        return mapping.get(text, text)

    @staticmethod
    def translate_flag(flag: Dict[str, Any], lang_code: str) -> Dict[str, Any]:
        """Translate flag labels while strictly preserving factual tokens (IDs, timestamps, names)."""
        if lang_code == "en" or lang_code not in TRANSLATION_MAP:
            return flag

        f_copy = flag.copy()
        mapping = TRANSLATION_MAP[lang_code]

        # Translate category if mapped
        if f_copy.get("category") in mapping:
            f_copy["category_translated"] = mapping[f_copy["category"]]
        else:
            f_copy["category_translated"] = f_copy.get("category")

        # Keep original explanation intact to avoid factual alteration, but prepend translated caution
        caution = mapping.get("Requires Human Review", "Requires Human Review")
        f_copy["audit_badge"] = caution
        return f_copy

translation_service = TranslationService()
