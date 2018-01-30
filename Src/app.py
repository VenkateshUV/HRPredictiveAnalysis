# In[]:
# Import required libraries
import os

import datetime as dt

import pandas as pd
from flask import Flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import math
import dash_table_experiments as dtable


import numpy as np

# Machine Learning
from sklearn import preprocessing, cross_validation, svm
from sklearn.linear_model import LinearRegression

# In[]:
# Setup app

app = dash.Dash(__name__)
server = app.server

app.css.append_css({'external_url': 'https://cdn.rawgit.com/VenkateshUV/HRPredictiveAnalysis/1e96b8dc/conti-ui.css'})

mapbox_access_token = 'pk.eyJ1IjoieXBlc3N0IiwiYSI6ImNqYW16cGkydzM5dWczM21odzY2b3BwZTcifQ.AWFR5CO9Buv-pLVZ_HixTw'  # noqa: E501

#--------------- Load HR data----------------
TerminationData = pd.read_csv('HRData/UNCC_Termination UNION_Loc.csv',low_memory=False)
TerminationData.fillna('null', inplace=True)
TerminationData['Birth date'] = pd.to_datetime(TerminationData['Birth date'] )
now = pd.Timestamp(dt.datetime.now())
TerminationData['Age'] = (now-TerminationData['Birth date']).astype('<m8[Y]')  #add column to existing dataframe
TerminationData['Leaving date'] = pd.to_datetime(TerminationData['Leaving date'] )
TerminationData['Entry'] = pd.to_datetime(TerminationData['Entry'] )
TerminationData['Length of Employment'] = (TerminationData['Leaving date']-TerminationData['Entry']).astype('<m8[Y]')

Leavingyearmonth = []
for leavingdate in TerminationData['Leaving date']:
    Leavingyearmonth.append(str(leavingdate.year) + '-' + str(leavingdate.month))
TerminationData['Leaving yearmonth'] = pd.to_datetime(Leavingyearmonth)



# Create controls
Gender_options = [{'label': 'Female', 'value': 'Female'},
                  {'label': 'Male', 'value': 'Male'}]
LeavingDate_min = min(TerminationData['Leaving date'])
LeavingDate_max = max(TerminationData['Leaving date'])
LeavingDate_rangetime = LeavingDate_max - LeavingDate_min
LeavingDate_range = LeavingDate_rangetime.days

age_min = min(TerminationData['Age'])
age_max = max(TerminationData['Age'])

Gender_TYPES = dict(Male = 'Male', Female = 'Female',)
Gender_COLORS = dict(Male = '#FFEDA0', Female = '#FA9FB5',)

Esubgroup_list = TerminationData['Employee Subgroup'].value_counts().index.values.tolist()
Esubgroup_sublist_null = list(Esubgroup_list)
Esubgroup_sublist_TI = list(Esubgroup_list)
Esubgroup_sublist_null.remove('null')
Esubgroup_sublist_TI.remove('Intern-Student')
Esubgroup_sublist_TI.remove('Temporary')

Esubgroup_options = []
for i in Esubgroup_list:
    Esubgroup_options.append({'label': str(i),'value': str(i)})

TerminationLocationcount = TerminationData.groupby('Location Name').agg(['count'])
maxTerminationLocationcount = TerminationLocationcount.max().iloc[0]
minTerminationLocationcount = TerminationLocationcount.min().iloc[0]


fontsizeC = 15
fontsizeS = '15'
margintopFigs = 60
fontsizeL = 15
fontsizeT = 20
Pieheight = 250
Figheight = 400

plotallclicknumber = 0


Master2017Data = pd.read_csv('HRData/MasterData_clean1_loc.csv',low_memory=False)
Master2017Data.fillna('null', inplace=True)
Master2017Data['Date of Birth'] = pd.to_datetime(Master2017Data['Date of Birth'] )
now = pd.Timestamp(dt.datetime.now())
Master2017Data['Age'] = (now-Master2017Data['Date of Birth']).astype('<m8[Y]')  #add column to existing dataframe

##Absdata

AbsStartDate_range = 10
AbsStartDate_min = 0
AbsStartDate_max = 10


# External data
ExtData = pd.read_csv('HRData/MFG10YearTerminationData_1.csv',low_memory=False)
FactorTest = pd.read_csv('HRData/FactorImportance.csv',low_memory=False)


# In[]:
# Create app layout

#------------------ Tabs ----------------
# In this case, we're adding the elements through a callback, so we can ignore
# the exception.

app.config.supress_callback_exceptions = True

vertical = False

if not vertical:
    app.layout = html.Div(
        [
            html.Div(
                [
                    html.Img(
                        src="http://www.continentaltire.com/sites/all/themes/continental/assets/images/print-logo.jpg",
                        className='one columns',
                        style={
                            'height': '100',
                            'width': '225',
                            'float': 'left',
                            'position': 'relative',
                            },
                        ),
                    
                    html.H1(
                        'HR Predictive Modeling Data',
                        className='eight columns',
                        style={'text-align': 'center'
                            },
                        ),
                    ],
                className='row',
                style = {'width': '80%','margin-left': '40','margin-right': '40',},

                ),
            html.Div(
                [
                    dcc.Tabs(
                        tabs=[
                            {'label': 'Termination', 'value': 'tab_Term'},
                            {'label': 'Absence', 'value': 'tab_Abs'},
                            {'label': 'Time2Hire', 'value': 'tab_Hire'},
                            {'label': 'External Test Data', 'value': 'tab_Test'},
                            ],
                        value='tab_Term',
                        id='tabs',
                        ),
                    ],
                style = {
                    'width': '100%',
                    'fontFamily': 'Sans-Serif',
                    'color': 'black',
                    'margin-left': 'auto',
                    'margin-right': 'auto',
                    'font-size':fontsizeS,
            }
                ),
            html.Div(id='tab-output')
            ],

        style = {
            'width': '100%',
            'fontFamily': 'Sans-Serif',
            'fontColor': 'black',
            'margin-left': 'auto',
            'margin-right': 'auto',
            'font-size':fontsizeS,
            }
        )

else:
    app.layout = html.Div(
        [
            html.Div
            (
                [
                    html.Img(
                        src="http://www.continentaltire.com/sites/all/themes/continental/assets/images/print-logo.jpg",
                        className='one columns',
                        style={
                            'height': '100',
                            'width': '225',
                            'float': 'left',
                            'position': 'relative',
                            },
                        ),
                    
                    html.H1(
                        'HR Predictive Modeling Data',
                        className='eight columns',
                        style={'text-align': 'center'
                            },
                        ),
                    ],

                className='row'

                ),
            
            html.Div(
                
                dcc.Tabs(
                    tabs=[
                        {'label': 'Termination', 'value': 'tab_Term'},
                        {'label': 'Absence', 'value': 'tab_Abs'},
                        {'label': 'Time2Hire', 'value': 'tab_Hire'},
                        {'label': 'ExternalTestData', 'value': 'tab_Test'},
                    ],
                    value='tab_Term',
                    id='tabs',
                    vertical = vertical,
                    style={
                        'height': '100vh',
                        'borderRight': 'thin lightgrey solid',
                        'textAlign': 'left',
                        'font-size':fontsizeS,
                        'font-weight':'bold',
                        }
                    ),

                style={'width': '20%', 'float': 'left'}
                ),

            html.Div(
                html.Div(id='tab-output'),
                style={'width': '100%', 'float': 'right'}
                )
            ],


        style={
            'fontFamily': 'Sans-Serif',
            'margin-left': 'auto',
            'margin-right': 'auto',
            }

        
        )


