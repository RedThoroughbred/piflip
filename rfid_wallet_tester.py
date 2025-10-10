#!/usr/bin/env python3
"""
RFID Wallet Tester - Test if your RFID-blocking wallet actually works
"""

import time
from datetime import datetime
from pathlib import Path
import board
import busio
from adafruit_pn532.i2c import PN532_I2C

class RFIDWalletTester:
    """Test RFID-blocking effectiveness"""

    def __init__(self):
        # Initialize PN532
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.pn532 = PN532_I2C(i2c, address=0x24, reset=None, debug=False)
            self.pn532.SAM_configuration()
            self.available = True
        except Exception as e:
            print(f"[!] PN532 not available: {e}")
            self.available = False

    def test_blocking_effectiveness(self, duration=10, sample_interval=0.2):
        """
        Test RFID blocking wallet

        Process:
        1. Scan without wallet (baseline)
        2. User puts card in wallet
        3. Scan with wallet (test blocking)
        4. Calculate blocking effectiveness

        Args:
            duration: How long to test (seconds)
            sample_interval: How often to check (seconds)

        Returns:
            dict with test results
        """
        if not self.available:
            return {'status': 'error', 'message': 'PN532 not available'}

        results = {
            'status': 'testing',
            'phase': 1,
            'baseline': None,
            'protected': None,
            'effectiveness': None
        }

        # Phase 1: Baseline (without wallet)
        print("\n[*] Phase 1: Testing WITHOUT wallet")
        print("[*] Please hold card near reader (outside wallet)")
        print(f"[*] Testing for {duration} seconds...")

        baseline_detections = 0
        baseline_attempts = 0
        start_time = time.time()

        while time.time() - start_time < duration:
            baseline_attempts += 1
            uid = self.pn532.read_passive_target(timeout=sample_interval)
            if uid:
                baseline_detections += 1
            time.sleep(sample_interval)

        baseline_success_rate = (baseline_detections / baseline_attempts * 100) if baseline_attempts > 0 else 0

        results['baseline'] = {
            'detections': baseline_detections,
            'attempts': baseline_attempts,
            'success_rate': baseline_success_rate
        }

        print(f"[+] Baseline: {baseline_detections}/{baseline_attempts} detections ({baseline_success_rate:.1f}%)")

        # Check if baseline is good enough
        if baseline_success_rate < 50:
            return {
                'status': 'error',
                'message': 'Baseline detection too low. Card may not be compatible or positioned incorrectly.',
                'baseline': results['baseline']
            }

        # Phase 2: Protected (with wallet)
        print("\n[*] Phase 2: Testing WITH wallet")
        print("[*] Please put card IN your RFID-blocking wallet")
        input("[*] Press ENTER when ready...")
        print(f"[*] Testing for {duration} seconds...")

        protected_detections = 0
        protected_attempts = 0
        start_time = time.time()

        while time.time() - start_time < duration:
            protected_attempts += 1
            uid = self.pn532.read_passive_target(timeout=sample_interval)
            if uid:
                protected_detections += 1
            time.sleep(sample_interval)

        protected_success_rate = (protected_detections / protected_attempts * 100) if protected_attempts > 0 else 0

        results['protected'] = {
            'detections': protected_detections,
            'attempts': protected_attempts,
            'success_rate': protected_success_rate
        }

        print(f"[+] Protected: {protected_detections}/{protected_attempts} detections ({protected_success_rate:.1f}%)")

        # Calculate effectiveness
        blocking_effectiveness = 100 - (protected_success_rate / baseline_success_rate * 100) if baseline_success_rate > 0 else 0
        blocking_effectiveness = max(0, min(100, blocking_effectiveness))  # Clamp 0-100

        results['effectiveness'] = blocking_effectiveness
        results['status'] = 'complete'

        # Assessment
        if blocking_effectiveness >= 95:
            results['assessment'] = 'excellent'
            results['recommendation'] = 'Your wallet provides excellent RFID protection!'
        elif blocking_effectiveness >= 80:
            results['assessment'] = 'good'
            results['recommendation'] = 'Your wallet provides good RFID protection.'
        elif blocking_effectiveness >= 60:
            results['assessment'] = 'fair'
            results['recommendation'] = 'Your wallet provides fair protection. Consider upgrading.'
        else:
            results['assessment'] = 'poor'
            results['recommendation'] = 'Your wallet provides poor protection. Upgrade recommended!'

        print(f"\n[+] Blocking Effectiveness: {blocking_effectiveness:.1f}%")
        print(f"[+] Assessment: {results['assessment'].upper()}")
        print(f"[+] {results['recommendation']}")

        return results

    def quick_test(self, test_duration=3):
        """
        Quick wallet test (simplified)

        Returns:
            dict with readable/blocked status
        """
        if not self.available:
            return {'status': 'error', 'message': 'PN532 not available'}

        print("[*] Quick wallet test")
        print("[*] Place card (in wallet) near reader...")
        print(f"[*] Testing for {test_duration} seconds...")

        detections = 0
        attempts = 0
        start_time = time.time()

        while time.time() - start_time < test_duration:
            attempts += 1
            uid = self.pn532.read_passive_target(timeout=0.2)
            if uid:
                detections += 1
                uid_hex = ''.join([f'{b:02X}' for b in uid])
                print(f"[!] Card detected: {uid_hex}")
            time.sleep(0.2)

        if detections > 0:
            return {
                'status': 'readable',
                'message': 'Card is READABLE through wallet!',
                'detections': detections,
                'attempts': attempts,
                'recommendation': 'Your wallet is NOT blocking RFID. Consider upgrading!'
            }
        else:
            return {
                'status': 'blocked',
                'message': 'Card is BLOCKED by wallet',
                'detections': 0,
                'attempts': attempts,
                'recommendation': 'Your wallet is working correctly!'
            }

    def continuous_monitor(self, duration=30):
        """
        Continuously monitor for card presence
        Useful for demonstrating blocking effect

        Returns real-time detection status
        """
        if not self.available:
            return {'status': 'error', 'message': 'PN532 not available'}

        print(f"[*] Monitoring for {duration} seconds...")
        print("[*] Try moving card in/out of wallet")
        print("")

        detections = []
        start_time = time.time()
        last_status = None

        while time.time() - start_time < duration:
            uid = self.pn532.read_passive_target(timeout=0.1)
            current_status = 'detected' if uid else 'not_detected'

            # Only print on status change
            if current_status != last_status:
                timestamp = time.time() - start_time
                if current_status == 'detected':
                    uid_hex = ''.join([f'{b:02X}' for b in uid])
                    print(f"[{timestamp:5.1f}s] ✅ DETECTED: {uid_hex}")
                else:
                    print(f"[{timestamp:5.1f}s] ⚫ BLOCKED")

                detections.append({
                    'time': timestamp,
                    'status': current_status,
                    'uid': ''.join([f'{b:02X}' for b in uid]) if uid else None
                })

                last_status = current_status

            time.sleep(0.1)

        return {
            'status': 'complete',
            'duration': duration,
            'events': detections,
            'total_events': len(detections)
        }


if __name__ == '__main__':
    # Test RFID Wallet Tester
    tester = RFIDWalletTester()

    print("[*] RFID Wallet Tester")
    print(f"[*] Available: {tester.available}")

    if tester.available:
        print("\n" + "="*60)
        print("RFID WALLET TESTER")
        print("="*60)

        choice = input("\nSelect test:\n1. Full test (baseline + protected)\n2. Quick test\n3. Continuous monitor\n\nChoice: ")

        if choice == '1':
            result = tester.test_blocking_effectiveness(duration=5)
            print("\n" + "="*60)
            print("TEST RESULTS")
            print("="*60)
            if result['status'] == 'complete':
                print(f"Blocking Effectiveness: {result['effectiveness']:.1f}%")
                print(f"Assessment: {result['assessment'].upper()}")
                print(f"Recommendation: {result['recommendation']}")

        elif choice == '2':
            result = tester.quick_test(test_duration=3)
            print("\n" + "="*60)
            print(f"Status: {result['status'].upper()}")
            print(f"Message: {result['message']}")
            print(f"Recommendation: {result['recommendation']}")

        elif choice == '3':
            result = tester.continuous_monitor(duration=30)
            print("\n" + "="*60)
            print(f"Monitoring complete: {result['total_events']} status changes")
