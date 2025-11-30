"""
Cartridge Loading Calculator
Models the frequency response of a phono cartridge + preamp system

The circuit model:
- Cartridge: inductance L, DC resistance R_cart
- Preamp: load resistance R_load (parallel), capacitance C (parallel)
- Cable capacitance is added to C

This forms a voltage divider where:
- Input voltage comes from the cartridge (modeled as voltage source + L + R_cart in series)
- Output voltage is taken across the parallel combination of R_load and C
"""

import os
import numpy as np
import matplotlib.pyplot as plt

def cartridge_frequency_response(
    L_cart_mH,      # Cartridge inductance in millihenries
    R_cart_ohms,    # Cartridge DC resistance in ohms
    R_load_kohms,   # Preamp load resistance in kilohms
    C_total_pF,     # Total capacitance (preamp + cable) in picofarads
    freq_range=(20, 20000),  # Frequency range in Hz
    num_points=1000
):
    """
    Calculate the frequency response of the cartridge-preamp system.
    
    The transfer function H(jω) is derived from the voltage divider:
    
    Z_load = R_load || (1/jωC)  [parallel combination]
    
    H(jω) = V_out / V_in = Z_load / (Z_cart + Z_load)
    
    where:
    Z_cart = R_cart + jωL
    Z_load = R_load / (1 + jωRC)
    
    Returns:
        frequencies: array of frequencies in Hz
        magnitude_dB: frequency response in dB (voltage ratio, 20*log10|H|)
        phase_deg: phase response in degrees
    """
    
    # Convert units to standard SI
    L = L_cart_mH * 1e-3  # henries
    R_cart = R_cart_ohms
    R_load = R_load_kohms * 1e3  # ohms
    C = C_total_pF * 1e-12  # farads
    
    # Generate frequency array (logarithmic spacing for audio analysis)
    frequencies = np.logspace(np.log10(freq_range[0]), np.log10(freq_range[1]), num_points)
    omega = 2 * np.pi * frequencies
    
    # Calculate impedances as complex numbers
    # Cartridge impedance: Z_cart = R_cart + jωL
    Z_cart = R_cart + 1j * omega * L
    
    # Load impedance: Z_load = R_load || (1/jωC)
    # Parallel combination: 1/Z = 1/R + jωC
    # Therefore: Z = R / (1 + jωRC)
    Z_cap = 1.0 / (1j * omega * C)  # Capacitor impedance
    Z_load = (R_load * Z_cap) / (R_load + Z_cap)  # Parallel combination
    
    # Transfer function: H(jω) = Z_load / (Z_cart + Z_load)
    H = Z_load / (Z_cart + Z_load)
    
    # Convert to magnitude (dB) and phase (degrees)
    magnitude_dB = 20 * np.log10(np.abs(H))
    phase_deg = np.angle(H) * 180 / np.pi
    
    # Calculate resonant frequency (approximate)
    # For series RLC: f_res ≈ 1 / (2π√(LC))
    # But damping from resistors shifts this
    f_res_ideal = 1 / (2 * np.pi * np.sqrt(L * C))
    
    # Calculate Q factor (quality factor - indicates how sharp/damped the resonance is)
    # For this circuit: Q ≈ √(L/C) / (R_cart + R_load)
    # Lower Q = more damping = lower peak
    Z0 = np.sqrt(L / C)  # Characteristic impedance
    R_total = R_cart + R_load
    Q = Z0 / R_total
    
    return frequencies, magnitude_dB, phase_deg, f_res_ideal, Q


