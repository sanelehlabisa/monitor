# Task 086 changes

- Added a descriptive Monitor title, summary and Open Graph metadata with the existing logo.
- Added robots.txt and a sitemap containing only https://monitor.roventics.com/.
  API and meter-workspace crawl exclusions are preferences, not access control.
  Authentication remains unchanged; no private records or IDs are published.
- Reused Vite's public asset copying; no Docker, environment, API or app UI changes.
- Frontend README records sitemap submission after deployment. Indexing/ranking
  remains a search-engine decision, not a promised outcome of these files.

## Checks

- Source metadata, unchanged app entry, robot rules and sitemap XML checks passed.
- Production Docker build passed, including TypeScript and Vite. Packaged HTML,
  search files, logo and bundled JavaScript were verified in a never-started
  extraction container; owned containers and image tags were removed.
- Host build still encounters the previously documented missing MUI declarations.
  No host dependencies were changed; the clean locked-dependency build passed.
  Vite retains its existing large-chunk warning.
- Evidence: .tmp/task086/seo-check-results.json and seo-packaged-results.json.
- No source service action, data/mail change, file deletion, commit or push.

Related authorized work adds the same search basics in Job Talk on
codex/086-search-discovery. The company-site UI/contact changes and browser checks
are recorded in ../roventics/agents/work/086-company-navigation-and-discovery/.

References: [Google robots.txt guidance](https://developers.google.com/search/docs/crawling-indexing/robots/intro)
and [sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview).

## Publication follow-up

On 25 October 2026 the user explicitly approved committing and pushing all three
repositories to master, including merging Job Talk's feature branch. The earlier
uncommitted/no-push statements describe implementation completion. Publication
reuses the passing checks and verifies tested implementation inputs are unchanged.
VPS rebuilds remain operator actions; this Git handoff does not execute them.
