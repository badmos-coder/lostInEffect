
import argparse
import json
import os

from main import SecureBiometricSystem

def handle_test_adversarial(args):
    """Handles the 'test-adversarial' command."""
    print("Testing Adversarial Detector...")
    if not os.path.exists(args.face_image):
        print(f"Error: Image file not found at '{args.face_image}'")
        return

    # Simulate reading an image
    # We pass the file path directly to the new demonstrable model
    result = system.adversarial_detector.detect_adversarial_attack(args.face_image)

    print(json.dumps(result, indent=4))

def handle_test_behavioral(args):
    """Handles the 'test-behavioral' command."""
    print("--- Testing Behavioral Analytics ---")
    system = SecureBiometricSystem()
    result = system.behavioral_analytics.analyze_fingerprint_hex(args.fingerprint_hex)
    print(json.dumps(result, indent=4))

def handle_full_authentication(args):
    """Handles the 'authenticate' command."""
    print("--- Running Full Biometric Authentication Flow ---")
    system = SecureBiometricSystem()

    biometric_data = {
        "face_image_path": args.face_image,
        "fingerprint_hex": args.fingerprint_hex
    }

    context_data = {
        'location_change': args.location_change,
        'device_change': args.device_change,
        'network_change': args.network_change,
        'failed_attempts': args.failed_attempts,
        'lighting': 'good',  # Assuming good lighting for CLI demo
        'noise_level': 0.1    # Assuming low noise for CLI demo
    }

    result = system.authenticate_user(args.user_id, biometric_data, context_data)
    print(json.dumps(result, indent=4))


def main():
    parser = argparse.ArgumentParser(
        description="CLI tool for the Secure Biometric System. Allows for individual model testing and full authentication flow.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # --- Sub-parser for 'test-adversarial' ---
    parser_adv = subparsers.add_parser('test-adversarial', help='Test the adversarial attack detector individually.')
    parser_adv.add_argument('--face-image', type=str, required=True, help='Path to the face image file.')
    parser_adv.set_defaults(func=handle_test_adversarial)

    # --- Sub-parser for 'test-behavioral' ---
    parser_beh = subparsers.add_parser('test-behavioral', help='Test the behavioral analytics module individually.')
    parser_beh.add_argument('--fingerprint-hex', type=str, required=True, help='Hex string of the fingerprint template.')
    parser_beh.set_defaults(func=handle_test_behavioral)

    # --- Sub-parser for 'authenticate' ---
    parser_auth = subparsers.add_parser('authenticate', help='Run the full multi-modal authentication flow.')
    parser_auth.add_argument('--user-id', type=str, required=True, help='The user ID for the authentication attempt.')
    parser_auth.add_argument('--face-image', type=str, required=True, help='Path to the face image file.')
    parser_auth.add_argument('--fingerprint-hex', type=str, required=True, help='Hex string of the fingerprint template.')
    parser_auth.add_argument('--location-change', action='store_true', help='Flag to indicate a change in location.')
    parser_auth.add_argument('--device-change', action='store_true', help='Flag to indicate a change in device.')
    parser_auth.add_argument('--network-change', action='store_true', help='Flag to indicate a change in network.')
    parser_auth.add_argument('--failed-attempts', type=int, default=0, help='Number of recent failed attempts.')
    parser_auth.set_defaults(func=handle_full_authentication)


    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
