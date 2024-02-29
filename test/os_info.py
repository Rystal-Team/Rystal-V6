import psutil, platform, datetime, time, sys

start_time = time.time()

while True:
    cpu = psutil.cpu_percent(0.5)
    time.sleep(0.5)
    ram_used = round(psutil.virtual_memory()[3] / 1000000000, 1)
    ram_total = round(psutil.virtual_memory()[0] / 1000000000, 1)
    os_platform = platform.system()
    os_version = platform.version()
    os_release = platform.release()
    os_time = datetime.datetime.now()
    os_time = os_time.strftime("%H:%M:%S %d/%m/%y")

    uptime_str = str(datetime.timedelta(seconds=(round(time.time() - start_time))))

    sys.stdout.write(
        f"CPU: {cpu}%\nRAM: {ram_used}/{ram_total} GB\nOS: {os_platform} Version: {os_version} Release: {os_release}\nUp Time: {uptime_str}\n",
    )
