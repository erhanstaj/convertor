from abc import ABC, abstractmethod

class IConverter(ABC):
    """Bütün Converter sınıflarının uyması gereken zorunlu arayüz (Interface)."""
    
    @abstractmethod
    def convert(self, json_data_list: list) -> str:
        pass
