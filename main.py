from extract_table_pdf import LerPdf

read = LerPdf(name_pdf="AMBEV",num_pages=12) #Incluir nome do arquivo pdf, sem a extensão, e numero de páginas

read.extract_table()
read.concat_row()
read.make_final_file()