# ------------ app layout for Tab 1 -----------------
@app.callback(Output('tab-output', 'children'), [Input('tabs', 'value')])   # ?First tab need to click
def display_content(value):
    if value=='tab_Term':
        return html.Div(
            [

                # Title
                html.Div(
                    [
                        html.H1('Termination Data',
                                style={'text-align': 'center'
                                },
                                ),
                        ],
                    className='row'
                    ),

    #********** Add a total prediction without filters
                
                # Leaving date slider and age slider
                html.Div(
                    [
                        html.Div( # Leaving date
                            [
                                html.H4(
                                    '',
                                    id='LeavingDate_text',
                                    style={'font-weight':'bold',},),
                                 html.Div(
                                     [
                                         dcc.RangeSlider(
                                             id='LeavingDate_slider',
                                             min = 0,
                                             max = LeavingDate_range,
                                             value = [0, LeavingDate_range],
                                             step = 1,
                                             marks={
                                                 0: {'label': LeavingDate_min.strftime('%m/%d/%Y'), 'style': {'font-size':fontsizeS, 'color':'white','font-weight':'bold'}},
                                                 LeavingDate_range: {'label': LeavingDate_max.strftime('%m/%d/%Y'), 'style': {'font-size':fontsizeS, 'color':'white','font-weight':'bold'}},
                                                 },
                                             
                                             ),
                                         ],
                                     style={'margin-left': '30', 'margin-right': '60','font-size':fontsizeS,'font-weight':'bold'},
                                     ),
                                ],
                            
                            className='col-sm-4',
##                            style={'background-color':"#191A1A"},
                            ),

                         html.Div( # Age
                            [
                                html.H4(
                                    '',
                                    id='Age_text',
                                    style={'font-weight':'bold',},),
                                 html.Div(
                                     [
                                         dcc.RangeSlider(
                                        id='Age_slider',
                                        min= age_min,
                                        max= age_max,
                                        value=[20, 60],
                                        step = 1,
                                        marks={
                                            int(age_min): {'label': str(age_min), 'style': {'font-size':fontsizeS, 'color':'white','font-weight':'bold'}},
                                            int(age_max): {'label': str(age_max), 'style': {'font-size':fontsizeS, 'color':'white','font-weight':'bold'}},
                                            },
                                        ),
                                ],
                                     style={'margin-left': '30', 'margin-right': '60','font-size':fontsizeS,'font-weight':'bold',},
                                     ),
                                ],
                            className='col-sm-4',
##                             style={'background-color':"#191A1A"},
                            ),


                        html.Div(  # by gender
                            [
                                html.H4('Filter by Gender:',
                                        style={'font-weight':'bold',},),
                                dcc.RadioItems(
                                    id='Gender_selector',
                                    options=[
                                        {'label': 'All ', 'value': 'All'},
                                        {'label': 'Female ', 'value': 'Female'},
                                        {'label': 'Male ', 'value': 'Male'}
                                        ],
                                    value='All',
                                    labelStyle={'display': 'inline-block'}
                                    ),
                                  
                                ],
                            className='col-sm-4',
##                            style={'margin-left': '60'},
                            ),
                        
                            ],
                    className='row',
                    style={'margin-left': '40','font-weight':'bold', 'background-color':"#191A1A"},
                    ),

                # Gender filter selector and Employment subgroup filter
                html.Div(
                    [
                        
                        html.Div(  # by employment subgroup
                            [
                                html.H4('Filter by Employment Subgroup:',
                                        style={'font-weight':'bold'},),
                                dcc.RadioItems(
                                    id='Esubgroup_selector',
                                    options=[
                                        {'label': 'All ', 'value': 'All'},
                                        {'label': 'Exclude Temporary and intern-student ', 'value': 'ExTI'},
                                        {'label': 'Exclude null data ', 'value': 'RmNull'},
                                        {'label': 'Customize ', 'value': 'Customize'}
                                        ],
                                    value='All',
                                    labelStyle={'display': 'inline-block'}
                                    ),

                                html.Div([
                                 dcc.Dropdown(
                                        id = 'Esubgroup_dropdown',
                                        options = Esubgroup_options,
                                        multi = True,
                                        value = []
                                    ),],
                                         className = 'row',
                                         style = {'color':'black'},
                                         )
                                 
                                ],
                             className='col-sm-4',
##                            style={'border-style': 'solid'},
                            ),


                         html.Div(  # Prediction selector, by day, week, or month, how long to predict slider
                            [  # Prediction selector, how long to predict slider, and button to plot all, Text box to show data results
                                html.H4('Forecasting by:',
                                        style={'font-weight':'bold'},),
                                dcc.RadioItems(
                                    id='TermPred_selector',
                                    options=[
                                        {'label': 'Day', 'value': 'Day'},
                                        {'label': 'Week', 'value': 'Week'},
                                        {'label': 'Month', 'value': 'Month'},
                                        ],
                                    value='Week',
                                    labelStyle={'display': 'inline-block'}
                                    ),
                                html.H4(
                                    '',
                                    id='TermPred_text',),
                                html.Div(
                                    [
                                        dcc.Slider(
                                        id='TermPred_slider',
                                        min= 1,
                                        max= 30,
                                        value=4,
                                        step = 1,
                                        marks={
                                            int(1): {'label': '1', 'style': {'font-size':fontsizeS, 'color':'white','font-weight':'bold'}},
                                            int(30): {'label': '30', 'style': {'font-size':fontsizeS, 'color':'white','font-weight':'bold'}},
                                            },
                                        ),
                                    ],
                                    style={'margin-left': '30', 'margin-right': '60','font-size':fontsizeS,'font-weight':'bold',},
                                    ),
                                
                                ],
                             className='col-sm-4',
##                            style={'border-style': 'solid'},
                            ),


                         html.Div( # button to plot all
                            [
                                html.Button('Plot all locations',
                                            id='buttonplotall',
                                            n_clicks = 0,
##                                            color='white',
##                                            font-size=fontsizeC,
                                            style={'font-size':fontsizeS,
                                                   'font-weight':'bold',
                                                   'color':'black',},
                                            ),
                                html.H4(
                                    '',
                                    id='noData_text',
                                    style={'font-size':fontsizeS,'font-weight':'bold',},),
                                
                                 html.H4(
                                    '',
                                    id='TermPlot_text',
                                    style={'font-size':fontsizeS,'font-weight':'bold',},),
                                
                                ],
                            className='col-sm-4',
##                            style={'margin-left': '60'},
                            ),

                        

                        
                        ],
                    className='row',
                    style={'margin-top': '40','margin-left': '40','font-size':fontsizeS, 'background-color':"#191A1A"},
                    ),



                # Map and individual graph based on location
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Graph(id='main_graph')
                                ],
                            className='col-sm-5',
    ##                        style={'width': '90%','height':'90%'},
                            ),
                        html.Div(
                            [
                                dcc.Graph(id='individual_graph')
                                ],
                            className='col-sm-7',
    ##                        style={'width': '90%','height':'90%'},
                            ),
                        ],
                    className='row',
                    style={'margin-top':'20','margin-left': '40','margin-right': '40','font-size':fontsizeS},
                    ),





                # Pie Charts
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Graph(id='pie_TerminationFactors')
                                ],
                            className='col-sm-3',
                            style={'margin-top': '10','font-size':fontsizeS,'font-weight':'bold',}
                            ),
                        
                        html.Div(
                            [
                                dcc.Graph(id='pie_Terminationreasons')
                                ],
                            className='col-sm-3',
                            style={'margin-top': '10','font-size':fontsizeS,'font-weight':'bold',}
                            ),

                        html.Div(
                            [
                                dcc.Graph(id='pie_TerminationSubgroup')
                                ],
                            className='col-sm-3',
                            style={'margin-top': '10','font-size':fontsizeS,'font-weight':'bold',}
                            ),

                        html.Div(
                            [
                                dcc.Graph(id='pie_TerminationJob')
                                ],
                            className='col-sm-3',
                            style={'margin-top': '10','font-size':fontsizeS,'font-weight':'bold',}
                            ),

                    
                    
                    ],
                    className='row',
                    style={'margin-top':'20','margin-left': '40','margin-right': '40','font-size':fontsizeS},
                    ),

