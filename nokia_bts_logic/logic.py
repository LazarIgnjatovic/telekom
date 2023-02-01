import xml.etree.ElementTree as ET
import copy
import re

ET.register_namespace('', "raml21.xsd")
old_id = ""
old_code = ""
defined_tech_codes = ['','M','H','U','Q','G','L','O','J','F','D','E','N']
gsm_cell_ext = ['D1','D2','D3','D4']
cell_ext = ['A','B','C','D']

new_name = 'KGL136'
new_label = 'KGL136_test_labela'
new_id ='4752'
new_location = 'test_lokacija'

input_path = 'C:\\Poso\\Nokia\\Stanice\\KGL136\\kgl136_MUSTRA.xml'
output_path = "test.xml"

#from LTE table
tac = '20411'
LNcell_ids = {
    'KGL136':['47521','47522','47523','47524'],
    'KGJ136':['1981','1982','1983','1984'],
    'KGO136':['47525','47526','47527','47528'],
}

rootSeqCodes = {
    'KGL136':['90','100','110','130'],
    'KGJ136':['90','100','110','130'],
    'KGO136':['90','100','110','130'],
}

cell_ids = {
    'KGL136':['1216513','1216514','1216515','1216516'],
    'KGJ136':['1216603','1216604','1216605','1216606'],
    'KGO136':['1216517','1216518','1216519','1216520'],
}

PHcell_ids = {
    'KGL136':['345','346','347','116'],
    'KGJ136':['345','346','347','116'],
    'KGO136':['345','346','347','116'],
}

def import_bts(file_path: str) -> ET.ElementTree:
    with open(file_path,'r') as f:
        d=f.read()

    data = ET.parse(file_path)
    return data

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

    cell_map = {}

    search = root.findall('.//*[@distName]')
    for elem in search:
        is_cell = len(elem.findall('./*[@name="cellName"]'))>0
        if is_cell:
            cell_name = elem.findall('./*[@name="cellName"]')[0].text

            if cell_name[-2] == 'D':
                #GSM celija
                to_replace =  re.findall(r'LNCEL-\d+',elem.get('distName'))[0]
                new_val = LNcell_ids[cell_name:-2][gsm_cell_ext.index(cell_name[-2:])]
            else:
                to_replace =  re.findall(r'LNCEL-\d+',elem.get('distName'))[0]
                new_val = LNcell_ids[cell_name[:-1]][cell_ext.index(cell_name[-1:])]

            cell_map[to_replace]=new_val
            elem.set('distName',elem.get('distName').replace('LNCEL-'+to_replace,'LNCEL-'+new_val))

        elem.set('distName',elem.get('distName').replace('MRBTS-'+old_id,'MRBTS-'+new_id))
        elem.set('distName',elem.get('distName').replace('SBTS-'+old_id,'SBTS-'+new_id))
        elem.set('distName',elem.get('distName').replace('LNBTS-'+old_id,'LNBTS-'+new_id))
        

    search = root.findall('.//p',namespaces={'':'raml21.xsd'})
    for elem in search:
        elem.text = elem.text.replace('MRBTS-'+old_id,'MRBTS-'+new_id)
        elem.text = elem.text.replace('SBTS-'+old_id,'SBTS-'+new_id)
        elem.text = elem.text.replace('LNBTS-'+old_id,'LNBTS-'+new_id)
        elem.text = elem.text.replace('LNCEL-'+old_id,'LNCEL-'+cell_map[old_id])

    search = root.findall('.//*[@name="ulCoMpCellList"]//p',namespaces={'':'raml21.xsd'})
    for elem in search:
        elem.text = elem.text.replace(old_id,cell_map[old_id])

    return changed

def label_change(orig: ET.ElementTree, new_code:str):
    changed = copy.deepcopy(orig)
    root = changed.getroot()
    new_loc_code = new_code[:2]
    old_loc_code = old_code[:2]
    new_num_code = re.findall(r'\d+', new_code)[0]
    old_num_code = re.findall(r'\d+', old_code)[0]

    search = root.findall('.//p',namespaces={'':'raml21.xsd'})
    for elem in search:
        for ext in defined_tech_codes:
            elem.text = elem.text.replace(old_loc_code+ext+old_num_code, new_loc_code+ext+new_num_code)

    return changed

def cell_id_change(orig: ET.ElementTree):
    changed = copy.deepcopy(orig)
    root = changed.getroot()

    search = root.findall('.//*[@name="traceId"]')
    lcrs = root.findall('.//*[@name="traceId"]/../../../*[@name="lcrId"]')
    cells = root.findall('.//*[@class="NOKLTE:LNCEL"]')
    for elem, lcr in zip(search, lcrs):
        for c in cells:
            if c.findall('.//*[@name="lcrId"]')[0] == lcr:
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
    cells = root.findall('.//*[@class="NOKLTE:LNCEL"]')
    for elem in search:
        for c in cells:
            lncell_id = re.findall(r'LNCEL-\d+', c.get('distName'))[0].replace('LNCEL-','')
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


data = import_bts(file_path=input_path)
changed = MRBTS_change(data,new_id,new_label,new_name,new_location)
changed = label_change(changed, new_name)
changed = tac_change(changed)
changed = root_seq_change(changed)
changed = cell_id_change(changed)
changed = phy_cell_id_change(changed)
changed.write(open(output_path,'w'), encoding='unicode')