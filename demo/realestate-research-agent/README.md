# 🏠 부동산 경매매물 분석 에이전트

## 🎯 개요

부동산 경매매물을 조회하고 권리관계, 입지분석, 인수부담비용 및 투자금 대비 ROI를 계산하여 핵심 투자 매물을 추천하는 **멀티 에이전트 시스템**입니다.

## 🚀 Strands Agents 프레임워크

이 데모는 **AWS Strands Agents** 프레임워크를 활용하여 구축되었습니다:

- **🧠 LLM 기반**: Amazon Bedrock Claude 모델을 활용한 지능형 에이전트
- **🔧 도구 통합**: MCP(Model Context Protocol)를 통한 외부 도구 연동
- **🤝 협업 패턴**: 에이전트 간 역할 분담과 협력을 통한 복잡한 업무 처리
- **📊 구조화된 출력**: JSON, HTML 등 다양한 형태의 결과물 생성

### 핵심 특징

1. **Agents as Tools**: 각 전문 에이전트를 도구로 정의하여 재사용 가능한 모듈화
2. **Orchestrator Pattern**: 총괄 에이전트가 업무를 분석하고 적절한 전문 에이전트에 위임
3. **MCP 통합**: 웹 스크래핑, 지도 API, 파일 처리 등 외부 도구와 원활한 연동

## 🏢 비즈니스 시나리오

부동산 투자 자문 컨설팅 회사를 상상해보세요. 각 분야의 전문가들이 협력하여 고객에게 최적의 투자 매물을 추천합니다:

```
👨💼 팀장 (오케스트레이터)
├── 📋 매물조사관 → 경매 사이트에서 매물 수집
├── 🗺️ 입지분석가 → 교통, 편의시설, 시세 분석
├── ⚖️ 법무팀 → 권리관계, 인수부담 분석
└── 💰 회계팀 → ROI 계산 및 투자가치 평가
```

## 🛠️ 에이전트 아키텍처

### 전문 에이전트별 역할과 도구

| 🎭 에이전트 | 🔧 도구 | 📝 용도 |
|---------|------|------|
| **📋 매물 수집** | `PLAYWRIGHT_MCP` | 옥션원 사이트 자동 접속, 로그인, 데이터 추출 |
| | `file_write` | 수집한 매물 리스트를 JSON 형태로 저장 |
| | `current_time` | 데이터 수집 시점 기록 |
| **🗺️ 입지 분석** | `NAVER_MAP_MCP` | 주소→좌표 변환, 주변 시설 검색, 실거래가 조회 |
| | `file_read/write` | 매물 데이터 읽기 및 분석 결과 저장 |
| | `http_request` | 부동산 시세 정보 웹 검색 |
| **⚖️ 권리 분석** | `file_read/write` | 권리관계 데이터 분석 및 결과 저장 |
| | `calculator` | 인수부담액, 명도비용 정밀 계산 |
| | `current_time` | 선순위/후순위 권리 판단 기준일 설정 |
| **💰 ROI 계산** | `file_read/write` | 분석 결과 통합 및 수익률 계산 |
| | `calculator` | 복잡한 ROI 수식 계산 및 등급 산정 |
| **👨💼 오케스트레이터** | `전문_에이전트들` | 각 전문 에이전트를 도구로 활용 |
| | `file_read/write` | 모든 결과 취합 및 최종 HTML 리포트 생성 |

### 🔄 워크플로우

1. **📥 요청 접수**: 사용자가 지역과 조건을 지정
2. **📋 매물 수집**: 경매 사이트에서 해당 지역 매물 크롤링
3. **🔀 병렬 분석**: 각 매물에 대해 입지/권리 분석 동시 진행
4. **💰 수익성 계산**: 모든 분석 결과를 종합하여 ROI 산출
5. **📊 리포트 생성**: 투자 등급별로 정렬된 HTML 보고서 출력

## 💡 사용 시나리오

```python
# 사용자 요청 예시
realestate_agent("서울 강남구 아파트 매물 중 ROI 20% 이상 기대되는 상위 3건 추천해줘")
```

**결과물**: 투자 등급(S/A/B/C/D)별로 분류된 매물 리스트와 상세 분석 리포트

## 🔧 설치 및 실행

1. 환경 설정

**파이썬 모듈**

```bash
pip install strands-agents
pip install bedrock-agentcore
pip install strands-agents-tools
pip install python-dotenv>=1.1.0
pip install boto3
pip install uv
# !pip install pywin32 # Windows 운영체제일 경우
```

**npx**
Playwright MCP 서버 실행을 위해 npx 도구가 필요합니다.

```bash
npm i -g npx
```

**AWS 크레덴셜**
Amazon Bedrock 과 AgentCore 서비스 권한이 있는 AWS 크레덴셜을 프로파일에 등록합니다.

```bash
aws configure --profile default
```

2. 환경변수 설정

`.env` 파일을 편집합니다. Auction1 사이트 로그인 정보, Naver Maps API 인증 정보를 제공해야합니다. 본 데모는 인증정보를 제공하지 않을 경우 샘플 매물 데이터를 사용합니다.

```
AUCTION1_LOGIN_ID=your_actual_id
AUCTION1_LOGIN_PASSWORD=your_actual_password

NAVER_MAPS_CLIENT_ID=your_actual_client_id
NAVER_MAPS_CLIENT_SECRET=your_actual_client_secret
NAVER_CLIENT_API=your_actual_client_api
NAVER_CLIENT_SECRET=your_actual_client_secret
```

3. Jupyter Notebook 또는 Python 코드 실행
```bash
jupyter notebook demo.ipynb
```

> 특히, Windows 환경에서는 IPython 상에서 비동기 인터랙션을 수행할 수 없으므로 직접 demo 파일을 실행하세요.

```bash
python demo.py
```
