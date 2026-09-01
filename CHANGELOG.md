# Changelog

All notable changes to Fantasy Command Center are documented here.

The project is currently in active beta development. Version numbers reflect iterative product updates rather than formal production releases.

## v2.12.3 — Trade Value Tier Calibration
**2026-08-31**

- Add target-tier raw-value ceilings for 2-for-1 trades.
- Allow a somewhat larger consolidation premium for true elite targets while sharply reducing acceptable overpay for lower-tier targets.
- Filter packages like a top TE plus a strong QB for a merely strong WR when the raw outgoing value is excessive.
- Preserve plausible aggressive offers for elite assets when both roster-impact tests remain positive.
- Label surviving 2-for-1 packages with 130%+ raw-value cost as AGGRESSIVE CONSOLIDATION instead of STRONG CANDIDATE.
- Show the raw-offer percentage directly on 2-for-1 recommendations.
- Cap heuristic trade-fit scores at 95 to reduce false precision.

## v2.12.2 — Consolidation Trade Guardrails
**2026-08-31**

- Tighten 2-for-1 trade generation after reviewing recommendations across all league rosters.
- Require the incoming consolidation target to be clearly more valuable than the best outgoing player by himself.
- Reject same-position near-peer upgrades that also require giving away another meaningful asset.
- Add a 1-QB league guardrail so a modest QB upgrade cannot justify attaching a useful RB/WR/TE asset.
- Add a raw outgoing-value ceiling so the consolidation discount cannot hide an extreme overpay.
- Require a larger projected roster improvement for the connected manager on 2-for-1 trades.
- Reject packages where the trade partner captures a disproportionately larger share of the projected benefit.
- Tighten minimum two-sided roster-impact thresholds for 1-for-1 trades.
- Show raw outgoing value alongside discounted package value for 2-for-1 recommendations.
- Replace HIGH CONFIDENCE wording with STRONG CANDIDATE to better reflect heuristic trade analysis.

## v2.12.1 — Trade Realism Guardrails
**2026-08-31**

- Rework trade values with a nonlinear market-rank curve so elite players separate meaningfully from ordinary starters.
- Reduce QB trade-value inflation for this 10-team, 1-QB format while retaining a modest boost for the league's 6-point passing-TD scoring.
- Recalibrate positional need/surplus scoring against the wider trade-value scale.
- Exclude opponent keepers from default trade targets until keeper-rights/cost transfer rules are explicitly modeled.
- Add a roster-utility simulator for QB, RB, WR, TE, and two FLEX spots.
- Require every displayed trade to improve the connected manager's optimized roster and provide positive projected roster impact to the trade partner.
- Add elite-asset premiums and tighter market-value tolerances to 1-for-1 proposals.
- Increase the consolidation discount on 2-for-1 offers so two middling players do not automatically equal one elite starter.
- Require stronger two-sided lineup/depth improvement for 2-for-1 packages.
- Reduce the recommendation panel from eight proposals to a maximum of five higher-quality trade concepts.
- Show market value plus projected roster impact for both sides directly on each recommendation.
- Raise the Weekly Action Plan threshold so only stronger trade concepts are surfaced.

## v2.12 — Trade Intelligence
**2026-08-31**

- Add a league-wide Trade Intelligence module to Weekly mode.
- Build relative RB/WR/QB/TE strength, need, and surplus profiles for every roster in the connected league.
- Generate mutually complementary 1-for-1 trade concepts using player value and positional fit.
- Generate selective 2-for-1 consolidation packages when the connected manager can convert surplus depth into a stronger single asset.
- Use season-long trade value rather than one-week weather/game-environment scoring.
- Add modest recent-usage, availability, news, age, draft-capital, and keeper-context adjustments to trade value.
- Protect the connected manager's current keepers, recent additions, and injury stashes from default outgoing proposals.
- Add a conservative acquisition premium to opponent keeper targets and display their keeper round.
- Detect the league trade deadline when Sleeper exposes it and stop generating proposals after the deadline.
- Add the strongest trade concept to the Weekly Action Plan when it clears the fit threshold.
- Keep proposals player-only for this release; future draft-pick valuation and league-specific keeper-rights transfer rules remain future work.

## v2.11.1 — Churn Recommendation Coherence
**2026-08-31**

- Centralize primary churn-slot selection into one shared roster-utility function.
- Make Drop Review, Add / Drop Opportunities, and the Waiver Claim Planner agree on the same primary drop candidate.
- Rank the canonical churn candidate first in Drop Review and label it PRIMARY CHURN.
- Continue showing other drop candidates as secondary review options.
- Preserve structural QB2/TE2 redundancy logic, draft-capital protection, recent-add protection, IR/PUP protection, and Start/Sit coherence.
- Suppress generic neutral +0 news headlines from free-agent rationale and other player-news summaries, even if an older news.json still contains them.

