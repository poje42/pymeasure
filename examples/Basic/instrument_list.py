# from instrument_register import instrument_t
from typing import NamedTuple


class instrument_t(NamedTuple):
    manufacturer: str
    model: str
    serialId: str
    category: list
    adr: str
    settings: list
    driver: str


# inst = {
#     # Define all instruments
#     'None': instrument_t('', '', ['DMM', 'PSU', 'PSU_DMM', 'RF_Gen', 'Temp_Chamber', 'Temp_Meter'], '', [], ''),
#     # LAB
#     'LAB002':   instrument_t("", "",           ['RF_Gen'], "GPIB::19", [], "agilent.AgilentE4438C"),
#     'UTV113':   instrument_t("", "", "MY59189002", ['DMM', 'PSU_DMM'], "COM?", [], "agilent.AgilentU1252B"),
#     'UTV115':   instrument_t("", "", "MY60420025", ['DMM', 'PSU_DMM'], "COM?", [], "agilent.AgilentU1252B"),
#     'UTV116':   instrument_t("", "", "MY59310014", ['DMM', 'PSU_DMM'], "COM?", [], "agilent.AgilentU1252B"),
#     'UTV121:1': instrument_t("", "", "",           ['PSU', 'PSU_DMM'], 'TCPIP0::192.168.32.30',{'channel':1},"keysight.KeysightE36313A"),
#     'UTV121:2': instrument_t("", "", "",           ['PSU', 'PSU_DMM'], 'TCPIP0::192.168.32.30',{'channel':2},"keysight.KeysightE36313A"),
#     'UTV121:3': instrument_t("", "", "",           ['PSU', 'PSU_DMM'], 'TCPIP0::192.168.32.30',{'channel':3},"keysight.KeysightE36313A"),
# }

instrument_dict = {
    # Define all instruments
    'None':     instrument_t('', '', '', ['DMM', 'PSU', 'PSU_DMM', 'DC_Load', 'DC_Load_DMM', 'RF_Gen', 'Temp_Chamber', 'Temp_Meter', 'Cntr'], '', [], ''),
    # LAB
    'ID019':     instrument_t("", "", "",         ['DC_Load', 'DC_Load_DMM'], "GPIB::1",
                              [], "pymeasure.instruments.hp.HP6050A"),
    'ID021':     instrument_t("", "", "",         ['RF_Gen'], "GPIB::3",
                              [], "pymeasure.instruments.hp.HP6032A"),
    'ID022:107': instrument_t("HEWLETT-PACKARD", "34970A", "",         ['PSU_DMM'], "GPIB::9",
                              {'channel': 107}, "pymeasure.instruments.agilent.Agilent34970A"),
    'ID022:111': instrument_t("HEWLETT-PACKARD", "34970A", "",         ['DC_Load_DMM'], "GPIB::9",
                              {'channel': 111}, "pymeasure.instruments.agilent.Agilent34970A"),
    'ID022:112': instrument_t("HEWLETT-PACKARD", "34970A", "",         ['DC_LOad_DMM'], "GPIB::9",
                              {'channel': 112}, "pymeasure.instruments.agilent.Agilent34970A"),
    'ID022:110': instrument_t("HEWLETT-PACKARD", "34970A", "",         ['DMM'], "GPIB::9",
                              {'channel': 110}, "pymeasure.instruments.agilent.Agilent34970A"),
    'ID022:113': instrument_t("HEWLETT-PACKARD", "34970A", "",         ['DMM'], "GPIB::9",
                              {'channel': 113}, "pymeasure.instruments.agilent.Agilent34970A"),
    'ID022:114': instrument_t("HEWLETT-PACKARD", "34970A", "",         ['DMM'], "GPIB::9",
                              {'channel': 114}, "pymeasure.instruments.agilent.Agilent34970A"),
    'ID022:120': instrument_t("HEWLETT-PACKARD", "34970A", "",         ['DMM'], "GPIB::9",
                              {'channel': 120}, "pymeasure.instruments.agilent.Agilent34970A"),
    'ID022:121': instrument_t("HEWLETT-PACKARD", "34970A", "",         ['DMM'], "GPIB::9",
                              {'channel': 121}, "pymeasure.instruments.agilent.Agilent34970A"),
    'ID022:122': instrument_t("HEWLETT-PACKARD", "34970A", "",         ['DMM'], "GPIB::9",
                              {'channel': 122}, "pymeasure.instruments.agilent.Agilent34970A"),
    'ID022:115': instrument_t("HEWLETT-PACKARD", "34970A", "",         ['DMM'], "GPIB::9",
                              {'channel': 115}, "pymeasure.instruments.agilent.Agilent34970A"),
    'ID022:116': instrument_t("HEWLETT-PACKARD", "34970A", "",         ['DMM'], "GPIB::9",
                              {'channel': 116}, "pymeasure.instruments.agilent.Agilent34970A"),
    'ID034':     instrument_t("HEWLETT-PACKARD", "53131A", "",         ['Cntr'], "GPIB::10",
                              [], "pymeasure.instruments.hp.HP53131A"),
    'ID017':     instrument_t("HEWLETT-PACKARD", "34401A", "",         ['DMM'], "GPIB::22",
                              {}, "pymeasure.instruments.agilent.Agilent34401A"),
    'ID030:1':   instrument_t("", "", "",         ['PSU'], "TCPIP0::192.168.1.85",
                              {'channel': 'ch_1'}, "pymeasure.instruments.keysight.KeysightE36312A"),
    'ID030:2':   instrument_t("", "", "",         ['PSU'], "TCPIP0::192.168.1.85",
                              {'channel': 'ch_2'}, "pymeasure.instruments.keysight.KeysightE36312A"),
    'ID030:3':   instrument_t("", "", "",         ['PSU'], "TCPIP0::192.168.1.85",
                              {'channel': 'ch_3'}, "pymeasure.instruments.keysight.KeysightE36312A"),
}
