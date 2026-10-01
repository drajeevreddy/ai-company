# Review-gating agent output: the extraction pass

A producer agent is not a reliable witness to its own work. It files a compliance checklist that
overstates (a "zero digits" claim when three captions carried digits, an "untouched" list that omitted
the one file under revision), and it can ignore a review instruction while reporting success. Read the
checklist for orientation, then verify the artifact itself. Everything below is mechanical — run it
before approving anything.

## The pass

Split the artifact on the producer's own headings first, so every finding can be attributed to one
item and one section. Then, in order:

1. **Per-platform limits.** Extract the platform units by their own numbering and measure them:

   ```python
   tweets = re.findall(r"^\d/\d .*$", section, flags=re.M)
   print(len(tweets), max(len(t) for t in tweets))          # count + worst case against the limit
   li = re.search(r"#### LinkedIn.*?\n(.*?)\n\n#### ", section, flags=re.S).group(1)
   body = re.sub(r"#[A-Za-z]+", "", li)                     # hashtags do not spend the char budget
   print(len(body.strip()), len(re.findall(r"#[A-Za-z]+", li)))
   ```

2. **Hook/label budgets.** Word count AND character count, plus a truncation preview — print the
   first 60 characters, because that is all a feed shows before the fold.

3. **Banned-term scan.** Lowercase the whole artifact, then test each banned term as a substring. A
   single miss invalidates the producer's "checked against the banned list" line.

4. **Placeholder scan — the one that ships defects.** Count `[` in the shippable region (everything
   above the producer's report-level notes). Any bracket in a caption, slide, or overlay is a defect,
   not a nag: those blocks get pasted straight onto a live surface, so `[price to confirm]` publishes
   as visible text. Flags belong in a report-level note, never inline.

5. **Empty-slot detection.** A line that is nothing but the CTA wastes a platform unit (a five-tweet
   thread ending on a 22-character link line). Fold the CTA into the previous unit and renumber.

6. **Claim classification.** List every line containing a digit and sort it into *structural* (week
   numbering, list counts, item titles) versus *claim* (company statistics, prices, capacities).
   Structural digits are fine; a claim without a recorded source is a rewrite, not an edit.

7. **Search-then-report on anything named as a fact.** Every number and every named technology gets
   checked against a real source before approval: a repo, a deployment doc, a machine inventory. A
   deployment doc contradicting a "cheap VPS" line is a cut, not a discussion.

## Confirming a review landed

Before sending a second round, string-match every instruction from the previous round against the
current artifact and report the split — landed, not landed — with counts. This is faster and more
credible than asking the producer whether it applied them, and it distinguishes "ignored" from "never
received" when you also quote the original request id.

## Rules for the reviewer

- The reviewer finds defects; the producer fixes them. Do not rewrite the artifact yourself, or the
  chain loses its single owner and the producer never learns the constraint.
- One defect, one named line. "Cut the solicitation" is weaker than quoting the sentence and saying
  which ruling forbids it.
- A second ask in a piece that already has a CTA is a defect even when it reads well. Flag budgets
  exist to be counted, not felt.
- When the producer's flag beats you, fix your own file, recount the source, and credit the
  correction in the facts file. Producers that flag well but apply unevenly are still worth listening
  to on evidence.
