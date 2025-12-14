# Story Graph Increments Diagram

```mermaid
graph TB
    subgraph Increments["Story Graph Increments"]
        I1["1. User Manually Drops Config In to AI Chat<br/>Priority: 1"]
        I2["2. Simplest MCP<br/>Priority: 2"]
        I3["3. Inject Content<br/>Priority: 4"]
        I4["4. Save Content<br/>Priority: 5"]
        I5["5. Later<br/>Priority: 6"]
        I6["6. Inject / Store Content<br/>Priority: 7"]
        I7["7. Code Scanner<br/>Priority: 8"]
    end

    subgraph Epic1["Build Agile Bots"]
        E1A["Generate MCP Tools"]
        E1B["Generate CLI"]
    end

    subgraph Epic2["Invoke Bot"]
        E2A["Init Project"]
        E2B["Invoke Bot Tool"]
        E2C["Invoke MCP"]
        E2D["Invoke CLI"]
    end

    subgraph Epic3["Execute Behavior Actions"]
        E3A["Gather Context"]
        E3B["Decide Planning Criteria Action"]
        E3C["Build Knowledge Action"]
        E3D["Render Output"]
        E3E["Validate Knowledge & Content Against Rules"]
        E3F["Suggest Bot Corrections"]
    end

    subgraph ScannerSubEpic["Integrate Code Scanners into Validation Workflow"]
        S1["Register and Load Code Scanners<br/>- Discover Scanners<br/>- Load Scanner Classes"]
        S2["Execute Code Scanners<br/>- Runs After Build Knowledge<br/>- Runs After Render Output<br/>- Runs Before AI Validation"]
        S3["Detect Violations<br/>- Regex Patterns<br/>- AST Parsing<br/>- File Structure Analysis"]
        S4["Collect and Report Violations<br/>- Collects from All Scanners<br/>- Reports with Location Context"]
    end

    I1 --> Epic1
    I1 --> Epic2
    I1 --> Epic3
    
    I2 --> Epic1
    I2 --> Epic2
    I2 --> Epic3
    
    I3 --> Epic2
    I3 --> Epic3
    
    I4 --> Epic2
    I4 --> Epic3
    
    I6 --> Epic1
    I6 --> Epic2
    I6 --> Epic3
    
    I7 --> Epic3
    Epic3 --> E3E
    E3E --> ScannerSubEpic
    ScannerSubEpic --> S1
    ScannerSubEpic --> S2
    ScannerSubEpic --> S3
    ScannerSubEpic --> S4

    style I1 fill:#e1f5ff
    style I2 fill:#e1f5ff
    style I3 fill:#fff4e1
    style I4 fill:#fff4e1
    style I5 fill:#f0f0f0
    style I6 fill:#e8f5e9
    style I7 fill:#fce4ec
    style ScannerSubEpic fill:#f3e5f5
```

## Increment Details

### Inject / Store Content (Priority 7)
**Stories included:**
- **Build Agile Bots → Generate MCP Tools:**
  - Store Context Files
  - Stores Activity for Initialize Project Action

- **Invoke Bot → Invoke MCP:**
  - Save Through MCP

- **Invoke Bot → Invoke CLI:**
  - Save Through CLI

- **Execute Behavior Actions → Gather Context:**
  - Load + Inject Guardrails
  - Gather Context Saves To Context Folder

- **Execute Behavior Actions → Decide Planning Criteria Action:**
  - Save Final Assumptions and Decisions

- **Execute Behavior Actions → Build Knowledge:**
  - Load + Inject Knowledge Graph
  - Save Knowledge Graph

- **Execute Behavior Actions → Render Output:**
  - Load+ Inject Content Into Instructions
  - Save Content

- **Execute Behavior Actions → Validate Knowledge & Content Against Rules:**
  - Run Diagnostics + inject Results

### Code Scanner (Priority 8)
**Stories included:**
- **Execute Behavior Actions → Validate Knowledge & Content Against Rules → Integrate Code Scanners into Validation Workflow:**
  - **Register and Load Code Scanners:**
    - Discover Scanners from rule.json
    - Load Scanner Classes
  
  - **Execute Code Scanners:**
    - Run Scanners After Build Knowledge
    - Run Scanners After Render Output
    - Run Scanners Before AI Validation
  
  - **Detect Violations:**
    - Detect Violations Using Regex Patterns
    - Detect Violations Using AST Parsing
    - Detect Violations Using File Structure Analysis
  
  - **Collect and Report Violations:**
    - Collect Violations from All Scanners
    - Report Violations with Location Context

