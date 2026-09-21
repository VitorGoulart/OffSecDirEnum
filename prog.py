import httpx
from urllib.parse import urlparse, quote
from pathlib import Path
import argparse
from collections.abc import Iterator

TIMEOUT = httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0)

parser = argparse.ArgumentParser()
parser.add_argument("url", help="base URL to enumerate", type=str, action="store")
parser.add_argument("-w", "--wordlist", help="path to wordlist file", required=True, type=Path)
parser.add_argument("-x", "--extensions", help="list of extensions to append to each word", nargs="*",
                     type=str, action="store")

def iterate_wordlist(wordlist: Path, extensions: list[str] | None) -> Iterator[str]:
    with wordlist.open("r", encoding="utf-8") as file:
        for line in file:
            item = line.strip().lstrip("/")
            if not item or item.startswith("#"):
                continue

            yield item

            if extensions:
                for extension in extensions:
                    normalized_extension = extension.strip().lstrip(".")
                    if normalized_extension:
                        yield f"{item}.{normalized_extension}"


# Função verificar se a URL passada como parâmetro é válida
def validate_base_url(base_url: str) -> str:
    normalized_url = base_url.rstrip("/")
    parsed_url = urlparse(normalized_url)

    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ValueError("URL must start with http:// or https:// and include a host")

    return normalized_url


# Função para iterar sobre os diretórios e arquivos da wordlist e fazer as requisições HTTP
def process_paths(
    client: httpx.Client,
    base_url: str,
    paths: Iterator[str],
) -> None:
    for path in paths:
        encoded_path = quote(path, safe="/")
        full_url = f"{base_url}/{encoded_path}"

        try:
            response = client.get(full_url)
            if response.status_code != httpx.codes.NOT_FOUND:
                print(f"[{response.status_code}] {full_url}")
        except httpx.TimeoutException:
            print(f"[TIMEOUT] {full_url}")
        except httpx.RequestError as error:
            print(f"[ERROR] {full_url}: {error}")


def main():
    args = parser.parse_args()
    try:
        base_url = validate_base_url(args.url)
    except ValueError as error:
        parser.error(str(error))

    wordlist = args.wordlist
    extensions = args.extensions

    if not wordlist.is_file():
        parser.error(f"wordlist file not found: {wordlist}")

    paths = iterate_wordlist(wordlist, extensions)

    with httpx.Client(
        timeout=TIMEOUT,
        follow_redirects=False,
    ) as client:
        process_paths(client, base_url, paths)

if __name__ == "__main__":
    main()
