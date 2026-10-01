# Prompt Evaluation Harness Reference

## Purpose
Automated testing of prompt versions against golden test cases to catch regressions and measure quality.

## Structure
```
prompts/eval/
├── test-cases/
│   ├── prompt-enhancement.json
│   ├── targetiq-meta.json
│   ├── targetiq-google.json
│   ├── creative-static.json
│   ├── creative-video.json
│   ├── creative-copy.json
│   ├── landing-page.json
│   ├── creative-refresh.json
│   └── closed-loop.json
├── harness.ts
├── runner.ts
└── report.html (generated)
```

## Test Case Format
```json
{
  "prompt": "prompt-enhancement",
  "version": "v1.0",
  "cases": [
    {
      "name": "fitness_app_busy_moms",
      "input": {
        "user_prompt": "fitness app for busy moms who want to workout at home",
        "brand_profile_json": "{...}"
      },
      "expected": {
        "targetAudience.demographics.ageMin": 25,
        "targetAudience.demographics.ageMax": 40,
        "targetAudience.demographics.gender": "female",
        "creativeBrief.hooks": {"contains": ["Problem-Agitation-Solution", "Social Proof"]},
        "platformSpecs.meta.objectives": {"contains": ["LEADS", "CONVERSIONS"]}
      },
      "minScore": 0.85
    }
  ]
}
```

## Harness Implementation (TypeScript)
```typescript
// prompts/eval/harness.ts
import { z } from 'zod';
import { OpenAI } from 'openai';

interface TestCase {
  name: string;
  input: Record<string, any>;
  expected: Record<string, any>;  // Partial match with operators
  minScore: number;
}

interface TestResult {
  caseName: string;
  passed: boolean;
  score: number;
  output: any;
  errors: string[];
  latencyMs: number;
  costUsd: number;
}

class PromptEvaluator {
  private client: OpenAI;
  private promptDir: string;
  
  constructor(apiKey: string, promptDir: string) {
    this.client = new OpenAI({ apiKey });
    this.promptDir = promptDir;
  }
  
  async loadPrompt(promptName: string, version: string): Promise<{system: string, user: string}> {
    const fs = await import('fs/promises');
    const path = await import('path');
    const system = await fs.readFile(path.join(this.promptDir, promptName, version, 'system.md'), 'utf-8');
    const user = await fs.readFile(path.join(this.promptDir, promptName, version, 'user.md'), 'utf-8');
    return { system, user };
  }
  
  async runCase(promptName: string, version: string, testCase: TestCase): Promise<TestResult> {
    const { system, user } = await this.loadPrompt(promptName, version);
    const renderedUser = this.renderTemplate(user, testCase.input);
    
    const start = Date.now();
    const completion = await this.client.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        { role: 'system', content: system },
        { role: 'user', content: renderedUser }
      ],
      temperature: 0.2,
      response_format: { type: 'json_object' }
    });
    const latencyMs = Date.now() - start;
    
    const output = JSON.parse(completion.choices[0].message.content || '{}');
    const costUsd = this.estimateCost(completion.usage);
    
    const { score, errors } = this.scoreOutput(output, testCase.expected);
    
    return {
      caseName: testCase.name,
      passed: score >= testCase.minScore,
      score,
      output,
      errors,
      latencyMs,
      costUsd
    };
  }
  
  private renderTemplate(template: string, vars: Record<string, any>): string {
    return template.replace(/\{\{(\w+)\}\}/g, (_, key) => {
      return JSON.stringify(vars[key] || '');
    });
  }
  
  private scoreOutput(output: any, expected: any): {score: number, errors: string[]} {
    const errors: string[] = [];
    let matches = 0;
    let total = 0;
    
    for (const [path, expectation] of Object.entries(expected)) {
      total++;
      const actual = this.getNested(output, path);
      
      if (typeof expectation === 'object' && expectation !== null) {
        if ('equals' in expectation) {
          if (actual === expectation.equals) matches++;
          else errors.push(`${path}: expected ${expectation.equals}, got ${actual}`);
        } else if ('contains' in expectation) {
          const arr = Array.isArray(actual) ? actual : [actual];
          const allFound = expectation.contains.every((v: any) => arr.includes(v));
          if (allFound) matches++;
          else errors.push(`${path}: missing ${expectation.contains.filter((v: any) => !arr.includes(v))}`);
        } else if ('min' in expectation || 'max' in expectation) {
          const num = Number(actual);
          if (!isNaN(num) && 
              (!('min' in expectation) || num >= expectation.min) && 
              (!('max' in expectation) || num <= expectation.max)) {
            matches++;
          } else {
            errors.push(`${path}: ${num} outside range`);
          }
        }
      } else {
        if (actual === expectation) matches++;
        else errors.push(`${path}: expected ${expectation}, got ${actual}`);
      }
    }
    
    return { score: total > 0 ? matches / total : 0, errors };
  }
  
  private getNested(obj: any, path: string): any {
    return path.split('.').reduce((o, k) => o?.[k], obj);
  }
  
  private estimateCost(usage: any): number {
    return (usage.prompt_tokens * 5 + usage.completion_tokens * 15) / 1_000_000;
  }
  
  async runSuite(promptName: string, version: string): Promise<TestResult[]> {
    const fs = await import('fs/promises');
    const path = await import('path');
    const testFile = path.join(this.promptDir, 'eval', 'test-cases', `${promptName}.json`);
    const content = await fs.readFile(testFile, 'utf-8');
    const { cases } = JSON.parse(content);
    
    const results: TestResult[] = [];
    for (const testCase of cases) {
      console.log(`Running ${testCase.name}...`);
      const result = await this.runCase(promptName, version, testCase);
      results.push(result);
      console.log(result.passed ? '✅ PASS' : '❌ FAIL', `(${result.score.toFixed(2)})`);
    }
    
    return results;
  }
  
  generateReport(results: TestResult[], promptName: string, version: string): string {
    const passed = results.filter(r => r.passed).length;
    const total = results.length;
    const avgScore = results.reduce((a, b) => a + b.score, 0) / total;
    const totalCost = results.reduce((a, b) => a + b.costUsd, 0);
    const totalLatency = results.reduce((a, b) => a + b.latencyMs, 0);
    
    return `
