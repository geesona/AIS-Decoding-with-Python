# Decode AIS string for type one messages.

# typical ATN msg = '\r\n!AIVDM,1,1,,A,ENlt;J@aSqP0000000000000000E;WUdm7Mu800003vP10,4*45\r\n'
#                 = !AIVDM,2,1,2,A,54`UvMD1ptHH?H@cF204<4<T6222222222222216AhcC=5`:0Gm21EQCPDQ8,0*46
#                   !AIVDM,2,2,9,A,C8888888880,2*56
#                   !AIVDM,2,2,2,B,C8888888880,2*5E
#                   !AIVDM,2,2,4,A,C8888888880,2*5B
#                   !AIVDM,2,2,5,B,C8888888880,2*59
#('503055460', 'ALLWAYS SUNDAY G777. ', '\r\n!AIVDM,1,1,,B,H7Oh4I04hiL5U>1=Dp@5V0OOOL0,2*0D\r\n')
#('503055460', 'ALLWAYS SUNDAY G777. ', '\r\n!AIVDM,1,1,,A,H7Oh4I04hiL5U>1=Dp@5V0OOOL0,2*0E\r\n')
#('503055460', 'ID5.1- *NM^].L0.NAPQ ', '\r\n!AIVDM,1,1,,A,H7Oh4I4TCD36n2`pmqnpk00p5150,0*35\r\n') = faulty message??
#('503055460', 'ID5.1- *NM^].L0.NAPQ ', '\r\n!AIVDM,1,1,,B,H7Oh4I4TCD36n2`pmqnpk00p5150,0*36\r\n')
 
def msg_to_bin(psn):               # typical ATN msg = '\r\n!AIVDM,1,1,,A,ENlt;J@aSqP0000000000000000E;WUdm7Mu800003vP10,4*45\r\n'
     global length
     global bin_data
     length = 0
     bin_data = 0
     start_psn = psn               # remember the original psn for later
     while data[psn] != "," :      # loop around the characters to the next comma
          length += 1              # count the characters in the message
          psn += 1                 # move to the next character
     end_psn = start_psn + length
     for n in range (start_psn, end_psn):
          r = ord (data[n])            # convert each character to binary
          r = r - 48                   # subtract 48 to reduce each character to 6 bits
          if r > 40:                   # if still to big reduce some more
               r = r - 8               # used to compress the lower case characters
          bin_data = bin_data + r      # add the next number to the cumulative number
          bin_data = operator.lshift (bin_data,6)  # shift the cumulative number up to make space for the next char
     bin_data = operator.rshift (bin_data,6)
     psn = start_psn                    # reset psn to original
     return bin_data


def bin_data_slice(length, slice_length, end_bit):     # length in 6 bit bytes
     number_of_bits = length * 6                       # calc number of bits in data
     if end_bit < number_of_bits :
          bit_length = 0
          movement = 0
          mask = 01                                         # the 1 required to shift for the mask
          global bin_slice                                  # the final result value
          movement = (number_of_bits - end_bit)             # work out how many trailing bits beyond the required slice
          movement = movement - 1
          bd = bin_data                                     # re load the original binary data bits
          bd = operator.rshift (bd, movement)               # right shift to remove unwanted lower bits
          for nn in range (1, slice_length):                # loop around for the slice_length filling with 1s
               mask = operator.lshift (mask,1)              # 
               mask = mask + 1
          bin_slice = bd & mask                             # remove unwanted upper bits
     else :
          print (data)
          print (" ERROR ____________________________________________")
          exit()
     return bin_slice


def calc_msg_type():
     global id
     bin_data_slice (length, 6, 5)
     id = bin_slice
     return id


def get_text(length, bits, slice_end):
     bin_data_slice(length, bits, slice_end)           # find name slice from the binary string
     bs = bin_slice
     chars = bits / 6                                  # calc how many chars in the bit stream
     chars = chars + 1                                 # an extra one to cover the remainder
     global text
     text = " "                                        # empty string to start off with
     for nn in range (1, chars):                       # loop for each char in text
          char_bits = bs & 63                          # get the 6 least significant bits for a char
          char = tc[char_bits]                         # get the char from the tc dictionary
          text = char + text                           # add the new char to the left hand end of text string
          bs = operator.rshift (bs, 6)                 # remove the char we just saved as text and loop
     return text                   


def get_lat(length, bits, slice_end):
     global Lat
     bin_data_slice(length, bits, slice_end)           # find latidude slice of the binary string
     bs = bin_slice
     bs = bs ^ 0b111111111111111111111111111           # 2's compliment xor with 27 bit mask
     bs = bs + 1                                       # add one for 2's compliment
     Lat = bs/-600000.00
     return Lat


