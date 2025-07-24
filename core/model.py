from dataclasses import dataclass

@dataclass
class ProductUpdate:
    product: str
    update: str
    source: str
    date: str
    confidence_score: float = 0.0