#************************ Pie chart click

                ]) # End Tab 1


##                html.Div(
##                    [
##                        html.Div(
##                            [
##                                dcc.Graph(id='pie_graph')
##                            ],
##                            className='eight columns',
##                            style={'margin-top': '10'}
##                        ),
####                        html.Div(
####                            [
####                                dcc.Graph(id='aggregate_graph')
####                            ],
####                            className='four columns',
####                            style={'margin-top': '10'}
####                        ),
##                    ],
##                    className='row'
##                ),
##            ],
##            className='ten columns offset-by-one'


    elif value=='tab_Abs':
         return html.Div(
             [

                 # Title
                 html.Div(
                     [
                         html.H1('Absence Data Under Construction',
                                 style={'text-align': 'center'},
                                 ),
                          ],
                     className='row'
                     ),


                 
                  html.Div(
                      [
                          html.Img(
                              src="https://cdn.pixabay.com/photo/2017/06/16/07/26/under-construction-2408061_960_720.png",
                              style={
                                  'height': '300',
                                  'width': '350',
                                    },
                              ),
                          ],
                      className='row',
                      style={
##                            'height': '300',
##                            'width': '350',
                            'margin-top':100,
                            'text-align':'center',
                            },
                      ),

                        
                 
##
###********** Add a total prediction without filters
##                 
##                 # Start Date slider and Capacity Utilization Level slider 
##                 html.Div(
##                     [
##                         html.Div( # Start date
##                             [
##                                html.P(
##                                    '',
##                                    id='AbsStartDate_text',),
##                                 html.Div(
##                                     [
##                                         dcc.RangeSlider(
##                                             id='AbsStartDate_slider',
##                                             min = 0,
##                                             max = AbsStartDate_range,
##                                             value = [0, AbsStartDate_range],
##                                             step = 1,
##                                             marks={
##                                                 0: AbsStartDate_min.strftime('%m/%d/%Y'),
##                                                 AbsStartDate_range: AbsStartDate_max.strftime('%m/%d/%Y'),
##                                                 },
##                                             ),
##                                         ],
##                                     style={'margin-left': '30', 'margin-right': '30'},
##                                     ),
##                                ],
##                             className='five columns',
##                             #style={'border-style': 'solid'},
##                             ),
##
##
##                         html.Div( # Capacity Utilization Level
##                             [
##                                html.P(
##                                    '',
##                                    id='Capacity_text',),
##                                 html.Div(
##                                     [
##                                         dcc.RangeSlider(
##                                             id='Capacity_slider',
##                                            min= Capacity_min,
##                                            max= Capacity_max,
##                                            value=[90, 100],
##                                            step = 1,
##                                            marks={
##                                                int(Capacity_min): str(Capacity_min),
##                                                int(Capacity_max): str(Capacity_max),
##                                                },
##                                            ),
##                                         ],
##                                     style={'margin-left': '30', 'margin-right': '30'},
##                                     ),
##                                ],
##                             className='five columns',
##                             style={'margin-left': '60'},
##                             ),
##
##                         ],
##                     className='row',
##                     style={'margin-left': '40'},
##                     ),
##
##
##
##                 # Gender selection
##                 html.Div(
##                     [
##                         html.P('Filter by Gender:'),
##                         dcc.RadioItems(
##                            id='AbsGender_selector',
##                            options=[
##                                {'label': 'All ', 'value': 'All'},
##                                {'label': 'Female ', 'value': 'Female'},
##                                {'label': 'Male ', 'value': 'Male'}
##                                ],
##                            value='All',
##                            labelStyle={'display': 'inline-block'}
##                            ),
##
##                         ],
##                     className='row',
##                     style={'margin-top': '40','margin-left': '40'},
##                     ),
##
##
##
##
##
##                 #  'Employee Group_A' 'Company' filters
##                 html.Div(
##                     [
##
##                         html.Div(  # by employment group
##                             [
##                                 html.P('Filter by Employment Sub Group:'),
##                                 dcc.RadioItems(
##                                     id='AbsEsGroup_selector',
##                                    options=[
##                                        {'label': 'All ', 'value': 'All'},
##                                        {'label': 'Customize ', 'value': 'Customize'}
##                                        ],
##                                    value='All',
##                                    labelStyle={'display': 'inline-block'}
##                                    ),
##                                 dcc.Dropdown(
##                                        id = 'AbsEsGroup_dropdown',
##                                        options = AbsEGroup_options,
##                                        multi = True,
##                                        value = []
##                                        ),
##                                 ],
##                             className='five columns',
##                             #style={'border-style': 'solid'},
##                             ),
##
##
##
##                         html.Div(  # by company
##                             [
##                                html.P('Filter by Company:'),
##                                dcc.RadioItems(
##                                    id='AbsCompany_selector',
##                                    options=[
##                                        {'label': 'All ', 'value': 'All'},
##                                        {'label': 'Customize ', 'value': 'Customize'}
##                                        ],
##                                    value='All',
##                                    labelStyle={'display': 'inline-block'}
##                                    ),
##                                 dcc.Dropdown(
##                                        id = 'AbsCompany_dropdown',
##                                        options = AbsCompany_options,
##                                        multi = True,
##                                        value = []
##                                    ),
##                                ],
##                             className='five columns',
##                             #style={'border-style': 'solid'},
##                             ),
##
##                         ],
##                     className='row',
##                     style={'margin-top': '40','margin-left': '40'},
##                     ),
##
##
##
##                 # No of data
##                 html.Div(
##                     [
##                         html.H4(
##                             '',
##                             id='AbsnoData_text',),
##                         ],
##                      className='row',
##                     style={'margin-top': '40','margin-left': '40'},
##                     ),
##
##
##
##
##
##
##                 # Map and individual graph based on location
##                 html.Div(
##                     [
##                        html.Div(
##                            [
##                                dcc.Graph(id='Absmain_graph')
##                                ],
##                            className='seven columns',
##    ##                        style={'width': '90%','height':'90%'},
##                            ),
##                        html.Div(
##                            [
##                                dcc.Graph(id='Absindividual_graph')
##                                ],
##                            className='five columns',
##    ##                        style={'width': '90%','height':'90%'},
##                            ),
##                        ],
##                    className='row',
##                    style={'margin-top':'40'},
##                     ),
##
##
##
##
##                 # Pie Charts
##                 html.Div(
##                     [
##                         html.Div( # Division Name
##                            [
##                                dcc.Graph(id='pie_AbsDivision')
##                                ],
##                            className='four columns',
##                            style={'margin-top': '10'}
##                            ),
##
##                        html.Div( # Functional Area
##                            [
##                                dcc.Graph(id='pie_AbsFuncArea')
##                                ],
##                            className='four columns',
##                            style={'margin-top': '10'}
##                            ),
##         
##                        html.Div( # Job 
##                            [
##                                dcc.Graph(id='pie_AbsJob')
##                                ],
##                            className='four columns',
##                            style={'margin-top': '10'}
##                            ),
##
##                         ],
##                     className='row',
##                     style={'margin-top':'40'},
##                     ),
##                 
##
##                 html.Div(
##                     [
##                         html.Div( # Position
##                            [
##                                dcc.Graph(id='pie_AbsPosition')
##                                ],
##                            className='four columns',
##                            style={'margin-top': '10'}
##                            ),
##
##                          html.Div( #  Cost Center_A
##                            [
##                                dcc.Graph(id='pie_AbsCostCtr')
##                                ],
##                            className='four columns',
##                            style={'margin-top': '10'}
##                            ),
##
##                          html.Div( # Attendance or Absence Type
##                            [
##                                dcc.Graph(id='pie_AbsType')
##                                ],
##                            className='four columns',
##                            style={'margin-top': '10'}
##                            ),
##
##
##                         ],
##                     className='row',
##                     style={'margin-top':'40'},
##                     ),
##
##
##                 
##                 # 'Entry', plot
##                 # age plot
##                 
##                 html.Div( 
##                     [
##                         html.Div( #'Entry', plot
##                            [
##                                dcc.Graph(id='pie_AbsEntry')
##                                ],
##                            className='four columns',
##                            style={'margin-top': '10'}
##                            ),
##
##                        html.Div( # age plot
##                            [
##                                dcc.Graph(id='pie_AbsAge')
##                                ],
##                            className='four columns',
##                            style={'margin-top': '10'}
##                            ),
##         
##                       
##                         ],
##                     className='row',
##                     style={'margin-top':'40'},
##                     ),
##
##
##
##                  


            ])





                 

    elif value=='tab_Hire':
          return html.Div(
             [

                 # Title
                 html.Div(
                     [
                         html.H1('Time to hire Data Under Construction',
                                 style={'text-align': 'center'},
                                 ),
                         ],
                     className='row'
                     ),

                    html.Div(
                      [
                          html.Img(
                              src="https://cdn.pixabay.com/photo/2017/06/16/07/26/under-construction-2408061_960_720.png",
                              style={
                                  'height': '300',
                                  'width': '350',
                                    },
                              ),
                          ],
                      className='row',
                      style={
##                            'height': '300',
##                            'width': '350',
                            'margin-top':100,
                            'text-align':'center',
                            },
                      ),
##
##                 # Opening date figure, Division filter, time option
##                 html.Div(
##                     [
##                         html.Div(  
##                             [
##                                 html.Div(  # Division filter
##                                     [
##                                         html.P('Filter by Division:'),
##                                         dcc.RadioItems(
##                                            id='HireDivision_selector',
##                                            options=[
##                                                {'label': 'All ', 'value': 'All'},
##                                                {'label': 'Customize ', 'value': 'Customize'}
##                                                ],
##                                            value='All',
##                                            labelStyle={'display': 'inline-block'}
##                                            ),
##                                         dcc.Dropdown(
##                                                id = 'HireDivision_dropdown',
##                                                options = HireDivision_options,
##                                                multi = True,
##                                                value = []
##                                            ),
##                                         ],
##                                     className='row',
##                                     #style={'border-style': 'solid'},
##                                     ),
##
##                                 html.Div( # time option
##                                     [
##                                         html.P('Time calculation options:'), 
##                                         dcc.RadioItems(
##                                             id='HireTime_options',
##                                             options=[
##                                                 {'label': 'Position open to Offer Accepted', 'value': 'POOA'},
##                                                 {'label': 'Position open to Hired', 'value': 'POH'},
##                                                 ],
##                                            value='All',
##                                            labelStyle={'display': 'inline-block'}
##                                            ),
##                                         ],
##                                     className='row',
##                                     #style={'border-style': 'solid'},
##                                     ),
##
##                                 ],
##                             className='five columns',
##                             #style={'border-style': 'solid'},
##                             ),
##
##
##                         html.Div( # Open date figure v.s. time to hire
##                             [
####                                 html.P(
####                                    '',
####                                    id='OpenDate_text',),
##                                 html.Div(
##                                     [
##                                         dcc.Graph(id='HireOpen_graph')
##                                         ],
##                                     className='five columns',
####                                     style={'margin-top': '10'}
##                                     ),
##                                ],
##                            
##                            className='five columns',
##                            #style={'border-style': 'solid'},
##                            ),
##
##
##                         # No of data
##                         html.Div(
##                             [
##                                 html.H4(
##                                     '',
##                                     id='HirenoData_text',),
##                                 ],
##                             className='five columns',
##                             style={'margin-top': '40','margin-left': '40'},
##                             ),
##
##                         ],
##                     className='row',
##                     style={'margin-left': '40'},
##                     ),
##
##
##                 # Map and individual graph based on location
##                 html.Div(
##                     [
##                        html.Div(
##                            [
##                                dcc.Graph(id='Hiremain_graph')    # chorology by state because all in US
##                                ],
##                            className='seven columns',
##    ##                        style={'width': '90%','height':'90%'},
##                            ),
##                        html.Div(
##                            [
##                                dcc.Graph(id='Hireindividual_graph') # time to hire v.s. open date *********** Forcasting on this
##                                ],
##                            className='five columns',
##    ##                        style={'width': '90%','height':'90%'},
##                            ),
##                        ],
##                    className='row',
##                    style={'margin-top':'40'},
##                    ),
##
##
##
##                # Pie Charts
##                html.Div(
##                    [
##                    html.Div(
##                        [
##                            dcc.Graph(id='pie_HirePosition')
##                            ],
##                        className='four columns',
##                        style={'margin-top': '10'}
##                        ),
##
##                    html.Div(
##                        [
##                            dcc.Graph(id='pie_HireJob')
##                            ],
##                        className='four columns',
##                        style={'margin-top': '10'}
##                        ),
##                    
##                    ],
##                    className='row',
##                    style={'margin-top':'40'},
##                    ),

# ******************* Pie chart click
# ******************* Select top 5 button

                 ])



    elif value=='tab_Test':
      return html.Div(

          [


              html.Div( # Title
                  [
                      html.H1(
                      'External Test Data',
                      id = 'ExtData_title',
                      style={
                          'text-align': 'center'
                          },
                      ),
                      ]
                  ),

              html.Div(
                  [
                      dcc.Markdown(''' [Data Source](https://www.kaggle.com/HRAnalyticRepository/employee-attrition-data/data)'''),
                       ],
                  style={
                          'text-align': 'center'
                          },
                  ),

              html.Div(
                  [
                      html.H4('External DataTable',
                              style={'font-weight':'bold',},),
##                        dtable.DataTable(
##                            rows=ExtData.to_dict('records'),
##
##                            # optional - sets the order of columns
##                            columns=sorted(ExtData.columns),
##
##                            row_selectable=True,
##                            filterable=True,
##                            sortable=True,
##                            selected_row_indices=[],
##                            id='datatable-External'
##                        ),
##                        html.Div(id='selected-indexes'),
##                        dcc.Graph(
##                            id='graph-External'
##                        ),
##                      ],
##                  className="container"
##                  ),


                      generate_table(ExtData),
                      

##                      draw_pie_ExtFactors(ExtData)
                      ],

                  style={'margin-left': '40','font-size':fontsizeS,'font-weight':'bold',}
                  ),

              



              # Pie Charts
                html.Div(
                    [
                        
                        html.Div(
                            [
                                pie_ExtFactors(FactorTest),
                                ],
##                            classname = 'col-sm-5',
##                            style={'margin-left': '40','font-weight':'bold', 'background-color':"#191A1A"},
                    ),
##                                dcc.Graph(id='pie_ExtFactors')
##                                ],
##                            className='row',
##                            style={'margin-top': '10','font-size':fontsizeS,'font-weight':'bold',}
##                            ),
##                        ],
##                    classname = 'col-sm-3',
##                     style={'align':'center','margin-left': '40','font-weight':'bold', 'background-color':"#191A1A"},
##                    ),
##
##              html.Div(id='ExtData-state')
                        ]),


              ])
    
    else:
        return {'display':'none'}


    
