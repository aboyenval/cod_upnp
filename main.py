"""
Open ports for COD game on a router using uPnp
"""
import asyncio
from aioupnp.upnp import UPnP
from enum import Enum
from games import Games
from typing import List, Dict, Tuple
import subprocess


class CodUPNP:
    """
    Open ports for COD game on a router using uPnp
    """

    def get_games(self) -> List[str]:
        """
        Get list of COD game
        :return: list of COD game
        """
        games_list = []
        for game in Games:
            games_list.append(game)

        return games_list

    def get_platforms(self, game: str) -> List[str]:
        """
        Get list of platform compatible for a game
        :param game: COD game
        :return: list of compatible plateform
        """
        platform_list = []
        for platform in Games[game]:
            platform_list.append(platform)
        return platform_list

    def get_ports(self, game: str, platform: str) -> Dict[str, list] :
        """
        get TCP and UDP port for a specific COD game / platform
        :param game: COD game
        :param platform: client's platform
        :return: Dictionnary for each type (TCP or UDP)
        """
        if game in Games and platform in Games[game]:
            return {
                "TCP": Games[game][platform]["TCP"],
                "UDP": Games[game][platform]["UDP"]
            }
        return {"TCP": [], "UDP": []}

    def get_full_port_list(self, port_list: list) -> List:
        """
        Convert list of port with range to a list without range
        :param port_list: list of port
        :return:
        """
        ports = []
        for p in port_list:
            # try to split with - according to the range format
            tabP = p.split("-")
            if len(tabP) == 1:
                ports.append(int(p))
            else:
                for p_step in range(int(tabP[0]), int(tabP[1])+1):
                    ports.append(p_step)

        return ports

    def convert_string(self, input: str) -> str:
        """
        Replace space by _ in a string
        :param input: input text with spaces
        :return: output text without space
        """
        return input.replace(" ", "_")

    def get_full_ports_to_open(self, game: str, platform: str) -> Tuple[Dict[str, str],Dict[str, str]]:
        """
        get TCP and UDP port for a specific COD game / platform
        :param game: COD game type
        :param platform: platform of the client
        :return: list of TCP and UDP port
        """
        tcp_list = {}
        udp_list = {}
        if game == "all":
            game_list = self.get_games()
            for g in game_list:
                if platform == "all":
                    platform_list = self.get_platforms(g)
                    for p in platform_list:
                        ports = self.get_ports(g, p)
                        tcp_ports = self.get_full_port_list(ports["TCP"])
                        udp_ports = self.get_full_port_list(ports["UDP"])
                        for tcp in tcp_ports:
                            if tcp not in tcp_list:
                                tcp_list[tcp] = f"{g}_{p}"
                            else:
                                tcp_list[tcp] = "cod_multi"
                        for udp in udp_ports:
                            if udp not in udp_list:
                                udp_list[udp] = f"{g}_{p}"
                            else:
                                udp_list[udp] = "cod_multi"
                else:
                    ports = self.get_ports(g, platform)
                    tcp_ports = self.get_full_port_list(ports["TCP"])
                    udp_ports = self.get_full_port_list(ports["UDP"])
                    for tcp in tcp_ports:
                        if tcp not in tcp_list:
                            tcp_list[tcp] = f"{g}_{platform}"
                        else:
                            tcp_list[tcp] = "cod_multi"
                    for udp in udp_ports:
                        if udp not in udp_list:
                            udp_list[udp] = f"{g}_{platform}"
                        else:
                            udp_list[udp] = "cod_multi"
        else:
            if platform == "all":
                platform_list = self.get_platforms(game)
                for p in platform_list:
                    ports = self.get_ports(game, p)
                    tcp_ports = self.get_full_port_list(ports["TCP"])
                    udp_ports = self.get_full_port_list(ports["UDP"])
                    for tcp in tcp_ports:
                        if tcp not in tcp_list:
                            tcp_list[tcp] = f"{game}_{p}"
                        else:
                            tcp_list[tcp] = "cod_multi"
                    for udp in udp_ports:
                        if udp not in udp_list:
                            udp_list[udp] = f"{game}_{p}"
                        else:
                            udp_list[udp] = "cod_multi"
            else:
                ports = self.get_ports(game, platform)
                tcp_ports = self.get_full_port_list(ports["TCP"])
                udp_ports = self.get_full_port_list(ports["UDP"])
                for tcp in tcp_ports:
                    if tcp not in tcp_list:
                        tcp_list[tcp] = f"{game}_{platform}"
                    else:
                        tcp_list[tcp] = "cod_multi"
                for udp in udp_ports:
                    if udp not in udp_list:
                        udp_list[udp] = f"{game}_{platform}"
                    else:
                        udp_list[udp] = "cod_multi"

        return tcp_list, udp_list

    async def open_ports(self, game: str, platform: str, ip_address: str):
        """
        Open ports for a COD game version for a platform
        :param game: COD game type
        :param platform: client type
        :param ip_address: ip address of the client
        :return:
        """

        self.upnp = await UPnP.discover()
        await self.upnp.add_port_mapping(1234, 'TCP', 1234, upnp.lan_address, 'test mapping')

        tcp, udp = self.get_full_ports_to_open(game, platform)
        for t in tcp:
            await self._open(ip_address, "TCP", int(t), int(t), self.convert_string(tcp[t]))

    async def _open(self, ip_address: str, port_type:  str, internal_port: int, external_port: int, description: str) -> None:
        """
        Add port mapping on the router
        :param ip_address: ip of the client
        :param port_type: TCP / UDP
        :param internal_port: port number
        :param external_port: port number
        :param description: description to add to the router
        :return:
        """
        print(f"Add rule for the port {port_type}:{internal_port}/{external_port} on {ip_address} width description {description}")
        await self.upnp.add_port_mapping(internal_port, port_type, external_port, ip_address, description)




async def example():
    """
    Example to open port for Moder Warfare for a PC
    :return:
    """

    upnp = await UPnP.discover()

    ip_address = "IP_ADDRESS_OF_THE_CLIENT"

    # get ports by platforms
    code_upnp = CodUPNP()

    tcp, udp = code_upnp.get_full_ports_to_open("Modern Warfare", "PC")
    for t in tcp:
        tcpport = int(t)
        text = code_upnp.convert_string(tcp[t])
        try:
            await upnp.add_port_mapping(tcpport, 'TCP', tcpport, ip_address, text)
            await upnp.delete_port_mapping(tcpport, 'TCP')
        except Exception as exp:
            print(f"Port TCP {tcpport} already configured")

        p = subprocess.Popen(f'netsh advfirewall firewall add rule name="COD {text} {tcpport}" dir=in action=allow protocol=TCP localport={tcpport}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        p = subprocess.Popen(f'netsh advfirewall firewall add rule name="COD {text} {tcpport}" dir=out action=allow protocol=TCP localport={tcpport}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

    # Add all UDP ports
    for port in udp:
        udpport = int(port)
        text = code_upnp.convert_string(udp[port])
        try:
            await upnp.add_port_mapping(udpport, 'UDP', udpport, ip_address, text)
        except Exception as exp:
            print(f"Port UDP {udpport} already configured")

        # add rule to windows firewall
        p = subprocess.Popen(
            f'netsh advfirewall firewall add rule name="COD {text} {tcpport}" dir=in action=allow protocol=UDP localport={tcpport}',
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        # add rule to windows firewall
        p = subprocess.Popen(
            f'netsh advfirewall firewall add rule name="COD {text} {tcpport}" dir=out action=allow protocol=UDP localport={tcpport}',
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

asyncio.run(example())