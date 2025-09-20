import re


_vowels = set("aeiouyäöüAEIOUYÄÖÜ")


def _sentences(text: str):
    s = [x.strip() for x in re.split(r"[.!?]+", text) if x.strip()]
    return s if s else [text.strip()] if text.strip() else []


def _words(text: str):
    return re.findall(r"\b\w+\b", text, flags=re.UNICODE)


def _syllables(word: str) -> int:
    cnt = 0; prev_v = False
    for ch in word:
        is_v = ch in _vowels
        if is_v and not prev_v:
            cnt += 1
        prev_v = is_v
    if word.lower().endswith("e"): cnt = max(1, cnt-1)
    if word.lower().endswith("le"): cnt += 1
    return max(1, cnt)


def flesch_de(text: str) -> float:
    sents = _sentences(text); words = _words(text)
    if not sents or not words: return 0.0
    asl = len(words) / len(sents)
    syl = sum(_syllables(w) for w in words)
    asw = syl / len(words)
    score = 180 - asl - (58.5 * asw)
    return max(0.0, min(100.0, score))


def lix(text: str) -> float:
    words = _words(text); sents = _sentences(text)
    if not words or not sents: return 0.0
    longw = sum(1 for w in words if len(w) > 6)
    return (len(words) / len(sents)) + (100 * longw / len(words))


def wstf(text: str) -> float:
    # Näherung an WSTF-1 (vereinfachte Heuristik, ausreichend konsistent für Vergleiche)
    words = _words(text); sents = _sentences(text)
    if not words or not sents: return 0.0
    longw = sum(1 for w in words if len(w) > 6)
    asl = len(words) / len(sents)
    return 0.1935 * longw + 0.1672 * asl + 0.1297 * (len(words)/max(1, len(sents)))


def basic_stats(text: str) -> dict:
    words = _words(text); sents = _sentences(text)
    if not words or not sents:
        return {
            "avg_sentence_length": 0.0,
            "avg_word_length": 0.0,
            "complex_word_ratio": 0.0,
            "sentence_count": 0,
            "word_count": 0,
            "character_count": 0,
        }
    complex_words = sum(1 for w in words if _syllables(w) > 2)
    return {
        "avg_sentence_length": len(words)/len(sents),
        "avg_word_length": sum(len(w) for w in words)/len(words),
        "complex_word_ratio": 100 * complex_words/len(words),
        "sentence_count": len(sents),
        "word_count": len(words),
        "character_count": len(re.sub(r"\s+", "", text)),
    }