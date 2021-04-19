#! /usr/bin/env python3

import json
import urllib.request as ur
from enum import Enum

import nfc

API_ENDPOINT = 'http://localhost:3000/v1/room'

PASORI_S380_PATH = 'usb:054c:06c3'


class Status(Enum):
    """状態を格納するenum

    メンバーは文字列
    SUCCESS : カードから番号が読み取れた
    ERROR   : カードとの通信時に何らかのエラーが発生した
    FATAL   : プロセスを終了する程度の深刻なエラー

    """
    SUCCESS = 'success'  # successfully read
    ERROR   = 'error'    # failed to read
    FATAL   = 'fatal'    # process will die


def send_status(status, user_id=None):
    """バックエンドサーバーにリクエストを投げる

    Parameters
    ----------
        status : Status
            カードの読み取り成功/失敗を表すenum
        user_id : int, optional
            カードから読み取った番号
            読み取りに失敗していた場合はNoneが設定される

    """
    data = json.dumps({
        'status': status.value,
        'user_id': user_id
    }).encode('utf-8')

    headers = {
        'Content-Type': 'application/json',
    }

    req = ur.Request(
        url=API_ENDPOINT, data=data,
        headers=headers, method='POST')

    try:
        with ur.urlopen(req):
            pass
    except Exception as e:
        print('\033[01;33m[!]\033[0m {}\n'.format(e))


def run():
    """
    メインルーチン
    これがずっと回る

    """
    try:
        with nfc.ContactlessFrontend(PASORI_S380_PATH) as clf:
            while clf.connect(rdwr={'on-connect': on_connect}):
                pass

    except OSError as ose:
        print('\033[01;31m[!]\033[0m {}'.format(ose))
        send_status(Status.FATAL)
        print('\033[01;31m[!]\033[0m Stop')
        exit(-1)


def on_connect(tag):
    """This function is called when a remote tag has been activated.

    カードにアクセスできた後の処理はこの関数を起点にして行う

    エラー処理に関して
    cf. https://github.com/nfcpy/nfcpy/blob/master/src/nfc/tag/__init__.py
    0x01A6 => "invalid service code number or attribute"
    0x0(nfc.tag.TIMEOUT_ERROR) => "unrecoverable timeout error"

    Parameters
    ----------
    tag : nfc.tag.Tag
        NFCカード

    Returns
    -------
    bool
        成功/失敗

    """
    print('\033[01;32m[*]\033[0m Card touched.')
    try:
        sc = nfc.tag.tt3.ServiceCode(0x200B >> 6, 0x200B & 0x3f)
        bc = nfc.tag.tt3.BlockCode(0, service=0)  # To get student ID
        block_data = tag.read_without_encryption([sc], [bc])

    except nfc.tag.TagCommandError as e:
        send_status(Status.ERROR)

        if e.errno == 0x1A6:
            print('\033[01;33m[!]\033[0m \
Your IC card seems to be unavailable. Is it valid one?\n')
        elif e.errno == 0x0:
            print('\033[01;33m[!]\033[0m \
Too short. Please touch your card again\n')
        else:
            print('\033[01;33m[!]\033[0m {}\n'.format(e))
        return False

    user_id_str = block_data[1:9].decode('utf-8') # bytearrayなのでdecode()を呼べる
    # 読み取ったuser_idの桁数を確認する(8桁なら正しい)
    if len(user_id_str) == 8:
        user_id = int(user_id_str)
        send_status(Status.SUCCESS, user_id)
    else:
        print('[!] ID length was incorrect. ID: {}'.format(user_id_str))
        send_status(Status.ERROR)

    return True


if __name__ == '__main__':
    print('\033[01;32m[*]\033[0m Hello!')
    run()
