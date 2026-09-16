# Changelog

All notable changes to Fantasy Command Center are documented here.

The project is currently in active beta development. Version numbers reflect iterative product updates rather than formal production releases.

## v2.19 — Transaction Priority Queue
**2026-09-16**

- Add a unified Move Priority card that ranks actionable Streamer Finder and ordinary waiver/add-drop recommendations against the same roster-capacity budget.
- Rank true one-week starter improvements primarily by projected starter gain, then use roster-utility improvement, coverage urgency, competition, and a modest transaction-cost signal as supporting factors.
- Allocate open roster slots sequentially so only the highest-priority move can consume a single free slot; later moves must identify a distinct protected churn path or show `BLOCKED — NO SAFE DROP`.
- Deduplicate the same free agent when he appears in both Streamer Finder and ordinary waiver logic, preserving the richer streaming context for QB/TE/K/DEF decisions.
- Feed Move Priority #1 into This Week's Action Plan while preserving the detailed Streamer Finder, Waiver Claim Planner, Add/Drop, and Drop Review evidence underneath.
- Add a real JavaScript behavior regression fixture for the Week 2 two-streamers/one-open-slot case: Jake Ferguson (+5.2) ranks ahead of Tampa Bay (+3.7), gets the open slot, and Tampa Bay is blocked unless a safe drop exists.

## v2.18.3 — Streamer → Waiver Planner Handoff
**2026-09-16**

- Carry the exact `STREAM` candidate selected in Streamer Finder into Waiver Claim Planner instead of only scrolling to the planner.
- Pin a dedicated `STREAMER REVIEW` card that evaluates the candidate against an open roster slot or the existing canonical safe churn candidate.
- Reuse `dropCandidates()`, `primaryChurnCandidate()`, and `effectiveKeepValue()` so the handoff follows the same roster-protection logic as Drop Review and ordinary add/drop decisions.
- Surface `STREAM EDGE — NO SAFE DROP` when the one-week stream grades well but no protected roster move clears the existing churn threshold.
- Never assume the incumbent QB/TE/K/DEF starter is the player to cut; the planner can show the stream edge without forcing a transaction.
- Preserve ordinary Waiver Claim Planner rankings when no Streamer Finder handoff is selected, and clear stale pinned reviews on the next Weekly Check.
- Add a permanent regression contract covering exact-candidate propagation, safe-drop reuse, and no-auto-incumbent-drop behavior.

## v2.18.2 — Streamer Decision Clarity
**2026-09-16**

- Make `HOLD` headlines name the incumbent starter being kept rather than the free-agent comparison, so examples read `HOLD Joe Burrow` and `HOLD Jake Bates`.
- Separate true projection-threshold misses from cases where the projection clears the streaming threshold but Weekly Outlook strongly disagrees.
- Label projection-vs-Outlook disagreements as `MODEL CONFLICT` and explain which model favors the incumbent instead of incorrectly saying the projection still needs to clear the threshold.
- Add an `AVAILABILITY CONFLICT` hold reason when the projection clears the threshold but the available option carries a meaningful availability penalty.
- Keep `STREAM` headlines focused on the incoming free agent and preserve the existing Review waiver move handoff.
- Extend the permanent Weekly regression contract to protect incumbent HOLD naming and explicit model-conflict handling.

## v2.18.1 — Streamer Candidate Pool Fix
**2026-09-16**

- Give Streamer Finder its own QB/TE/K/DEF candidate pool instead of reusing the normal waiver pool that intentionally suppresses backup-QB recommendations behind a strong QB1.
- Always compare an incumbent QB such as Joe Burrow against actually unrostered streaming options before returning `HOLD`, rather than showing `no usable available comparison` solely because ordinary QB redundancy logic hid the candidates.
- Keep the dedicated streaming pool free of ordinary QB/TE roster-redundancy penalties while preserving availability/usability screening inside the streaming recommendation itself.
- Add a compact `Review waiver move` handoff to every `STREAM` result; the button scrolls to Waiver Planner/Drop Review and never auto-selects a player to cut.
- Extend the permanent Weekly regression contract to require the dedicated streamer pool, prohibit strong-QB suppression inside it, verify the handoff wiring, and protect the updated Weekly pipeline.

## v2.18 — Streamer Finder
**2026-09-16**

