Tracing a Slice of the Bybit Hack Funds: An Open-Source Investigation

Author: Linda Gicheru · Date: 19 November 2026 · Status: Final

Open-source research using only public blockchain data and published reports. Attribution of the attackers relies on official and expert sources; fund movements were verified on-chain by the author.

1. Summary

On 21 February 2025, approximately $1.5B in ETH and liquid-staked ETH tokens was taken from a Bybit Ethereum cold wallet; the FBI attributed the theft to North Korea's "TraderTraitor" group [1]. Starting from the receiving address, I traced up to three hops across more than 10 wallets. The funds followed a fast, structured laundering pattern: staked-ETH tokens were moved to a second wallet and swapped to ETH through DEX aggregators (the largest single swap was 25,000 stETH via ParaSwap), proceeds of ~98,049 ETH were consolidated, and 90,000 ETH was then split into nine wallets of exactly 10,000 ETH within 48 seconds. These round, rapid tranches are typical preparation for onward bridging.

2. Scope
Wallets traced (labels as shown on Etherscan/MetaSleuth):
Exploiter 1 (receiving address): 0x47666Fab8bd0Ac7003bce3f5C3585383F09486E2
Exploiter 2: 0x0fa09C3A328792253f8dee7116848723b72a6d2e
Exploiter 5: ADD FULL ADDRESS
Nine 10,000 ETH fan-out wallets: listed in bybit_trace.csv
Assets followed: ETH, stETH, mETH, cmETH
Depth: up to three hops from the receiving address
Not traced: the off-chain compromise itself, the remaining split wallets, activity after bridging (including the Bitcoin side), and other chains.

3. Methodology
Tools: Etherscan (transactions, internal transactions, token transfers), MetaSleuth (flow visualisation), Google Sheets (hop log)
Starting point: receiving address taken from the FBI PSA [1] and confirmed on Etherscan by its label and activity on 21 February 2025
Address selection: largest outflows first; wallets showing repeated patterns were sampled rather than all traced
Source rating: primary/official sources (FBI, Bybit) ranked above expert reports (Sygnia, Safe, Mandiant, analytics firms), which rank above independent investigators on social media. Claims were confirmed on-chain wherever possible
Excluded: inbound dust, spam tokens and messages sent to the exploiter address

4. Background: how the theft happened (from published reports, not traced)

According to the Safe and Sygnia investigations [3][4], the compromise began off-chain: a Safe{Wallet} developer's machine was compromised in early February 2025, giving the attackers access to Safe's cloud environment, where they altered the web interface used by Bybit's signers. When the signers approved what appeared to be a routine transaction on 21 February 2025, they in fact approved a change to the cold wallet's contract logic via a delegatecall. On-chain, this appears as an Exec Transaction at 14:13 UTC, followed by Sweep ETH and Sweep ERC20 calls (14:15–14:16 UTC) that emptied the wallet to the attacker. Because the funds moved inside contract calls, they appear in Etherscan's internal transactions and token transfers rather than as normal transfers.


5. Findings

5.1 Preparation. Transactions consistent with test runs are visible from the address 0x19C6876E978D9F128147439ac4cd9EA2582cd141 as early as 18 February 2025, three days before the theft [7].

5.2 Staked tokens moved and swapped. Stolen stETH and mETH were moved from Exploiter 1 to Exploiter 2 on 21 February 2025 and swapped to ETH through DEX aggregators. The largest single swap converted 25,000 stETH to ETH via ParaSwap. Some swaps began before all stolen funds had been received, showing a pre-planned process.

Exploiter 1 to 2 Figure 1. Stolen stETH and mETH moved from Exploiter 1 to Exploiter 2, 21 Feb 2025 (UTC).

Largest swap Figure 2. Largest single swap: 25,000 stETH to ETH via ParaSwap.

5.3 Consolidation. Swap proceeds of approximately 98,049 ETH were consolidated into Exploiter 5.

Exploiter 2 to 5 Figure 3. Swap proceeds (~98,049 ETH) consolidated into Exploiter 5.

5.4 Structured fan-out. Exploiter 5 split 90,000 ETH into nine wallets of exactly 10,000 ETH each within 48 seconds.

Exploiter 5 fan-out Figure 4. Exploiter 5 splits 90,000 ETH into nine wallets of 10,000 ETH within 48 seconds.

