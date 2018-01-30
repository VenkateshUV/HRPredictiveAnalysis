# Search if absence ids are in master old
# isin(): if dataframe elements is in series or dataframe

##import pandas as pd
####MasterData = pd.read_csv('HRData/MasterUnion.csv',low_memory=False)
##MasterData = pd.read_csv('HRData/MasterData_clean1.csv',low_memory=False)
##AbsenceData = pd.read_csv('HRData/Absences.csv',low_memory=False)
##
##print(AbsenceData[AbsenceData['ID'].isin(MasterData['ID'])==False])
##
##AbsenceFalse = AbsenceData[AbsenceData['ID'].isin(MasterData['ID'])==False]
##AbsenceTrue = AbsenceData[AbsenceData['ID'].isin(MasterData['ID'])==True]
##
##
####AbsenceFalse.to_csv('HRData/Absencenotfound.csv')
####AbsenceTrue.to_csv('HRData/AbsenceFound.csv')
##


import pandas as pd
##MasterData = pd.read_csv('HRData/MasterUnion.csv',low_memory=False)
Old = pd.read_csv('HRData/MasterData_clean1.csv',low_memory=False)
New = pd.read_csv('HRData/MasterData_new_clean1.csv',low_memory=False)


DivisionFalse = Old[Old['Division Code'].isin(New['Division Code'])==False]
##AbsenceTrue = AbsenceData[AbsenceData['ID'].isin(MasterData['ID'])==True]

#FuncAreaFalse = New[New['Functional Area code'].isin(New['Functional Area code'])==False]

FuncAreaFalse = Old[Old['Functional Area code'].isin(New['Functional Area code'])==False]

print(DivisionFalse)
print(FuncAreaFalse)
