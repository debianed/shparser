#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

import json
import os
from jpath_finder.jpath_parser import find
from lxml import etree


class ConfigParser:
    def __init__(self, data_path):
        self._data_dir = os.path.join(os.path.dirname(__file__), data_path)
        self._tms = []
        self._hw = ''
        self._c_channel = ''
        self._c_rtu = ''
        self._c_signal = ''

    def __del__(self):
        pass

    def save_data(self, pretty=False):
        data = json.dumps(self._tms, indent=2, sort_keys=False, ensure_ascii=not pretty)
        with open(os.path.join(self._data_dir, 'tms.json'), "w", encoding="utf-8") as file:
            file.write(data)

    def load_data(self):
        self._hw = ''
        with open(os.path.join(self._data_dir, 'tms.json'), "rb") as file:
            self._tms = json.load(file)

    @property
    def tms(self):
        return self._tms

    def parse(self):
        with open(os.path.join(self._data_dir, 'hw.cfg'), "rb") as file:
            hw_data = file.read()
        self._hw = etree.fromstring(hw_data)

        with open(os.path.join(self._data_dir, 'tms.cfg'), "rb") as file:
            tms_data = file.read()

        tms_root = etree.fromstring(tms_data)
        if tms_root.tag.upper() == 'InterfaceSSHConfig'.upper():
            for chnl in tms_root.getchildren():
                if chnl.tag.upper() == 'CHANNEL':
                    self.__add_channel__(chnl)
        self._hw = ''

    def __add_channel__(self, data):
        self._c_channel = data.get('ChannelNum', default='').strip()
        self._tms.append(
            {
                'type': 'channel',
                'enabled': True if data.get('enab', default='1').strip() == '1' else False,
                'id': data.get('ChannelNum', default='').strip(),
                'name': data.get('ChannelName', default='').strip(),
                'external': data.get('ChannelExternal', default='').strip(),
                'extchn': data.get('ChannelExtChn', default='').strip(),
                'extmachine': data.get('ChannelExtMachine', default='').strip(),
                'extserver': data.get('ChannelExtServer', default='').strip(),
                'rtu': []
            }
        )

        for rtu in data.getchildren():
            if rtu.tag.upper() == 'RTU':
                self.__add_rtu__(rtu)

    def __add_rtu__(self, data):
        self._c_rtu = data.get('RTUNum', default='').strip()
        self._tms[len(self._tms) - 1]['rtu'].append(
            {
                'type': 'rtu',
                'enabled': True if data.get('enab', default='1').strip() == '1' else False,
                'id': data.get('RTUNum', default='').strip(),
                'name': data.get('RTUName', default='').strip(),
                'analogs': [],
                'statuses': []
            }
        )

        for tm in data.getchildren():
            if tm.tag.upper() == 'ANALOGS':
                self.__add_analogs__(tm)
            if tm.tag.upper() == 'STATUSES':
                self.__add_statuses__(tm)

    def __add_analogs__(self, data):
        last_channel = len(self._tms) - 1
        last_rtu = len(self._tms[last_channel]['rtu']) - 1
        self._tms[last_channel]['rtu'][last_rtu]['analogs'].append(
            {
                'type': 'analogs',
                'enabled': True if data.get('enab', default='1').strip() == '1' else False,
                'name': data.get('AnaDesc', default='').strip(),
                'data': []
            }
        )

        last_analogs = len(self._tms[last_channel]['rtu'][last_rtu]['analogs']) - 1
        for atm in data.getchildren():
            if atm.tag.upper() == 'ANALOG':
                self._c_signal = atm.get('AnalogPoint', default='').strip()
                hwi = self.__get_hw_info__(tp='an')
                self._tms[last_channel]['rtu'][last_rtu]['analogs'][last_analogs]['data'].append(
                    {
                        'type': 'analog',
                        'enabled': True if atm.get('enab', default='1').strip() == '1' else False,
                        'id': atm.get('AnalogPoint', default='').strip(),
                        'name': atm.get('AnalogName', default='').strip(),
                        'units': atm.get('AnalogUnits', default='').strip(),
                        'formattotal': atm.get('AnalogFormatTotal', default='').strip(),
                        'formatpoint': atm.get('AnalogFormatPoint', default='').strip(),
                        'mult': atm.get('AnalogMult', default='').strip(),
                        'shift': atm.get('AnalogShift', default='').strip(),
                        'nozero': atm.get('AnalogNoZero', default='').strip(),
                        'expr': atm.get('AnalogExpr', default='').strip(),
                        'formatvalue': atm.get('AnalogFormatValue', default='').strip(),
                        'reserve': atm.get('AnalogReserve', default='').strip(),
                        'filt': atm.get('AnalogFilt', default='').strip(),
                        'fhi': atm.get('AnalogFHi', default='').strip(),
                        'flo': atm.get('AnalogFLo', default='').strip(),
                        'stream': atm.get('AnalogStream', default='').strip(),
                        'outdate': atm.get('AnalogOutdate', default='').strip(),
                        're': self._tms[last_channel]['enabled'] and self._tms[last_channel]['rtu'][last_rtu][
                            'enabled'] and self._tms[last_channel]['rtu'][last_rtu]['analogs'][last_analogs][
                                  'enabled'] and (True if atm.get('enab', default='1').strip() == '1' else False),
                        'hw': hwi
                    }
                )

    def __add_statuses__(self, data):
        last_channel = len(self._tms) - 1
        last_rtu = len(self._tms[last_channel]['rtu']) - 1
        self._tms[last_channel]['rtu'][last_rtu]['statuses'].append(
            {
                'type': 'statuses',
                'enabled': True if data.get('enab', default='1').strip() == '1' else False,
                'name': data.get('StaDesc', default='').strip(),
                'data': []
            }
        )

        last_statuses = len(self._tms[last_channel]['rtu'][last_rtu]['statuses']) - 1
        for stm in data.getchildren():
            if stm.tag.upper() == 'STATUS':
                self._c_signal = stm.get('StatusPoint', default='').strip()
                hwi = self.__get_hw_info__()
                self._tms[last_channel]['rtu'][last_rtu]['statuses'][last_statuses]['data'].append(
                    {
                        'type': 'status',
                        'enabled': True if stm.get('enab', default='1').strip() == '1' else False,
                        'id': stm.get('StatusPoint', default='').strip(),
                        'name': stm.get('StatusName', default='').strip(),
                        'invert': stm.get('StatusInvert', default='').strip(),
                        'retro': stm.get('StatusRetro', default='').strip(),
                        'signal': stm.get('StatusSignal', default='').strip(),
                        'imp': stm.get('StatusImp', default='').strip(),
                        'expr': stm.get('StatusExpr', default='').strip(),
                        'controladr': stm.get('StatusControlADR', default='').strip(),
                        'reserve': stm.get('StatusReserve', default='').strip(),
                        'stream': stm.get('StatusStream', default='').strip(),
                        'outdate': stm.get('StatusOutdate', default='').strip(),
                        're': self._tms[last_channel]['enabled'] and self._tms[last_channel]['rtu'][last_rtu][
                            'enabled'] and self._tms[last_channel]['rtu'][last_rtu]['statuses'][last_statuses][
                                  'enabled'] and (True if stm.get('enab', default='1').strip() == '1' else False),
                        'hw': hwi
                    }
                )

    def __get_hw_info__(self, tp='st'):
        hwinfo = {'re': True, 'enabled': True, 'address': ''}

        if tp == 'st':
            nodes = self._hw.xpath("//*[@iec101PVStTmsChn='" + str(self._c_channel) + "' and @iec101PVStTmsRtu='" + str(
                self._c_rtu) + "' and @iec101PVStTmsPt='" + str(self._c_signal) + "']/ancestor-or-self::*")
        else:
            nodes = self._hw.xpath(
                ".//*[@iec101SVAnfTmsChn='" + str(self._c_channel) + "' and @iec101SVAnfTmsRtu='" + str(
                    self._c_rtu) + "' and @iec101SVAnfTmsPt='" + str(self._c_signal) + "']/ancestor-or-self::*")

        if len(nodes) > 0:
            for node in nodes:
                if hwinfo['re']:
                    hwinfo['re'] = True if node.get('enab', default='1').strip() == '1' else False
                if (node.tag.upper() == 'iec101PrimSt'.upper() or
                        node.tag.upper() == 'iec101SecSt'.upper() or
                        node.tag.upper() == 'iec101PrimAnf'.upper() or
                        node.tag.upper() == 'iec101SecAnf'.upper()):
                    hwinfo['enabled'] = True if node.get('enab', default='1').strip() == '1' else False
                if tp == 'st':
                    if node.tag.upper() == 'iec101PrimSt'.upper():
                        hwinfo['address'] = node.get('iec101PVStAddr', default='').strip()
                    if node.tag.upper() == 'iec101SecSt'.upper():
                        hwinfo['address'] = node.get('iec101SVStAddr', default='').strip()
                else:
                    if node.tag.upper() == 'iec101PrimAnf'.upper():
                        hwinfo['address'] = node.get('iec101PVAnfAddr', default='').strip()
                    if node.tag.upper() == 'iec101SecAnf'.upper():
                        hwinfo['address'] = node.get('iec101SVAnfAddr', default='').strip()
            return [hwinfo]
        return [
            {
                're': False,
                'enabled': False,
                'address': ''
            }
        ]


