import psutil
import time
import datetime

def get_system_info():
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)
    uptime = str(datetime.timedelta(seconds=uptime_seconds))
    boot_time = datetime.datetime.fromtimestamp(boot_time).strftime("%Y-%m-%d %H:%M:%S")


    network = psutil.net_io_counters()
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')   


    return{
        "cpu_usage": psutil.cpu_percent(interval=1),
        "ram_total": ram.total,
        "ram_used": ram.used,
        "ram_percent": ram.percent,
        "disk_total": disk.total,
        "disk_used": disk.used,
        "disk_percent": disk.percent,
        "disk_info": psutil.disk_usage('/'),
        "cpu_core": psutil.cpu_count(logical=False),
        "logical_cpu": psutil.cpu_count(),
        "boot_time": boot_time,
        "uptime": uptime,
        "downloaded": network.bytes_recv,
        "uploaded": network.bytes_sent,
        "battery": psutil.sensors_battery()

    }

def main():
    system_data = get_system_info()

    total_ram_gb = system_data['ram_total'] / (1024 ** 3)
    used_ram_gb = system_data['ram_used'] / (1024 ** 3)

    total_disk_gb = system_data['disk_total'] / (1024 ** 3)
    used_disk_gb = system_data['disk_used'] / (1024 ** 3)

    print("=========================")
    print("\n" + "-------SYSTEM INFO-------")
    print("=========================")
    print(f"CPU Usage: {system_data['cpu_usage']}%")
    print(f"CPU Cores: {system_data['cpu_core']}")
    print(f"Logical CPUs: {system_data['logical_cpu']} \n")

    print(f"RAM Usage: {used_ram_gb:.2f} / {total_ram_gb:.2f} GB ({system_data['ram_percent']}%)")
    print(f"DISK Usage: {used_disk_gb:.2f} / {total_disk_gb:.2f} GB ({system_data['disk_percent']}%)")

    print()
    print(f"System Boot time: {system_data['boot_time']}")
    print(f"System Uptime: {system_data['uptime']}")

    if system_data["battery"] is not None:
        print("\n" + f"Battery: {system_data['battery'].percent:.0f} %")

    print()
    print(f"Downloaded: {system_data['downloaded']  /(1024 ** 3):.2f} GB")
    print(f"Uploaded: {system_data['uploaded']  /(1024 ** 3):.2f} GB")

    print("=========================")

    
if __name__ == "__main__":
    main()   