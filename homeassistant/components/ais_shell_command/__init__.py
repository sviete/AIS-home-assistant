"""
Exposes regular shell commands as services.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/shell_command/
"""
import asyncio
import logging
import os

import homeassistant.components.ais_dom.ais_global as ais_global
from homeassistant.const import CONF_IP_ADDRESS, CONF_MAC

DOMAIN = "ais_shell_command"
GLOBAL_X = 0
_LOGGER = logging.getLogger(__name__)


@asyncio.coroutine
def async_setup(hass, config):
    """Register the service."""
    config = config.get(DOMAIN, {})

    @asyncio.coroutine
    def change_host_name(service):
        yield from _change_host_name(hass, service)

    @asyncio.coroutine
    def execute_command(service):
        yield from _execute_command(hass, service)

    @asyncio.coroutine
    def execute_script(service):
        yield from _execute_script(hass, service)

    @asyncio.coroutine
    def execute_restart(service):
        yield from _execute_restart(hass, service)

    @asyncio.coroutine
    def execute_stop(service):
        yield from _execute_stop(hass, service)

    @asyncio.coroutine
    def key_event(service):
        yield from _key_event(hass, service)

    @asyncio.coroutine
    def scan_network_for_devices(service):
        yield from _scan_network_for_devices(hass, service)

    @asyncio.coroutine
    def scan_network_for_ais_players(service):
        yield from _scan_network_for_ais_players(hass, service)

    @asyncio.coroutine
    def scan_device(service):
        yield from _scan_device(hass, service)

    @asyncio.coroutine
    def scan_ais_player(service):
        yield from _scan_ais_player(hass, service)

    @asyncio.coroutine
    def show_network_devices_info(service):
        yield from _show_network_devices_info(hass, service)

    @asyncio.coroutine
    def led(service):
        yield from _led(hass, service)

    @asyncio.coroutine
    def init_local_sdcard(service):
        yield from _init_local_sdcard(hass, service)

    @asyncio.coroutine
    def flush_logs(service):
        yield from _flush_logs(hass, service)

    @asyncio.coroutine
    def ssh_remote_access(service):
        yield from _ssh_remote_access(hass, service)

    @asyncio.coroutine
    def set_ais_secure_android_id_dom(service):
        yield from _set_ais_secure_android_id_dom(hass, service)

    @asyncio.coroutine
    def hdmi_control_disable(service):
        yield from _hdmi_control_disable(hass, service)

    @asyncio.coroutine
    def hdmi_control_disable(service):
        yield from _hdmi_control_disable(hass, service)

    @asyncio.coroutine
    def change_wm_overscan(service):
        yield from _change_wm_overscan(hass, service)

    @asyncio.coroutine
    def disable_irda_remote(service):
        yield from _disable_irda_remote(hass, service)

    def change_remote_access(service):
        _change_remote_access(hass, service)

    # register services
    hass.services.async_register(DOMAIN, "change_host_name", change_host_name)
    hass.services.async_register(DOMAIN, "execute_command", execute_command)
    hass.services.async_register(DOMAIN, "execute_script", execute_script)
    hass.services.async_register(DOMAIN, "execute_restart", execute_restart)
    hass.services.async_register(DOMAIN, "execute_stop", execute_stop)
    hass.services.async_register(DOMAIN, "key_event", key_event)
    hass.services.async_register(
        DOMAIN, "scan_network_for_devices", scan_network_for_devices
    )
    hass.services.async_register(
        DOMAIN, "scan_network_for_ais_players", scan_network_for_ais_players
    )

    hass.services.async_register(DOMAIN, "scan_device", scan_device)
    hass.services.async_register(DOMAIN, "scan_ais_player", scan_ais_player)
    hass.services.async_register(
        DOMAIN, "show_network_devices_info", show_network_devices_info
    )
    hass.services.async_register(DOMAIN, "led", led)
    hass.services.async_register(
        DOMAIN, "set_ais_secure_android_id_dom", set_ais_secure_android_id_dom
    )
    hass.services.async_register(DOMAIN, "init_local_sdcard", init_local_sdcard)
    hass.services.async_register(DOMAIN, "flush_logs", flush_logs)
    hass.services.async_register(DOMAIN, "change_remote_access", change_remote_access)
    hass.services.async_register(DOMAIN, "ssh_remote_access", ssh_remote_access)
    hass.services.async_register(DOMAIN, "hdmi_control_disable", hdmi_control_disable)
    hass.services.async_register(DOMAIN, "change_wm_overscan", change_wm_overscan)
    hass.services.async_register(DOMAIN, "disable_irda_remote", disable_irda_remote)
    return True


