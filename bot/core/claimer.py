import asyncio
from time import time, strftime, localtime
from urllib.parse import quote, unquote
from typing import Any, Dict, List

import aiohttp, random, math, hashlib, hmac
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
		self.user_id = None
		self.api_url = 'https://api.mmbump.pro/v1'
		self.errors = 0

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
					if self.user_id is None:
						user = await self.tg_client.get_me()
						self.user_id = user.id
						self.http_client.headers["user_auth"] = str(self.user_id)
						headers["user_auth"] = str(self.user_id)
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

	async def login(self, init_data: str) -> str:
		url = self.api_url + '/loginJwt'
		try:
			await self.http_client.options(url)
			json_data = {"initData": init_data}
			response = await self.http_client.post(url, json=json_data)
			response.raise_for_status()
			response_json = await response.json()
			token = response_json.get('access_token', '')
			return token
		except Exception as error:
			logger.error(f"{self.session_name} | Unknown error when log in: {error}")
			self.errors += 1
			await asyncio.sleep(delay=3)
			return False

	async def refresh_token(self) -> str | bool:
		url = self.api_url + '/auth/refresh'
		try:
			await self.http_client.options(url)
			response = await self.http_client.post(url)
			response.raise_for_status()
			response_json = await response.json()
			self.access_token = response_json.get('access', '')
			return True if self.access_token != '' else False
		except Exception as error:
			logger.error(f"{self.session_name} | Unknown error when Refresh auth tokens: {error}")
			await asyncio.sleep(delay=3)
			return False

	async def get_profile(self) -> Dict[str, Any]:
		url = self.api_url + '/farming'
		try:
			await self.http_client.options(url)
			response = await self.http_client.post(url)
			response.raise_for_status()
			response_json = await response.json()
			return response_json
		except Exception as error:
			logger.error(f"{self.session_name} | Unknown error when getting Profile Data: {error}")
			self.errors += 1
			await asyncio.sleep(delay=3)
			return {}

	async def daily_grant(self) -> bool:
		url = self.api_url + '/grant-day/claim'
		url_reset = self.api_url + '/grant-day/reset'
		try:
			json_data = {}
			data_list = []
			json_data["hash"] = await self.create_hash(data_list)
			await self.http_client.options(url, json=json_data)
			response = await self.http_client.post(url)
			#response.raise_for_status()
			if response.status == 400:
				await self.http_client.options(url_reset)
				await self.http_client.post(url_reset)
				await asyncio.sleep(delay=2)
				json_data["hash"] = await self.create_hash(data_list)
				response = await self.http_client.post(url)
			response_json = await response.json()
			balance = response_json.get('balance', False)
			if balance is not False:
				self.balance = int(balance)
				return True
			else: return False
		except Exception as error:
			logger.error(f"{self.session_name} | Unknown error when getting daily grant: {error}")
			self.errors += 1
			await asyncio.sleep(delay=3)
			return False

	async def friends_claim(self) -> bool:
		url_friends = self.api_url + '/friends'
		url_claim = self.api_url + '/friends/claim'
		try:
			json_data = {}
			data_list = []
			json_data["hash"] = await self.create_hash(data_list)
			await self.http_client.options(url_friends, json=json_data)
			response = await self.http_client.post(url)
			response.raise_for_status()
			response_json = await response.json()
			friend_claim = response_json.get('friend_claim', 0)
			if friend_claim > 0:
				logger.info(f"{self.session_name} | Friends reward available")
				json_data["hash"] = await self.create_hash(data_list)
				await self.http_client.options(url_claim, json=json_data)
				response = await self.http_client.post(url)
				response.raise_for_status()
				response_json = await response.json()
				balance = response_json.get('balance', False)
				if balance is not False:
					logger.success(f"{self.session_name} | Friends reward claimed")
					self.balance = int(balance)
					self.errors = 0
					return True
				else: return False
			else: return False
		except Exception as error:
			logger.error(f"{self.session_name} | Unknown error when claiming friends reward: {error}")
			self.errors += 1
			await asyncio.sleep(delay=3)
			return False

	async def send_claim(self, taps: int) -> bool:
		url = self.api_url + '/farming/finish'
		try:
			json_data = {"tapCount":taps}
			data_list = [json_data]
			json_data["hash"] = await self.create_hash(data_list)
			await self.http_client.options(url)
			response = await self.http_client.post(url, json=json_data)
			response.raise_for_status()
			response_json = await response.json()
			balance = response_json.get('balance', False)
			if balance is not False:
				self.balance = int(balance)
				return True
			else: return False
		except Exception as error:
			logger.error(f"{self.session_name} | Unknown error when Claiming: {error}")
			self.errors += 1
			await asyncio.sleep(delay=3)
			return False
			
	async def start_farming(self) -> bool:
		url = self.api_url + '/farming/start'
		await asyncio.sleep(delay=6)
		try:
			json_data = {"status":"inProgress"}
			data_list = [json_data]
			json_data["hash"] = await self.create_hash(data_list)
			await self.http_client.options(url)
			response = await self.http_client.post(url, json=json_data)
			response.raise_for_status()
			response_json = await response.json()
			status = response_json.get('status', False)
			if status is False: return False
			else: return True
		except Exception as error:
			logger.error(f"{self.session_name} | Unknown error when Start Farming: {error}")
			self.errors += 1
			await asyncio.sleep(delay=3)
			return False

	async def perform_tasks(self) -> None:
		url = self.api_url + '/task-list'
		try:
			json_data = {}
			data_list = []
			json_data["hash"] = await self.create_hash(data_list)
			await self.http_client.options(url)
			response = await self.http_client.post(url, json=json_data)
			response.raise_for_status()
			response_json = await response.json()
			completed = 0
			for task in response_json:
				if completed == 2: break # perform a maximum of 2 tasks in a row
				if task['type'] == 'tonkeeper_wallet': continue # ignore task with connecting Tonkeeper wallet
				if 'telegram' in task['type'] or 'telegram' in task['name'].lower():
					continue # ignore all Telegram tasks (they are verified on the server side)
				if task['status'] == 'possible':
					logger.info(f"{self.session_name} | Try to perform task {task['id']}")
					await asyncio.sleep(random.randint(4, 8))
					json_data2 = {"id":task['id']}
					data_list2 = [json_data2]
					json_data2['hash'] = await self.create_hash(data_list2)
					response2 = await self.http_client.post(f"{url}/complete", json=json_data2)
					response2.raise_for_status()
					response_json2 = await response2.json()
					status = response_json2.get('task', {}).get('status', False)
					if status == 'granted':
						logger.success(f"{self.session_name} | Task {task['id']} completed. Reward claimed.")
						await asyncio.sleep(random.randint(2, 4))
						completed += 1
						self.errors = 0
					else:
						logger.info(f"{self.session_name} | Failed to perform task {task['id']}")
		except Exception as error:
			logger.error(f"{self.session_name} | Unknown error while Performing tasks: {error}")
			self.errors += 1
			await asyncio.sleep(delay=3)
	
	async def check_proxy(self, proxy: Proxy) -> None:
		try:
			response = await self.http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
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
	
	async def create_hash(self, data_list: List[Dict[str, Any]], secret_key: str = 'super-key') -> str:
		params = []
		for item in data_list:
			for key, value in item.items():
				params.append(f"{key}={quote(str(value))}")
		
		time_param = f"time={math.ceil(time() / 60)}"
		if params:
			complete_str = '&'.join(params + [time_param])
		else:
			complete_str = time_param
		hashed = hmac.new(secret_key.encode(), complete_str.encode(), hashlib.sha256)
		return hashed.hexdigest()

	async def run(self, proxy: str | None) -> None:
		access_token_created_time = 0
		proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

		async with aiohttp.ClientSession(headers=headers, connector=proxy_conn) as http_client:
			self.http_client = http_client
			if proxy:
				await self.check_proxy(proxy=proxy)
			
			self.authorized = False
			while True:
				if self.errors >= settings.ERRORS_BEFORE_STOP:
					logger.error(f"{self.session_name} | Too many errors. Bot stopped.")
					break
				try:
					if not self.authorized:
						tg_web_data = await self.get_tg_web_data(proxy=proxy)
						access_token = await self.login(init_data=tg_web_data)
						if access_token is not False:
							self.authorized = True
							self.access_token = access_token
							self.http_client.headers['Authorization'] = 'Bearer ' + access_token
							headers['Authorization'] = 'Bearer ' + access_token
							access_token_created_time = time()
						else: continue
					
					if time() - access_token_created_time >= 3600:
						self.authorized = False
						continue
						#refresh_success = await self.refresh_token()
						#if refresh_success:
						#	self.http_client.headers['Authorization'] = 'Bearer ' + self.access_token
						#	headers['Authorization'] = 'Bearer ' + self.access_token
						#	access_token_created_time = time()
						#else:
						#	self.authorized = False
						#	continue

					profile = await self.get_profile()
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
						start_time = session['start_at']
						
					# Log current balance
					logger.info(f"{self.session_name} | Balance: {self.balance}")

					daily_grant_awail, daily_grant_wait = await self.check_daily_grant(start_time=day_grant_first, cur_time=system_time, day=day_grant_day)
					if daily_grant_awail:
						if await self.daily_grant():
							logger.success(f"{self.session_name} | Daily grant claimed.")
							self.errors = 0
							continue
					
					await self.friends_claim()
					await self.perform_tasks()
					
					# Log current balance
					logger.info(f"{self.session_name} | Balance: {self.balance}")
						
					if status == 'await':
						logger.info(f"{self.session_name} | Farm not active. Starting farming.")
						if await self.start_farming():
							logger.success(f"{self.session_name} | Farming started successfully.")
							self.errors = 0
						continue
					else:
						time_elapsed = system_time - start_time
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
								continue
						
						logger.info(f"{self.session_name} | Time to claim and restart farming.")
						taps = await self.calculate_taps(farm=farm, boost=boost)
						if await self.send_claim(taps=taps):
							logger.success(f"{self.session_name} | Claim successful.")
							self.errors = 0
						if await self.start_farming():
							logger.success(f"{self.session_name} | Farming restarted successfully.")
							self.errors = 0

					# Log current balance
					logger.info(f"{self.session_name} | Balance: {self.balance}")
					
				except InvalidSession as error:
					raise error
				except Exception as error:
					logger.error(f"{self.session_name} | Unknown error: {error}")
					self.errors += 1
					await asyncio.sleep(delay=3)
				else:
					logger.info(f"Sleep 1 min")
					await asyncio.sleep(delay=60)

async def run_claimer(tg_client: Client, proxy: str | None):
	try:
		await Claimer(tg_client=tg_client).run(proxy=proxy)
	except InvalidSession:
		logger.error(f"{tg_client.name} | Invalid Session")
