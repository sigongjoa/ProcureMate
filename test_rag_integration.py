#!/usr/bin/env python3
"""
G2B/쿠팡 → RAG 통합 테스트
"""

import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.api.rag_integration_handlers import get_rag_integration_handler
from utils import get_logger

logger = get_logger(__name__)

async def test_g2b_to_rag():
    """G2B → RAG 통합 테스트"""
    print("=" * 60)
    print("G2B → RAG 통합 테스트")
    print("=" * 60)
    
    handler = get_rag_integration_handler()
    
    # G2B 검색 파라미터
    search_params = {
        'search_type': 'bid_announcements',
        'query': '사무용품',
        'limit': 5
    }
    
    try:
        result = await handler.add_g2b_data_to_rag(search_params)
        
        if result['success']:
            print(f"✓ G2B → RAG 추가 성공")
            print(f"  - 원본 데이터: {result['data']['original_count']}개")
            print(f"  - 처리된 상품: {result['data']['processed_count']}개")
            print(f"  - 처리 시간: {result['data']['processing_time']:.2f}초")
            print(f"  - RAG 총 상품: {result['rag_stats']['total_products']}개")
        else:
            print(f"✗ G2B → RAG 추가 실패: {result['message']}")
            
    except Exception as e:
        print(f"✗ G2B → RAG 테스트 오류: {str(e)}")

async def test_coupang_to_rag():
    """쿠팡 → RAG 통합 테스트"""
    print("\n" + "=" * 60)
    print("쿠팡 → RAG 통합 테스트")
    print("=" * 60)
    
    handler = get_rag_integration_handler()
    
    # 쿠팡 검색 파라미터
    search_params = {
        'query': '사무용 의자',
        'limit': 5,
        'min_price': 50000,
        'max_price': 300000
    }
    
    try:
        result = await handler.add_coupang_data_to_rag(search_params)
        
        if result['success']:
            print(f"✓ 쿠팡 → RAG 추가 성공")
            print(f"  - 원본 데이터: {result['data']['original_count']}개")
            print(f"  - 처리된 상품: {result['data']['processed_count']}개")
            print(f"  - 처리 시간: {result['data']['processing_time']:.2f}초")
            print(f"  - RAG 총 상품: {result['rag_stats']['total_products']}개")
        else:
            print(f"✗ 쿠팡 → RAG 추가 실패: {result['message']}")
            
    except Exception as e:
        print(f"✗ 쿠팡 → RAG 테스트 오류: {str(e)}")

async def test_rag_data_summary():
    """RAG 데이터 요약 테스트"""
    print("\n" + "=" * 60)
    print("RAG 데이터 요약 테스트")
    print("=" * 60)
    
    handler = get_rag_integration_handler()
    
    try:
        result = await handler.get_rag_data_summary()
        
        if result['success']:
            data = result['data']
            print(f"✓ RAG 데이터 요약 조회 성공")
            print(f"  - 총 상품 수: {data['total_products']}개")
            print(f"  - 하이브리드 검색 준비: {data['hybrid_search_ready']}")
            print(f"  - 마지막 업데이트: {data['last_updated']}")
            
            if data['source_distribution']:
                print("  - 소스별 분포:")
                for source, count in data['source_distribution'].items():
                    print(f"    * {source}: {count}개")
                    
            if data['sample_products']:
                print(f"  - 샘플 상품: {len(data['sample_products'])}개")
        else:
            print(f"✗ RAG 데이터 요약 실패: {result['message']}")
            
    except Exception as e:
        print(f"✗ RAG 데이터 요약 테스트 오류: {str(e)}")

async def test_rag_search():
    """RAG 검색 테스트"""
    print("\n" + "=" * 60)
    print("RAG 검색 테스트")
    print("=" * 60)
    
    handler = get_rag_integration_handler()
    
    # 검색 테스트 케이스들
    test_queries = [
        "사무용 의자",
        "책상",
        "사무용품"
    ]
    
    for query in test_queries:
        try:
            result = await handler.search_rag_data(query, limit=3)
            
            if result['success']:
                data = result['data']
                print(f"✓ 검색 '{query}': {data['total_found']}개 결과 ({data['processing_time']:.3f}초)")
                
                for i, item in enumerate(data['results'][:2]):
                    metadata = item.get('metadata', {})
                    similarity = 1 - item.get('distance', 0) if item.get('distance') else 'N/A'
                    print(f"  {i+1}. {metadata.get('name', 'Unknown')} ({metadata.get('source', 'unknown')}) - 유사도: {similarity}")
            else:
                print(f"✗ 검색 '{query}' 실패: {result['message']}")
                
        except Exception as e:
            print(f"✗ 검색 '{query}' 오류: {str(e)}")

async def main():
    """메인 테스트 실행"""
    print("G2B/쿠팡 → RAG 통합 시스템 테스트 시작")
    print("=" * 60)
    
    # 순차 테스트 실행
    await test_g2b_to_rag()
    await test_coupang_to_rag()
    await test_rag_data_summary()
    await test_rag_search()
    
    print("\n" + "=" * 60)
    print("모든 테스트 완료!")
    print("=" * 60)
    
    # 웹 브라우저에서 테스트할 수 있는 URL 안내
    print("\n웹 브라우저에서 테스트:")
    print("1. GUI 서버 실행: python gui/main.py")
    print("2. http://localhost:8000 접속")
    print("3. G2B 테스트 → 검색 → 'RAG에 추가' 버튼 클릭")
    print("4. 쿠팡 테스트 → 검색 → 'RAG에 추가' 버튼 클릭")
    print("5. RAG 분석 → 데이터 상태 확인")

if __name__ == "__main__":
    asyncio.run(main())
