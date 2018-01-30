import pandas as pd

TerminationData = pd.read_csv('HRData/UNCC_Termination UNION.csv',low_memory=False)
CostCenterCode = pd.read_csv('HRData/CostCenterCode.csv',low_memory=False)
locs = []

for Index, Row in TerminationData.iterrows():
    print(Index)
    loc =  CostCenterCode[CostCenterCode['Cost Ctr'] == Row['Cost Ctr']].index[0]
    print(loc)
    locs.append(loc)

TerminationData['Cost Center Name New'] = pd.DataFrame(locs,columns = [CostCenterCode['Cost Center'][locs.tolist()]])

#************ Not finished yet, there are some with unknown Cost Ctr numbers
