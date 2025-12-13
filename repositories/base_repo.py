import sqlite3
import os
from abc import ABC, abstractmethod

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(REPO_DIR, '..', 'student_management.db')


class BaseRepository(ABC):

    def __init__(self):
        self.db_path = DB_PATH


    def execute_query(self, query, params=(), commit=True):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(query, params)
            
            if commit:
                conn.commit()
                
            return cursor
            
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Database Error: {e} in query: {query} with params: {params}")
            raise 
            
        finally:
            if conn:
                conn.close()

    @abstractmethod
    def get_all(self):
        pass