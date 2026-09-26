def summarize_text(text: str) -> str:
    sentences = [part.strip() for part in text.split(".") if part.strip()]
    if not sentences:
        return "No text provided to summarize."
    return " ".join(sentences[:3]) + ("..." if len(sentences) > 3 else "")
