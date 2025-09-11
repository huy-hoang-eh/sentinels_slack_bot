graph TD
    subgraph User Interface
        Slack_UI(Slack Command: /jira-summary)
    end

    subgraph Application Layer
        direction LR
        App_Command["commands/jira/summary.py"]
        App_Service["services/jira/get_summary.py"]
    end

    subgraph Domain Layer
        direction LR
        Domain_UseCase_Summary["use_case/jira/get_summary.py"]
        Domain_Entity_Agent_Planner["entity/agent/planner.py"]
        Domain_Entity_Agent_Tools["entity/agent/tools.py"]
    end

    subgraph Infrastructure Layer
        direction LR
        Infra_Slack["messaging/slack/notifier.py"]
        Infra_LLM["llm/adapter.py"]
        Infra_LLM_Gemni["llm/agent/gemini.py"]
        Infra_LLM_Claude["llm/agent/claude.py"]
    end

    %% Connections
    Slack_UI --> App_Command
    App_Command --> App_Service
    App_Command --> Infra_Slack

    App_Service --> Domain_UseCase_Summary

    Domain_UseCase_Summary --> Domain_Entity_Agent_Planner
    Domain_UseCase_Summary --> Domain_Entity_Agent_Tools

    Domain_Entity_Agent_Planner --> Infra_LLM
    Domain_Entity_Agent_Tools --> Infra_LLM

    Infra_LLM --> Infra_LLM_Gemni
    Infra_LLM --> Infra_LLM_Claude
