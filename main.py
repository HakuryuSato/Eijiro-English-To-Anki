# クリップボードから取得するため
import pyperclip

# HTTP requests for AnkiConnect
import requests
import json


def input_data():
    lines = []
    text = pyperclip.paste()
    lines = text.split("\r\n")
    return lines


def edit_data(lines):
    parts_of_speech = ["名", "動", "形", "副", "代", "前", "接", "感", "自", "他"]
    # 単語と例文を分ける(最初の文字が"・"かどうか)
    lines = [item for item in lines if not item == ""]
    sentence = [item for item in lines if not item.startswith("・")]
    example = [item for item in lines if item.startswith("・")]

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
    
    # Ankiフォーマット用に前半と後半に分ける
    front_text = sentence_2[0]  # 単語
    back_text = "<br>".join(sentence_2[1:])  # 意味と例文

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
    eijiro_text = input_data()  # クリップボードから英辞郎テキスト取得

    # sample text for debug :D
    # eijiro_text = [
    #     "massive",
    #     "形",
    #     "〔通常の物に比べて〕巨大な、非常に重い",
    #     "・The massive mountain is located near our village. : 大きな山が私たちの村の近くにある。",
    #     "〔通常の数量に比べて〕極めて多い、大量の",
    #     "〔規模や程度などが〕圧倒的な、壮大な、大規模な",
    #     "《医》〔がんなどが〕病巣が広がった",
    #     "《医》〔病気などが〕重度の",
    #     "《鉱物》塊状の◆結晶構造がない、非結晶質のもの。",
    #     "《地学》〔岩石が〕層理のない",
    #     "〈俗〉〔限度を超えていて〕大変な、ひどい",
    #     "・I had a massive argument with him. : 彼とひどい口げんかをしてしまった。",
    # ]

    front, back = edit_data(eijiro_text)
    send_to_anki(front, back)


if __name__ == "__main__":
    main()
