def encode(book,page,position):
    count = format(book,'b')
    leading_zeros = '0'*(16-len(count))
    key1 = leading_zeros+count
    count = format(page,'b')
    leading_zeros = '0'*(10-len(count))
    key2=leading_zeros+count
    count = format(position,'b')
    leading_zeros = '0'*(8-len(count))
    key3=leading_zeros+count
    key_name=key1+key2+key3
    key_name = str(int(key_name, 2))
    key_name = key_name
    return key_name

def decode(ID, printer = True):
    ID = format(ID,"b")
    Length = 16+10+8
    b = "0"*(Length-len(ID))+ID
    book = b[0:16]
    book = int(book,2)
    page = b[16:26]
    page = int(page,2)
    position = b[26:34]
    position = int(position, 2)
    if printer:
        print(f"Book = {book}, Page = {page}, position = {position}")
    return book, page, position
if __name__ == "__main__":
    #decode(263713)
    key = int(encode(55000,200,255))
    print(key, decode(key))
