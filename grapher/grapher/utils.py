"""
Utility functions
"""
import re


def extract_link(text):
    """
    :type text str
    :rtype: str|None
    """
    matches = extract_links(text)

    return matches[0] if matches else None


def extract_links(text):
    """
    :type text str
    :rtype: str|None
    """
    matches = re.findall(r'\[\[([^\]|]+)', text)

    return matches if matches else None


def extract_year(text):
    """
    :type text str
    :rtype: int|None
    """
    match = re.search(r'\d{4}', text)

    return int(match.group(0)) if match else None


def extract_number(text):
    """
    :type text str
    :rtype: int|float|None
    """
    match = re.search(r'[0-9.,]+', text)

    if match:
        value = str(match.group(0))
        if ',' in value:
            value = value.replace(',', '.')
        if '.' in value:
            return float(value)

        return int(value)

    return None
