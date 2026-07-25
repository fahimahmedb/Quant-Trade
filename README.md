# Quant-Trade — NASDAQ Trading Analysis & Automation

Clean repository structure for quantitative trading on NASDAQ indices.

## 📊 Quick Navigation

### 🎯 For Trading (You are here)
**→ `/finance/trading/`** — Complete analysis phases A-D

- **Phase A**: Diagnostics (VR, ARCH, ACF tests)
- **Phase B**: Direction Signal (LogitL2 classification) 
- **Phase C**: Volatility Model (GJR-GARCH(1,1)-t) ✅ APPROVED
- **Phase D**: Defensive Overlay (Vol-targeting) ✅ APPROVED

**Key files**:
- `SYNTHESE_AUDIT_FINAL.md` — French executive summary (deployment plan)
- `FINAL_DEPLOYMENT_STATUS.md` — Full deployment guide (Week 1-4)

### 💰 Core Libraries
**→ `/finance/`** — Data loaders, core algorithms, scientific models

- `/src/` — Python modules (data_loader, diagnostics, prediction, volatility)
- `/data/` — NASDAQ price history (Composite 5y, 100-index 40y)
- `/scripts/` — Utility runners (fetch data, robustness analysis)

### 🤖 Robot Deployment
**→ `/divers/robot-politique/`** — Paper trading bot (Telegram + Streamlit)

- Fully functional, 100% free (GCP free tier)
- See `EXECUTION_GUIDE.md` for setup

### 📚 Learning Resources
**→ `/cours/`** — Pedagogical documentation

- Course references (ESLSCA ML for Quantitative Finance)
- Academic sources cited in audit framework

### 📋 Other Documents
**→ `/divers/`** — Miscellaneous reports, analysis

---

## ✅ Deployment Status

| Component | Status | Confidence |
|-----------|--------|------------|
| **Phase C (GJR-t Vol)** | ✅ APPROVED | HIGH — SPA p=0.0000, cross-market validated |
| **Phase D (Overlay NDX)** | ✅ APPROVED | HIGH — 40-year backtest, criterion MET |
| **Phase B (Direction)** | ❌ REJECTED | HIGH — DSR fail, selection artifact |
| **Robot** | ✅ READY | MEDIUM — Paper trading only |

**Next**: Deploy Phase C (Week 1), then Phase D (Week 2-4) per `FINAL_DEPLOYMENT_STATUS.md`.

---

## 🚀 Quick Start

```bash
# Deployment guide
cat FINAL_DEPLOYMENT_STATUS.md

# French summary
cat SYNTHESE_AUDIT_FINAL.md

# For developers
cd finance/trading/scripts
python3 run_etape_c.py ../../../data/nasdaq_composite_daily.txt
```

---

## 📖 Framework Reference

This project follows a **canonical statistical audit framework** (21 academic sources):
- Bailey, López de Prado, Hansen, White, Diebold-Mariano, Lo-Mackinlay, Nelson
- Emphasis: no lookahead bias, multiple-testing correction (SPA, DSR), cross-market validation

See `finance/trading/results/AUDIT_CANONICAL_FRAMEWORK_FINAL.md` for full methodology.

---

**Repository**: Quant-Trade  
**Branch**: `claude/price-prediction-model-ykhog1`  
**Contact**: fahimbentata@gmail.com