#----------------- functions -----------        

# In[]:
# Helper functions

# Slider -> year text
@app.callback(Output('LeavingDate_text', 'children'),
              [Input('LeavingDate_slider', 'value')])
def update_LeavingDate_text(LeavingDate_slider):
    LeavingDate_disp1 = dt.timedelta(days =LeavingDate_slider[0])+ LeavingDate_min
    LeavingDate_disp2 = dt.timedelta(days =LeavingDate_slider[1])+ LeavingDate_min
    return "Filter by leaving Date: {} to {}".format(LeavingDate_disp1.strftime('%m/%d/%y'),LeavingDate_disp2.strftime('%m/%d/%y') )

# Slider -> Age text
@app.callback(Output('Age_text', 'children'),   
              [Input('Age_slider', 'value')])
def update_Age_text1(Age_slider):
    return "Filter by age: {} to {}".format(Age_slider[0],Age_slider[1])


# Radio -> multi
@app.callback(Output('Esubgroup_dropdown', 'value'),            #********** haven't include!
              [Input('Esubgroup_selector', 'value')])
def display_type(Esubgroup_selector):
    if Esubgroup_selector == 'All':
        return Esubgroup_list
    elif Esubgroup_selector == 'ExTI':
        return Esubgroup_sublist_TI
    elif Esubgroup_selector == 'RmNull':
        return Esubgroup_sublist_null
    else:
        return []


    

