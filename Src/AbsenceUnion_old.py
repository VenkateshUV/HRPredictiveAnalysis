import pandas as pd


Absences = pd.read_csv('HRData/Absences.csv',low_memory=False)
MasterUnion = pd.read_csv('HRData/MasterData_clean1.csv',low_memory=False)


##sindices = []
NewAbsence = pd.DataFrame()

for Index, Row in Absences.iterrows():
##    print(Row['Personnel ID'] in (MasterUnion['Personnel ID'].values))
    print(Index)
    if (Row['Personnel ID'] in (MasterUnion['Personnel ID'].values)):
        NewRow = pd.DataFrame()
##        print(Row['Personnel ID'])
##        print(MasterUnion[(MasterUnion['Personnel ID'] == Row['Personnel ID'])]['Personnel ID'])
        NewRow = NewRow.append(Row)
##        print(NewRow['Personnel ID'])
        Merg = pd.merge(NewRow,MasterUnion[(MasterUnion['Personnel ID'] == Row['Personnel ID'])], on='Personnel ID')
        
        NewAbsence = NewAbsence.append(Merg)
##        print(NewAbsence)
##        sindex =  MasterUnion[(MasterUnion['Personnel ID'] == Row['Personnel ID'])  ].index[0]
##        sindices.append(sindex)
    else:
        pass
        
        


##AbsenceMaster = pd.DataFrame(index = sindices, columns = MasterUnion.columns)

##Result = pd.merge(Absences, AbsenceMaster, on='Personnel ID')

NewAbsence.to_csv('HRData/AbsencesUnion_old.csv',encoding='utf-8')
