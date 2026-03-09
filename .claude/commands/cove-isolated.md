---
allowed-tools: Read, Glob, Grep, Bash, Agent
description: Isolated Chain-of-Verification (CoVe) -- verification step runs in a separate agent to prevent confirmation bias.
---

<!-- Inspired by serpro69/claude-starter-kit; based on Meta's CoVe paper (arxiv.org/abs/2309.11495) -->

# Isolated Chain-of-Verification (CoVe)

Apply the 4-step CoVe process with **isolated verification** -- Step 3 runs in a separate agent that cannot see the baseline response, preventing confirmation bias.

## Step 1: Generate Baseline Response

Answer the user's question fully, as you normally would. Write out your complete response under a heading:

```markdown
## Baseline Response
[your full answer here]
```

## Step 2: Plan Verification Questions

Review your baseline response and generate a numbered list of fact-check questions. Focus on claims that could be wrong -- file paths, function signatures, API behavior, version numbers, configuration syntax, behavioral assertions.

```markdown
## Verification Questions
1. [Is the file path X correct?]
2. [Does function Y actually accept parameter Z?]
3. [Is it true that library A supports feature B?]
...
```

Generate 3-8 questions depending on response complexity.

## Step 3: Isolated Verification (Agent)

Launch a general-purpose Agent to answer the verification questions **independently**. The agent must NOT see your baseline response -- only the verification questions. This prevents confirmation bias.

Provide the agent with:
- The numbered list of verification questions from Step 2
- Instructions to use Read, Grep, Glob, and Bash to find evidence
- Instructions to answer each question with CONFIRMED or INCORRECT plus evidence

Example agent prompt:
```
Answer each of these fact-check questions by investigating the codebase. For each question, respond with CONFIRMED or INCORRECT and cite your evidence.

Questions:
1. [question 1]
2. [question 2]
...
```

## Step 4: Generate Final Verified Response

Review the agent's verification results and revise your baseline response, incorporating all corrections. If no errors were found, state that the baseline was verified and present it as final.

```markdown
## Verified Response
[corrected answer, incorporating all verification results]
```

If any corrections were made, add a brief summary:

```markdown
## Corrections Made
- [what changed and why]
```
