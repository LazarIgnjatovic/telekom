import xml.etree.ElementTree as ET
import openpyxl as xl
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
new_location = 'ZC_Studenica'
bcf_id = '3965'
omusig_remote_addr = '172.21.7.28'

lte_path = "C:\\Poso\\Nokia\\LTE_tabele\\LTE_podaci_01_02_2023.xlsx"
ip_path = "C:\\Poso\\Nokia\\IP_tabele\\98NSN ALL IP i LTE  Tabela ver14.0.xlsm"
input_path = 'C:\\Poso\\Nokia\\Stanice\\KVO89\\Configuration_kgl136_MUSTRA_modified_20230201-1446.xml'
output_path = "test.xml"

global address_space
global tac
global new_id
global LNcell_ids
global rootSeqCodes
global cell_ids
global PHcell_ids

def log(message:str):
    print(message+'...')

def import_bts(file_path: str) -> ET.ElementTree:
    log('Importing template')
    with open(file_path,'r') as f:
        d=f.read()

    data = ET.parse(file_path)
    return data

def import_lte_table(path:str, code:str):
    log('Opening LTE table')
    workbook = xl.load_workbook(filename=path, data_only=True)
    sheet = workbook.active
    log('Finding Relevant Rows')
    loc_code = code[:2]
    num_code = re.findall(r'\d+', code)[0]
    relevant_rows = []
    enb_col = 1 
    tac_col = 0
    lncell_cols=[]
    root_cols=[]
    trace_cols=[]
    ph_cols=[]
    for cell in sheet['A']:
        if cell.value is not None and len(cell.value) > 2 and len(re.findall(r'\d+', cell.value)) > 0:
            cell_loc_code = cell.value[:2]
            cell_num_code = re.findall(r'\d+', cell.value)[0]
            if cell_loc_code == loc_code and cell_num_code == num_code:
                relevant_rows.append(cell.row)
    for cell in sheet[1]:
        if cell.value is not None:
            if 'LNcell ID ' in cell.value:
                lncell_cols.append(cell.column-1)
            elif 'CellId' in cell.value:
                trace_cols.append(cell.column-1)
            elif 'TAC' == cell.value:
                tac_col = cell.column-1
            elif len(cell.value) == 4 and 'PCI' in cell.value:
                ph_cols.append(cell.column-1)
            elif 'rachRootSequence' in cell.value:
                root_cols.append(cell.column-1)

    log("Collecting data")
    global tac
    global new_id
    global LNcell_ids
    global rootSeqCodes
    global cell_ids
    global PHcell_ids
    tac = ''
    new_id = ''
    LNcell_ids = {}
    rootSeqCodes = {}
    cell_ids = {}
    PHcell_ids = {}

    for row in relevant_rows:
        tac = str(sheet[row][tac_col].value)
        new_id = str(sheet[row][enb_col].value)

        c = sheet[row][0].value
        LNcell_ids[c] = []
        rootSeqCodes[c] = []
        cell_ids[c] = []
        PHcell_ids[c] = []

        for col in lncell_cols:
            if sheet[row][col].value is not None:
                LNcell_ids[c].append(str(sheet[row][col].value))
        for col in root_cols:
            if sheet[row][col].value is not None:
                rootSeqCodes[c].append(str(sheet[row][col].value))
        for col in trace_cols:
            if sheet[row][col].value is not None:
                cell_ids[c].append(str(sheet[row][col].value))
        for col in ph_cols:
            if sheet[row][col].value is not None:
                PHcell_ids[c].append(str(sheet[row][col].value))
    return 

def import_ip_table(path:str, code:str):
    log("Loading IP table")
    workbook = xl.load_workbook(filename=path, data_only=True, read_only=True)
    sheet = workbook.active

    relevant_rows = []
    global address_space 
    address_space = []
    ip_int_column = 34
    loc_code = code[:2]
    num_code = re.findall(r'\d+', code)[0]
    log('Searching for relevant fields')
    for row in sheet.rows:
        cell = row[ip_int_column]
        if cell.value is not None and type(cell.value) is str and len(cell.value) > 2 and len(re.findall(r'\d+', cell.value)) > 0:
            cell_loc_code = cell.value[:2]
            cell_num_code = re.findall(r'\d+', cell.value)[0]
            if cell_loc_code == loc_code and cell_num_code == num_code:
                relevant_rows.append(cell.row)

    log('Constructing address space')
    for row in relevant_rows:
        ip = sheet[row][ip_int_column+1].value.split('/')[0]
        vlan = sheet[row][ip_int_column+2].value
        octets = ip.split('.')
        octets[-1] = str(int(octets[-1])-1)
        gateway = '.'.join(octets)
        address_space.append([ip,gateway,vlan])

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
    log('General info update')
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

    log('Cell Name and Id update')

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
    log('TraceId update')
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
    log('PhCellId update')
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
    log('RACH update')
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
    log('Tac update')
    changed = copy.deepcopy(orig)
    root = changed.getroot()
    search = root.findall('.//*[@name="tac"]')
    for elem in search:
        elem.text=tac
    return changed

def bcf_change(orig:ET.ElementTree):
    log('Changing BCF data')
    changed = copy.deepcopy(orig)
    root = changed.getroot()

    search = root.findall('.//*[@name="mPlaneRemoteIpAddressOmuSig"]')[0]
    search.text=omusig_remote_addr

    search = root.findall('.//*[@name="bcfId"]')[0]
    search.text=bcf_id

    return changed

def address_change(orig:ET.ElementTree):
    log('Changig IP address space')
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
import_lte_table(lte_path,new_name)
import_ip_table(ip_path,new_name)
changed = MRBTS_change(data,new_id,new_label,new_name,new_location)
changed = tac_change(changed)
changed = root_seq_change(changed)
changed = cell_id_change(changed)
changed = phy_cell_id_change(changed)
changed = bcf_change(changed)
changed = address_change(changed)
changed.write(open(output_path,'w'), encoding='unicode')