def get_long(length, bits, slice_end):
     global Long
     bin_data_slice(length, bits, slice_end)           # find latidude slice of the binary string
     bs = bin_slice
     Long = bs/600000.00
     return Long


def get_ns(length, bits, slice_end):
     global n_stat
     bin_data_slice(length, bits, slice_end)
     nav = bin_slice
     n_stat = ns[nav]
     return n_stat


def test_lat_long(lat, long):
     global dist
     global max_dist
     global MMSI
     global md_dist
     global total
     valid_lat = False
     valid_long = False
     if Lat > -90 :
          valid_lat = True
          if Long < 180 :
               valid_long = True
               coords_1 = (-38.08705, 144.361) # (lat, Long)
               coords_2 = (Lat, Long)
               dist = geopy.distance.vincenty(coords_1, coords_2).km
               dist = dist * 0.5399          # convert from kilometres to nautical miles
     if valid_lat == False or valid_long == False :
#          print ("Invalid Position", ship )
          sh = str(ship)
          error = ("Invalid Position from " + sh )
          err_msg(error)
          dist = 0
     return (dist)

def err_msg(error_msg):
     f4 = open("error.txt","a")
     l_time = time.localtime(time.time())
     tmnow = time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time()))          # %Y-%m-%d %H:%M:%S
     e_msg = (str(tmnow) + " " + error_msg + "\n")
     f4.write(e_msg)
     f4.close()
     return ()


import socket
import time
import operator
import geopy.distance
import os


UDP_IP = "192.168.0.15"   # as set up in Marine Traffic Dash 192.168.0.15
UDP_PORT = 40005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

sock.bind((UDP_IP, UDP_PORT))


tc = {}
tc[0] = "."
tc[1] = "A"
tc[2] = "B"
tc[3] = "C"
tc[4] = "D"
tc[5] = "E"
tc[6] = "F"
tc[7] = "G"
tc[8] = "H"
tc[9] = "I"
tc[10] = "J"
tc[11] = "K"
tc[12] = "L"
tc[13] = "M"
tc[14] = "N"
tc[15] = "O"
tc[16] = "P"
tc[17] = "Q"
tc[18] = "R"
tc[19] = "S"
tc[20] = "T"
tc[21] = "U"
tc[22] = "V"
tc[23] = "W"
tc[24] = "X"
tc[25] = "Y"
tc[26] = "Z"
tc[27] = "["
tc[28] = "." # this is upposed to be a \
tc[29] = "]"
tc[30] = "^"
tc[31] = "_"
tc[32] = " "
tc[33] = "!"
tc[34] = '"'
tc[35] = "#"
tc[36] = "$"
tc[37] = "%"
tc[38] = "&"
tc[39] = "'"
tc[40] = "("
tc[41] = ")"
tc[42] = "*"
tc[43] = "+"
tc[44] = ","
tc[45] = "-"
tc[46] = "."
tc[47] = "/"
tc[48] = "0"
tc[49] = "1"
tc[50] = "2"
tc[51] = "3"
tc[52] = "4"
tc[53] = "5"
tc[54] = "6"
tc[55] = "7"
tc[56] = "8"
tc[57] = "9"
tc[58] = ":"
tc[59] = ";"
tc[60] = "<"
tc[61] = "="
tc[62] = ">"
tc[63] = "?"

ns = {}             # navigation status
ns[0] = "Under way"
ns[1] = "At anchor"
ns[2] = "Not under command"
ns[3] = "Restricted Manoeuverability"
ns[4] = "Constrained by he draught"
ns[5] = "Moored"
ns[6] = "Aground"
ns[7] = "Engaged in fishing"
ns[8] = "Under way sailing"
ns[9] = "Reserved"
ns[10] = "Reserved"
ns[11] = "Reserved"
ns[12] = "Reserved"
ns[13] = "Reserved"
ns[14] = "AIS-SART is active"
ns[15] = "Reserved"

global cntr
global md_avg
global mdt

hr_cnt = 0
vcount = 0
max_dist = 0
total_dists = 0
bs_count = 0
cntr = 0
mdt = 0
dist = 0
MMSI = 0
mmsi = 0
Lat = 0
Long = 0
md_avg = 0
md_mmsi = "a"
md_dist = "a"
sp = " "
total = 0
count = 0
vessels = set()
atns = set()
mi = dict()
at = {}             # This is a dict
vs = dict()
bs = dict()
bv = dict()
master_db = dict()  # for mmsi and ships names
bmast = dict()

