
SAMPLE_POWER_RESPONSE = {
	"instandby": False,
	"result": True
}

SAMPLE_VOL13_RESPONSE = {
	"current": 13,
	"message": "Volume set to 13",
	"result": True,
	"ismute": False
}

SAMPLE_CHANNEL_CHANGE_RESPONSE = {
	"message": "RC command '403' has been issued",
	"result": True
}

SAMPLE_MUTE_RESPONSE = {
	"current": 50,
	"message": "Mute toggled",
	"result": True,
	"ismute": True
}

SAMPLE_EMPTY_TIMER_LIST = {
	"timers": [],
	"result": True,
	"locations": [
		"/media/hdd/movie/"
	]
}

SAMPLE_EMPTY_EPG_SEARCH = {
	"events": [],
	"result": True
}

SAMPLE_STANDBY_STATUS_INFO = {
	"inStandby": "true",
	"currservice_begin": "",
	"muted": True,
	"isRecording": "false",
	"volume": 50,
	"currservice_fulldescription": "N/A",
	"currservice_name": "N/A",
	"currservice_filename": "",
	"transcoding": False,
	"currservice_end": "",
	"currservice_description": ""
}

SAMPLE_STATUS_INFO = {
	"inStandby": False,
	"currservice_begin": "21:00",
	"muted": True,
	"isRecording": "false",
	"currservice_station": "ITV2",
	"currservice_serviceref": "1:0:1:2756:7FC:2:11A0000:0:0:0:",
	"volume": 52,
	"currservice_fulldescription": "New: Family Guy\n21:00 - 21:30\n\n",
	"currservice_name": "New: Family Guy",
	"currservice_filename": "",
	"transcoding": False,
	"currservice_end": "21:30",
	"currservice_description": "Veteran Guy: Peter and the gang are forced to join the Coast Guard after getting caught pretending to be military veterans. S16 Ep14"
}

SAMPLE_ABOUT = {
  "info": {
    "tuners": [
      {
        "rec": "",
        "live": "",
        "type": "BCM7346 (internal) (DVB-S2)",
        "name": "Tuner A"
      },
      {
        "rec": "",
        "live": "",
        "type": "BCM7346 (internal) (DVB-S2)",
        "name": "Tuner B"
      },
      {
        "rec": "",
        "live": "",
        "type": "Si2168 (DVB-T2)",
        "name": "Tuner C"
      }
    ],
    "ifaces": [
      {
        "linkspeed": "1 GBit/s",
        "gw": "192.168.1.1",
        "friendlynic": "Broadcom Gigabit Ethernet",
        "ip": "192.168.1.1",
        "mac": "00:00:00:00:00:00",
        "name": "eth0",
        "v4prefix": 24,
        "ipv4method": "DHCP",
        "mask": "255.255.255.0",
        "ipmethod": "SLAAC",
        "firstpublic": "null",
        "ipv6": "none/IPv4-only network",
        "dhcp": "true"
      }
    ],
    "machinebuild": "mockmachine",
    "mem1": "321892 kB",
    "mem3": "145248 kB free / 321892 kB total",
    "mem2": "145248 kB",
    "oever": "OE-Alliance 4.0",
    "transcoding": False,
    "fp_version": None,
    "kernelver": "4.10.6",
    "kinopoisk": False,
    "uptime": "103d 21:11",
    "enigmaver": "2017-10-23",
    "driverdate": "20170413",
    "imagever": "6.0.0",
    "friendlychipsetdescription": "Chipset",
    "shares": [],
    "friendlyimagedistro": "OpenATV",
    "brand": "Mock",
    "boxtype": "mocker1",
    "imagedistro": "openatv",
    "EX": "",
    "webifver": "OWIF 1.2.7",
    "hdd": [
      {
        "capacity": "488 MB",
        "labelled_capacity": "512 MB",
        "friendlycapacity": "480 MB free / 488 MB (\"512 MB\") total",
        "mount": "/media/mmcblk0p1",
        "free": "480 MB",
        "model": "SD512"
      },
      {
        "capacity": "483 MB",
        "labelled_capacity": "507 MB",
        "friendlycapacity": "480 MB free / 483 MB (\"507 MB\") total",
        "mount": "/media/mmcblk0p1",
        "free": "480 MB",
        "model": "-?-"
      }
    ],
    "chipset": "bcm7356",
    "model": "M1",
    "friendlychipsettext": "Broadcom 7356"
  },
  "service": {
    "onid": 2,
    "txtpid": 2392,
    "pmtpid": 265,
    "name": "ITV2+1",
    "tsid": 2053,
    "pcrpid": 3352,
    "sid": 10165,
    "namespace": 18481152,
    "height": 576,
    "apid": 3353,
    "width": 704,
    "result": True,
    "aspect": 3,
    "provider": "BSkyB",
    "ref": "1:0:1:27B5:805:2:11A0000:0:0:0:",
    "vpid": 3352,
    "iswidescreen": True
	}
}