def encode(book,page,row,col):
    count = format(book,'b')
    leading_zeros = '0'*(16-len(count))
    key1 = leading_zeros+count
    count = format(page,'b')
    leading_zeros = '0'*(10-len(count))
    key2=leading_zeros+count
    count = format(row,'b')
    leading_zeros = '0'*(4-len(count))
    key3=leading_zeros+count
    count = format(col,'b')
    leading_zeros = '0'*(4-len(count))
    key4=leading_zeros+count
    key_name=key1+key2+key3+key4
    key_name = str(int(key_name, 2))
    key_name = key_name
    return key_name

def decode(ID, printer = True):
    ID = format(ID,"b")
    Length = 16+10+4+4
    b = "0"*(Length-len(ID))+ID
    book = b[0:16]
    book = int(book,2)
    page = b[16:26]
    page = int(page,2)
    row = b[26:30]
    row = int(row, 2)
    col = b[30:34]
    col = int(col, 2)

    if printer:
        print(f"Book = {book}, Page = {page}, row,col = {row,col}")
    return book, page, row,col
if __name__ == "__main__":
    #decode(263713)
    #key = int(encode(55000,200,3,3))
    #print(key, decode(key))
    print(decode(579))
