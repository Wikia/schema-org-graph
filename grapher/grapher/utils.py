"""
Utility functions
"""
import re


def extract_link(text):
    """
    :type text str
    :rtype: str|None
    """
    matches = re.findall(r'\[\[([^\]|]+)', text)

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
    :rtype: str|None
    """
    match = re.search(r'\d{4}', text)

    return match.group(0) if match else None
