# health-detector

Pulls daily Oura Ring data, condenses sleep / HR / readiness / stress / activity into a single number — the **Relief Index** — and writes a markdown report into my Obsidian vault. One cron away from being a real personal habit.

> The point isn't *"is stress high today"* — Oura already tells you that. It's whether stress and recovery are **balanced**. The Relief Index is the answer in one number.

## What's interesting

**Re-weighted aggregation when fields go missing.** Oura's API occasionally returns `null` for `daily_resilience` or `daily_stress` — usually on travel days or right after a firmware update. Most simple averagers either fill with `0` (penalty for missing data) or skip the day entirely (silence). `analyzer.calc_relief_index` instead **renormalizes the weights over whichever fields came back populated**:

```python
total_weight = sum(WEIGHTS[k] for k in available)
weighted_sum = sum(WEIGHTS[k] * available[k] for k in available)
final_score = round(weighted_sum / total_weight, 1)
```

A partial day still produces a comparable score — and `relief["missing"]` carries the audit trail of which fields were absent.

**Categorical → continuous translation.** Oura's `daily_stress` returns a label (`restored` / `normal` / `stressful`) rather than a numeric score. To put it in the same weighted sum as the numeric metrics, `parse_stress` maps it to `{restored: 90, normal: 65, stressful: 30}`. Crude — but honest about what the API gives you. *Polarity quirk: in code this field is named `stress_score` but its scale is inverted (`restored` = 90 = good). Renaming to `calmness_score` is on the cleanup list.*

**Markdown into the vault, not a fourth dashboard.** `reporter.py` writes a structured daily note (`# 健康日志 · 2026-04-22` … sections for sleep, HR, readiness, stress, activity) directly into `OBSIDIAN_VAULT/OBSIDIAN_HEALTH_DIR`. That's the design choice: the data lands where I already keep my thinking, instead of in a separate app I'd have to remember to open.

## The Relief Index

```
Index = 0.30 · readiness
      + 0.25 · sleep
      + 0.20 · resilience
      + 0.15 · calmness         (mapped from Oura day_summary)
      + 0.10 · activity_balance
```

Then bucketed: ≥80 excellent 🟢 · ≥65 good 🟡 · ≥50 warning 🟠 · else critical 🔴.

### How the weights were chosen — and the honest limit

These are heuristic, not tuned. The reasoning, ranked:

1. **`readiness` is heaviest because it's already an Oura aggregate** — it folds in HRV balance, recovery index, sleep balance, body temperature. Re-weighting those component fields again would double-count.
2. **`sleep` is the clearest single lever** — a low sleep score on a calm day still feels off. Worth a high coefficient.
3. **`resilience` smooths multi-day** — single-day stress can be noise; resilience corrects for that.
4. **`calmness` is intentionally low-weight** — the day-summary categorical is coarse; a 30-minute spike during a meeting can tilt the whole day to "stressful".
5. **`activity` is lowest** — high activity isn't always good; it can dig recovery debt.

**What I'd validate before trusting any of these weights:** correlate the Index against
- next-day climbing send rate (subjective performance)
- end-of-day rating in the Obsidian daily note
- coding-session count from `dashboard-me` (downstream effort)

If `readiness` alone wins on all three, drop the rest.

## Example output

See [`examples/2026-04-22.md`](examples/2026-04-22.md) — the actual file `reporter.py` writes into the vault. Numbers in the example are illustrative, not from a real run.

## Run it

Fill in `config.py`:

```python
OURA_TOKEN = "..."                    # https://cloud.ouraring.com/personal-access-tokens
OBSIDIAN_VAULT = "/path/to/vault"
OBSIDIAN_HEALTH_DIR = "Health"        # subdirectory inside the vault
```

Then:

```bash
pip install requests
python main.py                        # yesterday
python main.py 2026-04-22             # specific date
```

Output: `OBSIDIAN_VAULT/OBSIDIAN_HEALTH_DIR/{date}.md` plus a raw-JSON archive in `data/{date}.json` for re-processing.

## Files

- `client.py` — Oura API v2 client (`daily_stress`, `daily_resilience`, `daily_readiness`, `daily_sleep`, `daily_spo2`, `daily_activity`, `heartrate`)
- `analyzer.py` — per-domain parsers + Relief Index calc + level mapping
- `reporter.py` — markdown generator + Obsidian writer + raw-JSON archive
- `main.py` — CLI entry; runs the pipeline + prints summary
- `config.py` — token, weights, thresholds, Obsidian paths
