# NH3:Air Ratio and Turbine IGV Correlation Analysis Plan

**Date:** 2026-01-26  
**Status:** Planning Phase  
**Purpose:** Comprehensive analysis of NH3:Air ratio control, turbine IGV behavior, and environmental impacts on air flow

---

## ANALYSIS OBJECTIVES

### Primary Objectives

1. **NH3:Air Ratio Analysis** - Compare manual design specifications vs actual operating data
2. **Turbine IGV Correlation Study** - Analyze relationship between turbine vane position and incoming air volumetric flowrate
3. **Environmental Impact Assessment** - Quantify effects of ambient temperature and humidity on air flow and turbine performance
4. **Mass Flow Calculations** - Calculate actual mass flow from volumetric data and analyze relationships

---

## DATA SOURCES

### Historian Tags (Available in Parquet Files)

| Variable | Historian Tag | Description | Units | Notes |
|----------|---------------|-------------|-------|-------|
| **NH3 Flow (A)** | `95FI003A/PV` | Ammonia flow line A | Nm³/h | Design: ~15,650 Nm³/h |
| **NH3 Flow (B)** | `95FI003B/PV` | Ammonia flow line B | Nm³/h | Design: ~15,650 Nm³/h |
| **NH3 Flow (C)** | `95FI003C/PV` | Ammonia flow line C | Nm³/h | Design: ~15,650 Nm³/h |
| **Air Flow (A)** | `95FI004A/PV` | Air volumetric flow line A | Nm³/h | Design: ~138,880 Nm³/h |
| **Air Flow (B)** | `95FI004B/PV` | Air volumetric flow line B | Nm³/h | Design: ~138,880 Nm³/h |
| **Air Flow (C)** | `95FI004C/PV` | Air volumetric flow line C | Nm³/h | Design: ~138,880 Nm³/h |
| **Air Compressor IGV** | `95HIC403/PV` | Inlet guide vane position (air compressor) | % | Controls air throughput |
| **Tailgas Turbine IGV** | `95HIC404/PV` | Inlet guide vane position (tailgas turbine) | % | Controls plant pressure |
| **Ambient Temperature** | `95TI417/PV` | Atmospheric temperature | °C | Feedforward compensation input |
| **Air Suction Pressure** | `95PI002/PV` | Compressor inlet pressure | kPa | Atmospheric variations |
| **Air Discharge Pressure** | `95PI006/PV` | Compressor outlet pressure | kPa | Design: 401 kPaa |
| **Air Discharge Temp** | `95TI008/PV` | Air temperature after compression | °C | For density calculations |
| **Shaft Speed** | `95SI470/PV` | Common shaft speed | RPM | Couples all 4 machines |
| **Process Pressure** | `95PI007A/PV` | NO compressor discharge / Process pressure | kPa,g | Target: 945 kPa,g |

**Note:** No dedicated humidity sensor found in historian tags. May need to use ambient temperature correlation or request additional data.

### Manual References

| Document | Section | Key Information |
|----------|---------|-----------------|
| **Operating Manual** | Section 3.1, Page 26 | Design air flow: 203,445 kg/h <br> Design NH3 flow: 20,346 kg/h <br> Air compressor discharge: 401 kPaa |
| **Operating Manual** | Section 6.1, Page 129 | Ratio control valve FV95008 target: 60-80% position <br> Plant pressure adjustment via tailgas turbine IGV |
| **Design Ratios Analysis** | Full Document | Design NH3:O2 ratio = 0.476 (68% excess O2) <br> NH3 conversion efficiency = 95.05% <br> Stream composition data |
| **TAG_CROSS_REFERENCE.md** | Section 1.3 | Control architecture: Air IGV controls flow, pressure controlled independently |
| **OPERATING_MANUAL_ANALYSIS.md** | Section on Correlations | Air IGV vs Air Flow correlation: +0.925 <br> Air IGV vs Tailgas IGV correlation: -0.921 (opposite movement) <br> Ambient temp drives feedforward compensation |

---

## ANALYSIS PLAN - DETAILED STEPS

### STEP 1: NH3:Air Ratio Analysis

**Objective:** Compare design specifications with actual operating data and identify deviations

#### Step 1.1: Calculate Total Flow Rates
- **Method:** Sum redundant measurements for each stream
  ```
  Total_NH3_Flow = 95FI003A/PV + 95FI003B/PV + 95FI003C/PV
  Total_Air_Flow = 95FI004A/PV + 95FI004B/PV + 95FI004C/PV
  ```