@asyncio.coroutine
def _change_host_name(hass, call):
    if "hostname" not in call.data:
        return
    new_host_name = call.data["hostname"]
    file = "/data/data/pl.sviete.dom/.ais/ais-hostname"
    command = 'echo "net.hostname = ' + new_host_name + '" > ' + file
    import subprocess

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    command = 'su -c "/data/data/pl.sviete.dom/.ais/run_as_root.sh"'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()


def _change_remote_access(hass, call):
    import os

    text = " zdalny dostęp do bramki z Internetu"
    access = hass.states.get("input_boolean.ais_remote_access").state
    gate_id = hass.states.get("sensor.ais_secure_android_id_dom").state
    if access == "on":
        text = "Aktywuje " + text
    else:
        text = "Zatrzymuje " + text

    hass.services.call("ais_ai_service", "say_it", {"text": text})

    if access == "on":
        os.system("pm2 stop tunnel")
        os.system("pm2 delete tunnel")
        cmd = (
            "pm2 start lt --name tunnel --output NULL --error NULL --restart-delay=30000 -- "
            "-h http://paczka.pro -p 8180 -s {}".format(gate_id)
        )
        os.system(cmd)
        os.system("pm2 save")
    else:
        os.system("pm2 stop tunnel")
        os.system("pm2 delete tunnel")
        os.system("pm2 save")


@asyncio.coroutine
def _hdmi_control_disable(hass, call):
    comm = r'su -c "settings put global hdmi_control_enabled 0"'
    os.system(comm)


@asyncio.coroutine
def _change_wm_overscan(hass, call):
    if "value" not in call.data:
        return
    new_value = call.data["value"]
    cl = 0
    ct = 0
    cr = 0
    cb = 0

    try:
        import subprocess

        overscan = ""
        overscan = subprocess.check_output(
            "su -c \"dumpsys display  | grep -o 'overscan.*' | cut -d')' -f1 | rev | cut -d'(' -f1 | rev\"",
            shell=True,
            timeout=10,
        )
        overscan = overscan.decode("utf-8").replace("\n", "")
        if "," in overscan:
            cl = int(overscan.split(",")[0])
            ct = int(overscan.split(",")[1])
            cr = int(overscan.split(",")[2])
            cb = int(overscan.split(",")[3])
    except Exception:
        _LOGGER.warning("Can't get current overscan {}".format(overscan))

    # [reset|LEFT,TOP,RIGHT,BOTTOM]
    if new_value == "reset":
        comm = r'su -c "wm overscan reset"'
    elif new_value == "left":
        comm = (
            r'su -c "wm overscan '
            + str(int(cl) - 3)
            + ","
            + str(ct)
            + ","
            + str(cr)
            + ","
            + str(cb)
            + '"'
        )
    elif new_value == "top":
        comm = (
            r'su -c "wm overscan '
            + str(cl)
            + ","
            + str(int(ct) - 3)
            + ","
            + str(cr)
            + ","
            + str(cb)
            + '"'
        )
    elif new_value == "right":
        comm = (
            r'su -c "wm overscan '
            + str(cl)
            + ","
            + str(ct)
            + ","
            + str(int(cr) - 3)
            + ","
            + str(cb)
            + '"'
        )
    elif new_value == "bottom":
        comm = (
            r'su -c "wm overscan '
            + str(cl)
            + ","
            + str(ct)
            + ","
            + str(cr)
            + ","
            + str(int(cb) - 3)
            + '"'
        )
    elif new_value == "-left":
        comm = (
            r'su -c "wm overscan '
            + str(int(cl) + 3)
            + ","
            + str(ct)
            + ","
            + str(cr)
            + ","
            + str(cb)
            + '"'
        )
    elif new_value == "-top":
        comm = (
            r'su -c "wm overscan '
            + str(cl)
            + ","
            + str(int(ct) + 3)
            + ","
            + str(cr)
            + ","
            + str(cb)
            + '"'
        )
    elif new_value == "-right":
        comm = (
            r'su -c "wm overscan '
            + str(cl)
            + ","
            + str(ct)
            + ","
            + str(int(cr) + 3)
            + ","
            + str(cb)
            + '"'
        )
    elif new_value == "-bottom":
        comm = (
            r'su -c "wm overscan '
            + str(cl)
            + ","
            + str(ct)
            + ","
            + str(cr)
            + ","
            + str(int(cb) + 3)
            + '"'
        )
    else:
        _LOGGER.error("Value for overscan provided {}".format(new_value))
        return
    os.system(comm)


