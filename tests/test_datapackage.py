from typeable import capture, typecast
from typeable.schemas.datapackage import DataPackage, DataPackage1, DataPackage2


def test_v1():
    data = {
        "name": "geocsv",
        "title": "Geocsv",
        "resources": [
            {
                "path": "data/geo.csv",
                "name": "geo",
                "format": "csv",
                "mediatype": "text/csv",
                "encoding": "ISO-8859-1",
                "dialect": {"delimiter": ",", "quoteChar": '"'},
                "schema": {
                    "fields": [
                        {"name": "lon", "type": "number", "format": "default"},
                        {"name": "lat", "type": "number", "format": "default"},
                        {"name": "geopoint", "type": "geopoint", "format": "default"},
                        {"name": "label", "type": "string", "format": "default"},
                    ],
                    "missingValues": [""],
                },
            }
        ],
        "licenses": [
            {
                "name": "ODC-PDDL",
                "path": "http://opendatacommons.org/licenses/pddl/",
                "title": "Open Data Commons Public Domain Dedication and License",
            }
        ],
    }
    try:
        with capture() as error:
            schema = typecast(DataPackage, data)
    except TypeError:
        print(error.location)
        raise
    assert isinstance(schema, DataPackage1)


def test_v2():
    data = {
        "$schema": "https://datapackage.org/profiles/2.0/datapackage.json",
        "id": "{}",
        "name": "ismartcity-facility-{}",
        "title": "스마트 시설",
        "licenses": [{"path": "https://www.kogl.or.kr/info/licenseType1.do"}],
        "version": "1.0",
        "created": "2025-08-26T14:00:00Z",
        "resources": [
            {
                "$schema": "https://datapackage.org/profiles/2.0/dataresource.json",
                "name": "facility",
                "path": "facility.csv",
                "title": "시설",
                "format": "csv",
                "type": "table",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": {
                    "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
                    "fields": [{"name": "id", "type": "string", "format": "uuid"}],
                    "primaryKey": ["id"],
                    "missingValues": [""],
                },
            },
            {
                "$schema": "https://datapackage.org/profiles/2.0/dataresource.json",
                "name": "device",
                "path": "device.csv",
                "title": "장치",
                "format": "csv",
                "type": "table",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": {
                    "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
                    "fields": [
                        {
                            "name": "facilityId",
                            "type": "string",
                            "constraints": {"required": True},
                        },
                        {"name": "id", "type": "string", "format": "uuid"},
                    ],
                    "primaryKey": ["id"],
                    "foreignKeys": [
                        {
                            "fields": ["facilityId"],
                            "reference": {"resource": "facility", "fields": ["id"]},
                        }
                    ],
                    "missingValues": [""],
                },
            },
            {
                "$schema": "https://datapackage.org/profiles/2.0/dataresource.json",
                "name": "FacilityMeta",
                "path": "facility.meta.csv",
                "title": "시설 메타데이터",
                "format": "csv",
                "type": "table",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": {
                    "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
                    "fields": [
                        {"name": "timestamp", "type": "datetime"},
                        {"name": "id", "type": "string"},
                        {
                            "name": "name",
                            "type": "string",
                            "constraints": {"required": True},
                        },
                        {
                            "name": "category",
                            "type": "string",
                            "categories": [
                                "교통/쉼터",
                                "교통/CCTV",
                                "안전/CCTV",
                                "환경/CCTV",
                            ],
                        },
                        {
                            "name": "location",
                            "type": "geopoint",
                            "constraints": {"required": True},
                        },
                        {"name": "elevation", "type": "number"},
                        {
                            "name": "management",
                            "type": "integer",
                            "categories": [
                                {"value": 28000, "label": "인천광역시"},
                                {"value": 28001, "label": "인천경제자유구역청"},
                                {"value": 28002, "label": "인천교통정보센터"},
                                {"value": 28003, "label": "남동산업단지"},
                                {"value": 28110, "label": "중구"},
                                {"value": 28140, "label": "동구"},
                                {"value": 28177, "label": "미추홀구"},
                                {"value": 28185, "label": "연수구"},
                                {"value": 28200, "label": "남동구"},
                                {"value": 28237, "label": "부평구"},
                                {"value": 28245, "label": "계양구"},
                                {"value": 28260, "label": "서구"},
                                {"value": 28710, "label": "강화군"},
                                {"value": 28720, "label": "옹진군"},
                            ],
                        },
                        {"name": "removed", "type": "boolean"},
                    ],
                    "primaryKey": ["timestamp", "id"],
                    "foreignKeys": [
                        {
                            "fields": ["id"],
                            "reference": {"resource": "facility", "fields": ["id"]},
                        }
                    ],
                    "missingValues": [""],
                },
            },
            {
                "$schema": "https://datapackage.org/profiles/2.0/dataresource.json",
                "name": "DeviceMeta",
                "path": "device.meta.csv",
                "title": "장치 공통 메타데이터",
                "format": "csv",
                "type": "table",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": {
                    "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
                    "fields": [
                        {"name": "timestamp", "type": "datetime"},
                        {"name": "id", "type": "string", "format": "uuid"},
                        {
                            "name": "name",
                            "type": "string",
                            "constraints": {"required": True},
                        },
                        {
                            "name": "type",
                            "type": "string",
                            "constraints": {"required": True},
                            "categories": [
                                "AirConditioner",
                                "AirCurtain",
                                "AirQualityDetector",
                                "BidirectionalPeopleCounter",
                                "BrineSprayer",
                                "Camera",
                                "Door",
                                "Dumb",
                                "PTHSensor",
                                "Switch",
                                "ThermoHygrometer",
                            ],
                        },
                        {"name": "mutables", "type": "list", "itemType": "string"},
                        {"name": "removed", "type": "boolean"},
                    ],
                    "primaryKey": ["timestamp", "id"],
                    "foreignKeys": [
                        {
                            "fields": ["id"],
                            "reference": {"resource": "device", "fields": ["id"]},
                        }
                    ],
                    "missingValues": [""],
                },
            },
            {
                "$schema": "https://datapackage.org/profiles/2.0/dataresource.json",
                "name": "AirConditioner",
                "path": "airconditioner.csv",
                "title": "에어컨",
                "format": "csv",
                "type": "table",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": {
                    "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
                    "fields": [
                        {"name": "timestamp", "type": "datetime"},
                        {"name": "id", "type": "string"},
                        {
                            "name": "status",
                            "type": "boolean",
                            "constraints": {"required": True},
                        },
                        {"name": "power", "type": "boolean"},
                        {
                            "name": "mode",
                            "type": "string",
                            "categories": ["auto", "fan", "cool", "heat", "dry"],
                        },
                        {
                            "name": "fanSpeed",
                            "type": "string",
                            "categories": ["auto", "low", "mid", "high"],
                        },
                        {"name": "desiredTemperature", "type": "number"},
                        {"name": "temperature", "type": "number"},
                    ],
                    "primaryKey": ["timestamp", "id"],
                    "foreignKeys": [
                        {
                            "fields": ["id"],
                            "reference": {"resource": "device", "fields": ["id"]},
                        }
                    ],
                    "missingValues": [""],
                },
            },
            {
                "$schema": "https://datapackage.org/profiles/2.0/dataresource.json",
                "name": "AirCurtain",
                "path": "aircurtain.csv",
                "title": "에어 커튼",
                "format": "csv",
                "type": "table",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": {
                    "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
                    "fields": [
                        {"name": "timestamp", "type": "datetime"},
                        {"name": "id", "type": "string"},
                        {
                            "name": "status",
                            "type": "boolean",
                            "constraints": {"required": True},
                        },
                        {"name": "power", "type": "boolean"},
                        {
                            "name": "speed",
                            "type": "string",
                            "categories": ["low", "mid", "high"],
                        },
                        {"name": "ion", "type": "boolean"},
                    ],
                    "primaryKey": ["timestamp", "id"],
                    "foreignKeys": [
                        {
                            "fields": ["id"],
                            "reference": {"resource": "device", "fields": ["id"]},
                        }
                    ],
                    "missingValues": [""],
                },
            },
            {
                "$schema": "https://datapackage.org/profiles/2.0/dataresource.json",
                "name": "AirQualityDetectorMeta",
                "path": "airqualitydetector.meta.csv",
                "title": "대기질 측정기 제원 정보",
                "format": "csv",
                "type": "table",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": {
                    "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
                    "fields": [
                        {"name": "timestamp", "type": "datetime"},
                        {"name": "id", "type": "string"},
                        {"name": "indoor", "type": "boolean"},
                    ],
                    "primaryKey": ["id"],
                    "foreignKeys": [
                        {
                            "fields": ["id"],
                            "reference": {"resource": "device", "fields": ["id"]},
                        }
                    ],
                    "missingValues": [""],
                },
            },
            {
                "$schema": "https://datapackage.org/profiles/2.0/dataresource.json",
                "name": "AirQualityDetector",
                "path": "airqualitydetector.csv",
                "title": "대기질 측정기 상태 정보",
                "format": "csv",
                "type": "table",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": {
                    "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
                    "fields": [
                        {"name": "timestamp", "type": "datetime"},
                        {"name": "id", "type": "string"},
                        {
                            "name": "status",
                            "type": "boolean",
                            "constraints": {"required": True},
                        },
                        {"name": "power", "type": "boolean"},
                        {"name": "so2", "type": "number"},
                        {"name": "co", "type": "number"},
                        {"name": "o3", "type": "number"},
                        {"name": "no2", "type": "number"},
                        {"name": "pm25", "type": "number"},
                        {"name": "pm10", "type": "number"},
                    ],
                    "primaryKey": ["timestamp", "id"],
                    "foreignKeys": [
                        {
                            "fields": ["id"],
                            "reference": {"resource": "device", "fields": ["id"]},
                        }
                    ],
                    "missingValues": [""],
                },
            },
            {
                "$schema": "https://datapackage.org/profiles/2.0/dataresource.json",
                "name": "BidirectionalPeopleCounter",
                "path": "bidirectionalpeoplecounter.csv",
                "title": "양방향 인원 계수기",
                "format": "csv",
                "type": "table",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": {
                    "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
                    "fields": [
                        {"name": "timestamp", "type": "datetime"},
                        {"name": "id", "type": "string"},
                        {
                            "name": "status",
                            "type": "boolean",
                            "constraints": {"required": True},
                        },
                        {"name": "power", "type": "boolean"},
                        {
                            "name": "inCount",
                            "type": "integer",
                            "constraints": {"required": True},
                        },
                        {
                            "name": "outCount",
                            "type": "integer",
                            "constraints": {"required": True},
                        },
                    ],
                    "primaryKey": ["timestamp", "id"],
                    "foreignKeys": [
                        {
                            "fields": ["id"],
                            "reference": {"resource": "device", "fields": ["id"]},
                        }
                    ],
                    "missingValues": [""],
                },
            },
            {
                "$schema": "https://datapackage.org/profiles/2.0/dataresource.json",
                "name": "BrineSprayer",
                "path": "brinesprayer.csv",
                "title": "염수분사기",
                "format": "csv",
                "type": "table",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": {
                    "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
                    "fields": [
                        {"name": "timestamp", "type": "datetime"},
                        {"name": "id", "type": "string"},
                        {
                            "name": "status",
                            "type": "boolean",
                            "constraints": {"required": True},
                        },
                        {"name": "power", "type": "boolean"},
                        {"name": "run", "type": "boolean"},
                        {"name": "level", "type": "number"},
                    ],
                    "primaryKey": ["timestamp", "id"],
                    "foreignKeys": [
                        {
                            "fields": ["id"],
                            "reference": {"resource": "device", "fields": ["id"]},
                        }
                    ],
                    "missingValues": [""],
                },
            },
            {
                "$schema": "https://datapackage.org/profiles/2.0/dataresource.json",
                "name": "CameraMeta",
                "path": "camera.meta.csv",
                "title": "장치 제원 정보",
                "format": "csv",
                "type": "table",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": {
                    "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
                    "fields": [
                        {"name": "timestamp", "type": "datetime"},
                        {"name": "id", "type": "string"},
                        {
                            "name": "objective",
                            "type": "string",
                            "categories": [
                                {"value": "AVI", "label": "차량번호인식"},
                                {"value": "CPV", "label": "방범"},
                                {"value": "CTD", "label": "쓰레기투기"},
                                {"value": "MRK", "label": "시장"},
                                {"value": "MTP", "label": "다목적"},
                                {"value": "PET", "label": "불법주정차"},
                                {"value": "PRK", "label": "공원"},
                                {"value": "UDF", "label": "미분류"},
                            ],
                        },
                        {"name": "installDate", "type": "date"},
                    ],
                    "primaryKey": ["id"],
                    "foreignKeys": [
                        {
                            "fields": ["id"],
                            "reference": {"resource": "device", "fields": ["id"]},
                        }
                    ],
                    "missingValues": [""],
                },
            },
            {
                "$schema": "https://datapackage.org/profiles/2.0/dataresource.json",
                "name": "Door",
                "path": "door.csv",
                "title": "문",
                "format": "csv",
                "type": "table",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": {
                    "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
                    "fields": [
                        {"name": "timestamp", "type": "datetime"},
                        {"name": "id", "type": "string"},
                        {
                            "name": "status",
                            "type": "boolean",
                            "constraints": {"required": True},
                        },
                        {"name": "power", "type": "boolean"},
                        {"name": "open", "type": "boolean"},
                        {"name": "lock", "type": "boolean"},
                    ],
                    "primaryKey": ["timestamp", "id"],
                    "foreignKeys": [
                        {
                            "fields": ["id"],
                            "reference": {"resource": "device", "fields": ["id"]},
                        }
                    ],
                    "missingValues": [""],
                },
            },
            {
                "$schema": "https://datapackage.org/profiles/2.0/dataresource.json",
                "name": "PTHSensorMeta",
                "path": "pthsensor.meta.csv",
                "title": "기압, 온도, 습도 센서 제원 정보",
                "format": "csv",
                "type": "table",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": {
                    "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
                    "fields": [
                        {"name": "timestamp", "type": "datetime"},
                        {"name": "id", "type": "string"},
                        {"name": "indoor", "type": "boolean"},
                    ],
                    "primaryKey": ["id"],
                    "foreignKeys": [
                        {
                            "fields": ["id"],
                            "reference": {"resource": "device", "fields": ["id"]},
                        }
                    ],
                    "missingValues": [""],
                },
            },
            {
                "$schema": "https://datapackage.org/profiles/2.0/dataresource.json",
                "name": "PTHSensor",
                "path": "pthsensor.csv",
                "title": "기압, 온도, 습도 센서 상태 정보",
                "format": "csv",
                "type": "table",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": {
                    "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
                    "fields": [
                        {"name": "timestamp", "type": "datetime"},
                        {"name": "id", "type": "string"},
                        {
                            "name": "status",
                            "type": "boolean",
                            "constraints": {"required": True},
                        },
                        {"name": "power", "type": "boolean"},
                        {"name": "pressure", "type": "number"},
                        {"name": "temperature", "type": "number"},
                        {"name": "humidity", "type": "number"},
                    ],
                    "primaryKey": ["timestamp", "id"],
                    "foreignKeys": [
                        {
                            "fields": ["id"],
                            "reference": {"resource": "device", "fields": ["id"]},
                        }
                    ],
                    "missingValues": [""],
                },
            },
            {
                "$schema": "https://datapackage.org/profiles/2.0/dataresource.json",
                "name": "Switch",
                "path": "switch.csv",
                "title": "스위치",
                "format": "csv",
                "type": "table",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": {
                    "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
                    "fields": [
                        {"name": "timestamp", "type": "datetime"},
                        {"name": "id", "type": "string"},
                        {
                            "name": "status",
                            "type": "boolean",
                            "constraints": {"required": True},
                        },
                        {"name": "power", "type": "boolean"},
                    ],
                    "primaryKey": ["timestamp", "id"],
                    "foreignKeys": [
                        {
                            "fields": ["id"],
                            "reference": {"resource": "device", "fields": ["id"]},
                        }
                    ],
                    "missingValues": [""],
                },
            },
            {
                "$schema": "https://datapackage.org/profiles/2.0/dataresource.json",
                "name": "ThermoHygrometerMeta",
                "path": "thermohygrometer.meta.csv",
                "title": "온습도계 제원 정보",
                "format": "csv",
                "type": "table",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": {
                    "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
                    "fields": [
                        {"name": "timestamp", "type": "datetime"},
                        {"name": "id", "type": "string"},
                        {"name": "indoor", "type": "boolean"},
                    ],
                    "primaryKey": ["id"],
                    "foreignKeys": [
                        {
                            "fields": ["id"],
                            "reference": {"resource": "device", "fields": ["id"]},
                        }
                    ],
                    "missingValues": [""],
                },
            },
            {
                "$schema": "https://datapackage.org/profiles/2.0/dataresource.json",
                "name": "ThermoHygrometer",
                "path": "thermohygrometer.csv",
                "title": "온습도계 상태 정보",
                "format": "csv",
                "type": "table",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": {
                    "$schema": "https://datapackage.org/profiles/2.0/tableschema.json",
                    "fields": [
                        {"name": "timestamp", "type": "datetime"},
                        {"name": "id", "type": "string"},
                        {
                            "name": "status",
                            "type": "boolean",
                            "constraints": {"required": True},
                        },
                        {"name": "power", "type": "boolean"},
                        {"name": "temperature", "type": "number"},
                        {"name": "humidity", "type": "number"},
                    ],
                    "primaryKey": ["timestamp", "id"],
                    "foreignKeys": [
                        {
                            "fields": ["id"],
                            "reference": {"resource": "device", "fields": ["id"]},
                        }
                    ],
                    "missingValues": [""],
                },
            },
        ],
    }
    try:
        with capture() as error:
            schema = typecast(DataPackage, data)
    except TypeError:
        print(error.location)
        raise
    assert isinstance(schema, DataPackage2)