- **Expected Values:**
  - NH3: ~46,950 Nm³/h (3 × 15,650)
  - Air: ~416,640 Nm³/h (3 × 138,880)
- **Output:** Time series of total flows

#### Step 1.2: Calculate Volumetric Ratio
- **Method:** 
  ```
  Volumetric_Ratio = Total_NH3_Flow / Total_Air_Flow
  ```
- **Design Target:** From design ratios analysis, NH3 = 9.1 vol% in mix
  ```
  Design_Ratio = 9.1 / (100 - 9.1) = 0.100 (NH3:Air volumetric ratio)
  ```
- **Output:** Time series of actual ratios vs design target

#### Step 1.3: Calculate Molar NH3:O2 Ratio
- **Method:** Assuming air composition (21% O2, 79% N2):
  ```
  O2_Flow = Total_Air_Flow × 0.21
  Molar_Ratio = Total_NH3_Flow / O2_Flow
  ```
- **Design Target:** 0.476 (from design ratios analysis)
- **Stoichiometric Ratio:** 0.80 (4NH3 : 5O2)
- **Output:** Actual molar ratio vs design and stoichiometric targets

#### Step 1.4: Identify Operating Regimes
- **Method:** Cluster analysis or statistical binning
  - Low load (<80% design)
  - Normal load (80-100% design)
  - High load (>100% design)
- **Cross-reference:** Compare with `NAP2_Plant_Load.NAP2_Load_Output` tag
- **Output:** Ratio statistics by operating regime

#### Step 1.5: Analyze Ratio Control Valve Performance
- **Tags:** `95FFIC008/PV` (ratio controller PV), `95FFIC008/SP` (setpoint), `95FFIC008/OUT` (controller output)
- **Method:** 
  - Calculate ratio control error: `Error = PV - SP`
  - Assess controller performance (response time, overshoot, settling)
- **Reference:** Operating Manual states FV95008 should operate at 60-80% position
- **Output:** Control performance metrics and valve position distribution

---

### STEP 2: Turbine IGV and Air Flow Correlation Study

**Objective:** Quantify relationship between turbine vane positions and incoming air flow

#### Step 2.1: Air Compressor IGV vs Volumetric Air Flow
- **Tags:** `95HIC403/PV` vs `Total_Air_Flow`
- **Method:** 
  - Scatter plot with linear regression
  - Calculate Pearson correlation coefficient
  - Identify non-linearities at extreme IGV positions
- **Expected Result:** Strong positive correlation (reference: +0.925 from prior analysis)
- **Output:** Regression equation, R² value, residual analysis

#### Step 2.2: Tailgas Turbine IGV vs Air Flow (Indirect Effect)
- **Tags:** `95HIC404/PV` vs `Total_Air_Flow`
- **Method:**
  - Analyze correlation (expected to be weak/indirect)
  - Cross-lag correlation analysis (time delays)
- **Process Context:** Tailgas IGV controls plant pressure, not directly air flow
- **Expected Result:** Weak direct correlation, but coupled through common shaft
- **Output:** Correlation coefficient and lag analysis

#### Step 2.3: IGV Interaction Analysis
- **Tags:** `95HIC403/PV` vs `95HIC404/PV`
- **Method:**
  - 2D scatter plot to visualize coordinated movement
  - Calculate correlation (expected: -0.921 from prior analysis)
  - Identify operating constraints (mutual exclusion zones)
- **Process Context:** IGVs move in opposite directions due to pressure control coupling
- **Reference:** Operating Manual Analysis Section on Process Coupling
- **Output:** Correlation plot with operating envelope boundaries

#### Step 2.4: Shaft Speed Relationship
- **Tags:** `95SI470/PV` (shaft speed) vs `95HIC403/PV`, `95HIC404/PV`, `Total_Air_Flow`
- **Method:**
  - Analyze speed variations with IGV position changes
  - Confirm common shaft coupling mechanism
- **Process Context:** All 4 machines (steam turbine, air compressor, NO compressor, tailgas turbine) on common shaft
- **Reference:** Operating Manual Section 3.1, Page 26 - Common shaft drive train
- **Output:** Speed vs flow relationship, confirm mechanical coupling

---

### STEP 3: Environmental Impact Analysis

**Objective:** Quantify effects of ambient conditions on air flow and turbine performance

