#newTest.py
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go
import plotly.offline as pyo
import plotly.express as px
import dash_cytoscape as cyto
import pandas as pd
import numpy as np
from topicbar import create_topicbar
from topicColors import topicColors, topicColors2
import plotly.io as pio

from dash.dependencies import Input, Output, State, ClientsideFunction

#temlplates for plotly visualizations
my_template = go.layout.Template(
    layout=go.Layout(title_font_size=30,
            legend_font=dict(size=28),
            font_size = 28,
            hoverlabel_font=dict(size=40))
)

pio.templates['mine']=my_template
pio.templates.default ='seaborn+mine'

df= pd.read_excel('assets/Movement1ExtractedDataWithSecondaryTopics.xlsx')
#this is for the adjacency matrix
df['Next Topic']=df['Topic'].shift(-1)

defaultSonata = df['Sonata'].unique()[0]
#column names for table display
cnames=['Sonata', 'starting measure','ending measure','Topic','Secondary Topic','weighting']

#important features found
imp_features =['Amount_of_Arpeggiation','Average_Note_Duration','Average_Time_Between_Attacks','Chromatic_Motion',
'Diminished_Seventh_Simultaneity_Prevalence','Direction_of_Motion','Importance_of_Middle_Register','Melodic_Fifths',
'Melodic_Thirds',
'Major_Triad_Simultaneity_Prevalence',
'Melodic_Interval_Histogram_1','Most_Common_Note_Quarter_Length_Prevalence',
'Most_Common_Pitch_Class_Prevalence','Note_Density','Pitch_Class_Variety','Range','Stepwise_Motion','Tonal_Certainty']

feat_abbreviation={'Amount_of_Arpeggiation':'Amt Arpeggiation','Average_Note_Duration':'Avg. Note Duration','Average_Time_Between_Attacks':'Avg. Time Btwn Att.',
'Chromatic_Motion': 'Chromatic Motion',
'Diminished_Seventh_Simultaneity_Prevalence': 'Dim7th Simul. Prev.',
'Direction_of_Motion':'Dir. of Motion',
'Importance_of_Middle_Register':'Imp. of Mid. Register','Melodic_Fifths':'Melodic Fifths',
'Melodic_Thirds':'Meoldic Thirds',
'Major_Triad_Simultaneity_Prevalence':'Maj. Triad Simuul. Prev.',
'Melodic_Interval_Histogram_1':'Melodic Int. Hist. 1',
'Most_Common_Note_Quarter_Length_Prevalence': 'Most Common Note .25Len. Prev.',
'Most_Common_Pitch_Class_Prevalence': 'Most Common Pitch Class Prev.',
'Note_Density':'Note Density',
'Pitch_Class_Variety':'Pitch Class Var','Range':'Range',
'Stepwise_Motion':'Stepwise Motion',
'Tonal_Certainty':'Tonal Certainty', 'Sonata':'Sonata','Topic':'Topic'}
#network layout
nselector={'selector':'node','style':{'content':'data(label)'}}
styles = [{'selector':'[label="'+t+'"]','style':{'background-color':topicColors2[t]}} for t in topicColors2 ]
stylesheet=[nselector]
for s in styles:
    stylesheet.append(s)
stylesheet.append({'selector':'.extra','style':{'curve-style': 'bezier',
                    'source-endpoint':'outside-to-line',
                    'target-endpoint':'outside-to-line',
                    'target-arrow-shape':'triangle', 'arrow-scale':5}})
stylesheet.append({'selector':'.inter','style':{'label':'data(weight)', 'curve-style': 'bezier',
                    'source-endpoint':'outside-to-line',
                    'target-endpoint':'outside-to-line',
                    'target-arrow-shape':'triangle', 'arrow-scale':2}})

#make sure the parts follow each other
nextPart={'exposition: primary':'exposition: transition',
            'exposition: transition':'exposition: secondary',
            'exposition: secondary':'exposition: closing',
            'exposition: closing':'development',
            'development':'recapitulation: primary',
            'recapitulation: primary':'recapitulation: transition',
            'recapitulation: transition':'recapitulation: secondary',
            'recapitulation: secondary':'recapitulation: closing',
            'recapitulation: closing':'coda',
            'coda':None}
partPosition={'exposition: primary':(1,1),
            'exposition: transition':(1,2),
            'exposition: secondary':(1,3),
            'exposition: closing':(1,4),
            'development':(2,1),
            'recapitulation: primary':(3,1),
            'recapitulation: transition':(3,2),
            'recapitulation: secondary':(3,3),
            'recapitulation: closing':(3,4),
            'coda':(2,2)}
