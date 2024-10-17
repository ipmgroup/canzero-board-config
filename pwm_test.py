import time
import sys
import argparse
import signal

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
            with open(self.export_path, 'w') as f:
                f.write(str(self.pwm_channel))
        except FileExistsError:
            # PWM channel is already exported
            pass

        # Set the period
        with open(self.pwm_path + "period", 'w') as f:
            f.write(str(self.period_ns))

        # Set the duty cycle
        with open(self.pwm_path + "duty_cycle", 'w') as f:
            f.write(str(self.duty_cycle_ns))

        # Enable the PWM output
        with open(self.pwm_path + "enable", 'w') as f:
            f.write("1")

    # Function to change the duty cycle
    def set_duty_cycle(self, duty_ms):
        duty_ns = duty_ms * 1_000_000  # Convert milliseconds to nanoseconds
        with open(self.pwm_path + "duty_cycle", 'w') as f:
            f.write(str(duty_ns))

    # Function to disable PWM
    def disable_pwm(self):
        with open(self.pwm_path + "enable", 'w') as f:
            f.write("0")
        # Unexport the PWM channel
        with open(self.unexport_path, 'w') as f:
            f.write(str(self.pwm_channel))

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
