# Task 096 changes

Removed the company footer logo, credit and link from the app. Monitor's public
entry now presents its own identity. Removed the unused Typography import and
adapted the existing identity assertion. Updated context/frontend guidance.

The production frontend build and all 44 existing frontend checks pass. Production
Compose interpolation validates with config --quiet. The local Docker CLI reports
restricted access to its user config, but Compose validation returns success.
Backend, SQL schema, Compose and proxy configuration have zero changes in this release.

The guest/UI release is ready for a small local-data beta. The user approved
committing and pushing it to master after 504ac1c. Prepared a frontend-only
rebuild followed by an Nginx configuration test and reload command
for the existing edge. Guest-to-account history saving (68.4) and three-day
remembered login (68.6) remain future implementation slices.

Drafted a short personal project post with Cape Town in the title and a tool link.
Read the community's rules on 3 November 2026. The rules prohibit promotions and
AI-generated content, so moderator permission is needed before using a project
link there. The wording is a draft for the owner to review and adapt.
Source https://www.reddit.com/r/capetown/about/rules.json