atlst = list()
vslst = list()
bslst = list()
mtlst = list()
masterlst = list()
bmasterlst = list()
mmsi_list = list()
vlist = list()      # Value list for dictionary
bvlst = list()
md_avg_lst = list()
mmsi_set = set()
mmsi_dict = dict()
mmsi_dict = {} 

localtime = time.localtime(time.time()) 

hour_limit = localtime[3]  # hour_limit is set to the hour value
while hr_cnt < 3000 :
     f1 = open("ais.txt","a")
     f5 = open("graph.txt","a")

     for line in open ("master.txt"):
          mtlst.append("line")
          mmsi_x = (line[:9])
          if mmsi_x not in master_db:
               master_db[mmsi_x] = line

     for line in open ("bmast.txt"):
          mmsi_x = (line[:9])
          if mmsi_x not in bmast:
               bmast[mmsi_x] = line     # put in dictionary


     localtime = time.localtime(time.time())
     print('\a')     # Make beep sound
     while hour_limit == localtime[3] : # run for run_time
          data, addr = sock.recvfrom(90) # buffer size is up to 90 bytes
          cnt = 0
          psn = 0
          while cnt < 5 :
               a = data[psn]   # Loop around the data until 5 commas have passed
               if a == "," :   # to find the start of data position.
                    cnt += 1
               psn += 1
          msg_type = psn - 2
          msg_to_bin(psn)      # Converts the msg to binary and calculates length
          calc_msg_type()

          if data[11] == '1' : # Check that the message is the first of a possible number of sequenced messages

               if id == 1 or id == 2 or id == 3 :      # Position Reports
                    vcount += 1
                    print ("\033c")                    # clear the screen
                    print hr_cnt
                    bin_data_slice(length, 30, 37)     # find mmsi slice of the binary string
                    MMSI = str(bin_slice)
                    ship = int(bin_slice)
                    vessels.add(ship)
                    get_lat(length, 27, 115)           # find lat slice and convert to latitude
                    lt = Lat
                    lt = str(Lat)
                    v_lat = ("%0.5f" % (Lat))

                    get_long(length,28,88)             # find long slice
                    lg = Long
                    lg = str(Long)
                    v_long = ("%0.5f" % (Long))

                    get_ns(length, 4, 41)              # find the navigation status
                    bin_data_slice(length, 10, 59)
                    speed = int(bin_slice)
                    if speed == 0 and n_stat == "Under way" :
                         n_stat = "Stopped"
                    test_lat_long(Lat, Long)
                    if dist != 0 :
                         if dist < 400 :
                              if max_dist < dist :
                                   max_dist = dist
                              md_dist = str(max_dist)
                         total_dists = total_dists + dist   # caluculate the average distance for type 1,2,3 msgs
                         av_dist = total_dists / vcount
                    dt = ("%8.5f" % (dist))
                    if MMSI in vs :
                         if dist != 0 :
                              v_info = vs[MMSI]             # read the existing info
                              ship_name = v_info[15:35]     # cut the ships name
                              msg_count = v_info[11:13]     # cut the msg count
                              msg_count = int(msg_count)    # convert it to an integer
                              msg_count += 1                # increment it by one
                              msg_count = '{:03d}'.format(msg_count)  # Format it into three characters
                              v_info = (MMSI + " " + msg_count + "  " + ship_name + "  " + dt + " " + v_lat + " " + v_long + " " + n_stat)
                              vs[MMSI] = v_info             # Replace the data string
                    else :
                         if MMSI in master_db :
                              sh_name = master_db[MMSI]
                              sh_name = sh_name[10:30]
                              v_info = (MMSI + " " + "000" + "  " + sh_name + "  " + dt + " " + v_lat + " " + v_long + " " + n_stat)
                         else :
                              v_info = (MMSI + " " + "000" + "  " + "...................." + "  " + dt + " " + v_lat + " " + v_long + " " + n_stat)
                         vs[MMSI] = v_info
                    vslst = list(vs)

                    for x in vslst :                   # print out the 1,2,3 type msgs
                         vs_info = vs[x]
                         print (vs_info)
                    now = time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time()))          # %Y-%m-%d %H:%M:%S
                    vc = str(vcount)
                    no_v = str(len(vessels))
                    data =  ( "max = " + "%.4f" % max_dist + "  avg = " + "%.4f" % av_dist + "  msgs = " + vc + "  vessels = " + no_v + "  " + str(now))
                    print data
                    data = ("md_avg = " + "%.5f" %md_avg + " " + "count = " + str(len(md_avg_lst)) + " " + "total = " + "%.5f" % mdt )
                    print data
                    print (" ")

                    for x in bvlst :                   # print out the type 18 msgs
                         bv_info = bv[x]
                         print (bv_info)
                    print (" ")

                    for x in atlst :                   # print out the type 21 msgs
                         at_info = at[x]
                         print (at_info)
                    print (" ")

                    for x in bslst :                   # print out the type 4 msgs
                         bs_info = bs[x]
                         print (bs_info)


               if id == 4 :             # Base Station Report
                    bin_data_slice(length, 30, 37)     # find mmsi slice of the binary string
                    mmsi_2 = str(bin_slice)
