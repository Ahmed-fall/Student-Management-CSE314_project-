# core/service_locator.py
class ServiceLocator:
    """
    Central registry for all services.
    Ensures we only have ONE instance of each service (Singleton pattern).
    """
    _services = {}

    @classmethod
    def register(cls, interface, instance):
        cls._services[interface] = instance

    @classmethod
    def get(cls, interface):
        return cls._services.get(interface)