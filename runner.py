#!/usr/bin/env python3
"""
ProcureMate 통합 실행기
인터랙티브 메뉴로 모든 실행 옵션 제공
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

class ProcureMateRunner:
    """ProcureMate 통합 실행 클래스"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.gui_dir = self.root_dir / "gui"
        
    def show_main_menu(self):
        """메인 메뉴 표시"""
        print("\n" + "="*50)
        print("🚀 ProcureMate 통합 실행기")
        print("="*50)
        print("1. 빠른 시작 (문서 생성기)")
        print("2. GUI 웹 서버만 실행")
        print("3. 전체 시스템 실행 (Slack봇 + LLM + RAG)")
        print("4. 문서 생성기 (테스트 포함)")
        print("5. 종료")
        print("="*50)
        
        while True:
            try:
                choice = input("선택하세요 (1-5): ").strip()
                if choice in ['1', '2', '3', '4', '5']:
                    return int(choice)
                else:
                    print("❌ 1-5 사이의 숫자를 입력하세요.")
            except KeyboardInterrupt:
                print("\n👋 종료합니다.")
                sys.exit(0)
            except:
                print("❌ 올바른 숫자를 입력하세요.")
    
    def quick_start(self):
        """빠른 시작 (기존 start.py 기능)"""
        print("\n🚀 ProcureMate 문서 생성기 빠른 실행")
        print("브라우저에서 http://localhost:8080/document-generator 가 열립니다.")
        print("="*60)
        
        if not self.gui_dir.exists():
            print(f"❌ GUI 디렉토리가 없습니다: {self.gui_dir}")
            input("Enter를 눌러 메뉴로 돌아가세요...")
            return
            
        original_dir = os.getcwd()
        os.chdir(self.gui_dir)
        
        try:
            print(f"📍 서버 시작 위치: {self.gui_dir}")
            print(f"🔗 접속 주소: http://localhost:8080/document-generator")
            
            server_process = subprocess.Popen([
                sys.executable, "main.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            print(f"⏳ 서버 시작 대기 중... (3초)")
            time.sleep(3)
            
            # 서버 상태 확인
            if server_process.poll() is not None:
                stdout, stderr = server_process.communicate()
                print(f"❌ 서버 시작 실패:")
                print(stdout)
                input("Enter를 눌러 메뉴로 돌아가세요...")
                return
            
            print(f"✅ 서버 시작 성공")
            
            try:
                webbrowser.open("http://localhost:8080/document-generator")
                print(f"🌐 브라우저 열리지 않으면 직접 접속하세요.")
            except Exception as e:
                print(f"⚠️ 브라우저 자동 열기 실패: {e}")
            
            print(f"\n🛑 서버 종료하려면 Ctrl+C 누르세요.")
            print("메뉴로 돌아가려면 서버를 종료하세요.")
            server_process.wait()
            
        except KeyboardInterrupt:
            print(f"\n🚀 서버 종료 중...")
            server_process.terminate()
            server_process.wait()
            print(f"✅ 서버 종료 완료")
        except Exception as e:
            print(f"❌ 실행 실패: {e}")
            if 'server_process' in locals():
                server_process.terminate()
            input("Enter를 눌러 메뉴로 돌아가세요...")
        finally:
            os.chdir(original_dir)
    
    def run_gui_only(self):
        """GUI 서버만 실행"""
        print("\n🌐 ProcureMate GUI 서버 실행")
        print("- 웹 인터페이스 + API 서버")
        print("="*50)
        
        if not self.gui_dir.exists():
            print("❌ GUI 디렉토리 없음")
            input("Enter를 눌러 메뉴로 돌아가세요...")
            return
            
        original_dir = os.getcwd()
        os.chdir(self.gui_dir)
        
        try:
            print("📍 서버 주소: http://localhost:8080")
            print("📋 문서생성기: http://localhost:8080/document-generator")
            print("\n⏳ 서버 시작 중...")
            
            server_process = subprocess.Popen([sys.executable, "main.py"])
            time.sleep(3)
            
            try:
                webbrowser.open("http://localhost:8080/document-generator")
                print("🌐 브라우저 열림")
            except:
                print("⚠️ 수동 접속: http://localhost:8080/document-generator")
            
            print("\n🛑 종료: Ctrl+C")
            server_process.wait()
            
        except KeyboardInterrupt:
            print("\n🛑 서버 종료 중...")
            server_process.terminate()
            server_process.wait()
            print("✅ 종료 완료")
        except Exception as e:
            print(f"❌ GUI 실행 실패: {e}")
            input("Enter를 눌러 메뉴로 돌아가세요...")
        finally:
            os.chdir(original_dir)
    
    def run_full_system(self):
        """전체 시스템 실행 (main.py)"""
        print("\n🚀 ProcureMate 전체 시스템 실행")
        print("- Slack 봇 + LLM + RAG + 문서생성 통합")
        print("="*50)
        
        try:
            subprocess.run([sys.executable, "main.py"], cwd=self.root_dir)
        except KeyboardInterrupt:
            print("\n✅ 시스템 종료")
        except Exception as e:
            print(f"❌ 실행 실패: {e}")
            input("Enter를 눌러 메뉴로 돌아가세요...")
    
    def run_document_generator_with_test(self):
        """문서 생성기 실행 (테스트 포함)"""
        print("\n📋 ProcureMate 문서 생성기 실행")
        print("- 한국 기업 양식 9종 자동 생성")
        print("="*50)
        
        # 테스트 실행 여부 확인
        while True:
            test_choice = input("테스트를 먼저 실행하시겠습니까? (y/n): ").strip().lower()
            if test_choice in ['y', 'yes', 'n', 'no']:
                break
            print("❌ y 또는 n을 입력하세요.")
        
        run_test = test_choice in ['y', 'yes']
        
        # 테스트 실행
        if run_test:
            print("\n🧪 문서 생성기 테스트 실행 중...")
            test_script = self.root_dir / "test_document_generator.py"
            if test_script.exists():
                try:
                    result = subprocess.run([sys.executable, str(test_script)], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print("✅ 테스트 통과")
                    else:
                        print("❌ 테스트 실패")
                        print("⚠️ 테스트 실패했지만 계속 진행")
                except Exception as e:
                    print(f"❌ 테스트 실행 오류: {e}")
            else:
                print("⚠️ 테스트 스크립트 없음")
        
        # GUI 서버 시작
        self.run_gui_only()
    
    def run(self):
        """메인 실행 루프"""
        while True:
            choice = self.show_main_menu()
            
            if choice == 1:
                self.quick_start()
            elif choice == 2:
                self.run_gui_only()
            elif choice == 3:
                self.run_full_system()
            elif choice == 4:
                self.run_document_generator_with_test()
            elif choice == 5:
                print("👋 ProcureMate 실행기를 종료합니다.")
                break

def main():
    """메인 함수"""
    try:
        runner = ProcureMateRunner()
        runner.run()
    except KeyboardInterrupt:
        print("\n👋 사용자 중단")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
