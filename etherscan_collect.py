"""
etherscan_collect.py
Collect Ethereum transaction data for one or more addresses via the Etherscan API (V2).

What it collects for each address (you can choose which):
  normal   - ordinary ETH transactions        (Etherscan "Transactions" tab)
  internal - ETH moved by contracts           (Etherscan "Internal Transactions" tab)
  token    - ERC-20 token transfers           (Etherscan "Token Transfers (ERC-20)" tab)

What it adds for you:
  - Values converted to ETH / token units (not wei)
  - Timestamps converted to UTC dates
  - Direction (IN / OUT) relative to the address you asked about
  - A "dust" flag for tiny amounts (likely spam / address poisoning)
  - An FBI-list check on the counterparty (FULL-address match only)

Output: one CSV file per address per type, plus all_transactions.csv with everything.

HOW TO RUN
  1. Install the one library it needs:      pip install requests
  2. Get a free API key: etherscan.io -> sign in -> API Dashboard -> Add
  3. Run with the Bybit preset (Exploiters 2, 4, 5 on 21-22 Feb 2025):
         python etherscan_collect.py
     or for any address:
         python etherscan_collect.py 0xYourAddress --types normal token --start-block 0 --end-block 99999999
  The script asks for your API key if it is not set as the ETHERSCAN_API_KEY environment variable.
"""

import argparse
import csv
import os
import sys
import time
from datetime import datetime, timezone

import requests

API_URL = "https://api.etherscan.io/v2/api"
CHAIN_ID = 1            # 1 = Ethereum mainnet
PAGE_SIZE = 1000        # Free tier returns at most 1,000 records per request
PAUSE_SECONDS = 0.5     # 2 calls per second: safely under the free-tier limit
DUST_THRESHOLD = 0.001  # amounts below this are flagged as likely spam

# Which Etherscan "action" belongs to each data type
ACTIONS = {
    "normal": "txlist",
    "internal": "txlistinternal",
    "token": "tokentx",
}

# --- Bybit case preset --------------------------------------------------------
BYBIT_PRESET = {
    "Bybit Exploiter 2": "0xA4B2Fd68593B6F34E51cB9eDB66E71c1B4Ab449e",
    "Bybit Exploiter 4": "0x1542368a03ad1f03d96D51B414f4738961Cf4443",
    "Bybit Exploiter 5": "0xdD90071D52F20e85c89802e5Dc1eC0A7B6475f92",
}
BYBIT_START_BLOCK = 21895300  # 21 Feb 2025, just before 14:41 UTC
BYBIT_END_BLOCK = 21901000    # 22 Feb 2025, after the 09:14 UTC cmETH burn

# --- FBI PSA I-022625-PSA (26 Feb 2025): 51 Ethereum addresses ----------------
FBI_LIST = {a.lower() for a in """
0x51E9d833Ecae4E8D9D8Be17300AEE6D3398C135D 0x96244D83DC15d36847C35209bBDc5bdDE9bEc3D8
0x83c7678492D623fb98834F0fbcb2E7b7f5Af8950 0x83Ef5E80faD88288F770152875Ab0bb16641a09E
0xAF620E6d32B1c67f3396EF5d2F7d7642Dc2e6CE9 0x3A21F4E6Bbe527D347ca7c157F4233c935779847
0xfa3FcCCB897079fD83bfBA690E7D47Eb402d6c49 0xFc926659Dd8808f6e3e0a8d61B20B871F3Fa6465
0xb172F7e99452446f18FF49A71bfEeCf0873003b4 0x6d46bd3AfF100f23C194e5312f93507978a6DC91
0xf0a16603289eAF35F64077Ba3681af41194a1c09 0x23Db729908137cb60852f2936D2b5c6De0e1c887
0x40e98FeEEbaD7Ddb0F0534Ccaa617427eA10187e 0x140c9Ab92347734641b1A7c124ffDeE58c20C3E3
0x684d4b58Dc32af786BF6D572A792fF7A883428B9 0xBC3e5e8C10897a81b63933348f53f2e052F89a7E
0x5Af75eAB6BEC227657fA3E749a8BFd55f02e4b1D 0xBCA02B395747D62626a65016F2e64A20bd254A39
0x4C198B3B5F3a4b1Aa706daC73D826c2B795ccd67 0xCd7eC020121Ead6f99855cbB972dF502dB5bC63a
0xbdE2Cc5375fa9E0383309A2cA31213f2D6cabcbd 0xD3C611AeD139107DEC2294032da3913BC26507fb
0xB72334cB9D0b614D30C4c60e2bd12fF5Ed03c305 0x8c7235e1A6EeF91b980D0FcA083347FBb7EE1806
0x1bb0970508316DC735329752a4581E0a4bAbc6B4 0x1eB27f136BFe7947f80d6ceE3Cf0bfDf92b45e57
0xCd1a4A457cA8b0931c3BF81Df3CFa227ADBdb6E9 0x09278b36863bE4cCd3d0c22d643E8062D7a11377
0x660BfcEa3A5FAF823e8f8bF57dd558db034dea1d 0xE9bc552fdFa54b30296d95F147e3e0280FF7f7e6
0x30a822CDD2782D2B2A12a08526452e885978FA1D 0xB4a862A81aBB2f952FcA4C6f5510962e18c7f1A2
0x0e8C1E2881F35Ef20343264862A242FB749d6b35 0x9271EDdda0F0f2bB7b1A0c712bdF8dbD0A38d1Ab
0xe69753Ddfbedbd249E703EB374452E78dae1ae49 0x2290937A4498C96eFfb87b8371a33D108F8D433f
0x959c4CA19c4532C97A657D82d97acCBAb70e6fb4 0x52207Ec7B1b43AA5DB116931a904371ae2C1619e
0x9eF42873Ae015AA3da0c4354AeF94a18D2B3407b 0x1542368a03ad1f03d96D51B414f4738961Cf4443
0x21032176B43d9f7E9410fB37290a78f4fEd6044C 0xA4B2Fd68593B6F34E51cB9eDB66E71c1B4Ab449e
0x55CCa2f5eB07907696afe4b9Db5102bcE5feB734 0xA5A023E052243b7cce34Cbd4ba20180e8Dea6Ad6
0xdD90071D52F20e85c89802e5Dc1eC0A7B6475f92 0x1512fcb09463A61862B73ec09B9b354aF1790268
0xF302572594a68aA8F951faE64ED3aE7DA41c72Be 0x723a7084028421994d4a7829108D63aB44658315
0xf03AfB1c6A11A7E370920ad42e6eE735dBedF0b1 0xEB0bAA3A556586192590CAD296b1e48dF62a8549
0xD5b58Cf7813c1eDC412367b97876bD400ea5c489
""".split()}