#                    bsc = '{:03d}'.format(bs_count)      # '{:04d}'.format(42)
                    bsn = str(mmsi_2 + " " + "000")
                    get_lat(length, 27, 133)
                    lt = str(Lat)
                    lt = ("%0.5f" % (Lat))
                    get_long(length, 28, 106)
                    lg = str(Long)
                    lg = ("%0.5f" % (Long))
                    test_lat_long(Lat, Long)
                    dt = ("%0.5f" % (dist))
                    if mmsi_2 not in bs :
                         bs[mmsi_2] = bsn
                    if mmsi_2 in bs:
                         bs_info = bs[mmsi_2]               # read the old info
                         slice_bs_info = bs_info[8:11]      # select the message count
                         ff = int(slice_bs_info)            # turn it into an integer
                         ff += 1                            # add one to it
                         ff = '{:03d}'.format(ff)           # format it into three digits
                         bs_info = str(mmsi_2 + " " + ff + " " + dt + " " + lt + " " + lg)
                         bs[mmsi_2] = bs_info               # replace the dictionary string
                    bslst = list(bs)                        # turn the dictionary into a list

               if id == 5 :                            # Static and Voyage related data
                    bin_data_slice(length, 30, 37)     # find mmsi slice of the binary string
                    mmsi_3 = str(bin_slice)
                    get_text(length, 120, 231)         # find name slice and convert to text
                    ship_name = text
                    get_text(length, 42, 111)           # find call sign
                    call_sign = text
                    if mmsi_3 not in master_db :
                         master_db[mmsi_3] = (mmsi_3 + " " + ship_name + "\n")
                    if mmsi_3 in vs :
                         s_name = vs[mmsi_3]
                         s_name = s_name.replace("....................", ship_name)
                         vs[mmsi_3] = s_name
#                    else :
#                         ve_info = (MMSI + " " + "000" + "  " + ship_name)
#                         vs[mmsi_3] = ve_info
#                         print (ve_info, "not in vs - waiting")



               if id == 18 :            # B vessels position report
                    bin_data_slice(length, 30, 37)          # get the mmsi slice
                    mmsi_4 = str(bin_slice)
                    get_lat(length, 27, 111)                # get the latitude
                    blt = ("%0.5f" % (Lat))                         
                    get_long(length, 28, 84)                # get the long
                    blg = ("%0.5f" % (Long))
                    test_lat_long(Lat, Long)
                    dt = ("%8.5f" % (dist))
                    ship_name = "...................."
                    if mmsi_4 in bmast :
                         bm_info = bmast[mmsi_4]
                         ship_name = bm_info[10:30]
                    bc = (mmsi_4 + " " + "000" + "  " + ship_name + " " + dt + " " + blt + " " + blg)
                    if mmsi_4 not in bv :
                         bv[mmsi_4] = bc
                    else :
                         b_info = bv[mmsi_4]
                         bcount = b_info[11:13]
                         bcount = int(bcount)
                         bcount += 1
                         bcount = '{:03d}'.format(bcount)
                         bv[mmsi_4] = (mmsi_4 + " " + bcount + "  " + ship_name + "  " + dt + " " + blt + " " + blg)
