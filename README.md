# Job Application Agentic AI

An intelligent multi-agent system that automates job application form filling by extracting form fields, retrieving user data from RAG corpora, and filling forms using browser automation.

## Problem Statement

Job seekers often spend hours manually filling out repetitive application forms across different company websites. Each form asks for similar information (name, email, experience, resume) but in different formats and layouts. This manual process is:

- **Time-consuming**: Filling 10+ applications can take an entire day
- **Error-prone**: Manual data entry leads to typos and inconsistencies
- **Repetitive**: Same information entered dozens of times
- **Inefficient**: No way to reuse or standardize personal data across applications

This problem affects millions of job seekers who apply to multiple positions, especially in competitive markets where volume applications are necessary.

## Why Agents?

Agents are the ideal solution for this problem because:

**1. Multi-Step Orchestration**
- Job application requires coordinated steps: form analysis → data retrieval → form filling
- Each step has different requirements and failure modes
- Agents can handle complex workflows with error recovery

**2. Domain-Specific Intelligence**
- Form extraction requires understanding HTML structures and field semantics
- Data retrieval needs intelligent matching between form fields and user data
- Form filling requires adaptive strategies for different UI patterns

**3. Autonomous Decision Making**
- Agents can decide which fields to fill based on available data
- Handle partial failures gracefully (fill what's possible, report what's missing)
- Adapt to different form layouts and validation requirements

**4. Scalability & Reusability**
- Once trained, agents can handle forms from any company
- User data stored once, reused across all applications
- System improves over time through experience

## What You Created

### Overall Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                Job Application Coordinator                   │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Form Extractor  │  │   RAG Agent     │  │ Form Filler  │ │
│  │     Agent       │  │                 │  │    Agent     │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
           │                       │                    │
           ▼                       ▼                    ▼
    ┌─────────────┐         ┌─────────────┐      ┌─────────────┐
    │ Playwright  │         │ Vertex AI   │      │ Playwright  │
    │ MCP Tool    │         │ RAG Corpus  │      │ MCP Tool    │
    │             │         │ + GCS       │      │             │
    └─────────────┘         └─────────────┘      └─────────────┘
```

**Components:**

1. **Job Application Coordinator**: Orchestrates the entire workflow
2. **RAG Agent**: Manages user data in Vertex AI RAG corpora and retrieves relevant information. *__Important__*: Please use this agent to create RAG corpus in GCS for the user profile before hand.
3. **Form Extractor Agent**: Uses Playwright to analyze forms and extract field names
4. **Form Filler Agent**: Uses Playwright to fill forms with retrieved data

**Data Flow:**
1. User provides: "Apply for [name]: [job_url]"
2. Form Extractor → extracts form fields from URL
3. RAG Agent → retrieves user data matching form fields
4. Form Filler → fills form with retrieved data
5. Coordinator → returns summary of filled/unfilled fields

## The Build

### Technologies Used

**Core Framework:**
- **Google ADK (Agent Development Kit)**: Multi-agent orchestration and LLM integration
- **Gemini 2.5 Flash**: Language model for agent reasoning and decision making

**Browser Automation:**
- **Playwright MCP**: Model Context Protocol integration for browser automation
- **Shared browser sessions**: Maintains state between form extraction and filling
- **Gemini 2.5 Flash Lite**: Language model for browser automation

**Data Management:**
- **Vertex AI RAG**: Vector search and document retrieval
- **Google Cloud Storage**: Document storage and management
- **Text Embedding 004**: Vector embeddings for semantic search
- **Gemini 2.5 Flash Lite**: Language model for data retrieval

**Development Tools:**
- **Python 3.14**: Core language
- **UV Package Manager**: Dependency management

**How to create the RAG corpus:**
Please use the RAG agent to create the RAG corpus in GCS for the user profile which has all the necessary tools to accomplish the task.

### Implementation Approach

1. **Multi-Agent Architecture**: Each agent has a specific responsibility with clear interfaces
2. **Error-Resilient Design**: Graceful degradation when data is missing or steps fail
3. **Stateful Browser Sessions**: Form extractor and filler share browser state for efficiency
4. **Semantic Data Matching**: RAG system intelligently matches form fields to user data
5. **Configurable Timeouts**: Robust handling of network and browser timeouts

### Key Features

- **User Context Extraction**: Automatically identifies which user's data to retrieve
- **Intelligent Field Mapping**: Matches form fields to user data semantically
- **Partial Success Handling**: Reports what was filled vs. what couldn't be filled
- **Browser State Persistence**: Maintains session between extraction and filling
- **Comprehensive Logging**: Full audit trail of the application process

## If I Had More Time, This Is What I'd Do

**1. Enhanced Error Recovery**

**2. Input / Output Schema Validations for LLM Agents**

**3. Data Validation & Security**
- Input sanitization for form data
- Secure credential handling for sensitive information
- API key rotation and secure storage

**4. Testing & Monitoring**
- Comprehensive unit tests for each agent
- Integration tests with mock forms
- Performance monitoring and alerting

**5. Advanced Form Understanding**
- Computer vision for CAPTCHA solving
- Dynamic form handling (multi-step, conditional fields)
- File upload automation (resume, cover letters)

**6. AI-Powered Personalization**
- Custom cover letter generation per job
- Resume tailoring based on job requirements

**7. Code Quality**
- Type safety with Pydantic schemas
- Comprehensive error handling
- Performance optimization and caching

This system represents a foundation for intelligent job application automation that could significantly reduce the time and effort required for job seekers while improving application quality and consistency.