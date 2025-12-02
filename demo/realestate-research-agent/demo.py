import os
from dotenv import load_dotenv
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from botocore.config import Config
from strands.models import BedrockModel
from strands import Agent
from strands.tools import tool
from strands_tools import current_time, file_write, file_read, calculator, http_request

# 환경변수 설정
os.environ["BYPASS_TOOL_CONSENT"] = "true"
os.environ["AUCTION1_LOGIN_ID"] = "your_id"
os.environ["AUCTION1_LOGIN_PASSWORD"] = "your_password"
os.environ["NAVER_MAPS_CLIENT_ID"] = "your_client_id"
os.environ["NAVER_MAPS_CLIENT_SECRET"] = "your_client_secret"
os.environ["NAVER_CLIENT_API"] = "your_client_api"
os.environ["NAVER_CLIENT_SECRET"] = "your_client_secret"
load_dotenv(dotenv_path=".env", override=True)

# 프롬프트 정의
매물_수집_프롬프트 = f'''
# 1단계: 매물 수집 에이전트
당신은 경매매물 수집을 담당합니다.

## 목표 (Goal)
옥션원(auction1.co.kr) 사이트에서 특정 지역의 부동산 경매 매물을 조회하세요.

## 업무 원칙 (Principles)
Playwright MCP 도구를 사용하세요.
1. 옥션원 포털 접속 및 로그인
  - 아이디: {os.environ["AUCTION1_LOGIN_ID"]}
  - 비밀번호: {os.environ["AUCTION1_LOGIN_PASSWORD"]}
2. 검색 조건 설정:
   - 지역: 사용자 쿼리 지역
   - 물건 종류: 아파트, 오피스텔
   - 진행 상태: 입찰 예정
3. 각 매물에서 다음 정보 추출:
   - 사건번호
   - 물건 주소
   - 감정가
   - 최저가
   - 유찰 횟수
   - 입찰 기일
   - 권리관계 요약 (근저당, 전세권, 가압류 등)
4. 폴백 루틴: 아이디, 비밀번호가 정상적이지 않다고 판정
   - `asset/강남구_아파트_251127.json` 매물을 대체사용하세요.

## 출력 형태 (Output)
json
[{{
  "case_number": "2024타경12345",
  "address": "서울 강남구 역삼동 123-45",
  "appraisal_value": 500000000,
  "minimum_bid": 350000000,
  "failed_count": 2,
  "bid_date": "2025-12-15",
  "encumbrances": "근저당 2억, 전세권 1억"
}}]

## 출력물 (Artifact)
`output/지역명_yymmdd_1_listing.json`
'''

입지_분석_프롬프트 = '''
# 2단계: 위치 분석 에이전트
당신은 부동산 입지 분석 전문가입니다.

## 목표 (Goal)
매물의 입지적 가치를 평가하세요. 네이버 지도 MCP 도구를 활용하세요.

## 업무 원칙 (Principles)
1. 매물 주소를 근거로 좌표를 획득하세요. 
2. 교통 접근성: 매물 반경에 위치한 교통편의시설을 파악하세요. 
   - 반경 500m 내 지하철역
   - 반경 1km 내 버스 정류장
3. 생활 편의시설: 매물 반경에 위치한 생활편의시설을 파악하세요. 
   - 반경 500m 내 대형마트, 편의점
   - 반경 1km 내 병원, 학교
4. 폴백 루틴: 네이버 지도와 협업할 수 없는 경우
   - 더 이상 시도하지 입지 분석 단계를 건너띄세요.

## 출력 형태 (Output)
json
{
  "location_score": 85,  # 0-100점
  "subway_distance": 250,  # 미터
  "nearest_station": "역삼역 3번 출구",
  "schools": ["역삼초등학교", "역삼중학교"],
  "market_price_nearby": 800000000  # 주변 실거래가 평균
}

## 출력물 (Artifact)
`output/지역명_yymmdd_2_location.json`
'''

권리_분석_프롬프트='''
# 3단계: 권리관계 분석 에이전트
당신은 경매 권리관계 분석 전문가입니다.

## 목표 (Goal)
매물의 권리관계를 분석하고 인수/소멸 여부를 판단합니다.

## 업무 원칙 (Principles)
분석 기준:
1. 근저당권:
   - 설정일자가 경매 기일보다 선순위면 인수
   - 후순위면 소멸
2. 전세권/임차권:
   - 대항력 있는 임차인 확인
   - 보증금 규모 파악
3. 가압류/가처분:
   - 소멸 여부 확인
4. 총 인수 부담액 계산

## 출력 형태 (Output)
json
{
  "total_encumbrance": 150000000,  # 인수해야 할 총액
  "senior_mortgage": 100000000,
  "lease_deposits": 50000000,
  "risk_level": "medium",  # low/medium/high
  "clearance_cost": 10000000  # 예상 명도 비용
}

## 출력물 (Artifact)
`output/지역명_yymmdd_3_right.json`
'''

