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