nodePos={1:[(1,1)],2:[(0,0),(2,2)],3:[(0,0),(1,1),(2,2)],4:[(0,0),(0,2),(2,0),(2,2)],
        5:[(0,0),(0,2),(0,1),(2,0),(2,2)], 6:[(0,0),(0,1),(0,2),(2,0),(2,1),(2,2)]}

parentPlacementFactor=300
pHeight =200
pWidth = 100

# more parts of the newtork analysis
def getElements(sonatas=None):

    s=defaultSonata
    if sonatas:
        s = sonatas[0]
    dfs=df[df['Sonata']==s]
    parents=[]
    children=[]
    for p in dfs['Part'].unique():
        pLab = p
        if p[0]=='e':
            pLab='exposition:' + p[2:]
        if p[0]=='r':
            pLab='recapitulation:'+p[2:]
        parents.append(pLab)

        #create the adjacency matrix for this part in the score
        sdfs = dfs[dfs['Part']==p]
        #make sure the measures are actually adjacent
        sdfs = sdfs[sdfs['ending measure']==sdfs['starting measure'].shift(-1)-1]
        sdfs = sdfs[sdfs['Topic']!=sdfs['Next Topic']]

        #adjacencey matrix:
        am = pd.crosstab(sdfs['Topic'],sdfs['Next Topic'])
        idx = am.columns.union(am.index)
        am = am.reindex(index = idx, columns=idx, fill_value=0)
        pX = partPosition[pLab][0]*parentPlacementFactor
        pY = partPosition[pLab][1]*parentPlacementFactor
        c=[]
        e=[]
        if not am.empty:
            numNodes = len(am.index)
            cx=1
            cy=1
            coords = nodePos[numNodes]
            nCount = 0

            for cn in am.index:
                newX = coords[nCount][0]
                newY = coords[nCount][1]
                ofX = (newX-cx)*(pWidth/2)
                ofY = (newY-cy)*(pHeight/2)
                # ofX = (cx-newX)*(pWidth/2)
                # ofY = (cy-newY)*(pHeight/2)
                myPosX =pX + ofX
                myPosY = pY + ofY

                c.append({
                    'data':{'id':p+cn,'label':cn,'parent':pLab},
                    'position':{'x': myPosX,'y':myPosY}
                })
                nCount = nCount + 1
            #c=[{'data':{'id':p+cn,'label':cn,'parent':pLab}} for cn in am.index]
            for ix, row in am.iterrows():
                for cr in am.columns:
                    if row[cr]!=0:
                        e.append({'data':{ 'source':p+ix,'target':p+cr,'weight':row[cr]},'classes':'inter'})
        else:
            sdfs = dfs[dfs['Part']==p]
            cn=sdfs['Topic'].unique()[0]
            c=[{'data':{'id':p+cn,'label':cn,'parent':pLab},
                'position':{'x':pX,'y':pY}}]
        for entry in c:
            children.append(entry)
        if e:
            for value in e:
                children.append(value)

    els =[
        {
            'data':{'id':p,'label':p,'parent':p.split(':')[0]},
            'position':{'x':partPosition[p][0]*parentPlacementFactor, 'y':partPosition[p][1]*parentPlacementFactor}
        } for p in parents]

    for p in parents:
        src=p
        nextP=nextPart[p]
        while nextP and nextP not in parents:
            nextP =nextPart[nextP]
        if nextP and p.split(':')[0]==nextP.split(':')[0]:
            targ =nextP
            els.append({'data':{'source':src,'target':targ},'classes':'extra'})
    for ch in children:
        els.append(ch)
    return els


#cyto.load_extra_layouts()



app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
#app = dash.Dash(
#     __name__)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Topics, Mozart, and Data Science</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''
header = html.Div(
            [
            html.Div(
                [
                html.Img(
                            src="assets/bwulogocolor.jpg",
                            id="bwu-logo",
                            style={
                            #    "height": "300px",
                            #    "width": "auto",
                            #    "margin-bottom": "25px",
                            },
                        )
                        ],className="one column",
            ),
            html.Div(
                [
                html.H1("Musical Topics in Mozart’s Piano Sonatas: A Data Science Approach",
                        className="poster-title"
                        ),
                html.H2("Jessica Narum and Andrew Watkins",
                className="poster-authors"
                ),
                html.H3("Conservatory of Music and Department of Computer Science, Baldwin Wallace University, Berea, OH",
                className="poster-affiliations"
                ),
                #html.Hr(className='fancy-line')
                ],className="ten columns", id="title"
            ),
            html.Div(
                [
                html.Img(
                            src="assets/bwulogocolor.jpg",
                            id="bwu-logoright",
                            style={
                            #    "height": "300px",
                            #    "width": "auto",
                            #    "margin-bottom": "25px",
                            },
                        )
                ],className="one column",
            ),
            ],className="row flex-display"
        )


