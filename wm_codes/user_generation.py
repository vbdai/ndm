import numpy as np
import random
import hamming_codec

def generate_ID(ID_length=15, n_user=10, ecc=False):
    #function for generating IDs according to the Hamming codes
    #n_user  = 10
    ID_tbl = []
    ID_tbl_bit = []
    #ID_tbl =  possible_IDs[chosen_idx]
    ID_tbl = np.random.choice(np.arange(0,2**ID_length), n_user, replace=False)
    for ID in ID_tbl: #number of users, for each user create and ID
        if ecc:
            encoded_message = hamming_codec.encode(int(ID), ID_length)
        else:
            encoded_message = f'{ID:0{ID_length}b}'
        ID_tbl_bit_each = []
        for bit_here in encoded_message:
            ID_tbl_bit_each.append(bit_here == '1')
        ID_tbl_bit.append(ID_tbl_bit_each)

#    numbers = range(0, 9)
#    return random.sample(numbers, 5)
    ID_tbl_bit = np.array(ID_tbl_bit)
    ID_tbl = np.array(ID_tbl)
    #print(ID_tbl)
    #print(ID_tbl_ch)
    #print(ID_tbl_bit)
    return ID_tbl,ID_tbl_bit

def ID_to_bit(ID_tbl,ID_length, ecc=False):
    ID_tbl_bit = []
    for ID in ID_tbl:  # number of users, for each user create and ID
        if ecc:
            encoded_message = hamming_codec.encode(int(ID), ID_length)
        else:
            encoded_message = f'{int(ID):0{ID_length}b}'
        ID_tbl_bit_each = []
        for bit_here in encoded_message:
            ID_tbl_bit_each.append(bit_here == '1')
        ID_tbl_bit.append(ID_tbl_bit_each)

    #    numbers = range(0, 9)
    #    return random.sample(numbers, 5)
    ID_tbl_bit = np.array(ID_tbl_bit)
    ID_tbl = np.array(ID_tbl)
    # print(ID_tbl)
    # print(ID_tbl_ch)
    # print(ID_tbl_bit)
    return ID_tbl, ID_tbl_bit

def generate_trx(ID_tbl, n_message=5):
    n_ID = ID_tbl.shape[0]
    owner_buyer_IDs = np.random.randint(n_ID, size=(2, n_message))
    for i in np.arange(n_message):
       if owner_buyer_IDs[0,i] ==owner_buyer_IDs[1,i]:
           replace_num = owner_buyer_IDs[0,i]
           while replace_num == owner_buyer_IDs[0,i]:
               replace_num = np.random.randint(n_ID)
           owner_buyer_IDs[0, i] = replace_num
    #print(owner_buyer_IDs)
    message = []
    #message_bit = []
    for i in np.arange(n_message):
        owner_index      = owner_buyer_IDs[0, i]
        buyer_index      = owner_buyer_IDs[1, i]
        message_here = np.concatenate((ID_tbl[owner_index], ID_tbl[buyer_index]), axis=None)
        #message_bit_here = np.concatenate((ID_tbl_bit[owner_index], ID_tbl_bit[buyer_index]), axis=0)
        message.append(message_here)
        #message_bit.append(message_bit_here)
    message = np.array(message)
    #message_bit = np.array(message_bit)
    return message #, message_bit


def trx_to_bit(trx, ID_length, ecc=False):
    message_bit = []
    for tuple in trx:
        owner = tuple[0]
        buyer = tuple[1]
        if ecc:
            owner_bits = hamming_codec.encode(int(owner), ID_length)
            buyer_bits = hamming_codec.encode(int(buyer), ID_length)
        else:
            owner_bits = f'{int(owner):0{ID_length}b}'
            buyer_bits = f'{int(buyer):0{ID_length}b}'

        message_bit_here = owner_bits+buyer_bits # np.concatenate((owner_bits, buyer_bits), axis=0)
        message_bit_here_bol = []
        for bit_here in message_bit_here:
            message_bit_here_bol.append(bit_here == '1')

        message_bit.append(message_bit_here_bol)
    message_bit = np.array(message_bit)
    return message_bit