#### Step 3.1: Ambient Temperature Effects on Volumetric Flow
- **Tags:** `95TI417/PV` (ambient temperature) vs `Total_Air_Flow`
- **Method:**
  - Group data by temperature bins (5°C intervals)
  - Calculate average volumetric flow for constant IGV position across temperature ranges
  - Analyze temperature correction factor
- **Physics:** For constant mass flow, volumetric flow increases with temperature
  ```
  Q_actual = Q_normal × (T_actual / T_normal)
  ```
  where Q = volumetric flow, T = absolute temperature
- **Expected Result:** Positive correlation (higher temp → higher volumetric flow for same mass flow)
- **Reference:** Operating Manual Section 6.1 mentions ambient temperature affects operation
- **Output:** Temperature sensitivity coefficient (Nm³/h per °C)

#### Step 3.2: Ambient Temperature Effects on Turbine IGV
- **Tags:** `95TI417/PV` vs `95HIC403/PV`
- **Method:**
  - Analyze feedforward compensation behavior
  - Identify if APC system adjusts IGV based on ambient temperature
- **Control Context:** TAG_CROSS_REFERENCE.md shows feedforward path:
  ```
  95TI417/PV (Ambient T) → APC Controller → 95HIC403/PV (Air IGV)
  ```
- **Expected Result:** IGV opens more in hot weather to maintain constant mass flow
- **Output:** Feedforward gain (% IGV change per °C)

#### Step 3.3: Pressure Effects on Air Flow
- **Tags:** `95PI002/PV` (suction pressure) vs `Total_Air_Flow` and `95HIC403/PV`
- **Method:**
  - Analyze variations in atmospheric pressure (weather changes)
  - Calculate impact on volumetric flow measurement
- **Physics:** Lower atmospheric pressure → lower air density → higher volumetric flow for same mass flow
- **Output:** Pressure correction factor analysis

#### Step 3.4: Humidity Impact (Indirect Analysis)
- **Available Data:** No direct humidity measurement in historian
- **Method:** 
  - Use ambient temperature as proxy (assume typical humidity-temperature correlation)
  - Analyze unexplained variance in air flow after temperature correction
  - Calculate residuals: `Residual = Actual_Flow - (Predicted_Flow_from_Temp_Model)`
- **Alternative:** Request weather station data for humidity if available
- **Physics:** Humid air is less dense → affects mass flow calculations
- **Output:** Qualitative assessment and recommendation for humidity measurement

---

### STEP 4: Mass Flow Calculations and Analysis

**Objective:** Calculate actual mass flow rates and analyze relationships with volumetric measurements

#### Step 4.1: Air Mass Flow Calculation
- **Tags Required:** 
  - `95FI004A/PV`, `95FI004B/PV`, `95FI004C/PV` (volumetric flows at normal conditions)
  - `95TI417/PV` (ambient temperature)
  - `95PI002/PV` (suction pressure)
  - `95TI008/PV` (discharge temperature) - if needed for verification
- **Method:** 
  - Convert normal volumetric flow (Nm³/h) to mass flow (kg/h)
  ```
  Air density at normal conditions (0°C, 101.325 kPa) = 1.293 kg/Nm³
  Mass_Flow = Volumetric_Flow × ρ_normal × (P_actual/P_normal) × (T_normal/T_actual)
  ```
  - For Nm³/h (already at normal conditions), simplify to:
  ```
  Mass_Flow = Volumetric_Flow × 1.293 kg/Nm³
  ```
- **Design Target:** 203,445 kg/h (from Operating Manual)
- **Output:** Time series of mass flow rates

#### Step 4.2: NH3 Mass Flow Calculation
- **Tags Required:** `95FI003A/PV`, `95FI003B/PV`, `95FI003C/PV`
- **Method:**
  ```
  NH3 density at normal conditions = 0.771 kg/Nm³
  NH3_Mass_Flow = Total_NH3_Flow × 0.771 kg/Nm³
  ```
- **Design Target:** 20,346 kg/h
- **Output:** Time series of NH3 mass flow

#### Step 4.3: Mass Ratio Analysis
- **Method:**
  ```
  Mass_Ratio = NH3_Mass_Flow / Air_Mass_Flow
  ```
- **Design Target:** 20,346 / 203,445 = 0.100 (10.0% by mass)
- **Output:** Actual mass ratio vs design target

#### Step 4.4: Turbine IGV vs Mass Flow Relationship
- **Tags:** `95HIC403/PV` vs `Air_Mass_Flow`
- **Method:**
  - Linear regression analysis
  - Compare with volumetric flow relationship
  - Assess if IGV control is based on mass flow or volumetric flow
