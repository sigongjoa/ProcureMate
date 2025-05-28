from .config import ResearchConfig, ResearchDepth, ResearchFocus
from .core import DeepResearchCore, DeepResearchResult
from .factory import DeepResearchFactory
from .strategies import (
    PriceFocusedStrategy,
    QualityFocusedStrategy,
    RiskFocusedStrategy,
    SupplierFocusedStrategy,
    BalancedStrategy
)

__all__ = [
    'ResearchConfig',
    'ResearchDepth', 
    'ResearchFocus',
    'DeepResearchCore',
    'DeepResearchResult',
    'DeepResearchFactory',
    'PriceFocusedStrategy',
    'QualityFocusedStrategy',
    'RiskFocusedStrategy',
    'SupplierFocusedStrategy',
    'BalancedStrategy'
]

# 편의 함수
def create_research_engine(strategy: str = 'default', config: ResearchConfig = None):
    return DeepResearchFactory.create(strategy, config)

def get_available_strategies():
    return DeepResearchFactory.get_available_strategies()
