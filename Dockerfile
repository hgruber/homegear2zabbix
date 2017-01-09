from python:2.7-alpine

RUN pip install py-zabbix paho-mqtt requests
ADD homegear2zabbix.py /homegear2zabbix.py
ENTRYPOINT ["python", "/homegear2zabbix.py"]
