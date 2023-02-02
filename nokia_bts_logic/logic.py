import xml.etree.ElementTree as ET
from openpyxl import Workbook
import copy
import re

ET.register_namespace('', "raml21.xsd")
old_id = ""
old_code = ""
defined_tech_codes = ['','M','H','U','Q','G','L','O','J','F','D','E','N']
gsm_cell_ext = ['D1','D2','D3','D4']
cell_ext = ['A','B','C','D']

new_name = 'KVL89'
new_label = 'KVL89_ZC_Studenica_GL'
new_id ='4741'
new_location = 'ZC_Studenica'

input_path = 'C:\\Poso\\Nokia\\Stanice\\KVO89\\Configuration_kgl136_MUSTRA_modified_20230201-1446.xml'
output_path = "test.xml"

bcf_id = '3965'
omusig_remote_addr = '172.21.7.28'

address_space = [
    ['10.206.149.58','10.206.149.57','1010'],
    ['10.245.102.30','10.245.102.29','1011'],
    ['10.244.102.30','10.244.102.29','1012'],
    ['10.243.51.22','10.243.51.21','1013'],
]

#from LTE table
tac = '20411'
LNcell_ids = {
    'KVL89':['47411','47412','47413','47414'],
    'KVJ89':['1901','1902','1903','1904'],
    'KVO89':['47415','47416','47417','47418'],
}

rootSeqCodes = {
    'KVL89':['300','310','320','390'],
    'KVJ89':['300','310','320','390'],
    'KVO89':['660','682','704','0'],
}

cell_ids = {
    'KVL89':['1213697','1213698','1213699','1213700'],
    'KVJ89':['1213787','1213788','1213789','1213790'],
    'KVO89':['1213701','1213702','1213703','1213704'],
}

PHcell_ids = {
    'KVL89':['30','31','32','39'],
    'KVJ89':['30','31','32','39'],
    'KVO89':['30','31','32','39'],
}

def import_bts(file_path: str) -> ET.ElementTree:
    with open(file_path,'r') as f:
        d=f.read()

    data = ET.parse(file_path)
    return data

def import_lte_table(path:str):
    # TODO
    #indeksiraj relevantna polja

    #iteracija kroz polja koja sadrze kod i prikupljanje param [kgl, kgo, ...]

    return

def import_ip_table(path:str):
    # TODO

    # set() <= polja koja imaju kod
    # iteriraj kroz polja i skupi ip, gateway i vlan

    return

def get_cell_map(orig: ET.ElementTree):
    cell_map = {}
    root=orig.getroot()
    search = root.findall('.//*[@distName]')
    for elem in search:
        is_cell = len(elem.findall('./*[@name="cellName"]')) > 0
        if is_cell:
            cell_name = elem.findall('./*[@name="cellName"]')[0].text

            if cell_name[-2] == 'D':
                #GSM celija
                to_replace =  re.findall(r'LNCEL-\d+',elem.get('distName'))[0].replace('LNCEL-','')
                new_val = LNcell_ids[cell_name:-2][gsm_cell_ext.index(cell_name[-2:])]
            else:
                to_replace =  re.findall(r'LNCEL-\d+',elem.get('distName'))[0].replace('LNCEL-','')
                new_val = LNcell_ids[cell_name[:-1]][cell_ext.index(cell_name[-1:])]

            cell_map[to_replace]=new_val
    return cell_map


def MRBTS_change(orig: ET.ElementTree, new_id:str, label:str, name:str, location:str):
    changed = copy.deepcopy(orig)
    root=changed.getroot()

    search = root.findall('.//*[@name="lnBtsId"]')
    old_id = search[0].text
    for elem in search:
        elem.text=new_id

    search = root.findall('.//*[@name="location"]')
    for elem in search:
        elem.text=location

    search = root.findall('.//*[@name="btsName"]')
    for elem in search:
        elem.text=label

    search = root.findall('.//*[@name="enbName"]')
    global old_code 
    old_code = search[0].text
    for elem in search:
        elem.text=name

    new_loc_code = new_name[:2]
    old_loc_code = old_code[:2]
    new_num_code = re.findall(r'\d+', new_name)[0]
    old_num_code = re.findall(r'\d+', old_code)[0]

    search = root.findall('.//p',namespaces={'':'raml21.xsd'})
    for elem in search:
        for ext in defined_tech_codes:
            elem.text = elem.text.replace(old_loc_code+ext+old_num_code, new_loc_code+ext+new_num_code)

    cell_map = get_cell_map(changed)

    search = root.findall('.//*[@distName]')
    for elem in search:
        elem.set('distName',elem.get('distName').replace('MRBTS-'+old_id,'MRBTS-'+new_id))
        elem.set('distName',elem.get('distName').replace('SBTS-'+old_id,'SBTS-'+new_id))
        elem.set('distName',elem.get('distName').replace('LNBTS-'+old_id,'LNBTS-'+new_id))

        old_lncel = re.findall(r'LNCEL-\d+',elem.get('distName'))
        if len(old_lncel)>0:
            old_lncel = old_lncel[0].replace('LNCEL-','')
            elem.set('distName',elem.get('distName').replace('LNCEL-'+old_lncel,'LNCEL-'+cell_map[old_lncel]))
        
    search = root.findall('.//p',namespaces={'':'raml21.xsd'})
    for elem in search:
        elem.text = elem.text.replace('MRBTS-'+old_id,'MRBTS-'+new_id)
        elem.text = elem.text.replace('SBTS-'+old_id,'SBTS-'+new_id)
        elem.text = elem.text.replace('LNBTS-'+old_id,'LNBTS-'+new_id)
        old_lncel = re.findall(r'LNCEL-\d+',elem.text)
        if len(old_lncel)>0:
            old_lncel = old_lncel[0].replace('LNCEL-','')
            elem.text = elem.text.replace('LNCEL-'+old_id,'LNCEL-'+cell_map[old_lncel])

    search = root.findall('.//*[@name="ulCoMpCellList"]//p',namespaces={'':'raml21.xsd'})
    for elem in search:
        if elem.text in cell_map:
            elem.text = cell_map[elem.text]

    return changed