def recover_ID(ID_tbl_ch,decoded_msgs):
    dec_ID_tbl_ch = []
    for ID in decoded_msgs:
        dec_ID_ch_each = []
        for i in np.arange(0,len(ID),7):
            bits = ''.join(str(int(x)) for x in ID[i:i+7])
            bits = bytes(bits, encoding="raw_unicode_escape")
            char = bits2string(bits)
            dec_ID_ch_each.append(char)
        dec_ID_tbl_ch.append(dec_ID_ch_each)

    ID_tbl_ch = np.array(ID_tbl_ch)
    dec_ID_tbl_ch = np.array(dec_ID_tbl_ch)
    recover_msgs = []
    for dec_ID_ch in dec_ID_tbl_ch:
        diff = []
        dif_aray = dec_ID_ch !=ID_tbl_ch
        #print(dif_aray)
        diff = np.sum(dif_aray,axis=1)
        #print(diff)
        min_index = np.argmin(diff)
        #print(min_index)
        recover_msgs.append(ID_tbl_ch[min_index])

    recover_msgs = np.array(recover_msgs)
    #print(ID_tbl_ch)
    #print(decoded_msgs)
    #print(recover_msgs)
    #print(accuracy_ID_extraction(ID_tbl_ch[0:3], np.array(dec_ID_tbl_ch)))
    #print(accuracy_ID_extraction(ID_tbl_ch[0:3],recover_msgs))
    return recover_msgs

def recover_ID_SSL(ID_tbl_ch,decoded_msgs): #6 characters => split it two three chars
    dec_ID_tbl_ch = []
    for ID in decoded_msgs:
        dec_ID_ch_each = []
        for i in np.arange(0,len(ID),7):
            bits = ''.join(str(int(x)) for x in ID[i:i+7])
            bits = bytes(bits, encoding="raw_unicode_escape")
            char = bits2string(bits)
            dec_ID_ch_each.append(char)
            if i%3==2:
                dec_ID_tbl_ch.append(dec_ID_ch_each)
                dec_ID_ch_each = []

    ID_tbl_ch = np.array(ID_tbl_ch)
    dec_ID_tbl_ch = np.array(dec_ID_tbl_ch)
    recover_msgs = []
    for dec_ID_ch in dec_ID_tbl_ch:
        diff = []
        dif_aray = dec_ID_ch !=ID_tbl_ch
        #print(dif_aray)
        diff = np.sum(dif_aray,axis=1)
        #print(diff)
        min_index = np.argmin(diff)
        #print(min_index)
        recover_msgs.append(ID_tbl_ch[min_index])

    recover_msgs = np.array(recover_msgs)
    #print(ID_tbl_ch)
    #print(decoded_msgs)
    #print(recover_msgs)
    #print(accuracy_ID_extraction(ID_tbl_ch[0:3], np.array(dec_ID_tbl_ch)))
    #print(accuracy_ID_extraction(ID_tbl_ch[0:3],recover_msgs))
    return recover_msgs

def recover_ID_SSL_bits(ID_tbl,decoded_msgs_bits,n_decoded_bits = 20,ecc=False): #40 bits => split it two 20bits
    dec_ID_tbl = []
    for ID in decoded_msgs_bits:
        dec_ID_ch_each = []
        for i in np.arange(0,len(ID),n_decoded_bits):
            bits = ''.join(str(int(x)) for x in ID[i:i+n_decoded_bits])
            if ecc:
                decoded_each = hamming_codec.decode(int(bits, 2), len(bits))
                dec_ID_tbl.append(int(decoded_each,2))
            else:
                dec_ID_tbl.append(int(bits, 2))

    ID_tbl = np.array(ID_tbl)
    dec_ID_tbl = np.array(dec_ID_tbl)
    recover_msgs = dec_ID_tbl
    #recover_msgs = []

    # another layer of corrections by comparing against the user table
    #for dec_ID_ch in dec_ID_tbl:
    #    diff = []
    #    XORed  = np.bitwise_xor(dec_ID_ch, ID_tbl)
    #    diff   = np.array([bin(x).count("1")  for x in XORed])
    #    #print(diff)
    #    min_index = np.argmin(diff)
    #    #print(min_index)
    #    recover_msgs.append(ID_tbl[min_index])

    #recover_msgs = np.array(recover_msgs)
    return recover_msgs

def accuracy_ID_extraction(msgs_ch,decoded_msgs_ch):
    msgs_ch       = np.array(msgs_ch)
    decoded_msgs_ch      = np.array(decoded_msgs_ch)
    eq = msgs_ch == decoded_msgs_ch
    sum_eq               = np.sum(eq)
    accuracy             = sum_eq/float(decoded_msgs_ch.shape[0])                   #np.sum(sum_dif==3)/float(decoded_msgs_ch.shape[0])
    return accuracy

def bits2string(b=None):
    return ''.join([chr(int(b, 2))])

def test_accuracy():
     msgs_ch         = [['a','b','c'],['e','f','g'],['h','i','j']]
     decoded_msgs_ch = [['a','b','c'],['g','h','f'],['a','i','j']]
     print(accuracy_ID_extraction(msgs_ch,decoded_msgs_ch))