5.5 cmETH. 15,000 cmETH was sent to the null address on 22 February 2025 at 09:14:47 UTC. The reason for this transfer is not confirmed in this analysis.

cmETH to null address Figure 5. 15,000 cmETH sent to the null address, 22 Feb 2025 09:14:47 UTC.

Patterns observed

Speed: swaps began before all stolen funds had arrived; fan-out completed within seconds
Conversion: liquid-staked tokens rapidly swapped to ETH through DEX aggregators
Consolidation followed by fan-out into round-number tranches
Fresh, single-purpose wallets at each stage

Representative edges shown; full hop log in bybit_trace.csv. Flow diagrams built in MetaSleuth; times in UTC.

## 6. Attribution assessment

| Claim | Who says it | Supported by my trace? | Confidence |
|---|---|---|---|
| North Korea (TraderTraitor) responsible | FBI [1]; Mandiant tracks the group as UNC4899 [5] | Partly: laundering pattern is consistent; identity relies on official attribution | High (official) |
| ~$1.5B stolen from a Bybit cold wallet | Bybit; FBI [1] | Yes: theft transactions observed 21 Feb 2025, 14:13–14:16 UTC | High |
| Compromise via a manipulated Safe{Wallet} interface | Safe [4]; Sygnia [3] | No: off-chain, outside the scope of on-chain tracing | Medium–High (expert reports) |
| Funds split into round tranches for laundering | This analysis | Yes: 90,000 ETH split into nine 10,000 ETH wallets in 48 seconds | High (verified on-chain) |
| Funds later bridged to Bitcoin | Analytics firms and investigators [2][6][8] | Not traced in this slice | Medium (secondary sources) |

7. Risk assessment: what an exchange or bank should do
Screen deposits against the FBI-listed addresses and their downstream wallets
Monitor inflows from bridge routers and DEX aggregators shortly after major hacks
Red flags: round-number tranches (e.g. exactly 10,000 ETH), splitting within seconds, rapid swaps of liquid-staked tokens into ETH, consolidation followed by fan-out, and fresh single-purpose wallets
Third-party risk: wallet and custody providers' off-chain infrastructure (developer machines, cloud environments, web interfaces) should be part of an exchange's vendor risk assessment

9. Risk assessment: what an exchange or bank should do
Screen deposits against the FBI-listed addresses and their downstream wallets
Monitor inflows from bridge routers and DEX aggregators shortly after major hacks
Red flags: round-number tranches (e.g. exactly 10,000 ETH), splitting within seconds, rapid swaps of liquid-staked tokens into ETH, consolidation followed by fan-out, and fresh single-purpose wallets
Third-party risk: wallet and custody providers' off-chain infrastructure (developer machines, cloud environments, web interfaces) should be part of an exchange's vendor risk assessment

10. Limitations
Only a sample of the split wallets was traced; the remaining wallets were not followed.
The trace stops before bridging; the Bitcoin side was not analysed.
Wallet labels (Exploiter 1, 2, 5) come from Etherscan/MetaSleuth and were not independently verified.
The description of the off-chain compromise relies entirely on published reports.
USD values are approximate, based on prices at the time of the hack.

11. Sources
FBI, North Korea Responsible for $1.5 Billion Bybit Hack, PSA I-022625-PSA, 26 Feb 2025. https://www.ic3.gov/PSA/2025/PSA250226
Inca Digital, Bybit analysis. https://drive.google.com/file/d/1f6ue8r6f1nfHiZHECrQBtLoMNVfcEqMg/view
Sygnia, Bybit investigation. https://www.sygnia.co/blog/sygnia-investigation-bybit-hack/
Safe, incident report. https://x.com/safe/article/1897663514975649938
Mandiant, reporting on UNC4899. ADD LINK
ZachXBT on X. https://x.com/zachxbt/status/1893211577836302365
Etherscan, test-run transactions. https://etherscan.io/txs?a=0x19C6876E978D9F128147439ac4cd9EA2582cd141
Arkham Intelligence on X. https://x.com/arkham/status/1893033424224411885
Breadcrumbs, The Bybit Hack: How $1.46 Billion in Crypto Was Stolen. https://learn.breadcrumbs.app/posts/the-bybit-hack-how-1-46-billion-in-crypto-was-stolen-a-breakdown-of-the-largest-crypto-heist

Appendix
Full transaction log: bybit_trace.csv









