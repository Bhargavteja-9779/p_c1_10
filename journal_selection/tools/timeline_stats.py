"""Empirical submission-to-acceptance measurement for candidate journals.

Sources (both public, no fabrication possible):
  * Crossref REST API 'assertion' fields (received/accepted) deposited by
    Springer Nature, Wiley, Taylor & Francis, IET, ACM.
  * PubMed E-utilities article history dates (PubStatus=received/accepted)
    for MEDLINE/PMC-indexed journals (OUP, Elsevier biomedical, IEEE some).
Output: one JSON line per journal with n, median, mean, IQR, share <=60/<=100 days.
Caveat: only *accepted* articles are observable; 'received' may be the date of a
resubmission at some journals. Statistics describe published articles only.
"""
import sys, json, time, re, statistics, urllib.request, urllib.parse
from datetime import datetime
import xml.etree.ElementTree as ET

UA = {"User-Agent": "journal-timeline-research/1.0"}

def get(url, tries=4):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:
            time.sleep(2 * (k + 1))
    raise RuntimeError(f"failed {url}")

def parse_date(s):
    s = s.strip()
    for fmt in ("%d %B %Y", "%Y-%m-%d", "%B %d, %Y", "%d %b %Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None

def summarize(name, days, source, extra=None):
    days = sorted(d for d in days if d is not None and 0 <= d <= 2000)
    out = {"journal": name, "source": source, "n": len(days)}
    if days:
        q = statistics.quantiles(days, n=4) if len(days) >= 4 else [None, None, None]
        out.update({
            "median_days": statistics.median(days),
            "mean_days": round(statistics.mean(days), 1),
            "q1_days": q[0], "q3_days": q[2],
            "share_le_60": round(sum(d <= 60 for d in days) / len(days), 3),
            "share_le_100": round(sum(d <= 100 for d in days) / len(days), 3),
        })
    if extra:
        out.update(extra)
    return out

def crossref(name, issn, since="2025-11-01", rows=300):
    url = (f"https://api.crossref.org/journals/{issn}/works?rows={rows}"
           f"&filter=type:journal-article,from-pub-date:{since}"
           f"&select=DOI,title,assertion,type")
    d = json.loads(get(url))
    days, n_items = [], 0
    for it in d["message"]["items"]:
        n_items += 1
        title = (it.get("title") or [""])[0].lower()
        if re.search(r"\b(review|survey|editorial|erratum|correction|retraction)\b", title):
            continue
        rec = acc = None
        for a in it.get("assertion", []) or []:
            if a.get("name") == "received":
                rec = parse_date(a.get("value", ""))
            elif a.get("name") == "accepted":
                acc = parse_date(a.get("value", ""))
        if rec and acc:
            days.append((acc - rec).days)
    return summarize(name, days, f"Crossref assertions, pub>={since}", {"items_scanned": n_items})

def pubmed(name, ta, since="2025/11/01", until="2026/11/15", retmax=300):
    term = f'"{ta}"[ta] AND ("{since}"[dp] : "{until}"[dp]) AND journal article[pt] NOT review[pt]'
    q = urllib.parse.urlencode({"db": "pubmed", "term": term, "retmax": retmax, "retmode": "json"})
    ids = json.loads(get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + q))["esearchresult"]["idlist"]
    days = []
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        x = get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=" + ",".join(chunk))
        root = ET.fromstring(x)
        for art in root.findall(".//PubmedArticle"):
            h = {}
            for p in art.findall(".//History/PubMedPubDate"):
                st = p.get("PubStatus")
                try:
                    h[st] = datetime(int(p.findtext("Year")), int(p.findtext("Month")), int(p.findtext("Day")))
                except Exception:
                    pass
            if "received" in h and "accepted" in h:
                days.append((h["accepted"] - h["received"]).days)
        time.sleep(0.4)
    return summarize(name, days, f"PubMed history, dp {since}-{until}", {"pmids_found": len(ids)})

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    for j in spec:
        try:
            if j["src"] == "crossref":
                r = crossref(j["name"], j["issn"])
            else:
                r = pubmed(j["name"], j["ta"])
        except Exception as e:
            r = {"journal": j["name"], "error": str(e)}
        print(json.dumps(r), flush=True)
        time.sleep(1.0)
