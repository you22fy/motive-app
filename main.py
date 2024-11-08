import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_sortables import sort_items
import json

if 'events' not in st.session_state:
    st.session_state.events = {
        '幼少期': [],
        '小学校': [],
        '中学校': [],
        '高校': [],
        '大学': []
    }
    st.session_state.event_id_counter = 0

st.set_page_config(page_title="モチベーショングラフ", layout="wide")
st.title("モチベーショングラフ作成アプリ")

with st.sidebar:
    st.header("イベントの追加")
    period = st.selectbox("時期を選択", ['幼少期', '小学校', '中学校', '高校', '大学'])
    event = st.text_input("出来事")
    motivation = st.slider("モチベーションスコア", -10, 10, 0)

    if st.button("イベントを追加"):
        if event:
            st.session_state.events[period].append({
                "event": event,
                "motivation": motivation,
                "id": st.session_state.event_id_counter
            })
            st.session_state.event_id_counter += 1
            st.success("イベントが追加されました！")


st.header("モチベーショングラフ")
graph_data = []
time_mapping = {
    '幼少期': 0,
    '小学校': 1,
    '中学校': 2,
    '高校': 3,
    '大学': 4
}

for period, events in st.session_state.events.items():
    base_x = time_mapping[period]
    for i, event in enumerate(events):
        x = base_x + (i / (len(events) + 1)) if events else base_x
        graph_data.append({
            'Time': x,
            'Motivation': event['motivation'],
            'Event': event['event'],
            'Period': period
        })

if graph_data:
    df = pd.DataFrame(graph_data)

    fig = px.line(df, x='Time', y='Motivation',
                  title='モチベーション推移',
                  labels={'Time': '時期', 'Motivation': 'モチベーション'},
                  markers=True)

    fig.update_traces(
        hovertemplate="<b>%{customdata}</b><br>" +
        "モチベーション: %{y}<br>" +
        "<extra></extra>",
        customdata=df['Event']
    )

    fig.update_xaxes(
        ticktext=list(time_mapping.keys()),
        tickvals=list(time_mapping.values())
    )

    fig.update_layout(
        hovermode='closest',
        plot_bgcolor='white',
        yaxis_range=[-10, 10],
        yaxis_gridcolor='lightgray',
        xaxis_gridcolor='lightgray'
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("イベントを追加するとグラフが表示されます。")


st.header("イベント一覧")
for period in st.session_state.events.keys():
    st.subheader(period)
    if len(st.session_state.events[period]) > 0:
        items_with_ids = [
            f"{event['id']}::{event['event']} ({event['motivation']})"
            for event in st.session_state.events[period]
        ]

        sorted_items = sort_items(
            items_with_ids,
            direction="vertical",
            key=f"sort_{period}_{st.session_state.event_id_counter}"
        )

        if sorted_items:
            new_order_ids = [int(item.split("::")[0]) for item in sorted_items]
            id_to_event = {
                event["id"]: event for event in st.session_state.events[period]}
            st.session_state.events[period] = [
                id_to_event[id_] for id_ in new_order_ids]
    else:
        st.write("イベントがありません。")
