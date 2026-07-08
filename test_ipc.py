import subprocess
import time
import sys
import psutil


def cleanup():
    for proc in psutil.process_iter(["name"]):
        if proc.info["name"] == "Mreminder.exe":
            proc.kill()


cleanup()
time.sleep(1)

print("1. Start primary instance")
p1 = subprocess.Popen(["dist\\Mreminder\\Mreminder.exe"])
time.sleep(3)

if p1.poll() is not None:
    print(f"Error: p1 exited early with code {p1.poll()}")
    sys.exit(1)
print("p1 is running")

print("2. Start second instance (normal)")
p2 = subprocess.Popen(["dist\\Mreminder\\Mreminder.exe"])
p2.wait()
print(f"p2 exit code: {p2.returncode}")

print("3. Start second instance (silent)")
p3 = subprocess.Popen(["dist\\Mreminder\\Mreminder.exe", "--silent"])
p3.wait()
print(f"p3 exit code: {p3.returncode}")

print("4. Terminate p1")
p1.terminate()
p1.wait()
time.sleep(1)
cleanup()
time.sleep(1)

print("5. Start new primary instance (silent)")
p4 = subprocess.Popen(["dist\\Mreminder\\Mreminder.exe", "--silent"])
time.sleep(3)
if p4.poll() is not None:
    print(f"Error: p4 exited early with code {p4.poll()}")
    sys.exit(1)
print("p4 is running")

print("6. Start second instance (normal)")
p5 = subprocess.Popen(["dist\\Mreminder\\Mreminder.exe"])
p5.wait()
print(f"p5 exit code: {p5.returncode}")

p4.terminate()
p4.wait()
cleanup()
print("All tests passed.")
