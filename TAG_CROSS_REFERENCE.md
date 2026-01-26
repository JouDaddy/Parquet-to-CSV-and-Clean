# APC Tag Cross-Reference
## Step 2: Instrumentation & Control Study - Complete Tag Mapping

**Date:** 2026-01-17
**Status:** COMPLETE
**Data Source:** Historian Parquet Files (C:\Users\GideonCrous\Documents\Historian Data)

---

## EXECUTIVE SUMMARY

**ALL CRITICAL TAGS FOR APC IMPLEMENTATION ARE AVAILABLE IN THE HISTORIAN.**

| Data Set | Files | Rows per File | Unique Tags |
|----------|-------|---------------|-------------|
| NAP2 | 4 parquet files | ~175,000 | **189 tags** |
| ANP2 | 4 parquet files | ~175,000 | **63 tags** |
| **Total** | 8 files | ~700,000 rows each | **252 tags** |

---

## 1. OBJ-1: PLANT THROUGHPUT CONTROL

### 1.1 Tag Availability - ALL FOUND ✓

| Role | Client SOW | SCADA Tag | **Historian Tag** | Status |
|------|------------|-----------|------------------|--------|
| **CV** | 95FI004 | FI95003A/B/C | **95FI003A/PV, 95FI003B/PV, 95FI003C/PV** | ✅ FOUND |
| **MV** | 95HIC403 | HIC95403 | **95HIC403/PV** | ✅ FOUND |
| **Pressure MV** | 95HIC404 | HIC95404 | **95HIC404/PV** | ✅ FOUND |
| **Shaft Speed** | - | SI95470 | **95SI470/PV, 95SI470/PVMT** | ✅ FOUND |
| **Ambient T** | - | TI95417 | **95TI417/PV** | ✅ FOUND |
| **Pressure** | 95PI007 | PI95007 | **95PI007A/PV** | ✅ FOUND |

### 1.2 Additional Supporting Tags

| Tag | Description |
|-----|-------------|
| 95PI002/PV | Suction pressure |
| 95PI006/PV | Discharge pressure |
| 95PI041/PV | Tailgas pressure (876 kPag on SCADA) |
| 95TI008/PV | Discharge temperature |
| 95TI010/PV | Tailgas temperature |

### 1.3 Control Architecture Confirmation

```
FEEDFORWARD COMPENSATION (APC):
  95TI417/PV (Ambient T) ──► APC Controller ──► 95HIC403/PV (Air IGV)
                                    │
                                    ▼
                              95FI004A/B/C/PV (Air Flow CV)

EXISTING DCS PRESSURE CONTROL (NOT modified):
  95PI007A/PV ──► DCS PID ──► 95HIC404/PV (Tailgas IGV)
```

---

## 2. OBJ-2: CONVERSION EFFICIENCY CONTROL

### 2.1 Tag Availability - ALL FOUND ✓

| Role | Client SOW | SCADA Tag | **Historian Tag** | Status |
|------|------------|-----------|------------------|--------|
| **CV (Ratio)** | 95FFI008 | FFIC95008 | **95FFIC008/PV** | ✅ FOUND |
| **CV (Ratio SP)** | - | - | **95FFIC008/SP** | ✅ FOUND |
| **MV Output** | - | - | **95FFIC008/OUT** | ✅ FOUND |
| **Gauze Temp A** | 95TI016 | TI95016A | **95TI016A/PV** | ✅ FOUND |
| **Gauze Temp B** | - | TI95016B | **95TI016B/PV** | ✅ FOUND |
| **Gauze Temp C** | - | TI95016C | **95TI016C/PV** | ✅ FOUND |

### 2.2 Ratio Calculation Inputs

| Tag | Description |
|-----|-------------|
| 95FI003A/PV | NH3 Flow A (~15,650 Nm³/h) |
| 95FI003B/PV | NH3 Flow B (~15,650 Nm³/h) |
| 95FI003C/PV | NH3 Flow C (~15,650 Nm³/h) |
| 95FI004A/PV | Air Flow A (~138,880 Nm³/h) |
| 95FI004B/PV | Air Flow B (~138,880 Nm³/h) |
| 95FI004C/PV | Air Flow C (~138,880 Nm³/h) |
| 95FFI005A/PV | Ratio reading A |
| 95FFI005B/PV | Ratio reading B |
| 95FFI005C/PV | Ratio reading C |

### 2.3 Control Architecture Confirmation

```
RATIO CONTROL:
  95FI003A/B/C ──┐
                 ├──► 95FFIC008 ──► NH3 Valve
  95FI004A/B/C ──┘     (Ratio)
                        │
                   Target: 10.0-10.5%

SECONDARY CV:
  95TI016A/B/C (Gauze Temp) ──► Constraint/Override
                                Target: 880-900°C
```

---

