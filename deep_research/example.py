import asyncio
from deep_research import create_research_engine, get_available_strategies, ResearchConfig, ResearchFocus

async def main():
    print("=== 딥리서치 엔진 테스트 ===")
    
    # 사용 가능한 전략 출력
    print(f"사용 가능한 전략: {get_available_strategies()}")
    
    # 테스트 데이터
    request_data = {
        '품명': 'GPU 그래픽카드',
        '규격': 'RTX 4070, 12GB VRAM',
        '수량': '3개',
        '예상단가': '1,500,000원',
        '긴급도': '보통'
    }
    
    # 기본 전략 테스트
    engine = create_research_engine('default')
    result = await engine.conduct_research(request_data)
    
    print(f"\n=== 기본 전략 결과 ===")
    print(f"신뢰도: {result.confidence_score:.1%}")
    print(f"실행시간: {result.execution_time:.2f}초")
    print(f"데이터 소스: {', '.join(result.data_sources)}")
    print(f"발견된 제품: {result.market_analysis.get('total_products', 0)}개")
    print(f"공급업체: {len(result.supplier_evaluation)}개")
    print(f"추천사항:")
    for rec in result.recommendations:
        print(f"  - {rec}")
    
    # 가격 중심 전략 테스트
    price_engine = create_research_engine('price')
    price_result = await price_engine.conduct_research(request_data)
    
    print(f"\n=== 가격 중심 전략 결과 ===")
    print(f"권장 가격: {price_result.market_analysis.get('price_range', {}).get('recommended', 0):,}원")
    print(f"추천사항:")
    for rec in price_result.recommendations:
        print(f"  - {rec}")

if __name__ == "__main__":
    asyncio.run(main())