# Real token contracts in this case. Spam tokens often copy a real symbol
# (even "ETH"), so a token is identified by its CONTRACT, never by its symbol.
KNOWN_TOKENS = {
    "0xae7ab96520de3a18e5e111b5eaab095312d7fe84": "stETH (Lido)",
    "0xd5f7838f5c461feff7fe49ea5ebaf7728bb0adfa": "mETH (Mantle)",   # verify on Etherscan
    "0xe6829d9a7ee3040e1276fa75293bde931859e8fa": "cmETH (Mantle)",
}

OUTPUT_COLUMNS = [
    "wallet_label", "wallet", "type", "date_utc", "block", "tx_hash", "direction",
    "from", "to", "counterparty", "amount", "asset", "token_contract", "token_status", "method", "is_error",
    "dust_flag", "counterparty_in_fbi_list", "etherscan_link",
]


# ------------------------------------------------------------------------------
# 1. Talking to the API
# ------------------------------------------------------------------------------
def call_api(params, api_key, retries=3):
    """Send one request. Returns the list in 'result', or [] if there is nothing."""
    params = {**params, "chainid": CHAIN_ID, "apikey": api_key}
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(API_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as err:
            print(f"    network problem ({err}); retry {attempt}/{retries}")
            time.sleep(2 * attempt)
            continue

        if data.get("status") == "1":
            return data["result"]

        message = f"{data.get('message', '')} {data.get('result', '')}".strip()
        if "No transactions found" in message or "No records found" in message:
            return []
        if "rate limit" in message.lower():
            print(f"    rate limit hit; waiting before retry {attempt}/{retries}")
            time.sleep(5 * attempt)
            continue
        # Anything else (bad key, wrong parameter, paid-only endpoint): stop and say why
        sys.exit(f"Etherscan returned an error: {message}")

    sys.exit("Gave up after repeated failures. Check your internet connection and API key.")


def fetch_all(address, data_type, start_block, end_block, api_key):
    """Page through results 1,000 at a time until a page comes back short."""
    rows, page = [], 1
    while True:
        batch = call_api({
            "module": "account",
            "action": ACTIONS[data_type],
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "page": page,
            "offset": PAGE_SIZE,
            "sort": "asc",
        }, api_key)
        rows.extend(batch)
        print(f"    page {page}: {len(batch)} records")
        time.sleep(PAUSE_SECONDS)
        if len(batch) < PAGE_SIZE:
            return rows
        page += 1
        if page * PAGE_SIZE > 10000:
            # Etherscan won't page past 10,000 records for one query.
            print("    WARNING: over 10,000 records. Narrow the block range to get the rest.")
            return rows


# ------------------------------------------------------------------------------
# 2. Turning raw API records into readable rows
# ------------------------------------------------------------------------------
def to_units(raw_value, decimals):
    """Etherscan gives amounts as whole numbers of the smallest unit (e.g. wei)."""
    try:
        return int(raw_value) / (10 ** int(decimals))
    except (TypeError, ValueError):
        return 0.0


def tidy(record, wallet, label, data_type):
    wallet_lc = wallet.lower()
    sender = (record.get("from") or "").lower()
    receiver = (record.get("to") or record.get("contractAddress") or "").lower()

    if data_type == "token":
        amount = to_units(record.get("value"), record.get("tokenDecimal", 18))
        contract = (record.get("contractAddress") or "").lower()
        asset = KNOWN_TOKENS.get(contract, record.get("tokenSymbol") or "UNKNOWN")
        token_status = "real" if contract in KNOWN_TOKENS else "UNVERIFIED (likely spam)"
        receiver = (record.get("to") or "").lower()
    else:
        amount = to_units(record.get("value"), 18)
        contract, asset, token_status = "", "ETH (native)", "real"

    direction = "OUT" if sender == wallet_lc else "IN" if receiver == wallet_lc else "OTHER"
    counterparty = receiver if direction == "OUT" else sender
    tx_hash = record.get("hash", "")

    return {
        "wallet_label": label,
        "wallet": wallet,
        "type": data_type,
        "date_utc": datetime.fromtimestamp(int(record["timeStamp"]), tz=timezone.utc)
                            .strftime("%Y-%m-%d %H:%M:%S"),
        "block": record.get("blockNumber", ""),
        "tx_hash": tx_hash,
        "direction": direction,
        "from": sender,
        "to": receiver,
        "counterparty": counterparty,
        "amount": amount,
        "asset": asset,
        "token_contract": contract,
        "token_status": token_status,
        "method": record.get("functionName", "").split("(")[0],
        "is_error": record.get("isError", "0"),
        "dust_flag": "dust" if 0 < amount < DUST_THRESHOLD or amount == 0 else "",
        "counterparty_in_fbi_list": "Yes" if counterparty in FBI_LIST else "No",
        "etherscan_link": f"https://etherscan.io/tx/{tx_hash}",
    }


# ------------------------------------------------------------------------------
# 3. Saving and summarising
# ------------------------------------------------------------------------------
def save_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def print_summary(rows):
    """Total IN and OUT per wallet and asset: real assets only, no dust, no failed txs."""
    totals, spam = {}, set()
    for r in rows:
        if r["token_status"] != "real":
            spam.add(f'{r["asset"]} ({r["token_contract"][:10]}...)')
            continue
        if r["dust_flag"] or r["is_error"] == "1":
            continue
        key = (r["wallet_label"], r["asset"])
        totals.setdefault(key, {"IN": 0.0, "OUT": 0.0})
        if r["direction"] in ("IN", "OUT"):
            totals[key][r["direction"]] += r["amount"]

    print("\nSUMMARY (real assets only; dust and failed transactions excluded)")
    print(f"{'Wallet':<22}{'Asset':<16}{'IN':>16}{'OUT':>16}{'IN - OUT':>16}")
    for (label, asset), t in sorted(totals.items()):
        print(f"{label:<22}{asset:<16}{t['IN']:>16,.4f}{t['OUT']:>16,.4f}{t['IN'] - t['OUT']:>16,.4f}")
    if spam:
        print(f"\nExcluded {len(spam)} unverified tokens (see token_status column):")
        for name in sorted(spam):
            print(f"  {name}")


# ------------------------------------------------------------------------------
# 4. Command line
# ------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Collect Ethereum transactions via Etherscan.")
    parser.add_argument("addresses", nargs="*", help="Addresses to collect (default: Bybit preset)")
    parser.add_argument("--types", nargs="+", choices=list(ACTIONS), default=list(ACTIONS),
                        help="Which data to collect (default: all three)")
    parser.add_argument("--start-block", type=int, default=None)
    parser.add_argument("--end-block", type=int, default=None)
    parser.add_argument("--out-dir", default="etherscan_data")
    args = parser.parse_args()

    api_key = os.environ.get("ETHERSCAN_API_KEY") or input("Paste your Etherscan API key: ").strip()
    if not api_key:
        sys.exit("An API key is required.")

    if args.addresses:
        wallets = {f"Address {i + 1}": a for i, a in enumerate(args.addresses)}
        start = args.start_block if args.start_block is not None else 0
        end = args.end_block if args.end_block is not None else 99999999
    else:
        print("No address given: using the Bybit preset (Exploiters 2, 4, 5; 21-22 Feb 2025).")
        wallets = BYBIT_PRESET
        start = args.start_block if args.start_block is not None else BYBIT_START_BLOCK
        end = args.end_block if args.end_block is not None else BYBIT_END_BLOCK

    os.makedirs(args.out_dir, exist_ok=True)
    everything = []

    for label, address in wallets.items():
        for data_type in args.types:
            print(f"\n{label} ({address}): {data_type} transactions, blocks {start}-{end}")
            raw = fetch_all(address, data_type, start, end, api_key)
            rows = [tidy(r, address, label, data_type) for r in raw]
            filename = f"{label.replace(' ', '_')}_{data_type}.csv"
            save_csv(os.path.join(args.out_dir, filename), rows)
            print(f"    saved {len(rows)} rows -> {filename}")
            everything.extend(rows)

    everything.sort(key=lambda r: (r["date_utc"], r["tx_hash"]))
    save_csv(os.path.join(args.out_dir, "all_transactions.csv"), everything)
    print(f"\nSaved {len(everything)} rows in total -> {args.out_dir}/all_transactions.csv")
    print_summary(everything)


if __name__ == "__main__":
    main()