# filter_dataframe, filter data according to the filters
def filter_dataframe(TerminationData, Age_slider, Gender_selector, LeavingDate_slider,Esubgroup_selector, Esubgroup_dropdown):

    dff = TerminationData[(TerminationData['Age'] >= Age_slider[0])
                          & (TerminationData['Age'] <= Age_slider[1])
                          & ((TerminationData['Gender']== Gender_selector) if Gender_selector!= 'All' else (TerminationData['Gender'].isin(['Female','Male']) ))
                          & (TerminationData['Leaving date'] >= (dt.timedelta(days =LeavingDate_slider[0])+ LeavingDate_min))
                          & (TerminationData['Leaving date'] <= (dt.timedelta(days =LeavingDate_slider[1])+ LeavingDate_min))
                          & (TerminationData['Employee Subgroup'].isin(Esubgroup_dropdown))
           ]

    
    return dff

# filter_dataframe, filter data according to the filters
def filter_dataframe_master(Data, Age_slider, Gender_selector, Esubgroup_selector, Esubgroup_dropdown):

    dff = Data[(Data['Age'] >= Age_slider[0])
               & (Data['Age'] <= Age_slider[1])
               & ((Data['Gender']== Gender_selector) if Gender_selector!= 'All' else (Data['Gender'].isin(['Female','Male']) ))
               & (Data['Employee Subgroup'] .isin(Esubgroup_dropdown))
           ]


    
    return dff

# Selectors -> NooData text
@app.callback(Output('noData_text', 'children'),
              [Input('Age_slider', 'value'),
               Input('Gender_selector', 'value'),
               Input('LeavingDate_slider', 'value'),
               Input('Esubgroup_selector', 'value'),
               Input('Esubgroup_dropdown', 'value')])
def update_NoofData_text(Age_slider, Gender_selector, LeavingDate_slider,Esubgroup_selector, Esubgroup_dropdown):

    dff = filter_dataframe(TerminationData, Age_slider, Gender_selector, LeavingDate_slider,Esubgroup_selector, Esubgroup_dropdown)
    
    return "Total no. of Data: {}".format(dff.shape[0])


                     
# Selectors -> Prediction text
@app.callback(Output('TermPlot_text', 'children'),
              [Input('main_graph', 'hoverData'),
               Input('main_graph', 'selectedData'),
               Input('Age_slider', 'value'),
               Input('Gender_selector', 'value'),
               Input('LeavingDate_slider', 'value'),
               Input('Esubgroup_selector', 'value'),
               Input('Esubgroup_dropdown', 'value')])
def update_TermPlot_text(main_graph_hover, main_graph_selected,Age_slider, Gender_selector,
                         LeavingDate_slider,Esubgroup_selector, Esubgroup_dropdown):

    
    dff = filter_dataframe(TerminationData, Age_slider, Gender_selector, LeavingDate_slider,Esubgroup_selector, Esubgroup_dropdown)
    dfE = filter_dataframe_master(Master2017Data, Age_slider, Gender_selector, Esubgroup_selector, Esubgroup_dropdown)

        # ---------------- Forcastings -----------------


    if main_graph_hover is None:
        custdata = dff
        custdataE = dfE

        locationname = 'all locations<br>Total no. of data:' + str(custdata.shape[0]) 
    else:
        custdata = dff[dff['Location Name'] == main_graph_hover['points'][0]['customdata']]
        custdataE = dfE[dfE['Location Name'] == main_graph_hover['points'][0]['customdata']]

        locationname = custdata['Personnel Area - State'].iloc[0] + '-' + custdata['Personnel Area - City'].iloc[0] +'<br>Total no. of termination data:' + str(custdata.shape[0]) 
        
    
    dfI = custdata
    dfE = custdataE

    return 'Total no. of current (2017) employees at selected location: {}'.format(dfE.shape[0])



