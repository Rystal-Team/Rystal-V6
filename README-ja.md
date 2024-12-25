<div align="center">
  <a href="https://github.com/Rystal-Team/Rystal-V6/blob/main/assets/logo.png?raw=true">
    <img src="assets/logo.png" alt="Logo" width="80" height="80">
  </a>
  <h3 align="center">Rystal V6</h3>
  <p align="center">
    Pythonで書かれたシンプルなボットで、便利なユーティリティを備えています
    <br />
    <br />  
    <a href="https://github.com/Rystal-Team/Rystal-V6/issues">問題を報告</a>
    · 
    <a href="https://github.com/Rystal-Team/Rystal-V6/releases">リリース</a>
    · 
    <a href="./README.md">English</a>
  </p>
</div>

<div align="center">

[![GitHub Forks](https://img.shields.io/github/forks/Rystal-Team/Rystal-V6.svg?style=for-the-badge)](https://github.com/Rystal-Team/Rystal-V6)
[![GitHub Stars](https://img.shields.io/github/stars/Rystal-Team/Rystal-V6.svg?style=for-the-badge)](https://github.com/Rystal-Team/Rystal-V6)
[![License](https://img.shields.io/github/license/Rystal-Team/Rystal-V6.svg?style=for-the-badge)](https://github.com/Rystal-Team/Rystal-V6/blob/main/LICENSE)
[![Github Watchers](https://img.shields.io/github/watchers/Rystal-Team/Rystal-V6.svg?style=for-the-badge)](https://github.com/Rystal-Team/Rystal-V6)
[![Black Formatter](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)

</div>

## 🌟 主な機能

- 音楽プレイヤー
    - lavalink/wavelinkなどのリモートサーバー設定なしでプレイヤーが動作
    - Pythonで書かれたほとんどのDiscordボットと比べて豊富な機能を提供
    - 最も再生された曲の要約ポスター
    - 歌詞
- ランクシステム
- 多言語対応
- ポイントシステム
- ノートシステム
- 権限システム
- ミニゲーム
    - ブラックジャック
    - サイコロ
    - コインフリップ
    - ジャックポット
    - ルーレット

## 📸 スクリーンショット

<details>
<summary><h2>表示</h2></summary>

![screenshot](assets/screenshot_1.png)
![screenshot](assets/screenshot_2.png)
![screenshot](assets/screenshot_3.png)
![screenshot](assets/screenshot_4.png)
</details>

## ⚙️ セットアップ

[リリース](https://github.com/Rystal-Team/Rystal-V6/releases)
から最新の[リリース](https://github.com/Rystal-Team/Rystal-V6/releases/latest)をダウンロードしてください。

ボットを実行するには、`requirements.txt`にある要件を`pip install -r <path-to>/requirements.txt`
でインストールするだけです。<br>
**Pterodactylのようなコンテナでは、`setuptools`
が既に含まれているため、インストール時に問題が発生する可能性があります。その場合は、`container-requirements.txt`
を使用するか、`requirements.txt`から`setuptools`を削除してください。*

メインの設定ファイルは`.env`です。`.env.example`のコピーを作成し、それを`.env`
にリネームして必要なトークンを入力してください。<br>
ボットのカスタマイズは`config/example.config.yaml`にあります。コピーを作成し、それを`config.yaml`にリネームして続行してください。

## 🚀 使用技術

このボットは以下の技術で構築され、動作しています

- [![YouTube](https://img.shields.io/badge/YTDLP-ffffff?style=for-the-badge&logo=youtube&logoColor=ff0000)](https://github.com/yt-dlp/yt-dlp)
- [![Python](https://img.shields.io/badge/python-ffffff?style=for-the-badge&logo=python&logoColor=3670A0)](https://www.python.org/)
- [![FFMpeg](https://img.shields.io/badge/ffmpeg-ffffff?style=for-the-badge&logo=ffmpeg&logoColor=388e3c)](https://ffmpeg.org/)

## 🌐 ホスティングプロバイダーを探している？

Sparked Hostをチェックしてください！月額1ドル（約150円）から！<br>

- 設定が簡単
- 無料のSQLデータベース

<a href="https://billing.sparkedhost.com/aff.php?aff=2435"><img src="assets/sparkedhost.png" alt="Sparked Host" style="width:373.875px;height:78px;"/></a>

<div align="center">
	<p><small>Emoji Icons by <a href="https://icons8.com">icons8</a></small></p>
	<p><small>Copyright © 2024 <a href="https://rystal.net">Rystal</a>. All rights reserved.</small></p>
</div>