@asyncio.coroutine
def _ssh_remote_access(hass, call):
    access = "on"
    if "access" in call.data:
        access = call.data["access"]
    gate_id = "ssh-" + hass.states.get("sensor.ais_secure_android_id_dom").state
    import os

    if access == "on":
        os.system("pm2 delete ssh-tunnel")
        os.system(
            "pm2 start lt --name ssh-tunnel --restart-delay=30000 -- -h http://paczka.pro -p 8888 -s "
            + gate_id
        )
        os.system("pm2 save")
        _LOGGER.warning(
            "You have SSH access to gate on http://" + gate_id + ".paczka.pro"
        )
    else:
        os.system("pm2 delete ssh-tunnel")
        os.system("pm2 save")


@asyncio.coroutine
def _key_event(hass, call):
    if "key_code" not in call.data:
        return
    key_code = call.data["key_code"]
    import subprocess

    subprocess.Popen(
        "su -c 'input keyevent " + key_code + "'", shell=True, stdout=None, stderr=None
    )


@asyncio.coroutine
def _led(hass, call):
    if "brightness" not in call.data:
        return
    brightness = call.data["brightness"]

    script = str(os.path.dirname(__file__))
    script += "/scripts/led.sh"

    import subprocess

    subprocess.Popen(
        "su -c ' " + script + " " + str(brightness) + "'",
        shell=True,
        stdout=None,
        stderr=None,
    )


@asyncio.coroutine
def _set_ais_secure_android_id_dom(hass, call):
    # the G_AIS_SECURE_ANDROID_ID_DOM is set only in one place ais_global
    hass.states.async_set(
        "sensor.ais_secure_android_id_dom",
        ais_global.get_sercure_android_id_dom(),
        {
            "friendly_name": "Unikalny identyfikator bramki",
            "icon": "mdi:account-card-details",
        },
    )


@asyncio.coroutine
def _init_local_sdcard(hass, call):
    script = str(os.path.dirname(__file__))
    script += "/scripts/init_local_sdcard.sh"
    import subprocess

    subprocess.Popen(script, shell=True, stdout=None, stderr=None)


@asyncio.coroutine
def _execute_command(hass, call):
    command = None
    ret_entity = None
    friendly_name = None
    icon = None

    if "command" not in call.data:
        return
    else:
        command = call.data["command"]
    if "entity_id" in call.data:
        ret_entity = call.data["entity_id"]
    if "friendly_name" in call.data:
        friendly_name = call.data["friendly_name"]
    if "icon" in call.data:
        icon = call.data["icon"]

    import subprocess

    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, err = process.communicate()
    if ret_entity is not None:
        hass.states.async_set(
            ret_entity, output, {"friendly_name": friendly_name, "icon": icon}
        )


@asyncio.coroutine
def _execute_script(hass, call):
    if "script" not in call.data:
        return
    script = call.data["script"]

    if script == "reset_usb.sh":
        # take the full path
        script = str(os.path.dirname(__file__))
        script += "/scripts/reset_usb.sh"
        ais_global.G_USB_INTERNAL_MIC_RESET = True

    import subprocess

    process = subprocess.Popen(script, shell=True, stdout=subprocess.PIPE)
    process.wait()


@asyncio.coroutine
def _execute_restart(hass, call):
    import subprocess

    subprocess.Popen("su -c reboot", shell=True, stdout=None, stderr=None)


@asyncio.coroutine
def _execute_stop(hass, call):
    import subprocess

    subprocess.Popen("su -c 'reboot -p'", shell=True, stdout=None, stderr=None)


@asyncio.coroutine
def _show_network_devices_info(hass, call):
    import homeassistant.components.ais_device_search_mqtt.sensor as dsm

    info = dsm.get_text()
    hass.states.async_set("sensor.network_devices_info_value", "ok", {"text": info})


