# Changelog

All notable changes to Fantasy Command Center are documented here.

The project is currently in active beta development. Version numbers reflect iterative product updates rather than formal production releases.

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
