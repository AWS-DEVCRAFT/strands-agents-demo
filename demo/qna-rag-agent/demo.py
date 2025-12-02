import os
import time
from datetime import datetime
from typing import List, Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from strands import Agent
from strands.models import BedrockModel
from strands_tools import retrieve, http_request, file_read, file_write, editor


class ChatbotResponse(BaseModel):
    """챗봇 응답 구조"""
    summary: str = Field(description="핵심 답변을 2-3문장으로 요약")
    detailed_content: str = Field(description="업무 원칙에 맞추어 작성한 답변")
    related_info: str = Field(description="관련 센터 연락처, 홈페이지 링크 등")


class ReferenceSource(BaseModel):
    """참고자료 구조"""
    type: Literal["FAQ", "홈페이지", "공지사항", "기타"] = Field(description="자료 유형")
    title: str = Field(description="자료 제목")
    source: str = Field(description="URL 또는 상세 정보")
    relevance: str = Field(description="해당 자료가 답변과 어떻게 연관되는지 간단 설명")


class ChatbotMetadata(BaseModel):
    """메타데이터 구조"""
    category: Literal["체력측정", "사이트", "기타", "운동처방"] = Field(description="답변 카테고리")
    topic: Literal["예약", "측정", "튼튼머니", "체력증진교실", "회원가입", "기타"] = Field(description="답변 주제")
    created_at: str = Field(description="YYYY-MM-DD HH:MM:SS 형식")
    reliability: Literal["높음", "보통", "낮음"] = Field(description="답변 신뢰도")


class ChatbotOutput(BaseModel):
    """챗봇 최종 출력 구조"""
    question: str = Field(description="사용자의 원본 질문을 명확하고 완전한 문장으로 정리")
    response: ChatbotResponse = Field(description="챗봇 응답 내용")
    references: List[ReferenceSource] = Field(description="참고한 자료 목록")
    metadata: ChatbotMetadata = Field(description="답변 메타데이터")


def setup_environment():
    """환경 변수 설정"""
    # 도구 사용 동의 자동화
    os.environ["BYPASS_TOOL_CONSENT"] = "true"
    
    # Amazon Bedrock 정보
    os.environ["AWS_REGION"] = "ap-northeast-2"
    os.environ["BEDROCK_MODEL_ID"] = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
    os.environ["BEDROCK_KB_ID"] = "your_kb_id"
    os.environ["AGENTCORE_MEMORY_ID"] = "your_memory_id"
    
    # dotenv 설정 적재
    load_dotenv(dotenv_path=".env", override=True)


def setup_memory():
    """AgentCore Memory 설정"""
    client = MemoryClient(region_name=os.environ["AWS_REGION"])
    
    try:
        response = client.get_memory(memoryId=os.environ["AGENTCORE_MEMORY_ID"])
        print(f"Using existing memory...{response}")
    except Exception as e:
        print(e)
        print("Creating a new AgentCore memory...")
        response = client.create_memory(
            name=os.environ["AGENTCORE_MEMORY_ID"],
            description="Basic memory for testing short-term functionality"
        )
        
        completion = False
        while not completion:
            try:
                response = client.get_memory(memory_id=os.environ["AGENTCORE_MEMORY_ID"])
                completion = True
            except Exception as e:
                print(e)
                print("Waiting for memory to be created...")
                time.sleep(5)
    
    memory_id = response['memory']['id']
    print(memory_id)
    return memory_id


def create_session_manager(memory_id):
    """세션 매니저 생성"""
    chat_memory_config = AgentCoreMemoryConfig(
        memory_id=memory_id,
        session_id="test_session_id" + datetime.now().strftime("%Y%m%d%H%M%S"),
        actor_id="test_actor_id" + datetime.now().strftime("%Y%m%d%H%M%S"),
    )
    
    return AgentCoreMemorySessionManager(
        agentcore_memory_config=chat_memory_config,
        region_name=os.environ["AWS_REGION"]
    )