# Selectors -> main graph
@app.callback(Output('main_graph', 'figure'),
              [Input('Age_slider', 'value'),
               Input('Gender_selector', 'value'),
               Input('LeavingDate_slider', 'value'),
               Input('Esubgroup_selector', 'value'),
               Input('Esubgroup_dropdown', 'value')],
              [State('main_graph', 'relayoutData')])
def make_main_figure(Age_slider, Gender_selector, LeavingDate_slider,
                     Esubgroup_selector,Esubgroup_dropdown, main_graph_layout ):
    
    dff = filter_dataframe(TerminationData, Age_slider, Gender_selector, LeavingDate_slider,Esubgroup_selector, Esubgroup_dropdown)

    traces = []
    for locations, dfff in dff.groupby('Location Name'):  #*********** group by state might be a better option
        trace = dict(
            type = 'scattermapbox',
            lon = dfff['Longitude'],  
            lat = dfff['Latitude'],
            text = dfff['Personnel Area - City'].iloc[0]+':' + str(dfff.shape[0]) + ',' + '%.2f' % (dfff.shape[0]/dff.shape[0]*100) +'% ',  # add state name

            customdata = dfff['Location Name'],
            mode = 'markers',
            textposition = 'bottom center',
            name = dfff['Personnel Area - City'].iloc[0], #
##            opacity = 0.6,
            showlegend = False,
            hoverinfo = 'text',
            hovertext = dfff['Personnel Area - City'].iloc[0]+':' + str(dfff.shape[0]) + ',' + '%.2f' % (dfff.shape[0]/dff.shape[0]*100) +'%',
##            geo = 'geo',
            
            marker = dict(
                size = math.sqrt((dfff.shape[0]-minTerminationLocationcount)/(maxTerminationLocationcount-minTerminationLocationcount))*50, #***********choose vs what,  plot v.s. master data

                opacity = 0.3,
##                sizemode  = 'area',
            ), 
        )
        traces.append(trace)

    layout = dict(
        autosize = True,
        height = Figheight,
    ##    width = 800,
        font=dict(color='#CCCCCC'),
        titlefont=dict(color='white', size=fontsizeT,),
        title = 'Termination Data by Area',
        style = {'font-weight':'bold'},
##        dragmode = 'pan',
        margin=dict(
                l=10,
                r=10,
                b=10,
                t=margintopFigs,
                ),
        hovermode="closest",

        plot_bgcolor="#191A1A",
        paper_bgcolor="#191A1A",

        mapbox=dict(
            accesstoken=mapbox_access_token,
            style="dark",
            center = dict(
                lon = -90,
                lat = 28,
                ),
            zoom=2.8,
            ), 
        )

        

    figure = dict(data=traces, layout=layout)
    return figure

# individual graph
@app.callback(Output('individual_graph', 'figure'),
              [Input('main_graph', 'hoverData'),
               Input('main_graph', 'selectedData'), #************ add this function
               Input('Age_slider', 'value'),
               Input('Gender_selector', 'value'),
               Input('LeavingDate_slider', 'value'),
               Input('Esubgroup_selector', 'value'),
               Input('Esubgroup_dropdown', 'value'),
               Input('TermPred_selector', 'value'),
               Input('TermPred_slider', 'value'),
               Input('buttonplotall', 'n_clicks'),]) #**************** button to return to full data plot
def make_individual_figure(main_graph_hover, main_graph_selected, Age_slider, Gender_selector, LeavingDate_slider,
                     Esubgroup_selector, Esubgroup_dropdown, TermPred_selector,TermPred_slider, plotallclicks):

    dff = filter_dataframe(TerminationData, Age_slider, Gender_selector, LeavingDate_slider,Esubgroup_selector, Esubgroup_dropdown)

        # ---------------- Forcastings -----------------

    global plotallclicknumber
    
    if ((main_graph_hover is None) | (plotallclicks!= plotallclicknumber)  ):
        custdata = dff

        locationname = 'all locations<br>Total no. of data:' + str(custdata.shape[0]) 
    else:
        custdata = dff[dff['Location Name'] == main_graph_hover['points'][0]['customdata']]

        locationname = custdata['Personnel Area - State'].iloc[0] + '-' + custdata['Personnel Area - City'].iloc[0] +'<br>Total no. of data:' + str(custdata.shape[0]) 
        
    if TermPred_selector=='Day':
        PredSel = 'D'
        Mult = 1
    elif TermPred_selector=='Week':
        PredSel = 'W-Mon'
        Mult = 7
    else :
        PredSel = 'M'
        Mult = 30
        
    dfI = custdata[['Leaving date','Count']]
    dfM = dfI.resample(PredSel,convention='end',  on='Leaving date').sum().reset_index().sort_values(by='Leaving date')  # by month
    dfM = dfM.fillna(0)
    dfF = dfM
    dfF = dfF.set_index('Leaving date')
    forecast_col = 'Count'
    forecast_out = TermPred_slider
    dfF['label'] = dfF[forecast_col].shift(-forecast_out)
    X = np.array(dfF.drop(['label'], 1))

    if (X.size):
        X = preprocessing.scale(X)
        X_forecast_out = X[-forecast_out:]
        X = X[:-forecast_out]
        y = np.array(dfF['label'])
        y = y[:-forecast_out]
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size = 0.2)
        if (X_train.size & X_test.size & y_train.size & y_test.size):
            clf = LinearRegression()
            clf.fit(X_train,y_train)
            accuracy = clf.score(X_test, y_test)
            forecast_prediction = clf.predict(X_forecast_out)
            dfF.dropna(inplace=True)
            dfF['forecast'] = np.nan
            last_date = dfF.iloc[-1].name
            last_unix = last_date.timestamp()
            Extras = 86400*Mult*TermPred_slider
            next_unix = last_unix + Extras

            for i in forecast_prediction:
                next_date = dt.datetime.fromtimestamp(next_unix)
                next_unix += Extras
                dfF.loc[next_date] = [np.nan for _ in range(len(dfF.columns)-1)]+[i]
        ##    dfF['Count'].plot(figsize=(15,6), color="green")
        ##    dfF['forecast'].plot(figsize=(15,6), color="orange")
        ##    count = concatenate((count1,dfF['Count'].iloc[:,1]),axis=0)
        else:
            dfF['forecast'] = np.nan
            

                
    else:
        dfF['forecast'] = np.nan
    

    data = [
        dict(
            type='scatter',
            mode='lines+markers',
            name= 'Historical data',
            x = dfF.index,  #*******
            y = dfF['Count'],    #*******
            line=dict(
                shape="spline",
                smoothing=2,
                width=3,
                color='yellow'
                ),
            marker=dict(symbol='diamond-open')
            ),

        dict(
            type='scatter',
            mode='lines+markers',
            name= 'Forcasting',
            x = dfF.index,  #*******
            y = dfF['forecast'],    #*******
            line=dict(
                shape="spline",
                smoothing=2,
                width=3,
                color='orange'
                ),
            marker=dict(symbol='diamond-open')
            ),
        ]

    layout_individual = dict(
        autosize = True,
        legend=dict(orientation="h",),
        height = Figheight,
        font=dict(color='#CCCCCC'),
        titlefont=dict(color='white', size=fontsizeT),
##        dragmode = 'pan',
        margin=dict(
                l=40,
                r=20,
                b=40,
                t=margintopFigs,
                ),
        tickfont=dict(size=fontsizeL),
        hovermode="closest",

        plot_bgcolor="#191A1A",
        paper_bgcolor="#191A1A",

        xaxis=dict(
            title='Dates',
            titlefont=dict(
                family='Arial, sans-serif',
                size=fontsizeL,
                color='white'
            ),
            showticklabels=True,
            tickfont=dict(
    ##            family='Old Standard TT, serif',
                size=fontsizeL,
                color='white'
                ),
            ),
        yaxis=dict(
##            title='Number of Employees Terminated',
##            titlefont=dict(
##                family='Arial, sans-serif',
##                size=fontsizeL,
##                color='white'
##            ),
            showticklabels=True,
            tickfont=dict(
    ##            family='Old Standard TT, serif',
                size=fontsizeL,
                color='white'
                ),
            ticklen = 0,
            ),

        
        )
    
    layout_individual['title'] = 'No of Termination of city: ' + locationname  

    figure = dict(data=data, layout=layout_individual)

    plotallclicknumber = plotallclicks
    
    return figure


