"""Rate-limit-aware helpers for PubMed E-utilities and Crossref (public APIs).
Used for literature search and citation verification. No data is invented:
every record returned comes from the remote API response."""
import json, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET

UA = {"User-Agent": "lit-research/1.0"}

def get(url, tries=6, base_sleep=1.5):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except Exception as e:
            last = e
            time.sleep(base_sleep * (2 ** k))
    raise RuntimeError(f"GET failed after {tries} tries: {url} ({last})")

def pubmed_search(term, retmax=100, sort="relevance"):
    q = urllib.parse.urlencode({"db": "pubmed", "term": term, "retmax": retmax,
                                "retmode": "json", "sort": sort})
    r = json.loads(get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + q))
    time.sleep(0.5)
    return int(r["esearchresult"]["count"]), r["esearchresult"]["idlist"]

def pubmed_fetch(ids):
    out = []
    for i in range(0, len(ids), 80):
        chunk = ids[i:i + 80]
        x = ET.fromstring(get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=" + ",".join(chunk)))
        time.sleep(0.6)
        for a in x.findall(".//PubmedArticle"):
            rec = {"pmid": a.findtext(".//PMID"), "title": "".join(a.find(".//ArticleTitle").itertext()) if a.find(".//ArticleTitle") is not None else "",
                   "journal": a.findtext(".//Journal/ISOAbbreviation"),
                   "year": a.findtext(".//PubDate/Year") or (a.findtext(".//PubDate/MedlineDate") or "")[:4],
                   "doi": None, "abstract_sections": [], "abstract": ""}
            # Only the article's own IDs (PubmedData/ArticleIdList), NOT IDs inside the reference list.
            own = a.find("PubmedData/ArticleIdList")
            if own is not None:
                for aid in own.findall("ArticleId"):
                    if aid.get("IdType") == "doi":
                        rec["doi"] = aid.text
            if rec["doi"] is None:
                for el in a.findall("MedlineCitation/Article/ELocationID"):
                    if el.get("EIdType") == "doi":
                        rec["doi"] = el.text
            parts = []
            for e in a.findall(".//Abstract/AbstractText"):
                lab = e.get("Label")
                rec["abstract_sections"].append(lab)
                parts.append((lab + ": " if lab else "") + "".join(e.itertext()))
            rec["abstract"] = " ".join(parts)
            au = a.findall(".//AuthorList/Author")
            rec["authors"] = [((x.findtext("LastName") or x.findtext("CollectiveName") or "") + " " + (x.findtext("Initials") or "")).strip() for x in au]
            out.append(rec)
    return out

def crossref_doi(doi):
    d = json.loads(get("https://api.crossref.org/works/" + urllib.parse.quote(doi)))
    time.sleep(0.3)
    return d["message"]

def crossref_search(query, rows=20, filt=None):
    params = {"query.bibliographic": query, "rows": rows}
    if filt:
        params["filter"] = filt
    d = json.loads(get("https://api.crossref.org/works?" + urllib.parse.urlencode(params)))
    time.sleep(0.3)
    return d["message"]["items"]
