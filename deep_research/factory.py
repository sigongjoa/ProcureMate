from typing import Dict, Type
from .core import DeepResearchCore
from .strategies import (
    PriceFocusedStrategy,
    QualityFocusedStrategy, 
    RiskFocusedStrategy,
    SupplierFocusedStrategy,
    BalancedStrategy
)
from .config import ResearchConfig

class DeepResearchFactory:
    _strategies: Dict[str, Type[DeepResearchCore]] = {
        'default': BalancedStrategy,
        'balanced': BalancedStrategy,
        'price': PriceFocusedStrategy,
        'quality': QualityFocusedStrategy,
        'risk': RiskFocusedStrategy,
        'supplier': SupplierFocusedStrategy,
        'core': DeepResearchCore
    }
    
    @classmethod
    def create(cls, strategy_type: str = 'default', config: ResearchConfig = None) -> DeepResearchCore:
        strategy_class = cls._strategies.get(strategy_type, BalancedStrategy)
        
        if config and strategy_type == 'core':
            return strategy_class(config)
        else:
            return strategy_class()
    
    @classmethod
    def get_available_strategies(cls) -> list:
        return list(cls._strategies.keys())
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[DeepResearchCore]):
        cls._strategies[name] = strategy_class