#                    bvlst = list(bv)


               if id == 24 :            # Type B vessels name
                    bin_data_slice(length, 30, 37)          # get the mmsi slice
                    mmsi_5 = str(bin_slice)
                    bin_data_slice(length, 2, 39)
                    part_no = int(bin_slice)
                    if part_no == 0 :
                         get_text(length, 120, 159)              # get the ship's name
                         ship_name = text
                         if mmsi_5 not in bmast :
                              bmast[mmsi_5] = (mmsi_5 + " " + ship_name + "\n")
                         ban = (mmsi_5 + " " + "000" + "  " + ship_name)
                         if mmsi_5 not in bv :                   # update the bv
                              bv[mmsi_5] = ban
                         else :
                              bmsg = bv[mmsi_5]
                              bcount = bmsg[11:13]
                              bcount = int(bcount)
                              bcount += 1
                              bcount = '{:03d}'.format(bcount)
                              bmsg = bmsg.replace(".................... ", ship_name)
                              bv[mmsi_5] = bmsg
                         bvlst = list(bv)


               if id == 21 :            # Aid to navigation reports
                    bin_data_slice(length, 30, 37)     # find mmsi slice of the binary string
                    mmsi_1 = str(bin_slice)
                    get_text(length, 120, 162)         # find name slice and convert to text
                    name = text
                    get_lat(length, 27, 218)           # find lat slice and convert to latitude
                    lt = Lat
                    lt = ("%0.5f" % (Lat))
                    get_long(length, 28, 191)          # find long slice and convert to longitude
                    lg = ("%0.5f" % (Long))
                    test_lat_long(Lat, Long)
                    dt = str("%8.5f" % (dist))
                    info = (mmsi_1 + " " + "0000" + "  " + name + " " + dt + " " + lt + " " + lg)
                    if mmsi_1 not in at:
                         at[mmsi_1] = info
                    else :
                         at_info = at[mmsi_1]
                         atcount = at_info[10:14]
                         at_count = int(atcount)
                         at_count += 1
                         at_count = '{:04d}'.format(at_count)
                         at[mmsi_1] = (mmsi_1 + " " + at_count + "  " + name + " " + dt + " " + lt + " " + lg)
                    atlst = list(at)

               localtime = time.localtime(time.time())


     sp = ", "

     ships = len(vessels)
     result = md_dist + sp + "%.5f" % av_dist + sp + str(vcount) + sp + str(len(vessels)) + sp + str(now) + sp + str(md_avg) + '\n'
     result1 = str(hr_cnt) + sp + md_dist + sp + "%.5f" % av_dist + sp + str(vcount) + sp + str(len(vessels)) + sp + str(now) + sp + str(md_avg)+'\n'

     if len(md_avg_lst) < 24 :                         # if less than the rolling average length number
          md_avg_lst.append(max_dist)                   # copy the max_distance string into the list
          mdt = 0
          mdt = sum(md_avg_lst)
          print ("mdt =", mdt)
          md_avg = mdt / len(md_avg_lst)               # divide the total by the list length to find average
     else :
          if len(md_avg_lst) == 24 :
               cntr += 1
          if cntr == 24 :
               cntr = 0
          md_avg_lst[cntr] = (max_dist)
          mdt = sum(md_avg_lst)
          md_avg = mdt / 24


     os.remove("master.txt")
     masterlst = list(master_db)
     f2 = open("master.txt","a")
     for x in masterlst :               # save the master database with mmsi & shipnames
          mt_info = master_db[x]
          f2.write(mt_info)
     f2.close()

     os.remove("bmast.txt")
     bmasterlst = list(bmast)
     f3 = open("bmast.txt","a")
     for x in bmasterlst :               # save the master database with mmsi & shipnames
          mt_info = bmast[x]
          f3.write(mt_info)
     f3.close()

     for x in vslst :                   # write to file the type 1,2,3 msgs
          vs_info = vs[x]
          f1.write(vs_info + "\r\n")
     f1.write(result + "\r\n")
     f5.write(result1)

     for x in bvlst :                  # write to file the type 18 msgs
          bv_info = bv[x]
          f1.write(bv_info + "\r\n")
     f1.write("\r\n")
     f1.close()

     print('\a')     # Make beep sound
     max_dist = 0
     dist = 0
     mmsi = 0
     MMSI = 0
     total_dists = 0
     av_dist = 0
     vcount = 0
     vessels = set()
     mi = dict()
     at.clear()     # empty the type 21 msg dictionary
     bs.clear()     # empty the type 4 msg dictionary
     bv.clear()     # empty the type 18 msg dictionary
     vs.clear()     # empty the type 1,2,3 msg and type 5 dictionary
     vslst = []
     bvlst = []
     atlst = []
     bslst = []
     mmsi_dict.clear()
     hour_limit = localtime[3]
     hr_cnt += 1


sock.close()


# 14/7/2019 Added the hour count and daily running average to the file graph.txt
# 14/7/2019 Removed "invalid position" print
# 14/7/2019 Added the else into id 5
# 14/7/2019 Removed \n from f5 write
# 14/7/2019 Added "if dist != 0" to type 1,2 & 3 msgs
# 15/7/2019 Renoved the else in id 5 as duplicates appearing