- Add a dedicated Waivers-tab Streamer Finder for one-week QB, TE, K, and DEF decisions; RB/WR remain in the normal waiver/add-drop engine.
- Compare the current starter with the strongest usable available option using league-scored projected points as the primary decision signal, with Weekly Outlook, game environment, and availability as supporting context.
- Use conservative position thresholds (QB/DEF +2.0 projected points; TE/K +1.5) and label smaller apparent gains as `NO-ACTION STREAMING EDGE` rather than recommending churn.
- Prevent players with meaningful availability penalties from becoming automatic stream recommendations, and require Outlook not to strongly contradict a projection-led move.
- Treat a missing/unusable required-position starter as a coverage case, while keeping roster-space/drop decisions in the existing Drop Review and Waiver Planner instead of assuming the incumbent starter should be cut.
- Add Streamer Finder to the Waivers sub-navigation and the permanent Weekly regression contract.

## v2.17.3 — Weekly Regression Tests
**2026-09-16**

- Add a permanent GitHub Actions regression workflow for Weekly-mode changes instead of relying only on manual post-deploy checks.
- Add a structural Weekly contract test that verifies the complete `loadWeekly()` dependency chain, critical projection/simulation helpers, required DOM anchors, Enter/Connect and Weekly Check event wiring, confidence-guardrail copy, and frontend JavaScript syntax.
- Explicitly protect the projection helpers whose accidental removal caused the v2.17.1 Weekly Check regression.
- Add a live Sleeper integration smoke test that verifies the configured league, manager, owned roster, current matchup endpoint, and the same-origin projection, usage, and calibration snapshots used by Weekly mode.
- Run the regression suite automatically for `index.html`, test, and regression-workflow changes, and on pull requests that touch those paths.
- Keep the suite intentionally lightweight and dependency-free so it can fail quickly before future Weekly changes are treated as validated.

## v2.17.2 — Weekly Check Regression Fix
**2026-09-16**

- Restore the projection helper functions accidentally removed by the v2.17.1 calibration-summary replacement.
- Fix the runtime failure that allowed Sleeper connection to succeed but prevented `Run Weekly Check` from rendering roster, Outlook, Start/Sit, availability, and simulation results.
- Restore league-scored projection lookup, lineup projection totals, projection-optimal lineup construction, projected league median, and nonlinear scoring-key detection.
- Preserve all v2.17.1 simulation confidence guardrails, no-action thresholds, calibration collection, current-week resolution, usage, median strategy, waivers, trades, and Enter-to-Connect behavior.
- Add semantic regression checks requiring every restored projection helper to exist before the hotfix can commit.

## v2.17.1 — Simulation Confidence Guardrails
**2026-09-16**

- Label simulation probabilities as `PROVISIONAL • LOW CONFIDENCE` while empirical calibration is still collecting instead of presenting early-season probabilities with false precision.
- Automatically upgrade confidence to `CALIBRATED • MED CONFIDENCE` once empirical position variance begins blending, and reserve `HIGH CONFIDENCE` for at least four completed calibration weeks with five position groups ready.
- Add an explicit simulation lineup-change threshold: 3.0 percentage points while confidence is low, 2.0 pp at medium confidence, and 1.5 pp at high confidence.
- Treat projection-optimal lineup probability changes below the active threshold as a `NO-ACTION TIE` rather than an actionable edge.
- If a projection-optimal lineup clears the active threshold, surface it as simulation support for review without allowing the simulator to override the separate Start/Sit consensus engine automatically.
- Avoid positive/green simulation styling solely from favorable probabilities while calibration confidence remains low; under-pressure outcomes can still show warning context.
- Preserve the 6,000-iteration pregame simulation, 12% same-team shared factor, empirical-calibration collection, projection coverage requirements, league-median modeling, and live-scoring guardrail.

## v2.17 — Simulation Calibration Foundation
**2026-09-16**