- **Expected Result:** Mass flow control is the actual objective (constant mass ratio NH3:Air)
- **Output:** Regression analysis, control strategy confirmation

#### Step 4.5: Ambient Correction Validation
- **Method:**
  - Compare mass flow variation vs volumetric flow variation across ambient conditions
  - Validate if feedforward compensation maintains constant mass flow
- **Expected Result:** Mass flow should be more stable than volumetric flow across temperature changes
- **Reference:** APC feedforward compensation design from TAG_CROSS_REFERENCE.md
- **Output:** Statistical comparison (CV% for mass flow vs volumetric flow)

---

## ANALYSIS METHODS AND TOOLS

### Statistical Methods

1. **Descriptive Statistics**
   - Mean, median, standard deviation, min/max for all variables
   - Coefficient of variation (CV%) to assess control stability
   - Percentile analysis (5th, 25th, 75th, 95th)

2. **Correlation Analysis**
   - Pearson correlation coefficients (linear relationships)
   - Spearman rank correlation (non-linear monotonic relationships)
   - Cross-correlation with time lags (dynamic responses)

3. **Regression Analysis**
   - Linear regression (primary method)
   - Polynomial regression (if non-linearities detected)
   - Multiple linear regression (environmental corrections)

4. **Time Series Analysis**
   - Trend analysis (long-term drift)
   - Seasonal/diurnal patterns (day/night, summer/winter)
   - Step response analysis (IGV changes → flow response)

### Software Tools

- **Python** with libraries:
  - `pandas` - data manipulation
  - `numpy` - numerical calculations
  - `matplotlib` / `seaborn` - visualization
  - `scipy.stats` - statistical analysis
  - `sklearn` - regression modeling

### Visualization Outputs

1. **Time Series Plots**
   - NH3 and air flows over time with design targets
   - IGV positions over time
   - Ambient conditions overlay

2. **Scatter Plots with Regression**
   - IGV vs volumetric flow
   - IGV vs mass flow
   - Ambient temperature vs flow
   - Air IGV vs Tailgas IGV

3. **Distribution Plots**
   - Histogram of NH3:Air ratios
   - Box plots by operating regime
   - Ratio control valve position distribution

4. **Correlation Matrix Heatmap**
   - All key variables cross-correlated
   - Color-coded by correlation strength

---

## EXPECTED OUTPUTS AND DELIVERABLES

### Quantitative Results

1. **NH3:Air Ratio Statistics**
   - Mean actual ratio vs design target (%)
   - Standard deviation (control tightness)
   - Operating range (min-max)
   - Percentage time within ±5% of target

2. **Turbine IGV Correlations**
   - Air Compressor IGV vs Air Flow: R² value, slope, intercept
   - Tailgas IGV vs Air IGV: correlation coefficient
   - IGV operating ranges and constraints

3. **Environmental Sensitivities**
   - Temperature coefficient: Nm³/h per °C
   - Feedforward gain: % IGV per °C
   - Pressure correction factor

4. **Mass Flow Performance**
   - Actual vs design mass flows (kg/h)
   - Mass flow control stability (CV%)
   - Mass ratio accuracy vs target

### Analytical Insights

1. **Control Performance Assessment**
   - Is the NH3:Air ratio consistently maintained?
   - How well does feedforward compensation work?
   - Are there systematic biases or drift?

2. **Process Understanding**
   - Confirm IGV control mechanisms
   - Validate common shaft coupling effects
   - Identify any unexpected interactions

3. **Operational Recommendations**
   - Optimal operating ranges for IGVs
   - Environmental compensation improvements
   - Ratio control tuning suggestions

### Documentation

1. **Analysis Report (Markdown)**
   - Methods section with equations
   - Results with tables and figures
   - Conclusions and recommendations

2. **Data Quality Report**
   - Missing data assessment
   - Outlier identification
   - Measurement validation

3. **Code Documentation**
   - Python scripts with comments
   - Reproducible analysis workflow

---

## DATA QUALITY CONSIDERATIONS

### Pre-Processing Steps

1. **Data Validation**
   - Check for missing values (NaN, NULL)
   - Identify sensor failures (stuck values, flatlines)
   - Remove outliers (>3σ from mean, or physical impossibilities)

2. **Timestamp Alignment**
   - Ensure all tags have synchronized timestamps
   - Resample to common time interval if needed
   - Handle daylight saving time changes