class ConfigComp:
    def __init__(self, b_data, k_data, s_data, u_data, z_data, mode):
        self._mode = mode
        if self._mode:
            self._td = b_data
            self._td += k_data
        else:
            self._tms = b_data
            self._td = k_data
        self._td += s_data
        self._td += u_data
        self._td += z_data

        # data = json.dumps(self._td, indent=2, sort_keys=False, ensure_ascii=False)
        # with open(os.path.join(os.path.join(os.path.dirname(__file__), "data"), 'td.json'), "w", encoding="utf-8") as file:
        #     file.write(data)

    def __del__(self):
        pass

    def __get_re__(self, c, r, s):
        # $..[?(@.id=="7")]..rtu[?(@.id=="2")].[analogs,statuses]..data[?(@.id=="76")].re
        # je = Path.parse_str('$..[?(@.id="7")]..rtu[*][?(@.id="2")][*]..data[*][?(@.id="76")].re')
        res = find('$.[?(id="' + str(c) + '")]..rtu[?(id="' + str(r) + '")].[analogs,statuses]..data[?(id="' + str(
            s) + '")].re', self._td)
        if len(res) < 1:
            return ''
        return res[0]

    def __get_re_hw__(self, c, r, s):
        # $..[?(@.id=="7")]..rtu[?(@.id=="2")].[analogs,statuses]..data[?(@.id=="76")].re
        # je = Path.parse_str('$..[?(@.id="7")]..rtu[*][?(@.id="2")][*]..data[*][?(@.id="76")].hw.re')
        res = find('$.[?(id="' + str(c) + '")]..rtu[?(id="' + str(r) + '")].[analogs,statuses]..data[?(id="' + str(
            s) + '")].hw..re', self._td)
        if len(res) < 1:
            return ''
        return res[0]

    def save_data_csv(self):
        data = 'Channel;RTU;Signal;Type;Enabled;HWEnabled;Rn;HWRn;Channel;RTU;Address\n'
        chnls = []
        if self._mode:
            chnls = self._td
        else:
            chnls = self._tms
        for chnl in chnls:
            c_name = chnl['name']
            cid = chnl['id']
            for rtu in chnl['rtu']:
                r_name = rtu['name']
                rid = rtu['id']
                for sn in rtu['statuses']:
                    for sd in sn['data']:
                        data += c_name + ";" + r_name + ";" + sd['name'] + ";S;" + str(sd['re']) + ";" + str(
                            sd['hw'][0]['re']) + ";" + str(self.__get_re__(cid, rid, sd['id'])) + ";" + str(
                            self.__get_re_hw__(cid, rid, sd['id'])) + ";" + str(cid) + ";" + str(rid) + ";" + str(sd['id']) + "\n"
                        print(c_name + " - " + r_name + " - " + sd['name'])
                for an in rtu['analogs']:
                    for ad in an['data']:
                        data += c_name + ";" + r_name + ";" + ad['name'] + ";A;" + str(ad['re']) + ";" + str(
                            ad['hw'][0]['re']) + ";" + str(self.__get_re__(cid, rid, ad['id'])) + ";" + str(
                            self.__get_re_hw__(cid, rid, ad['id'])) + ";" + str(cid) + ";" + str(rid) + ";" + str(ad['id']) + "\n"
                        print(c_name + " - " + r_name + " - " + ad['name'])
        with open(os.path.join(os.path.join(os.path.dirname(__file__), "data"), 'tms.csv'), "w",
                  encoding="cp1251") as file:
            file.write(data)


