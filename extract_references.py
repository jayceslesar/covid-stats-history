from refextract import extract_references_from_file, extract_references_from_url


def get_refs(fp) -> list:
    return extract_references_from_file(fp)


def get_refs_web(url) -> list:
    return extract_references_from_url(url)


print(get_refs_web("https://www.medrxiv.org/content/10.1101/2020.05.21.20108621v1.full.pdf"))