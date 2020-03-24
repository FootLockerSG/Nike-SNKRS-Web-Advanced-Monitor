from discord_webhook import DiscordWebhook, DiscordEmbed
from proxymanager import ProxyManager
from threading import Thread
from datetime import datetime
from collections import OrderedDict
import time, requests, ujson, logging, os
requests.models.json = ujson
from mods.logger import Logger
log = Logger()

def nike_web(code1, code2, main_webhook_1, sleep, keywords):

    from random_user_agent.user_agent import UserAgent
    from random_user_agent.params import SoftwareName, OperatingSystem

    url = f"https://api.nike.com/product_feed/threads/v2/?filter=marketplace%28{code1}%29&filter=language%28{code2}%29&filter=channelId%28d9a5bc42-4b9c-4976-858a-f159cf99c647%29"
    proxy_manager = ProxyManager('proxies.txt')
    main_webhook = main_webhook_1
    sserver_logs = "server log webhook"

    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

    items = []

    def monitor():

        try:

            headers = {
                'upgrade-insecure-requests' : '1',
                'cache-control' : 'no-cache',
                'Pragma' : 'no-cache',
                'user-agent' : user_agent_rotator.get_random_user_agent(),
                'accept' : 'application/xhtml+xml,text/html,application/xml;q=0.9,image/apng,image/webp,*/*;q=0.8,application/signed-exchange;v=b3',
                'sec-fetch-site' : 'none',
                'accept-encoding' : 'gzip, deflate, br',
                'accept-language' : 'en-US,en;q=0.9'
            }

            session = requests.Session()
            session.headers = OrderedDict(headers)

            proxydict = proxy_manager.next_proxy()
            proxies = proxydict.get_dict()
            r = session.get(url = url, proxies = proxies)
            data = r.json()['objects']
            for x in data:
                id = x['id']
                items.append(id)

            log.warning(f"{len(items)} products loaded on site")
            log.info(f'Initialized Nike {code1} Web Monitor')

        except Exception as e:
            log.error(str(e))


    def monitor():

        while True:
            try:

                proxydict = proxy_manager.next_proxy()
                proxies = proxydict.get_dict()

                headers = {
                    'upgrade-insecure-requests' : '1',
                    'cache-control' : 'no-cache',
                    'Pragma' : 'no-cache',
                    'user-agent' : user_agent_rotator.get_random_user_agent(),
                    'sec-fetch-mode' : 'navigate',
                    'sec-fetch-user' : '?1',
                    'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                    'sec-fetch-site' : 'none',
                    'accept-encoding' : 'gzip, deflate, br',
                    'accept-language' : 'en-US,en;q=0.9'
                }

                session.headers = OrderedDict(headers)
                r = session.get(url = url, proxies = proxies)
                data = r.json()['objects']

                for x in data:
                    id = x['id']
                    if id not in items:
                        title = x['productInfo'][0]['productContent']['fullTitle']
                        link = f"https://www.nike.com/{code1.lower()}/t/{x['publishedContent']['properties']['seo']['slug']}"
                        image_url = x['productInfo'][0]['imageUrls']['productImageUrl']
                        price = x['productInfo'][0]['merchPrice']['currentPrice']
                        currency = x['productInfo'][0]['merchPrice']['currency']

                        sizes = []
                        stock_level = []
                        for y in x['productInfo'][0]['skus']:
                            sizes.append(y['nikeSize'])

                        for y in x['productInfo'][0]['availableSkus']:
                            stock_level.append(y['level'])

                        final = ""
                        for i in range(len(sizes)):
                            final = final + sizes[i] + f" - [{stock_level[i]}]" +"\n"

                        webhook = DiscordWebhook(url=main_webhook)
                        embed = DiscordEmbed(title= f"Nike {code1} Web [BACKEND]", description = f"[{title}]({link})", color=0xFF7F50)
                        embed.set_thumbnail(url= image_url)
                        embed.add_embed_field(name="Price", value = f"${str(price)} {currency}", inline=True) #Need to check api to determine
                        embed.add_embed_field(name="Possible Sizes InStock", value = final, inline=True)
                        embed.add_embed_field(name="Useful links: ", value = f"[Cart](https://secure-store.nike.com/{code1.lower()}/checkout/html/cart.jsp) | [Region Switch](https://www.nike.com/?geoselection=true) | [Shopback](https://www.shopback.sg) | [BuyAndShip](https://www.buyandship.com.sg/)", inline=False)
                        embed.set_footer(text = f'DogeSolutions • {time.strftime("%H:%M:%S", time.localtime())} SGT', icon_url='https://pbs.twimg.com/profile_images/1128853846753546240/CB8smmAP_400x400.jpg')
                        webhook.add_embed(embed)
                        webhook.execute()

                        items.append(id)
                        log.info(f"Item sent to discord! - [{code1}]")

                        log.warning("Checking for KWs")
                        hit = ""
                        for i in keywords:
                            if i in title.lower():
                                hit = hit + i + "\n"

                        if hit != "" :
                            webhook = DiscordWebhook(url = main_webhook, content = f'@everyone Keyword detected!```{hit}```')
                            webhook.execute()
                            log.info("Keyword hit!")
                        else:
                            log.warning("No keywords detected")

                time.sleep(sleep_time)
                log.warning(f'Scraping Nike Web - [{code1}]')

            except Exception as e:
                log.error(str(e))

if(__name__ == "__main__"):

    def read_from_txt(path):

        raw_lines = []
        lines = []
        f = open(path, "r")
        raw_lines = f.readlines()
        f.close()

        for line in raw_lines:
            lines.append(line.strip("\n"))

        return lines

    f = read_from_txt('nike_webhooks.txt')
    total_webhooks = len(f)
    log.info(f"{str(total_webhooks)} webhooks loaded.")
    for i in range(len(f)):
        log.warning(f[i])

    ##### Must match accordingly #####
    country_codes = ['SG', 'AU', 'CN', 'JP', 'TW', 'CA', 'US', 'GB']
    country_codes_2 = ['en-GB', 'en-GB', 'zh-Hans', 'ja', 'zh-hant', 'en-GB', 'en', 'en-GB']
    positive_keywords = ["jordan", "sacai", "fear", "mars", "landing", "dunk"]
    negative_keywords = ['shirt', 't-shirt', 'short', 'sock', 'cap', 'singlet', 'tee', 'leggings']
    ##### Must match accordingly #####

    for i in range(len(f)):
        code1 = country_codes[i]
        code2 = country_codes_2[i]
        main_webhook_1 = f[i]
        sleep = 10

        t = Thread(target=nike_web, args=(code1, code2, main_webhook_1, sleep, positive_keywords,))
        t.start()