def plot_cartridge_response(L_cart, R_cart, R_load, C_total, 
                           use_log_scale=True, output_file='cartridge_loading_response.png',
                           output_dir='.', show_phase=True):
    """
    Plot the frequency response with two subplots using dual y-axes:
    - Top: Full audible range (20 Hz - 20 kHz) - magnitude on left, phase on right
    - Bottom: Extended ultrasonic range (20 Hz - 50 kHz) - magnitude on left, phase on right
    """
    
    # Calculate responses for both ranges
    freq_audible, mag_audible, phase_audible, f_res, Q = cartridge_frequency_response(
        L_cart, R_cart, R_load, C_total,
        freq_range=(20, 20000), num_points=2000
    )
    
    freq_extended, mag_extended, phase_extended, _, _ = cartridge_frequency_response(
        L_cart, R_cart, R_load, C_total,
        freq_range=(20, 50000), num_points=3000
    )
    
    # Create figure
    fig, (ax1, ax3) = plt.subplots(2, 1, figsize=(14, 10))
    
    # ============================================================
    # Plot 1: Audible range (20 Hz - 20 kHz)
    # ============================================================
    # Calculate peak values first
    peak_idx = np.argmax(mag_audible)
    peak_freq = freq_audible[peak_idx]
    peak_mag = mag_audible[peak_idx]
    
    # Left y-axis: Magnitude
    line1 = ax1.plot(freq_audible, mag_audible, 'b-', linewidth=2.5, 
             label=f'Magnitude (Peak: {peak_freq:.0f}Hz @ {peak_mag:.2f}dB, Q={Q:.2f})')
    
    # Mark the resonant frequency
    ax1.plot(peak_freq, peak_mag, 'bo', markersize=8)
    
    ax1.set_xlabel('Frequency (Hz)', fontsize=11)
    ax1.set_ylabel('Magnitude (dBV)', fontsize=11, color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.set_title(f'Frequency Response - Audible Range (20 Hz - 20 kHz)\n' + 
                  f'{"Logarithmic" if use_log_scale else "Linear"} frequency scale', fontsize=12, fontweight='bold')
    
    if use_log_scale:
        ax1.set_xscale('log')
        ax1.set_xlim(20, 20000)
    else:
        ax1.set_xlim(20, 20000)
    
    ax1.grid(True, alpha=0.3, which='both' if use_log_scale else 'major')
    
    # Add y-axis reference lines for magnitude
    ax1.axhline(y=0, color='b', linestyle='--', alpha=0.3, linewidth=0.8)
    ax1.axhline(y=3, color='b', linestyle=':', alpha=0.2, linewidth=0.8)
    ax1.axhline(y=-3, color='b', linestyle=':', alpha=0.2, linewidth=0.8)
    
    # Right y-axis: Phase (if enabled)
    if show_phase:
        ax1_phase = ax1.twinx()
        line2 = ax1_phase.plot(freq_audible, phase_audible, 'g-', linewidth=2, alpha=0.7,
                               label=f'Phase (@ peak: {phase_audible[peak_idx]:.1f}°)')
        
        # Mark phase at peak frequency
        phase_at_peak = phase_audible[peak_idx]
        ax1_phase.plot(peak_freq, phase_at_peak, 'go', markersize=8)
        
        ax1_phase.set_ylabel('Phase (degrees)', fontsize=11, color='g')
        ax1_phase.tick_params(axis='y', labelcolor='g')
        
        # Add reference lines for phase
        ax1_phase.axhline(y=0, color='g', linestyle='--', alpha=0.2, linewidth=0.8)
        ax1_phase.axhline(y=-90, color='g', linestyle=':', alpha=0.3, linewidth=1)
        
        # Combine legends
        lines = line1 + line2
        labs = [l.get_label() for l in lines]
        ax1.legend(lines, labs, loc='lower left', fontsize=9)
    else:
        ax1.legend(loc='lower left', fontsize=9)
    
    # ============================================================
    # Plot 2: Extended ultrasonic range (20 Hz - 50 kHz)
    # ============================================================
    # Calculate peak values first
    peak_idx_ext = np.argmax(mag_extended)
    peak_freq_ext = freq_extended[peak_idx_ext]
    peak_mag_ext = mag_extended[peak_idx_ext]
    
    # Left y-axis: Magnitude
    line3 = ax3.plot(freq_extended, mag_extended, 'b-', linewidth=2.5, 
                     label=f'Magnitude (Peak: {peak_freq_ext:.0f}Hz @ {peak_mag_ext:.2f}dB, Ideal LC: {f_res:.0f}Hz)')
    
    # Mark the resonant frequency
    ax3.plot(peak_freq_ext, peak_mag_ext, 'bo', markersize=8)
    
    # Show the theoretical LC resonance frequency
    ax3.axvline(x=f_res, color='orange', linestyle=':', alpha=0.6, linewidth=2.5,
                label=f'Ideal LC: {f_res:.0f}Hz')
    
    ax3.set_xlabel('Frequency (Hz)', fontsize=11)
    ax3.set_ylabel('Magnitude (dBV)', fontsize=11, color='b')
    ax3.tick_params(axis='y', labelcolor='b')
    ax3.set_title(f'Frequency Response - Extended Range (20 Hz - 50 kHz)', fontsize=12, fontweight='bold')
    
    if use_log_scale:
        ax3.set_xscale('log')
        ax3.set_xlim(20, 50000)
    else:
        ax3.set_xlim(20, 50000)
    
    ax3.grid(True, alpha=0.3, which='both' if use_log_scale else 'major')
    
    # Add y-axis reference lines for magnitude
    ax3.axhline(y=0, color='b', linestyle='--', alpha=0.3, linewidth=0.8)
    ax3.axhline(y=3, color='b', linestyle=':', alpha=0.2, linewidth=0.8)
    ax3.axhline(y=-3, color='b', linestyle=':', alpha=0.2, linewidth=0.8)
    
    # Right y-axis: Phase (if enabled)
    if show_phase:
        ax3_phase = ax3.twinx()
        
        # Calculate phase at peak and ideal LC
        phase_at_peak_ext = phase_extended[peak_idx_ext]
        idx_ideal = np.argmin(np.abs(freq_extended - f_res))
        phase_at_ideal = phase_extended[idx_ideal]
        
        line4 = ax3_phase.plot(freq_extended, phase_extended, 'g-', linewidth=2, alpha=0.7,
                               label=f'Phase (@ peak: {phase_at_peak_ext:.1f}°, @ ideal LC: {phase_at_ideal:.1f}°)')
        
        # Mark phase at peak frequency
        ax3_phase.plot(peak_freq_ext, phase_at_peak_ext, 'go', markersize=8)
        
        # Mark the ideal LC resonance line on phase axis too
        ax3_phase.axvline(x=f_res, color='orange', linestyle=':', alpha=0.3, linewidth=1.5)
        
        ax3_phase.set_ylabel('Phase (degrees)', fontsize=11, color='g')
        ax3_phase.tick_params(axis='y', labelcolor='g')
        
        # Add reference lines for phase
        ax3_phase.axhline(y=0, color='g', linestyle='--', alpha=0.2, linewidth=0.8)
        ax3_phase.axhline(y=-90, color='g', linestyle=':', alpha=0.3, linewidth=1)
        
        # Combine legends
        lines = line3 + line4
        labs = [l.get_label() for l in lines]
        ax3.legend(lines, labs, loc='lower left', fontsize=9)
    else:
        ax3.legend(loc='lower left', fontsize=9)
    
    plt.tight_layout()
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_file)
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✓ Plot saved to: {output_path}")
    
    # Print diagnostic information
    print("\n" + "="*60)
    print("CARTRIDGE LOADING ANALYSIS")
    print("="*60)
    print(f"\nCartridge Parameters:")
    print(f"  Inductance:      {L_cart} mH")
    print(f"  DC Resistance:   {R_cart} Ω")
    print(f"\nLoad Parameters:")
    print(f"  Load Resistance: {R_load} kΩ")
    print(f"  Total Capacitance: {C_total} pF")
    print(f"\nCalculated Results:")
    print(f"  Ideal LC Resonance:  {f_res:.1f} Hz")
    print(f"  Actual Peak Freq:    {peak_freq:.1f} Hz")
    print(f"  Peak Magnitude:      {peak_mag:.2f} dB")
    print(f"  Q Factor:            {Q:.3f}")
    print(f"  Damping:             {'Under-damped (resonant peak visible)' if Q > 1 else 'Critically/Over-damped (minimal peak)'}")
    
    # Interpret the results
    print(f"\nInterpretation:")
    if peak_mag > 3.0:
        print(f"  ⚠ Significant treble boost of {peak_mag:.1f}dB at {peak_freq:.0f}Hz")
        print(f"    This may sound bright or harsh. Consider reducing capacitance.")
    elif peak_mag > 1.0:
        print(f"  ℹ Moderate treble lift of {peak_mag:.1f}dB at {peak_freq:.0f}Hz")
        print(f"    This is typical and usually not problematic.")
    else:
        print(f"  ✓ Well-damped response with minimal peak ({peak_mag:.1f}dB)")
        print(f"    Good loading for this cartridge.")
    print("="*60)


