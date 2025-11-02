# 使用方法
gitのコミット履歴を調べたいリポジトリまでcdコマンドを使用する
そのあと、以下のコマンドを使用する
echo "date,detail" > log.csv

実行後、以下のコマンドを使用する
git log --encoding=sjis --pretty=format:"%ad,%s" --date=short >> log.csv