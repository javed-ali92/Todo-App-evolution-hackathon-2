"""
Rate limiting service for chat API.
Implements per-user rate limiting using PostgreSQL backend.
"""
from sqlmodel import Session, select
from typing import Optional
from datetime import datetime, timedelta
import os
import logging
from ..models.rate_limit import RateLimit

logger = logging.getLogger(__name__)


class RateLimitService:
    """
    Service for managing API rate limits per user.

    Uses PostgreSQL for persistent rate limit tracking.
    """

    def __init__(self, session: Session):
        self.session = session
        self.limit = int(os.getenv("CHAT_RATE_LIMIT", "100"))

    def check_rate_limit(
        self,
        user_id: int,
        endpoint: str = "/api/chat"
    ) -> tuple[bool, Optional[int]]:
        """
        Check if user has exceeded rate limit.

        Args:
            user_id: ID of the user
            endpoint: API endpoint path

        Returns:
            Tuple of (is_allowed, seconds_until_reset)
            - is_allowed: True if request is allowed, False if rate limit exceeded
            - seconds_until_reset: Seconds until rate limit resets (None if allowed)
        """
        try:
            # Get or create rate limit record
            statement = select(RateLimit).where(
                RateLimit.user_id == user_id,
                RateLimit.endpoint == endpoint
            )
            rate_limit = self.session.exec(statement).first()

            now = datetime.utcnow()

            # No existing record - create one
            if not rate_limit:
                rate_limit = RateLimit(
                    user_id=user_id,
                    endpoint=endpoint,
                    count=1,
                    reset_at=now + timedelta(days=1),
                    updated_at=now
                )
                self.session.add(rate_limit)
                self.session.commit()
                logger.info(f"Created rate limit record for user {user_id}")
                return True, None

            # Check if reset time has passed
            if now >= rate_limit.reset_at:
                # Reset counter
                rate_limit.count = 1
                rate_limit.reset_at = now + timedelta(days=1)
                rate_limit.updated_at = now
                self.session.add(rate_limit)
                self.session.commit()
                logger.info(f"Reset rate limit for user {user_id}")
                return True, None

            # Check if limit exceeded
            if rate_limit.count >= self.limit:
                seconds_until_reset = int((rate_limit.reset_at - now).total_seconds())
                logger.warning(f"Rate limit exceeded for user {user_id}")
                return False, seconds_until_reset

            # Increment counter
            rate_limit.count += 1
            rate_limit.updated_at = now
            self.session.add(rate_limit)
            self.session.commit()

            return True, None

        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            # On error, allow the request (fail open)
            return True, None

    def get_remaining_requests(
        self,
        user_id: int,
        endpoint: str = "/api/chat"
    ) -> int:
        """
        Get number of remaining requests for a user.

        Args:
            user_id: ID of the user
            endpoint: API endpoint path

        Returns:
            Number of remaining requests
        """
        try:
            statement = select(RateLimit).where(
                RateLimit.user_id == user_id,
                RateLimit.endpoint == endpoint
            )
            rate_limit = self.session.exec(statement).first()

            if not rate_limit:
                return self.limit

            now = datetime.utcnow()

            # Check if reset time has passed
            if now >= rate_limit.reset_at:
                return self.limit

            remaining = self.limit - rate_limit.count
            return max(0, remaining)

        except Exception as e:
            logger.error(f"Error getting remaining requests: {str(e)}")
            return self.limit

    def cleanup_expired_limits(self) -> int:
        """
        Clean up expired rate limit records.

        This is a background task that should run periodically.

        Returns:
            Number of records deleted
        """
        try:
            now = datetime.utcnow()

            statement = select(RateLimit).where(
                RateLimit.reset_at < now
            )

            expired_limits = self.session.exec(statement).all()

            for limit in expired_limits:
                self.session.delete(limit)

            self.session.commit()

            logger.info(f"Cleaned up {len(expired_limits)} expired rate limit records")
            return len(expired_limits)

        except Exception as e:
            logger.error(f"Error cleaning up expired limits: {str(e)}")
            return 0