center_head = html.Div(
                [
                #html.H3("A Data Science Approach",style={"font-size": "38pt","text-align": "center"}),#,className="twelve columns"),
                html.Div([
                dcc.Markdown('''Choose one or more first movements to display: ''',
                        #    style={'width':'100%'},
                            #className="three columns"
                            ),
                dcc.Dropdown(
                    id='dropdown-1',
                    options=[{'label':i,'value':i} for i in df['Sonata'].unique()],
                    multi=True,
                    placeholder='Select one or more movement',
                    #style={"text-align":"center", "width":"25%"}
                    #style={'width':'100%'},
                    #className="three columns"# offset-by-three columns"
                    ),
                    ],className="three columns"
                ),
                #html.Br(),
                html.Div([
                dcc.Markdown('''Listen to your first selection:''',
                #className='two columns'
                ),
                html.Audio(id='sonEx',controls=True, preload="auto",
                    #className = 'two columns'
                    #className='two columns offset-by-four columns'
                    )
                    ], className='two columns'
                )
                ],className='row flex-display'#,className="pretty_container"
                )

sc_mat =html.Div(
        [
            html.H1("Feature-Based Visualizations",style={"font-size": "38pt","font-weight":"bold","text-align": "center"}),
            dcc.Markdown('''
            Based on the topical analysis, we use the feature extraction
            capabilities of the [music21 toolkit](https://web.mit.edu/music21/)
            to determine the values of a wide variety of features in the music. These
            features can then be used in various contexts (such as machine learning and
            data visulizations). For example, the visualization below allows you
            to choose three of these features and compare their values in a
            scatter matrix.

            (Note, this visualization is only for the first sonata you chose
            or for K279-1, if you haven't chosen one.)

            **Choose Three Features:**
            ''',),
            html.Div(
            [
            dcc.Dropdown(
            id='featDrop1',
            options=[{'label':i.replace('_',' '),'value':i} for i in imp_features],
            value="Average_Time_Between_Attacks",
            clearable = False,
            style={"width":'100%',
                    "padding":"10px",
                    "font-size":"18pt",
                    "line-height":"36px"},
            optionHeight=200,
            #className="four columns"
            ),
            dcc.Dropdown(
            id='featDrop2',
            options=[{'label':i.replace('_',' '),'value':i} for i in imp_features],
            value="Most_Common_Pitch_Class_Prevalence",
            clearable = False,
            style={"width":'100%',
                    "padding":"10px 10px",
                    "font-size":"18pt",
                    "line-height":"36px"},
             optionHeight=200,
            #className="four columns"
            ),
            dcc.Dropdown(
            id='featDrop3',
            options=[{'label':i.replace('_',' '),'value':i} for i in imp_features],
            value="Average_Note_Duration",
            clearable = False,
            style={"width":'100%',
                    "padding":"10px",
                    "font-size":"18pt",
                    "line-height":"36px"},
            optionHeight=200,
            #className="four columns"
            )],className='row flex-display'),
            html.Div([dcc.Graph(id='ex-scatter-matrix', style={"height":'1200px'})])
        ], #className="three columns"
        className="panel-body pretty_container twelve columns"
        )
suc_an = html.Div(
    [
        html.H1("Examining Topical Succession",style={"font-size": "38pt","font-weight":"bold","text-align": "center"}),
        dcc.Markdown('''
        One of the benefits of this type of approach is that it allows us to quickly view
        how topics follow each other across a movement and even compare this type of
        succession across multiple works.

        (Note: Choosing no movements in the dialog box above results in all of the
        first movements being visualized.)
        '''),
        html.Div([dcc.Graph(id='topical-analysis', style={"height":"600px"}
                    #style={'height':'auto', 'font-size': '30pt'}
                    )
                    ])
    ], #className="three columns"
    className = 'panel-body pretty_container twelve columns'
)

# filters for the analysis table
sc=[]
for t in topicColors2:
    fq1='{Topic} eq "'+t+'"'
    fq2='{Secondary Topic} eq "'+t+'"'
    s1={'if':{'column_id': 'Topic','filter_query':fq1},'backgroundColor':topicColors2[t], 'color':'white'}
    s2={'if':{'column_id': 'Secondary Topic','filter_query':fq2},'backgroundColor':topicColors2[t], 'color':'white'}
    sc.append(s1)
    sc.append(s2)
