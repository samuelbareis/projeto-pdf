
import tabula
import pandas as pd
import numpy as np
import os

class LerPdf():
    def __init__(self,name_pdf:str,num_pages:int):
        self.num_pages = num_pages + 1
        self.name_pdf = name_pdf
    def extract_table(self):

        print("Lendo arquivo {}.pdf...".format(self.name_pdf))
        for page in range(self.num_pages):
            
            if page == 0:
                pass

            elif page == 1:

                tabela = tabula.read_pdf("./pdfs/{}.pdf".format(self.name_pdf), pages="1")

                df = tabela[0]

                df.columns = df.iloc[2]

                df = df[2:]

                df.reset_index(drop=True, inplace=True)

                df = df.drop([0, 1, 2])

                df.to_csv("./bruto/{}_{}.csv".format(self.name_pdf,page), index=False)
            
            elif page > 1:
                try:
                    tabela = tabula.read_pdf("./pdfs/{}.pdf".format(self.name_pdf), pages= "{}".format(page))
                    df = tabela[0]
                    df.to_csv("./bruto/{}_{}.csv".format(self.name_pdf,page), index=False)
                except Exception as e:
                    print(f"Ocorreu um erro: {e}")

    def __concat_rows_ignore_nan(self,df:pd.DataFrame, col_name):
        result = []
        skip = False 

        for i in range(len(df) - 1):
            if skip:
                skip = False
                continue

            if pd.isna(df[col_name].iloc[i + 1]):

                combined_row = {
                    col: str(df[col].iloc[i]) if pd.isna(df[col].iloc[i + 1]) else str(df[col].iloc[i]) + ' ' + str(df[col].iloc[i + 1])
                    if col == col_name else str(df[col].iloc[i]) + ' ' + str(df[col].iloc[i + 1])
                    for col in df.columns
                }
                result.append(combined_row)
                skip = True  
            else:
                result.append(df.iloc[i].to_dict())

        if not skip:
            result.append(df.iloc[-1].to_dict())

        return pd.DataFrame(result)
    
    def concat_row(self):
        print("Tratamento incial...".format(self.name_pdf))
        for i in range (self.num_pages):
            try:
                df = pd.read_csv("./bruto/{}_{}.csv".format(self.name_pdf,i))
                concatenated_df = self.__concat_rows_ignore_nan(df, str(list(df.columns)[7]))
                concatenated_df.replace('nan', '', inplace=True)
                concatenated_df.replace('', np.nan, inplace=True)

                concatenated_df = concatenated_df.dropna(axis=1, how='all')

                data_row = list(concatenated_df.columns[0:])
                row = [np.nan if x.startswith('Unnamed') else x for x in data_row]
                
                
                df = pd.concat([pd.DataFrame([row], columns=concatenated_df.columns), concatenated_df], ignore_index=True)


                concatenated_df2 = self.__concat_rows_ignore_nan(df, str(list(df.columns)[7]))

                concatenated_df2.replace('nan', '', inplace=True)
                concatenated_df2.replace('', np.nan, inplace=True)

                concatenated_df3 = self.__concat_rows_ignore_nan(concatenated_df2, str(list(concatenated_df2.columns)[7]))

                
                if 1 == 1:

                    concatenated_df3['EAN_Extraido'] = concatenated_df3[str(list(concatenated_df3.columns)[0])].str.extract(r'(EANs:.*)')

                    concatenated_df3[str(list(concatenated_df3.columns)[0])] = concatenated_df3[str(list(concatenated_df3.columns)[0])].str.replace(r'(EANs:.*)', '', regex=True)
                    concatenated_df3[str(list(concatenated_df3.columns)[0])] = concatenated_df3[str(list(concatenated_df3.columns)[0])].str.replace('nan', '', regex=True)
                    concatenated_df3[str(list(concatenated_df3.columns)[1])] = concatenated_df3[str(list(concatenated_df3.columns)[1])].fillna('').astype(str)
                    concatenated_df3['EAN_Extraido'] = concatenated_df3['EAN_Extraido'].fillna('').astype(str)

                    concatenated_df3['Produtos'] = concatenated_df3[str(list(concatenated_df3.columns)[1])] + ' ' + concatenated_df3['EAN_Extraido']
                    concatenated_df3[str(list(concatenated_df3.columns)[1])] = concatenated_df3['Produtos']

                    concatenated_df3.drop(columns=['EAN_Extraido'], inplace=True)
                    
                    df_final = concatenated_df3.iloc[:, 1:6]
                    try:
                        df_final.rename(columns={'Emb':'Emb Qtde','Qtde Qtd.Canc.':'Qtd.Canc.','Valor': 'Valor Unit.', 'Valor.1': 'Valor Item'}, inplace=True)
                    except:
                        pass
                    df_final = df_final.dropna(axis=1, how='all')

                    df_final = df_final.dropna(thresh=len(df_final.columns) - 2)

                    df_final.to_csv("./intermediario/{}_{}_t.csv".format(self.name_pdf,i), index=False)
                else:
                    
                    concatenated_df3 = concatenated_df3.dropna(thresh=len(df.columns) - 2)

                    concatenated_df3 = concatenated_df3.dropna(axis=1, how='all')

                    col = str(list(concatenated_df3.columns)[3])
                    if concatenated_df3.iloc[0].str.contains('Emb').any():

                        df_filtered = concatenated_df3.iloc[:, 1:6]
                        df_filtered.columns = df_filtered.iloc[0]
                        df_filtered = df_filtered[1:]
                        df_filtered.rename(columns={'Emb':'Emb Qtde','Qtde Qtd.Canc.':'Qtd.Canc.','Valor': 'Valor Unit.', 'Valor.1': 'Valor Item'}, inplace=True)
                    else:
                        df_filtered = concatenated_df3.iloc[:, 1:6]
                    
                    df_filtered.to_csv("./intermediario/{}_{}_t.csv".format(self.name_pdf,i), index=False)
            except Exception as e:
                print(f"Ocorreu um erro: {e}")

    def make_final_file(self):
        print("Lendo arquivo {}.pdf...".format(self.name_pdf))
        df_geral = pd.DataFrame()
        expected_columns = ['Produtos', 'Emb Qtde', 'Qtd.Canc.', 'Valor Unit.', 'Valor Item']
        row = []
        for i in range (self.num_pages):
            try:
                df_csv = pd.read_csv("./intermediario/{}_{}_t.csv".format(self.name_pdf,i))

                df = pd.DataFrame()
                if not all(col in expected_columns for col in df_csv.columns):
                    new_row = {col: col for col in expected_columns}

                    df_new_row = pd.DataFrame([new_row], columns=expected_columns)

                    df = pd.concat([df_new_row, df_csv], ignore_index=True)

                    df = df.reindex(columns=expected_columns)
                
                df.loc[0:, 'Produtos'] = df_csv.loc[0:, df_csv.columns[0]]
                df.loc[0:, 'Emb Qtde'] = df_csv.loc[0:, df_csv.columns[1]]
                df.loc[0:, 'Qtd.Canc.'] = df_csv.loc[0:, df_csv.columns[2]]
                df.loc[0:, 'Valor Unit.'] = df_csv.loc[0:, df_csv.columns[3]]
                if len(df_csv.columns) > 4:
                    df.loc[0:, 'Valor Item'] = df_csv.loc[0:, df_csv.columns[4]]
                else:
                    df.loc[0:, 'Valor Item'] = np.nan
                
                df_geral = pd.concat([df_geral, df], ignore_index=True)

            except Exception as e:
                print(f"Ocorreu um erro: {e}")

        rows_to_drop = df_geral[df_geral.apply(lambda row: row.astype(str).str.contains('Produtos|a Receber|TOTAIS').any(), axis=1)].index

        df = df_geral.drop(index=rows_to_drop).reset_index(drop=True)

        df.rename(columns={'Canc.':'Qtd.Canc.','Unit.':'Valor Unit.','Item': 'Valor Item'}, inplace=True)
        df = df.dropna(thresh=len(df_geral.columns) - 2)
        df.to_csv("{}.csv".format(self.name_pdf), index=False)
        print("Arquivo {}.csv gerado".format(self.name_pdf))

        os.system(command="del .\intermediario\*.csv") 
        os.system(command="del .\bruto\*.csv") 
        print("FIM")