class ShParser:
    def __init__(self, data_path):
        self._data_dir = os.path.join(os.path.dirname(__file__), data_path)
        self._sh = []

    def __del__(self):
        pass

    def save_data(self, pretty=False):
        data = json.dumps(self._sh, indent=2, sort_keys=False, ensure_ascii=not pretty)
        with open(os.path.join(self._data_dir, 'sh.json'), "w", encoding="utf-8") as file:
            file.write(data)

    def load_data(self):
        with open(os.path.join(self._data_dir, 'sh.json'), "rb") as file:
            self._sh = json.load(file)

    @property
    def sh(self):
        return self._sh

    def parse(self):
        with open(os.path.join(self._data_dir, 'sh.xsde'), "rb") as file:
            sh_data = file.read()

        sh_root = etree.fromstring(sh_data)
        tags = sh_root.xpath("//*[name()='Tech']")
        for tag in tags:
            key = tag.get('keyLink', default='').strip()
            vlt = tag.get('voltage', default='').strip()
            nm = tag.get('DispName', default='').strip()
            if key != '':
                if key[0] == '#':
                    self._sh.append(
                        {
                            'key': key,
                            'voltage': vlt,
                            'name': nm
                        }
                    )
                    print(key + " - " + vlt + " - " + nm)

    def save_data_csv(self):
        data = 'Key;Voltage;Name\n'
        for rec in self._sh:
            data += rec['key'] + ";" + rec['voltage'] + ";" + rec['name'] + "\n"
        with open(os.path.join(self._data_dir, 'sh.csv'), "w", encoding="cp1251") as file:
            file.write(data)

    def append_csv(self):
        data = 'Key;Voltage;Name\n'
        sfile = open(os.path.join(self._data_dir, 'sig.csv'), "r", encoding="cp1251")
        sigs = sfile.readlines()
        for sig in sigs:
            sdata = sig.split(';')
            key = "#TC" + sdata[1][:-1]
            res = find('$.[?(key="' + key + '")].voltage', self._sh)
            if len(res) > 0:
                if res[0].strip() != '':
                    data += key + ";" + res[0] + ";" + sdata[0] + "\n"
                else:
                    data += key + ";0,4кВ;" + sdata[0] + "\n"
        with open(os.path.join(self._data_dir, 'sigf.csv'), "w", encoding="cp1251") as file:
            file.write(data)


def main():
    bParser = ConfigParser("data\\b")
    #bParser.parse()
    #bParser.save_data(pretty=True)
    bParser.load_data()

    kParser = ConfigParser("data\\k")
    #kParser.parse()
    #kParser.save_data(pretty=True)
    kParser.load_data()

    sParser = ConfigParser("data\\s")
    #sParser.parse()
    #sParser.save_data(pretty=True)
    sParser.load_data()

    uParser = ConfigParser("data\\u")
    #uParser.parse()
    #uParser.save_data(pretty=True)
    uParser.load_data()

    zParser = ConfigParser("data\\z")
    #zParser.parse()
    #zParser.save_data(pretty=True)
    zParser.load_data()

    cCmp = ConfigComp(bParser.tms, kParser.tms, sParser.tms, uParser.tms, zParser.tms, True)
    cCmp.save_data_csv()


if __name__ == '__main__':
    main()
