from abc import ABC, abstractmethod
from typing import Any

class ReportingInterface(ABC):
    @abstractmethod
    def generate_html_report(self, results: Any, filename: str):
        pass

    @abstractmethod
    def generate_excel_report(self, results: Any, filename: str):
        pass 