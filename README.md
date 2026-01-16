# thuuwa_tuuchi_bot
通話の開始をお知らせします

## コマンド一覧

すべてのコマンドは `/callnotion` グループ配下にあります。

| コマンド | 説明 |
|---------|------|
| `/callnotion set` | 通知を送信するチャンネルを設定します（コマンドを実行したチャンネルに設定） |
| `/callnotion textchange <newtext>` | 通知時のテキストを変更します（デフォルト: `@everyone`） |
| `/callnotion changenotificationmode` | 通話終了時に通知するかどうかを切り替えます |
| `/callnotion offchannel` | ボイスチャンネルごとに通知のオン/オフを切り替えます |
| `/callnotion offlist` | 各ボイスチャンネルの通知オン/オフ状態を確認します |
| `/callnotion getnotiontext` | 現在設定されている通知テキストを確認します |
| `/callnotion reset` | 設定をリセットします（終了時通知/通知テキスト/全て） |

## 初期設定

1. Botをサーバーに招待
2. 通知を送りたいテキストチャンネルで `/callnotion set` を実行