- Begin collecting one stable pregame Sleeper projection snapshot per NFL week for empirical simulation calibration instead of permanently relying on fixed variance assumptions.
- Refresh the weekly calibration snapshot through Thursday 6:00 PM Eastern, then freeze it so later projection changes cannot rewrite the baseline being evaluated.
- Add an automated calibration job that compares completed frozen projections with realized Sleeper weekly PPR results using matching Sleeper player IDs.
- Estimate projection-error dispersion by QB, RB, WR, TE, K, and DEF, while requiring at least two completed archived weeks and 50 samples at a position before empirical variance can influence simulations.
- Shrink empirical variance estimates toward the conservative v1 baseline rather than switching abruptly to noisy early-season estimates.
- Load `data/calibration.json` into Weekly Simulation and show whether variance is still `CALIBRATION COLLECTING` or has advanced to an empirical blend.
- Keep the existing minimum variance floors, 12% same-team shared factor, projection-coverage requirements, pregame-only guardrail, lineup consensus, median strategy, waivers, trades, news, weather, and usage behavior.
- Calibration collection starts with the current Week 2 projection cycle; do not fabricate a Week 1 archive after the fact because it would not represent the projection information that existed before Week 1 games.

## v2.16.4 — Enter-to-Connect Shortcut
**2026-09-16**

- Allow pressing `Enter` in the Sleeper username / display-name field to run the same connection flow as clicking the Connect button.
- Prevent the keyboard shortcut from submitting twice while a connection attempt is already in progress.
- Preserve the existing Connect button, manager datalist suggestions, current-week resolution, weekly navigation, lineup consensus, simulation, median strategy, usage, waivers, trades, news, weather, and availability behavior.

## v2.16.3 — Median Strategy Integration
**2026-09-16**

- Bring the already-existing league-median live panel and pregame simulation probability into one coherent median view instead of making the manager reconcile separate cards.
- Keep live score, live median, and live league rank as the in-game source of truth.
- Add a pregame median forecast showing the connected lineup projection, projected league median, and simulated probability of beating the median when coverage requirements are met.
- Reuse the existing 6,000-iteration Weekly Simulation output rather than creating a second probability model.
- Remove the stale v2.14-era message claiming Probability Above Median is not available now that the projection and simulation layers exist.
- Avoid showing a misleading 1/10-style league rank before scoring begins; pregame rank is displayed as unavailable until teams actually score.
- Add conservative pregame median context to the Weekly Action Plan for under-pressure, swing-zone, and clearly favorable median paths.
- Do not automatically override Start/Sit on the basis of median probability; model-split lineup changes still require a meaningful projection, role, availability, or consensus edge.
- Preserve current-week resolution, usage snapshots, lineup consensus, H2H simulation, waivers, trades, news, weather, and availability behavior.

## v2.16.2 — Current Week Resolution
**2026-09-15**

- Resolve the default Weekly management week from Sleeper's official NFL state plus fresh same-season projection and usage snapshots instead of assuming the raw state pill is always the best management-week signal.
- Allow a fresh projection/usage snapshot to move the default at most one week ahead when Sleeper's raw state is still on the prior week, preventing Week 2 analysis from reconnecting to Week 1.
- Keep the Week field fully editable; a manually selected historical/future week is never overwritten by a normal Weekly check.
- Make the NFL-state pill explicit when values differ: it can show `analysis W2 • Sleeper state W1`, or `selected W3 • current W2` for a manual override, instead of misleadingly labeling the selected analysis as the raw Sleeper week.
- Prefer Sleeper `week` / `leg` as official state fields and treat `display_week` only as a fallback because Sleeper permits display week to differ from the underlying week.
- Preserve v2.16.1 usage snapshots, v2.16 lineup consensus, projections, simulation, league median, waiver, trade, news, and availability behavior.

## v2.16.1 — Usage Snapshot Reliability
**2026-09-15**

- Fix the Week 2 `usage baseline unavailable` condition caused by browser-time dependency on redirected GitHub release assets.
- Add `scripts/update_usage.py` and a permanent GitHub Actions workflow that snapshots nflverse weekly player stats and snap counts into `data/usage.json` four times per day during NFL-season months.
- Load the same-origin usage snapshot first in Weekly mode, with the previous direct nflverse CSV request retained only as a fallback.
- Store current-season completed-week data plus a compact late-season prior-year fallback so Week 1 can still use a deliberately down-weighted historical workload baseline.
- Preserve the existing usage model, player matching, target/carry/snap calculations, Start/Sit consensus engine, projections, simulation, waiver, trade, news, and availability logic.

## v2.16 — Lineup Consensus Engine
**2026-09-15**

