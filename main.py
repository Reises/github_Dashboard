import pandas as pd
from dash import Dash, dash_table, dcc, callback, Output, Input, html
import plotly.express as px #   グラフ描画
import dash_uploader as du

# Dashアプリ初期化
app = Dash(__name__)

# アップロード先フォルダ設定
UPLOAD_FOLDER = "uploads"
du.configure_upload(app, UPLOAD_FOLDER)


weekday_names = ['月', '火', '水', '木', '金', '土', '日']

# レイアウト定義
app.layout = html.Div(
    [
        html.H2("コミット履歴"),

        # ファイルアップロードUI
        du.Upload(
            id="dash-uploader",
            text = "ここにCSVをドラッグ&ドロップまたはクリックして選択",
            filetypes=["csv"],
        ),

        html.Hr(),

        # アップロード後にテーブルを表示する場所
        html.Div(id="table-area"),

        # アップロード後にグラフを表示する場所
        html.Div(id="graph-area"),
    ],
    style={"textAlign": "center", "width": "80%", "margin": "auto"}
)

# アップロード完了後の処理
@du.callback(
    output=[
        Output("table-area", "children"),
        Output("graph-area", "children"),
    ],
    id="dash-uploader",  # du.Uploadのidと一致させる
)
def display_uploaded_file(filenames):
    """
    filenames:アップロードされたファイルパスのリスト
    """

    if not filenames:
        return html.Div("ファイルがアップロードされていません。")
    
    # 最初の1つだけ使う
    filepath = filenames[0]

    # CSV読み込み
    df = pd.read_csv(filepath, encoding="UTF-16LE")

    # datetime変換
    df['date'] = pd.to_datetime(df['date'])

    # 曜日列
    df['weekday'] = df['date'].map(lambda x: weekday_names[x.weekday()])

    # 曜日ごとに集計
    weekday_counts = df.groupby('weekday').size().reindex(weekday_names)  # 月〜日の順に並べる

    # Dash DataTableに変換して返す
    return dash_table.DataTable(
        data = df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df.columns],
        page_size=10,
        style_table={"overflowX": "auto"}
    ),dcc.Graph(figure=px.bar(x=weekday_counts.index, y=weekday_counts.values, title="コミット曜日毎の集計"))


if __name__ == "__main__":
    app.run(debug=True)