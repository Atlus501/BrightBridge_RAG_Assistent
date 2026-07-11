from infrastructure.cryptographer import Cryptographer
from infrastructure.databases.redis_manager import Redis_Manager

"""
Sets up the context manager
"""
def set_up_context_manager():
    cryptographer = Cryptographer()

    #creating the redis manager
    redis_manager = Redis_Manager(num_recent_messages=3, cryptographer=cryptographer)

    return redis_manager