if __name__ == "__main__":
    import sys
    
    # Check if running interactively or with command-line arguments
    if len(sys.argv) > 1:
        # Command-line mode
        try:
            L_cart = float(sys.argv[1])
            R_cart = float(sys.argv[2])
            R_load = float(sys.argv[3])
            C_total = float(sys.argv[4])
            use_log = sys.argv[5].lower() in ['log', 'logarithmic', 'true', '1'] if len(sys.argv) > 5 else True
            show_phase = sys.argv[6].lower() in ['phase', 'true', '1', 'yes'] if len(sys.argv) > 6 else True
            
            print(f"\nGenerating cartridge loading plot...")
            plot_cartridge_response(L_cart, R_cart, R_load, C_total, use_log, show_phase=show_phase)
            
        except (IndexError, ValueError) as e:
            print("\nUsage: python cartridge_loading.py L_cart R_cart R_load C_total [scale] [phase]")
            print("\nArguments:")
            print("  L_cart   : Cartridge inductance in mH")
            print("  R_cart   : Cartridge DC resistance in Ω")
            print("  R_load   : Preamp load resistance in kΩ")
            print("  C_total  : Total capacitance (cable + preamp) in pF")
            print("  scale    : 'log' or 'linear' (optional, default: log)")
            print("  phase    : 'yes' or 'no' to show phase plots (optional, default: yes)")
            print("\nExample:")
            print("  python cartridge_loading.py 500 600 47 200 log yes")
            sys.exit(1)
    else:
        # Interactive mode
        print("\n" + "="*60)
        print("CARTRIDGE LOADING CALCULATOR")
        print("="*60)
        print("\nEnter cartridge and loading parameters:")
        print("(Press Enter for defaults shown in brackets)\n")
        
        try:
            L_cart_input = input("Cartridge Inductance [500] mH: ").strip()
            L_cart = float(L_cart_input) if L_cart_input else 500.0
            
            R_cart_input = input("Cartridge DC Resistance [600] Ω: ").strip()
            R_cart = float(R_cart_input) if R_cart_input else 600.0
            
            R_load_input = input("Preamp Load Resistance [47] kΩ: ").strip()
            R_load = float(R_load_input) if R_load_input else 47.0
            
            C_total_input = input("Total Capacitance (cable + preamp) [200] pF: ").strip()
            C_total = float(C_total_input) if C_total_input else 200.0
            
            scale_input = input("Frequency scale (log/linear) [log]: ").strip().lower()
            use_log = scale_input in ['', 'log', 'logarithmic']
            
            phase_input = input("Show phase response? (yes/no) [yes]: ").strip().lower()
            show_phase = phase_input in ['', 'yes', 'y', 'true', '1']
            
            print(f"\nGenerating cartridge loading plot...")
            plot_cartridge_response(L_cart, R_cart, R_load, C_total, use_log, show_phase=show_phase)
            
        except ValueError as e:
            print(f"\n✗ Error: Invalid input - {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n\n✗ Cancelled by user")
            sys.exit(1)
