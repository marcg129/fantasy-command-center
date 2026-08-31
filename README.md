# Fantasy Command Center

A responsive fantasy-football decision-support tool built around the Sleeper public API.

**Live demo:** https://marccg129.github.io/fantasy-command-center/

## Overview

Fantasy Command Center began as a personal draft assistant for a 10-team keeper league and has evolved into a reusable multi-manager beta with:

- Live Sleeper draft syncing
- Keeper-aware recommendations
- Traded-pick detection
- Manager-specific roster construction analysis
- Mobile-responsive design
- Immediate post-draft waiver scanning
- Early weekly roster-management features

The core product question is:

> **Who is the best player or roster move for this specific team, in this specific league, right now?**

Instead of simply repeating generic rankings, the application combines league state, roster construction, player availability, pick spacing, keeper context, and market information to provide more personalized decision support.

## Current Features

### Live Draft Assistant
- Connects to a Sleeper league using the public API
- Reads the live draft board automatically
- Removes drafted players from recommendations
- Detects managers, rosters, keepers, and traded picks
- Tracks upcoming selections
- Detects unusually close picks and applies paired-pick strategy
- Adjusts recommendations for roster construction and positional need
- Uses keeper-adjusted player availability
- Displays tier, value, need, and availability warnings
- Includes a manual `Taken` fallback
- Auto-refreshes during the draft

### Multi-Manager Support
Within the same supported league, the app can personalize recommendations after a manager enters their Sleeper username/display name.

It derives:
- Keepers
- Current roster
- Future picks
- Traded picks
- Position counts
- Pick spacing
- Close-pick leverage

### Mobile Responsive
The interface supports desktop and mobile browsers, including:
- Full-width mobile setup controls
- Responsive recommendation cards
- Stacked mobile layouts
- Mobile-friendly status indicators
- Horizontal scrolling only where appropriate

### Immediate Post-Draft Scan
The Weekly tab includes an aggressive-but-protected scan for players who remain unrostered after the draft and may deserve immediate attention.

It looks for:
- Undrafted players with meaningful market value
- Young RB/WR upside
- Backup RBs with paths to larger workloads
- Players receiving significant Sleeper add activity
- Players who may be better than a manager's weakest bench spot

The model deliberately protects:
- Keepers
- Starters
- Early-round draft capital
- Thin RB/WR depth

### Weekly Command Center — Beta
Current weekly features include:
- Live roster retrieval
- League-specific free-agent detection
- Sleeper trending adds/drops
- Add/drop comparison
- Drop-candidate review
- Waiver-priority display
- Recent league transactions
- Opponent snapshot
- Prioritized weekly action plan

## Technology

- HTML5
- CSS3
- Vanilla JavaScript
- Sleeper public API
- GitHub Pages

No backend or database is currently required.

## Architecture

The application separates three layers:

### 1. Live League State
Pulled from Sleeper:
- League
- Managers
- Rosters
- Drafts
- Draft picks
- Traded picks
- Matchups
- Transactions
- Player data
- Trending adds/drops

### 2. Strategy Layer
Local application logic considers:
- Roster construction
- Positional need
- Keeper value
- Pick spacing
- Player tiers
- Draft capital
- Post-draft churn thresholds
- League-specific scoring

### 3. External Football Intelligence
The current beta uses a manually refreshed strategy/news snapshot.

Future versions may add:
- Injury/practice-report data
- Snap percentages
- Route participation
- Target share
- Carries and red-zone usage
- Weather
- Game totals
- Defensive matchup data
- Independent projections

## Development History

The project has been developed iteratively:

1. Built an initial personal draft assistant
2. Connected it to Sleeper's API
3. Added live draft syncing
4. Added keeper and traded-pick awareness
5. Added manager-specific recommendations
6. Generalized the model for multiple managers
7. Added mobile responsiveness
8. Deployed with GitHub Pages
9. Added a Weekly Command Center beta
10. Added an Immediate Post-Draft Scan

## Current Limitations

This is an active beta and should be treated as decision support rather than an automated authority.

Current limitations:
- Scoring logic is still tuned to the original test league
- External rankings/news are not continuously refreshed
- Practice reports and breaking news are not yet automatically ingested
- Advanced usage metrics are not yet integrated
- Weekly recommendations are still being tested
- Sleeper is currently the only fully supported platform
- An unrostered player may still be subject to waivers
- Recommendations are heuristic/model-driven and do not guarantee player performance

## Planned Improvements

### Draft
- User-configurable scoring
- Automatic scoring-rule parsing
- Improved player-tier modeling
- Better estimates of whether a player will survive to the next pick
- Draft-history analytics
- Manager tendency modeling

### Weekly
- Start/sit optimization
- Injury and practice-report integration
- Snap and route participation
- Usage-trend detection
- Waiver claim recommendations
- Streaming recommendations
- Opponent-specific floor/ceiling strategy
- Trade-target identification
- Buy-low / sell-high analysis
- Playoff schedule planning

### Platform Support
Potential future integrations include Yahoo Fantasy and other platforms with supported APIs or permitted integrations.

## Running Locally

Because the application is static, `index.html` can be opened directly in a browser.

For more reliable API testing, serve the folder locally:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

## Deployment

The project is deployed through GitHub Pages from the `main` branch.

Typical workflow:

1. Update `index.html`
2. Commit changes
3. Push to `main`
4. GitHub Pages republishes the site

## Data & API Notes

Fantasy Command Center currently uses Sleeper's public API.

The project was created for personal/non-commercial use. Any commercial version would require a separate review of API terms, data licensing, redistribution rights, and other applicable requirements.

No Sleeper passwords or authentication credentials are stored.

## Project Structure

```text
fantasy-command-center/
├── index.html
├── README.md
└── .gitignore
```

## Portfolio Presentation

Recommended screenshots to add:
1. Desktop live draft view
2. Mobile draft view
3. Best Choices Right Now panel
4. Immediate Post-Draft Scan
5. Weekly Command Center

This project demonstrates:
- API integration
- Real-time data consumption
- Responsive frontend development
- State management in vanilla JavaScript
- Recommendation-system design
- Data-driven decision support
- Iterative product development
- Mobile usability improvements
- Static-site deployment
- Translating domain-specific rules into software logic

## Disclaimer

Fantasy Command Center is an independent personal project and is not affiliated with or endorsed by Sleeper.

Fantasy recommendations are decision-support outputs and do not guarantee player performance.