## 3. OBJ-3: ACID CONCENTRATION CONTROL

### 3.1 Tag Availability - ALL FOUND ✓

| Role | Client SOW | SCADA Tag | **Historian Tag** | Status |
|------|------------|-----------|------------------|--------|
| **CV (Density)** | 95DI023 | DI96001 | **95DI023/PV** | ✅ FOUND |
| **CV (Density %)** | - | DYI96001 | **95DY023/PV** | ✅ FOUND |
| **MV (Water)** | 95FIC024 | FIC96024 | **95FIC024/PV** | ✅ FOUND |
| **MV SP** | - | - | **95FIC024/SP** | ✅ FOUND |
| **MV Output** | - | - | **95FIC024/OUT** | ✅ FOUND |
| **Tower Level** | - | LIC95017 | **95LIC017/PV** | ✅ FOUND |
| **Acid Temp** | 95TI038 | - | **95TI038/PV** | ✅ FOUND |

### 3.2 Control Architecture Confirmation

```
CONCENTRATION CONTROL:
  95DI023/PV (Density) ──► Controller ──► 95FIC024 (Water Flow)
                              │
  95TI038/PV (Temp) ──────────┘ (Compensation)

  NOTE: ~35 minute dead time - requires predictive control
```

---

## 4. OBJ-4: pH CONTROL

### 4.1 Tag Availability - ALL FOUND ✓

| Role | Client SOW | SCADA Tag | **Historian Tag** | Status |
|------|------------|-----------|------------------|--------|
| **CV (pH)** | 96AI002 | AIC96002 | **96AIC002/PV** | ✅ FOUND |
| **CV SP** | - | - | **96AIC002/SP** | ✅ FOUND |
| **CV Output** | - | - | **96AIC002/OUT** | ✅ FOUND |
| **NH3 Flow** | 96FIC002 | FIC96006 | **96FIC002/PV** | ✅ FOUND |
| **NH3 Flow SP** | - | - | **96FIC002/SP** | ✅ FOUND |
| **NH3 Flow Out** | - | - | **96FIC002/OUT** | ✅ FOUND |
| **Acid Feed** | 96FIC005 | FIC96005 | **96FIC005/PV** | ✅ FOUND |

### 4.2 Additional pH System Tags

| Tag | Description |
|-----|-------------|
| 96AIC006/PV | Secondary analyzer controller |
| 96AIC006/SP | Secondary analyzer setpoint |
| 96FIC005/OUT | Acid feed output |

### 4.3 Control Architecture Confirmation

```
CASCADE pH CONTROL:
  96AIC002/PV (pH) ──► pH Controller ──► 96FIC002 (NH3 Flow)
       │                                     │
  SP = 2.30 pH                              ▼
                                       NH3 Valve

FEEDFORWARD:
  96FIC005/PV (Acid Feed) ──► FF ──► 96FIC002/SP
```

---

## 5. AMBIENT CONDITIONS - CRITICAL FOR OBJ-1

### 5.1 Confirmed Ambient Tag

| Tag | Description | SCADA Value | Location |
|-----|-------------|-------------|----------|
| **95TI417/PV** | Ambient Temperature | 18.2°C | Compressor area |

### 5.2 Missing Tags (Not Found in Historian)

| Parameter | Expected Tag Pattern | Status | Mitigation |
|-----------|---------------------|--------|------------|
| **Relative Humidity** | RH*, HUMID* | ❌ NOT FOUND | Use weather API or install sensor |
| **Atmospheric Pressure** | BARO*, ATM* | ❌ NOT FOUND | Use weather API or install sensor |

### 5.3 Recommendation

For full OBJ-1 feedforward compensation, we need:
1. **Temperature**: ✅ Available (95TI417/PV)
2. **Humidity**: ❌ Consider weather station data from Sasolburg area
3. **Barometric Pressure**: ❌ Consider weather station data

Air density formula: ρ = (P × M) / (R × T × (1 + x × (M_w/M_a - 1)))

Where x = humidity ratio. Without RH and P_atm, we can only do partial compensation.

---

## 6. COMPLETE TAG INVENTORY

### 6.1 NAP2 Tags (189 total)

**Flow Tags:**
- 95FI001/PV, 95FI003A/B/C/PV, 95FI004A/B/C/PV
- 95FI012/PV, 95FI013/PV, 95FI015/PV, 95FI018/PV
- 95FI408/PVMT, 95FI409/PVMT, 95FI410/PVMT
- 95FIC024/PV/SP/OUT
- 95FFI005A/B/C/PV, 95FFIC008/PV/SP/OUT
- 95FY006/PV, 95FY007/PV

**Temperature Tags:**
- 95TI001-95TI090 range (multiple)
- 95TI016A/B/C/PV (Gauze temperatures)
- 95TI417/PV (Ambient)
- 95TI400A/B through 95TI413A/B (machinery temps)
- 95TI470A/B through 95TI479A/B (turbine temps)

