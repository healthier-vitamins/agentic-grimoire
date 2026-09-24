## Motivations
Given the dichotomy of easily accessible knowledge and constant LLM hallucinations presenting misinformation as fact, how do we improve our productivity and learning, efficiently and responsibly?

This set of skills attempt to solve this issue. 

> This is by no means perfect nor absolutely correct. Please create an issue or pull request if there's any errors/improvements to be made. I'll gladly appreciate it. Thank you!

### Personal Habits
**1. In every single prompt, always attach your personal inference**
You should never offload critical thinking to LLMs. For every prompt, always attach what you think the answer might be alongside your query
 
This brings about 2 major benefits: 
- Attaching your personal inference, right or wrong, ensures you've actually thought about the question
- It gives the LLM more context on where your knowledge stands.

**2. Always use `oracle` and `compass` to ground LLM responses**
One of the best ways to ground LLM responses is to cite credible sources: technical blogs, articles, research papers, etc. 

Always open the cited links to confirm they are indeed relevant. If you don't understand or keep losing focus, you probably lack some foundational knowledge. Use another LLM to **ELI5** or **show worked examples**.

## Install

Install the skills into the central store and symlink them into Claude Code and Codex:

```sh
npx skills add healthier-vitamins/agentic-grimoire --global -a claude-code codex
```

_This shows a picker so you choose which skills to install. In a non-TTY shell add `--yes`._

### Optional: guidelines

If you also want my guidelines, paste the prompt for your agent. Run it again to update.

**Claude Code** (`~/.claude/CLAUDE.md`):

```text
Fetch https://raw.githubusercontent.com/healthier-vitamins/agentic-grimoire/main/guidelines/claude.md.
In ~/.claude/CLAUDE.md, replace the text between the lines
<!-- AGENTIC-GRIMOIRE: MANAGED FILE --> and <!-- END AGENTIC-GRIMOIRE: MANAGED FILE -->
with the fetched text. If the markers are absent, append both markers with the fetched text
between them. Do not change anything outside the markers.
```

<details>
<summary>Remove from Claude Code</summary>

```text
In ~/.claude/CLAUDE.md, delete the lines
<!-- AGENTIC-GRIMOIRE: MANAGED FILE --> and <!-- END AGENTIC-GRIMOIRE: MANAGED FILE -->
and everything between them. Do not change anything outside the markers.
```

</details>

**Codex** (`~/.codex/AGENTS.md`):

```text
Fetch https://raw.githubusercontent.com/healthier-vitamins/agentic-grimoire/main/guidelines/codex.md.
In ~/.codex/AGENTS.md, replace the text between the lines
<!-- AGENTIC-GRIMOIRE: MANAGED FILE --> and <!-- END AGENTIC-GRIMOIRE: MANAGED FILE -->
with the fetched text. If the markers are absent, append both markers with the fetched text
between them. Do not change anything outside the markers.
```

<details>
<summary>Remove from Codex</summary>

```text
In ~/.codex/AGENTS.md, delete the lines
<!-- AGENTIC-GRIMOIRE: MANAGED FILE --> and <!-- END AGENTIC-GRIMOIRE: MANAGED FILE -->
and everything between them. Do not change anything outside the markers.
```

</details>

>The CLAUDE.md and AGENTS.md guidelines delegate work to subagents. There **will** be an increased in tokens consumption rate. Worth it for cleaner context on big tasks, skip it if you want a lean setup.

## All skills