@asyncio.coroutine
def _scan_device(hass, call):
    url = None
    if "url" in call.data:
        url = call.data["url"]
    url_a = None
    if "url_a" in call.data:
        url_a = call.data["url_a"]
    from requests_futures.sessions import FuturesSession
    from urllib.parse import urlparse
    import homeassistant.components.ais_device_search_mqtt.sensor as dsm

    session = FuturesSession()

    if url is not None:

        def bg_cb(resp, *args, **kwargs):
            try:
                # parse the json storing the result on the response object
                json_ws_resp = resp.json()
                hostname = urlparse(resp.url).hostname
                name = json_ws_resp["Status"]["FriendlyName"][0]
                # ip = json_ws_resp["StatusNET"]["IPAddress"]
                dsm.NET_DEVICES.append("- " + name + ", http://" + hostname)
                info = dsm.get_text()
                hass.states.async_set(
                    "sensor.network_devices_info_value", "", {"text": info}
                )
            except Exception:
                pass

    if url_a is not None:

        def bg_cb_a(resp, *args, **kwargs):
            try:
                # parse the json storing the result on the response object
                json_ws_resp = resp.json()
                model = json_ws_resp["Model"]
                manufacturer = json_ws_resp["Manufacturer"]
                ip = json_ws_resp["IPAddressIPv4"]
                mac = json_ws_resp["MacWlan0"]
                dsm.DOM_DEVICES.append(
                    "- " + model + " " + manufacturer + ", http://" + ip + ":8180"
                )
                info = dsm.get_text()
                hass.states.async_set(
                    "sensor.network_devices_info_value", "", {"text": info}
                )
                # add the device to the speakers lists
                hass.async_add_job(
                    hass.services.async_call(
                        "ais_cloud",
                        "get_players",
                        {
                            "device_name": model + " " + manufacturer + "(" + ip + ")",
                            CONF_IP_ADDRESS: ip,
                            CONF_MAC: mac,
                        },
                    )
                )
            except Exception:
                pass

    if url is not None:
        session.get(url, hooks={"response": bg_cb})
    if url_a is not None:
        session.get(url_a, hooks={"response": bg_cb_a})

    if url is not None:
        hass.async_add_job(
            hass.services.async_call("ais_shell_command", "scan_network_for_devices")
        )


@asyncio.coroutine
def _scan_ais_player(hass, call):
    url = call.data["url"]
    import homeassistant.components.ais_device_search_mqtt.sensor as dsm
    from requests_futures.sessions import FuturesSession

    session = FuturesSession()

    def bg_cb(resp, *args, **kwargs):
        try:
            # parse the json storing the result on the response object
            json_ws_resp = resp.json()
            model = json_ws_resp["Model"]
            manufacturer = json_ws_resp["Manufacturer"]
            ip = json_ws_resp["IPAddressIPv4"]
            ais_gate_client_id = None
            if "ais_gate_client_id" in json_ws_resp:
                ais_gate_client_id = json_ws_resp.get("ais_gate_client_id")
            if ais_gate_client_id is None and "gate_id" in json_ws_resp:
                ais_gate_client_id = json_ws_resp.get("gate_id")
            elif ais_gate_client_id is None and "MacWlan0" in json_ws_resp:
                ais_gate_client_id = json_ws_resp.get("MacWlan0")
            elif ais_gate_client_id is None and "MacEth0" in json_ws_resp:
                ais_gate_client_id = json_ws_resp.get("MacEth0")
            if ais_gate_client_id is None:
                return
            if ais_gate_client_id == ais_global.G_AIS_SECURE_ANDROID_ID_DOM:
                return
            dsm.DOM_DEVICES.append(
                "- " + model + " " + manufacturer + ", http://" + ip + ":8122"
            )
            # add the device to the speakers lists
            hass.async_add_job(
                hass.services.async_call(
                    "ais_cloud",
                    "get_players",
                    {
                        "device_name": model + " " + manufacturer,
                        CONF_IP_ADDRESS: ip,
                        "ais_gate_client_id": ais_gate_client_id,
                    },
                )
            )
        except Exception as e2:
            _LOGGER.error("Exception " + str(e2))

    try:
        future = session.get(url, hooks={"response": bg_cb}, timeout=2, verify=False)
    except Exception:
        pass
    hass.async_add_job(
        hass.services.async_call("ais_shell_command", "scan_network_for_ais_players")
    )


