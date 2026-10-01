# EndoCare doccare Vercel deploy (worked example)

- Vercel account scope: cardzey (CLI user drajeevreddy15-8422). Real project: cardzey/endocare (prj_PZX2o0M2YcC0zg2wT7xexFyx98LU, org team_yrVNWutUGa6knTudLmNInZfU). Live alias: endocare-gold.vercel.app (alias name ≠ project name — the alias belongs to project endocare).
- vercel.json declares `"name": "endocare-gold"` (deprecated field) → a blind `vercel --prod` created a NEW project cardzey/endocare-gold and connected the repo to it, leaving the real project's GitHub check red. Fixed per SKILL.md sequence (.vercel/project.json → deploy to endocare → `echo y | vercel project rm endocare-gold` → `vercel git connect` confirmed "already connected"). Stray project deleted.
- Repo: github.com/drajeevreddy/doccare connected to project endocare via GitHub integration. `gh` CLI authenticated as drajeevreddy; `vercel` CLI authenticated (keyring). Both work directly from the dev box.
- Cron history: keep-alive `0 0 */3 * *` (allowed, ≤ daily); process-reminders was `*/15 * * * *` → Hobby rejection at deploy → changed to `0 9 * * *` (once daily at 9am). Reminder delivery is now a daily pass.
- Env: project endocare has the Supabase env vars; fresh projects (like the accidental endocare-gold) do NOT → build fails at prerender with "@supabase/ssr: Your project's URL and API key are required" on pages importing the client (e.g. /consultation).
- After fixes: GitHub check on latest commit = success; site returns 307 → /auth/login.