| Skill | What it does |
|---|---|
| oracle | Goes one level deeper on a topic. Surfaces the unknown-unknowns beneath your prompt. **Use when you want to gain deeper knowledge.** |
| compass | **Goes wide instead of deep.** Lays out the alternatives to a chosen solution and recommends one. Use when you want options. |
| storm[^storm] | Heavy research before a big decision. Five expert lenses, contradictions mapped, one confidence-rated pick. Uses Matt Pocock's `grilling` for intake. |
| codewalk | Socratic walkthrough of provided topic/commit SHA/code. Two gears: `--walk` quizzes you on the highest-leverage snippets, `--sweep` traces the code into atomic steps, one chain at a time, to review a diff today. Tracks what you know per project. |
| keystone | Clean code pedagogy. GoF patterns, functions over inline code, OOP. To be applied for all types of code. |
| keystone-react | Same idea as `keystone`, but for React only. Decomposed components, context over prop-drilling, co-located CSS. |
| playbook | Audit changed code against your engineering conventions (race conditions, idempotency, etc) and flag what is missing. |
| skillsmith | Create a new skill or audit an existing one, attempted Matt Pocock philosophies. |
| ticketsmith | Draft a Jira story with checkbox acceptance criteria from a description or the codebase. Interviews you in rounds with Matt Pocock's `grilling`, writes in `scribe` style (prompts to install either if missing). |
| watermark | Turn uncommitted work into clean atomic conventional commits for user to review code easily. Never pushes. |
| scribe | Write for one reader, in the voice of your samples. Mechanism over concept, length borrowed from the document, and a cleanup pass against AI tells. |

### STORM
STORM is extremely heavy, but it provides the most detailed output compared to `oracle` and `compass`. My personal approach is first tackle unknowns with `oracle` and `compass`. Once you feel relatively comfortable in diving deeper, proceed with `storm`.

## When to reach for what

**Understanding something**
- Deeper on one thing: `oracle`
- Wider across options: `compass`
- Serious research before deciding: `storm`
- Learn any code/module: `codewalk`
- Review a diff before you approve it: `codewalk --sweep`

**Writing code**
- General: `keystone`
- React: `keystone-react`
- Check it against your conventions: `playbook`

**Shipping**
- Commits: `watermark`
- Jira story: `ticketsmith`

**Authoring skills**
- Attempted Matt Pocock's philosophies on writing skills: `skillsmith`

**Plain language**
- Write or cut prose for one reader, in your own voice: `scribe`

## For non-development work

You do not need to write code to get value here. The knowledge skills work on any topic, not just code.

- `oracle` goes deep on one thing and teaches you what you didn't know to ask.
- `compass` lays out your options and picks one, great for decisions.
- `storm` does serious research before a big call, with a confidence-rated recommendation.
- `ticketsmith` turns a plain description into a proper Jira ticket, no coding needed.
- `scribe` writes or cuts any prose for one reader, no coding needed.

The rest of the skills are aimed at people writing or reviewing code.

## Recommended Skills

### Matt Pocock's Skills

A separate collection worth installing alongside these. Install with:

```sh
npx skills@latest add mattpocock/skills
```

Brief suggested skills:

- `/grill-me` interviews you about a plan until every branch is resolved. Each round asks every question that is ready at once, with a recommended answer for each.
- `/handoff` compresses the current conversation into a handoff doc so another agent can pick up where you left off.
- `/teach` builds a personalized curriculum to teach you *anything*. Matt used it to learn to solve a Rubik's cube. Custom lessons, diagrams, and practice drills; not limited to code.
- `/wait-what` tells the agent its last message did not land, so it explains the point again a different way.

Sources: [mattpocock/skills](https://github.com/mattpocock/skills), [skills.sh listing](https://www.skills.sh/mattpocock/skills)

### Visual plans

Builder.io's skills for turning plans and diffs into rich, interactive visual artifacts. Scannable and commentable before any changes begin. Install with:

```sh
npx @agent-native/skills@latest add
```

_The interactive picker preselects `visual-plan` and `visual-recap`. The installer also asks where visual plans should live: hosted shareable links (recommended), local files only, or a self-hosted/custom Plan app._

Brief suggested skills:

- `/visual-plan` turns a text plan into an interactive visual plan with diagrams, file maps, annotated code, and open questions.
- `/visual-recap` turns a diff, branch, or commit into an interactive visual recap with annotated changes and file maps.

Source: [BuilderIO/skills](https://github.com/BuilderIO/skills)

[^storm]: The `storm` skill adapts the STORM method from Stanford OVAL. If you build on this work, please cite: Shao et al., *Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models*, NAACL 2024 (https://www.alphaxiv.org/overview/2402.14207); and Jiang et al., *Into the Unknown Unknowns: Engaged Human Learning through Participation in Language Model Agent Conversations*, EMNLP 2024 (https://www.alphaxiv.org/overview/2408.15232).
