# 🤖 국민체력100 고객 QA 지원 에이전트

## 🎯 개요

국민체육진흥공단 국민체력100 서비스에 대한 고객 질의를 지능적으로 분석하고 관련 문서를 검색하여 정확하고 친화적인 답변을 제공하는 **RAG 기반 고객 상담 에이전트**입니다.

## 🚀 Strands Agents 프레임워크

이 데모는 **AWS Strands Agents** 프레임워크를 활용하여 구축되었습니다:

- **🧠 LLM 기반**: Amazon Bedrock Claude 모델을 활용한 지능형 에이전트
- **🔧 도구 통합**: MCP(Model Context Protocol)를 통한 외부 도구 연동
- **🤝 협업 패턴**: 에이전트 간 역할 분담과 협력을 통한 복잡한 업무 처리
- **📊 구조화된 출력**: JSON, HTML 등 다양한 형태의 결과물 생성

### 핵심 특징

1. **RAG 통합**: Amazon Bedrock 지식베이스에서 국민체력100 관련 문서를 검색하여 정확한 답변 생성
2. **메모리 기능**: Amazon Bedrock AgentCore Memory를 활용한 대화 맥락 유지
3. **구조화된 응답**: Pydantic 으로 구조화된 에이전트 출력을 명세
4. **HTML 리포트**: 고객용 안내문 자동 생성

## 🏢 비즈니스 시나리오

국민체육진흥공단 고객센터를 상상해보세요. 전문 상담사들이 협력하여 고객에게 최적의 서비스 안내를 제공합니다:

```
💼 상담 흐름
├── 🤖 고객상담챗봇 → 질문 분석 및 지식베이스 검색
└── 📝 QnA문건작성 → 고객용 안내문 HTML 생성
```

## 🛠️ 에이전트 아키텍처

### 전문 에이전트별 역할과 도구

| 🎭 에이전트 | 🔧 도구 | 📝 용도 |
|---------|------|------|
| **🤖 챗봇 상담사** | `retrieve` | Amazon Bedrock 지식베이스에서 FAQ 검색 |
| | `http_request` | 국민체력100 홈페이지 실시간 정보 조회 |
| | `file_read` | 로컬 FAQ 파일 참조 |
| | `current_time` | 답변 작성 시간 기록 |
| **📝 안내문 작성팀** | `file_read/write` | HTML 템플릿 읽기 및 개인화된 안내문 생성 |
| | `template_processor` | 고객별 맞춤 안내문 치환 및 포맷팅 |

### 🔄 워크플로우

1. **📥 질문 접수**: 고객이 국민체력100 서비스에 대해 질문
2. **🔍 정보 검색**: 지식베이스, 홈페이지, FAQ 파일에서 관련 정보 수집
3. **🤖 답변 생성**: 구조화된 JSON 형태로 상세 답변 작성
4. **📝 안내문 생성**: HTML 템플릿을 활용한 고객용 안내문 작성
5. **💾 결과 저장**: 상담 내역을 파일로 저장

## 💡 사용 시나리오

```python
# 사용자 요청 예시
qnaAgent("체력측정 예약은 어떻게 하나요?")
qnaAgent("튼튼머니는 어떻게 사용하나요?")
qnaAgent("체력증진교실 신청 방법을 알려주세요")
```

**결과물**: 
- JSON 형태의 구조화된 답변 (요약, 상세내용, 관련정보, 참고자료, 메타데이터)
- 고객용 HTML 안내문 (`output/yymmdd_카테고리_질문.html`)

## 🎯 핵심 기능

- 📚 **지식베이스 검색**: Amazon Bedrock KB를 활용한 정확한 정보 검색
- 💬 **자연어 처리**: 고객 질문 의도 파악 및 분석
- 🔍 **다중 소스 검색**: 지식베이스, 웹사이트, 로컬 파일 통합 검색
- ✨ **구조화된 답변**: 요약, 상세내용, 관련정보가 포함된 체계적 응답
- 📊 **품질 관리**: 답변 신뢰도 및 카테고리 자동 분류
- 📄 **고객 안내문**: HTML 템플릿 기반 개인화된 안내문 생성

## 🔧 설치 및 실행

### 1. 환경 설정

**필수 패키지 설치**
```bash
pip install strands-agents
pip install bedrock-agentcore
pip install strands-agents-tools
pip install "python-dotenv>=1.1.0"
pip install "pydantic>=2.0.0"
pip install boto3
```

**AWS 크레덴셜**
Amazon Bedrock과 AgentCore 서비스 권한이 있는 AWS 크레덴셜을 설정합니다.
```bash
aws configure --profile default
```

### 2. 환경변수 설정

`.env` 파일을 생성하고 다음 정보를 편집하세요:

```env
# AWS 설정
AWS_REGION=ap-northeast-2

# Amazon Bedrock 설정
BEDROCK_MODEL_ID=global.anthropic.claude-sonnet-4-5-20250929-v1:0
BEDROCK_KB_ID=your_knowledge_base_id
AGENTCORE_MEMORY_ID=your_memory_id
```

### 3. 실행

**Jupyter Notebook**
```bash
jupyter notebook demo.ipynb
```

**Python 스크립트**
```bash
python demo.py
```

## 📁 출력 파일

상담 결과는 `output/` 디렉토리에 저장됩니다:

- `yymmdd_카테고리_질문.html` - 고객용 HTML 안내문
- 상담 내역은 AgentCore Memory에 자동 저장


## ⚠️ 주의사항

- Amazon Bedrock 지식베이스 ID와 AgentCore Memory ID를 정확히 설정해야 합니다
- 지식베이스가 없는 경우 로컬 FAQ 파일을 대체 사용합니다
