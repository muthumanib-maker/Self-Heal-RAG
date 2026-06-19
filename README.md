RAG-based auto-remediation starter kit for self-healing IT infrastructure — retrieves similar past incidents and uses an LLM to diagnose issues and suggest/execute fixes.

## Self-Healing RAG

A staged, beginner-friendly implementation of a Retrieval-Augmented Generation 
(RAG) system for IT/infra auto-remediation. Given a new alert, it retrieves 
similar past incidents from a vector database, asks an LLM (Claude) to diagnose 
the root cause and suggest a fix, and optionally auto-executes low-risk, 
pre-approved remediation actions — with human review required for anything 
higher-risk.

Built in 6 stages: knowledge base → retrieval → LLM diagnosis → live alert 
ingestion → tiered auto-execution → feedback loop. Each stage is independently 
testable so you can validate retrieval quality before ever wiring up automated 
execution against production systems.

## Prerequisites

- Python 3.10+
- pip
- An [Anthropic API key](https://console.anthropic.com/) (for Claude diagnosis)
- (Optional) A Slack incoming webhook URL, for posting diagnoses to Slack
- (Optional, for Stage 4+) An existing alerting tool that can send webhooks — 
  e.g. Prometheus Alertmanager, Datadog, or AWS CloudWatch + SNS
- (Optional, for Stage 5) Access/credentials to your infra automation tooling 
  (kubectl, Ansible, AWS SSM, etc.) if you want actions to actually execute 
  rather than just print what they'd do
