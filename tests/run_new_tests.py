#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path
import os

def run_tests():
    """모든 테스트 실행"""
    
    # 테스트 디렉토리로 이동
    test_dir = Path(__file__).parent
    os.chdir(test_dir)
    
    print("🚀 ProcureMate 새 모듈 테스트 시작")
    print("=" * 50)
    
    # 테스트 파일 목록
    test_files = [
        "test_g2b_api.py",
        "test_coupang_api.py", 
        "test_data_processor.py",
        "test_advanced_rag.py",
        "test_document_generator.py",
        "test_api_handlers.py",
        "test_integration.py"
    ]
    
    results = {}
    
    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"⚠️  {test_file} 파일이 존재하지 않습니다")
            continue
            
        print(f"\n📋 {test_file} 실행 중...")
        print("-" * 30)
        
        try:
            # pytest 실행
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_file, 
                "-v", 
                "--tb=short",
                "--capture=no"
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"✅ {test_file} 테스트 통과")
                results[test_file] = "PASS"
            else:
                print(f"❌ {test_file} 테스트 실패")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                results[test_file] = "FAIL"
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_file} 테스트 시간 초과")
            results[test_file] = "TIMEOUT"
        except Exception as e:
            print(f"💥 {test_file} 테스트 오류: {str(e)}")
            results[test_file] = "ERROR"
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_file, status in results.items():
        if status == "PASS":
            print(f"✅ {test_file}: 통과")
            passed += 1
        else:
            print(f"❌ {test_file}: {status}")
            failed += 1
    
    print(f"\n📈 총 {len(results)}개 테스트 중 {passed}개 통과, {failed}개 실패")
    
    if failed == 0:
        print("🎉 모든 테스트 통과!")
        return True
    else:
        print("⚠️  일부 테스트가 실패했습니다")
        return False

def run_single_test(test_name):
    """특정 테스트만 실행"""
    test_file = f"test_{test_name}.py"
    
    if not Path(test_file).exists():
        print(f"❌ {test_file} 파일이 존재하지 않습니다")
        return False
    
    print(f"🚀 {test_file} 단일 테스트 실행")
    print("-" * 30)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            test_file,
            "-v",
            "--tb=long",
            "--capture=no"
        ], timeout=60)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"💥 테스트 실행 오류: {str(e)}")
        return False

def install_test_dependencies():
    """테스트 의존성 설치"""
    print("📦 테스트 의존성 설치 중...")
    
    dependencies = [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-mock>=3.10.0"
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                          check=True, capture_output=True)
            print(f"✅ {dep} 설치 완료")
        except subprocess.CalledProcessError as e:
            print(f"❌ {dep} 설치 실패: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 특정 테스트 실행
        test_name = sys.argv[1]
        success = run_single_test(test_name)
    else:
        # 의존성 설치 확인
        try:
            import pytest
        except ImportError:
            install_test_dependencies()
        
        # 모든 테스트 실행
        success = run_tests()
    
    sys.exit(0 if success else 1)