- Add a two-model Start/Sit consensus layer instead of mathematically blending Weekly Outlook scores with projected fantasy points.
- Run the existing Weekly Outlook optimizer and league-scored projection optimizer side by side for the selected week.
- Label lineup changes supported by both models as `MODEL AGREEMENT` and surface disagreements as `MODEL SPLIT` review items rather than automatic starts.
- Surface projection-only lineup changes inside Start/Sit so users no longer have to reconcile a separate projection card manually.
- Show projected-point edges next to Outlook edges when both compared players have current-week projections.
- Add lineup-summary context for current projected points, Outlook-optimal projected points, projection-optimal projected points, and starter-set agreement when projection coverage is sufficient.
- Exclude OUT / IR / PUP / NFI / DOUBTFUL players from the Weekly Outlook optimized lineup, matching the existing positional-coverage and projection-optimizer availability guardrails.
- Keep Weekly Outlook, projection points, and simulation probabilities as distinct concepts; no conversion of heuristic Outlook scores into fantasy points or win probability is introduced.
- Preserve v2.15.3 in-season baseline cleanup, waiver, trade, league-median, simulation, usage, weather, news, and roster-management behavior.

## v2.15.3 — In-Season Baseline Cleanup
**2026-09-15**

- Isolate the Aug. 29/30 expert-consensus ECR snapshot and embedded preseason news adjustments to Draft Day / immediate post-draft analysis.
- Remove preseason `newsAdjustments` from Normal Weekly scoring and free-agent rationale.
- Replace the Weekly base-value market anchor with current Sleeper/search market rank at a lighter weight, allowing live role, usage, availability, current news, game environment, weather, projections, and roster construction to carry more of the in-season decision signal.
- Remove stale draft ECR from Trade Intelligence market ranking while preserving its existing current usage, availability, news, age, position-scarcity, keeper, and roster-impact adjustments.
- Use current in-season market rank for normal-weekly free-agent tie breaks and TE-depth filtering; retain draft ECR only where the user explicitly runs the immediate Post-Draft scan.
- Change Best Available Adds metadata from preseason ECR-first wording to current market rank, with draft ECR shown only in Post-Draft mode.
- Replace the Weekly `Strategy rankings: Aug 30 snapshot` badge with `In-season model: current` and relabel the global snapshot badge as `Draft board snapshot: Aug 30`.
- Keep the v2.15 projection layer as an independent cross-check rather than silently making projected points the primary Weekly Outlook input.
- Preserve the v2.15.2 pregame simulation engine, league-median logic, navigation, positional coverage, waiver, and Start/Sit guardrails.

## v2.15.2 — Weekly Simulation Engine
**2026-09-15**

- Add a conservative pregame Monte Carlo simulation layer on top of the league-scored projection foundation.
- Run 6,000 repeated weekly outcomes and estimate P(beat H2H opponent), P(beat league median), and the combined 2–0 weekly result when median scoring applies.
- Simulate the full adequately-projected league each iteration so the median threshold moves with simulated team scores rather than being treated as a fixed number.
- Compare the current starter set with the projection-optimal legal lineup using common random draws, allowing the app to show how a proposed lineup swap changes H2H, median, and 2–0 probabilities.
- Add a middle-50% team-score range so projected outcomes are presented as a distribution instead of a single mean.
- Require at least 90% starter-projection coverage for the connected team and H2H opponent before producing probabilities.
- Require at least 80% of league teams to meet that stricter coverage threshold before producing a league-median probability.
- Use position-level variance assumptions plus a modest shared same-NFL-team factor so stacked players are not modeled as completely independent.
- Label the variance model HEURISTIC VARIANCE v1; it is not yet calibrated from this season's projection errors.
- Treat small probability differences as noise rather than automatic lineup-change signals.
- Withhold simulation probabilities once live scoring begins rather than mixing full-game projections with incomplete in-game results.
- Surface a small Overview alert badge when the pregame model puts either the H2H or median path below 45%.
- Show Weekly Simulation in both Overview and Lineup without allowing it to override the existing Outlook optimizer automatically.
- Preserve all v2.15.1 navigation, current-week selection, waiver, trade, injury, usage, weather, projection, and league-median behavior.

## v2.15.1 — Weekly Navigation & Current Week
**2026-09-15**

