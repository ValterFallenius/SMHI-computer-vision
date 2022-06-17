import PyPDF2
IN = 'LANDSORT/landsort_1936_mod'
#pages_to_remove = [1,2,185,186,187,188,189,190,375]
#vinga_37: pages_to_remove = [1,2,9,49,66,184,185,186,371]
print(IN)
#pages_to_remove = [1,2,185,186,187,372]#leap
#pages_to_remove = [1,2,184,185,186,371]
pages_to_remove = [367]
add_blank_after = {}
move_at = {}
print(move_at)
pdf_in = open(IN+".pdf", 'rb')
pdf_reader = PyPDF2.PdfFileReader(pdf_in)
pdf_writer = PyPDF2.PdfFileWriter()

for pagenum in range(pdf_reader.numPages):

    if pagenum+1 in pages_to_remove or pagenum+1 in list(*move_at.values()):
        print("SKIP ", pagenum+1)
        continue

    page = pdf_reader.getPage(pagenum)
    pdf_writer.addPage(page)
    if pagenum+1 in list(move_at.keys()):
        for pp in move_at[pagenum+1]:
            print(f"Move {pp} to {pagenum+1}")
            page = pdf_reader.getPage(pp-1)
            pdf_writer.addPage(page)
    if pagenum+1 in list(add_blank_after.keys()):
        print(f"Add {add_blank_after[pagenum+1]} blank(s) after: ", pagenum+1)
        for i in range(add_blank_after[pagenum+1]):
            pdf_writer.addBlankPage(width = page["/MediaBox"][2],height  = page["/MediaBox"][3] )
print("PAGES: ",pdf_reader.numPages - len(pages_to_remove) + sum(add_blank_after.values()))

with open(IN + "_mod.pdf", 'wb') as pdf_out:
    pdf_writer.write(pdf_out)
    pdf_out.close()
pdf_in.close()
