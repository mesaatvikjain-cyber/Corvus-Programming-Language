import re

# Corvus Regular Expression Engine (v4.2)

class RegexEngine:
    @staticmethod
    def match(pattern, text):
        return bool(re.search(pattern, str(text)))

    @staticmethod
    def findall(pattern, text):
        return re.findall(pattern, str(text))

    @staticmethod
    def replace(pattern, replacement, text):
        return re.sub(pattern, replacement, str(text))

    @staticmethod
    def is_email(email_str):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return bool(re.match(pattern, str(email_str)))

_global_regex_engine = RegexEngine()
