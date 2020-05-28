#topicbar.py
#
# This is borrowed heavily from plotly's figure_factory create_gantt
import pandas as pd
import numpy as np
import plotly.graph_objs as go

def create_topicbar(df, topicColors = None, sonatas=None,bar_width = 0.2,
                    title='Topical Analysis', xtitle='Measures',
                    ytitle='Sonatas'):
    """
    returns a figure for a topic bar graph

    This function creates plotly style data and layout dictionaries
    for creating a topicbar visualzation of the progression of
    topics across a musical work.


    :param (dataframe) df: It assumes that df is a pandas style dataframe that has
        at least the followingcolumns:
        Sonata--string identifying which sonata a row of data correspondes to
        Topic--the Primary topic classification for the particular chunk of measures
        Secondary Topic--the secondary classification
        starting measure--which measure does this chunk begin on
        ending measure--which measure does this chunk end on
        weighting--how heavily weighted is the primary vs secondary topic?
            --'a' 100% Primary
            --'b' 70% Primary 30% Secondary
            --'c' 50% Primary 50% Secondary
        Identifier--an identifier/label for each chunk
    :param (dictionary) topicColors: a mapping from topics to hex colors
    :param (list) sonatas: List indicating which sonatas to include in the analysis.
        If no list is provided,then all sonatas in df are graphed
    :param (float) bar_width: The width of horizontal bars in the plot
    :param (string) title: title for the chart
    :param (string) xtitle: title for the xaxis
    :param (string) ytitle: title for the yaxis
    """

    #Have to have a mapping from topics to colors
    if not topicColors:
        raise ValueError("Must Provide a dictionary of topic colors")

    #If specific sonatas are given, use that subset of the data
    if sonatas:
        df=df[df['Sonata'].isin(sonatas)]

    #Get the individual sonata names
    sons=df['Sonata'].unique()

    #Get all of the topics in the data set
    tps = df['Topic'].append(df['Secondary Topic'][df['Secondary Topic'].notna()])
    topics =tps.unique()

    #Number those sonatas for graph placement
    gids={}
    for i,s in enumerate(sons):
        gids[s]=i

    chunks=[]
    topicChunks={}

    # Capture the extent of each chunk including both primary and secondary
    # topics. This will be used for the coordinates of the rectangles.
    # This loop also assigns appropriate identifying labels to each chunk.
    for index,row in df.iterrows():
        #print(df[index]['start'])
        chunk = dict(x0=row['starting measure'],
                    x1=row['ending measure']+1)
        chunk['description']="{0} {1}\n{2}".format(row["Identifier"],row['Part'],"Primary")
        gid = gids[row['Sonata']]
        chunk['gid']=gid
        weight = row['weighting']
        chunk['y0']=gid-bar_width

        chunk['y1']=gid+bar_width
        if weight=='b':
            chunk['y1']=gid-bar_width + 2*bar_width*.7
        elif weight == 'c':
            chunk['y1']=gid
        chunk['topic']=row["Topic"]
        chunk['fillcolor']=topicColors[chunk['topic']]
        chunks.append(chunk)
        if chunk['topic'] not in topicChunks:
            topicChunks[chunk['topic']]=chunk
            #topicsIncluded.append(chunk['topic'])
        if weight =='b' or weight == 'c':
            chunk2=dict(x0=row['starting measure'],
                        x1=row['ending measure']+1)
            chunk2['description']="{0} {1}\n{2}".format(row["Identifier"],row['Part'],"Secondary")
            chunk2['gid']=gid
            if weight=='b':
                chunk2['y0']=gid-bar_width + 2*bar_width*.7
            else:
                chunk2['y0']=gid
            chunk2['y1']=gid+bar_width
            chunk2['topic']=row['Secondary Topic']
            chunk2['fillcolor']=topicColors[chunk2['topic']]
            chunks.append(chunk2)
            if chunk2['topic'] not in topicChunks:
                topicChunks[chunk2['topic']]=chunk2



    data=[]

    #Create data to generate the legend.
    for t in topics:
        data.append(
            go.Scatter(
                x=[topicChunks[t]['x0']+0.5,topicChunks[t]['x0']+0.5],
                y=[topicChunks[t]['y0']+bar_width*.2,topicChunks[t]['y0']+bar_width*0.2],
                visible='legendonly',
                hoverinfo='none',
                text=t,
                name=t,
                legendgroup=t,
                mode='markers',
                marker = dict(
                    color = topicColors[t],
                    symbol = 'circle',
                    )

                )
            )

    # Create data for tracing
    for index in range(len(chunks)):
        entry = go.Scatter(
            x=[chunks[index]['x0'],chunks[index]['x1'],chunks[index]['x1'],chunks[index]['x0']],
            y=[chunks[index]['y0'],chunks[index]['y0'],chunks[index]['y1'],chunks[index]['y1']],
            showlegend = False,
            legendgroup=chunks[index]['topic'],
            text = chunks[index]['description'],
            name=chunks[index]['topic'],
            fill='toself',
            fillcolor=topicColors[chunks[index]['topic']],
            hoverinfo="x+text+name",
            hoveron="fills",
            mode='lines',
            marker=dict(
                color = topicColors[chunks[index]['topic']],
                #color = "white",
                symbol = 'circle',
                size = 1
                )
            )
        data.append(entry)

    # various layout parameters
    layout = go.Layout(
        title =  title,
        showlegend = True,
        hovermode='closest',
        yaxis = dict(
            title=ytitle,
            ticktext=sons,
            tickvals=list(range(len(sons))),
            range = [-1,len(sons)],
            autorange=False,
            zeroline = False,
            showgrid =False

        ),
        xaxis = dict(
            title=xtitle,
            zeroline=False,
            showgrid = False,
        )
    )
    fig = go.Figure(data=data,layout=layout)
    return fig
