import asyncio
from time import time, strftime, localtime
from urllib.parse import unquote
from typing import Any, Dict

import aiohttp, random
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered
from pyrogram.raw.functions.messages import RequestWebView

from bot.config import settings
from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers

class Claimer:
	def __init__(self, tg_client: Client):
		self.session_name = tg_client.name
		self.tg_client = tg_client

	async def get_tg_web_data(self, proxy: str | None) -> str:
		if proxy:
			proxy = Proxy.from_str(proxy)
			proxy_dict = dict(
				scheme=proxy.protocol,
				hostname=proxy.host,
				port=proxy.port,
				username=proxy.login,
				password=proxy.password
			)
		else:
			proxy_dict = None

		self.tg_client.proxy = proxy_dict

		try:
			if not self.tg_client.is_connected:
				try:
					await self.tg_client.connect()
				except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
					raise InvalidSession(self.session_name)
			web_view = await self.tg_client.invoke(RequestWebView(
				peer=await self.tg_client.resolve_peer('MMproBump_bot'),
				bot=await self.tg_client.resolve_peer('MMproBump_bot'),
				platform='android',
				from_bot_menu=False,
				url='https://api.mmbump.pro/'
			))
			auth_url = web_view.url
			tg_web_data = unquote(
				string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0])
			if self.tg_client.is_connected:
				await self.tg_client.disconnect()

			return tg_web_data

		except InvalidSession as error:
			raise error

		except Exception as error:
			logger.error(f"{self.session_name} | Unknown error during Authorization: {error}")
			await asyncio.sleep(delay=3)

	async def login(self, http_client: aiohttp.ClientSession, init_data: str) -> str:
		url = 'https://api.mmbump.pro/v1/login'
		try:
			await http_client.options(url)
			json_data = {"initData": init_data}
			response = await http_client.post(url, json=json_data)
			response.raise_for_status()
			response_json = await response.json()
			token = response_json.get('token', '')
			return token
		except Exception as error:
			logger.error(f"{self.session_name} | Unknown error when log in: {error}")
			await asyncio.sleep(delay=3)

	async def get_profile(self, http_client: aiohttp.ClientSession) -> Dict[str, Any]:
		url = 'https://api.mmbump.pro/v1/farming'
		try:
			await http_client.options(url)
			response = await http_client.get(url)
			response.raise_for_status()
			response_json = await response.json()
			return response_json
		except Exception as error:
			logger.error(f"{self.session_name} | Unknown error when getting Profile Data: {error}")
			await asyncio.sleep(delay=3)
			return {}

	async def day_grant(self, http_client: aiohttp.ClientSession) -> bool:
		url = 'https://api.mmbump.pro/v1/grant-day/claim'
		try:
			await http_client.options(url)
			response = await http_client.post(url)
			response.raise_for_status()
			response_json = await response.json()
			balance = response_json.get('balance', False)
			if balance is not False:
				self.balance = int(balance)
				return True
			else: return False
		except Exception as error:
			logger.error(f"{self.session_name} | Unknown error when getting daily grant: {error}")
			await asyncio.sleep(delay=3)
			return False

	async def send_claim(self, http_client: aiohttp.ClientSession, taps: int) -> bool:
		url = 'https://api.mmbump.pro/v1/farming/finish'
		try:
			await http_client.options(url)
			response = await http_client.post(url, json={"tapCount":taps})
			response.raise_for_status()
			response_json = await response.json()
			balance = response_json.get('balance', False)
			if balance is not False:
				self.balance = int(balance)
				return True
			else: return False
		except Exception as error:
			logger.error(f"{self.session_name} | Unknown error when Claiming: {error}")
			await asyncio.sleep(delay=3)
			return False
			
	async def start_farming(self, http_client: aiohttp.ClientSession) -> bool:
		url = 'https://api.mmbump.pro/v1/farming/start'
		await asyncio.sleep(delay=6)
		try:
			await http_client.options(url)
			response = await http_client.post(url, json={"status":"inProgress"})
			response.raise_for_status()
			response_json = await response.json()
			status = response_json.get('status', False)
			if status is False: return False
			else: return True
		except Exception as error:
			logger.error(f"{self.session_name} | Unknown error when Start Farming: {error}")
			await asyncio.sleep(delay=3)
			return False

	async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
		try:
			response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
			ip = (await response.json()).get('origin')
			logger.info(f"{self.session_name} | Proxy IP: {ip}")
		except Exception as error:
			logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

	async def check_daily_grant(self, start_time: int | None, cur_time: int, day: int | None) -> tuple[bool, int]:
		if start_time is None and day is None:
			logger.info(f"{self.session_name} | First daily grant available")
			return True, 0
		
		seconds = cur_time - start_time
		days = seconds / 86400
		if days > day:
			logger.info(f"{self.session_name} | Daily grant available")
			return True, 0
		else:
			next_grant_time = start_time + (day * 86400)
			time_to_wait = next_grant_time - cur_time
			logger.info(f"{self.session_name} | Next daily grant: {strftime('%Y-%m-%d %H:%M:%S', localtime(next_grant_time))}")
			return False, time_to_wait
			
	async def calculate_taps(self, farm: int, boost: int | bool) -> int:
		if isinstance(boost, int) and boost > 0:
			full_farm = farm * boost
		else:
			full_farm = farm
		
		perc = random.randint(100, 200)
		taps = int(full_farm * (perc / 100))
		return taps

	async def run(self, proxy: str | None) -> None:
		access_token_created_time = 0
		proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

		async with aiohttp.ClientSession(headers=headers, connector=proxy_conn) as http_client:
			if proxy:
				await self.check_proxy(http_client=http_client, proxy=proxy)

			while True:
				try:
					if time() - access_token_created_time >= 3600:
						tg_web_data = await self.get_tg_web_data(proxy=proxy)
						token = await self.login(http_client=http_client, init_data=tg_web_data)
						http_client.headers["Authorization"] = token
						headers["Authorization"] = token
						access_token_created_time = time()

					profile = await self.get_profile(http_client=http_client)
					info = profile['info']
					farm = info['farm']
					boost = info.get('boost', False)
					if boost: boost = int(boost[1:])
					system_time = profile['system_time']
					self.balance = profile['balance']
					day_grant_first = profile.get('day_grant_first', None)
					day_grant_day = profile.get('day_grant_day', None)
					session = profile['session']
					status = session['status']
					if status == 'inProgress':
						moon_time = session['moon_time']
						
					# Log current balance
					logger.info(f"{self.session_name} | Balance: {self.balance}")

					daily_grant_awail, daily_grant_wait = await self.check_daily_grant(start_time=day_grant_first, cur_time=system_time, day=day_grant_day)
					if daily_grant_awail:
						if await self.day_grant(http_client=http_client):
							logger.success(f"{self.session_name} | Daily grant claimed.")
						continue
						
					if status == 'await':
						logger.info(f"{self.session_name} | Farm not active. Starting farming.")
						if await self.start_farming(http_client=http_client):
							logger.success(f"{self.session_name} | Farming started successfully.")
						continue
					else:
						time_elapsed = system_time - moon_time
						claim_wait = (6 * 3600) - time_elapsed
						if claim_wait > 0:
							if daily_grant_wait > 0 and daily_grant_wait < claim_wait:
								hours = daily_grant_wait // 3600
								minutes = (daily_grant_wait % 3600) // 60
								logger.info(f"{self.session_name} | Farming active. Waiting for {hours} hours and {minutes} minutes before claiming daily grant.")
								await asyncio.sleep(daily_grant_wait)
								continue
							else:
								hours = claim_wait // 3600
								minutes = (claim_wait % 3600) // 60
								logger.info(f"{self.session_name} | Farming active. Waiting for {hours} hours and {minutes} minutes before claiming and restarting.")
								await asyncio.sleep(claim_wait)
						
						logger.info(f"{self.session_name} | Time to claim and restart farming.")
						taps = await self.calculate_taps(farm=farm, boost=boost)
						if await self.send_claim(http_client=http_client, taps=taps):
							logger.success(f"{self.session_name} | Claim successful.")
						if await self.start_farming(http_client=http_client):
							logger.success(f"{self.session_name} | Farming restarted successfully.")

					# Log current balance
					logger.info(f"{self.session_name} | Balance: {self.balance}")
					
				except InvalidSession as error:
					raise error
				except Exception as error:
					logger.error(f"{self.session_name} | Unknown error: {error}")
					await asyncio.sleep(delay=3)
				else:
					logger.info(f"Sleep 1 min")
					await asyncio.sleep(delay=60)

async def run_claimer(tg_client: Client, proxy: str | None):
	try:
		await Claimer(tg_client=tg_client).run(proxy=proxy)
	except InvalidSession:
		logger.error(f"{tg_client.name} | Invalid Session")