@asyncio.coroutine
def _scan_network_for_ais_players(hass, call):
    import homeassistant.components.ais_device_search_mqtt.sensor as dsm

    global GLOBAL_X
    my_ip = ais_global.get_my_global_ip()
    info = ""
    if GLOBAL_X == 0:
        GLOBAL_X += 1
        # clear the value
        dsm.MQTT_DEVICES = []
        dsm.NET_DEVICES = []
        dsm.DOM_DEVICES = []
        # info
        if ais_global.G_AIS_START_IS_DONE:
            yield from hass.services.async_call(
                "ais_ai_service", "say_it", {"text": "Wykrywam, to potrwa chwilę..."}
            )
        yield from hass.services.async_call(
            "ais_shell_command", "scan_network_for_ais_players"
        )
    # 256
    elif 0 < GLOBAL_X < 256:
        GLOBAL_X += 1
        # search android devices
        rest_url = "http://{}.{}:8122"
        url = rest_url.format(my_ip.rsplit(".", 1)[0], str(GLOBAL_X))

        yield from hass.services.async_call(
            "ais_shell_command", "scan_ais_player", {"url": url}
        )
    else:
        GLOBAL_X = 0
        # the search is done


@asyncio.coroutine
def _scan_network_for_devices(hass, call):
    import homeassistant.components.ais_device_search_mqtt.sensor as dsm

    global GLOBAL_X
    my_ip = ais_global.get_my_global_ip()
    info = ""
    if GLOBAL_X == 0:
        GLOBAL_X += 1
        # clear the value
        dsm.MQTT_DEVICES = []
        dsm.NET_DEVICES = []
        dsm.DOM_DEVICES = []
        hass.states.async_set(
            "sensor.network_devices_info_value",
            "",
            {"text": "wykrywam, to może potrwać minutę..."},
        )

        # send the message to all robots in network
        yield from hass.services.async_call(
            "mqtt", "publish", {"topic": "cmnd/dom/status", "payload": 0}
        )
        # fix for new robots, Tasmota 6.4.0
        yield from hass.services.async_call(
            "mqtt", "publish", {"topic": "dom/cmnd/status", "payload": 0}
        )
        # disco
        yield from hass.services.async_call(
            "mqtt", "publish", {"topic": "dom/cmnd/SetOption19", "payload": 1}
        )

        yield from hass.services.async_call(
            "ais_shell_command", "scan_network_for_devices"
        )
    # 256
    elif 0 < GLOBAL_X < 256:
        GLOBAL_X += 1
        rest_url = "http://{}.{}/cm?cmnd=status"
        url = rest_url.format(my_ip.rsplit(".", 1)[0], str(GLOBAL_X))
        info = "Sprawdzam " + my_ip.rsplit(".", 1)[0]
        info += "." + str(GLOBAL_X) + "\n"
        info += dsm.get_text()
        hass.states.async_set("sensor.network_devices_info_value", "", {"text": info})

        # search android devices
        rest_url_a = "http://{}.{}:8122"
        url_a = rest_url_a.format(my_ip.rsplit(".", 1)[0], str(GLOBAL_X))

        yield from hass.services.async_call(
            "ais_shell_command", "scan_device", {"url": url, "url_a": url_a}
        )

    else:
        GLOBAL_X = 0
        hass.states.async_set(
            "sensor.network_devices_info_value", "", {"text": dsm.get_text()}
        )
        yield from hass.services.async_call(
            "ais_ai_service", "say_it", {"text": dsm.get_text_to_say()}
        )


@asyncio.coroutine
def _flush_logs(hass, call):
    import os

    # pm2
    os.system("pm2 flush")
    os.system("rm /data/data/pl.sviete.dom/files/home/.pm2/logs/*.log")

    # pip cache
    os.system("rm -rf /data/data/pl.sviete.dom/files/home/.cache/pip")
    # recorder.purge if recorder exists
    if hass.services.has_service("recorder", "purge"):
        yield from hass.services.async_call(
            "recorder", "purge", {"keep_days": 3, "repack": True}
        )


@asyncio.coroutine
def _disable_irda_remote(hass, call):
    # aml_keypad -> event0 irda remote
    comm = r'su -c "rm -rf /dev/input/event0"'
    os.system(comm)
    # cec_input -> event2 hdmi cec
    comm = r'su -c "rm -rf /dev/input/event2"'
    os.system(comm)
    # gpio_keypad -> event0 - button behind the AV port can be used it in the future :)
