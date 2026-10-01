# Skill Index

**555 unique skills** across 8 CLI skill roots — consolidated from the local agent installations (hermes, claude, codex, commandcode, cursor, agents, muse, gstack).

When two CLIs carry a byte-identical skill it is stored once, under the first CLI that had it; the other CLIs appear in the *Also in* column. 111 skills are shared by more than one CLI. Full mapping in `_aliases.json`.

| CLI | Skills |
|---|---|
| `agents` | 29 |
| `claude` | 97 |
| `codex` | 6 |
| `commandcode` | 11 |
| `cursor` | 2 |
| `gstack` | 95 |
| `hermes` | 304 |
| `muse` | 11 |

---

## agents — 29 skills

| Skill | Also in | Description |
|---|---|---|
| `archify` |  | Create polished, validated architecture, workflow, sequence, data-flow, and lifecycle/state diagrams as explorable standalone HTML with inline SVG, dark/light themes, optional trace … |
| `find-skills` |  | Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending cap… |
| `migrate-radix-to-base` |  | Migrates React projects and components from Radix UI to Base UI. Use when asked to migrate from radix, move to base-ui, convert radix primitives, or switch a shadcn project's base li… |
| `remotion-best-practices` |  | Router for all Remotion skills |
| `remotion-captions` |  | Transcribing, displaying and animating captions |
| `remotion-create` |  | Create a new Remotion video |
| `remotion-docs` |  | Search Remotion documentation |
| `remotion-interactivity` |  | Structure Remotion markup for interactivity |
| `remotion-maps` |  | Remotion Map animation knowledge |
| `remotion-markup` |  | Content, animation and effects best practices |
| `remotion-multimedia` |  | Interacting with Mediabunny |
| `remotion-render` |  | Export a Remotion video |
| `remotion-saas` |  | Build an app with Remotion |
| `remotion-studio` |  | Preview a Remotion video |
| `remotion-upgrade` |  | Upgrade Remotion, and related packages |
| `shadcn` |  | Manages shadcn components and projects — adding, searching, fixing, debugging, styling, and composing UI, including chat interfaces. Provides project context, component docs, and usa… |
| `superset-10x` |  | Personalized audit that teaches the advanced Superset features the user isn't using yet (automations, parallel agents, tasks, multi-host, terminal remote control, custom commands, MC… |
| `superset-automate` |  | Turn a recurring chore into a Superset automation. Drafts the agent prompt, confirms schedule and target, creates it with the CLI, and reviews the first run together. Use when the us… |
| `superset-browser` |  | Open, navigate, screenshot, read, click, and type in web pages from an agent. Use when the user asks to open a URL, preview or verify a running web app, check a page's console, fill … |
| `superset-computer` |  | Operate the user's real desktop apps and windows on macOS, Windows, or Linux. Use when the user asks to open or drive a native app, click or type in a desktop UI, inspect or arrange … |
| `superset-contribute` |  | Set up a Superset open-source contribution, from forking and cloning superset-sh/superset through local dev setup and the repo's rules to a merge-ready PR. Use when the user wants to… |
| `superset-doctor` |  | Diagnose and fix Superset problems such as connection failures, offline hosts, terminals not attaching, auth or update issues. Use when the user reports something broken or misbehavi… |
| `superset-feedback` |  | Collect and submit feedback about Superset (bug reports, feature requests, or general feedback) privately to the Superset team or as a public GitHub issue. Use when the user wants to… |
| `superset-integrations` |  | Discover and call the tools a connected integration exposes, such as Linear, GitHub, Sentry, or Notion, through `superset mcp`. Use when the user wants something done in a connected … |
| `superset-orchestrate` |  | Coordinate several coding agents in parallel through Superset, each in its own workspace, with follow-ups, progress reads, dependency tracking, and structured results. Use when the u… |
| `superset-page` |  | Build and publish a self-contained HTML page to Superset, then answer the comments readers pin to it. Use when the user asks to make or publish a page, turn a report, dashboard, char… |
| `superset-plugins` |  | Install Superset plugins, connect the accounts they need, and call their MCP tools through the credential proxy. Use when the user wants a plugin installed, removed, enabled, or conn… |
| `superset-setup` |  | Make a repository Superset-ready by authoring .superset/config.json with setup, teardown, and run scripts so every new workspace boots configured, then verifying with a real workspac… |
| `superset-standup` |  | Digest of what the user's Superset agents did while they were away, sweeping workspaces, tasks, and agent terminals to report what finished, what needs review, and what's blocked. Us… |

## claude — 97 skills

