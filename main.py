# クリップボードから取得するため
import pyperclip

# HTTP requests for AnkiConnect
import requests
import json


def debug_text(text, label=""):
    """デバッグ用：テキストの内容を詳細に表示"""
    print(f"\n=== {label} ===")
    print("Raw content:")
    print(repr(text))
    print("\nHex representation:")
    print(" ".join(hex(ord(c)) for c in text))
    print("=" * 50)


def input_data():
    text = pyperclip.paste()
    debug_text(text, "Clipboard Content")
    
    # 改行コードの確認
    print("\nLine break types found:")
    crlf = "\r\n"
    lf = "\n"
    cr = "\r"
    print(f"CRLF count: {text.count(crlf)}")
    print(f"LF count: {text.count(lf)}")
    print(f"CR count: {text.count(cr)}")
    
    # Handle different types of line breaks
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    lines = text.split('\n')
    
    print("\nSplit lines:")
    for i, line in enumerate(lines):
        print(f"Line {i}: {repr(line)}")
    
    return [line for line in lines if line.strip()]


def edit_data(lines):
    parts_of_speech = ["名", "動", "形", "副", "代", "前", "接", "感", "自", "他"]
    
    print("\nProcessing lines:")
    for i, line in enumerate(lines):
        print(f"Line {i}: {repr(line)}")
    
    # 単語と例文を分ける(最初の文字が"・"かどうか)
    sentence = [item for item in lines if not item.startswith("・")]
    example = [item for item in lines if item.startswith("・")]

    if not sentence:
        raise ValueError("No valid content found in text")
    
    print("\nMain content:")
    for i, s in enumerate(sentence):
        print(f"Content {i}: {repr(s)}")

    # 本文の編集 *1文字目が数字なら削除
    sentence = [item[1:] if item and item[0].isdigit() else item for item in sentence]

    sentence_2 = []
    for i, word in enumerate(sentence):
        if i == 1:
            sentence_2.append(word)
            continue

        elif word[0] in parts_of_speech:  # 1文字目に品詞の頭文字があるか
            sentence_2.append("")
            sentence_2.append(word)

        else:
            sentence_2.append(word)

    # 例文の編集
    example_2 = []
    example = [item[1:] for item in example]  # "・"削除

    for line_example in example:  # ":"を空白データ化
        if ":" in line_example:
            data_split = line_example.split(" : ")
            example_2.append(data_split[0])
            example_2.append(data_split[1])
            example_2.append("")
        else:
            example_2.append(line_example)

    example_2.insert(0, "")  # 例文の先頭に空白データ

    # 全体を結合する
    sentence_2.extend(example_2)
    
    print("\nProcessed content:")
    for i, s in enumerate(sentence_2):
        print(f"Final {i}: {repr(s)}")
    
    # Ankiフォーマット用に前半と後半に分ける
    front_text = sentence_2[0] if sentence_2 else ""  # 単語
    back_text = "<br>".join(sentence_2[1:]) if len(sentence_2) > 1 else ""  # 意味と例文

    if not front_text or not back_text:
        raise ValueError("Failed to create card content - empty front or back")

    print("\nFinal card content:")
    print(f"Front: {repr(front_text)}")
    print(f"Back: {repr(back_text)}")

    return front_text, back_text


def send_to_anki(front, back):
    """AnkiConnectを使用してカードを作成する"""
    url = "http://localhost:8765"
    
    note = {
        "deckName": "ALL_DECK::Basic Knowledge::English",
        "modelName": "English",
        "fields": {
            "Front": front,
            "Back": back
        },
        "options": {
            "allowDuplicate": False
        },
    }
    
    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": note
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        if result.get("error") is not None:
            print(f"Error: {result['error']}")
            return False
        print("Card created successfully!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to create card: {str(e)}")
        print("Make sure Anki is running and AnkiConnect is installed.")
        return False


def main():
    try:
        eijiro_text = input_data()  # クリップボードから英辞郎テキスト取得
        if not eijiro_text:
            print("Error: No valid text found in clipboard")
            return
        front, back = edit_data(eijiro_text)
        if not send_to_anki(front, back):
            print("Failed to create Anki card")
    except ValueError as e:
        print(f"Error processing text: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
