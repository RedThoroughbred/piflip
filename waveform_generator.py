#!/usr/bin/env python3
"""
Waveform Generator for PiFlip
Creates ASCII waveform visualizations from signal timings
"""

class WaveformGenerator:
    """Generate ASCII waveforms from signal data"""

    @staticmethod
    def generate_ascii_waveform(timings, width=50, height=1):
        """
        Generate ASCII waveform from timing data

        Args:
            timings: List of {state, duration_us} dicts
            width: Character width of output
            height: Height in characters (1 for simple, 3+ for detailed)

        Returns:
            String containing ASCII waveform
        """
        if not timings or len(timings) == 0:
            return '▁' * width

        # Calculate total duration
        total_duration = sum(t['duration_us'] for t in timings)

        if total_duration == 0:
            return '▁' * width

        # Build waveform
        waveform = []
        current_pos = 0

        for timing in timings:
            # Calculate how many characters this pulse should take
            pulse_width = int((timing['duration_us'] / total_duration) * width)

            if pulse_width < 1:
                pulse_width = 1

            # Add pulse representation
            if timing['state'] == 1:  # High
                waveform.extend(['█'] * pulse_width)
            else:  # Low
                waveform.extend(['▁'] * pulse_width)

            current_pos += pulse_width

            # Stop if we've filled the width
            if current_pos >= width:
                break

        # Pad if needed
        while len(waveform) < width:
            waveform.append('▁')

        # Trim if too long
        waveform = waveform[:width]

        return ''.join(waveform)

    @staticmethod
    def generate_detailed_waveform(timings, width=50, height=3):
        """
        Generate multi-line detailed waveform

        Args:
            timings: List of {state, duration_us} dicts
            width: Character width
            height: Number of lines (3 recommended)

        Returns:
            Multi-line string
        """
        if not timings or len(timings) == 0:
            return '\n'.join(['─' * width] * height)

        total_duration = sum(t['duration_us'] for t in timings)

        if total_duration == 0:
            return '\n'.join(['─' * width] * height)

        # Build waveform for each line
        lines = [[] for _ in range(height)]
        current_pos = 0

        for timing in timings:
            pulse_width = max(1, int((timing['duration_us'] / total_duration) * width))

            if timing['state'] == 1:  # High
                # Top line
                lines[0].extend(['▀'] * pulse_width)
                # Middle line
                lines[1].extend(['█'] * pulse_width)
                # Bottom line
                lines[2].extend(['▀'] * pulse_width)
            else:  # Low
                # Top line
                lines[0].extend([' '] * pulse_width)
                # Middle line
                lines[1].extend(['▁'] * pulse_width)
                # Bottom line
                lines[2].extend([' '] * pulse_width)

            current_pos += pulse_width

            if current_pos >= width:
                break

        # Pad and trim all lines
        for i in range(height):
            while len(lines[i]) < width:
                lines[i].append(' ')
            lines[i] = lines[i][:width]

        return '\n'.join([''.join(line) for line in lines])

    @staticmethod
    def generate_rssi_meter(rssi, width=20):
        """
        Generate RSSI signal strength bar

        Args:
            rssi: RSSI value in dBm (e.g., -65)
            width: Character width of bar

        Returns:
            String like "▓▓▓▓▓░░░░░ -65 dBm"
        """
        # RSSI typically ranges from -100 (worst) to -30 (best)
        # Normalize to 0-100
        normalized = max(0, min(100, int(((rssi + 100) / 70) * 100)))

        # Calculate bar segments
        filled = int((normalized / 100) * width)
        empty = width - filled

        bar = '▓' * filled + '░' * empty

        # Add quality indicator
        if rssi > -60:
            quality = '✅ STRONG'
        elif rssi > -80:
            quality = '⚠️  MODERATE'
        else:
            quality = '❌ WEAK'

        return f"{bar} {rssi:.0f} dBm {quality}"

    @staticmethod
    def generate_progress_bar(current, total, width=30):
        """
        Generate progress bar

        Args:
            current: Current value
            total: Total value
            width: Character width

        Returns:
            String like "[========>     ] 60%"
        """
        if total == 0:
            return '[' + ' ' * width + '] 0%'

        percent = int((current / total) * 100)
        filled = int((current / total) * width)
        empty = width - filled - 1

        if filled == width:
            bar = '=' * width
        else:
            bar = '=' * filled + '>' + ' ' * empty

        return f"[{bar}] {percent}%"

    @staticmethod
    def generate_spectrum(frequencies, width=50, height=10):
        """
        Generate ASCII spectrum analyzer view

        Args:
            frequencies: List of {frequency, rssi} dicts
            width: Character width
            height: Height in lines

        Returns:
            Multi-line spectrum display
        """
        if not frequencies:
            return 'No data'

        # Find RSSI range
        rssi_values = [f['rssi'] for f in frequencies]
        min_rssi = min(rssi_values)
        max_rssi = max(rssi_values)

        if min_rssi == max_rssi:
            max_rssi = min_rssi + 10

        # Create lines
        lines = []

        for level in range(height, 0, -1):
            line = []
            threshold = min_rssi + ((max_rssi - min_rssi) * level / height)

            for freq_data in frequencies:
                if freq_data['rssi'] >= threshold:
                    line.append('█')
                else:
                    line.append(' ')

            # Add RSSI label
            rssi_label = f"{int(threshold):>4}"
            lines.append(f"{rssi_label} ┤{''.join(line)}")

        # Add frequency axis
        freq_values = [f['frequency'] for f in frequencies]
        min_freq = min(freq_values)
        max_freq = max(freq_values)

        axis = f"     └{'─' * len(frequencies)}"
        labels = f"      {min_freq:.1f}MHz  {max_freq:.1f}MHz"

        lines.append(axis)
        lines.append(labels)

        return '\n'.join(lines)


if __name__ == '__main__':
    # Test waveform generator
    gen = WaveformGenerator()

    # Create sample timings
    sample_timings = [
        {'state': 1, 'duration_us': 500},
        {'state': 0, 'duration_us': 500},
        {'state': 1, 'duration_us': 1500},
        {'state': 0, 'duration_us': 500},
        {'state': 1, 'duration_us': 500},
        {'state': 0, 'duration_us': 1500},
        {'state': 1, 'duration_us': 1500},
        {'state': 0, 'duration_us': 500},
    ]

    print("Simple Waveform:")
    print(gen.generate_ascii_waveform(sample_timings, width=60))

    print("\nDetailed Waveform:")
    print(gen.generate_detailed_waveform(sample_timings, width=60, height=3))

    print("\nRSSI Meter:")
    print(gen.generate_rssi_meter(-65, width=20))

    print("\nProgress Bar:")
    print(gen.generate_progress_bar(45, 100, width=30))

    print("\nSpectrum:")
    sample_spectrum = [
        {'frequency': 433.0, 'rssi': -75},
        {'frequency': 433.2, 'rssi': -82},
        {'frequency': 433.4, 'rssi': -90},
        {'frequency': 433.6, 'rssi': -65},
        {'frequency': 433.8, 'rssi': -88},
        {'frequency': 434.0, 'rssi': -95},
    ]
    print(gen.generate_spectrum(sample_spectrum, width=50, height=8))
