# Slate

A calm, minimal planner for iPad: a Home dashboard, three calendar layouts (big date, list with Routines, week planner), routines you drag into your day, an idea board and a daily feeling check-in.

**Live app:** https://imatiny408-tech.github.io/slate-app/

## Install on iPad
Open the live app in Safari, tap Share, then **Add to Home Screen**. Use Slate from that icon: it opens full screen, works offline, and the iPad keeps its data.

## Work from Workspace
If you also use the Workspace app, connect Slate there (Settings → Connections → Slate, with your Slate username and password). Then:

- **Goals:** on a goal in Workspace, press **Send to iPad Slate**. In Slate, tap the suitcase (next to Home) to open **Work**, and pick **Queue** (one task at a time, in order) or **Outline** (the whole goal, numbered by milestone). When the last task is ticked, Slate shows "Completed goal sent to your Workspace" and Workspace shows "“goal” goal was completed on iPad".
- **Work calendar:** your Workspace calendar events show on Slate's month calendar. Use **Show Work Schedule** to hide or show them, and **+ Work event** to add one from Slate; it appears in the Workspace calendar too.
- **Tasks:** tasks you send from Workspace's planner are listed on the Work page; ticking one off here ticks it off in Workspace.

It needs the `work_items` table: run `supabase/work_items.sql` in the Slate Supabase project's SQL editor (run it again after updates; it keeps existing rows).

## Your data
Everything is saved on the device, in the browser's storage for this site. There's no account yet.
- Updates to the app never erase it. Each update only replaces the app's code.
- To move data between devices, or out of the Claude version, use **Settings → Back up or restore data**.

## How updates go live
Every push to `main` runs `.github/workflows/deploy.yml`, which builds `dist/` with `tools/build.py` and publishes it to GitHub Pages. The app picks up the new version the next time it's opened.

## Project layout
- `src/slate.html`: the whole app (the same page that's published as the Claude artifact)
- `public/`: icons and the web app manifest
- `tools/build.py`: wraps the page into an installable web app in `dist/`
- `tools/sw.template.js`: offline support; network first so updates always arrive