# Evaluation Report: ${promptName}@${version}

## Summary
- **Pass Rate**: ${passed}/${total} (${(passed/total*100).toFixed(1)}%)
- **Average Score**: ${avgScore.toFixed(2)}
- **Total Cost**: $${totalCost.toFixed(4)}
- **Total Latency**: ${totalLatency}ms

## Results
${results.map(r => `
### ${r.caseName}
- **Status**: ${r.passed ? '✅ PASS' : '❌ FAIL'}
- **Score**: ${r.score.toFixed(2)}
- **Latency**: ${r.latencyMs}ms
- **Cost**: $${r.costUsd.toFixed(4)}
${r.errors.length > 0 ? `- **Errors**:\n${r.errors.map(e => `  - ${e}`).join('\n')}` : ''}
`).join('\n')}
    `.trim();
  }
}

export { PromptEvaluator, TestCase, TestResult };
```

## Runner Script
```typescript
// prompts/eval/runner.ts
import { PromptEvaluator } from './harness.js';

async function main() {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error('OPENAI_API_KEY required');
  
  const evaluator = new PromptEvaluator(apiKey, './prompts');
  
  const prompts = [
    'prompt-enhancement',
    'targetiq-meta',
    'targetiq-google',
    'creative-static',
    'creative-copy',
    'landing-page',
    'creative-refresh',
    'closed-loop'
  ];
  
  for (const prompt of prompts) {
    console.log(`\n=== Evaluating ${prompt} ===`);
    const results = await evaluator.runSuite(prompt, 'v1.0');
    const report = evaluator.generateReport(results, prompt, 'v1.0');
    
    await Bun.write(`./eval/report-${prompt}.md`, report);
    console.log(report);
  }
  
  const allResults = [];
  for (const prompt of prompts) {
    const results = await evaluator.runSuite(prompt, 'v1.0');
    allResults.push(...results);
  }
  
  const totalPassed = allResults.filter(r => r.passed).length;
  console.log(`\n=== OVERALL: ${totalPassed}/${allResults.length} passed ===`);
}

main().catch(console.error);
```

## CI Integration
```yaml
# .github/workflows/prompt-eval.yml
name: Prompt Evaluation
on:
  push:
    paths:
      - 'prompts/**'
  schedule:
    - cron: '0 2 * * 0'  # Weekly

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1
      - run: bun install
      - run: bun run prompts/eval/runner.ts
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      - uses: actions/upload-artifact@v4
        with:
          name: prompt-eval-reports
          path: eval/report-*.md
```

## Golden Test Case Creation Workflow
1. Run prompt manually with known good input
2. Review output with domain expert
3. Save as test case with `expected` fields for critical paths
4. Set `minScore` based on importance (0.9 for core, 0.7 for exploratory)
5. Add to version control

## Regression Detection
- Run eval on every prompt change
- Fail CI if pass rate drops below 90%
- Alert on cost increase > 20%
- Track latency trends