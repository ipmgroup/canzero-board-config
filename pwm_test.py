import os
import sys
import argparse
import signal
import subprocess
import time


# Class to control PWM
class PWMController:
    def __init__(self, pwm_chip, pwm_channel, period_ms, duty_cycle_ms):
        self.pwm_chip = pwm_chip
        self.pwm_channel = pwm_channel
        # Convert milliseconds to nanoseconds
        self.period_ns = period_ms * 1_000_000
        self.duty_cycle_ns = duty_cycle_ms * 1_000_000

        # Paths for the sysfs interface
        self.pwm_path = f"/sys/class/pwm/pwmchip{self.pwm_chip}/pwm{self.pwm_channel}/"
        self.export_path = f"/sys/class/pwm/pwmchip{self.pwm_chip}/export"
        self.unexport_path = f"/sys/class/pwm/pwmchip{self.pwm_chip}/unexport"

    # Function to set up PWM
    def setup_pwm(self):
        # Export the PWM channel if it is not already exported
        try:
            subprocess.run(['echo', str(self.pwm_channel), '>', self.export_path], check=True, shell=True)
        except subprocess.CalledProcessError:
            # PWM channel is already exported
            pass

        # Set the period
        subprocess.run(['echo', str(self.period_ns), '>', os.path.join(self.pwm_path, "period")], check=True, shell=True)
        # print('echo', str(int(self.period_ns)), '>', os.path.join(self.pwm_path, "period"))

        # Set the duty cycle
        subprocess.run(['echo', str(self.duty_cycle_ns), '>', os.path.join(self.pwm_path, "duty_cycle")], check=True, shell=True)
        # print('echo', str(int(self.duty_cycle_ns)), '>', os.path.join(self.pwm_path, "duty_cycle"))

        # Enable the PWM output
        subprocess.run(['echo', '1', '>', os.path.join(self.pwm_path, "enable")], check=True, shell=True)
        # print('echo', '1', '>', os.path.join(self.pwm_path, "enable"))


    # Function to change the duty cycle
    def set_duty_cycle(self, duty_ms):
        duty_ns = duty_ms * 1_000_000  # Convert milliseconds to nanoseconds
        subprocess.run(['echo', str(duty_ns), '>', os.path.join(self.pwm_path, "duty_cycle")], check=True, shell=True)

    # Function to disable PWM
    def disable_pwm(self):
        if not os.path.exists(self.pwm_path):
            print(f"Error: Path {self.pwm_path} does not exist.")
            sys.exit(1)
        try:
            subprocess.run(['echo', '0', '>', os.path.join(self.pwm_path, "enable")], check=True, shell=True)
        except subprocess.CalledProcessError as e:
            if e.returncode == 22:
                print(f"Invalid argument: Unable to write to {os.path.join(self.pwm_path, 'enable')}. Check the device state.")
            else:
                print(f"Unexpected error: {e}")
            sys.exit(1)
        # Unexport the PWM channel
        try:
            subprocess.run(['echo', str(self.pwm_channel), '>', self.unexport_path], check=True, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to unexport PWM channel: {e}")
            sys.exit(1)

# Handle exit on key press
def signal_handler(sig, frame):
    print("\nProgram interrupted. Exiting...")
    sys.exit(0)

# Main function
def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Control PWM on Raspberry Pi using pwmchip interface.")
    parser.add_argument("--chip", type=int, default=0, help="PWM chip number (default: 0)")
    parser.add_argument("--channel", type=int, default=0, help="PWM channel number (default: 0)")
    parser.add_argument("--period", type=float, default=20, help="PWM period in milliseconds (default: 20 ms)")
    parser.add_argument("--duty", type=float, default=1.5, help="Duty cycle in milliseconds (default: 1.5 ms)")

    args = parser.parse_args()

    # Create an instance of PWMController
    pwm_controller = PWMController(args.chip, args.channel, args.period, args.duty)

    # Set up signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)

    try:
        pwm_controller.setup_pwm()
        print(f"PWM is set with a period of {args.period} ms and a duty cycle of {args.duty} ms.")
        print("Press Ctrl+C to exit...")

        # Wait indefinitely for user to press Ctrl+C
        while True:
            time.sleep(1)

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
    finally:
        pwm_controller.disable_pwm()
        print("PWM disabled")

# Run the main function
if __name__ == "__main__":
    main()