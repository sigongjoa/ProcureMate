from typing import Any, Dict, List, Callable
from utils.logger import get_logger

logger = get_logger(__name__)

class ModuleValidator:
    """모듈 검증 및 디버깅 클래스"""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.test_results: List[Dict] = []
    
    def validate_function(self, func: Callable, test_cases: List[Dict]) -> bool:
        """함수 단위 테스트 및 검증"""
        logger.info(f"Validating {func.__name__} in {self.module_name}")
        
        all_passed = True
        for i, case in enumerate(test_cases):
            try:
                input_data = case.get('input', {})
                expected = case.get('expected')
                
                logger.debug(f"Test case {i+1}: {input_data}")
                
                if isinstance(input_data, dict):
                    result = func(**input_data)
                else:
                    result = func(input_data)
                
                if expected is not None and result != expected:
                    logger.error(f"Test case {i+1} failed: expected {expected}, got {result}")
                    all_passed = False
                else:
                    logger.debug(f"Test case {i+1} passed")
                    
                self.test_results.append({
                    "case": i+1,
                    "status": "pass" if (expected is None or result == expected) else "fail",
                    "input": input_data,
                    "result": result,
                    "expected": expected
                })
                
            except Exception as e:
                logger.error(f"Test case {i+1} error: {str(e)}")
                all_passed = False
                self.test_results.append({
                    "case": i+1,
                    "status": "error",
                    "input": input_data,
                    "error": str(e)
                })
        
        return all_passed
    
    def debug_module_state(self, module_instance: Any) -> Dict:
        """모듈 상태 디버깅 정보 수집"""
        debug_info = {
            "module_name": self.module_name,
            "class_name": module_instance.__class__.__name__,
            "attributes": {},
            "methods": []
        }
        
        for attr_name in dir(module_instance):
            if not attr_name.startswith('_'):
                attr_value = getattr(module_instance, attr_name)
                if callable(attr_value):
                    debug_info["methods"].append(attr_name)
                else:
                    debug_info["attributes"][attr_name] = str(attr_value)
        
        logger.debug(f"Module debug info: {debug_info}")
        return debug_info
    
    def get_test_summary(self) -> Dict:
        """테스트 결과 요약"""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['status'] == 'pass')
        failed = sum(1 for r in self.test_results if r['status'] == 'fail')
        errors = sum(1 for r in self.test_results if r['status'] == 'error')
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "success_rate": passed / total if total > 0 else 0
        }
