import re

class TextFilter:
    @staticmethod
    def basic(text: str) -> str:
        """保留字母、數字與空白，並去除多餘換行"""
        if not text: return ""
        text = text.strip().replace("\n", " ")
        text = re.sub(r"[^A-Za-z0-9 ]+", " ", text) 
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def numerical(text: str) -> str:
        """僅保留數字"""
        if not text: return ""
        text = text.strip().replace("\n", "")
        text = re.sub(r"[^0-9]+", "", text)
        return text