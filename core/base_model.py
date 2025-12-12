from abc import ABC, abstractmethod

class BaseModel(ABC):
    """
    The Abstract Parent class for ALL data models .
    """

    @abstractmethod
    def to_dict(self):
        """
        REQUIRED: Must return a dictionary representation of the object.
        Used for populating UI tables (TreeViews).
        """
        pass

    def __repr__(self):
        """
        Optional: Returns a string representation for debugging in the console.
        """
        return str(self.to_dict())