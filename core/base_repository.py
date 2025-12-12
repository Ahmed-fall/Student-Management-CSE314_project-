from abc import ABC, abstractmethod
from database.db_connection import get_db_connection

class BaseRepository(ABC):
    """
    The Abstract Parent class for ALL repositories.
    """
    
    def get_connection(self):
        """
        Team Usage: conn = self.get_connection()
        """
        return get_db_connection()

    @abstractmethod
    def create(self, *args, **kwargs):
        
        pass

    @abstractmethod
    def get_all(self):
        
        pass

    @abstractmethod
    def delete(self, id):
        
        pass