- Add sticky Weekly sub-navigation with focused Overview, Lineup, Waivers, Trades, and Intel views instead of one continuously growing page.
- Keep the existing Draft Day / Weekly top-level navigation unchanged.
- Preserve the selected Weekly sub-tab in browser storage so managers can return directly to the area they use most.
- Add compact alert-count badges for actionable Lineup, Waiver, and Intel items after each weekly scan.
- Allow cards such as My Roster to appear in more than one relevant view without duplicating their data or decision logic.
- Collapse the weekly two-column grid to one column when the selected view only has content on one side, avoiding empty desktop space.
- On every new Sleeper connection, read the live NFL state and default the editable Week field to Sleeper's current week.
- Keep manual week selection fully available after connection for looking ahead or reviewing another week.
- Preserve v2.15 projection scoring, Weekly Outlook, positional coverage, league median, waiver, trade, news, usage, weather, and injury logic unchanged.

## v2.15 — Projection Foundation
**2026-09-15**

- Add an automated weekly projection snapshot generated by GitHub Actions from Sleeper's public, undocumented projection endpoint.
- Isolate the undocumented projection dependency in `data/projections.json` so the browser app reads a same-origin snapshot instead of relying on live cross-origin projection requests.
- Refresh the projection snapshot every two hours during NFL months and allow manual workflow runs.
- Rescore raw Sleeper projection stats with the connected league's actual `scoring_settings` instead of assuming a generic STD, half-PPR, or PPR format.
- Keep nonlinear yardage/bonus categories explicitly excluded for now rather than pretending an average projection can model threshold-bonus probability correctly.
- Approximate DEF points-allowed scoring from the projected mean points allowed and clearly disclose that approximation.
- Add a Projection Foundation panel showing the connected team's current starter projection, projection-only optimal legal lineup, opponent starter projection, and projected league-median baseline when league-wide starter coverage is sufficient.
- Require at least 70% starter projection coverage for an individual team and at least 80% adequately covered teams before showing a projected league median.
- Add a projection-only lineup cross-check that can identify a different starter set without automatically overriding the existing Weekly Outlook optimizer.
- Add projected points to My Roster rows when the selected-week snapshot contains the player.
- Preserve the existing Weekly Outlook score as a separate decision-support model; projected fantasy points do not replace it yet.
- Continue to withhold head-to-head and median win probabilities until projection-error variance is calibrated well enough to support a defensible simulation model.

## v2.14.2 — League Median Intelligence
**2026-09-13**

- Detect Sleeper's league-median rule automatically from `settings.league_average_match`.
- Respect `playoff_week_start` so the extra median result is treated as a regular-season rule rather than applied during fantasy playoffs.
- Add a League Median panel to Weekly mode showing the connected manager's live score, the live league median, score margin, and league score rank.
- Calculate the median directly from the selected week's Sleeper matchup scores, including the average of the two middle scores in even-team leagues.
- Label pregame, above-median, below-median, and tied states without presenting the live threshold as a projection.
- Add league-median context to the Matchup Snapshot and Start/Sit summary.
- Surface a Weekly Action Plan note when the connected team is below or very close to the live median.
- Keep Start/Sit focused on maximizing expected lineup quality rather than inventing opponent-specific or median-specific probabilities.
- Explicitly defer “Probability Above Median” until a defensible fantasy-points projection and league-wide simulation layer exists; Weekly Outlook scores are not converted into fake win probabilities.
- Preserve all v2.14.1 positional-coverage logic and existing recommendation guardrails.

## v2.14.1 — Positional Coverage Logic
**2026-09-13**

- Add required-position coverage detection using the league's actual starting roster positions.
- Treat OUT / IR / PUP / NFI / DOUBTFUL players as unavailable for coverage planning while leaving ordinary QUESTIONABLE players usable unless later ruled out.
- Detect when the connected roster does not have enough usable players to fill a required QB, RB, WR, TE, K, or DEF starting slot.
- Temporarily boost legitimate free agents at an uncovered position instead of suppressing them as redundant depth.
- Add a visible POSITIONAL COVERAGE PRIORITY banner to Best Available Adds.
- Add COVERAGE NEED labels to relevant free-agent recommendations.
- Propagate the same coverage need into Add/Drop Opportunities and Waiver Claim Planner.
- Make coverage-restoring waiver claims more urgent without bypassing roster-value and transaction guardrails.
- Add Coverage Priority to the Weekly Action Plan, including the top available replacement when one is detected.
- Keep the injured starter protected from ordinary churn; replacement adds are compared against expendable bench assets instead.
- Automatically remove the emergency boost once a usable replacement is actually on the roster.
- Preserve the existing 24-hour recent-add protection, so a newly acquired replacement is not immediately suggested as the next drop.
- Keep v2.14 Weekly Outlook, Start/Sit, trade, injury-freshness, and roster-utility logic otherwise unchanged.

