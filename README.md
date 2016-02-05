# homegear2zabbix
push homegear readings to zabbix

This tiny python script is run as a permanent service. It connects to a mosquitto server that is fed by homegear. All sensor readings are passed on to a zabbix server. If devices were unknown to zabbix homegear will be queried and all devices will be discovered automatically by low level discovery rules.
This way you will get timeseries for all readings broadcast by every device connected to homegear.
