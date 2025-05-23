"""
Whale Watcher — отслеживает транзакции и сигнализирует, если переводы превышают указанный порог (например, 1000 BTC).
"""

import requests
import time

THRESHOLD_BTC = 1000  # Порог в BTC

def fetch_latest_block_height():
    r = requests.get("https://blockstream.info/api/blocks/tip/height")
    r.raise_for_status()
    return int(r.text)

def fetch_block_hash(height):
    r = requests.get(f"https://blockstream.info/api/block-height/{height}")
    r.raise_for_status()
    return r.text

def fetch_block_txids(block_hash):
    r = requests.get(f"https://blockstream.info/api/block/{block_hash}/txids")
    r.raise_for_status()
    return r.json()

def fetch_tx(txid):
    r = requests.get(f"https://blockstream.info/api/tx/{txid}")
    r.raise_for_status()
    return r.json()

def sat_to_btc(sats):
    return sats / 100_000_000

def analyze_transaction(tx):
    total_output = sum(vout["value"] for vout in tx["vout"])
    btc_value = sat_to_btc(total_output)
    return btc_value

def main():
    print(f"🐋 Whale Watcher запущен. Отслеживаем транзакции с порогом > {THRESHOLD_BTC} BTC...")

    last_checked = fetch_latest_block_height()

    while True:
        current_height = fetch_latest_block_height()
        if current_height > last_checked:
            for height in range(last_checked + 1, current_height + 1):
                try:
                    block_hash = fetch_block_hash(height)
                    txids = fetch_block_txids(block_hash)
                    print(f"🔍 Анализ блока {height} ({len(txids)} транзакций)")
                    for txid in txids:
                        tx = fetch_tx(txid)
                        value = analyze_transaction(tx)
                        if value > THRESHOLD_BTC:
                            print(f"🚨 Крупная транзакция: {value:.2f} BTC (txid: {txid})")
                    last_checked = height
                except Exception as e:
                    print(f"⚠️ Ошибка обработки блока {height}: {e}")
        time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("⏹️ Завершено пользователем.")
