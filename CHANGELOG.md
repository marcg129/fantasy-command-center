# Changelog

All notable changes to Fantasy Command Center are documented here.

The project is currently in active beta development. Version numbers reflect iterative product updates rather than formal production releases.

## v2.8 — Usage & Opportunity Intelligence
**2026-08-31**

- Add nflverse weekly player-stat data to the Weekly Command Center.
- Add nflverse offensive snap-count data and recent snap-share context.
- Add a Usage & Opportunity panel for rostered QB/RB/WR/TE players.
- Track recent carries, targets, receptions, passing volume, scrimmage production, target share, and offensive snap percentage when available.
- Detect rising, stable, and falling short-term workload trends.
- Add workload-based adjustments to the Start / Sit Optimizer.
- Add recent-usage adjustments to weekly free-agent scoring and add/drop context.
- Add a modest usage component to roster-utility scoring so low-opportunity bench assets are easier to distinguish from useful depth.
- Fall back to a deliberately reduced-weight late-season prior-year workload baseline before enough current-season games exist.
- Preserve live game context, weather, Start/Sit-to-waiver coherence, recent-transaction protection, IR/PUP guardrails, required K/DST protection, and QB2 suppression.

## v2.7 — Live Game Context & Weather
**2026-08-30**

- Add nflverse schedule/game-environment data to the weekly scan.
- Match players to their selected-week opponent, venue, roof type, spread and game total.
- Add an outdoor-weather integration using Open-Meteo when the selected game is within forecast range.
- Add a Game Environment panel for teams represented in the current starting lineup.
- Add game-total and severe-weather adjustments to the Start / Sit Optimizer.
- Add selected-week game-environment context to free-agent scoring and explanations.
- Add opponent/game-environment details to the Matchup Snapshot.
- Keep weather effects deliberately modest so rain or cold alone do not create exaggerated sit recommendations.
- Preserve v2.6.1 recommendation-coherence, IR/PUP, recent-transaction, K/DST and QB2 guardrails.

## v2.6.1 — Recommendation Coherence Fix
**2026-08-30**

- Add a shared decision-coherence layer between Start / Sit and waiver recommendations.
- Protect every player selected by the optimized lineup from automatic drop/churn recommendations in the same scan.
- At redundant one-starter positions, allow the optimizer to redefine which QB/TE is the starter and which becomes the expendable backup.
- Prevent contradictory output such as recommending Brock Purdy as both a Week 1 starter and the roster's primary drop candidate.
- Update drop-review labels to distinguish optimizer-protected starters from current starters displaced by a recommended lineup change.

## v2.6 — Weekly Lineup Command Center
**2026-08-30**

- Add a Start / Sit Optimizer that builds a legal lineup from the manager's active Sleeper roster.
- Read the league's roster-position structure when determining valid starter and FLEX assignments.
- Compare the current Sleeper lineup against an optimized baseline lineup.
- Add START / SIT recommendations with confidence labels and value gaps.
- Add starter injury alerts for major injury/reserve designations.
- Expand the selected-week matchup panel with opponent starters and lineup-health flags.
- Add lineup issues to the weekly action plan.
- Preserve roster-utility waiver logic, recent-add/drop protection, IR/PUP safeguards, and unnecessary-QB2 suppression.
- Clearly label the current optimizer as a baseline pending richer matchup, usage, weather, and live-news data.

## v2.5.7 — Weekly Default & Recent-Add Protection
**2026-08-30**

- Make Normal Weekly Check the default Weekly Command Center mode.
- Keep Immediate Post-Draft Scan available as an optional mode.
- Protect players the manager added within the previous 24 hours from automatic churn recommendations.
- Label recently added players for evaluation instead of immediately suggesting they be dropped.
- Preserve the existing recently-dropped-player and QB2 recommendation guardrails.

## v2.5.6 — QB2 Waiver Guardrails
**2026-08-30**

- Suppress unnecessary QB2 waiver recommendations when a healthy high-end QB1 already solves the position.
- Add an additional QB-value penalty as a safety guardrail.
- Hide players the manager personally dropped from recommendations for 24 hours.
- Prevent the app from immediately recommending that a manager reverse their own transaction.
- Add a UI note explaining that Sleeper roster updates may take a short time to propagate through the public API.

## v2.5.5 — Weekly Tab Fix
**2026-08-30**

- Fix the default navigation state so the Weekly tab is visually highlighted when the Weekly Command Center is the landing page.
- Preserve weekly-first workflow and roster-utility scoring.

