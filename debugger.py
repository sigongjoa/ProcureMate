#!/usr/bin/env python3
"""
ProcureMate 통합 디버거
인터랙티브 메뉴로 모든 디버그 기능 제공
"""

import os
import sys
import time
import requests
import subprocess
from pathlib import Path

class ProcureMateDebugger:
    """ProcureMate 통합 디버거 클래스"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.gui_dir = self.root_dir / "gui"
    
    def show_main_menu(self):
        """메인 메뉴 표시"""
        print("\n" + "="*50)
        print("🔍 ProcureMate 통합 디버거")
        print("="*50)
        print("1. 빠른 디버그 (기본 파일 및 import 확인)")
        print("2. 전체 시스템 진단 (모든 모듈 상태 확인)")
        print("3. GUI 서버 상세 디버그")
        print("4. API 라우트 디버그")
        print("5. 특정 모듈 디버그")
        print("6. 모든 디버그 실행")
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
    
    def quick_debug(self):
        """빠른 디버그 - 기본 파일 및 import 확인"""
        print("\n🔍 빠른 디버그 시작")
        print("="*40)
        
        # 1. 기본 파일 확인
        print("\n📁 기본 파일 확인:")
        main_py = self.gui_dir / "main.py" 
        template_file = self.gui_dir / "templates" / "document_generator.html"
        
        print(f"GUI 디렉토리: {'✅' if self.gui_dir.exists() else '❌'}")
        print(f"main.py: {'✅' if main_py.exists() else '❌'}")
        print(f"템플릿 파일: {'✅' if template_file.exists() else '❌'}")
        
        if not self.gui_dir.exists():
            print("❌ GUI 디렉토리가 없습니다.")
            input("Enter를 눌러 메뉴로 돌아가세요...")
            return False
        
        # 2. import 테스트
        original_dir = os.getcwd()
        os.chdir(self.gui_dir)
        sys.path.insert(0, str(self.gui_dir))
        sys.path.insert(0, str(self.root_dir))
        
        try:
            print("\n📦 모듈 import 테스트:")
            
            # 기본 패키지
            import fastapi, uvicorn
            print("✅ FastAPI/Uvicorn")
            
            # main.py import
            import main
            print("✅ main.py import 성공")
            
            # API 라우터
            from api import router
            print("✅ API 라우터 import 성공")
            
            # 모듈들
            from modules import DocumentFormGenerator
            print("✅ DocumentFormGenerator import 성공")
            
            # 라우트 확인
            app = main.app
            routes = [str(route.path) for route in app.routes if hasattr(route, 'path')]
            print(f"✅ 등록된 라우트: {len(routes)}개")
            
            if "/document-generator" in routes:
                print("✅ /document-generator 라우트 존재")
            else:
                print("❌ /document-generator 라우트 없음")
            
            print("\n🎉 빠른 디버그 완료 - 기본 시스템 정상")
            input("Enter를 눌러 메뉴로 돌아가세요...")
            return True
            
        except Exception as e:
            print(f"❌ Import 실패: {e}")
            input("Enter를 눌러 메뉴로 돌아가세요...")
            return False
        finally:
            os.chdir(original_dir)
            if str(self.gui_dir) in sys.path:
                sys.path.remove(str(self.gui_dir))
            if str(self.root_dir) in sys.path:
                sys.path.remove(str(self.root_dir))
    
    def full_diagnosis(self):
        """전체 진단 - 모든 모듈 및 시스템 상태 확인"""
        print("\n🔍 전체 시스템 진단")
        print("="*50)
        
        original_dir = os.getcwd()
        os.chdir(self.root_dir)
        sys.path.insert(0, str(self.root_dir))
        
        try:
            print("1️⃣ 핵심 모듈 import 진단:")
            
            # 기본 모듈들 테스트
            modules_to_test = [
                'LlmModule', 'VectorDbModule', 'DataCollectorModule',
                'DocumentAutomationModule', 'TestFrameworkModule', 'SlackBotModule',
                'G2BAPIClient', 'CoupangAPIClient', 'DocumentGenerator',
                'DocumentFormGenerator', 'AdvancedRAGModule'
            ]
            
            failed_imports = []
            
            for module_name in modules_to_test:
                try:
                    exec(f"from modules import {module_name}")
                    print(f"   ✅ {module_name}")
                except Exception as e:
                    print(f"   ❌ {module_name}: {e}")
                    failed_imports.append((module_name, str(e)))
            
            print(f"\n2️⃣ API 모듈 진단:")
            try:
                from gui.api import router
                from gui.api.handlers import get_status_handler
                print("   ✅ API 모듈")
                
                handler = get_status_handler()
                print("   ✅ 상태 핸들러")
                
            except Exception as e:
                print(f"   ❌ API 모듈: {e}")
            
            print(f"\n3️⃣ GUI main.py 진단:")
            try:
                import gui.main
                app = gui.main.app
                
                routes = []
                for route in app.routes:
                    if hasattr(route, 'path') and hasattr(route, 'methods'):
                        routes.append(f"{list(route.methods)} {route.path}")
                
                print(f"   ✅ main.py - {len(routes)}개 라우트")
                
                # 중요 라우트 확인
                important_routes = [
                    "GET /", "GET /document-generator", 
                    "GET /api/documents/types", "POST /api/documents/generate"
                ]
                
                route_paths = [r.split()[-1] for r in routes]
                
                for imp_route in important_routes:
                    method, path = imp_route.split(" ", 1)
                    if path in route_paths:
                        print(f"   ✅ {imp_route}")
                    else:
                        print(f"   ❌ {imp_route} - 누락")
                
            except Exception as e:
                print(f"   ❌ main.py: {e}")
            
            print(f"\n4️⃣ 파일 구조 진단:")
            required_files = [
                "gui/main.py", "gui/templates/document_generator.html",
                "gui/api/__init__.py", "gui/api/routes.py", "gui/api/handlers.py"
            ]
            
            for file_path in required_files:
                full_path = Path(file_path)
                status = "✅" if full_path.exists() else "❌"
                print(f"   {status} {file_path}")
            
            # 요약
            print(f"\n📊 진단 요약:")
            print(f"   실패한 import: {len(failed_imports)}개")
            
            if failed_imports:
                print(f"\n❌ 해결 필요한 import 오류:")
                for module, error in failed_imports[:5]:
                    print(f"   - {module}: {error}")
            
            if len(failed_imports) == 0:
                print("🎉 전체 진단 완료 - 모든 시스템 정상")
            else:
                print("⚠️ 일부 모듈에 문제가 있습니다.")
            
            input("Enter를 눌러 메뉴로 돌아가세요...")
            return len(failed_imports) == 0
            
        except Exception as e:
            print(f"❌ 진단 중 오류: {e}")
            input("Enter를 눌러 메뉴로 돌아가세요...")
            return False
        finally:
            os.chdir(original_dir)
            if str(self.root_dir) in sys.path:
                sys.path.remove(str(self.root_dir))
    
    def debug_gui_server(self):
        """GUI 서버 상세 디버그"""
        print("\n🔍 GUI 서버 상세 디버그")
        print("="*60)
        
        # 1. 파일 구조 확인
        print("\n📁 파일 구조 확인:")
        print(f"GUI 디렉토리: {self.gui_dir}")
        print(f"GUI 디렉토리 존재: {'✅' if self.gui_dir.exists() else '❌'}")
        
        if self.gui_dir.exists():
            main_py = self.gui_dir / "main.py"
            templates_dir = self.gui_dir / "templates"
            api_dir = self.gui_dir / "api"
            
            print(f"main.py 존재: {'✅' if main_py.exists() else '❌'}")
            print(f"templates 디렉토리 존재: {'✅' if templates_dir.exists() else '❌'}")
            print(f"api 디렉토리 존재: {'✅' if api_dir.exists() else '❌'}")
            
            if templates_dir.exists():
                template_files = list(templates_dir.glob("*.html"))
                print(f"템플릿 파일 수: {len(template_files)}")
                for template in template_files:
                    print(f"  - {template.name}")
        
        # 2. Python 환경 확인
        print(f"\n🐍 Python 환경:")
        print(f"Python 경로: {sys.executable}")
        print(f"Python 버전: {sys.version}")
        print(f"현재 작업 디렉토리: {os.getcwd()}")
        
        # 3. 필수 패키지 확인
        print(f"\n📦 필수 패키지 확인:")
        required_packages = ['fastapi', 'uvicorn', 'jinja2']
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package}: 설치됨")
            except ImportError:
                print(f"❌ {package}: 설치되지 않음")
        
        # 4. 서버 시작 테스트 여부 확인
        while True:
            test_choice = input("\n실제 서버 시작 테스트를 진행하시겠습니까? (y/n): ").strip().lower()
            if test_choice in ['y', 'yes', 'n', 'no']:
                break
            print("❌ y 또는 n을 입력하세요.")
        
        if test_choice in ['n', 'no']:
            print("서버 시작 테스트를 건너뜁니다.")
            input("Enter를 눌러 메뉴로 돌아가세요...")
            return
        
        # 5. 서버 시작 테스트
        print(f"\n🚀 서버 시작 테스트:")
        
        original_dir = os.getcwd()
        try:
            os.chdir(self.gui_dir)
            print(f"작업 디렉토리 변경: {os.getcwd()}")
            
            # 서버 프로세스 시작
            print("FastAPI 서버 시작 중...")
            server_process = subprocess.Popen([
                sys.executable, "main.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            print("서버 시작 대기 중...")
            time.sleep(5)
            
            # 프로세스 상태 확인
            if server_process.poll() is None:
                print("✅ 서버 프로세스 실행 중")
                
                # HTTP 요청 테스트
                test_urls = [
                    "http://localhost:8080/",
                    "http://localhost:8080/document-generator",
                    "http://localhost:8080/api/documents/types"
                ]
                
                for url in test_urls:
                    try:
                        response = requests.get(url, timeout=5)
                        print(f"✅ {url}: {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        print(f"❌ {url}: 연결 실패 - {e}")
                
                # 서버 종료
                print(f"\n🛑 서버 종료 중...")
                server_process.terminate()
                server_process.wait()
                print("✅ 서버 종료 완료")
                
                print("🎉 GUI 서버 디버그 완료 - 서버 정상 작동")
            else:
                print("❌ 서버 프로세스 종료됨")
                stdout, stderr = server_process.communicate()
                print(f"STDOUT:\n{stdout}")
                print(f"STDERR:\n{stderr}")
            
        except Exception as e:
            print(f"❌ 서버 테스트 실패: {e}")
        finally:
            os.chdir(original_dir)
        
        input("Enter를 눌러 메뉴로 돌아가세요...")
    
    def debug_api_routes(self):
        """API 라우트 디버그"""
        print(f"\n🛣️ API 라우트 디버그")
        print("="*40)
        
        original_dir = os.getcwd()
        
        try:
            os.chdir(self.gui_dir)
            sys.path.insert(0, str(self.gui_dir))
            
            # API 라우터 import
            from api import router
            print("✅ API 라우터 import 성공")
            
            # 라우트 확인
            if hasattr(router, 'routes'):
                print(f"등록된 라우트 수: {len(router.routes)}")
                for route in router.routes:
                    if hasattr(route, 'path') and hasattr(route, 'methods'):
                        print(f"  - {route.methods} {route.path}")
            
            print("🎉 API 라우트 디버그 완료")
            
        except Exception as e:
            print(f"❌ API 라우터 디버그 실패: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            os.chdir(original_dir)
            if str(self.gui_dir) in sys.path:
                sys.path.remove(str(self.gui_dir))
        
        input("Enter를 눌러 메뉴로 돌아가세요...")
    
    def debug_specific_module(self):
        """특정 모듈 디버그"""
        print(f"\n🔧 특정 모듈 디버그")
        print("="*40)
        
        modules_list = [
            ("LlmModule", "LLM 모듈"),
            ("DocumentAutomationModule", "문서 자동화 모듈"),
            ("VectorDbModule", "벡터 DB 모듈"),
            ("DataCollectorModule", "데이터 수집 모듈"),
            ("SlackBotModule", "Slack 봇 모듈"),
            ("DocumentFormGenerator", "문서 양식 생성기"),
            ("AdvancedRAGModule", "고급 RAG 모듈")
        ]
        
        print("디버그할 모듈을 선택하세요:")
        for i, (module_name, description) in enumerate(modules_list, 1):
            print(f"{i}. {description} ({module_name})")
        print(f"{len(modules_list)+1}. 메뉴로 돌아가기")
        
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
        
        print(f"\n🔍 {description} 디버그 시작")
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
            
            print(f"\n🎉 {description} 디버그 완료")
            
        except Exception as e:
            print(f"❌ {module_name} 디버그 실패: {e}")
            import traceback
            traceback.print_exc()
        finally:
            os.chdir(original_dir)
            if str(self.root_dir) in sys.path:
                sys.path.remove(str(self.root_dir))
        
        input("Enter를 눌러 메뉴로 돌아가세요...")
    
    def debug_all(self):
        """모든 디버그 실행"""
        print("\n🔍 모든 디버그 실행")
        print("="*50)
        
        results = []
        
        print("\n1️⃣ 빠른 디버그:")
        results.append(("빠른 디버그", self.quick_debug()))
        
        print("\n2️⃣ 전체 진단:")
        results.append(("전체 진단", self.full_diagnosis()))
        
        print("\n3️⃣ API 라우트 디버그:")
        self.debug_api_routes()
        
        print(f"\n📊 디버그 결과:")
        for name, success in results:
            status = "✅ 성공" if success else "❌ 실패"
            print(f"   {name}: {status}")
        
        input("Enter를 눌러 메뉴로 돌아가세요...")
    
    def run(self):
        """메인 실행 루프"""
        while True:
            choice = self.show_main_menu()
            
            if choice == 1:
                self.quick_debug()
            elif choice == 2:
                self.full_diagnosis()
            elif choice == 3:
                self.debug_gui_server()
            elif choice == 4:
                self.debug_api_routes()
            elif choice == 5:
                self.debug_specific_module()
            elif choice == 6:
                self.debug_all()
            elif choice == 7:
                print("👋 ProcureMate 디버거를 종료합니다.")
                break

def main():
    """메인 함수"""
    try:
        debugger = ProcureMateDebugger()
        debugger.run()
    except KeyboardInterrupt:
        print("\n👋 사용자 중단")
    except Exception as e:
        print(f"❌ 디버그 중 오류: {e}")

if __name__ == "__main__":
    main()
