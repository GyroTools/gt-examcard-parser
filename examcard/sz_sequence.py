import base64
import hashlib
import os
import struct
import zipfile
from typing import List


class EnumDesc:
    def __init__(self, it: int, values: List[str]):
        self.id = id
        self.values = values


def _get_a_param(str_block, i):
    # each parameter has: name, type, number, offset1, offset2
    pos0 = 32  # initial offset of the whole str_block base64 decoded

    if pos0+(i+1)*50 > len(str_block):
        return None, None, None

    b_str1 = str_block[pos0+i*50:pos0+(i+1)*50]   # each param has a length of 50 bytes

    # work out its name from the first 33 bytes   
    b = b_str1[0:33]

    pos_s = b.find(b'\x00')   # find end of name string 
    if pos_s >= 0:
        b = b[:pos_s] 
  
    nm = str(b, 'utf-8', errors="ignore")  # name of param

    if len(nm) < 5:
        return None, None, None

    if (nm[2] != '_') and (nm[3] != '_'):  # name should be something like GEX_   EX_ or IF_
        return None, None, None

    # work out its data type
    b = b_str1[34:38]
    tp = int.from_bytes(b, byteorder='little', signed=False)   # data type of param as unsigned int

    if tp > 4:
        return None, None, None

    # work out the numbers
    b = b_str1[38:42]
    num = int.from_bytes(b, byteorder='little', signed=False)   # number of params as unsigned int

    # work out its offset1
    b = b_str1[42:46]
   
    off1 = int.from_bytes(b, byteorder='little', signed=False)   # offset1 as unsigned int, from current pos
   
    off1 = off1 + pos0 + i*50 + 42  # now offset1 from the beginning of whole str_block

    # work out its offset2
    b = b_str1[46:50]
    off2 = int.from_bytes(b, byteorder='little', signed=False)   # offset2 as unsigned int, from current pos
   
    off2 = off2 + pos0 + i*50 + 46    # now offset2 is from the beginning of whole str_block

    # to get the param's values using tp, num, off1, off2 from the base64 decoded str_block
    parm, enum_desc = _get_param_value(tp, num, off1, off2, str_block)

    return nm, parm, enum_desc


def _get_param_value(typ, num, off1, off2, b_str):
    values = []
    enum_desc = (None, None)
    
    if typ == 0:   # float
        k = 0
        while k < num:
            b = b_str[off2+k*4:off2+(k+1)*4]   # size of float == 4
      
            flt = struct.unpack('<f', b)
            values.append(flt[0])
            k += 1

    if typ == 1:   # int
        k = 0
        while k < num:
            b = b_str[off2+k*4:off2+(k+1)*4]   # size of int == 4
               
            intgr = struct.unpack('<i', b)
            values.append(intgr[0])
            k += 1

    if typ == 2:   # string
        k = 0
        while k < num:
            b = b_str[off2+k*81:off2+(k+1)*81]   # size of string == 81 here

            pos_s = b.find(b'\x00')   # end of string 
            if pos_s >= 0:
                b = b[:pos_s] 
  
            str1 = str(b, 'utf-8', errors="ignore")
            if len(str1) > 0:
                values.append(str1)
            k += 1

    if typ == 4:  # enum, only consider the case of num == 1
        
        pos_s = b_str.find(b'\x00', off1)
        
        b = b_str[off1:pos_s]

        str1 = str(b, 'utf-8', errors="ignore")  # the enum string separated by ','
        md5hash = hashlib.md5(str1.encode()).hexdigest()
        list1 = str1.split(',')   # the enum split out as a list
        enum_desc = (md5hash, list1)

        b = b_str[off2:off2+4]   # size of int == 4
        inx = (struct.unpack('<i', b))[0]

        values.append(inx)

    if len(values) == 1:
        values = values[0]

    return values, enum_desc


def _get_parameter_data(node):
    out = dict()
    decoded_str = base64.b64decode(node.text)

    enums = dict()
    enum_desc = dict()
    enum_id = 0

    for i in range(0, 4096):  # loop through each parameter of protocol
        key, value, cur_enum_desc = _get_a_param(decoded_str, i)   # initial pos = 32 will be used
        if key is None:
            break
        else:
            out[key] = value

        md5hash = cur_enum_desc[0]
        if md5hash:
            enums[key] = enum_id
            if not enum_desc.get(md5hash):
                ed = EnumDesc(enum_id, cur_enum_desc[1])
                enum_desc[md5hash] = ed
                enum_id += 1

    return out, enum_desc, enums


def _get_data_buffer(el, el_cnt):  # el_cnt used to assign sub-dir for temp files
    pth = './tmp_' + str(el_cnt)  # 2dn layer of tmp dirs
        
    if not os.path.exists(pth):
        os.mkdir(pth)
            
    os.chdir(pth)

    if el.text is None:
        os.chdir('..')   # need to go back to dir in this case before return
            
        return
        
    decoded_str = base64.b64decode(el.text)
        
    file1 = open("zipped_byte.txt", "wb")
    file1.write(decoded_str) 
    file1.close()        
      
    with zipfile.ZipFile("zipped_byte.txt", "r") as zip_ref:
        zip_ref.extractall('.')
        
    files = filter(os.path.isfile, os.listdir(os.curdir))

    for filename in files:
        if filename.find(".rtf") > 0:
            pass
            # captn += rtf.get_rtf_file_parsed(filename)

        if filename.find(".1rtf") > 0:
            pass
            # captn += rtf.get_rtf_file_parsed(filename)

        if filename.find(".2rtf") > 0:
            pass
            # captn += rtf.get_rtf_file_parsed(filename)

        if filename.find(".3rtf") > 0:
            pass
            # captn += rtf.get_rtf_file_parsed(filename)
                
        if filename.find('.jpg') > 0:
            pass
            # fpdf.insert_image(pdf, filename, captn)
              
    os.chdir('..')
