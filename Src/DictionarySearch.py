import pandas as pd
from numpy import isnan

FuncAreaCode = pd.read_csv('HRData/previous cleaned/FunctionalAreaCode.csv',low_memory=False)
DivisionCode = pd.read_csv('HRData/previous cleaned/DivisionCode.csv',low_memory=False)

NewMasterData = pd.read_csv('HRData/previous cleaned/UNCC_HR Master Data active employees_clean2.csv',low_memory=False)


Divisionindices = []
FuncAreaindices = []
count = 0

for Index, Row in NewMasterData.iterrows():
    Divisionindex =  DivisionCode[(DivisionCode['Division Code'] == Row['Division Code'])  ].index[0]
    Divisionindices.append(Divisionindex)

    FuncAreaindex =  FuncAreaCode[FuncAreaCode['Functional Area code'].str.strip() == Row['Functional Area code'].strip()].index[0]
    FuncAreaindices.append(FuncAreaindex)
    


NewMasterData.loc[:,'Division Name'] = pd.Series(DivisionCode['Division Name'][Divisionindices].values,index=NewMasterData.index)
NewMasterData.loc[:,'Functional Area'] = pd.Series(FuncAreaCode['Functional Area'][FuncAreaindices].values, index=NewMasterData.index)

NewMasterData.to_csv('HRData/MasterDataNew_clean3.csv',encoding='utf-8')


####    print(Index)
##    if isnan(Row['Division Code']):
##        Divisionindex = float('nan')
##    else:
##        Divisionindex =  DivisionCode[(DivisionCode['Division Code'] == Row['Division Code'])  ].index[0]
####    & ~isnan(DivisionCode['Division Code']
####    print(Divisionindex)
##    Divisionindices.append(Divisionindex)
##
##    if (str(Row['Functional Area code'])=='nan'):
##        FuncAreaindex = float('nan')
##    else:
##        FuncAreaindex =  FuncAreaCode[FuncAreaCode['Functional Area code'].str.strip() == Row['Functional Area code'].strip()].index[0]
####    print(FuncAreaindex)
##    FuncAreaindices.append(FuncAreaindex)
