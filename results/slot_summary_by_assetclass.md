# Slot Summary by Asset Class — who wins each slot, across assets

> **FLAT / non-regime-conditioned.** 'Wins most often' = most FDR-surviving best-in-slot finishes across the assets in that class, on full history. This is the closest thing to actionable, but it is still not regime-validated.

- Continuous IC tests with valid p-value: **2316**  |  raw p<0.05: **570**  |  survive FDR@0.1: **399**

## credit

### Trend slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| TR-VORTEX-14 | 1 | SUBSTITUTE | PARTIAL |

### Momentum slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| MO-TSI-13-25 | 1 | SUPPRESS | DISAGREES(regime-mask?) |

### Volatility slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| VO-UI-14 | 1 | MAINTAIN | AGREES |

### Volume slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| VL-CMF-20 | 1 | SUBSTITUTE | PARTIAL |

## energy

### Trend slot
_No FDR-surviving winner in this slot for any asset in this class._

### Momentum slot
_No FDR-surviving winner in this slot for any asset in this class._

### Volatility slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| VO-ATRRATIO-14 | 1 | MAINTAIN | AGREES |

### Volume slot
_No FDR-surviving winner in this slot for any asset in this class._

## equity

### Trend slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| TR-VORTEX-14 | 3 | SUBSTITUTE | PARTIAL |
| TR-TRIX-15 | 1 | SUPPRESS | DISAGREES(regime-mask?) |
| TR-ADX-14 | 1 | MAINTAIN | AGREES |

### Momentum slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| MO-TSI-13-25 | 3 | SUPPRESS | DISAGREES(regime-mask?) |
| MO-STOCH-14 | 1 | SUPPRESS | DISAGREES(regime-mask?) |

### Volatility slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| VO-UI-14 | 3 | MAINTAIN | AGREES |
| VO-DCW-20 | 1 | MAINTAIN | AGREES |
| VO-ATRRATIO-14 | 1 | MAINTAIN | AGREES |
| VO-BBP-20-2 | 1 | SUBSTITUTE | PARTIAL |

### Volume slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| VL-ADOSC-3-10 | 2 | MAINTAIN | AGREES |
| VL-EOM-14 | 1 | SUBSTITUTE | PARTIAL |
| VL-PVT-SLOPE-5 | 1 | MAINTAIN | AGREES |
| VL-AD-SLOPE-5 | 1 | MAINTAIN | AGREES |
| VL-MFI-14 | 1 | SUBSTITUTE | PARTIAL |

## fx

### Trend slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| TR-VORTEX-14 | 2 | SUBSTITUTE | PARTIAL |
| TR-TRIX-15 | 1 | SUPPRESS | DISAGREES(regime-mask?) |

### Momentum slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| MO-UO-7-14-28 | 2 | MAINTAIN | AGREES |
| MO-TSI-13-25 | 1 | SUPPRESS | DISAGREES(regime-mask?) |

### Volatility slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| VO-RVI-14 | 1 | SUBSTITUTE | PARTIAL |

### Volume slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| VL-AD-SLOPE-5 | 1 | MAINTAIN | AGREES |

## metals

### Trend slot
_No FDR-surviving winner in this slot for any asset in this class._

### Momentum slot
_No FDR-surviving winner in this slot for any asset in this class._

### Volatility slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| VO-ATRRATIO-14 | 1 | MAINTAIN | AGREES |

### Volume slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| VL-CMF-20 | 1 | SUBSTITUTE | PARTIAL |

## rates

### Trend slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| TR-AROONOSC-14 | 1 | SUBSTITUTE | PARTIAL |

### Momentum slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| MO-MOM-10 | 1 | MAINTAIN | AGREES |
| MO-CMO-14 | 1 | SUPPRESS | DISAGREES(regime-mask?) |

### Volatility slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| VO-RVI-14 | 1 | SUBSTITUTE | PARTIAL |
| VO-ATRRATIO-14 | 1 | MAINTAIN | AGREES |

### Volume slot

| indicator | winning assets | shock prior | prior check |
|---|---:|:--:|---|
| VL-ADOSC-3-10 | 1 | MAINTAIN | AGREES |
| VL-OBV-SLOPE-5 | 1 | MAINTAIN | AGREES |

## NOTES
- **FLAT screen caveat:** an indicator strong only in one regime can show near-zero flat IC and be wrongly demoted here. This screen finds best-in-slot on full history; it cannot promote anything to regime-validated.
- **Prior check semantics:** MAINTAIN winner = library prior AGREES; SUPPRESS winner = DISAGREES, flag as possible regime-masking for the regime run; SUBSTITUTE winner = PARTIAL (a second-string indicator leading flat).
- **^TNX** is yield-based (forward change in yield), not price returns.
- **CL=F** is a continuous front-month stitch; roll artifacts possible.
- **Deferred (not fetched):** STAR 50, CSI 300 native, HSI Tech.
