# Tracing a Slice of the Bybit Hack Funds: An Open-Source Investigation

*Author: Linda Gicheru · Date: [17th November 2026] · Status: [Final]*

> Open-source research using only public blockchain data and published reports.
> Attribution of the attackers relies on official sources; fund movements were verified on-chain by the author.

---

## 1. Summary
[3–4 sentences: what happened, what you traced, your main finding.]

On 21 February 2025, approximately $1.5B in ETH and liquid-staked ETH tokens was taken from a Bybit Ethereum cold wallet. The FBI attributed the theft to North Korea's "TraderTraitor" group. This report traces 2-3 hops from the receiving address `0x47666Fab8bd0Ac7003bce3f5C3585383F09486E2` across over 10 wallets. The findings include the fact that software engineering mechanisms were used to execute the attack that actually happened off-chain.

## 2. Scope
- **Traced:** receiving address → 0x0fa09C3A328792253f8dee7116848723b72a6d2e, 0x0fa09C3A328792253f8dee7116848723b72a6d2e, [2–3] hops each
- **Asset(s) followed:** [ETH only / ETH + stETH]
- **Not traced:** Bitcoin side after bridging, other chains, the remaining split wallets, the attack mechanism itself

## 3. Methodology
- **Tools:** Etherscan, MetaSleuth, Google Sheets
- **Address selection:** largest outflows
- **Verification:** each hop checked against the FBI PSA address list
- **Source rating:** primary/official (the FBI, Bybit)> expert firms (Signia reports, Safe Wallet report) > AI (RAG)
- **Excluded:** inbound dust and spam tokens sent to the exploiter address

## 4. Findings
![Exploiter 1 to 2](fig1_exploiter1_to_2.png)
*Figure 1. Stolen stETH and mETH moved from Exploiter 1 to Exploiter 2, 21 Feb 2025 (UTC).*

![Exploiter 2 to 5](fig2_exploiter2_to_5.png)
*Figure 2. Swap proceeds (~98,049 ETH) consolidated into Exploiter 5.*

![Exploiter 5 fan-out](fig3_exploiter5_fanout.png)
*Figure 3. Exploiter 5 splits 90,000 ETH into nine wallets of 10,000 ETH within 48 seconds.*

![Largest swap](fig4_largest_swap.png)
*Figure 4. Largest single swap: 25,000 stETH to ETH via ParaSwap.*

![cmETH burn](fig5_cmeth_burn.png)
*Figure 5. 15,000 cmETH burned to the null address, 22 Feb 2025 09:14:47 UTC.*

*Representative edges shown; full hop log in [bybit_trace.csv](bybit_trace.csv). Built in MetaSleuth; times in UTC.*

| Hop | From | To | Asset | Amount | Time (UTC) | What happened |
|---|---|---|---|---|---|---|
| 1 | | | | | | |

**Patterns observed:**
- **Splitting:** [ ]
- **Speed:** [ ]
- **Conversion:** [ ]
- **Exchange touchpoints:** [ ]

## 5. Attribution assessment
| Claim | Who says it | Supported by my trace? | Confidence |
|---|---|---|---|
| North Korea (TraderTraitor) responsible | FBI; Mandiant | Partly. Laundering pattern only; identity relies on FBI | High (official) |
| | | | |

## 6. Risk assessment: what an exchange or bank should do
- Screen deposits against the FBI-listed addresses and their downstream clusters
- Monitor inflows that originate from bridge routers shortly after major hacks
- Red flags: [e.g. round-number tranches, rapid multi-hop movement, fresh wallets]

## 7. Limitations
- Small test transfers that were attributed as possible test runs ahead of the attack.
- Onward movement to bridges to Bitcoin

## 8. Sources
1. FBI, *North Korea Responsible for $1.5 Billion Bybit Hack*, PSA I-022625-PSA, 26 Feb 2025. https://www.ic3.gov/PSA/2025/PSA250226


## Appendix
- Full transaction log: [`bybit_trace.csv`](bybit_trace.csv)
