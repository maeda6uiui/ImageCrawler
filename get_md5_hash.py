"""
与えられた文字列のハッシュ値を計算する。
(補助ツール)
"""
import hashlib
import sys

if __name__=="__main__":
    args=sys.argv
    h=hashlib.md5(args[1].encode()).hexdigest()
    print(h)