s1={'if':{'column_id': 'Topic','filter_query':'{Topic} eq "singing style"'},'backgroundColor':topicColors2['singing style'], 'color':'black'}
s2={'if':{'column_id': 'Secondary Topic','filter_query':'{Secondary Topic} eq "sing style"'},'backgroundColor':topicColors2['singing style'], 'color':'black'}
sc.append(s1)
sc.append(s2)
s1={'if':{'column_id': 'Topic','filter_query':'{Topic} eq "learned style"'},'backgroundColor':topicColors2['learned style'], 'color':'black'}
s2={'if':{'column_id': 'Secondary Topic','filter_query':'{Secondary Topic} eq "learned style"'},'backgroundColor':topicColors2['learned style'], 'color':'black'}
sc.append(s1)
sc.append(s2)

analysis_table =html.Div(
    [
        html.H1("Identifying Topics",style={"font-size": "38pt","font-weight":"bold","text-align": "center"}),
        dcc.Markdown('''
        In order to facilitate computational analysis, we first
        labeled segments of the music with primary and (where applicable) secondary topics.
        To more accurately reflect the role of the secondary topic in the segment, we employed a weighting scheme
        where 'a' indicates only one topic present, 'b' indicates a 70% weight of the
        primary topic, and 'c' indicates that both identified topics were equally present. The
        role of this weighting is shown in the Examining Topical Succession Section.
        '''),
        html.Iframe(id='pdf-display',width='100%',height='1000px'),
        dash_table.DataTable(id='analysis-table',
                columns=[{'name':i,'id':i}for i in cnames],
                style_table={'overflowX':'scroll',
                'overflowY':'scroll',
                'height': '1000px'},
                style_cell={
                'whiteSpace': 'normal',
                'height': 'auto',
                'minWidth': '0px', 'maxWidth': '300px',
                'textAlign':'left',
                },
                style_cell_conditional=[
                {'if':{'column_id':'Topic'}, 'width':'30%'},
                ],
                style_data_conditional=sc,
                #fixed_rows={ 'headers': True, 'data': 0 },
                ),
        dcc.Markdown('''
            **Acknowledgments**:
            
            This work wouldn't be possible without our undergraduate student collaborators.

            **From the Conservatory of Music**: Rachel Fogle, Evan Fraser, Tim Michel

            **From the Department of Computer Science**: Ali Al-Ramezi, Miriam Alramzi, Tyler Hardy,
            Miranda Lemmer, Kyle Ray, Amari Sewell, Brandon Zlotnik
         ''')
        #data_proc
    ], #className="three columns"
    className='panel-body pretty_container four columns'
)

network_g = html.Div(
    [
       html.H1("Network Analysis",style={"font-size": "38pt","font-weight":"bold","text-align": "center"}),
       dcc.Markdown('''
      This visualization examines the links within
      each formal section of the movement presenting how topics interact with each other.

       Feel free to move these components around.

       (Note, this visualization is only for the first sonata you chose
       or for K279-1, if you haven't chosen one.)
       '''),
       html.P(id='netName',style={'font-weight':'bold','text-align':'center'}),
       cyto.Cytoscape(
            id='cyt-topics',
            layout={'name': 'preset',
                    'fit': True},
            #layout={'name':'dagre'},
            #layout ={'name': 'cola'},
            # layout={'name': 'cose-bilkent',
            #         'tile': False,
            #         'nestingFactor': 5,
            #         'gravity': 80,
            #         'nodeRepulsion': 400000},
            #layout={'name': 'breadthfirst',
            #        'roots': '[id="exposition: primary", id="development", id="recapitulation: primary"]'},
            #layout={'name': 'grid',
            #        'rows': 4,},
            #        'condense': True},
            #layout={'name': 'cose',
            #    'avoidOverlap': True},
            # layout={'name': 'cose',
            # 'idealEdgeLength': 100,
            # 'nodeOverlap': 20,
            # #refresh: 20,
            # 'fit': True,
            # 'padding': 30,
            # 'randomize': False,
            # 'componentSpacing': 100,
            # 'nodeRepulsion': 400000,
            # 'edgeElasticity': 100,
            # 'nestingFactor': 5,
            # #gravity: 80,
            # #numIter: 1000,
            # #initialTemp: 200,
            # #coolingFactor: 0.95,
            # #minTemp: 1.0
            # },
            style={'width': '100%', 'height': '2500px'},
            stylesheet=stylesheet,
            elements=getElements()
            )
    ],className="panel-body pretty_container four columns"#className='pretty_container three columns'
)

mid_column =html.Div(
[sc_mat, suc_an],className='pretty_container four columns'
)

