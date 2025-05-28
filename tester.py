#!/usr/bin/env python3
"""
ProcureMate 통합 테스터
인터랙티브 메뉴로 모든 테스트 및 검증 기능 제공
"""

import sys
import os
import json
import traceback
from pathlib import Path
from datetime import datetime

class ProcureMateTester:
    """ProcureMate 통합 테스터 클래스"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.gui_dir = self.root_dir / "gui"
        self.results = {}
        
        # 프로젝트 루트를 Python 경로에 추가
        sys.path.insert(0, str(self.root_dir))
    
    def show_main_menu(self):
        """메인 메뉴 표시"""
        print("\n" + "="*50)
        print("🧪 ProcureMate 통합 테스터")
        print("="*50)
        print("1. 간단 검증 (Import 테스트)")
        print("2. 모듈 검증 (GUI + API 테스트)")
        print("3. 전체 구현 상황 체크")
        print("4. 특정 모듈 선택 테스트")
        print("5. 모든 테스트 실행")
        print("6. 테스트 결과 조회")
        print("7. 종료")
        print("="*50)
        
        while True:
            try:
                choice = input("선택하세요 (1-7): ").strip()
                if choice in ['1', '2', '3', '4', '5', '6', '7']:
                    return int(choice)
                else:
                    print("❌ 1-7 사이의 숫자를 입력하세요.")
            except KeyboardInterrupt:
                print("\n👋 종료합니다.")
                sys.exit(0)
            except:
                print("❌ 올바른 숫자를 입력하세요.")
    
    def simple_import_test(self):
        """간단한 import 테스트"""
        print("\n🧪 간단 Import 검증")
        print("="*40)
        
        tests = [
            ("modules 패키지", lambda: __import__('modules')),
            ("utils 패키지", lambda: __import__('utils')),
            ("config 패키지", lambda: __import__('config')),
            ("DocumentGenerator", lambda: getattr(__import__('modules', fromlist=['DocumentGenerator']), 'DocumentGenerator')),
            ("LlmModule", lambda: getattr(__import__('modules', fromlist=['LlmModule']), 'LlmModule')),
            ("DocumentFormGenerator", lambda: getattr(__import__('modules', fromlist=['DocumentFormGenerator']), 'DocumentFormGenerator')),
            ("DocumentAutomationModule", lambda: getattr(__import__('modules', fromlist=['DocumentAutomationModule']), 'DocumentAutomationModule')),
            ("GUI API handlers", lambda: getattr(__import__('gui.api.handlers', fromlist=['get_status_handler']), 'get_status_handler'))
        ]
        
        passed = 0
        failed = 0
        failed_tests = []
        
        for name, test_func in tests:
            try:
                result = test_func()
                print(f"✅ {name}")
                passed += 1
            except Exception as e:
                print(f"❌ {name}: {e}")
                failed += 1
                failed_tests.append((name, str(e)))
        
        print(f"\n📊 Import 검증 결과:")
        print(f"   성공: {passed}개")
        print(f"   실패: {failed}개")
        
        if failed == 0:
            print("🎉 모든 기본 모듈이 정상적으로 로드됩니다!")
        else:
            print("⚠️ 일부 모듈에 문제가 있습니다:")
            for name, error in failed_tests:
                print(f"   - {name}: {error}")
        
        input("Enter를 눌러 메뉴로 돌아가세요...")
        return failed == 0
    
    def module_verification_test(self):
        """모듈 검증 테스트"""
        print("\n🔧 모듈 검증 테스트")
        print("="*40)
        
        # 1. modules import 테스트
        print("1️⃣ 핵심 모듈 import 테스트:")
        try:
            from modules import DocumentGenerator
            print("   ✅ DocumentGenerator")
        except Exception as e:
            print(f"   ❌ DocumentGenerator: {e}")
        
        # 2. GUI API 테스트
        print("\n2️⃣ GUI API 테스트:")
        try:
            from gui.api import router
            from gui.api.handlers import get_status_handler
            print("   ✅ GUI API 모듈")
            
            # 상태 핸들러 테스트
            handler = get_status_handler()
            print("   ✅ 상태 핸들러")
            
            # 공유 모듈 테스트
            modules = handler.modules
            print(f"   ✅ 공유 모듈: {len(modules)}개")
            
            # DummyModule 개수 확인
            from gui.api.handlers import DummyModule
            dummy_count = sum(1 for m in modules.values() if isinstance(m, DummyModule))
            real_count = len(modules) - dummy_count
            print(f"   📊 실제 모듈: {real_count}개, Dummy 모듈: {dummy_count}개")
            
        except Exception as e:
            print(f"   ❌ GUI API: {e}")
        
        # 3. GUI main.py 테스트
        print("\n3️⃣ GUI main.py 테스트:")
        try:
            import gui.main
            app = gui.main.app
            print("   ✅ GUI main.py")
            
            # 라우트 개수 확인
            route_count = len([r for r in app.routes if hasattr(r, 'path')])
            print(f"   📊 등록된 라우트: {route_count}개")
            
            # 중요 라우트 확인
            routes = [str(r.path) for r in app.routes if hasattr(r, 'path')]
            important_routes = ["/", "/document-generator", "/api/documents/types"]
            
            for route in important_routes:
                if route in routes:
                    print(f"   ✅ {route} 라우트 존재")
                else:
                    print(f"   ❌ {route} 라우트 누락")
            
            print("🎉 모듈 검증 완료")
            input("Enter를 눌러 메뉴로 돌아가세요...")
            return True
            
        except Exception as e:
            print(f"   ❌ GUI main.py: {e}")
            input("Enter를 눌러 메뉴로 돌아가세요...")
            return False
    
    def implementation_check(self):
        """전체 구현 상황 체크"""
        print("\n🚀 전체 구현 상황 체크")
        print("="*40)
        
        modules_to_check = [
            ("SlackBotModule", "Slack 봇 모듈"),
            ("LlmModule", "LLM 모듈"),
            ("DataCollectorModule", "데이터 수집 모듈"),
            ("DocumentAutomationModule", "문서 자동화 모듈"),
            ("VectorDbModule", "벡터 DB 모듈"),
            ("TestFrameworkModule", "테스트 프레임워크 모듈"),
            ("DocumentFormGenerator", "문서 양식 생성기"),
            ("AdvancedRAGModule", "고급 RAG 모듈")
        ]
        
        results = {}
        
        for module_name, description in modules_to_check:
            print(f"\n=== {description} 체크 ===")
            
            status = {
                "name": module_name,
                "initialization": False,
                "validation": False,
                "error": None,
                "progress": 0,
                "details": []
            }
            
            try:
                # 모듈 import
                module_class = getattr(__import__('modules', fromlist=[module_name]), module_name)
                
                # 모듈 초기화 테스트
                print(f"   {module_name} 초기화 중...")
                module_instance = module_class()
                status["initialization"] = True
                status["progress"] += 50
                status["details"].append("모듈 초기화 성공")
                print("   ✅ 초기화 성공")
                
                # 검증 테스트 실행
                if hasattr(module_instance, 'run_validation_tests'):
                    print(f"   {module_name} 검증 테스트 실행 중...")
                    validation_result = module_instance.run_validation_tests()
                    status["validation"] = validation_result
                    status["progress"] += 50 if validation_result else 25
                    status["details"].append(f"검증 테스트: {'성공' if validation_result else '부분 성공'}")
                    print(f"   {'✅' if validation_result else '⚠️'} 검증 테스트")
                else:
                    status["details"].append("검증 테스트 메서드 없음")
                    status["progress"] += 25
                    print("   ⚠️ 검증 테스트 메서드 없음")
                
                print(f"   📊 진행률: {status['progress']}%")
                
            except Exception as e:
                error_msg = f"{module_name} 오류: {str(e)}"
                print(f"   ❌ {error_msg}")
                status["error"] = error_msg
                status["details"].append(f"오류 발생: {str(e)}")
            
            results[module_name] = status
        
        # 결과 요약
        self._print_implementation_summary(results)
        
        # 결과 저장 여부 확인
        while True:
            save_choice = input("결과를 JSON 파일로 저장하시겠습니까? (y/n): ").strip().lower()
            if save_choice in ['y', 'yes', 'n', 'no']:
                break
            print("❌ y 또는 n을 입력하세요.")
        
        if save_choice in ['y', 'yes']:
            self.save_test_results(results, "implementation_check")
        
        input("Enter를 눌러 메뉴로 돌아가세요...")
        return results
    
    def specific_module_test(self):
        """특정 모듈 선택 테스트"""
        print(f"\n🔧 특정 모듈 선택 테스트")
        print("="*40)
        
        modules_list = [
            ("LlmModule", "LLM 모듈"),
            ("DocumentAutomationModule", "문서 자동화 모듈"),
            ("VectorDbModule", "벡터 DB 모듈"),
            ("DataCollectorModule", "데이터 수집 모듈"),
            ("SlackBotModule", "Slack 봇 모듈"),
            ("DocumentFormGenerator", "문서 양식 생성기"),
            ("AdvancedRAGModule", "고급 RAG 모듈"),
            ("TestFrameworkModule", "테스트 프레임워크 모듈"),
            ("G2BAPIClient", "나라장터 API 클라이언트"),
            ("CoupangAPIClient", "쿠팡 API 클라이언트")
        ]
        
        print("테스트할 모듈을 선택하세요:")
        for i, (module_name, description) in enumerate(modules_list, 1):
            print(f"{i:2d}. {description} ({module_name})")
        print(f"{len(modules_list)+1:2d}. 메뉴로 돌아가기")
        
        while True:
            try:
                choice = input(f"선택하세요 (1-{len(modules_list)+1}): ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(modules_list)+1:
                    break
                else:
                    print(f"❌ 1-{len(modules_list)+1} 사이의 숫자를 입력하세요.")
            except:
                print("❌ 올바른 숫자를 입력하세요.")
        
        if choice_num == len(modules_list)+1:
            return
        
        module_name, description = modules_list[choice_num-1]
        
        print(f"\n🔍 {description} 테스트 시작")
        print("-" * 40)
        
        original_dir = os.getcwd()
        os.chdir(self.root_dir)
        sys.path.insert(0, str(self.root_dir))
        
        try:
            # 모듈 import 테스트
            print(f"1. {module_name} import 테스트...")
            module_class = getattr(__import__('modules', fromlist=[module_name]), module_name)
            print(f"   ✅ {module_name} import 성공")
            
            # 모듈 초기화 테스트
            print(f"2. {module_name} 초기화 테스트...")
            module_instance = module_class()
            print(f"   ✅ {module_name} 초기화 성공")
            
            # 검증 테스트 실행
            if hasattr(module_instance, 'run_validation_tests'):
                print(f"3. {module_name} 검증 테스트 실행...")
                validation_result = module_instance.run_validation_tests()
                if validation_result:
                    print(f"   ✅ {module_name} 검증 테스트 성공")
                else:
                    print(f"   ⚠️ {module_name} 검증 테스트 부분 성공")
            else:
                print(f"3. {module_name} 검증 테스트 메서드 없음")
            
            # 모듈별 특별 테스트
            self._run_module_specific_tests(module_instance, module_name)
            
            print(f"\n🎉 {description} 테스트 완료")
            
        except Exception as e:
            print(f"❌ {module_name} 테스트 실패: {e}")
            import traceback
            traceback.print_exc()
        finally:
            os.chdir(original_dir)
            if str(self.root_dir) in sys.path:
                sys.path.remove(str(self.root_dir))
        
        input("Enter를 눌러 메뉴로 돌아가세요...")
    
    def _run_module_specific_tests(self, module_instance, module_name):
        """모듈별 특별 테스트"""
        print(f"4. {module_name} 특별 기능 테스트...")
        
        try:
            if module_name == "DocumentFormGenerator":
                types = module_instance.get_document_types()
                print(f"   ✅ 문서 타입 {len(types)}개 로딩")
                
            elif module_name == "DocumentAutomationModule":
                # 간단한 PDF 생성 테스트
                test_data = {
                    'created_date': '2025-05-26',
                    'requester': '테스트',
                    'request_description': '테스트 요청',
                    'urgency': '보통',
                    'budget_range': '100만원',
                    'items': [{'name': '테스트 상품', 'quantity': '1', 'unit_price': '50000', 'total_price': '50000', 'notes': ''}]
                }
                result = module_instance.generate_procurement_pdf(test_data)
                if result and result.endswith('.pdf'):
                    print(f"   ✅ PDF 생성 테스트 성공")
                else:
                    print(f"   ❌ PDF 생성 테스트 실패")
                    
            elif module_name == "LlmModule":
                health = module_instance.check_server_health()
                if health:
                    print(f"   ✅ LLM 서버 연결 성공")
                else:
                    print(f"   ⚠️ LLM 서버 연결 실패 (Mock 모드 동작)")
                    
            else:
                print(f"   ⚠️ {module_name} 특별 테스트 없음")
                
        except Exception as e:
            print(f"   ❌ 특별 테스트 실패: {e}")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("\n🧪 모든 테스트 실행")
        print("="*50)
        
        test_results = {}
        
        # 1. Import 테스트
        print("\n1️⃣ Import 테스트:")
        test_results["import"] = self.simple_import_test()
        
        # 2. 검증 테스트
        print("\n2️⃣ 모듈 검증 테스트:")
        test_results["verify"] = self.module_verification_test()
        
        # 3. 구현 상황 체크
        print("\n3️⃣ 구현 상황 체크:")
        implementation_results = self.implementation_check()
        test_results["implementation"] = implementation_results
        
        # 결과 저장
        self.save_test_results(test_results, "all_tests")
        
        # 최종 요약
        print(f"\n📊 전체 테스트 결과:")
        for test_name, result in test_results.items():
            if test_name == "implementation":
                continue  # 이미 요약이 출력됨
            status = "✅ 성공" if result else "❌ 실패"
            print(f"   {test_name}: {status}")
        
        input("Enter를 눌러 메뉴로 돌아가세요...")
    
    def view_test_results(self):
        """테스트 결과 조회"""
        print("\n📄 테스트 결과 조회")
        print("="*40)
        
        # 테스트 결과 파일들 찾기
        result_files = list(self.root_dir.glob("test_results_*.json"))
        
        if not result_files:
            print("저장된 테스트 결과가 없습니다.")
            input("Enter를 눌러 메뉴로 돌아가세요...")
            return
        
        # 최신 파일들 10개 표시
        result_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        print("최근 테스트 결과 파일들:")
        for i, file in enumerate(result_files[:10], 1):
            timestamp = file.stem.split('_')[-2:]  # test_results_20250526_154110.json
            date_time = f"{timestamp[0]} {timestamp[1][:2]}:{timestamp[1][2:4]}:{timestamp[1][4:6]}"
            print(f"{i:2d}. {file.name} ({date_time})")
        
        print(f"{len(result_files[:10])+1:2d}. 메뉴로 돌아가기")
        
        while True:
            try:
                choice = input(f"조회할 파일을 선택하세요 (1-{len(result_files[:10])+1}): ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(result_files[:10])+1:
                    break
                else:
                    print(f"❌ 1-{len(result_files[:10])+1} 사이의 숫자를 입력하세요.")
            except:
                print("❌ 올바른 숫자를 입력하세요.")
        
        if choice_num == len(result_files[:10])+1:
            return
        
        selected_file = result_files[choice_num-1]
        
        try:
            with open(selected_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"\n📄 테스트 결과: {selected_file.name}")
            print("-" * 50)
            print(f"실행 시간: {data.get('timestamp', 'Unknown')}")
            
            results = data.get('results', {})
            
            if 'implementation' in results and isinstance(results['implementation'], dict):
                # 구현 상황 체크 결과
                print("\n📊 모듈별 구현 상황:")
                for module_name, status in results['implementation'].items():
                    if isinstance(status, dict):
                        progress = status.get('progress', 0)
                        init_status = "✅" if status.get('initialization') else "❌"
                        validation_status = "✅" if status.get('validation') else "❌"
                        print(f"   {module_name}: {progress}% {init_status} {validation_status}")
                        
                        if status.get('error'):
                            print(f"     오류: {status['error']}")
            
            else:
                # 기타 테스트 결과
                for test_name, result in results.items():
                    status = "✅ 성공" if result else "❌ 실패"
                    print(f"   {test_name}: {status}")
            
        except Exception as e:
            print(f"❌ 파일 읽기 실패: {e}")
        
        input("Enter를 눌러 메뉴로 돌아가세요...")
    
    def _print_implementation_summary(self, results):
        """구현 상황 요약 출력"""
        print("\n" + "="*50)
        print("📊 ProcureMate 구현 상황 요약")
        print("="*50)
        
        total_modules = len(results)
        successful_init = sum(1 for r in results.values() if r["initialization"])
        successful_validation = sum(1 for r in results.values() if r["validation"])
        
        print(f"전체 모듈: {total_modules}개")
        print(f"초기화 성공: {successful_init}개")
        print(f"검증 성공: {successful_validation}개")
        
        for name, status in results.items():
            progress = status["progress"]
            init_status = "✅" if status["initialization"] else "❌"
            validation_status = "✅" if status["validation"] else "❌"
            
            print(f"{name}: {progress}% {init_status} {validation_status}")
            
            if status["error"]:
                print(f"  오류: {status['error']}")
        
        overall_progress = sum(r["progress"] for r in results.values()) / total_modules if total_modules > 0 else 0
        print(f"\n전체 진행률: {overall_progress:.1f}%")
        
        if overall_progress >= 80:
            print("🎉 구현이 거의 완료되었습니다!")
        elif overall_progress >= 60:
            print("🚧 구현이 잘 진행되고 있습니다.")
        else:
            print("⚠️  더 많은 작업이 필요합니다.")
    
    def save_test_results(self, results, test_type="test"):
        """테스트 결과를 JSON 파일로 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.root_dir / f"test_results_{test_type}_{timestamp}.json"
        
        test_data = {
            "timestamp": datetime.now().isoformat(),
            "test_type": test_type,
            "results": results
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"📄 테스트 결과 저장: {results_file.name}")
        return str(results_file)
    
    def run(self):
        """메인 실행 루프"""
        while True:
            choice = self.show_main_menu()
            
            if choice == 1:
                self.simple_import_test()
            elif choice == 2:
                self.module_verification_test()
            elif choice == 3:
                self.implementation_check()
            elif choice == 4:
                self.specific_module_test()
            elif choice == 5:
                self.run_all_tests()
            elif choice == 6:
                self.view_test_results()
            elif choice == 7:
                print("👋 ProcureMate 테스터를 종료합니다.")
                break

def main():
    """메인 함수"""
    try:
        tester = ProcureMateTester()
        tester.run()
    except KeyboardInterrupt:
        print("\n👋 사용자 중단")
    except Exception as e:
        print(f"❌ 테스트 중 오류: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
