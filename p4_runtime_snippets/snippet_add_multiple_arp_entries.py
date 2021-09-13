
arp_table = [(0xAC100101, 0x00000000001a), (0xAC100102, 0x00000000001b), (0xAC100103, 0x00000000001c), (0xAC100104, 0x000000000020)]

for arp_te in arp_table: 
    te = table_entry["IngressPipeImpl.arp_table"](action = "IngressPipeImpl.arp_req_to_reply") 
    te.match["hdr.arp.target_proto_addr"] = ("%d" % arp_te[0]) 
    te.action["target_mac"] = ("%d" % arp_te[1]) 
    te.insert()

mac_table = [(0x00000000001a, 0x01), (0x00000000001b, 0x02), (0x00000000001c, 0x03), (0x000000000020, 0x04)]

for mac_te in mac_table: 
    te = table_entry["IngressPipeImpl.l2_exact_table"](action = "IngressPipeImpl.set_egress_port") 
    te.match["hdr.ethernet.dst_addr"] = ("%d" % mac_te[0]) 
    te.action["port_num"] = ("%d" % mac_te[1]) 
    te.insert()