def create_agents(session_manager):
    """에이전트 생성"""
    챗봇_프롬프트 = f'''
# 1단계. 국민체력100 고객 상담 챗봇

## 역할 (Role)
당신은 국민체육진흥공단 국민체력100 사업의 고객 상담 전문가입니다.

## 목표 (Goal)
국민체력100 서비스(체력측정, 체력증진교실, 튼튼머니 등)에 대한 정확하고 친절한 상담을 제공하여, 국민들이 체력 관리 서비스를 원활하게 이용할 수 있도록 지원합니다.

## 업무 원칙 (Principles)
1. 가독성
  - 모든 한자어는 한글로 변환해 가독성을 높입니다.
  - 문장을 명확한 종결어미로 마무리합니다. 구어체와 불완전한 표현을 피합니다.
  - 모든 문장은 적절한 문장부호로 종결합니다.
  - 친절하고 공손한 어조를 유지합니다.
2. 문서 구조화
  - 내용상 구분이 필요하다면 한줄 공백을 추가해 문단으로 나눕니다.
  - 순서 표시에는 반드시 "1. 2. 3." 형식만 사용하세요. 비순서 나열에는 하이픈(-)을 사용하세요.
  - 기본적인 맞춤법과 오타를 정정하세요.
3. 정보 정확성
  - 체력인증센터 위치, 연락처, 예약 방법 등은 최신 정보를 제공합니다.
  - 튼튼머니 적립/사용 규정, 사업 기간 등은 정확히 안내합니다.
  - 불확실한 정보는 체력인증센터 또는 콜센터(02-1644-7110) 문의를 안내합니다.

## 참고 가능한 리소스 (External Resources)
  - `retrieve` 도구: FAQ 지식베이스에서 연관 자료를 색인/참고하세요. AWS 리전: {os.environ["AWS_REGION"]}, 지식베이스ID: {os.environ["BEDROCK_KB_ID"]}
  - `http_request` 도구: 국민체력100 홈페이지(nfa.kspo.or.kr) 및 관련 웹사이트를 색인하세요.
  - `asset/국민체력100_FAQ.csv` 파일: 유용한 정보를 찾지 못했다면 로컬 파일을 확인합니다.

## 최종 출력형식 (Output Format)
구조화된 Pydanctic 클래스 명세를 확인하세요.
'''

    레터_프롬프트 = '''
# 2단계. 국민체력100 상담 결과 안내문 작성하기

## 역할 (Role)
당신은 국민체육진흥공단 국민체력100 사업의 고객 상담 전문가이자 안내문 작성에 뛰어납니다.

## 목표 (Goal)
당신에게 주어진 국민체력100 서비스에 대한 상담 결과를 확인하세요. 문의자가 받아볼 질의응답지를 HTML 포맷으로 작성하여 로컬에 저장하십시오.

## 업무 원칙 (Principles)
1. HTML 문서 템플릿이 이미 존재합니다! (템플릿 파일: asset/qna_letter_template.html)
2. 당신에게 주어진 입력 JSON을 참고해서 HTML 템플릿 내 치환자를 변경해주세요.
3. HTML 파일의 이름은 입력 데이터를 참고하여 "output/yymmdd_카테고리_질문.html"으로 하세요.
4. 안내문 하단에는 다음 정보를 포함하세요:
   - 국민체력100 홈페이지: nfa.kspo.or.kr
   - 고객센터: 02-1644-7110
   - 튼튼머니 문의: 02-410-1414
'''

    model = BedrockModel(
        model_id=os.environ["BEDROCK_MODEL_ID"],
        region_name=os.environ["AWS_REGION"]
    )

    qnaAgent = Agent(
        system_prompt=챗봇_프롬프트,
        model=model,
        session_manager=session_manager,
        tools=[retrieve, http_request, file_read],
        structured_output_model=ChatbotOutput
    )

    letterAgent = Agent(
        system_prompt=레터_프롬프트,
        model=model,
        tools=[file_read, file_write, editor]
    )

    return qnaAgent, letterAgent


def main():
    """메인 실행 함수"""
    print("🚀 국민체력100 고객 QA 지원 에이전트 시작")
    
    # 환경 설정
    setup_environment()
    
    # 메모리 설정
    memory_id = setup_memory()
    
    # 세션 매니저 생성
    session_manager = create_session_manager(memory_id)
    
    # 에이전트 생성
    qnaAgent, letterAgent = create_agents(session_manager)
    
    # 질문 처리
    question = "튼튼머니를 적립하는 방식은 몇 가지가 있는지와, 각 방식 모두 설명해주세요."
    print(f"\n📝 질문: {question}")
    
    # QnA 에이전트 실행
    print("\n🤖 QnA 에이전트 실행 중...")
    qna_result = qnaAgent(question)
    print(f"\n✅ QnA 결과:\n{qna_result.structured_output}")
    
    # 레터 에이전트 실행
    print("\n📄 HTML 안내문 생성 중...")
    letter_result = letterAgent(f"다음 QnA 내용을 HTML 레터로 작성해 주세요: {qna_result.structured_output.model_dump_json()}")
    print(f"\n✅ 레터 생성 완료:\n{letter_result}")
    
    print("\n🎉 데모 완료!")


if __name__ == "__main__":
    main()