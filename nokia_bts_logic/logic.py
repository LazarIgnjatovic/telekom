import xml.etree.ElementTree as ET
import openpyxl as xl
import copy
import re

class Logic(object):

    def __init__(self,name,label,location,bcf,omusig,lte,ip,template,out) -> None:

        ET.register_namespace('', "raml21.xsd")
        self.new_name = name
        self.new_label = label
        self.new_location = location
        self.bcf_id = bcf
        self.omusig_remote_addr = omusig
        self.lte_path = lte
        self.ip_path = ip
        self.input_path = template
        self.output_path = out

        self.old_id = ""
        self.old_code = ""
        self.defined_tech_codes = ['','M','H','U','Q','G','L','O','J','F','D','E','N']
        self.gsm_cell_ext = ['D1','D2','D3','D4']
        self.cell_ext = ['A','B','C','D']
        self.address_space = []
        self.logger = print

    def set_logger(self,logger):
        self.logger=logger

    def log(self,message:str):
        self.logger(message+'...')

    def import_bts(self,file_path: str) -> ET.ElementTree:
        self.log('Importing template')
        data = ET.parse(file_path)
        return data

    def import_lte_table(self, path:str, code:str):
        self.log('Opening LTE table')
        workbook = xl.load_workbook(filename=path, data_only=True)
        sheet = workbook.active
        self.log('Finding Relevant Rows')
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

        self.log("Collecting data")
        self.tac = ''
        self.new_id = ''
        self.LNcell_ids = {}
        self.rootSeqCodes = {}
        self.cell_ids = {}
        self.PHcell_ids = {}

        for row in relevant_rows:
            self.tac = str(sheet[row][tac_col].value)
            self.new_id = str(sheet[row][enb_col].value)

            c = sheet[row][0].value
            self.LNcell_ids[c] = []
            self.rootSeqCodes[c] = []
            self.cell_ids[c] = []
            self.PHcell_ids[c] = []

            for col in lncell_cols:
                if sheet[row][col].value is not None:
                    self.LNcell_ids[c].append(str(sheet[row][col].value))
            for col in root_cols:
                if sheet[row][col].value is not None:
                    self.rootSeqCodes[c].append(str(sheet[row][col].value))
            for col in trace_cols:
                if sheet[row][col].value is not None:
                    self.cell_ids[c].append(str(sheet[row][col].value))
            for col in ph_cols:
                if sheet[row][col].value is not None:
                    self.PHcell_ids[c].append(str(sheet[row][col].value))
        return 

    def import_ip_table(self, path:str, code:str):
        self.log("Loading IP table")
        workbook = xl.load_workbook(filename=path, data_only=True, read_only=True)
        sheet = workbook.active

        relevant_rows = set()
        self.address_space 
        self.address_space = {}
        ip_int_column = 34
        loc_code = code[:2]
        num_code = re.findall(r'\d+', code)[0]
        self.log('Searching for relevant fields')
        for row in sheet.rows:
            cell = row[ip_int_column]
            if cell.value is not None and type(cell.value) is str:
                for name_part in cell.value.split('_'):
                     if len(name_part) > 2 and len(re.findall(r'\d+', name_part)) > 0 and len(re.findall(r'\d+', name_part)[0]) > 1:
                          # Ovo predstavlja loc code u tabeli
                        cell_loc_code = name_part[:2]
                        cell_tech_code = ''
                        if not name_part[2].isdigit():
                            cell_tech_code = name_part[2]
                        cell_num_code = re.findall(r'\d+', name_part)[0]
                        if cell_loc_code == loc_code and cell_num_code == num_code and cell_tech_code in self.defined_tech_codes:
                            relevant_rows.add(cell.row)

        self.log('Constructing address space')
        for row in relevant_rows:
            ip = sheet[row][ip_int_column+1].value.split('/')[0]
            vlan = sheet[row][ip_int_column+2].value
            octets = ip.split('.')
            octets[-1] = str(int(octets[-1])-1)
            gateway = '.'.join(octets)
            int_name = sheet[row][ip_int_column].value
            if 'rbs' in int_name.lower():
                if 'RBS' in self.address_space.keys():
                    raise Exception("Multiple address entries detected in IP_TABLE (same location and number), Check for validity!")
                self.address_space['RBS'] = [ip,gateway,vlan]
            elif 'abis' in int_name.lower():
                if 'ABIS' in self.address_space.keys():
                    raise Exception("Multiple address entries detected in IP_TABLE (same location and number), Check for validity!")
                self.address_space['ABIS'] = [ip,gateway,vlan]
            elif 's1' in int_name.lower():
                if 'S1' in self.address_space.keys():
                    raise Exception("Multiple address entries detected in IP_TABLE (same location and number), Check for validity!")
                self.address_space['S1'] = [ip,gateway,vlan]
            elif 'oam' in int_name.lower() and '10.244.' in ip:
                if 'OAM' in self.address_space.keys():
                    raise Exception("Multiple address entries detected in IP_TABLE (same location and number), Check for validity!")
                self.address_space['OAM'] = [ip,gateway,vlan]
            elif 'sync' in int_name.lower():
                if 'SYNC' in self.address_space.keys():
                    raise Exception("Multiple address entries detected in IP_TABLE (same location and number), Check for validity!")
                self.address_space['SYNC'] = [ip,gateway,vlan]

        return

    def get_cell_map(self, orig: ET.ElementTree):
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
                    new_val = self.LNcell_ids[cell_name:-2][self.gsm_cell_ext.index(cell_name[-2:])]
                else:
                    to_replace =  re.findall(r'LNCEL-\d+',elem.get('distName'))[0].replace('LNCEL-','')
                    new_val = self.LNcell_ids[cell_name[:-1]][self.cell_ext.index(cell_name[-1:])]

                cell_map[to_replace]=new_val
        return cell_map

    def MRBTS_change(self, orig: ET.ElementTree, new_id:str, label:str, name:str, location:str):
        self.log('General info update')
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
        self.old_code = search[0].text
        for elem in search:
            elem.text=name

        self.log('Cell Name and Id update')

        new_loc_code = self.new_name[:2]
        old_loc_code = self.old_code[:2]
        new_num_code = re.findall(r'\d+', self.new_name)[0]
        old_num_code = re.findall(r'\d+', self.old_code)[0]

        search = root.findall('.//p',namespaces={'':'raml21.xsd'})
        for elem in search:
            for ext in self.defined_tech_codes:
                elem.text = elem.text.replace(old_loc_code+ext+old_num_code, new_loc_code+ext+new_num_code)

        cell_map = self.get_cell_map(changed)

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

    def cell_id_change(self, orig: ET.ElementTree):
        self.log('TraceId update')
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
                    for code in self.LNcell_ids:
                        for ind, val in enumerate(self.LNcell_ids[code]):
                            if val == lncell_id:
                                elem.text=self.cell_ids[code][ind]

        return changed

    def phy_cell_id_change(self, orig: ET.ElementTree):
        self.log('PhCellId update')
        changed = copy.deepcopy(orig)
        root = changed.getroot()

        search = root.findall('.//*[@name="phyCellId"]')
        cells = root.findall('.//*[@name="phyCellId"]/..')
        for elem, cell in zip(search,cells):
            lncell_id = re.findall(r'LNCEL-\d+', cell.get('distName'))[0].replace('LNCEL-','')
            for code in self.LNcell_ids:
                for ind, val in enumerate(self.LNcell_ids[code]):
                    if val == lncell_id:
                        elem.text=self.PHcell_ids[code][ind]

        return changed

    def root_seq_change(self, orig: ET.ElementTree):
        self.log('RACH update')
        changed = copy.deepcopy(orig)
        root = changed.getroot()
        
        search = root.findall('.//*[@name="rootSeqIndex"]')
        parents = root.findall('.//*[@name="rootSeqIndex"]/..')
        for elem, parent in zip(search,parents):
            cell_id = re.findall(r'LNCEL-\d+', parent.get('distName'))[0].replace('LNCEL-','')
            for code in self.LNcell_ids:
                for ind, val in enumerate(self.LNcell_ids[code]):
                    if val == cell_id:
                        elem.text = self.rootSeqCodes[code][ind]

        return changed

    def tac_change(self, orig: ET.ElementTree):
        self.log('Tac update')
        changed = copy.deepcopy(orig)
        root = changed.getroot()
        search = root.findall('.//*[@name="tac"]')
        for elem in search:
            elem.text=self.tac
        return changed

    def bcf_change(self,orig:ET.ElementTree):
        self.log('Changing BCF data')
        changed = copy.deepcopy(orig)
        root = changed.getroot()

        search = root.findall('.//*[@name="mPlaneRemoteIpAddressOmuSig"]')[0]
        search.text=self.omusig_remote_addr

        search = root.findall('.//*[@name="bcfId"]')[0]
        search.text=self.bcf_id

        return changed

    def address_change(self, orig:ET.ElementTree):
        self.log('Changig IP address space')
        changed = copy.deepcopy(orig)
        root = changed.getroot()

        search = root.findall('.//*[@name="localIpAddr"]')
        parents = root.findall('.//*[@name="localIpAddr"]/..')
        for elem, parent in zip(search, parents):
            for addr in self.address_space:
                if addr[0][:7] in elem.text:
                    elem.text = addr[0]
                    addr.append(re.findall(r'IPIF-\d+',parent.get('distName'))[0].replace('IPIF-',''))

        vlan_parents = root.findall('.//*[@name="interfaceDN"]/..')
        for elem in vlan_parents:
            for addr in self.address_space:
                if re.findall(r'IPIF-\d+',parent.get('distName'))[0].replace('IPIF-','') == addr[3]:
                    addr.append(re.findall(r'VLANIF-\d+',elem.findall('.//*[@name="interfaceDN"]')[0].text)[0].replace('VLANIF-',''))

        vlans = root.findall('.//*[@name="vlanid"]/..')
        for elem in vlans:
            for addr in self.address_space:
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
            for addr in self.address_space:
                if addr[0][:7] in elem.text:
                    elem.text=addr[1]

        return changed
    
    def address_change_new(self, orig:ET.ElementTree):
        self.log('Changig IP address space')
        changed = copy.deepcopy(orig)
        root = changed.getroot()

        vlan_lbs = ['RBS','ABIS','S1','OAM','SYNC']
        vlans = root.findall('.//*[@name="vlanid"]/..')
        #svi vlanovi
        for elem in vlans:
            vlan_labels = elem.findall('.//[@name="userLabel"]')
            if len(vlan_labels) == 0:
                #ne postoje labele
                raise Exception('Please label VLANs with values [RBS/ABIS/S1/OAM/SYNC] inside the template file')
            vlan_label = vlan_labels[0].text
            vlan_type = ''
            for lb in vlan_lbs:
                if lb.lower() in vlan_label.lower():
                    vlan_type=lb
            if vlan_type=='':
                raise Exception('VLAN labeled: '+vlan_label+' has no corresponding addres, please use values [RBS/ABIS/S1/OAM/SYNC] inside the label')
            
            #replace label VLAN value (if defined)
            old_label = re.findall(r'((VLAN)|(Vlan)|(vlan))\d+',elem.findall('.//[@name="userLabel"]')[0].text)
            if len(old_label)>0:
                old_label = old_label[0]
                elem.findall('.//[@name="userLabel"]')[0].text.replace(old_label,'VLAN'+ self.address_space[vlan_type][2])
            #replace VLAN Id
            elem.findall('.//[@name="vlanid"]')[0].text = self.address_space[vlan_type][2]
            #add previous vlanId to address_space
            self.address_space[vlan_type].append(re.findall(r'VLANIF-\d+',elem.get('distName'))[0].replace('VLANIF-',''))

        #VLAN->IP connection
        vlan_parents = root.findall('.//*[@name="interfaceDN"]/..')
        for elem in vlan_parents:
            for addr in self.address_space.values():
                if re.findall(r'VLANIF-\d+',elem.findall('.//*[@name="interfaceDN"]')[0].text)[0].replace('VLANIF-','') == addr[3]:
                    addr.append(re.findall(r'IPIF-\d+',parent.get('distName'))[0].replace('IPIF-',''))

        #IP address change
        search = root.findall('.//*[@name="localIpAddr"]')
        parents = root.findall('.//*[@name="localIpAddr"]/..')
        for elem, parent in zip(search, parents):
            for addr in self.address_space.values():
                if re.findall(r'IPIF-\d+',parent.get('distName'))[0].replace('IPIF-','') == addr[4]:
                    addr.append(elem.text)
                    octets = elem.text.split('.')
                    octets[-1] = str(int(octets[-1])-1)
                    old_gateway = '.'.join(octets)
                    addr.append(old_gateway)
                    elem.text=addr[0]

        #Gateway change
        search = root.findall('.//*[@name="gateway"]')
        for elem in search:
            for addr in self.address_space:
                if addr[6] == elem.text:
                    elem.text=addr[1]

        return changed

    def start(self):
        data = self.import_bts(file_path=self.input_path)
        self.import_lte_table(self.lte_path,self.new_name)
        self.import_ip_table(self.ip_path,self.new_name)
        changed = self.MRBTS_change(data,self.new_id,self.new_label,self.new_name,self.new_location)
        changed = self.tac_change(changed)
        changed = self.root_seq_change(changed)
        changed = self.cell_id_change(changed)
        changed = self.phy_cell_id_change(changed)
        changed = self.bcf_change(changed)
        # changed.write(open(self.output_path,'w'), encoding='unicode')
        changed = self.address_change_new(changed)
        changed.write(open(self.output_path,'w'), encoding='unicode')