| Skill | Also in | Description |
|---|---|---|
| `10x` | superset | Personalized audit that teaches the advanced Superset features the user isn't using yet (automations, parallel agents, tasks, multi-host, terminal remote control, custom commands, MC… |
| `_gstack-command` | commandcode | Router for the gstack skill suite. (gstack) |
| `amazon-bedrock` | agents, cursor, pi | Builds generative AI applications on Amazon Bedrock. Covers model invocation (Converse API, InvokeModel), RAG with Knowledge Bases, Bedrock Agents, Guardrails, and AgentCore (includi… |
| `automate` | superset | Turn a recurring chore into a Superset automation. Drafts the agent prompt, confirms schedule and target, creates it with the CLI, and reviews the first run together. Use when the us… |
| `autoplan` | commandcode | Auto-review pipeline — reads the full CEO, design, eng, and DX review skills from disk and runs them sequentially with auto-decisions using 6 decision principles. (gstack) |
| `aws-ai-ml` | agents, cursor, pi | Selects, deploys, and customizes AI models on Amazon SageMaker. Fine-tuning (SFT, DPO, RLVR, RLAIF), model selection, dataset preparation, evaluation, deployment to SageMaker endpoin… |
| `aws-auth` | agents, cursor, pi | Adds user authentication to web and mobile apps with Amazon Cognito (user pools and identity pools) and the AWS Amplify client auth libraries. Covers sign-up/sign-in flows and the lo… |
| `aws-billing-and-cost-management` | agents, cursor, pi | Analyze AWS costs, find savings, manage budgets, evaluate Savings Plans and Reserved Instances, right-size EC2/Lambda/RDS/EBS with Compute Optimizer, look up service pricing, query C… |
| `aws-blocks` | agents, cursor, pi | Guides building full-stack applications with AWS Blocks — an Infrastructure-from-Code framework. Applies when creating APIs, selecting Building Blocks (KVStore, DistributedTable, Dat… |
| `aws-cdk` | agents, cursor, pi | Authors, deploys, and troubleshoots AWS infrastructure using CDK with TypeScript or Python. Covers best practices, stack architecture, and construct patterns. Applies when writing CD… |
| `aws-cloudformation` | agents, cursor, pi | Authors, validates, and troubleshoots AWS CloudFormation templates. Covers template authoring with secure defaults, local validation with either cfn-lint or cloudformation-validate, … |
| `aws-compute` | agents, cursor, pi | Provisions, scales, and operates Amazon EC2 virtual-machine workloads: instance-type selection (Graviton/Arm64, burstable T credits, GPU, instance store vs EBS), launch templates, Au… |
| `aws-containers` | agents, cursor, pi | Builds, deploys, debugs, and optimizes containerized workloads on Amazon EKS, ECS, Fargate, ECR, and Elastic Beanstalk. Covers EKS operations and add-ons; ECS task definitions, servi… |
| `aws-database` | agents, cursor, pi | Routes any task involving AWS databases — choosing, comparing, recommending, getting started with, or operating a database — to the correct service-specific skill. Supersedes general… |
| `aws-deployment` | agents, cursor, pi | Configures CI/CD pipelines using AWS CodePipeline, CodeBuild, CodeDeploy, CodeConnections, and CodeArtifact. Covers CodePipeline V2 (triggers, variables, execution modes, cross-accou… |
| `aws-iam` | agents, cursor, pi | Provides verified corrections for IAM behaviors that AI agents frequently get wrong — policy evaluation edge cases, trust policy gotchas, STS session limits, Organizations quirks, an… |
| `aws-messaging-and-streaming` | agents, cursor, pi | Guides general use of AWS messaging and streaming services. Covers Amazon SQS, Amazon SNS, Amazon EventBridge, Amazon MQ, Amazon Kinesis Data Streams, Amazon Data Firehose, Amazon Ma… |
| `aws-networking` | agents, cursor, pi | Routes AWS networking requests to the correct service skill for implementation. Covers Route 53 (DNS, health checks, routing policies, Resolver, DNS Firewall), CloudFront (caching, e… |
| `aws-observability` | agents, cursor, pi | Builds, configures, debugs, and optimizes AWS observability - operator-symptom questions and detecting Omni vs classic CloudWatch. CloudWatch: Log Insights, alarms, Dynamic Instrumen… |
| `aws-sdk-js-v3-usage` | agents, cursor, pi | AWS SDK for JavaScript v3 development patterns. Use when writing JavaScript or TypeScript code that uses AWS services via @aws-sdk/* packages (aws-sdk-js-v3), or when asked about sch… |
| `aws-sdk-python-usage` | agents, cursor, pi | AWS SDK for Python (boto3/botocore) development patterns. You MUST use this skill when writing Python code that uses AWS services via boto3 or botocore. This includes creating servic… |
| `aws-sdk-swift-usage` | agents, cursor, pi | AWS SDK for Swift development patterns. Use when writing Swift code that uses AWS services via aws-sdk-swift package. |
| `aws-security` | agents, cursor, pi | Covers AWS security services and workflows — Security Hub V2 (OCSF) findings, connectors, aggregators, automation rules, and security posture summaries; Security Hub CSPM (V1/ASFF) c… |
| `aws-serverless` | agents, cursor, pi | Routes serverless requests to a compute form factor and the skill that owns it. Applies first to Lambda, API Gateway, EventBridge, Step Functions and event-driven work while the comp… |
| `aws-storage` | agents, cursor, pi | Selects, investigates, and compares AWS object, file, and block storage services, and answers cost, performance, configuration, security, and troubleshooting questions about storage … |
| `benchmark` | commandcode | Performance regression detection using the browse daemon. (gstack) |
| `benchmark-models` | commandcode | Cross-model benchmark for gstack skills. (gstack) |
| `brag` | agents, gemini | Turn the current project website into a short, polished, shareable launch video using Hyperframes. Use when someone says "/brag", "let's brag about this", "make a launch video", "tur… |
| `browse` | commandcode | Fast headless browser for QA testing and site dogfooding. (gstack) |
| `browser` | superset | Open, navigate, screenshot, read, click, and type in web pages from an agent. Use when the user asks to open a URL, preview or verify a running web app, check a page's console, fill … |
| `canary` | commandcode | Post-deploy canary monitoring. (gstack) |
| `careful` | commandcode | Safety guardrails for destructive commands. (gstack) |
| `codex` | commandcode | OpenAI Codex CLI wrapper — three modes. (gstack) |
| `computer` | superset | Operate the user's real desktop apps and windows on macOS, Windows, or Linux. Use when the user asks to open or drive a native app, click or type in a desktop UI, inspect or arrange … |
| `connect-chrome` | claude, commandcode | Launch GStack Browser — AI-controlled Chromium with the sidebar extension baked in. |
| `context-restore` | commandcode | Restore working context saved earlier by /context-save. (gstack) |
| `context-save` | commandcode | Save working context. (gstack) |
| `contribute` | superset | Set up a Superset open-source contribution, from forking and cloning superset-sh/superset through local dev setup and the repo's rules to a merge-ready PR. Use when the user wants to… |
| `cso` | commandcode | Chief Security Officer mode. (gstack) |
| `design-consultation` | commandcode | Design consultation: understands your product, researches the landscape, proposes a complete design system (aesthetic, typography, color, layout, spacing, motion), and generates font… |
| `design-html` | commandcode | Design finalization: generates production-quality Pretext-native HTML/CSS. (gstack) |
| `design-review` | commandcode | Designer's eye QA: finds visual inconsistency, spacing issues, hierarchy problems, AI slop patterns, and slow interactions — then fixes them. (gstack) |
| `design-shotgun` | commandcode | Design shotgun: generate multiple AI design variants, open a comparison board, collect structured feedback, and iterate. (gstack) |
| `devex-review` | commandcode | Live developer experience audit. (gstack) |
| `diagram` | commandcode | Turn an English description (or mermaid source) into a diagram triplet: the source, an editable .excalidraw file you can open (gstack) |
| `doctor` | superset | Diagnose and fix Superset problems such as connection failures, offline hosts, terminals not attaching, auth or update issues. Use when the user reports something broken or misbehavi… |
| `document-generate` | commandcode | Generate missing documentation from scratch for a feature, module, or entire project. (gstack) |
| `document-release` | commandcode | Post-ship documentation update. (gstack) |
| `feedback` | superset | Collect and submit feedback about Superset (bug reports, feature requests, or general feedback) privately to the Superset team or as a public GitHub issue. Use when the user wants to… |
| `freeze` | commandcode | Restrict file edits to a specific directory for the session. (gstack) |
| `general-video` | agents | Author or edit a custom HyperFrames composition when no specialized workflow fits, or when BRIEF.md sets flow: companion. Use for longer or multi-scene pieces, brand and sizzle reels… |
| `graft` |  | This repo is indexed by graft/. For ANY task here, whether |
| `guard` | commandcode | Full safety mode: destructive command warnings + directory-scoped edits. (gstack) |
| `health` | commandcode | Code quality dashboard. (gstack) |
| `hyperframes` | agents | Mandatory entry point: read this first for any request to make, create, edit, animate, or render a video, animation, or motion graphic, including a promo, explainer, captioned clip, … |
| `hyperframes-audio` | agents | Use when audio already placed in a HyperFrames composition needs to be mixed: fade-in/fade-out, crossfade, track gain or volume, volume automation, ducking, a music bed that fights a… |
| `hyperframes-cli` | agents | Use the HyperFrames CLI development loop: init, add, catalog, capture, lint, check, snapshot, compare, grade-compare, preview, play, present, beats, keyframes, single or batch render… |
| `hyperframes-registry` | agents | Search, install, and wire registry blocks and components into HyperFrames compositions. Use BEFORE hand-building any named visual — whenever a brief, a user, or a storyboard names a … |
| `integrations` | superset | Discover and call the tools a connected integration exposes, such as Linear, GitHub, Sentry, or Notion, through `superset mcp`. Use when the user wants something done in a connected … |
| `investigate` | commandcode | Systematic debugging with root cause investigation. (gstack) |
| `ios-clean` | commandcode | Remove the DebugBridge SPM package and all #if DEBUG wiring from an iOS app. (gstack) |
| `ios-design-review` | commandcode | Visual design audit for iOS apps on real hardware. (gstack) |
| `ios-fix` | commandcode | Autonomous iOS bug fixer. (gstack) |
| `ios-qa` | commandcode | Live-device iOS QA for SwiftUI apps. (gstack) |
| `ios-sync` | commandcode | Regenerate the iOS debug bridge against the latest upstream gstack templates. (gstack) |
| `land-and-deploy` | commandcode | Land and deploy workflow. (gstack) |
| `landing-report` | commandcode | Read-only queue dashboard for workspace-aware ship. (gstack) |
| `launch-with-aws` | agents, cursor, pi | Migrates vibe-coded web applications to AWS. Handles the full workflow from analysis through migration to deployment, producing deployable AWS Blocks infrastructure code. Supports fu… |
| `learn` | commandcode | Manage project learnings. |
| `make-pdf` | commandcode | Turn any markdown file into a publication-quality PDF. (gstack) |
| `office-hours` | commandcode | YC Office Hours — two modes. (gstack) |
| `orchestrate` | superset | Coordinate several coding agents in parallel through Superset, each in its own workspace, with follow-ups, progress reads, dependency tracking, and structured results. Use when the u… |
| `page` | superset | Build and publish a self-contained HTML page to Superset, then answer the comments readers pin to it. Use when the user asks to make or publish a page, turn a report, dashboard, char… |
| `pair-agent` | commandcode | Pair a remote AI agent with your browser. (gstack) |
| `plan-ceo-review` | commandcode | CEO/founder-mode plan review. (gstack) |
| `plan-design-review` | commandcode | Designer's eye plan review — interactive, like CEO and Eng review. (gstack) |
| `plan-devex-review` | commandcode | Interactive developer experience plan review. (gstack) |
| `plan-eng-review` | commandcode | Eng manager-mode plan review. (gstack) |
| `plan-tune` | commandcode | Self-tuning question sensitivity + developer psychographic for gstack (v1: observational). (gstack) |
| `plugins` | superset | Install Superset plugins, connect the accounts they need, and call their MCP tools through the credential proxy. Use when the user wants a plugin installed, removed, enabled, or conn… |
| `qa` | commandcode | Systematically QA test a web application and fix bugs found. (gstack) |
| `qa-only` | commandcode | Report-only QA testing. (gstack) |
| `retro` | commandcode | Weekly engineering retrospective. (gstack) |
| `review` | commandcode | Pre-landing PR review. (gstack) |
| `scrape` | commandcode | Pull data from a web page. (gstack) |
| `setting-up-cloudwatch-observability` | agents, cursor, pi | Sets up CloudWatch Application Observability (also called Omni) for the first time. Covers creating an Omni Space or Domain; configuring and listing Omni access grants (who has acces… |
| `setup` | superset | Make a repository Superset-ready by authoring .superset/config.json with setup, teardown, and run scripts so every new workspace boots configured, then verifying with a real workspac… |
| `setup-browser-cookies` | commandcode | Import cookies from your real Chromium browser into the headless browse session. (gstack) |
| `setup-deploy` | commandcode | Configure deployment settings for /land-and-deploy. |
| `setup-gbrain` | commandcode | Set up gbrain for this coding agent: install the CLI, initialize a local PGLite or Supabase brain, register MCP, capture per-remote trust policy. (gstack) |
| `ship` | commandcode | Ship workflow: detect + merge base branch, run tests, review diff, bump VERSION, update CHANGELOG, commit, push, create PR. (gstack) |
| `signing-in-to-aws` | agents, cursor, pi | Gets AWS credentials for CLI/SDK access via `aws login`. Activates when a developer needs to authenticate to AWS for local development, when an AWS operation fails due to missing or … |
| `skillify` | commandcode | Codify the most recent successful /scrape flow into a permanent browser-skill on disk. (gstack) |
| `spec` | commandcode | Turn vague intent into a precise, executable spec in five phases. (gstack) |
| `standup` | superset | Digest of what the user's Superset agents did while they were away, sweeping workspaces, tasks, and agent terminals to report what finished, what needs review, and what's blocked. Us… |
| `sync-gbrain` | commandcode | Keep gbrain current with this repo's code and refresh agent search guidance in CLAUDE.md. Wraps the gstack-gbrain-sync orchestrator with state (gstack) |
| `unfreeze` | commandcode | Clear the freeze boundary set by /freeze, allowing edits to all directories again. (gstack) |

## codex — 6 skills

| Skill | Also in | Description |
|---|---|---|
| `imagegen` |  | Generate or edit raster images when the task benefits from AI-created bitmap visuals such as photos, illustrations, textures, sprites, mockups, or transparent-background cutouts. Use… |
| `openai-docs` |  | Use for Codex models/pricing, scheduled tasks, skills, settings, setup, troubleshooting, customization, automations, and self-knowledge—including 'you,' 'your,' 'this app,' or 'this … |
| `plugin-creator` |  | Create and scaffold plugin directories for Codex with a required `.codex-plugin/plugin.json`, optional plugin folders/files, valid manifest defaults, and personal-marketplace entries… |
| `review-agent` |  | Perform a read-only, defect-first review of a specified code change and return every actionable finding. Use when another agent delegates review of uncommitted changes, a base-branch… |
| `skill-creator` |  | Create or update a Codex skill with appropriately scoped instructions and any needed supporting resources. |
| `skill-installer` |  | Install Codex skills into $CODEX_HOME/skills from a curated list or a GitHub repo path. Use when a user asks to list installable skills, install a curated skill, or install a skill f… |

## commandcode — 11 skills

| Skill | Also in | Description |
|---|---|---|
| `gstack-openclaw-ceo-review` | commandcode | Use when asked to review a plan, challenge a proposal, run a CEO review, poke holes in an approach, think bigger about scope, or decide whether to expand or reduce the plan. |
| `gstack-openclaw-investigate` | commandcode | Use when asked to debug, fix a bug, investigate an error, or do root cause analysis, and when users report errors, stack traces, unexpected behavior, or say something stopped working. |
| `gstack-openclaw-office-hours` | commandcode | Use when asked to brainstorm, evaluate whether an idea is worth building, run office hours, or think through a new product idea or design direction before any code is written. |
| `gstack-openclaw-retro` | commandcode | Weekly engineering retrospective. Analyzes commit history, work patterns, and code quality metrics with persistent history and trend tracking. Team-aware with per-person contribution… |
| `hackernews-frontpage` | commandcode | Scrape the Hacker News front page (titles, points, comment counts). |
| `ponytail` |  | Forces the laziest solution that actually works, simplest, shortest, most minimal. Channels a senior dev who has seen everything: question whether the task needs to exist at all (YAG… |
| `ponytail-audit` |  | Whole-repo audit for over-engineering. Like ponytail-review, but scans the entire codebase instead of a diff: a ranked list of what to delete, simplify, or replace with stdlib/native… |
| `ponytail-debt` |  | Harvest every `ponytail:` comment in the codebase into a debt ledger, so the deliberate shortcuts and deferrals ponytail leaves behind get tracked instead of rotting into "later mean… |
| `ponytail-gain` |  | Show ponytail's measured impact as a compact scoreboard: less code, less cost, more speed, from the benchmark medians. One-shot display, not a persistent mode, and not a per-repo num… |
| `ponytail-help` |  | Quick-reference card for all ponytail modes, skills, and commands. One-shot display, not a persistent mode. Trigger: /ponytail-help, "ponytail help", "what ponytail commands", "how d… |
| `ponytail-review` |  | Code review focused exclusively on over-engineering. Finds what to delete: reinvented standard library, unneeded dependencies, speculative abstractions, dead flexibility. One line pe… |

## cursor — 2 skills

| Skill | Also in | Description |
|---|---|---|
| `gstack` |  | Router for the gstack skill suite. Sends any gstack request to the right skill (planning, review, QA, shipping, debugging, docs, security, design). For browser/QA and dogfooding it p… |
| `gstack-upgrade` |  | Upgrade gstack to the latest version. |

## gstack — 95 skills

| Skill | Also in | Description |
|---|---|---|
| `apollo-client` |  | Guide for building React applications with Apollo Client 4.x. Use this skill when: (1) setting up Apollo Client in a React project, (2) writing GraphQL queries or mutations with hook… |
| `architecture-decision-records` |  | Write and maintain Architecture Decision Records (ADRs) following best practices for technical decision documentation. Use when documenting significant technical decisions, reviewing… |
| `architecture-patterns` |  | Implement proven backend architecture patterns including Clean Architecture, Hexagonal Architecture, and Domain-Driven Design. Use this skill when designing clean architecture for a … |
| `better-auth-best-practices` |  | Configure Better Auth server and client, set up database adapters, manage sessions, add plugins, and handle environment variables. Use when users mention Better Auth, betterauth, aut… |
| `claude-api` |  | Reference for the Claude API / Anthropic SDK — model ids, pricing, params, streaming, tool use, MCP, agents, caching, token counting, model migration. TRIGGER — read BEFORE opening t… |
| `clerk-backend-api` |  | Clerk Backend REST API explorer and executor. Browse tags, inspect endpoint schemas, and execute authenticated requests. Use when listing users, managing organizations, or calling an… |
| `clerk-nextjs-patterns` |  | Advanced Next.js patterns - middleware, Server Actions, caching with |
| `clerk-testing` |  | E2E testing for Clerk apps. Use with Playwright or Cypress for auth flow |
| `clerk-webhooks` |  | Clerk webhooks for real-time events and data syncing. Verify with verifyWebhook |
| `database-migration` |  | Execute database migrations across ORMs and platforms with zero-downtime strategies, data transformation, and rollback procedures. Use when migrating databases, changing schemas, per… |
| `deploy-to-vercel` |  | Deploy applications and websites to Vercel. Use when the user requests deployment actions like "deploy my app", "deploy and give me the link", "push this live", or "create a preview … |
| `dotnet-backend-patterns` |  | Master C#/.NET backend development patterns for building robust APIs, MCP servers, and enterprise applications. Covers async/await, dependency injection, Entity Framework Core, Dappe… |
| `e2e-testing-patterns` |  | Master end-to-end testing with Playwright and Cypress to build reliable test suites that catch bugs, improve confidence, and enable fast deployment. Use when implementing E2E tests, … |
| `expo-tailwind-setup` |  | Framework (OSS). Set up Tailwind CSS v4 in Expo with react-native-css and NativeWind v5 for universal styling |
| `firebase-ai-logic-basics` |  | Official skill for integrating Firebase AI Logic (Gemini API) into web applications. Covers setup, multimodal inference, structured output, and security. |
| `firebase-firestore` |  | Sets up, manages, queries, and configures Cloud Firestore databases (Standard/Enterprise edition), including data modeling, security rules, indexes, and SDK integrations (Web, Python… |
| `frontend-design` |  | Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Helps with aesthetic direction, typography, and making choices that don't read … |
| `golang-database` |  | Comprehensive guide for Go database access — parameterized queries, struct scanning, NULLable columns, transactions, isolation levels, SELECT FOR UPDATE, connection pool, batch proce… |
| `golang-graphql` |  | Implements GraphQL APIs in Golang using gqlgen or graphql-go. Apply when building GraphQL servers, designing schemas, writing resolvers, handling subscriptions, or integrating GraphQ… |
| `golang-security` |  | Security best practices and vulnerability prevention for Golang. Covers injection (SQL, command, XSS), cryptography, filesystem safety, network security, cookies, secrets management,… |
| `graphql-schema` |  | Guide for designing GraphQL schemas following industry best practices. Use this skill when: (1) designing a new GraphQL schema or API, (2) reviewing existing schema for improvements,… |
| `gstack` |  | Router for the gstack skill suite. Sends any gstack request to the right skill (planning, review, QA, shipping, debugging, docs, security, design). For browser/QA and dogfooding it p… |
| `gstack-autoplan` |  | Auto-review pipeline — reads the full CEO, design, eng, and DX review skills from disk and runs them sequentially with auto-decisions using 6 decision principles. Surfaces taste deci… |
| `gstack-benchmark` |  | Performance regression detection using the browse daemon. Establishes baselines for page load times, Core Web Vitals, and resource sizes. Compares before/after on every PR. Tracks pe… |
| `gstack-benchmark-models` |  | Cross-model benchmark for gstack skills. Runs the same prompt through Claude, GPT (via Codex CLI), and Gemini side-by-side — compares latency, tokens, cost, and optionally quality vi… |
| `gstack-browse` |  | Fast headless browser for QA testing and site dogfooding. Navigate any URL, interact with elements, verify page state, diff before/after actions, take annotated screenshots, check re… |
| `gstack-canary` |  | Post-deploy canary monitoring. Watches the live app for console errors, performance regressions, and page failures using the browse daemon. Takes periodic screenshots, compares again… |
| `gstack-careful` |  | Safety guardrails for destructive commands. Warns before rm -rf, DROP TABLE, force-push, git reset --hard, kubectl delete, and similar destructive operations. User can override each … |
| `gstack-claude` |  | Claude Code CLI wrapper for non-Claude hosts - three modes. Review: independent diff review via claude -p. Challenge: adversarial failure-mode review. Consult: ask Claude about the r… |
| `gstack-context-restore` |  | Restore working context saved earlier by /context-save. Loads the most recent saved state (across all branches by default) so you can pick up where you left off — even across Conduct… |
| `gstack-context-save` |  | Save working context. Captures git state, decisions made, and remaining work so any future session can pick up without losing a beat. Use when asked to "save progress", "save state",… |
| `gstack-cso` |  | Chief Security Officer mode. Infrastructure-first security audit: secrets archaeology, dependency supply chain, CI/CD pipeline security, LLM/AI security, skill supply chain scanning,… |
| `gstack-design-consultation` |  | Design consultation: understands your product, researches the landscape, proposes a complete design system (aesthetic, typography, color, layout, spacing, motion), and generates font… |
| `gstack-design-html` |  | Design finalization: generates production-quality Pretext-native HTML/CSS. Works with approved mockups from /design-shotgun, CEO plans from /plan-ceo-review, design review context fr… |
| `gstack-design-review` |  | Designer's eye QA: finds visual inconsistency, spacing issues, hierarchy problems, AI slop patterns, and slow interactions — then fixes them. Iteratively fixes issues in source code,… |
| `gstack-design-shotgun` |  | Design shotgun: generate multiple AI design variants, open a comparison board, collect structured feedback, and iterate. Standalone design exploration you can run anytime. Use when: … |
| `gstack-devex-review` |  | Live developer experience audit. Uses the browse tool to actually TEST the developer experience: navigates docs, tries the getting started flow, times TTHW, screenshots error message… |
| `gstack-diagram` |  | Turn an English description (or mermaid source) into a diagram triplet: the source, an editable .excalidraw file you can open on excalidraw.com, and rendered SVG + PNG (clean mermaid… |
| `gstack-document-generate` |  | Generate missing documentation from scratch for a feature, module, or entire project. Uses the Diataxis framework (tutorial / how-to / reference / explanation) to produce complete, s… |
| `gstack-document-release` |  | Post-ship documentation update. Reads all project docs, cross-references the diff, builds a Diataxis coverage map (reference/how-to/tutorial/explanation), updates README/ARCHITECTURE… |
| `gstack-freeze` |  | Restrict file edits to a specific directory for the session. Blocks Edit and Write outside the allowed path. Use when debugging to prevent accidentally "fixing" unrelated code, or wh… |
| `gstack-guard` |  | Full safety mode: destructive command warnings + directory-scoped edits. Combines /careful (warns before rm -rf, DROP TABLE, force-push, etc.) with /freeze (blocks edits outside a sp… |
| `gstack-health` |  | Code quality dashboard. Wraps existing project tools (type checker, linter, test runner, dead code detector, shell linter), computes a weighted composite 0-10 score, and tracks trend… |
| `gstack-investigate` |  | Systematic debugging with root cause investigation. Four phases: investigate, analyze, hypothesize, implement. Iron Law: no fixes without root cause. Use when asked to "debug this", … |
| `gstack-ios-clean` |  | Remove the DebugBridge SPM package and all #if DEBUG wiring from an iOS app. Cleans up StateServer, DebugOverlay, accessor codegen output, and app-side hooks installed by /ios-qa. Th… |
| `gstack-ios-design-review` |  | Visual design audit for iOS apps on real hardware. Connects to a real iPhone via the same StateServer as /ios-qa, screenshots every screen, evaluates against Apple HIG, DESIGN.md, an… |
| `gstack-ios-fix` |  | Autonomous iOS bug fixer. Takes a bug found by /ios-qa, reads the source, writes the fix, rebuilds, redeploys, and verifies the fix on the real device. Closes the loop: find bug → fi… |
| `gstack-ios-qa` |  | Live-device iOS QA for SwiftUI apps. Connects to a real iPhone via USB CoreDevice IPv6 tunnel, reads Swift source to understand every screen, then runs a vision-driven agent loop: sc… |
| `gstack-ios-sync` |  | Regenerate the iOS debug bridge against the latest upstream gstack templates. Updates StateServer.swift, DebugOverlay.swift, Package.swift, and the typed @Observable state accessors.… |
| `gstack-land-and-deploy` |  | Land and deploy workflow. Merges the PR, waits for CI and deploy, verifies production health via canary checks. Takes over after /ship creates the PR. Use when: "merge", "land", "dep… |
| `gstack-landing-report` |  | Read-only queue dashboard for workspace-aware ship. Shows which VERSION slots are currently claimed by open PRs, which sibling Conductor workspaces have WIP work likely to ship soon,… |
| `gstack-learn` |  | Manage project learnings. Review, search, prune, and export what gstack has learned across sessions. Use when asked to "what have we learned", "show learnings", "prune stale learning… |
| `gstack-make-pdf` |  | Turn any markdown file into a publication-quality PDF. Proper 1in margins, intelligent page breaks, page numbers, cover pages, running headers, curly quotes and em dashes, clickable … |
| `gstack-office-hours` |  | YC Office Hours — two modes. Startup mode: six forcing questions that expose demand reality, status quo, desperate specificity, narrowest wedge, observation, and future-fit. Builder … |
| `gstack-open-gstack-browser` |  | Launch GStack Browser — AI-controlled Chromium with the sidebar extension baked in. Opens a visible browser window where you can watch every action in real time. The sidebar shows a … |
| `gstack-pair-agent` |  | Pair a remote AI agent with your browser. One command generates a setup key and prints instructions the other agent can follow to connect. Works with OpenClaw, Hermes, Codex, Cursor,… |
| `gstack-plan-ceo-review` |  | CEO/founder-mode plan review. Rethink the problem, find the 10-star product, challenge premises, expand scope when it creates a better product. Four modes: SCOPE EXPANSION (dream big… |
| `gstack-plan-design-review` |  | Designer's eye plan review — interactive, like CEO and Eng review. Rates each design dimension 0-10, explains what would make it a 10, then fixes the plan to get there. Works in plan… |
| `gstack-plan-devex-review` |  | Interactive developer experience plan review. Explores developer personas, benchmarks against competitors, designs magical moments, and traces friction points before scoring. Three m… |
| `gstack-plan-eng-review` |  | Eng manager-mode plan review. Lock in the execution plan — architecture, data flow, diagrams, edge cases, test coverage, performance. Walks through issues interactively with opiniona… |
| `gstack-plan-tune` |  | Self-tuning question sensitivity + developer psychographic for gstack (v1: observational). Review which AskUserQuestion prompts fire across gstack skills, set per-question preference… |
| `gstack-qa` |  | Systematically QA test a web application and fix bugs found. Runs QA testing, then iteratively fixes bugs in source code, committing each fix atomically and re-verifying. Use when as… |
| `gstack-qa-only` |  | Report-only QA testing. Systematically tests a web application and produces a structured report with health score, screenshots, and repro steps — but never fixes anything. Use when a… |
| `gstack-retro` |  | Weekly engineering retrospective. Analyzes commit history, work patterns, and code quality metrics with persistent history and trend tracking. Team-aware: breaks down per-person cont… |
| `gstack-review` |  | Pre-landing PR review. Analyzes diff against the base branch for SQL safety, LLM trust boundary violations, conditional side effects, and other structural issues. Use when asked to "… |
| `gstack-scrape` |  | Pull data from a web page. First call on a new intent prototypes the flow via $B primitives and returns JSON. Subsequent calls on a matching intent route to a codified browser-skill … |
| `gstack-setup-browser-cookies` |  | Import cookies from your real Chromium browser into the headless browse session. Opens an interactive picker UI where you select which cookie domains to import. Use before QA testing… |
| `gstack-setup-deploy` |  | Configure deployment settings for /land-and-deploy. Detects your deploy platform (Fly.io, Render, Vercel, Netlify, Heroku, GitHub Actions, custom), production URL, health check endpo… |
| `gstack-setup-gbrain` |  | Set up gbrain for this coding agent: install the CLI, initialize a local PGLite or Supabase brain, register MCP, capture per-remote trust policy. One command from zero to "gbrain is … |
| `gstack-ship` |  | Ship workflow: detect + merge base branch, run tests, review diff, bump VERSION, update CHANGELOG, commit, push, create PR. Use when asked to "ship", "deploy", "push to main", "creat… |
| `gstack-skillify` |  | Codify the most recent successful /scrape flow into a permanent browser-skill on disk. Future /scrape calls with the same intent run the codified script in ~200ms instead of re-drivi… |
| `gstack-spec` |  | Turn vague intent into a precise, executable spec in five phases. Files the issue, optionally spawns a Claude Code agent in a fresh worktree, and lets /ship close the source issue on… |
| `gstack-sync-gbrain` |  | Keep gbrain current with this repo's code and refresh agent search guidance in CLAUDE.md. Wraps the gstack-gbrain-sync orchestrator with state probing, native code-surface registrati… |
| `gstack-unfreeze` |  | Clear the freeze boundary set by /freeze, allowing edits to all directories again. Use when you want to widen edit scope without ending the session. Use when asked to "unfreeze", "un… |
| `gstack-upgrade` |  | Upgrade gstack to the latest version. Detects global vs vendored install, runs the upgrade, and shows what's new. Use when asked to "upgrade gstack", "update gstack", or "get latest … |
| `neon` |  | Overview of Neon, a complete set of cloud backend primitives for apps and agents, spanning Lakebase Postgres, Auth, the Data API, Object Storage, Compute Functions, and the AI Gatewa… |
| `neon-postgres` |  | Guides and best practices for working with Lakebase Postgres, the database behind Neon. Covers setup, connection methods and drivers, pooled vs direct connections, branching, autosca… |
| `nextjs-app-router-patterns` |  | Master Next.js 14+ App Router with Server Components, streaming, parallel routes, and advanced data fetching. Use when building Next.js applications, implementing SSR/SSG, or optimiz… |
| `node` |  | Provides domain-specific best practices for Node.js development with TypeScript, covering type stripping, async patterns, error handling, streams, modules, testing, performance, cach… |
| `nodejs-backend-patterns` |  | Build production-ready Node.js backend services with Express/Fastify, implementing middleware patterns, error handling, authentication, database integration, and API design best prac… |
| `playwright-best-practices` |  | Use when writing Playwright tests, fixing flaky tests, debugging failures, implementing Page Object Model, configuring CI/CD, optimizing performance, mocking APIs, handling authentic… |
| `playwright-cli` |  | Automate browser interactions, test web pages and work with Playwright tests. |
| `prisma-client-api` |  | Prisma Client API reference covering model queries, filters, operators, and client methods. Use when writing database queries, using CRUD operations, filtering data, or configuring P… |
| `prisma-database-setup` |  | Guides for configuring Prisma with different database providers (PostgreSQL, MySQL, SQLite, MongoDB, etc.). Use when setting up a new project, changing databases, or troubleshooting … |
| `react-native-architecture` |  | Build production React Native apps with Expo, navigation, native modules, offline sync, and cross-platform patterns. Use when developing mobile apps, implementing native integrations… |
| `react-state-management` |  | Master modern React state management with Redux Toolkit, Zustand, Jotai, and React Query. Use when setting up global state, managing server state, or choosing between state managemen… |
| `security-and-hardening` |  | Hardens code against vulnerabilities. Use when handling user input, authentication, data storage, or external integrations. Use when building any feature that accepts untrusted data,… |
| `security-review` |  | Security code review for vulnerabilities. Use when asked to "security review", "find vulnerabilities", "check for security issues", "audit security", "OWASP review", or review code f… |
| `tailwind-design-system` |  | Build scalable design systems with Tailwind CSS v4, design tokens, component libraries, and responsive patterns. Use when creating component libraries, implementing design systems, o… |
| `typescript-advanced-types` |  | Master TypeScript's advanced type system including generics, conditional types, mapped types, template literals, and utility types for building type-safe applications. Use when imple… |
| `unocss` |  | UnoCSS instant atomic CSS engine, superset of Tailwind CSS. Use when configuring UnoCSS, writing utility rules, shortcuts, or working with presets like Wind, Icons, Attributify. |
| `vercel-react-native-skills` |  | React Native Skills |
| `vercel-react-view-transitions` |  | Guide for implementing smooth, native-feeling animations using React's View Transition API (`<ViewTransition>` component, `addTransitionType`, and CSS view transition pseudo-elements… |
| `vitest` |  | Vitest fast unit testing framework powered by Vite with Jest-compatible API. Use when writing tests, mocking, configuring coverage, or working with test filtering and fixtures. |
| `web-component-design` |  | Master React, Vue, and Svelte component patterns including CSS-in-JS, composition strategies, and reusable component architecture. Use when building UI component libraries, designing… |

## hermes — 304 skills

| Skill | Also in | Description |
|---|---|---|
| `achieving-cmmc-level-2-compliance` |  | Prepare a defense-contractor environment for CMMC Level 2 certification: scope CUI and FCI, implement the 110 NIST SP 800-171 Rev 2 security requirements across 14 families, compute … |
| `agent-build-packs` |  | Author agent build packs: prompt, contracts, briefs. |
| `ai-routing-gateway` |  | Install local AI routing gateway (OmniRoute) inside Hermes. |
| `airtable` |  | Airtable REST API via curl. Records CRUD, filters, upserts. |
| `analytics-insights` |  | Drive Google Analytics (GA4), Google Tag Manager, Google Search Console, and BigQuery from chat — tracking plans, GA4 reports, key-event (conversion) setup, custom dimensions and met… |
| `analyzing-malware-behavior-with-cuckoo-sandbox` |  | Detonate malware samples in Cuckoo Sandbox to observe runtime behavior |
| `analyzing-security-logs-with-splunk` |  | Leverages Splunk Enterprise Security and SPL (Search Processing Language) |
| `analyzing-windows-event-logs-in-splunk` |  | Analyzes Windows Security, System, and Sysmon event logs in Splunk to |
| `android-tablet-second-screen-usb` |  | Use when an Android tablet becomes a USB second screen. |
| `app-security-slop-audit` |  | Audit an owned codebase for authz holes and AI slop. |
| `apple-notes` |  | Manage Apple Notes via memo CLI: create, search, edit. |
| `apple-reminders` |  | Apple Reminders via remindctl: add, list, complete. |
| `architecture-diagram` |  | Dark-themed SVG architecture/cloud/infra diagrams as HTML. |
| `artifact-delivery` |  | Use when delivering a file or report to the user's chat. |
| `arxiv` |  | Search arXiv papers by keyword, author, category, or ID. |
| `ascii-art` |  | ASCII art: pyfiglet, cowsay, boxes, image-to-ascii. |
| `ascii-video` |  | ASCII video: convert video/audio to colored ASCII MP4/GIF. |
| `auditing-azure-active-directory-configuration` |  | Auditing Microsoft Entra ID (Azure Active Directory) configuration to |
| `auditing-cloud-with-cis-benchmarks` |  | Audit AWS, Azure, and GCP environments against the CIS Foundations Benchmarks by running automated scans with tools like Prowler and ScoutSuite, interpreting failed controls, and tra… |
| `avoid-ai-writing` |  | Audit and rewrite content to remove AI writing patterns ("AI-isms"). Use this skill when asked to "remove AI-isms," "clean up AI writing," "edit writing for AI patterns," "audit writ… |
| `baoyu-infographic` |  | Infographics: 21 layouts x 21 styles (信息图, 可视化). |
| `blocked-page-recovery` |  | Use when a fetch fails: 403/429, paywall, WAF, bot wall. |
| `blogwatcher` |  | Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool. |
| `blue-ocean-strategy` |  | Create uncontested market space using value innovation instead of competing head-to-head. Use when the user mentions "blue ocean", "red ocean", "strategy canvas", "ERRC framework", "… |
| `blynk-prompt` |  | Load when writing BlynkAds AI pipeline prompts with schemas. |
| `box` |  | Box manages cloud files, sharing, search, and metadata. |
| `brand-context` |  | Create and maintain a single brand-context.md — positioning, audience, personas, pain points, customer language, voice, proof points — that every other marketing skill reads before a… |
| `brand-recovery` |  | Recover logo & theme from a down or expired website. |
| `browser-agents` |  | Use when building browser agents with the webcmd CLI. |
| `bug-bounty` |  | Complete bug bounty workflow — recon (subdomain enumeration, asset discovery, fingerprinting, HackerOne scope, source code audit), pre-hunt learning (disclosed reports, tech stack re… |
| `canvas-design` |  | Create beautiful visual art in .png and .pdf documents using design philosophy. You should use this skill when the user asks to create a poster, piece of art, design, or other static… |
| `captions-overlay` |  | Overlay doctrine for the embedded-captions workflow — the caption MODEL (drop / rail / embed) and the rule that captions are an OVERLAY composited on top of the film, never a reserve… |
| `caveman` |  | Ultra-compressed communication mode. Cuts output tokens 65% (measured) by speaking like caveman while keeping full technical accuracy. Supports intensity levels: lite, full (default)… |
| `chainlink-ccip-skill` |  | Handle Chainlink CCIP requests including read-only route, token, message-status, and lane lookups; fee-estimation guidance; user-run cross-chain transfer and messaging artifacts; sen… |
| `changelog-video` |  | Turn a weekly changelog .md into a finished branded changelog video (square 1080, ~45-60s, Annie VO, animated brand background, mock-UI visualizations, lowkey captions). Use when the… |
| `cinematic-web-development` |  | Build cinematic agency sites with WebGL heroes, GSAP scroll. |
| `claude-code` |  | Delegate coding to Claude Code CLI (features, PRs). |
| `claude-design` |  | Design one-off HTML artifacts (landing, deck, prototype). |
| `clean-code` |  | Write readable, maintainable code through disciplined naming, small functions, and clean error handling. Use when the user mentions "clean up this code", "this function is too long",… |
| `code-review` |  | Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes — Standards (does the code follow this repo's documented coding standards?) and Spec (does … |
| `codebase-design` |  | Shared vocabulary for designing deep modules. Use when the user wants to design or improve a module's interface, find deepening opportunities, decide where a seam goes, make code mor… |
| `codebase-inspection` |  | Inspect codebases w/ pygount: LOC, languages, ratios. |
| `codex` |  | Delegate coding to OpenAI Codex CLI (features, PRs). |
| `cold-email-outreach` |  | Send cold emails via Himalaya CLI. Compose, send, track. |
| `collective-wisdom-install` |  | Browse, install, or share team skills with consent. |
| `comfyui` |  | Generate images, video, and audio via diffusion workflows. |
| `command-code` |  | Delegate coding to Command Code CLI (features, fixes, PRs). |
| `community-management` |  | Use to build a genuine community — turning an audience into people who interact with each other, not just with the brand. Run when the user asks how to build community, foster belong… |
| `competitor-analysis` |  | Competitor analysis for social media — public-data competitive reconnaissance to find the gap a brand can own. Use when someone wants to "analyse/research our competitors," "see what… |
| `competitor-news-monitor` |  | Watch named companies for material news; cited digests. |
| `computer-use` |  | Drive the desktop background-first; escalate on signal. |
| `conducting-external-reconnaissance-with-osint` |  | Conduct external recon using OSINT techniques to map an organization's external attack surface without touching target systems, gathering DNS records, certificate transparency logs, … |
| `content-calendar` |  | Use to build a content calendar — a sustainable, repeatable posting rhythm and recurring structure (which pillars/formats post on which days, on which platforms), derived from strate… |
| `continuous-llm-red-teaming-with-promptfoo` |  | Wires Promptfoo and DeepTeam into CI/CD for automated, repeatable red-teaming of LLM apps against OWASP LLM Top 10, OWASP Agentic, and MITRE ATLAS presets, failing the build when jai… |
| `cursor-agent` |  | Delegate coding to Cursor Agent CLI (features, PRs, fixes). |
| `cut-the-curve` |  | The technique catalog: five velocity-matched SEAMS (zoom-through, INVERSE zoom-through, cut-the-curve, waterfall cut, rack-focus blur-cut) plus the two in-scene techniques — waterfal… |
| `ddia-systems` |  | Design data systems by understanding storage engines, replication, partitioning, transactions, and consistency models. Use when the user mentions "database choice", "which database s… |
| `demo-video-production` |  | Use when a project demo video is needed. |
| `design-md` |  | Author/validate/export Google's DESIGN.md token spec files. |
| `diagnosing-bugs` |  | Diagnosis loop for hard bugs and performance regressions. Use when the user says "diagnose"/"debug this", or reports something broken/throwing/failing/slow. |
| `document-to-action-items` |  | Extract cited obligations, deadlines, tasks from documents. |
| `docx` |  | Create, read, edit, template, and review Word .docx files. |
| `dogfood` |  | Exploratory QA of web apps: find bugs, evidence, reports. |
| `domain-modeling` |  | Build and sharpen a project's domain model. Use when the user wants to pin down domain terminology or a ubiquitous language, record an architectural decision, or when another skill n… |
| `email-inbox-triage` |  | Triage an inbox: prioritize threads, draft replies safely. |
| `embedded-captions` |  | Add captions or subtitles to an existing single-subject talking-head video without editing the footage. Use for plain verbatim captions, cinematic captions embedded behind the subjec… |
| `engagement-routine` |  | Use to design a sustainable engagement routine — the operating system that turns the engagement craft into a daily/weekly habit. Run when the user asks how to keep up with comments/D… |
| `evaluating-llms-harness` |  | lm-eval-harness: benchmark LLMs (MMLU, GSM8K, etc.). |
| `excalidraw` |  | Hand-drawn Excalidraw JSON diagrams (arch, flow, seq). |
| `faceless-explainer` |  | Turn arbitrary text — an article, notes, a topic, a brief — into a faceless explainer video: there is no site or footage to capture, so the visuals are invented per scene (typography… |
| `figma` |  | Import Figma content into a HyperFrames composition — rendered assets, brand tokens, components, storyboard sections → reconstructed motion (frames read as states, not slides) (REST/… |
| `findmy` |  | Track Apple devices/AirTags via FindMy.app on macOS. |
| `free-chatbot-platform` |  | Build free WhatsApp/Telegram chatbot with Botpress. |
| `frontend-design` |  | Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Helps with aesthetic direction, typography, and making choices that don't read … |
| `general-video` |  | Author or edit a custom HyperFrames composition when no specialized workflow fits, or when BRIEF.md sets flow: companion. Use for longer or multi-scene pieces, brand and sizzle reels… |
| `gif-search` |  | Search/download GIFs from Tenor via curl + jq. |
| `github` |  | GitHub via gh CLI: PRs, issues, reviews, repos, auth. |
| `github-auth` |  | GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login. |
| `github-code-review` |  | Review PRs: diffs, inline comments via gh or REST. |
| `github-issues` |  | Create, triage, label, assign GitHub issues via gh or REST. |
| `github-pr-workflow` |  | GitHub PR lifecycle: branch, commit, open, CI, merge. |
| `github-repo-management` |  | Clone/create/fork repos; manage remotes, releases. |
| `godmode` |  | Jailbreak LLMs: Parseltongue, GODMODE, ULTRAPLINIAN. |
| `good-strategy-bad-strategy` |  | Formulate and audit real strategy using Richard Rumelt''s "Good Strategy Bad Strategy": an honest diagnosis, a guiding policy, and coherent action instead of goals, vision, and wishf… |
| `google-workspace` |  | Gmail, Calendar, Drive, Docs, Sheets via gws CLI or Python. |
| `grill-with-docs` |  | A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go. |
| `grounded-citations` |  | Ground answers and documents in cited, verifiable sources. |
| `gstack` |  | Router for the gstack skill suite. Sends any gstack request to the right skill (planning, review, QA, shipping, debugging, docs, security, design). For browser/QA and dogfooding it p… |
| `gstack-install` |  | Install gstack AI engineering skills into Hermes. |
| `gstack-upgrade` |  | Upgrade gstack to the latest version. |
| `gstack-upgrade` | claude, commandcode, cursor | Upgrade gstack to the latest version. |
| `headless-site-inspection` |  | Use when scraping or visually inspecting websites from CLI. |
| `hermes-agent` |  | Use, configure, theme, extend, and orchestrate Hermes Agent. |
| `hermes-agent-skill-authoring` |  | Author in-repo SKILL.md files: frontmatter and structure. |
| `hermes-persistent-context` |  | Wire vaults and project rules into Hermes context. |
| `hermes-skill-discovery-install` |  | Batch-install Hermes skills from GitHub with security scans. |
| `hermes-skill-library-portability` |  | Export a Hermes skill library to another machine. |
| `high-output-management` |  | Manage for output using Grove''s "High Output Management": a manager''s output is their organization''s output, raised by high-leverage activities. Use when the user mentions "high o… |
| `himalaya` |  | Himalaya CLI: IMAP/SMTP email from terminal. |
| `himalaya-v2x-config` |  | Himalaya v2.x config templates for IMAP/SMTP providers. |
| `hosting-php-apps` |  | Use when hosting PHP web apps (Docker, Hostinger). |
| `huggingface-hub` |  | HuggingFace hf CLI: search/download/upload models, datasets. |
| `humanizer` |  | Humanize text: strip AI-isms and add real voice. |
| `hunt-api-misconfig` |  | Hunt API security misconfiguration — mass assignment, prototype pollution, HTTP verb tampering. Mass assignment: send {is_admin:true, role:admin, verified:true} on profile/account/re… |
| `hunt-auth-bypass` |  | Hunting skill for auth bypass vulnerabilities. Built from 12 public bug bounty reports across SAML XSW / parser-differential (GitHub Enterprise CVE-2025-25291/25292), SAML signature … |
| `hunt-idor` |  | Hunting skill for idor vulnerabilities. Built from 26 public bug bounty reports. Use when hunting idor on any target. |
| `hunt-llm-ai` |  | Hunt LLM/AI feature bugs — prompt injection, indirect injection, exfiltration via tool-use/markdown, ASCII smuggling, agentic AI security (OWASP Agentic Apps 2026, ASI01-ASI10). Patt… |
| `hunt-rce` |  | Hunting skill for rce vulnerabilities. Built from 67 public bug bounty reports. Use when hunting rce on any target. |
| `hunt-sqli` |  | Hunting skill for sqli vulnerabilities. Built from 12 public bug bounty reports including modern NoSQL injection (Rocket.Chat CVE-2021-22911 MongoDB $regex, Mongoose ORM CVE-2024-539… |
| `hunt-ssrf` |  | Hunting skill for ssrf vulnerabilities. Built from 15 public bug bounty reports including AWS metadata SSRF (HackerOne $25k Analytics PDF, Shopify Exchange $25k, Capital One 106M-rec… |
| `hunt-xss` |  | Hunting skill for xss vulnerabilities. Built from 174 public bug bounty reports. Use when hunting xss on any target. For markup injection that reflects raw HTML but does NOT execute … |
| `hyperframes` |  | Mandatory entry point: read this first for any request to make, create, edit, animate, or render a video, animation, or motion graphic, including a promo, explainer, captioned clip, … |
| `hyperframes-animation` | agents, claude | All animation knowledge for HyperFrames — atomic motion rules, multi-phase scene blueprints, scene transitions, broader motion-design techniques, AND the seven runtime adapters (GSAP… |
| `hyperframes-audio` |  | Use when audio already placed in a HyperFrames composition needs to be mixed: fade-in/fade-out, crossfade, track gain or volume, volume automation, ducking, a music bed that fights a… |
| `hyperframes-cli` |  | Use the HyperFrames CLI development loop: init, add, catalog, capture, lint, check, snapshot, compare, grade-compare, preview, play, present, beats, keyframes, single or batch render… |
| `hyperframes-core` | agents, claude | The HyperFrames composition contract — build one renderable project. Use for composition structure, the `data-*` timing attributes, `class="clip"`, tracks, sub-compositions, variable… |
| `hyperframes-creative` | agents, claude | Non-animation creative direction for HyperFrames videos. Use for design spec (frame.md / design.md) handling, palettes, typography, narration, beat planning, audio-reactive visuals, … |
| `hyperframes-keyframes` | agents, claude | Use when a HyperFrames composition needs a punch-in, punch-out, zoom, reframe, Ken Burns treatment, camera move, visual match/whip handoff, or other seek-safe 2D/3D keyframes; also f… |
| `hyperframes-registry` |  | Install, discover, and wire registry blocks and components into HyperFrames compositions. Use when running hyperframes add or hyperframes catalog, installing one item or every block … |
| `imessage` |  | Send and receive iMessages/SMS via the imsg CLI on macOS. |
| `implement` |  | Implement a piece of work based on a spec or set of tickets. |
| `implementing-api-rate-limiting-and-throttling` |  | Implements API rate limiting and throttling with token bucket, sliding |
| `implementing-api-security-posture-management` |  | Implements API Security Posture Management (API-SPM) to continuously |
| `implementing-api-security-testing-with-42crunch` |  | Implements API security testing on the 42Crunch platform, combining |
| `implementing-api-threat-protection-with-apigee` |  | Implements API threat protection using Google Apigee reverse-proxy |
| `implementing-aws-config-rules-for-compliance` |  | Implements AWS Config managed and custom rules for continuous compliance |
| `implementing-aws-security-hub` |  | Deploy AWS Security Hub as a centralized CSPM platform, backed by AWS |
| `implementing-gdpr-data-protection-controls` |  | Implements GDPR (EU 2016/679) technical and organizational measures — privacy by design/default, DPIAs, data subject rights management, 72-hour breach notification, and cross-border … |
| `implementing-github-advanced-security-for-code-scanning` |  | Configures GitHub Advanced Security (code scanning with CodeQL, secret scanning, dependency review, and Dependabot alerts) to perform automated static analysis and vulnerability dete… |
| `implementing-iso-27001-information-security-management` |  | Guides implementation of an ISO/IEC 27001:2022 Information Security Management System (ISMS) end to end: gap analysis and scoping, risk assessment methodology, Annex A control select… |
| `implementing-pci-dss-compliance-controls` |  | Implements PCI DSS 4.0.1's 12 requirements across 6 control objectives |
| `implementing-secrets-management-with-vault` |  | Deploy HashiCorp Vault for centralized secrets management, covering dynamic |
| `implementing-secrets-scanning-in-ci-cd` |  | Integrate gitleaks and trufflehog into CI/CD pipelines to detect leaked |
| `implementing-semgrep-for-custom-sast-rules` |  | Write custom Semgrep SAST rules in YAML to detect application-specific |
| `improve-codebase-architecture` | gstack | Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick. |
| `inspecting-hermes-desktop-dom` |  | Read the live Hermes desktop DOM/CSS over CDP. |
| `instagram-reel-prompts` |  | Generate AI video prompt banks for Reels growth. |
| `integrating-dast-with-owasp-zap-in-pipeline` |  | Integrates OWASP ZAP (Zed Attack Proxy) into GitHub Actions and GitLab CI pipelines, covering baseline, full, and API scan configuration against running applications, ZAP finding int… |
| `integrating-sast-into-github-actions-pipeline` |  | Integrates CodeQL and Semgrep SAST scanning into GitHub Actions, covering scans on pull requests/pushes, rule tuning to cut false positives, SARIF upload to GitHub Advanced Security,… |
| `jobs-to-be-done` |  | Discover what customers truly need by analyzing the "job" they hire your product to do. Use when the user mentions "customer discovery", "why customers churn", "what job does this so… |
| `kali-pentest` |  | Execute authorized penetration testing via Kali Linux CLI tools over SSH or Docker. Covers: information gathering, vulnerability analysis, sniffing & spoofing, web/API testing, explo… |
| `lean-analytics` |  | Choose and audit startup metrics using Croll and Yoskovitz''s "Lean Analytics". Use when the user mentions "what metrics should we track", "KPIs", "north star metric", "One Metric Th… |
| `lean-startup` |  | Design MVPs, validated learning experiments, and pivot-or-persevere decisions using Build-Measure-Learn. Use when the user mentions "MVP scope", "validated learning", "pivot or perse… |
| `legacy-php-csv-app-hardening` |  | Harden PHP/CSV apps via Docker+Apache; security + mobile UX. |
| `linkedin` |  | Publish and manage LinkedIn content via the Hyper MCP — text posts, article / link previews, document and PDF posts, organization (company page) posts, and AI-generated text-to-carou… |
| `linux-appimage-desktop` |  | Use when installing a downloaded .AppImage as a desktop app. |
| `linux-desktop-app-integration` |  | Install/launch GUI desktop apps on Fedora GNOME Wayland. |
| `llama-cpp` |  | llama.cpp local GGUF inference + HF Hub model discovery. |
| `llm-api-benchmarking` |  | Measure LLM API TPS/TTFT; use when asked to 'test the tps'. |
| `llm-wiki` |  | Karpathy's LLM Wiki: build/query interlinked markdown KB. |
| `localai` |  | Run or set up LocalAI for local OpenAI-compatible inference. |
| `localai-image-generation` |  | Run LocalAI Stable Diffusion image gen on CPU in Docker. |
| `manim-video` |  | Manim CE animations: 3Blue1Brown math/algo videos. |
| `maps` |  | Geocode, POIs, routes, timezones via OpenStreetMap/OSRM. |
| `mcp-server-integration` |  | Use when adding or verifying an MCP server. |
| `media-use` | agents, claude | Agent Media OS, the single skill for every media need in a HyperFrames project. Resolve BGM, SFX, image, icon, brand logo, voice, color grade, or LUT into a frozen local file or past… |
| `meeting-action-items` |  | Turn meeting notes into cited decisions, owners, tickets. |
| `meta-ads` |  | Plan and create Meta (Facebook + Instagram) advertising campaigns end-to-end via the Hyper MCP, defaulting to Advantage+ automation. Use when the user wants to launch Meta ads, Faceb… |
| `mimo` |  | Delegate coding to mimocode CLI (features, fixes, PRs). |
| `mom-test` |  | Talk to customers without leading them using Mom Test rules: discuss their life not your idea, ask about specifics in the past, and talk less. Use when the user mentions "customer in… |
| `motion-doctrine` |  | GATEWAY — load FIRST before composing any HyperFrames animation or video. The high-level motion law that makes a multi-scene video feel like ONE continuous camera move instead of a s… |
| `motion-graphics` |  | A short, design-led motion graphic where motion is the message — kinetic typography, stat count-up, chart/data-viz hit, logo sting / brand lockup, lower-third / callout / social over… |
| `multi-agent-orchestration` |  | Orchestrate many coding CLI agents; use for agent teamwork. |
| `music-to-video` |  | Turn a music track (an audio file, a video to pull audio from, or a track generated from a mood brief) into a beat-synced video — lyric video, slideshow, or kinetic promo. The music … |
| `nano-pdf` |  | Edit text in existing PDFs via natural-language prompts. |
| `nextjs-supabase-e2e-testing` |  | E2E test/debug patterns for Next.js 15 + Supabase EMR apps — authenticated browser QA, session-cookie import, data-layer write verification, deployed-revision checks, date/timezone f… |
| `nextjs-supabase-vercel-ops` |  | Troubleshoot deployed Next.js + Supabase + Vercel web apps. |
| `node-inspect-debugger` |  | Debug Node.js via --inspect + Chrome DevTools Protocol CLI. |
| `notion` |  | Notion API + ntn CLI: pages, databases, markdown, Workers. |
| `obsidian` |  | Read, search, create, and edit notes in the Obsidian vault. |
| `obviously-awesome` |  | Define product positioning by mapping competitive alternatives, unique attributes, and best-fit customers to the right market category. Use when the user mentions "positioning", "com… |
| `ocr-and-documents` |  | Extract text from PDFs/scans (pymupdf, marker-pdf). |
| `october-canvas-bus` |  | Use when wiring October canvas bus tools into Hermes. |
| `offensive-osint` |  | Operational arsenal for authorized external red-team and bug-bounty recon. Concrete probes, wordlists, regexes, dorks, curl one-liners for: subdomain enum, GraphQL/Swagger/REST disco… |
| `one-page-marketing` |  | Build a complete marketing plan covering the full customer journey from stranger to raving fan. Use when the user mentions "marketing plan", "marketing strategy", "target market", "U… |
| `onequery-cli` |  | Load when a user request can only be completed by connecting to a company data source through OneQuery-managed access — including internal metrics, analytics, customer or company dat… |
| `opencode` |  | Delegate coding to OpenCode CLI (features, PR review). |
| `openhue` |  | Control Philips Hue lights, scenes, rooms via OpenHue CLI. |
| `oversized-cursor` |  | House-style oversized macOS cursor technique for HyperFrames launch videos. Load whenever a scene involves cursors or a pointer-led action, when kicking off a UI scene, when igniting… |
| `p5js` |  | p5.js sketches: gen art, shaders, interactive, 3D. |
| `paleo` |  | Use when user says "paleo mode", "save tokens", "be brief", "terse", "compress output", or says "paleo". Switch agent to terse replies that cut output tokens ~50-70% (median ~54% on … |
| `paleo-auto` |  | Use when you want automatic token-saving without manual skill selection. Auto-detects long sessions (>15 turns), high token usage, or bulky context — then auto-enables paleo + paleo-… |
| `paleo-budget` |  | Use when user says "budget", "token limit", "stay under N tokens", or wants per-task token caps. Enforce a hard token budget per task/response — track estimate, stop before limit, su… |
| `paleo-converse` |  | Use when user says "compress conversation", "condense chat", "summarize history", "too long context", or a session has many old turns. Condense prior conversation turns into a tight … |
| `paleo-json` |  | Use when user says "compact json", "minify output", "tight structured", or the agent must emit JSON / structured data. Strip insignificant whitespace, collapse long arrays, shorten k… |
| `paleo-summary` |  | Use when user says "summarize output", "condense this", "tldr", or a tool result / log / file dump / long stdout is large. Reduce long content (tool output, logs, diffs, docs) to a c… |
| `paleo-trim-context` |  | Use when context window is large / token cost high / long session. Proactively trim, summarize, or drop stale content to save context tokens without losing the task state. |
| `pdf` |  | PDF files: create, read, merge, fill, OCR, edit text. |
| `performing-aws-account-enumeration-with-scout-suite` |  | Run the agentless, open-source ScoutSuite tool (via pip install and the `scout` CLI) |
| `performing-cloud-asset-inventory-with-cartography` |  | Run Cartography to sync AWS, GCP, or Azure resources into a Neo4j graph database, |
| `performing-cloud-penetration-testing-with-pacu` |  | Run authorized AWS penetration tests with Pacu, the open-source AWS exploitation |
| `performing-container-security-scanning-with-trivy` |  | Scan container images, filesystems, Git repositories, and Kubernetes manifests |
| `performing-credential-access-with-lazagne` |  | Extract stored credentials from compromised endpoints using the LaZagne |
| `performing-disk-forensics-investigation` |  | Conduct disk forensics investigations using forensic imaging, file system |
| `performing-fuzzing-with-aflplusplus` |  | Performs coverage-guided fuzzing of compiled binaries with AFL++, instrumenting |
| `performing-gcp-penetration-testing-with-gcpbucketbrute` |  | Performs authorized GCP security testing using GCPBucketBrute to enumerate |
| `performing-nist-csf-maturity-assessment` |  | Conduct a NIST Cybersecurity Framework (CSF) 2.0 maturity assessment across the six core Functions (Govern, Identify, Protect, Detect, Respond, Recover), scoring organizational postu… |
| `performing-ransomware-response` |  | Executes a structured ransomware incident response from detection through |
| `performing-red-team-phishing-with-gophish` |  | Automates GoPhish phishing simulation campaigns using the Python gophish |
| `performing-sca-dependency-scanning-with-snyk` |  | This skill covers implementing Software Composition Analysis (SCA) using |
| `performing-security-headers-audit` |  | Auditing HTTP security headers including CSP, HSTS, X-Frame-Options, |
| `performing-soc2-type2-audit-preparation` |  | Automates SOC 2 Type II audit preparation including gap assessment against |
| `performing-threat-emulation-with-atomic-red-team` |  | Executes Atomic Red Team tests for MITRE ATT&CK technique validation |
| `performing-vulnerability-scanning-with-nessus` |  | Performs authenticated and unauthenticated vulnerability scanning using |
| `performing-web-application-firewall-bypass` |  | Bypasses Web Application Firewall protections using encoding tricks, |
| `performing-web-application-scanning-with-nikto` |  | Runs Nikto, an open-source web server and web application scanner, |
| `php-docker-apache-deployment` |  | Deploy PHP apps with Apache in Docker on SELinux Enforcing. |
| `pillow-graphics` |  | Poster/social PNGs via Pillow, no headless browser needed. |
| `plan` |  | Write a markdown plan to .hermes/plans/; no execution. |
| `polymarket` |  | Query Polymarket: markets, prices, orderbooks, history. |
| `ponytail` |  | Forces the laziest solution that actually works. Channels a senior dev who has seen everything: question whether the task needs to exist at all (YAGNI), reach for the standard librar… |
| `popular-web-designs` |  | 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS. |
| `poster-qa` |  | QA batches of rendered poster PNGs against a spec. |
| `powerpoint` |  | Create, read, edit .pptx decks with python-pptx. |
| `pr-to-video` |  | Turn a GitHub pull request (a PR URL, owner/repo#N, or 'this PR' in a checked-out repo) into a code-change explainer video — changelog, feature reveal, fix, or refactor walkthrough b… |
| `pragmatic-programmer` |  | Apply meta-principles of software craftsmanship: DRY, orthogonality, tracer bullets, and design by contract. Use when the user mentions "best practices", "pragmatic approach", "broke… |
| `pretext` |  | Build creative browser demos with DOM-free text layout. |
| `product-launch-video` |  | Turn a product or marketing URL, pasted script, or brief into a product launch / promo video — SaaS promos, feature reveals, product demos, app and company launches. Use when the use… |
| `product-price-monitor` |  | Watch product, flight, or listing prices; alert on target. |
| `prototype` |  | Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state model or logic feels right, or explore what a UI should look like. |
| `python-debugpy` |  | Debug Python: pdb REPL + debugpy remote (DAP). |
| `quivane-design-system` |  | Use when making any Quivane visual. Posts, web, image gen. |
| `quivane-execution-tax` |  | Use when building a Quivane Execution Tax episode. |
| `redteam-mindset` |  | Red-team operator discipline — the mindset corrections that separate offensive testing from defensive WAPT. Built from authorized red-team work where conservative defaults caused mul… |
| `refactoring-patterns` |  | Apply named refactoring transformations to improve code structure without changing behavior. Use when the user mentions "refactor this", "code smells", "extract method", "replace con… |
| `remotion-to-hyperframes` |  | Port an existing Remotion (React) composition''s source to HyperFrames HTML. Use ONLY on an explicit ask to port/convert/migrate/translate a Remotion source — one-way, Remotion-only.… |
| `remotion-video-production` |  | Use when building or revising a Remotion composition. |
| `requesting-code-review` |  | Pre-commit review: security scan, quality gates, auto-fix. |
| `research` |  | Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathe… |
| `research-paper-writing` |  | Write ML papers for NeurIPS/ICML/ICLR: design→submit. |
| `resolving-merge-conflicts` |  | Use when you need to resolve an in-progress git merge/rebase conflict. |
| `sales-data-generator` |  | Generate realistic sales CSVs with Excel and PDF output. |
| `scanning-containers-with-trivy-in-cicd` |  | Integrates Aqua Security''s Trivy scanner into CI/CD pipelines to detect |
| `scanning-kubernetes-manifests-with-kubesec` |  | Perform security risk analysis on Kubernetes resource manifests using |
| `sdlc-review` |  | Review Kanban handoffs and route verified outcomes. |
| `seam-craft` |  | Render-correctness doctrine for scene-to-scene seams in HyperFrames launch videos — the prerequisites that make transitions composite correctly on the master timeline. Load when asse… |
| `securing-api-gateway-with-aws-waf` |  | Secures AWS API Gateway endpoints with AWS WAF by configuring managed |
| `securing-aws-iam-permissions` |  | Hardens AWS IAM configurations to enforce least-privilege access, covering |
| `securing-aws-lambda-execution-roles` |  | Hardens AWS Lambda execution roles by writing least-privilege IAM policies, |
| `securing-azure-with-microsoft-defender` |  | Deploys and configures Microsoft Defender for Cloud as a CNAPP for |
| `security-tool-integration` |  | Add security tools to Hermes Agent and AI clients via MCP. |
| `seo-content-creation` |  | Create SEO content for websites. |
| `serving-llms-vllm` |  | vLLM: high-throughput LLM serving, OpenAI API, quantization. |
| `simplify-code` |  | Parallel 4-agent cleanup of recent code changes. |
| `site-content-recovery` |  | Use when a site must be fully scraped for a rebuild. |
| `site-visual-review` |  | Judge website design visually. Use for hero/UX reviews. |
| `sketch` |  | Throwaway HTML mockups: 2-3 design variants to compare. |
| `skill-creator` |  | Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run eva… |
| `slideshow` |  | Author a HyperFrames slideshow — a presentation, pitch deck, or interactive deck with discrete slides, fragment reveals, branching, hotspot navigation, and built-in presenter mode wi… |
| `social-page-audit` |  | Audit social pages from screenshots and captions. |
| `software-design-philosophy` |  | Manage software complexity through deep modules, information hiding, and strategic programming. Use when the user mentions "module design", "API too complex", "shallow class", "compl… |
| `songsee` |  | Audio spectrograms/features (mel, chroma, MFCC) via CLI. |
| `songwriting-and-ai-music` |  | Songwriting craft and Suno AI music prompts. |
| `spike` |  | Throwaway experiments to validate an idea before build. |
| `static-site-audit` |  | Use when auditing a site for errors/broken links — local static projects OR deployed URLs (Vercel/Next.js) the user wants reviewed. |
| `supabase-app-fixes` |  | Fix Supabase apps with silent write failures. |
| `supabase-nextjs-debugging` |  | Debug write/storage failures in Supabase Next.js apps. |
| `supabase-project-operations` |  | Use when operating a linked Supabase + Vercel project. |
| `supabase-rls-data-layer-audit` |  | Use when auditing Supabase RLS for cross-tenant data leaks. |
| `system-design` |  | Design scalable distributed systems using structured approaches for load balancing, caching, database scaling, and message queues. Use when the user mentions "system design", "scale … |
| `systematic-debugging` |  | 4-phase root cause debugging: understand bugs before fixing. |
| `talking-head-recut` |  | Package an existing talking-head / interview / podcast video with timed, designed GRAPHIC OVERLAY cards — kinetic titles, lower-thirds, data callouts, quotes, side panels, picture-in… |
| `tdd` |  | Test-driven development. Use when the user wants to build features or fix bugs test-first, mentions "red-green-refactor", or wants integration tests. |
| `team-topologies` |  | Organize business and technology teams for fast flow using Skelton & Pais''s "Team Topologies". Use when the user mentions "team topologies", "Conway''s law", "platform team", "strea… |
| `teams-meeting-pipeline` |  | Teams meeting summaries, job replay, Graph subscriptions. |
| `test-driven-development` |  | TDD: enforce RED-GREEN-REFACTOR, tests before code. |
| `testing-api-for-mass-assignment-vulnerability` |  | Tests APIs for mass assignment (auto-binding), OWASP API3:2023, by identifying |
| `testing-prompt-injection-in-rag-pipelines` |  | Probes Retrieval-Augmented Generation pipelines for indirect prompt injection |
| `theme-factory` |  | Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML landing pages, etc. There are 10 pre-set themes with colors/fonts that you can apply… |
| `third-party-license-audit` |  | Verify a third-party license boundary before building. |
| `tiktok` |  | Publish organic TikTok content (videos, photos, carousels) through the TikTok-compliant interactive posting form via the Hyper MCP. Use when the user wants to post a video to TikTok,… |
| `to-spec` |  | Turn the current conversation into a spec and publish it to the project issue tracker — no interview, just synthesis of what you've already discussed. |
| `to-tickets` |  | Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges, published to the configured tracker — edges as text in one fil… |
| `touchdesigner-mcp` |  | Control TouchDesigner via twozero MCP. |
| `transcript` |  | Use when the spoken content of a YouTube video is needed — even if not explicitly requested: pasted video links or IDs, requests to summarize, quote, transcribe, translate, fact-chec… |
| `triage` |  | Move issues and external PRs through a state machine of triage roles — categorise, verify, grill if needed, and write agent-ready briefs. |
| `ui-quality-audit` |  | Use when auditing a web UI for measurable defects. |
| `velen-cli` |  | Use when the user wants to inspect company or customer data that lives behind Velen, configure Velen CLI org selection or local profiles, run ad hoc read-only SQL or source API opera… |
| `vercel-composition-patterns` |  | React Composition Patterns |
| `vercel-deployment-troubleshooting` |  | Fix failing Vercel deployments and red GitHub checks. |
| `vercel-react-best-practices` | gstack | React and Next.js performance optimization guidelines from Vercel Engineering. This skill should be used when writing, reviewing, or refactoring React/Next.js code to ensure optimal … |
| `vibe` |  | Delegate coding to Mistral Vibe CLI (features, fixes, PRs). |
| `wayfinder` |  | Plan a huge chunk of work — more than one agent session can hold — as a shared map of decision tickets on your issue tracker, and resolve them one at a time until the way to the dest… |
| `web-design-guidelines` | gstack | Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices". |
| `web-scraping-pipelines` |  | Use when scraping listing/directory data at scale. |
| `web2-recon` |  | Web2 recon pipeline — subdomain enumeration (subfinder, Chaos API, assetfinder), live host discovery (dnsx, httpx), URL crawling (katana, waybackurls, gau), directory fuzzing (ffuf),… |
| `webapp-testing` | gstack | Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and… |
| `website-audit` |  | Audit a website's SEO meta and headers via curl. |
| `website-reconnaissance` |  | Use when asked what a website is or what it's built on. |
| `website-security-hardening` |  | Fix website security issues without changing content. |
| `weekly-review-planning` |  | Weekly reset: commitments, stalled work, next-week plan. |
| `weights-and-biases` |  | W&B: log ML experiments, sweeps, model registry, dashboards. |
| `wizard` |  | Generate an interactive bash wizard that walks a human through steps only they can perform. Use when provisioning infrastructure, setting up credentials or CI secrets, walking an unf… |
| `woopsocial-publish` |  | Use when publishing or scheduling posts via WoopSocial. |
| `workspace-dispatch` |  | Single-agent mission orchestrator. Decomposes a mission into tasks, spawns one worker per task using the default model, verifies exit criteria, and chains tasks with retry. No critic… |
| `x402-agentic-payments` |  | Use when building x402 paid endpoints or agent payments. |
| `xlsx` |  | Create, read, edit Excel .xlsx workbooks and CSVs. |
| `xurl` |  | X/Twitter via xurl CLI: raw post search, posting, DM, media. |
| `youtube-channels` |  | Use when a YouTube channel is the focus: pasted @handles or channel URLs, requests to browse a creator's uploads, see what a channel has posted recently, search within a channel, or … |
| `youtube-content` |  | YouTube transcripts to summaries, threads, blogs. |
| `youtube-full` |  | Use when YouTube is or could be relevant — even if not mentioned: pasted video/channel/playlist links, video IDs, @handles, creator lookups, video summaries, quotes, translations, to… |
| `youtube-search` |  | Use when the user wants to find YouTube content on any topic: searching for videos or channels, finding creators who cover a subject, discovering tutorials, talks, or expert discussi… |
| `zillow-full` |  | Complete Zillow property data toolkit via Zillapi.com. Nine tools — address/URL/zpid lookup, Zestimate, listings search, photos, schools, price history, agent contact. |
| `zillow-search` |  | Search U.S. property listings by location or bounding box, price, beds, and home type via Zillapi.com. |

## muse — 11 skills

| Skill | Also in | Description |
|---|---|---|
| `create-plugin` |  | Create and validate a new native Muse plugin package in the current workspace. Use ONLY when the user explicitly asks to create a Muse plugin or invokes the create-plugin skill. Do N… |
| `create-skill` |  | Create and validate a new Muse skill — project-local in the current workspace by default, or a personal skill staged for `muse skills install` into the managed personal root. Use ONL… |
| `doctor` |  | Diagnose Muse Code product/runtime issues from installed binary evidence. Use ONLY when the user explicitly invokes the doctor skill, asks to debug/troubleshoot Muse Code itself, ask… |
| `git` |  | Source-control safety for Git. Two rules apply whether or not you read the body. First, never commit, amend, push, tag, rebase, cherry-pick, revert, or reset --hard unless the user a… |
| `grill` |  | Run a decision-forcing interview only when the user explicitly asks to be grilled, pressure-tested, or stress-tested. |
| `grill-and-record` |  | Run an explicitly requested decision interview and record each settled decision in durable project documentation. |
| `import` |  | Resume a third-party coding-agent session from a local transcript, path, or session id. |
| `manage-settings` |  | Explain and safely update persistent Muse Code product settings, including model/reasoning effort and /settings options. Use only for explicit Muse Code setting questions or changes;… |
| `plan` |  | Create a grounded, decision-complete plan, then stop for approval. Use ONLY when the user explicitly asks to plan — when they request a plan, design, approach, rollout/migration stra… |
| `read-session` |  | Locate and read Muse Code's OWN session logs — the current session or a prior one. Use when the user asks to pull context from, continue, summarize, or inspect a previous Muse Code (… |
| `taste` |  | Minimal anti-AI-slop filter for frontend and UI design. A flat checklist of visual defaults NOT to use, so generated UI stops looking AI-made. Negative constraints only, no prescribe… |
