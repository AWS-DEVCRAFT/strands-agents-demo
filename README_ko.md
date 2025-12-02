# AWS DEVCRAFT strands-agents-demo
AWS DEVCRAFT strands agents 데모 저장소

이 저장소는 **AWS Strands Agents** 프레임워크의 실용적인 데모를 포함하고 있으며, Amazon Bedrock과 MCP(Model Context Protocol) 통합을 사용하여 지능형 멀티 에이전트 시스템을 구축하는 방법을 보여줍니다.

🌐 **[Strands Agents 유저 가이드](https://strandsagents.com/latest/documentation/docs/)** | 🔧 **[MCP 프로토콜](https://modelcontextprotocol.io/)**

## 🚀 프레임워크 특징

- **🧠 LLM 기반**: 지능형 에이전트 동작을 위한 Amazon Bedrock Claude 모델
- **🔧 도구 통합**: 원활한 외부 도구 연결을 위한 MCP(Model Context Protocol)
- **🤝 멀티 에이전트 협업**: 전문화된 에이전트 역할을 가진 오케스트레이터 패턴
- **📊 구조화된 출력**: JSON, HTML 및 기타 형식의 결과 생성
- **🔄 워크플로우 오케스트레이션**: 에이전트 협력을 통한 복잡한 비즈니스 프로세스 자동화

## 📁 데모 내용

- [🏠 부동산 경매매물조사 에이전트](demo/realestate-research-agent) - 경매 부동산 분석 및 ROI 계산을 위한 멀티 에이전트 시스템
- [🤖 QnA RAG 에이전트](demo/qna-rag-agent) - 지식베이스 통합 고객 지원 챗봇


## 시작하기

Strands Agents 데모를 시작하려면:

1. **사전 요구사항**: [Amazon Bedrock](https://aws.amazon.com/bedrock/) 액세스 권한이 있는지 확인
2. **저장소 복제**: 이 저장소를 `git clone`
3. **데모 선택**: 위의 데모 폴더 중 하나로 이동
4. **지침 따르기**: 각 데모는 README에 자세한 설정 지침이 있습니다

### 핵심 종속성

```bash
pip install strands-agents
pip install bedrock-agentcore
pip install strands-agents-tools
pip install python-dotenv>=1.1.0
pip install boto3
```

### Bedrock을 위한 AWS IAM 권한 활성화

환경에서 가정하는 AWS ID([SageMaker의 *Studio/notebook 실행 역할*](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html) 또는 자체 관리 노트북이나 기타 사용 사례의 역할 또는 IAM 사용자)는 Amazon Bedrock 서비스를 호출할 수 있는 충분한 [AWS IAM 권한](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html)이 있어야 합니다.

ID에 Bedrock 액세스 권한을 부여하려면:

- [AWS IAM 콘솔](https://us-east-1.console.aws.amazon.com/iam/home?#) 열기
- [역할](https://us-east-1.console.aws.amazon.com/iamv2/home?#/roles)(SageMaker를 사용하거나 IAM 역할을 가정하는 경우) 또는 [사용자](https://us-east-1.console.aws.amazon.com/iamv2/home?#/users) 찾기
- *권한 추가 > 인라인 정책 생성*을 선택하여 새 인라인 권한을 연결하고, *JSON* 편집기를 열어 아래 예시 정책을 붙여넣기:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockFullAccess",
            "Effect": "Allow",
            "Action": ["bedrock:*"],
            "Resource": "*"
        }
    ]
}
```

> ⚠️ **참고 1:** Amazon SageMaker에서는 노트북 실행 역할이 일반적으로 AWS 콘솔에 로그인하는 사용자 또는 역할과 *분리*됩니다. Amazon Bedrock용 AWS 콘솔을 탐색하려면 콘솔 사용자/역할에도 권한을 부여해야 합니다.

> ⚠️ **참고 2:** 최상위 폴더 변경사항은 GitHub 관리자에게 문의하세요.

Bedrock의 세분화된 작업 및 리소스 권한에 대한 자세한 정보는 [Bedrock 개발자 가이드](https://docs.aws.amazon.com/bedrock/latest/userguide/)를 확인하세요.

## 기여하기

커뮤니티 기여를 환영합니다! 가이드라인은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

## 보안

자세한 정보는 [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications)을 참조하세요.

## 라이선스

이 라이브러리는 MIT-0 라이선스에 따라 라이선스가 부여됩니다. [LICENSE](LICENSE) 파일을 참조하세요.