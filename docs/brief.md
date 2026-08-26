# Brief — The AI Forward-Deployed Engineer (FDE)

Internal context for agents. The public submission lives in `README.md`.

## What to build

Create a workflow for a real or fictional company that demonstrates FDE judgment on **where to apply AI**.

Include:

1. A workflow map.
2. Identification of deterministic vs. non-deterministic steps.
3. An AI deployment strategy (existing systems + integration points).

## Training requirements

- Core loop: **audit → evals → deployment** (`docs/core-loop.md`).
- Distinction among deterministic / LLM judgment / human-in-the-loop.
- Basic programming (clear code or pseudocode, with error handling).

## How to submit (once the content exists)

1. Public GitHub repository (this one: `https://github.com/renatosantosti/taller-fde-skill`).
2. A README explaining the workflow design and deployment decisions.
3. Code examples or pseudocode for the integration strategies.
4. Submit the repository link.

Do not commit, push, or submit without explicit authorization from the owner.

## Rubric

| # | Criterion | Weight | 3-star | Disqualification |
|---|---|---|---|---|
| 1 | Workflow mapping | x3 | Clear, detailed map of a real or fictional process; each step classified | Incomplete map or missing detail |
| 2 | Deployment strategy | x3 | Integration with existing systems and explicit rationale | Vague or unfeasible strategy |
| 3 | README quality | x2 | Clear, concise, appropriate Markdown | Lacks clarity or required information |
| 4 | Code clarity | x2 | Easy-to-follow logic, comments where they matter | Convoluted code or missing documentation |
| 5 | Error handling | x2 | Anticipates common AI-integration failures and handles them sensibly | No error-handling strategy |

## Step classification

Each map step must be **one** of:

- **deterministic**
- **LLM judgment**
- **human-in-the-loop**

See the rules in `AGENTS.md`.