## v2.11 — Waiver Claim Planner
**2026-08-31**

- Add a Waiver Claim Planner that converts add/drop opportunities into an ordered claim strategy.
- Read the connected roster's waiver position and exposed league waiver-budget/clear-day settings when available.
- Raise the required upgrade threshold for managers holding premium waiver priority.
- Add competition-risk labels using Sleeper 24-hour add trends and player value.
- Add fallback claim ordering so secondary targets can be queued behind the preferred player.
- Add conservative FAAB starting-bid suggestions when a waiver budget is detected.
- Preserve the existing churn-slot, IR, recent-transaction, K/DST, QB2, and Start/Sit coherence guardrails.
- Tighten automated-news quality by suppressing betting/award-odds, power-ranking, mock-draft, and similar fantasy-irrelevant headlines.
- Hide generic neutral +0 news items from the News Intelligence panel.
- Update the GitHub Actions workflow package to checkout/setup-python v7.

## v2.10 — Automated News Intelligence
**2026-08-31**

- Add a zero-cost GitHub Actions news pipeline for the hosted GitHub Pages app.
- Collect publisher-provided NFL RSS/feed metadata from CBS Sports, ProFootballTalk/NBC Sports, and NFL.com when available.
- Store only feed-supplied headline, description, source URL, publication time, and heuristic classification; do not scrape full articles.
- Add a News Intelligence panel for recent roster and top-free-agent headlines.
- Match news to players by name and distinguish direct headline matches from weaker summary matches.
- Add conservative recency- and confidence-weighted news adjustments to Start/Sit, waiver, and roster-utility scoring.
- Add significant starter news to the Weekly Action Plan.
- Keep source links visible so users can verify important reports before acting.
- Refresh the hosted news feed every two hours during NFL-season months and only commit when data changes.
- Preserve availability freshness, usage, weather/game context, recommendation coherence, recent-transaction, IR/PUP, K/DST, and QB2 guardrails.

## v2.9.3 — Early-Watch Freshness Threshold
**2026-08-31**

- Add a 72-hour freshness threshold for Questionable tags before the game-week practice window.
- Keep recently updated Questionable players as EARLY WATCH with no scoring penalty.
- Reclassify older preseason/early-week Questionable tags as STALE TAG.
- Prevent 4–7 day-old injury tags from being counted as fresh early-watch information.
- Preserve zero scoring adjustment for both early-watch and stale pre-practice-window tags.

## v2.9.2 — Early-Watch vs. Stale Status
**2026-08-31**

- Separate fresh EARLY WATCH injury statuses from genuinely STALE Questionable tags.
- Keep recently updated Questionable players outside the game-week practice window at zero scoring adjustment.
- Count active, early-watch, and stale availability statuses separately in the Practice & Availability panel.
- Clarify that a fresh early-watch status is current information but not yet actionable.
- Clarify that a stale tag is old information without fresh supporting practice context.
- Preserve active injury/practice alerts, matchup-health logic, Start/Sit scoring, waiver logic, and Weekly Action Plan behavior.

## v2.9.1 — Availability Freshness Guardrails
**2026-08-31**

- Separate active game-week injury concerns from stale preseason/early-week Questionable tags.
- Use days until kickoff, practice participation, and Sleeper status freshness to determine whether a Questionable tag should affect recommendations.
- Treat Questionable players outside the game-week practice window as EARLY WATCH with no automatic scoring penalty.
- Treat Questionable tags older than 48 hours with no practice context as STALE TAG with no automatic scoring penalty.
- Keep DNP, limited practice, Doubtful, Out, IR, PUP, and NFI designations actionable.
- Show active vs. stale availability counts separately in the Practice & Availability panel.
- Prevent stale Questionable tags from creating matchup-health alerts or Weekly Action Plan warnings.
- Preserve all v2.9 practice/injury integration and existing Start/Sit, waiver, roster-utility, IR/PUP, recent-transaction, K/DST, and QB2 guardrails.

## v2.9 — Practice & Availability Intelligence
**2026-08-31**

- Add Sleeper practice-participation data to weekly player evaluation.
- Normalize full, limited, and did-not-participate practice statuses.
- Add injury designation, injury/body-part detail when available, and freshness of Sleeper's latest player-status update.
- Add a Practice & Availability panel for rostered players.
- Add availability-risk adjustments to the Start / Sit Optimizer.
- Add current practice/injury context to weekly waiver and free-agent scoring.
- Add availability context to roster-utility scoring and matchup health.
- Add availability warnings to the weekly action plan.
- Treat full practice as a modest positive signal and DNP/limited participation as risk context rather than standalone sit decisions.
- Preserve usage intelligence, live game context, weather, recommendation coherence, recent-transaction protection, IR/PUP guardrails, K/DST protection, and QB2 suppression.

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
