import discord
import asyncio
import os
from dotenv import load_dotenv
# やるべきこと→受信するチャンネルが複数の場合の実装、getenvで取得するチャンネルIDを配列に格納する実装

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# 受信するテキストチャンネルIDを指定（送信元）
SOURCE_CHANNEL_IDS = os.getenv("SOURCE_CHANNEL_ID")  # 受信元のチャンネルIDを取得
# メッセージを転送するテキストチャンネルIDを指定（送信先）
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID")) # 転送先のチャンネルIDを取得

if SOURCE_CHANNEL_IDS:
    try:
        # カンマで分割してリストに変換し、さらに各要素を int に変換

        source_channel_list =[int(item) for item in SOURCE_CHANNEL_IDS.split(',')]
    except ValueError:
        print("Error: 環境変数に整数以外の値が含まれています。")
else:
    print("Error: 環境変数'SOURCE_CHANNEL_ID'が見つかりません。")

# Discordクライアントのインスタンスを作成
intents = discord.Intents.default()
intents.messages = True  # メッセージイベントを有効にする
intents.message_content = True  # メッセージコンテンツインテントを有効化
client = discord.Client(intents=intents)

# リプライの追跡用辞書 {メッセージID: リプライがついたかどうか（True/False）}
message_tracker = {}
# 遅延時間（秒単位）
DELAY_SECONDS = 10

@client.event
async def on_ready():
    print(f"Bot is ready. Logged in as {client.user}")

@client.event
async def on_message(message):
    # ボット自身のメッセージは無視
    if message.author == client.user:
        return

    # メッセージが指定された送信元チャンネルから送られた場合
    if source_channel_list[message.channel.id]:
        # 送信先チャンネルを取得
        target_channel = client.get_channel(TARGET_CHANNEL_ID)
        if not target_channel:
            print(f"エラー: 指定された送信先チャンネルID {TARGET_CHANNEL_ID} が見つかりません。")
            return
    else: # 送信元チャンネル以外からのメッセージは無視する
        return
    
    # メッセージがリプライであるかを確認。
    if message.reference and message.reference.message_id:
        # リプライの場合
        original_message_id = message.reference.message_id
        # リプライ元のメッセージが追跡対象であれば、リプライがついたことを記録
        if original_message_id in message_tracker:
            message_tracker[original_message_id] = True
            # ここはテスト用で使う部分のためコメントアウト
            # print(f"リプライがつきました: メッセージID {original_message_id}")
   # 通常のメッセージの場合
    else:
        # 通常のメッセージを追跡対象に追加
        original_message_id = message.id
        message_tracker[original_message_id] = False

        # ユーザーからのメッセージを受け取り、即座に応答
        # ここはテスト用で使う部分のためコメントアウト
        # await message.channel.send(f"メッセージを受け取りました: `{message.content}`")
        # await message.channel.send(f"{DELAY_SECONDS}秒後に同じメッセージを送信します...")

        # ユーザー名とチャンネルリンクを取得
        user_name = message.author.display_name
        channel_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}"
    
        # 一定時間後にリプライがない場合は再投稿
        await asyncio.sleep(DELAY_SECONDS)
        if not message_tracker[original_message_id]:
            await target_channel.send(f"募集主:{user_name}さん\n\n{message.content}\n\n返信は下記リンク先のメッセージへお願いします\n\n{channel_link}")

        else:
            print(f"リプライが検出されたため再投稿をスキップします: メッセージID {original_message_id}")

        # 二回目
        await asyncio.sleep(DELAY_SECONDS)
        if not message_tracker[original_message_id]:
            await target_channel.send(f"募集主:{user_name}さん\n\n{message.content}\n\n返信は下記リンク先のメッセージへお願いします\n\n{channel_link}")

        else:
            print(f"リプライが検出されたため再投稿をスキップします: メッセージID {original_message_id}")

        # 追跡を終了（必要に応じて削除）
        del message_tracker[original_message_id]

# ボットを実行
client.run(TOKEN)
