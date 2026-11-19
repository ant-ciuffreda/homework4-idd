import statistics, time
from ricerca import cerca

query = []
with open("test/query_test.txt", encoding="utf-8") as f:
    for riga in f:
        if riga.strip():
            parti = [p.strip() or None for p in riga.split("|")] + [None] * 3
            query.append(parti[:4])

for testo, cat, da, a in query:          # giro a vuoto, non misurato
    cerca(testo, 1, cat, da, a)

tempi = []
for _ in range(5):
    for testo, cat, da, a in query:
        t0 = time.perf_counter()
        cerca(testo, 1, cat, da, a)
        tempi.append((time.perf_counter() - t0) * 1000)

print(f"Ricerche misurate: {len(tempi)}")
print(f"Tempo medio: {statistics.mean(tempi):.1f} ms ± {statistics.stdev(tempi):.1f} ms")
print(f"Mediana: {statistics.median(tempi):.1f} ms | massimo: {max(tempi):.1f} ms")