# Selectors, main graph -> pie graph
@app.callback(Output('pie_Terminationreasons', 'figure'),
              [Input('Age_slider', 'value'),
               Input('Gender_selector', 'value'),
               Input('LeavingDate_slider', 'value'),
               Input('Esubgroup_selector', 'value'),
               Input('Esubgroup_dropdown', 'value')])
def make_pie_Terminationreasons( Age_slider, Gender_selector, LeavingDate_slider,
                     Esubgroup_selector, Esubgroup_dropdown):

    dff = filter_dataframe(TerminationData, Age_slider, Gender_selector, LeavingDate_slider,Esubgroup_selector, Esubgroup_dropdown)

    Reason_count = dff['Reason'].value_counts()
    
    data = [
        dict(
            type='pie',
            labels = Reason_count.index,
            values = Reason_count.values,
            name = 'Reasons for Leaving',
            text = Reason_count.index,  # noqa: E501?
            hoverinfo = "text+value+percent",
##            textinfo = "label+percent+name",
            textinfo = 'none',
            hole = 0.5,
##            marker = dict(
##                colors = ['#fac1b7', '#a9bb95', '#92d8d8']
##            ),
##            domain={"x": [0, .3], 'y':[0.2, 0.8]},
            showlegend = False,
            ),
        ]

    year1 = (dt.timedelta(days =LeavingDate_slider[0])+ LeavingDate_min).year 
    year2 = (dt.timedelta(days =LeavingDate_slider[0])+ LeavingDate_max).year
    month1 =(dt.timedelta(days =LeavingDate_slider[0])+ LeavingDate_min).month 
    month2 = (dt.timedelta(days =LeavingDate_slider[0])+ LeavingDate_max).month
    layout_pie = dict(
        title = 'Reason for leaving<br>{}-{} to {}-{}'.format(year1,month1,year2,month2),
        autosize = True,
        height = Pieheight,
        font=dict(color='#CCCCCC'),
        titlefont=dict(color='white', size=fontsizeT),
##        dragmode = 'pan',
        margin=dict(
                l=40,
                r=20,
                b=40,
                t=margintopFigs,
                ),
        hovermode="closest",

        plot_bgcolor="#191A1A",
        paper_bgcolor="#191A1A",
        showlegend = False,

        )


    figure = dict(data=data, layout=layout_pie)
    return figure



# Selectors, main graph -> pie graph
@app.callback(Output('pie_TerminationJob', 'figure'),
              [Input('Age_slider', 'value'),
               Input('Gender_selector', 'value'),
               Input('LeavingDate_slider', 'value'),
               Input('Esubgroup_selector', 'value'),
               Input('Esubgroup_dropdown', 'value')])
def make_pie_Terminationreasons( Age_slider, Gender_selector, LeavingDate_slider,
                     Esubgroup_selector, Esubgroup_dropdown):

    dff = filter_dataframe(TerminationData, Age_slider, Gender_selector, LeavingDate_slider,Esubgroup_selector, Esubgroup_dropdown)

    Job_count = dff['Job'].value_counts()
    
    
    data = [
        dict(
            type='pie',
            labels = Job_count.index,
            values = Job_count.values,
            name = 'Job',
            text = Job_count.index,  # noqa: E501?
            hoverinfo = "text+value+percent",
##            textinfo = "text+value+percent",
            textinfo = 'none',
            hole = 0.5,

            showlegend = False,
            ),
        ]

    year1 = (dt.timedelta(days =LeavingDate_slider[0])+ LeavingDate_min).year 
    year2 = (dt.timedelta(days =LeavingDate_slider[0])+ LeavingDate_max).year
    month1 =(dt.timedelta(days =LeavingDate_slider[0])+ LeavingDate_min).month 
    month2 = (dt.timedelta(days =LeavingDate_slider[0])+ LeavingDate_max).month
    
    
    layout_pie = dict(
        title = 'Job titles<br>{}-{} to {}-{}'.format(year1,month1,year2,month2),
        autosize = True,
        height = Pieheight,
        font=dict(color='#CCCCCC'),
        titlefont=dict(color='white', size=fontsizeT),
##        dragmode = 'pan',
        margin=dict(
                l=40,
                r=20,
                b=40,
                t=margintopFigs,
                ),
        hovermode="closest",

        plot_bgcolor="#191A1A",
        paper_bgcolor="#191A1A",
        showlegend = False,

        )



    figure = dict(data=data, layout=layout_pie)
    return figure


# Selectors, main graph -> pie graph
@app.callback(Output('pie_TerminationSubgroup', 'figure'),
              [Input('Age_slider', 'value'),
               Input('Gender_selector', 'value'),
               Input('LeavingDate_slider', 'value'),
               Input('Esubgroup_selector', 'value'),
               Input('Esubgroup_dropdown', 'value')])
def make_pie_Terminationreasons( Age_slider, Gender_selector, LeavingDate_slider,
                     Esubgroup_selector, Esubgroup_dropdown):

    dff = filter_dataframe(TerminationData, Age_slider, Gender_selector, LeavingDate_slider,Esubgroup_selector, Esubgroup_dropdown)

    EmployeeSubgroup_count = dff['Employee Subgroup'].value_counts()
    
    data = [
        dict(
            type='pie',
            labels = EmployeeSubgroup_count.index,
            values = EmployeeSubgroup_count.values,
            name = 'Employee Subgroup',
            text = EmployeeSubgroup_count.index,
            hoverinfo = "text+value+percent",
##            textinfo = "label+percent+name",
            textinfo = 'none',
            hole = 0.5,

            showlegend = False,
            ),
        ]

    year1 = (dt.timedelta(days =LeavingDate_slider[0])+ LeavingDate_min).year 
    year2 = (dt.timedelta(days =LeavingDate_slider[0])+ LeavingDate_max).year
    month1 =(dt.timedelta(days =LeavingDate_slider[0])+ LeavingDate_min).month 
    month2 = (dt.timedelta(days =LeavingDate_slider[0])+ LeavingDate_max).month
    layout_pie = dict(
        title = 'Subgroups<br>{}-{} to {}-{}'.format(year1,month1,year2,month2),
        autosize = True,
        height = Pieheight,
        font=dict(color='#CCCCCC'),
        titlefont=dict(color='white', size=fontsizeT),
##        dragmode = 'pan',
        margin=dict(
                l=40,
                r=20,
                b=40,
                t=margintopFigs,
                ),
        hovermode="closest",

        plot_bgcolor="#191A1A",
        paper_bgcolor="#191A1A",
        showlegend = False,

        )


    figure = dict(data=data, layout=layout_pie)
    return figure


