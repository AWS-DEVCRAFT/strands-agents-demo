# AWS DEVCRAFT strands-agents-demo
AWS DEVCRAFT strands agents demo repository

This repository contains practical demonstrations of the **AWS Strands Agents** framework, showcasing how to build intelligent multi-agent systems using Amazon Bedrock and MCP (Model Context Protocol) integrations.

📖 **[한국어 README](README_ko.md)** | 🌐 **[Strands Agents SDK user guide](https://strandsagents.com/latest/documentation/docs/)** | 🔧 **[MCP Protocol](https://modelcontextprotocol.io/)**

## 🚀 Framework Features

- **🧠 LLM-Powered**: Amazon Bedrock Claude models for intelligent agent behavior
- **🔧 Tool Integration**: MCP (Model Context Protocol) for seamless external tool connectivity
- **🤝 Multi-Agent Collaboration**: Orchestrator patterns with specialized agent roles
- **📊 Structured Outputs**: JSON, HTML, and other formatted result generation
- **🔄 Workflow Orchestration**: Complex business process automation through agent coordination

## 📁 Demo Contents

- [🏠 Real Estate Research Agent](demo/realestate-research-agent) - Multi-agent system for auction property analysis and ROI calculation
- [🤖 QnA RAG Agent](demo/qna-rag-agent) - Customer support chatbot with knowledge base integration

## Getting Started

To get started with the Strands Agents demos:

1. **Prerequisites**: Ensure you have access to [Amazon Bedrock](https://aws.amazon.com/bedrock/)
2. **Clone Repository**: `git clone` this repository
3. **Choose Demo**: Navigate to one of the demo folders above
4. **Follow Instructions**: Each demo has detailed setup instructions in its README

### Core Dependencies

```bash
pip install strands-agents
pip install bedrock-agentcore
pip install strands-agents-tools
pip install python-dotenv>=1.1.0
pip install boto3
```

### Enable AWS IAM permissions for Bedrock

The AWS identity you assume from your environment (which is the [*Studio/notebook Execution Role*](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html) from SageMaker, or could be a role or IAM User for self-managed notebooks or other use-cases), must have sufficient [AWS IAM permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html) to call the Amazon Bedrock service.

To grant Bedrock access to your identity, you can:

- Open the [AWS IAM Console](https://us-east-1.console.aws.amazon.com/iam/home?#)
- Find your [Role](https://us-east-1.console.aws.amazon.com/iamv2/home?#/roles) (if using SageMaker or otherwise assuming an IAM Role), or else [User](https://us-east-1.console.aws.amazon.com/iamv2/home?#/users)
- Select *Add Permissions > Create Inline Policy* to attach new inline permissions, open the *JSON* editor and paste in the below example policy:

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

> ⚠️ **Note 1:** With Amazon SageMaker, your notebook execution role will typically be *separate* from the user or role that you log in to the AWS Console with. If you'd like to explore the AWS Console for Amazon Bedrock, you'll need to grant permissions to your Console user/role too.

> ⚠️ **Note 2:** For top level folder changes, please reach out to the GitHub mainterners.

For more information on the fine-grained action and resource permissions in Bedrock, check out the [Bedrock Developer Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/).

## Contributing

We welcome community contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file.
