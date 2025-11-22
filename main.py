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
month_names = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']

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

        # アップロード後に月別グラフを表示する場所
        html.Div(id="month-area"),
    ],
    style={"textAlign": "center", "width": "80%", "margin": "auto"}
)

# アップロード完了後の処理
@du.callback(
    output=[
        Output("table-area", "children"),
        Output("graph-area", "children"),
        Output("month-area", "children"),
    ],
    id="dash-uploader",  # du.Uploadのidと一致させる
)
# 直前のデコレータで呼ばれている。一致するid（du.uploader)つまりファイルがアップロードされたらファイルのパスをリスト形式で引数filenamesに渡される
def display_uploaded_file(filenames):
    """
    filenames:アップロードされたファイルパスのリスト
    """

    if not filenames:
        return html.Div("ファイルがアップロードされていません。")
    
    # 最初の1つだけ使う
    filepath = filenames[0]

    # CSV読み込み
    try:
        df = pd.read_csv(filepath, encoding="UTF-16LE")
    except Exception as e:
        return html.Div(f"ファイルの読み込みに失敗しました。CSVの形式や文字コード(UTF-16LE)を確認してください。(Error: {e})")

    # datetime変換
    df['date'] = pd.to_datetime(df['date'])

    # 曜日列
    df['weekday'] = df['date'].map(lambda x: weekday_names[x.weekday()])

    # 月列 x[-2:]は2025-01の場合、01を取得するそれをintにすると1になるただ、month_names[1]は2月なので、1を引いてから月名を取得する
    df['month'] = df['date'].dt.to_period('M').astype(str).map(lambda x: month_names[int(x[-2:]) - 1])

    # 曜日ごとに集計
    weekday_counts = df.groupby('weekday').size().reindex(weekday_names)  # 月〜日の順に並べる
    month_counts = df.groupby('month').size().reindex(month_names)

    # Dash DataTableに変換して返す
    return dash_table.DataTable(
        data = df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df.columns],
        page_size=10,
        style_table={"overflowX": "auto"}
    ),dcc.Graph(figure=px.bar(x=weekday_counts.index, y=weekday_counts.values, title="コミット曜日毎の集計")),dcc.Graph(figure=px.bar(x=month_counts.index, y=month_counts.values, title="コミット月毎の集計"))


if __name__ == "__main__":
    app.run(debug=True)