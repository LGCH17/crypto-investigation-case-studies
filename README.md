# Tracing a Slice of the Bybit Hack Funds: An Open-Source Investigation

*Author: Linda Gicheru · Date: 17th November 2026 · Status: Final

> Open-source research using only public blockchain data and published reports.
> Attribution of the attackers relies on official sources; fund movements were verified on-chain by the author.

---

## 1. Summary

On 21 February 2025, approximately $1.5B in ETH and liquid-staked ETH tokens was taken from a Bybit Ethereum cold wallet; the FBI attributed the theft to North Korea's "TraderTraitor" group. Starting from the receiving address, I traced 2–3 hops across more than 10 wallets. The funds followed a fast, structured laundering pattern: staked-ETH tokens were moved to a second wallet and swapped to ETH through DEX aggregators (the largest single swap was 25,000 stETH via ParaSwap), proceeds of ~98,049 ETH were consolidated, and 90,000 ETH was then split into nine wallets of exactly 10,000 ETH within 48 seconds. These round, rapid tranches are typical preparation for onward bridging.

## 2. Scope
- **Traced:** receiving address → 0x0fa09C3A328792253f8dee7116848723b72a6d2e, [2–3] hops each
- **Asset(s) followed:** ETH only / ETH + stETH
- **Not traced:** Other chains, the remaining split wallets

## 3. Methodology
- **Tools:** Etherscan, MetaSleuth, Google Sheets, AI
- **Address selection:** largest outflows
- **Verification:** each hop checked against the FBI PSA address list
- **Source rating:** primary/official (the FBI, Bybit)> expert firms (Signia reports, Safe Wallet report, Breadcrumbs, Arkham on X,  ) 
- **Excluded:** inbound dust and spam tokens sent to the exploiter address

## 4. Findings
From my viewpoint, the attackers are well versed in software engineering and blockchain mechanisms. They started operations well before the attack, i've documented as far back as 2025-02-18 but the operations had started earlier. The North Korean (DPRK) attribution arose from SlowMist's reporting on February 23, 2026 upon their following the digital footprint of UNC4899.
This was an infrastructure issue where the attacker had a clear picture of the entire architecture (from Online to On-chain)- right from cloud (hosting) to the structure of Ethereum smart contracts. They knew that, the Web App & Cloud Infrastructure of Gnosis Safe were vulnerable.
The root action of the breach took place entirely in the traditional, online web stack not on-chain: they breached a developer’s macOS (took over the machine as an "insider", on February 04, 2026 and used it to takeover Safe's AWS cloud environment (off-chain i.e. online). They overwrote previous code and executed DELEGATECALL (from the Standard Call) on the brain of the proxy of Gnosis Safe multisig cold wallet system belonging to Bybit. They placed a spoof contract that guided to which address the funds should go upon signing by Bybit, where they implanted their own, replacing Bybit Hot Wallet address. The first target was to happen on 21-02-2026, 1413hrs UTC.
The traced transactions herein are four, and each is followed out more than 3-hops. The laundering operations took less than an hour starting with some swaps that happened even before all the funds had been received, within 48-seconds splits of 90,000 ETH each were Transferred. At least 15,000 cmETH was burned to the null address, on 22 Feb 2025.
My findings consider that although the crypto industry may lack standardized security standards and third-party risk assessments, leading to severe vulnerabilities, as seen in this and other crypto heists, the strength lies in bridging the gap on information flow between online and on-chain mechanisms.

Exploiter 1 to 2(fig1_exploiter1_to_2.png)
*Figure 1. Stolen stETH and mETH moved from Exploiter 1 to Exploiter 2, 21 Feb 2025 (UTC).*

Exploiter 2 to 5(fig2_exploiter2_to_5.png)
*Figure 2. Swap proceeds (~98,049 ETH) consolidated into Exploiter 5.*

Exploiter 5 fan-out(fig3_exploiter5_fanout.png)
*Figure 3. Exploiter 5 splits 90,000 ETH into nine wallets of 10,000 ETH within 48 seconds.*

!Largest swap(fig4_largest_swap.png)
*Figure 4. Largest single swap: 25,000 stETH to ETH via ParaSwap.*

cmETH burn(fig5_cmeth_burn.png)
*Figure 5. 15,000 cmETH burned to the null address, 22 Feb 2025 09:14:47 UTC.*

*Representative edges shown; full hop log in bybit_trace.csv(bybit_trace.csv). Built in MetaSleuth; times in UTC.*

## 5. Attribution assessment
| Claim | Who says it | Supported by my trace? | Confidence |
| North Korea (TraderTraitor) responsible | FBI; Mandiant | Partly. Laundering pattern only; identity relies on FBI | High (official) |


## 6. Risk assessment: what an exchange or bank should do
- Screen deposits against the FBI-listed addresses and their downstream clusters
- Monitor inflows that originate from bridge routers shortly after major hacks
- Red flags: e.g. round-number tranches, rapid multi-hop movement, fresh wallets

## 7. Limitations
- Small test transfers that were attributed as possible test runs ahead of the attack.
- Onward movement to bridges to Bitcoin

## 8. Sources
1. FBI, *North Korea Responsible for $1.5 Billion Bybit Hack*, PSA I-022625-PSA, 26 Feb 2025. https://www.ic3.gov/PSA/2025/PSA250226
2. Inca Digital, https://drive.google.com/file/d/1f6ue8r6f1nfHiZHECrQBtLoMNVfcEqMg/view
3. Sygnia, https://www.sygnia.co/blog/sygnia-investigation-bybit-hack/
4. Safe, https://x.com/safe/article/1897663514975649938
5. ZachXBT on X, https://x.com/zachxbt/status/1893211577836302365?s=19
6. Arkham Intelligence, https://x.com/arkham/status/1893033424224411885?s=19
7. Etherscan, "Test runs started on 2025-02-18, https://etherscan.io/txs?a=0x19C6876E978D9F128147439ac4cd9EA2582cd141
8. Metasleuth, https://metasleuth.io/system/workspace/personal/charts
9. Breadcrumbs, https://learn.breadcrumbs.app/posts/the-bybit-hack-how-1-46-billion-in-crypto-was-stolen-a-breakdown-of-the-largest-crypto-heist
10. AI, https://gemini.google.com/app/efd1b5104519beb2?utm_source=app_launcher&utm_medium=owned&utm_campaign=base_all


## Appendix
- Full transaction log:`bybit_trace.csv`(bybit_trace.csv)