**Pressure Tags:**
- 95PI002-95PI042 range
- 95PI003A/B/C/PV, 95PI004A/B/C/PV
- 95PI407A/B/C/PV, 95PI410-412/PV
- 95PY008/PV

**Level Tags:**
- 95LI001A/B/C/PV, 95LI003/PV, 95LI016/PV
- 95LIC001/PV/SP/OUT, 95LIC017/PV

**Analyzer Tags:**
- 95DI023/PV, 95DY023/PV
- 97AI08/PV

**Controller Tags:**
- 95HIC007/PV/SP, 95HIC008/PV/SP
- 95HIC403/PV, 95HIC404/PV
- 95FFIC008/PV/SP/OUT
- 95FIC024/PV/SP/OUT
- 95LIC001/PV/SP/OUT

**Vibration/Speed Tags:**
- 95SI470/PV, 95SI470/PVMT
- 95VI400-411 (X/Y vibration)
- 95VI470-471 (X/Y vibration)
- 95ZI400A/B/C, 95ZI401A/B/C, 95ZI470A/B/C

### 6.2 ANP2 Tags (63 total)

**pH/Analyzer Tags:**
- 96AIC002/PV/SP/OUT
- 96AIC006/PV/SP/OUT

**Flow Tags:**
- 96FIC002/PV/SP/OUT
- 96FIC005/PV/SP/OUT

---

## 7. DATA QUALITY NOTES

### 7.1 File Summary

| File | Date | Rows | Sampling |
|------|------|------|----------|
| pi_data_20251229_151817.parquet | 2025-12-29 | 178,560 | ~15 sec |
| pi_data_20251229_155201.parquet | 2025-12-29 | 172,800 | ~15 sec |
| pi_data_20251230_082720.parquet | 2025-12-30 | 178,560 | ~15 sec |
| pi_data_20251230_092335.parquet | 2025-12-30 | 172,800 | ~15 sec |

### 7.2 Data Coverage

- **Date Range:** Late December 2025 (need to verify full July-Nov 2025)
- **Sampling Rate:** ~15 second intervals (confirmed)
- **Data Quality:** To be assessed in Step 5

---

## 8. TAG NAMING CONVENTION

### 8.1 Historian Tag Format

```
[Area][Type][Number][Suffix]/[Attribute]

Examples:
95FFIC008/PV  = Area 95, Flow-Flow (Ratio) Controller 008, Process Value
95FFIC008/SP  = Area 95, Flow-Flow (Ratio) Controller 008, Setpoint
95FFIC008/OUT = Area 95, Flow-Flow (Ratio) Controller 008, Output
95TI016A/PV   = Area 95, Temperature Indicator 016A, Process Value
```

### 8.2 Common Attributes

| Attribute | Meaning |
|-----------|---------|
| /PV | Process Value (measurement) |
| /SP | Setpoint |
| /OUT | Controller Output |
| /PVMT | Process Value (alternate/metric) |
| /AO1/OUT | Analog Output 1 |

---

## 9. CONCLUSIONS

### 9.1 APC Feasibility - CONFIRMED ✓

| Objective | Tags Available | Control Loop Complete | Ready for APC |
|-----------|---------------|----------------------|---------------|
| **OBJ-1** | ✅ All found | ✅ HIC403, HIC404, FI003, TI417 | ✅ YES |
| **OBJ-2** | ✅ All found | ✅ FFIC008, TI016, FI003/004 | ✅ YES |
| **OBJ-3** | ✅ All found | ✅ DI023, FIC024, TI038 | ✅ YES |
| **OBJ-4** | ✅ All found | ✅ AIC002, FIC002, FIC005 | ✅ YES |

### 9.2 Gaps Identified

1. **Ambient RH and Barometric Pressure** - Not in historian
   - Impact: Partial feedforward only for OBJ-1
   - Mitigation: Weather API or new sensors

2. **Date Range Verification** - Need to confirm full 5-month coverage
   - Impact: Model identification may be limited
   - Action: Verify in Step 5 data quality analysis

### 9.3 Next Steps

1. **Step 5: Data Quality Assessment**
   - Load full date range
   - Check for missing data, outliers, stuck values
   - Validate process dynamics

2. **Step 3: APC Control Strategy Design**
   - Use confirmed tags for CV/MV/DV mapping
   - Design feedforward compensation for OBJ-1
   - Plan non-linear gain scheduling for OBJ-4

---

## DOCUMENT CONTROL

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-17 | Claude Code | Complete tag cross-reference from historian |

**Source Files:**
- Historian Data: `C:\Users\GideonCrous\Documents\Historian Data\`
- NAP2: 4 parquet files, 189 unique tags
- ANP2: 4 parquet files, 63 unique tags