def test_recover_ID():
    ID_tbl_ch = [['1', '+', 'k'], ['#', '@', ':'], ['w', '2', 'r'], ['\x0e', '\x7f', 'y'], ['T', 'U', 'H'], ['i', 'G', 'A'], ['?', '\x1d', '\x02'], ['\x00', 'c', 'V'], ['\x1c', 'q', '\x10'], ['M', '\x01', '\x17']]
    decoded_msgs_str = [['011000101010111101011'], ['010001110000000111010'], ['111011101100101110011']]
    decoded_msgs_bit = []
    for bits_str in decoded_msgs_str:
        #print(bits_str[0])
        decoded_msgs_bit.append([x == '1' for x in bits_str[0]])
    #print(decoded_msgs_bit)
    recover_ID(ID_tbl_ch,decoded_msgs_bit)

def generate_trx_v0(ID_tbl_ch, ID_tbl_bit, n_message=5):
    n_ID = ID_tbl_ch.shape[0]
    owner_buyer_IDs = np.random.randint(n_ID, size=(2, n_message))
    for i in np.arange(n_message):
       if owner_buyer_IDs[0,i] ==owner_buyer_IDs[1,i]:
           replace_num = owner_buyer_IDs[0,i]
           while replace_num == owner_buyer_IDs[0,i]:
               replace_num = np.random.randint(n_ID)
           owner_buyer_IDs[0, i] = replace_num
    #print(owner_buyer_IDs)
    message = []
    message_bit = []
    for i in np.arange(n_message):
        message_here     = []
        message_bit_here = []
        owner_index      = owner_buyer_IDs[0, i]
        buyer_index      = owner_buyer_IDs[1, i]
        #print(ID_tbl_ch[owner_index])
        #print(ID_tbl_ch[buyer_index])
        message_here = np.concatenate((ID_tbl_ch[owner_index], ID_tbl_ch[buyer_index]), axis=None)
        message_bit_here = np.concatenate((ID_tbl_bit[owner_index], ID_tbl_bit[buyer_index]), axis=0)
        #print(message_here,message_bit_here)
        #''.join(x for x in ID_tbl_bit[owner_index]+ID_tbl_bit[buyer_index])
        message.append(message_here)
        message_bit.append(message_bit_here)
    message = np.array(message)
    message_bit = np.array(message_bit)
    #print(message)
    #print(message_bit)
    #print(message_bit.shape)
    return message, message_bit

def generate_ID_v0(l_string=3, n_user=10):

    #l_string = 3
    #n_user  = 10
    ID_tbl = []
    #ASCI length 128
    l_asci = 128
    dif_bit = 7
    char_candidates = []
    #list of candidates for first/second/third ...
    for id_char in np.arange(l_string):
        candidates = np.arange(id_char,l_asci,dif_bit)
        char_candidates.append(candidates)

    for cnt_user in np.arange(n_user): #number of users, for each user create and ID
        ID_user = []
        generate_again=True
        while generate_again:
            for cnt_char in np.arange(l_string):
                char = random.choice(char_candidates[cnt_char])

                if len(ID_tbl) !=0:
                    ID_tbl_np = np.vstack(ID_tbl)
                    #ID_tbl_np = np.asarray(ID_tbl)
                    #print(ID_table_np[:,cnt_char])
                    # if it is already created, created new one unless we have chosen all possible cases
                    while (char in ID_tbl_np[:,cnt_char]) & (len(list(set(ID_tbl_np[:,cnt_char])))<len(char_candidates[cnt_char])):
                        char = random.choice(char_candidates[cnt_char])
                    ID_user.append(char)
                else:
                    ID_user.append(char)

            #print(ID_user)
            if ID_user not in  ID_tbl:
                if len(ID_user)>3:
                    print("oops")
                ID_tbl.append(ID_user)
                generate_again = False
            else:
                ID_user =[]

    ID_tbl_bit = []
    ID_tbl_ch = []
    for ID_user in ID_tbl:
        ID_tbl_ch_each = []
        ID_tbl_bit_each = []
        for char in ID_user:
            char_of_num = chr(int(char))
            ID_tbl_ch_each.append(char_of_num)
            bit_string = ' '.join(f"{ord(char_of_num):07b}")

            for i, bit_here in enumerate(bit_string):
                if i%2 ==0:
                    ID_tbl_bit_each.append(bit_here =='1')
        #ID_tbl_bit_each.append(ID_tbl_bit_each_here)
        #ID_tbl_bit_each.append(bit_string=='1')
        ID_tbl_bit.append(ID_tbl_bit_each)
        ID_tbl_ch.append(ID_tbl_ch_each)

    ID_tbl_ch = np.array(ID_tbl_ch)
    ID_tbl_bit = np.array(ID_tbl_bit)
    ID_tbl = np.array(ID_tbl)
    #print(ID_tbl)
    #print(ID_tbl_ch)
    #print(ID_tbl_bit)
    return ID_tbl_ch,ID_tbl_bit,ID_tbl

if __name__=='__main__':
    #generate_message(5)
    #generate_ID()
    #test_accuracy()
    test_recover_ID()