## v2.5.4 — Roster Utility Scoring
**2026-08-30**

- Replace raw player-value comparisons with roster-utility scoring for waiver decisions.
- Heavily discount redundant QB2 value in a 10-team, 1-QB league when a strong starter already exists.
- Reduce redundant TE2 utility.
- Preserve additional utility for RB/WR depth in a 2-FLEX format.
- Show standalone player value separately from effective roster utility.
- Improve add/drop explanations so recommendations reflect team context rather than positional ranking alone.

## v2.5.3 — Weekly-First Workflow
**2026-08-30**

- Make Weekly Command Center the default landing page after connecting.
- Always identify a current churn slot.
- Show HOLD / MONITOR comparisons even when no waiver move clears the recommendation threshold.
- Compare available players against a single clearly identified expendable roster spot.
- Prefer redundant QB2/TE2 roster spots over useful RB/WR depth when selecting a churn candidate.

## v2.5.2 — Hard IR/PUP Guardrail
**2026-08-30**

- Add raw-status protection for PUP, IR, and NFI players.
- Exclude protected injury stashes from automatic add/drop pairings even when Sleeper exposes the designation through different status fields.
- Improve IR/PUP detection across `status` and `injury_status`.
- Keep injury stashes available for manual review without allowing the churn engine to force a drop.

## v2.5.1 — IR Pairing Fix
**2026-08-30**

- Strengthen IR eligibility detection.
- Exclude IR-eligible players from automatic add/drop comparisons.
- Prioritize redundant QB2/TE2 roster spots ahead of injured stashes.
- Display more Sleeper status information in the IR management panel.

## v2.5 — Smarter Weekly Roster Logic
**2026-08-30**

- Add IR/PUP-aware roster management.
- Protect injury stashes from automatic drop recommendations.
- Protect a manager's only kicker and D/ST from generic churn logic.
- Increase drop pressure on redundant QB2/TE2 roster spots.
- Reduce the influence of Sleeper trending activity.
- Increase the weight of depth-chart role and opportunity.
- Add an IR / Roster Management panel.
- Improve post-draft add/drop and churn recommendations.

## v2.4 — Active Player Filtering
**2026-08-30**

- Filter inactive, historical, and unsigned players from recommendations.
- Prevent retired/stale Sleeper records such as Todd Gurley, Antonio Brown, and Julian Edelman from appearing as draft or post-draft values.
- Add additional validation to the Immediate Post-Draft Scan.

## v2.3 — Immediate Post-Draft Scan
**2026-08-30**

- Add a dedicated Immediate Post-Draft Scan mode.
- Identify undrafted players who may represent draft-room value.
- Add an Undrafted Steals panel.
- Add more aggressive post-draft roster churn analysis while protecting starters, keepers, and early-round draft capital.
- Add urgency labels such as Immediate Review, Strong Watch, and Watch.
- Introduce the concept of a current churn slot.

## v2.2 — Weekly Command Center Beta
**2026-08-30**

- Add the first Weekly Command Center.
- Pull live Sleeper rosters.
- Detect league-specific free agents.
- Add Sleeper trending add/drop activity.
- Add add/drop comparisons.
- Add drop-candidate review.
- Display waiver priority.
- Show recent league transactions.
- Add opponent snapshot.
- Add a prioritized weekly action plan.

## v2.1.1 — Mobile Responsive Update
**2026-08-30**

- Add responsive mobile layout.
- Improve iPhone usability.
- Stack setup controls on narrow screens.
- Reflow recommendation cards and player metadata.
- Improve mobile status indicators and navigation layout.

## v2.1 — Multi-Manager Beta
**2026-08-30**

- Generalize the draft engine beyond one manager.
- Derive keepers, roster construction, traded picks, and upcoming selections dynamically.
- Detect close-pick leverage automatically.
- Remove manager-specific assumptions from the recommendation model.
- Allow multiple managers in the same Sleeper league to use the same application.

## v2 — Live Sleeper Draft Assistant
**2026-08-30**

- Connect the application to the Sleeper public API.
- Add live draft synchronization.
- Detect keepers and traded picks.
- Remove drafted players from recommendations automatically.
- Add manager-specific roster construction and pick-spacing logic.
- Add recommendation tiers, positional need, and availability warnings.
- Add a manual Taken fallback.
- Add automatic refresh during the draft.

## v1 — Initial Prototype
**2026-08-30**

- Build the original personal fantasy draft assistant.
- Create the first recommendation board.
- Tune the initial model to a specific keeper league and manager roster.