## v2.14 — Weekly Outlook & Opportunity Engine
**2026-09-01**

- Add a shared Weekly Outlook & Opportunity engine for player-week decision support.
- Centralize market/base value, depth-chart role, recent usage/opportunity, injury/practice availability, game environment, weather, and automated news into one player-week evaluation object.
- Make the Start/Sit Optimizer consume the shared Weekly Outlook score rather than rebuilding its own independent weekly score.
- Make weekly free-agent scoring consume the same underlying weekly context components while preserving roster-construction and positional-redundancy rules.
- Add a Weekly Outlook panel showing each active QB/RB/WR/TE's overall outlook score and the individual base, role, opportunity, availability, game, and news adjustments.
- Add data-confidence labels (HIGH / MEDIUM / LOW) based on the completeness and freshness of available usage, game, weather, availability, and news inputs.
- Explicitly distinguish the Outlook score from projected fantasy points and distinguish data confidence from certainty of player performance.
- Show Weekly Outlook and data confidence in the roster side panel.
- Improve Start/Sit explanations so they reference the same weekly-outlook reasoning used by the optimizer.
- Add a conservative Opportunity Watch to the Weekly Action Plan when current-season workload produces a material positive or negative signal.
- Preserve prior-season Week 1 usage as a reduced-confidence baseline rather than presenting it as current workload.
- Preserve HOLD/no-action behavior when the shared weekly model does not identify a meaningful edge.
- Independent projection feeds, route participation, and richer red-zone opportunity remain future data layers.

## v2.13.1 — Mobile Trade Player Picker
**2026-09-01**

- Replace the Trade Explorer's browser-dependent HTML datalist with a custom touch-friendly player suggestion panel.
- Show rostered-player guidance consistently on desktop, iPhone, and other mobile browsers.
- Show player position, NFL team, fantasy team, manager ownership, and YOURS / OPPONENT status directly in search suggestions.
- Prioritize the connected manager's own roster when browsing the player list with an empty search.
- Allow Trade Explorer search to match player name, NFL team, fantasy team, or manager.
- Stack the Trade Explorer search button below the search field on narrow mobile screens.
- Preserve all v2.13 trade-style and trade-value logic; this update changes only the player-selection UX.

## v2.13 — Trade Explorer & Trade Styles
**2026-09-01**

- Add a persistent Trade Style control with Conservative, Balanced, and Aggressive modes.
- Keep Balanced as the v2.12.3.1 baseline while centralizing all style-specific thresholds in one trade configuration.
- Conservative mode requires tighter market fairness and stronger projected gains for both managers.
- Aggressive mode widens negotiation ranges and consolidation premiums without disabling keeper, 1-QB, raw-overpay, or two-sided-benefit guardrails.
- Add a Trade Explorer view alongside the automatic League Scan.
- Add rostered-player search with automatic ownership detection.
- When the selected player is on the connected manager's roster, lock that player into every outgoing proposal and show realistic return targets across the league.
- When the selected player belongs to another manager, lock that player as the target and generate realistic offers using only the connected manager's roster.
- For opponent targets, surface Best Balanced, Cheapest Plausible, and Acceptance-Leaning offer paths when distinct options exist.
- Show fantasy owner/team context for every explored target.
- Add projected roster-utility change as both raw utility and percentage impact for each manager.
- Clarify that roster-impact percentages are model utility estimates, not projected win probability.
- Keep opponent keepers out of numerical trade recommendations until keeper-rights/cost transfer is explicitly modeled.
- Redirect unrostered player searches toward Add/Drop rather than manufacturing trade advice.
- Keep the League Scan and Trade Explorer on the same underlying valuation, roster simulator, and proposal evaluators to avoid contradictory trade logic.

## v2.12.3.1 — Trade Fit Score Cap Fix
**2026-08-31**

- Fix the remaining 2-for-1 trade-fit calculation so heuristic fit scores are capped at 95 as intended.
- Preserve all v2.12.3 target-tier raw-value ceilings, aggressive-consolidation labels, and trade guardrails.

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