######## ????????????????????? age is an interesting plot too, choose from plot!
## Forcasting

# Selectors, main graph -> pie graph
@app.callback(Output('pie_TerminationFactors', 'figure'),
              [Input('Age_slider', 'value'),
               Input('Gender_selector', 'value'),
               Input('LeavingDate_slider', 'value'),
               Input('Esubgroup_selector', 'value'),
               Input('Esubgroup_dropdown', 'value')])
def make_pie_Terminationreasons( Age_slider, Gender_selector, LeavingDate_slider,
                     Esubgroup_selector, Esubgroup_dropdown):
 
    data = [
        dict(
            type='pie',

            labels = FactorTest['Factors'],
            values = FactorTest['Overall Importance'],
            name = 'Influencing Factors',
            text = FactorTest['Factors'],
            hoverinfo = "text+value+percent",
##            textinfo = "label+percent+name",
            textinfo = 'none',
            hole = 0.5,

            showlegend = False,
            ),
        ]


    layout_pie = dict(
        title = 'Influencing Factors<br>2017',
        autosize = True,
        height = Pieheight,
        font=dict(color='#CCCCCC'),
        titlefont=dict(color='white', size=fontsizeT),
##        dragmode = 'pan',
        margin=dict(
                l=40,
                r=20,
                b=40,
                t=margintopFigs,
                ),
        hovermode="closest",

        plot_bgcolor="#191A1A",
        paper_bgcolor="#191A1A",
        showlegend = False,

        )


    figure = dict(data=data, layout=layout_pie)
    return figure



#********************** Table
def generate_table(dataframe, max_rows=10):
    style = {
##        'backgroundColor':'#CCCCCC',
             'color': 'white',
             'border': '#CCCCCC',
             'border-color':'white'
             }
    
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col], style = style) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


# Selectors, main graph -> pie graph
##@app.callback(Output('pie_ExtFactors', 'figure'),
##              [State('ExtData_state', 'value')])

##def make_pie_ExtFactors(FactorTest):
def pie_ExtFactors(FactorTest):

    
    data = [
        dict(
            type='pie',
##            labels = EmployeeSubgroup_count.index,
##            values = EmployeeSubgroup_count.values,
            labels = FactorTest['Factors'],
            values = FactorTest['Overall Importance'],
            name = 'Influencing Factors',
            text = FactorTest['Factors'],
            hoverinfo = "text+value+percent",
##            textinfo = "label+percent+name",
            textinfo = 'none',
            hole = 0.5,
##            marker=dict(
##                colors=[Gender_COLORS[i] for i in aggregate.index]  
##            ),
##            domain={"x": [0.35, 0.65], 'y':[0.2, 0.8]},
            showlegend = False,
            ),
        ]


    layout_pie = dict(
        title = 'Influencing Factors<br>2017',
        autosize = True,
        height = Pieheight,
        font=dict(color='#CCCCCC'),
        titlefont=dict(color='white', size=fontsizeT),
##        dragmode = 'zoom',
        margin=dict(
                l=40,
                r=20,
                b=40,
                t=margintopFigs,
                ),
        hovermode="closest",

        plot_bgcolor="#191A1A",
        paper_bgcolor="#191A1A",
        showlegend = False,
##        legend = dict( #*********** top 5
##            font = dict(color='#CCCCCC', size='10'),
##            orientation='h',
##            bgcolor='rgba(0,0,0,0)'
##            )
        )


##    figure = dict(data=data, layout=layout_pie)

 
    return     dcc.Graph(id='pie_ExtFactors',figure = dict(data=data, layout=layout_pie))
           



##@app.callback(
##    Output('datatable-External', 'selected_row_indices'),
##    [Input('graph-External', 'clickData')],
##    [State('datatable-External', 'selected_row_indices')])
##def update_selected_row_indices(clickData, selected_row_indices):
##    if clickData:
##        for point in clickData['points']:
##            if point['pointNumber'] in selected_row_indices:
##                selected_row_indices.remove(point['pointNumber'])
##            else:
##                selected_row_indices.append(point['pointNumber'])
##    return selected_row_indices
##
##
##@app.callback(
##    Output('graph-External', 'figure'),
##    [Input('datatable-Externa', 'rows'),
##     Input('datatable-Externa', 'selected_row_indices')])
##def update_figure(rows, selected_row_indices):
##    custdata = pd.DataFrame(rows)
##    
##    custdatagroupage = custdata.groupby('age')
##    xage = list(custdatagroupage.groups.keys())  # group by month,
##    yage = custdatagroupage.agg(['count']).iloc[:,1]
##
##    custdatagroupdate = custdata.groupby('terminationdate_key')
##    xdate = list(custdatagroupdate.groups.keys())  # group by month,
##    ydate = custdatagroupdate.agg(['count']).iloc[:,1]
##
##    custdatagroupLen = custdata.groupby('length_of_service')
##    xLen = list(custdatagroupLen.groups.keys())  # group by month,
##    yLen = custdatagroupLen.agg(['count']).iloc[:,1]
##
##    
##    
##    fig = plotly.tools.make_subplots(
##        rows=3, cols=1,
##        subplot_titles=('Termination v.s. Termination date', 'Termination v.s. Age', 'Termination v.s. Length of employeement',),
##        shared_xaxes=True)
##    marker = {'color': ['#0074D9']*len(dff)}
##    for i in (selected_row_indices or []):
##        marker['color'][i] = '#FF851B'
##    fig.append_trace({
##        'x': xdate,
##        'y': ydate,
##        'type': 'bar',
##        'marker': marker
##    }, 1, 1)
##    fig.append_trace({
##        'x': xage,
##        'y': yage,
##        'type': 'bar',
##        'marker': marker
##    }, 2, 1)
##    fig.append_trace({
##        'x': xLen,
##        'y': yLen,
##        'type': 'bar',
##        'marker': marker
##    }, 3, 1)
##    fig['layout']['showlegend'] = False
##    fig['layout']['height'] = 800
##    fig['layout']['margin'] = {
##        'l': 40,
##        'r': 10,
##        't': 60,
##        'b': 200
##    }
##    fig['layout']['yaxis3']['type'] = 'log'
##    return fig



# In[]:
# Main
if __name__ == '__main__':
    app.server.run(debug = True, threaded=True)
