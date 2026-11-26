---
name: checker-board
description: >-
  The board review for an Indonesian business that is already open. Puts the
  business as it really is (its numbers, its channels, what its customers say,
  what changed around it, its papers) in front of a four-member board, each a
  sub-agent reading the evidence through one lens: Money (does it earn after a
  fair owner's salary, what does it keep), Customer (do buyers come back and why
  they leave), Position (can it hold its ground, what is hard to copy, what it
  depends on) and Local market (permits, staff rules, promo culture, the
  calendar, region). Each member scores it, names what threatens it most and
  votes GROW, FIX, PIVOT or CLOSE. Use when the owner asks "should I expand",
  "buka cabang", "should I close", "tutup atau lanjut", "is it worth continuing",
  "what should I focus on", or before a big decision.
argument-hint: "[the decision on the table, e.g. 'open a second outlet']"
---

# checker-board

The big-decision meeting. Four board members read the evidence the checker
gathered and vote on what to do with the business.

What the user typed after `/checker-board`: `$ARGUMENTS`. If it names a decision
(a second outlet, a new channel, a loan, closing), the board votes on that too.

## The rule about the lenses

The four lenses in `${CLAUDE_SKILL_DIR}/lenses.md` are the checker's own
checklists. Members apply them and speak for no one. Write "the Money lens",
never a person's name.

## Step 0: the evidence

The board needs at least `checker/business.md` and `checker/health.md`. If the
health check has not run, run `/checker-intake` and `/checker-health` first.
List what else exists (`channels.md`, `customers.md`, `competitors.md`,
`compliance.md`) and say which lenses will be working with less.

## Step 1: brief the board

Write `checker/board/brief.md`: the decision on the table (if any), then the
evidence files to read, each with a one-line summary of what is in it. **Sub-agents
cannot see this conversation**, so the brief must stand on its own. Do not add
your own view of the business.

## Step 2: convene

Launch four sub-agents in ONE message (Agent tool, `subagent_type:
general-purpose`, one per member), each told: `Read checker/board/brief.md, the
files it lists, and the <lens> section of <path to lenses.md>. Apply ONLY the
<lens> lens and write your memo to checker/board/<lens>.md.` Give the full path
of `${CLAUDE_SKILL_DIR}/lenses.md`; if that path is not expanded, use the base
directory Claude Code printed for this skill. Give the Local market member the
path to `${CLAUDE_SKILL_DIR}/../checker-compliance/reference/` too.

Each memo, in this shape:

```markdown
# <Lens> lens
Score: <1-10> | Vote: GROW / FIX / PIVOT / CLOSE
## What is working
## What threatens it most (the top 3, most dangerous first, each with its evidence)
## What I would want to know before deciding
## If FIX or PIVOT: what exactly, and how we know it worked (the number and the date)
## On the decision on the table (if any): yes / not yet / no, and why
```

The votes mean:

- **GROW**: healthy enough to put more money and time in (a second outlet, a new
  channel, more stock).
- **FIX**: worth keeping; fix the named problems first and spend on nothing new.
- **PIVOT**: the business as it is will not get there; change the product, the
  customer, the channel or the place.
- **CLOSE**: stop before more money goes in. Say what closing well looks like
  (stock, staff, the lease, debts).

## Step 3: the chair's summary

Read the four memos and write `checker/board.md`:

1. The vote, e.g. "3 fix, 1 grow", and the average score.
2. The threats more than one member raised: these go first.
3. The conditions, merged, as a checklist: each with the number that shows it
   is done and a date to check it.
4. On the decision on the table: the board's answer and what would change it.
5. One paragraph: the strongest version of this business the board can see.

Keep the disagreements. A board that agrees on everything was not doing its job.

## Rules

- The board reads the verdict from `checker/health.md`; it does not recompute it
  or overrule it. It may disagree about what to do next.
- No made-up facts. A missing number is an open question, with the checker skill
  that answers it.
- A CLOSE vote is a result, not a failure. Say it plainly and kindly: the owner
  has often put years into this.
- Score the business, not the owner.

## Output

`checker/board/` (brief and four memos), `checker/board.md`. Then say the vote
in one line, and run `/checker-report` to put it all together.
