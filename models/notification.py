# models/notification.py

from core.base_model import BaseModel
import datetime


class Notification(BaseModel):
    """
    Represents a Notification entity.

    Strict OOP Implementation:
    - Inherits BaseModel
    - Encapsulation via private attributes
    - Immediate validation via setters
    """

    def __init__(self, id, user_id, announcement_id, read_flag=0, sent_at=None):
        self.id = id
        self.user_id = user_id
        self.announcement_id = announcement_id
        self.read_flag = read_flag
        self.sent_at = sent_at or datetime.datetime.now().isoformat()

    # -------------------
    # Getters
    # -------------------
    @property
    def id(self):
        return self._id

    @property
    def user_id(self):
        return self._user_id

    @property
    def announcement_id(self):
        return self._announcement_id

    @property
    def read_flag(self):
        return self._read_flag

    @property
    def sent_at(self):
        return self._sent_at

    # -------------------
    # Setters (Validation)
    # -------------------
    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, int):
            raise TypeError("Notification ID must be an integer.")
        self._id = value

    @user_id.setter
    def user_id(self, value):
        if not isinstance(value, int):
            raise TypeError("User ID must be an integer.")
        self._user_id = value

    @announcement_id.setter
    def announcement_id(self, value):
        if not isinstance(value, int):
            raise TypeError("Announcement ID must be an integer.")
        self._announcement_id = value

    @read_flag.setter
    def read_flag(self, value):
        if value not in (0, 1):
            raise ValueError("read_flag must be 0 (unread) or 1 (read).")
        self._read_flag = value

    @sent_at.setter
    def sent_at(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("sent_at must be a valid datetime string.")
        self._sent_at = value.strip()

    # -------------------
    # BaseModel Methods
    # -------------------
    def to_dict(self):
        """
        Converts the object to a dictionary.
        Matches database column names exactly.
        """
        return {
            "id": self._id,
            "user_id": self._user_id,
            "announcement_id": self._announcement_id,
            "read_flag": self._read_flag,
            "sent_at": self._sent_at
        }

    @staticmethod
    def from_row(row):
        """
        Factory method to create a Notification from a database row.
        """
        if row is None:
            return None

        return Notification(
            id=row["id"],
            user_id=row["user_id"],
            announcement_id=row["announcement_id"],
            read_flag=row["read_flag"],
            sent_at=row["sent_at"]
        )