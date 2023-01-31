import xml.etree.ElementTree as ET
import copy
import re

ET.register_namespace('', "raml21.xsd")
old_id = ""
old_code = ""
defined_tech_codes = ['','M','H','U','Q','G','L','O','J','F','D','E','N']

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

    search = root.findall('.//*[@distName]')
    for elem in search:
        elem.set('distName',elem.get('distName').replace('MRBTS-'+old_id,'MRBTS-'+new_id))
        elem.set('distName',elem.get('distName').replace('LNBTS-'+old_id,'LNBTS-'+new_id))
        elem.set('distName',elem.get('distName').replace('LNCEL-'+old_id,'LNBTS-'+new_id))

    search = root.findall('.//p',namespaces={'':'raml21.xsd'})
    for elem in search:
        elem.text = elem.text.replace('MRBTS-'+old_id,'MRBTS-'+new_id)
        elem.text = elem.text.replace('SBTS-'+old_id,'SBTS-'+new_id)
        elem.text = elem.text.replace('LNBTS-'+old_id,'LNBTS-'+new_id)
        elem.text = elem.text.replace('LNCEL-'+old_id,'LNBTS-'+new_id)

    search = root.findall('.//*[@name="ulCoMpCellList"]//p',namespaces={'':'raml21.xsd'})
    for elem in search:
        elem.text = elem.text.replace(old_id,new_id)
        elem.text = elem.text.replace(old_id,new_id)
        elem.text = elem.text.replace(old_id,new_id)

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

def cell_id_change(orig: ET.ElementTree, cell_ids):
    changed = copy.deepcopy(orig)
    #traceId
    return changed

def phy_cell_id_change(orig: ET.ElementTree, cell_ids):
    changed = copy.deepcopy(orig)
    #phyCellId
    return changed

def root_seq_change(orig: ET.ElementTree, root_seqs):
    changed = copy.deepcopy(orig)
    #rootSeqIndex
    return changed

def tac_change(orig: ET.ElementTree, root_seqs):
    changed = copy.deepcopy(orig)
    #tac
    return changed

path = 'C:\\Poso\\Nokia\\Stanice\\KGL136\\kgl136_MUSTRA.xml'
data = import_bts(file_path=path)
changed = MRBTS_change(data,'4343','TSL199_test_labela','TSL199','test_lokacija')
changed = label_change(changed, "TSL199")
changed.write(open("test.xml",'w'), encoding='unicode')