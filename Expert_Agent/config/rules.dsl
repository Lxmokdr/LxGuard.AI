RULE "Project Initialization Security"
  VERSION: "1.0.0"
  PRIORITY: 10
  DESCRIPTION: "Controls access to project initialization documentation with strict security"
  
  WHEN
    intent IS "ProjectInitialization"
    AND user.role IN ["admin", "employee"]
  
  THEN
    ALLOW documents: ["installation.md", "create_next_app.md"]
    FORBID documents: ["deployment.md", "production.md"]
    STRUCTURE: step_by_step
    EXCLUDE intents: ["Deployment", "Docker", "Production"]
    REQUIRE citations: true
    MAX_LENGTH: 300

---

RULE "Environment Setup Access"
  VERSION: "1.0.0"
  PRIORITY: 9
  DESCRIPTION: "Environment setup requires installation documentation"
  
  WHEN
    intent IS "EnvironmentSetup"
    AND user.role IN ["admin", "employee"]
  
  THEN
    ALLOW documents: ["installation.md", "basic_commands.md"]
    FORBID documents: ["deployment.md"]
    STRUCTURE: step_by_step
    EXCLUDE intents: ["Deployment"]
    REQUIRE citations: true
    MAX_LENGTH: 250

---

RULE "Deployment Access Control"
  VERSION: "2.0.0"
  PRIORITY: 8
  DESCRIPTION: "Restricts deployment information to authorized users only"
  
  WHEN
    intent IS "Deployment"
    AND user.role IN ["admin", "employee"]
  
  THEN
    ALLOW documents: ["deployment.md"]
    FORBID documents: ["create_next_app.md", "installation.md"]
    STRUCTURE: step_by_step
    EXCLUDE intents: ["Setup", "ProjectInitialization"]
    REQUIRE citations: true
    MAX_LENGTH: 400
  
  CONFLICTS_WITH: ["RULE_PROJECT_INIT"]

---

RULE "Rendering Concepts"
  VERSION: "1.0.0"
  PRIORITY: 8
  DESCRIPTION: "Rendering questions require rendering guide"
  
  WHEN
    intent IS "Rendering"
  
  THEN
    ALLOW documents: ["rendering.md"]
    FORBID documents: ["deployment.md"]
    STRUCTURE: conceptual_then_example
    EXCLUDE intents: ["Deployment"]
    REQUIRE citations: true
    MAX_LENGTH: 300

---

RULE "Component Development"
  VERSION: "1.0.0"
  PRIORITY: 7
  DESCRIPTION: "Component questions require component guide"
  
  WHEN
    intent IS "ComponentDevelopment"
  
  THEN
    ALLOW documents: ["components.md"]
    FORBID documents: ["deployment.md"]
    STRUCTURE: example_driven
    EXCLUDE intents: ["Deployment"]
    REQUIRE citations: true
    MAX_LENGTH: 300

---

RULE "Routing System"
  VERSION: "1.0.0"
  PRIORITY: 7
  DESCRIPTION: "Routing questions require routing documentation"
  
  WHEN
    intent IS "Routing"
  
  THEN
    ALLOW documents: ["routing.md", "api_routes.md", "middleware.md"]
    STRUCTURE: conceptual_then_example
    REQUIRE citations: true
    MAX_LENGTH: 350

---

RULE "Server Functions"
  VERSION: "1.0.0"
  PRIORITY: 8
  DESCRIPTION: "Function questions require functions guide"
  
  WHEN
    intent IS "Functions"
  
  THEN
    ALLOW documents: ["functions.md"]
    FORBID documents: ["deployment.md"]
    STRUCTURE: conceptual_then_example
    EXCLUDE intents: ["Deployment"]
    REQUIRE citations: true
    MAX_LENGTH: 300

---

RULE "Data Fetching Patterns"
  VERSION: "1.0.0"
  PRIORITY: 7
  DESCRIPTION: "Data fetching requires functions and API documentation"
  
  WHEN
    intent IS "DataFetching"
  
  THEN
    ALLOW documents: ["functions.md", "api_routes.md"]
    STRUCTURE: example_driven
    REQUIRE citations: true
    MAX_LENGTH: 300

---

RULE "Configuration Management"
  VERSION: "1.0.0"
  PRIORITY: 6
  DESCRIPTION: "Configuration questions for authorized users"
  
  WHEN
    intent IS "Configuration"
    AND user.role IN ["admin", "employee"]
  
  THEN
    STRUCTURE: reference
    REQUIRE citations: true
    MAX_LENGTH: 250

---

RULE "General Fallback"
  VERSION: "1.0.0"
  PRIORITY: 1
  DESCRIPTION: "Default rule for general queries without specific intent"
  
  WHEN
    intent IS "General"
  
  THEN
    STRUCTURE: flexible
    REQUIRE citations: false
    MAX_LENGTH: 200
