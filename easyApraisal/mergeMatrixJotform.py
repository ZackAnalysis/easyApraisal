import pandas as pd


def merge_matrix_jotform(df_matrix, df_jotform):

    taxratio = pd.read_excel('NiagaraPropertyTaxRates.xlsx')
    city = df_matrix.loc[df_matrix['Name'] == 'City', 'main'].values[0]
    if city == 'Niagara on the Lake':
        city = 'Niagara-on-the-Lake'
    existinguse = df_jotform.loc[df_jotform['Name'] == 'Existing use', 'value'].values[0]
    assessedValue = df_matrix.loc[df_matrix['Name'] == 'Assessed value', 'main'].values[0]
    if existinguse == 'Single-family residential':
        usage = 'Residential'
    else:
        usage = 'Multi-residential'
    taxrate = taxratio.loc[(taxratio['City'] == city), usage].values
    if len(taxrate) > 0:
        taxrate = taxrate[0]
        try:
            taxrate = float(taxrate)
            assessedValue = float(assessedValue)
            df_matrix.loc[df_matrix['Name'] == 'Taxes', 'main'] = taxrate * assessedValue
        except:
            print('taxrate or assessedValue is not a number')
    df_jotform = df_jotform[['value']]
    df_jotform.loc[df_jotform['value']=='','value'] = None
    # df_matrix = df_matrix.merge(df_jotform, on='Name', how='left')
    df_matrix = pd.concat([df_matrix, df_jotform], axis=1)
    df_matrix['main'] = df_matrix['value'].fillna(df_matrix['main'])
    
    return df_matrix.drop(['value'], axis=1)

if __name__ == '__main__':
    matrixfile ='Matrix__20220319_163550.xlsx'
    jotformfile = 'jotformOutput-20220313-171338.xlsx'
    outfile = matrixfile.replace('.xlsx', '-jotform.xlsx')
    df_matrix = pd.read_excel(matrixfile)
    df_jotform = pd.read_excel(jotformfile)
    df_matrix = merge_matrix_jotform(df_matrix, df_jotform)
    df_matrix.to_excel(outfile, index=False)