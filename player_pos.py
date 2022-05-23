import json
from binary_reader import BinaryReader
import sys

f = open(sys.argv[1], "rb")
r = BinaryReader(f.read()) # parse the opened full file result through binary reader
r.set_endian(True) # big endian
r.set_encoding("shift_jisx0213") # encoding

# player_pos.bin magic: 0x00000010 => detect export (.bin > json)
if(r.read_uint32()==16):
    fe = open(sys.argv[1] + ".json", "w", encoding='shift_jisx0213') # create or replace ("w") myfile.json > name to sys.argv (compile)
    nodecount = r.read_uint32()
    r.seek(16)

    header = {
        "Node Count": nodecount
    }

    # each individual node
    for i in range(nodecount):
        # read values
        pointer = r.read_uint32()
        vector1 = r.read_float(3)
        unk1 = r.read_uint16(2)
        map = r.read_int32()
        vector2 = r.read_float(3)
        unk2 = r.read_uint32(3)
        stay = r.pos()
        r.seek(pointer)
        string = r.read_str()
        r.seek(stay)

        # write individual dictionary node
        node = {
            "Name": string,
            "Coordinates 1": vector1,
            "Unk1": unk1,
            "Map ID": map,
            "Coordinates 2": vector2,
            "Unk2": unk2,
            }

        # add current node to header dictionary, with index showing up
        header.update({i: node}) 

    # dump full dictionary; 'ensure_ascii = False'> NEEDED for SJIS (japanese characters showing up in encoding)
    dump = json.dumps(header,indent=2,ensure_ascii = False)
    print(dump)
    fe.write(dump) # fe should potentially change in compiled


else: # player_pos.json "magic":0x7B0D0A20 (2064452128) => detect export (.bin > json)
    f = open(sys.argv[1], encoding='shift_jisx0213') # change it to "open file as text" (rather than initial binary) # might be a better way to do this than reopen the file
    fe = open(sys.argv[1] + ".bin", "wb") # create or replace ("w") myfile.bin > name to sys.argv (compile)
    w = BinaryReader()
    w.set_endian(True)
    w.set_encoding("shift_jisx0213")
    p = json.loads(f.read()) # load file to json
    nodecount = p["Node Count"]

    # write header
    w.write_uint32(16)
    w.write_uint32(nodecount)
    pointer = 48 * nodecount + 16
    w.align(pointer) # make buffer size of file - strings
    stay = 16

    for i in range(nodecount):

        node = p[str(i)]

        w.write_str(node["Name"])
        w.seek(stay)
        w.write_uint32(pointer)
        w.write_float(node["Coordinates 1"])
        w.write_uint16(node["Unk1"])
        w.write_int32(node["Map ID"])
        w.write_float(node["Coordinates 2"])
        w.write_uint32(node["Unk2"])

        stay = w.pos()
        pointer = w.size() + 1
        w.align(pointer)
        w.seek(0, whence=2)
        print(node["Name"])

    fe.write(w.buffer())
