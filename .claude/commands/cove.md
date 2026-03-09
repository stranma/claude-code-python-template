---
allowed-tools: Read, Glob, Grep, Bash
description: Chain-of-Verification (CoVe) prompting for high-stakes accuracy. Generates a response, self-verifies with fact-check questions, then revises.
---

<!-- Inspired by serpro69/claude-starter-kit; based on Meta's CoVe paper (arxiv.org/abs/2309.11495) -->

# Chain-of-Verification (CoVe)

Apply the 4-step CoVe process to reduce hallucinations and factual errors in your response to the user's question.

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

## Step 3: Answer Verifications

Answer each verification question independently. Use tools (Read, Grep, Glob, Bash) to check facts against the actual codebase, documentation, or runtime behavior. Do not rely on your baseline response -- verify from source.

```markdown
## Verification Results
1. [CONFIRMED / INCORRECT] -- [evidence]
2. [CONFIRMED / INCORRECT] -- [evidence]
...
```

## Step 4: Generate Final Verified Response

Revise your baseline response, incorporating all corrections from Step 3. If no errors were found, state that the baseline was verified and present it as final.

```markdown
## Verified Response
[corrected answer, incorporating all verification results]
```

If any corrections were made, add a brief summary:

```markdown
## Corrections Made
- [what changed and why]
```
