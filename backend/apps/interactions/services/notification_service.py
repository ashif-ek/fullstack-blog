import json
from django_redis import get_redis_connection
from django.db import transaction
from ..models import Notification

class NotificationService:
    """
    Hardened Notification service with aggregation buffer.
    """
    @staticmethod
    def _get_buffer_key(user_id):
        return f"notification:{user_id}:buffer"

    @classmethod
    def buffer_notification(cls, recipient_id, actor_id, verb, target_post_id):
        """
        Buffer notification event in Redis for aggregation.
        """
        conn = get_redis_connection("default")
        key = cls._get_buffer_key(recipient_id)
        
        event = {
            "actor_id": actor_id,
            "verb": verb,
            "target_post_id": target_post_id,
        }
        
        # Add to buffer
        conn.lpush(key, json.dumps(event))
        # Set expiry for buffer cleanup
        conn.expire(key, 3600)  # 1h

    @classmethod
    def aggregate_and_save(cls, user_id):
        """
        Process the buffer and save aggregated notifications.
        Called by a Celery task.
        """
        conn = get_redis_connection("default")
        key = cls._get_buffer_key(user_id)
        
        # Atomically pop all events from buffer
        events = []
        while True:
            event = conn.rpop(key)
            if not event:
                break
            events.append(json.loads(event))
            
        if not events:
            return

        # Aggregation logic: Group by post and verb
        # Example: { (post_id, 'like'): [actor_ids] }
        aggregated = {}
        for e in events:
            group_key = (e["target_post_id"], e["verb"])
            if group_key not in aggregated:
                aggregated[group_key] = set()
            aggregated[group_key].add(e["actor_id"])
            
        with transaction.atomic():
            for (post_id, verb), actor_ids in aggregated.items():
                actor_count = len(actor_ids)
                first_actor_id = list(actor_ids)[0]
                
                # Check for existing recent unread notification for the same post/verb
                # If it exists, update it instead of creating a new one
                # For simplicity here, we just create a new one but in prod you'd update
                Notification.objects.create(
                    recipient_id=user_id,
                    actor_id=first_actor_id,
                    verb=verb,
                    target_post_id=post_id,
                    # We could add an 'additional_actors_count' field to Notification model
                )
