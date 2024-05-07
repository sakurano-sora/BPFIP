import socket
import re

# 文明6默认端口
port_min = 62900
port_max = 62999


def main():

    interfaces = socket.getaddrinfo(socket.gethostname(), None)

    device_ip = ["localhost"]

    if interfaces:
        print(f"[0] 网卡地址: {device_ip[0]}")
        for index in range(len(interfaces)):
            device_ip.append(interfaces[index][4][0])
            print(f"[{index + 1}] 网卡地址: {device_ip[index + 1]}")
    else:
        print("未获取到网卡")
        return

    # 监听广播地址 (使用WinIPBroadcast时需手动指定到OpenVPN网卡地址)
    while True:
        try:
            listen_device_index = input("输入序号选择监听网卡[默认localhost]: ") or 0
            listen_ip = device_ip[int(listen_device_index)]
            break
        except ValueError:
            print("输入数据类型错误,请输入序号")
            continue
        except IndexError:
            print("输入序号超出范围,请重新输入")
            continue

    # 发送地址 (OpenVPN中本机地址)
    while True:
        try:
            src_device_index = input("输入序号选择发送网卡: ")
            src_ip = device_ip[int(src_device_index)]
            break
        except ValueError:
            print("输入数据类型错误,请输入序号")
            continue
        except IndexError:
            print("输入序号超出范围,请重新输入")
            continue

    # 目标地址 (OpenVPN中主机地址)
    while True:
        dst_ip = input("输入目标主机地址: ")
        pattern = r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$'
        if re.match(pattern, dst_ip):
            break
        else:
            print("输入数据类型错误,请输入序号")
            continue

    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for port in range(port_min, port_max + 1):
        try:
            listen_sock.bind((listen_ip, port))
            print("\n")
            print(f"监听地址: {listen_ip},监听端口: {port}")
            break
        except socket.error as e:
            print(f'端口 {port} 绑定失败,尝试下一个: {e}')
    else:
        print('没有可用的端口')
        return

    while True:
        print("\n等待接收消息...")
        data, address = listen_sock.recvfrom(2048)
        print(f"收到消息: {data.hex()}")
        print(f"来源地址: {address[0]},来源端口: {address[1]}")
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            send_sock.bind((src_ip, address[1]))
            print(f"发送地址: {src_ip},发送端口: {address[1]}")
        except socket.error as e:
            print(f'端口 {address[1]} 绑定失败: {e}')
            return
        print(f"目标地址: {dst_ip}")
        for port in range(port_min, port_max + 1):
            try:
                send_sock.sendto(data, (dst_ip, port))
                print(f'目标端口: {port},发送成功')
            except socket.error as e:
                print(f'目标端口: {port},发送失败: {e}')
        send_sock.close()


main()