ROI_계산_프롬프트 = '''
# 4단계: ROI 계산 에이전트
당신은 경매 투자 수익률 분석 전문가입니다.

## 목표 (Goal)
매물의 예상 ROI를 계산하고 투자 가치를 평가합니다.

## 업무 원칙 (Principles)
입력:
- 최저가 (minimum_bid)
- 주변 시세 (market_price_nearby)
- 인수 부담액 (total_encumbrance)
- 명도 비용 (clearance_cost)

계산 공식:
1. 예상 낙찰가 = 최저가 × (1 + 유찰횟수 × 0.05)  # 유찰 시 할인율 반영
2. 총 투자금 = 낙찰가 + 인수부담액 + 명도비용 + 취득세(4.6%)
3. 예상 매각가 = 주변시세 × 0.95  # 보수적 추정
4. 순이익 = 매각가 - 총투자금 - 양도세(추정)
5. ROI = (순이익 / 총투자금) × 100

평가 기준:
1. ROI > 30%: 우수
2. 위치 점수 > 70점: 양호
3. 권리관계 리스크 = low: 안전
4. 유찰 횟수 > 1: 저가 낙찰 가능성

최종 등급:
- S급: ROI>50%, 위치>80, 리스크 low
- A급: ROI>30%, 위치>70, 리스크 low/medium
- B급: ROI>20%, 위치>60
- C급: ROI>10%
- D급: 투자 비추천

## 출력 형태 (Output)
json
{
  "expected_bid_price": 360000000,
  "total_investment": 420000000,
  "expected_sale_price": 760000000,
  "net_profit": 280000000,
  "roi_percentage": 66.7,
  "investment_grade": "A"  # S/A/B/C/D
}

## 출력물 (Artifact)
`output/지역명_yymmdd_4_roi.csv`
'''

오케스트레이터_프롬프트='''
# 경매 매물 종합평가 에이전트
당신은 경매 매물 종합 평가 전문가입니다. 경매 매물 분석팀을 이끄는 총괄 매니저이며 팀원 에이전트를 활용해 목적을 달성합니다. 

## 목표 (Goal)
모든 분석 결과를 종합하여 투자 추천 여부를 결정합니다. Human-in-the-loop 는 배제합니다.

## 업무 원칙 (Principles)
당신의 팀원 에이전트에게 적합하게 관심사를 분리하고 업무를 위임합니다.
1. 매물 수집 에이전트 → 강남구 경매 매물 리스트 수집
2. 각 매물에 대해 병렬 실행:
   - 위치 분석 에이전트
   - 권리관계 분석 에이전트
3. ROI 계산 에이전트 → 수익률 계산
4. 종합 평가 에이전트 → 최종 등급 부여
5. 결과를 ROI 순으로 정렬하여 상위 5개 매물 리포트 생성

## 출력물 (Artifact)
`output/지역명_yymmdd_5_report.html`
'''

# MCP 클라이언트 설정
PLAYWRIGHT_MCP = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="npx", args=["@playwright/mcp@latest"])
))

NAVER_MAP_MCP = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="uv", 
        args=["run", "--directory", os.path.join(os.getcwd(), "naver-map-mcp/src"), os.path.join(os.getcwd(), "naver-map-mcp/src/naver_map_mcp")], 
        env={
            "NAVER_MAPS_CLIENT_ID" : os.environ["NAVER_MAPS_CLIENT_ID"],
            "NAVER_MAPS_CLIENT_SECRET" : os.environ["NAVER_MAPS_CLIENT_SECRET"],
            "NAVER_CLIENT_API" : os.environ["NAVER_CLIENT_API"],
            "NAVER_CLIENT_SECRET" : os.environ["NAVER_CLIENT_SECRET"]}
    )
))

# 모델 설정
model = BedrockModel(
    model_id="global.anthropic.claude-opus-4-5-20251101-v1:0",
    region_name="ap-northeast-2",
    boto_client_config=Config(read_timeout=1000)
)

# 전문 에이전트 정의
listing_agent = Agent(
    model=model,
    system_prompt=매물_수집_프롬프트,
    tools=[current_time, PLAYWRIGHT_MCP, file_write]
)

location_agent = Agent(
    model=model,
    system_prompt=입지_분석_프롬프트,
    tools=[current_time, NAVER_MAP_MCP, http_request, file_read, file_write]
)

right_agent = Agent(
    model=model,
    system_prompt=권리_분석_프롬프트,
    tools=[current_time, file_read, file_write, calculator]
)

roi_agent = Agent(
    model=model,
    system_prompt=ROI_계산_프롬프트,
    tools=[file_read, file_write, calculator]
)

# 에이전트 도구 래퍼
@tool
def listing(query: str):
    """
    경매매물 수집 에이전트를 호출합니다.
    옥션원(auction1.co.kr) 사이트에서 특정 지역의 부동산 경매 매물을 조회할 수 있습니다.
    """
    try:
        response = listing_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in research assistant: {str(e)}"

@tool
def location(query: str):
    """
    위치 분석 에이전트를 호출합니다.
    매물의 위치적 가치를 평가합니다.
    """
    try:
        response = location_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in location assistant: {str(e)}"

@tool
def right(query: str):
    """
    권리 분석 에이전트를 호출합니다.
    매물의 권리관계를 분석하고 인수/소멸 여부를 판단합니다.
    """
    try:
        response = right_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in rights assistant: {str(e)}"

@tool
def roi(query: str):
    """
    ROI 계산 에이전트를 호출합니다.
    매물의 예상 ROI를 계산하고 투자 가치를 평가합니다.
    """
    try:
        response = roi_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in ROI assistant: {str(e)}"

# 오케스트레이터 에이전트
realestate_research_agency = Agent(
    model=model,
    system_prompt=오케스트레이터_프롬프트,
    tools=[listing, location, right, roi, current_time, file_read, file_write]
)

# 메인 실행
if __name__ == "__main__":
    response = realestate_research_agency("서울 강남권 베스트 아파트 매물을 나열해보세요!")
    print(response)