3. **Unit Verification**
   - Confirm all flows are in Nm³/h (normal conditions: 0°C, 101.325 kPa)
   - Verify temperature in °C
   - Verify pressure in kPa or kPa,g (check gauge vs absolute)

### Known Data Limitations

1. **No Humidity Sensor**
   - Cannot directly calculate humid air density
   - May need external weather data
   - Recommend addition of humidity measurement

2. **Redundant Measurements**
   - Three parallel flow measurements (A, B, C) for both NH3 and air
   - Need to verify if all three are valid or if one is spare
   - Check for flow splitting vs redundant measurement

---

## TIMELINE AND MILESTONES

| Phase | Task | Estimated Duration | Deliverable |
|-------|------|-------------------|-------------|
| **Phase 1** | Data extraction and cleaning | 1 day | Clean dataset (CSV/Parquet) |
| **Phase 2** | NH3:Air ratio analysis (Step 1) | 1-2 days | Ratio analysis report section |
| **Phase 3** | Turbine IGV correlation study (Step 2) | 1-2 days | IGV analysis report section |
| **Phase 4** | Environmental impact analysis (Step 3) | 2 days | Environmental sensitivity report section |
| **Phase 5** | Mass flow calculations (Step 4) | 1-2 days | Mass flow analysis report section |
| **Phase 6** | Integration and reporting | 1 day | Complete analysis document |
| **Total** | | **7-10 days** | Full analysis package |

---

## REFERENCES

### Internal Documents

1. **Operating Manual Section 3.1** - Process Description (Pages 26-28)
   - Air compressor design: 401 kPaa discharge, 203,445 kg/h
   - NH3 evaporator: 550 kPaa
   - Common shaft drive train description
   - Tailgas turbine: 920 kPaa inlet, 437°C

2. **Operating Manual Section 6.1** - Operation (Pages 129-130)
   - Plant pressure adjustment via tailgas turbine IGV
   - Ratio control valve FV95008 target: 60-80% position
   - Tray 20 concentration varies with ambient temperature and plant pressure

3. **Design Ratios Analysis** (design_ratios_analysis.md)
   - NH3:O2 molar ratio: 0.476 (design)
   - Stoichiometric ratio: 0.80 (4NH3 : 5O2)
   - Excess O2: 68%
   - NH3 conversion efficiency: 95.05%
   - Design stream compositions (PFD 01-02, 01-03)

4. **TAG_CROSS_REFERENCE.md** - Section 1.3
   - Control architecture diagram
   - Feedforward compensation: Ambient T → APC → Air IGV
   - Pressure control: 95PI007A → DCS PID → Tailgas IGV

5. **OPERATING_MANUAL_ANALYSIS.md** - Correlation Data
   - Air IGV vs Air Flow: +0.925 correlation
   - Air IGV vs Tailgas IGV: -0.921 correlation (opposite movement)
   - Process pressure vs Air Flow: +0.985 correlation
   - Historical operating statistics

### External References

1. **Perry's Chemical Engineers' Handbook** - Fluid density data
   - Air density at normal conditions: 1.293 kg/Nm³
   - NH3 gas density: 0.771 kg/Nm³

2. **NIST Chemistry WebBook** - Gas properties for validation

3. **Nitric Acid Plant Design Standards** - Industry best practices for NH3:Air ratios

---

## NOTES AND ASSUMPTIONS

1. **Normal Conditions Definition**
   - Assuming Nm³ refers to 0°C, 101.325 kPa (ISO 13443 standard)
   - Verify with plant documentation if different reference conditions used

2. **Air Composition**
   - Assuming standard dry air: 21% O2, 79% N2 (by volume)
   - Neglecting trace gases (Ar, CO2, etc.) for ratio calculations

3. **Humidity Impact**
   - Without humidity data, assuming dry air basis
   - This may introduce small errors in mass flow calculations (typically <2%)

4. **Instrument Accuracy**
   - Flow meters: typically ±1-2% of full scale
   - Temperature: typically ±0.5°C
   - Pressure: typically ±0.25% of span

5. **Steady-State vs Dynamic Analysis**
   - Primary focus on steady-state correlations
   - Dynamic response analysis (step tests) requires separate transient data identification

---

## REVISION HISTORY

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-01-26 | 1.0 | Initial analysis plan created | Analysis Team |

---

**Status:** Ready for data extraction and analysis execution  
**Next Action:** Extract historian data for specified tags and begin Step 1 (NH3:Air Ratio Analysis)