center_body =html.Div([analysis_table,mid_column,network_g],className='row flex-display')
center_column = html.Div([center_head,center_body],className="twelve columns vjustify")
body=html.Div([center_column],className='row flex-display')
footer=html.Div([
    dcc.Markdown('''
        This work wouldn't be possible without our undergraduate student collaborators.
        From the Conservatory of Music:
        * Rachel Fogle
        * Evan Fraser
        * Tim Michel
        From the Department of Computer Science:
        * Ali Al-Ramezi
        * Miriam Alramzi
        * Tyler Hardy (class of 2019)
        * Miranda Lemmer (class of 2019)
        * Kyle Ray
        * Amari Sewell
        * Brandon Zlotnik
     ''')
],className="row flex-display")

app.layout=html.Div(
    [
        html.Div(
        [
    #    html.Div(id="output-clientside"),
        header,
        body
        ]#,className="row flex-display"
        )
    ],
    id="mainContainer",
    #style={"display": "flex", "flex-direction": "column"}
    className="poster"
    )

# Getting sound file name
@app.callback(
    Output('sonEx','src'),
    [Input('dropdown-1','value')]
)
def update_audio(sonatas=None):
    audioBase = "assets/audio/"
    fext = ".m4a"
    s=defaultSonata
    if sonatas:
        s = sonatas[0]
    return audioBase+s+fext
# Getting score pdf file name
@app.callback(
    Output('pdf-display','src'),
    [Input('dropdown-1','value')]
)
def update_pdf(sonatas=None):
    pdfBase = "assets/pdfs/Mozart"
    fext = ".pdf"
    s=defaultSonata
    if sonatas:
        s = sonatas[0]
    s=s[:-2]
    return pdfBase+s+fext+"#toolbar=0&view=fitH"

#topic bar cration
@app.callback(
    Output('topical-analysis','figure'),
    [Input('dropdown-1','value')]
)
def update_figure(sonatas=None):
    fig= create_topicbar(df,topicColors=topicColors2,sonatas=sonatas,
                            bar_width=.25,title='Topical Succession')
    fig.update_layout(font_size=24)
    fig.update_layout(title_font_size=24)
    fig.update_layout(height=550)
    return fig
#scatter matrix creation
@app.callback(
    Output('ex-scatter-matrix','figure'),
    [Input('featDrop1','value'),
    Input('featDrop2','value'),
    Input('featDrop3','value'),
    Input('dropdown-1','value')]
)
def update_smatrix(f1="Average_Time_Between_Attacks", f2="Most_Common_Pitch_Class_Prevalence",
                    f3="Average_Note_Duration", sonatas = None):
    s=defaultSonata
    if sonatas:
        s = sonatas[0]
    dfs = df[df['Sonata']==s]
    feats=[f1,f2,f3]
    if f1==f2 or f1==f3 or f2==f3:
        feats=['Average_Time_Between_Attacks','Most_Common_Pitch_Class_Prevalence','Average_Note_Duration' ]
    columns=["Sonata","Topic"]+feats#,"Average_Time_Between_Attacks","Most_Common_Pitch_Prevalence","Average_Note_Duration"]
    #feats=
    dfs=dfs[columns]
    fig = px.scatter_matrix(dfs,
        dimensions=feats,
        color="Topic",
        color_discrete_map=topicColors2,
        title="Scatter Matrix for "+s,
        #labels={"Average_Time_Between_Attacks":"Avg Time Between Att.", "Most_Common_Pitch_Prevalence":"Pitch Prev.",
        #        "Average_Note_Duration":"Avg Note Duration"}
        labels={col:feat_abbreviation[col] for col in dfs.columns}
        )
    fig.update_traces(diagonal_visible=False)
    fig.update_traces(showupperhalf=False)
    fig.update_traces(marker=dict(size=20))
    fig.update_layout(height=1200)
    fig.update_layout(font_size=24)

    return fig


@app.callback(
    Output('analysis-table', 'data'),
    [Input('dropdown-1','value')]
)
def update_table1(sonatas=None):
    s=defaultSonata
    if sonatas:
        s = sonatas[0]
    dfs = df[df['Sonata']==s]
    return dfs[cnames].to_dict('records')

@app.callback(
    Output('netName', 'children'),
    [Input('dropdown-1','value')]
)
def update_netName(sonatas=None):
    s=defaultSonata
    if sonatas:
        s = sonatas[0]
    return "Network Analysis for "+s

@app.callback(
    Output('cyt-topics', 'elements'),
    [Input('dropdown-1','value')]
)
def update_network(sonatas=None):
    return getElements(sonatas)

if __name__ == '__main__':
    app.run_server(debug=True)
