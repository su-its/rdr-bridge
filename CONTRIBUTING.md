# 開発者ガイド

## 必要機材

Sonyのカードリーダー `PaSoRi SC-360/P`が必要。

---

## 使い方

必要なモジュールがインストールされていない場合は以下の通りインストール。

```shell
pip3 install -r requirement.txt
```

```shell
./main.py
```

止めるときはCTRL+C。

---

## エンドポイントへ送るJSON

```json5
{
  // Example
  "status": "success", // status: string ("success" | "error" | "fatal")
  "user_id": 1         // user_id: number | null (is null iff status is not "success")
}
```

```json5
{
  // Another example
  "status": "error",
  "user_id": null
}
```
