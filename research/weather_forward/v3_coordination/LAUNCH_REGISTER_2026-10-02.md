# V3 WAVE A LAUNCH REGISTER — 2026-10-02 (coordinator)

Launched by the coordinator on the owner's explicit "Oui" (2026-10-02). Prompts: PROMPT_S0/S1/S2_2026-10-02.md in this directory (coordination commit ea6ebbc).
Plan: blue/weather-v3-orchestration-2026-10-02 @ bfe58f3 (research/weather_forward/v3/BLUE_V3_ORCHESTRATION_2026-10-02.md). Model: claude-sonnet-5-5. Authority flags: all FALSE, t0 NOT_DECLARED.

| WP | Session | Branch (outcome branch) | External heartbeat (cron, min past hour) |
|---|---|---|---|
| S0 compute | session_0184HjGBiAecqkwADq7XLSJ5 | claude/weather-v3-s0-compute-2026-10-02 | trig_011zceDDSAizrCKhk9LwNWkp (46) |
| S1 data archaeology | session_012ubGTfUoU8rXn4tQKhuZwE | claude/weather-v3-s1-data-archaeology-2026-10-02 | trig_01QFKnLFqJuLvB2wrFTnnGa4 (47) |
| S2 capture architecture | session_014NnvWyvDxcUx7uzzx63dJT | claude/weather-v3-s2-capture-architecture-2026-10-02 | trig_01UCb5QKnGnYPWmwYD78fAoy (48) |

Watchdog (coordinator session, minute 16): trig_01LJUasFXqTY1LcmtBfh3yfL. Each session also creates its own self-bound hourly heartbeat (recorded in S<n>.HEARTBEAT on its branch). When S<n>.DONE appears, the watchdog disables both.
Next waves (NOT created): Wave B S3 tail/price, S4 forecast/hindcast, S6 cohort; Wave C S5 ANCOVA/CUPED/pooling; Wave D S7 Blue synthesis; Wave E S8 fresh Astra (plan section 14).
