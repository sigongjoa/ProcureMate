from enum import Enum
from dataclasses import dataclass

class ResearchDepth(Enum):
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    ENTERPRISE = "enterprise"

class ResearchFocus(Enum):
    PRICE_FOCUSED = "price"
    QUALITY_FOCUSED = "quality"
    SUPPLIER_FOCUSED = "supplier"
    RISK_FOCUSED = "risk"
    BALANCED = "balanced"

@dataclass
class ResearchConfig:
    depth: ResearchDepth = ResearchDepth.STANDARD
    focus: ResearchFocus = ResearchFocus.BALANCED
    max_products: int = 50
    max_suppliers: int = 10
    timeout_seconds: int = 30
    enable_real_time_data: bool = True
    enable_rag_search: bool = True