def cell_id_change(orig: ET.ElementTree):
    changed = copy.deepcopy(orig)
    root = changed.getroot()

    search = root.findall('.//*[@name="traceId"]')
    lcrs = root.findall('.//*[@name="traceId"]/../../../*[@name="lcrId"]')
    cells = root.findall('.//*[@class="NOKLTE:LNCEL"]')
    for elem, lcr in zip(search, lcrs):
        for c in cells:
            cell_lcr = c.findall('.//*[@name="lcrId"]')[0].text
            if c.findall('.//*[@name="lcrId"]')[0].text == lcr.text:
                lncell_id = re.findall(r'LNCEL-\d+', c.get('distName'))[0].replace('LNCEL-','')
                for code in LNcell_ids:
                    for ind, val in enumerate(LNcell_ids[code]):
                        if val == lncell_id:
                            elem.text=cell_ids[code][ind]

    return changed

def phy_cell_id_change(orig: ET.ElementTree):
    changed = copy.deepcopy(orig)
    root = changed.getroot()

    search = root.findall('.//*[@name="phyCellId"]')
    cells = root.findall('.//*[@name="phyCellId"]/..')
    for elem, cell in zip(search,cells):
        lncell_id = re.findall(r'LNCEL-\d+', cell.get('distName'))[0].replace('LNCEL-','')
        for code in LNcell_ids:
            for ind, val in enumerate(LNcell_ids[code]):
                if val == lncell_id:
                    elem.text=PHcell_ids[code][ind]

    return changed

def root_seq_change(orig: ET.ElementTree):
    changed = copy.deepcopy(orig)
    root = changed.getroot()
    
    search = root.findall('.//*[@name="rootSeqIndex"]')
    parents = root.findall('.//*[@name="rootSeqIndex"]/..')
    for elem, parent in zip(search,parents):
        dn=parent.get('distName')
        tst=re.findall(r'LNBTS-\d+', parent.get('distName'))
        cell_id = re.findall(r'LNCEL-\d+', parent.get('distName'))[0].replace('LNCEL-','')
        for code in LNcell_ids:
            for ind, val in enumerate(LNcell_ids[code]):
                if val == cell_id:
                    elem.text = rootSeqCodes[code][ind]

    return changed

def tac_change(orig: ET.ElementTree):
    changed = copy.deepcopy(orig)
    root = changed.getroot()
    search = root.findall('.//*[@name="tac"]')
    for elem in search:
        elem.text=tac
    return changed

def bcf_change(orig:ET.ElementTree):
    changed = copy.deepcopy(orig)
    root = changed.getroot()

    search = root.findall('.//*[@name="mPlaneRemoteIpAddressOmuSig"]')[0]
    search.text=omusig_remote_addr

    search = root.findall('.//*[@name="bcfId"]')[0]
    search.text=bcf_id

    return changed

def address_change(orig:ET.ElementTree):
    changed = copy.deepcopy(orig)
    root = changed.getroot()

    search = root.findall('.//*[@name="localIpAddr"]')
    parents = root.findall('.//*[@name="localIpAddr"]/..')
    for elem, parent in zip(search, parents):
        for addr in address_space:
            if addr[0][:7] in elem.text:
                elem.text = addr[0]
                addr.append(re.findall(r'IPIF-\d+',parent.get('distName'))[0].replace('IPIF-',''))

    vlan_parents = root.findall('.//*[@name="interfaceDN"]/..')
    for elem in vlan_parents:
        for addr in address_space:
            if re.findall(r'IPIF-\d+',parent.get('distName'))[0].replace('IPIF-','') == addr[3]:
                addr.append(re.findall(r'VLANIF-\d+',elem.findall('.//*[@name="interfaceDN"]')[0].text)[0].replace('VLANIF-',''))

    vlans = root.findall('.//*[@name="vlanid"]/..')
    for elem in vlans:
        for addr in address_space:
            if re.findall(r'VLANIF-\d+',parent.get('distName'))[0].replace('VLANIF-','') == addr[4]:
                if len(elem.findall('.//[@name="userLabel"]'))>0:
                    #postoji labela
                    old_label = re.findall(r'((VLAN)|(Vlan)|(vlan))\d+',elem.findall('.//[@name="userLabel"]')[0].text)
                    if len(old_label)>0:
                        old_label = old_label[0]
                        elem.findall('.//[@name="userLabel"]')[0].text.replace(old_label,'VLAN'+addr[2])
                elem.findall('.//[@name="vlanid"]')[0].text = addr[2]        

    search = root.findall('.//*[@name="gateway"]')
    for elem in search:
        for addr in address_space:
            if addr[0][:7] in elem.text:
                elem.text=addr[1]

    return changed


data = import_bts(file_path=input_path)
changed = MRBTS_change(data,new_id,new_label,new_name,new_location)
changed = tac_change(changed)
changed = root_seq_change(changed)
changed = cell_id_change(changed)
changed = phy_cell_id_change(changed)
changed = bcf_change(changed)
changed = address_change(changed)
changed.write(open(output_path,'w'), encoding='unicode')