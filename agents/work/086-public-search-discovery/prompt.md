# Task 086: Public app search discovery

## Aim

Add minimal public search metadata while completing the user's company-site cleanup.

## Clarifications

- The user directly requests the company-site changes and missing search basics in the app repositories.
- Company departments confirmed as Engineering, Operations, and Sales & Marketing.
- Monitor's app layout and private meter routes remain unchanged; only the public homepage is listed.

## Change

- Add a descriptive title, summary and sharing metadata using the existing Monitor logo.
- Add public/robots.txt and a homepage-only public/sitemap.xml.
- Record the existing Vite build behavior and Search Console follow-up in the frontend README.
- The related company-site implementation and shared verification are recorded in sibling Roventics work/086-company-navigation-and-discovery.

## Reuse

- Existing HTML entry, public assets, production build and authentication.

## Verify

- Build with existing locked Docker dependencies and inspect packaged metadata, search files, logo and JavaScript.

## Out of scope

- App features, dependencies, backend, proxy, certificates, production data, deployment or Git publication.
