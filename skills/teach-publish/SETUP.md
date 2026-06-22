# teach-publish — one-time setup

You do this **once, ever** — not per course. After it, publishing is a single command and
every future course is instantly live and already private.

What you get: a private site at `https://<your-project>.pages.dev` that only **you** can
open (email one-time-PIN gate), works on your phone with no computer running, free tier,
no credit card.

## Steps

1. **Cloudflare account** — create a free one at <https://dash.cloudflare.com/sign-up>
   (no card needed).

2. **Log in the CLI** — in a terminal:
   ```bash
   npx wrangler login
   ```
   This opens a browser to authorize. (A human must do this — an agent can't.)

3. **First publish** — from your course's repo, run the skill's driver:
   ```bash
   bash publish.sh        # (the skill calls this for you)
   ```
   On first run it asks for a **globally-unique** project name (lowercase, e.g. `my-teach`
   — plain names like `learn` are taken). It saves that to
   `~/.config/teach-publish/config`, creates the Pages project, uploads, and prints
   `https://<name>.pages.dev/<course>/`. At this point the site is **public** — gate it next.

4. **Gate it private (Access)** — in the dashboard:
   - **Workers & Pages → `<your-project>` → Settings → Access policy** → enable it for the
     **Production** deployment.
   - Use this Pages-native toggle. Do **not** hand-roll a separate Zero-Trust application
     pointed at `*.pages.dev` — that path has a known enforcement gap and can leave the
     site open.

5. **Allow only you** — in **Zero Trust → Settings → Authentication**, enable the
   **One-time PIN** login method. Then in the Access policy: **Allow → Include → Emails →
   your email only**. (Free tier covers a single user comfortably.)

6. **Phone** — open the URL, enter your email, get the PIN by email, log in. The session
   cookie lasts ~30 days. **Add to Home Screen** for an app-like icon.

## After setup

- **Update a course:** edit lessons → run the skill → live in ~10s.
- **A new course (even in another repo):** run the skill from there. It drops under a new
  subfolder and redeploys — **already private, zero new setup**.

## Notes / fallback

- The only per-user state is `~/.config/teach-publish/config` (just the project name) and
  your Cloudflare account. The skill folder holds nothing personal.
- If `.pages.dev` Access ever misbehaves, attach a free custom domain to the Pages project
  and gate that hostname instead — same Access policy, more reliable enforcement.
