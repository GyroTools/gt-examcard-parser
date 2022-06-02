def _clean_str_value(s: str):
    if s is None:
        return ''
    
    pos = s.find('}')  # get rif of the substring enclosed in {  }
    if pos >= 0:
        tmp = s[pos+1:]
    else:
        tmp = s

    length = len(tmp)
    if tmp[length-1] == '\n':  # get rig of the line feed at end of string
        tmp = tmp[:length-2]

    return tmp


def _get_attrib_value(node, key):
    for attr in node.attrib:
        if attr.find(key) >= 0:
            return node.attrib[key]
        else:
            return None
    

def _get_nodes_by_tag(node, tag):
    res = []

    for ele in node.iter():
 
        if _clean_str_value(ele.tag) == tag:
            res.append(ele)

    return res


def _get_node_by_attrib_value(root, key, val):
  
    for ele in root.iter():
    
        for attr in ele.attrib:
          
            if attr.find(key) >= 0:
                if ele.attrib[key] == val:
                    return ele

    return None
