import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from tokenizer import ChineseTokenizer

def test_tokenize():
    tokenizer = ChineseTokenizer()
    result = tokenizer.tokenize("結巴中文分詞")
    assert result == {
        "結巴": 1,
        "中文": 1,
        "分詞": 1,
    }

def test_tokenize_from_url():
    tokenizer = ChineseTokenizer()
    tokenizer.tokenize_from_url("https://www.chinatimes.com/realtimenews/20220604000014-260410?chdtv")

def test_tokenize_filter():
    tokenizer = ChineseTokenizer()
    tokenizer.add_keyword("結巴")
    tokenizer.add_keyword("分詞")
    result = tokenizer.filter_keyword({
        "結巴": 8,
        "中文": 93,
        "分詞": 32,
    })
    assert result == {
        "結巴": 8,
        "分詞": 32,
    }
