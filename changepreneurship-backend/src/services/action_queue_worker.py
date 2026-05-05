"""
Action Queue Worker — Sprint 4 (S4-06)
=========================================
CEO (Section 13.4): action execution must be async, retried, and fully logged.

Executes APPROVED UserActions via Redis queue.
  - Max 3 retries per action
  - Exponential backoff: 60s, 120s, 240s
  - Failed after 3 attempts → FAILED state + audit entry
  - Queue key: changepreneurship:action_queue

Worker loop:
  1. BLPOP from queue (blocking pop, 5s timeout)
  2. Fetch UserAction by id
  3. Verify status == APPROVED → transition to QUEUED
  4. Execute platform adapter
  5. Mark EXECUTED or FAILED
  6. Record to audit trail
"""
import json
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

QUEUE_KEY = 'changepreneurship:action_queue'
RETRY_KEY_PREFIX = 'changepreneurship:action_retry:'
MAX_RETRIES = 3
BACKOFF_SECONDS = [60, 120, 240]


class ActionQueueWorker:
    """
    Manages the Redis action queue. Actual worker loop is run separately.
    This class encapsulates enqueue/dequeue/retry logic.
    """

    def __init__(self, redis_client=None):
        self._redis = redis_client

    def enqueue(self, action_id: int) -> bool:
        """Push action_id onto the queue. Returns True if enqueued."""
        if not self._redis:
            logger.warning("ActionQueueWorker: Redis not connected, skipping enqueue")
            return False
        try:
            payload = json.dumps({'action_id': action_id, 'attempt': 1})
            self._redis.rpush(QUEUE_KEY, payload)
            logger.info("ActionQueueWorker: enqueued action_id=%s", action_id)
            return True
        except Exception as exc:
            logger.error("ActionQueueWorker enqueue failed: %s", exc)
            return False

    def dequeue(self, timeout: int = 5) -> Optional[dict]:
        """Blocking pop from queue. Returns payload dict or None on timeout."""
        if not self._redis:
            return None
        try:
            result = self._redis.blpop(QUEUE_KEY, timeout=timeout)
            if result:
                _, data = result
                return json.loads(data)
        except Exception as exc:
            logger.error("ActionQueueWorker dequeue failed: %s", exc)
        return None

    def requeue_with_backoff(self, action_id: int, attempt: int) -> bool:
        """Re-enqueue with incremented attempt counter (exponential backoff)."""
        if not self._redis:
            return False
        if attempt > MAX_RETRIES:
            return False
        delay = BACKOFF_SECONDS[min(attempt - 1, len(BACKOFF_SECONDS) - 1)]
        try:
            payload = json.dumps({'action_id': action_id, 'attempt': attempt})
            # Schedule via sorted set with score = execute_after timestamp
            execute_at = time.time() + delay
            self._redis.zadd(
                f'{RETRY_KEY_PREFIX}scheduled',
                {payload: execute_at},
            )
            logger.info(
                "ActionQueueWorker: action_id=%s requeued for attempt=%s in %ds",
                action_id, attempt, delay,
            )
            return True
        except Exception as exc:
            logger.error("ActionQueueWorker requeue failed: %s", exc)
            return False

    def flush_due_retries(self) -> int:
        """
        Move actions from scheduled retry set to main queue if their time has come.
        Call this from the worker loop periodically.
        """
        if not self._redis:
            return 0
        now = time.time()
        try:
            due = self._redis.zrangebyscore(
                f'{RETRY_KEY_PREFIX}scheduled', '-inf', now,
            )
            if not due:
                return 0
            pipe = self._redis.pipeline()
            for payload in due:
                pipe.rpush(QUEUE_KEY, payload)
                pipe.zrem(f'{RETRY_KEY_PREFIX}scheduled', payload)
            pipe.execute()
            return len(due)
        except Exception as exc:
            logger.error("ActionQueueWorker flush_due_retries failed: %s", exc)
            return 0

    def queue_size(self) -> int:
        """Current queue depth (for monitoring)."""
        if not self._redis:
            return 0
        try:
            return self._redis.llen(QUEUE_KEY)
        except Exception:
            return 0
