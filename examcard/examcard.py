import xml.etree.ElementTree as Et
from pathlib import Path

from examcard.sz_funcs import _get_nodes_by_tag, _clean_str_value, _get_attrib_value, \
    _get_node_by_attrib_value
from examcard.sz_sequence import _get_parameter_data


def _get_item_content(item):  # item has id attrib
    out = dict()

    try:
        children = item.getchildren()
    except:
        children = list(item)

    for child in children:
        if child.text:
            key = _clean_str_value(child.tag)
            out[key] = child.text.strip()

    return out


def _print_info_for_node(node, root):  # root is needed for referenced nodes
    out = dict()
    try:
        children = node.getchildren()
    except:
        children = list(node)

    for child in children:
        key = _clean_str_value(child.tag)
        if child.text:  # print those that have text
            value = child.text
            out[key] = value
        else:
            # no text, in this case href directs to somewhere else
            href = _get_attrib_value(child, 'href')
            if href:
                ref = href[1:]  # change #ref-11 to ref-11

                lk = _get_node_by_attrib_value(root, 'id', ref)
                if lk:
                    value = _get_item_content(lk)
                    if value:
                        out[key] = value

    return out


def _print_tag(root, tag_name):
    out = dict()
    nodes = _get_nodes_by_tag(root, tag_name)

    if len(nodes) == 1:
        out = _print_info_for_node(nodes[0], root)
    else:
        for nd in nodes:
            key = _clean_str_value(nd.tag)
            value = _print_info_for_node(nd, root)
            if value:
                out[key] = value

    return out


def _get_one_exec_step(root, one_step):
    # get node of SingleScan
    single_scan = _get_child_thru_ref(root, one_step, 'singleScan')

    # get node of ScanProcedure
    scan_proc = _get_child_thru_ref(root, single_scan, 'scanProcedure')

    # get name of SingleScan
    name = _get_child_name(single_scan)
    if name == '':
        name = _get_child_name(scan_proc)

    # get node of parameterData
    param_data = _get_child_thru_ref(root, scan_proc, 'parameterData')

    # get node of htmlDesc
    html_desc = _get_child_thru_ref(root, single_scan, 'detail')

    # get node of dataBuffer
    data_buff = _get_child_thru_ref(root, html_desc, 'dataBuffer')

    # get node of ScanProperties
    scan_prop = _get_child_thru_ref(root, single_scan, 'scanProperties')

    # get node of ScanProcedureConfig
    proc_conf = _get_child_thru_ref(root, scan_prop, 'requiredConfiguration')

    return name, param_data, data_buff, scan_proc, scan_prop, proc_conf


def _get_child_name(node):
    try:
        children = node.getchildren()
    except:
        children = list(node)

    for child in children:
        if child.tag == 'name':
            nm = child.text
            return nm

    return ''


def _get_child_thru_ref(root, parent, child_tag):
    try:
        children = parent.getchildren()
    except:
        children = list(parent)
    ref = None
    for child in children:
        if child.tag == child_tag:
            href = _get_attrib_value(child, 'href')
            ref = href[1:]  # ref to child

    return _get_referenced_id_item(root, ref)


def _get_referenced_id_item(root, id_val):  # id_val: something like ref-81, NOT #ref-81 !!!!
    if id_val:
        for ele in root.iter():
            val = _get_attrib_value(ele, 'id')
            if val == id_val:
                return ele


def parse(filename):
    out = dict()

    filename = Path(filename)
    if not filename.exists():
        raise RuntimeError('the ExamCard file does not exist')

    try:
        tree = Et.parse(filename)
        root = tree.getroot()
    except Et.ParseError as e:
        raise RuntimeError(f'error while parsing the ExamCard: {str(e)}')
    except Exception as e:
        raise RuntimeError(f'error while parsing the ExamCard: {str(e)}')

    exec_step = _get_nodes_by_tag(root, 'ExecutionStep')

    # some info for the exam card
    out['General'] = _print_tag(root, 'ExamCard')

    for one_step in exec_step:
        name, param_data, data_buff, scan_proc, scan_prop, proc_conf = _get_one_exec_step(root, one_step)
        # all needed nodes are ready now

        # decode the dataBuffer for sequence description
        # res = seq._get_data_buffer(data_buff, seq_cnt)
        # dataBuffer info only export to pdf as it contains image

        # some more info for the sequence
        out[name] = _print_info_for_node(scan_proc, root)

        res = _print_info_for_node(scan_prop, root)
        out[name].update(res)

        res = _print_info_for_node(proc_conf, root)
        out[name].update(res)

        # work out parameterData for sequence parameters
        out[name]['protocolParameter'], enum_desc, out[name]['enumMap'] = _get_parameter_data(param_data)
        out[name]['enumDescriptions'] = [ed for h, ed in enum_desc.items()]
    return out
