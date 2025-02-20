import shelve
import logging


def reset_cache():
    """Clear all cached data."""
    try:
        with shelve.open("cache.db", flag="n"):
            logging.info("Cache reset successfully.")
    except Exception as e:
        logging.error(f"Error resetting cache: {e}")


def load_cache():
    """Load cached data from the shelve database."""
    try:
        with shelve.open("cache.db") as cache:
            return dict(cache)
    except Exception as e:
        logging.error(f"Error loading cache: {e}")
        return {}


def save_cache(data):
    """Save data to the shelve database."""
    try:
        with shelve.open("cache.db") as cache:
            # Ensure all keys are strings to avoid encoding issues.
            data = {str(key): value for key, value in data.items()}
            cache.update(data)
            logging.info("Cache saved successfully.")
    except Exception as e:
        logging.error(f"Error saving cache: {e}")
