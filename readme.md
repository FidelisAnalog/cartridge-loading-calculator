# Cartridge Loading Calculator - Usage Guide

## Overview
This script calculates and plots the frequency response of a phono cartridge + preamp loading system. It shows both the audible range (20 Hz - 20 kHz) and extended ultrasonic range (20 Hz - 50 kHz).

## Running the Script

### Method 1: Interactive Mode
Simply run without arguments and follow the prompts:

```bash
python cartridge_loading.py
```

You'll be prompted for:
- Cartridge Inductance (mH)
- Cartridge DC Resistance (Ω)
- Preamp Load Resistance (kΩ)
- Total Capacitance - cable + preamp (pF)
- Frequency scale (log or linear)

Press Enter to accept default values shown in brackets.

### Method 2: Command-Line Mode
Provide all parameters at once:

```bash
python cartridge_loading.py L_cart R_cart R_load C_total [scale]
```

**Arguments:**
- `L_cart`   : Cartridge inductance in mH
- `R_cart`   : Cartridge DC resistance in Ω
- `R_load`   : Preamp load resistance in kΩ
- `C_total`  : Total capacitance (cable + preamp) in pF
- `scale`    : 'log' or 'linear' (optional, default: log)

**Examples:**

Typical MM cartridge with standard loading:
```bash
python cartridge_loading.py 500 600 47 200 log
```

High-output MM with low capacitance:
```bash
python cartridge_loading.py 400 800 47 100 log
```

High capacitance loading (long cable):
```bash
python cartridge_loading.py 500 600 47 400 linear
```

Low impedance MC cartridge (different model - just for illustration):
```bash
python cartridge_loading.py 0.5 10 100 200 log
```

## Output

The script produces:
1. **A dual-panel plot** showing:
   - Top: Audible range (20 Hz - 20 kHz)
   - Bottom: Extended range (20 Hz - 50 kHz) showing ultrasonic resonance
   
2. **Detailed analysis** including:
   - Ideal LC resonance frequency
   - Actual peak frequency and magnitude
   - Q factor (damping)
   - Interpretation and recommendations

## Typical Cartridge Values

### Moving Magnet (MM) Cartridges
- **Inductance**: 300-600 mH (typical: 500 mH)
- **Resistance**: 400-1000 Ω (typical: 600 Ω)
- **Load**: 47 kΩ standard
- **Capacitance**: 100-300 pF typical (cable + preamp)

### Moving Coil (MC) Cartridges
- **Inductance**: 0.1-10 mH (much lower than MM)
- **Resistance**: 2-100 Ω (much lower than MM)
- **Load**: Often 100 Ω - 47 kΩ depending on type
- **Capacitance**: Less critical due to low inductance

## Reading the Results

### Q Factor
- **Q > 1.5**: Under-damped, expect visible resonant peak
- **Q ≈ 1.0**: Critically damped, minimal peak
- **Q < 0.7**: Over-damped, very smooth rolloff

### Peak Magnitude
- **< 1 dB**: Well damped, minimal effect
- **1-3 dB**: Typical, usually acceptable
- **3-6 dB**: Noticeable treble boost, may sound bright
- **> 6 dB**: Significant peak, likely too bright

### Recommendations
- If peak is too high (>3 dB), reduce capacitance
- If peak is in audible range (<15 kHz), it's more noticeable
- If peak is ultrasonic (>20 kHz), effect is mainly on transient response

## Log vs Linear Scale

**Logarithmic (recommended for most uses):**
- Standard for audio analysis
- Shows full spectrum proportionally
- Easier to see bass, midrange, and treble equally

**Linear:**
- Same as AlignmentProtractor.com uses
- Emphasizes treble region
- Makes high-frequency problems very visible
- 1 kHz appears at 5% of plot width

## Tips

1. **Finding your cartridge specs**: Check manufacturer website or manual
2. **Measuring capacitance**: Cable typically 30-50 pF/foot, preamp usually 100-200 pF
3. **Experimentation**: Try different capacitances to see the effect on response
4. **Comparison**: Run multiple scenarios and compare the plots

## Example Session

```bash
$ python cartridge_loading.py

============================================================
CARTRIDGE LOADING CALCULATOR
============================================================

Enter cartridge and loading parameters:
(Press Enter for defaults shown in brackets)

Cartridge Inductance [500] mH: 450
Cartridge DC Resistance [600] Ω: 700
Preamp Load Resistance [47] kΩ: 
Total Capacitance (cable + preamp) [200] pF: 150
Frequency scale (log/linear) [log]: 

Generating cartridge loading plot...

✓ Plot saved to: cartridge_loading_response.png

============================================================
CARTRIDGE LOADING ANALYSIS
============================================================
[... detailed results ...]
```

## Troubleshooting

**"Invalid input" error**: Make sure to enter numeric values only
**Plot doesn't show peak**: Your loading is well-damped (this is usually good!)
**Peak is huge**: Reduce capacitance - try shorter cable or different preamp
