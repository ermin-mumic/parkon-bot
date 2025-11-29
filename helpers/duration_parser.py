import re

WORD_NUMBERS = {
    "eine": 1,
    "eins": 1,
    "einen": 1,
    "zwei": 2,
    "drei": 3,
    "vier": 4,
    "fünf": 5,
    "sechs": 6,
    "sieben": 7,
    "acht": 8,
    "neun": 9,
    "zehn": 10,
    "elf": 11,
    "zwölf": 12,
    "dreizehn": 13,
    "vierzehn": 14,
    "fünfzehn": 15,
    "sechzehn": 16,
    "siebzehn": 17,
    "achtzehn": 18,
    "neunzehn": 19,
    "zwanzig": 20,
    "einundzwanzig": 21,
    "zweiundzwanzig": 22,
    "dreiundzwanzig": 23,
}

def parse_duration_text(text: str) -> int:
    if not text:
        return 23
    
    text = text.lower().strip()

    match = re.search(r"\d+", text)
    if match:
        num = int(match.group())
        if 1 <= num <= 23:
            return max(1, min(23, num))
        
    for word, number in WORD_NUMBERS.items():
        pattern = r"\b" + re.escape(word) + r"\b"
        if re.search(pattern, text):
            return number
    
    return 23