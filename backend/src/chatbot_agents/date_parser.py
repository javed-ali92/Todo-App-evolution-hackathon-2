"""
Natural language date parsing utility for AI chatbot.
Converts natural language date expressions to YYYY-MM-DD format.
"""
import dateparser
from datetime import datetime, date
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def parse_natural_date(date_string: str) -> Optional[str]:
    """
    Parse natural language date expressions to YYYY-MM-DD format.

    Supports expressions like:
    - "tomorrow"
    - "next Friday"
    - "in 2 days"
    - "next week"
    - "2026-02-15" (already formatted)

    Args:
        date_string: Natural language date expression

    Returns:
        Date in YYYY-MM-DD format, or None if parsing fails
    """
    if not date_string:
        return None

    try:
        # Try parsing with dateparser
        parsed_date = dateparser.parse(
            date_string,
            settings={
                'PREFER_DATES_FROM': 'future',  # Prefer future dates for ambiguous expressions
                'RELATIVE_BASE': datetime.now()
            }
        )

        if parsed_date:
            # Convert to YYYY-MM-DD format
            return parsed_date.strftime('%Y-%m-%d')

        logger.warning(f"Failed to parse date: {date_string}")
        return None

    except Exception as e:
        logger.error(f"Error parsing date '{date_string}': {str(e)}")
        return None


def is_valid_date_format(date_string: str) -> bool:
    """
    Check if a string is already in YYYY-MM-DD format.

    Args:
        date_string: Date string to validate

    Returns:
        True if valid YYYY-MM-DD format, False otherwise
    """
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except (ValueError, TypeError):
        return False


def get_relative_date_description(date_string: str) -> str:
    """
    Get a human-readable description of a date relative to today.

    Args:
        date_string: Date in YYYY-MM-DD format

    Returns:
        Human-readable description (e.g., "tomorrow", "next Friday", "Feb 15")
    """
    try:
        target_date = datetime.strptime(date_string, '%Y-%m-%d').date()
        today = date.today()
        delta = (target_date - today).days

        if delta == 0:
            return "today"
        elif delta == 1:
            return "tomorrow"
        elif delta == -1:
            return "yesterday"
        elif 2 <= delta <= 7:
            return target_date.strftime('%A')  # Day name (e.g., "Friday")
        else:
            return target_date.strftime('%b %d')  # Month and day (e.g., "Feb 15")

    except Exception as e:
        logger.error(f"Error getting date description: {str(e)}")
        return date_string
