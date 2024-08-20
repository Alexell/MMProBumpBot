import os
import glob
import asyncio
import argparse
import random
from itertools import cycle
from pathlib import Path

from pyrogram import Client
from better_proxy import Proxy

from bot.config import settings
from bot.utils import logger
from bot.core.claimer import run_claimer
from bot.core.registrator import register_sessions


start_text = """


███    ███ ███    ███ ██████  ██████   ██████      ██████  ██    ██ ███    ███ ██████  
████  ████ ████  ████ ██   ██ ██   ██ ██    ██     ██   ██ ██    ██ ████  ████ ██   ██ 
██ ████ ██ ██ ████ ██ ██████  ██████  ██    ██     ██████  ██    ██ ██ ████ ██ ██████  
██  ██  ██ ██  ██  ██ ██      ██   ██ ██    ██     ██   ██ ██    ██ ██  ██  ██ ██      
██      ██ ██      ██ ██      ██   ██  ██████      ██████   ██████  ██      ██ ██      
                                                                                       

Select an action:

    1. Create session
    2. Run bot
"""


def get_session_names() -> list[str]:
	session_path = Path('sessions')
	session_files = session_path.glob('*.session')
	session_names = sorted([file.stem for file in session_files])
	return session_names

def get_proxies() -> list[Proxy]:
	if settings.USE_PROXY_FROM_FILE:
		with open(file='bot/config/proxies.txt', encoding='utf-8-sig') as file:
			proxies = sorted([Proxy.from_str(proxy=row.strip()).as_url for row in file if row.strip()])
	else:
		proxies = []

	return proxies

async def get_tg_clients() -> list[Client]:
	session_names = get_session_names()

	if not session_names:
		raise FileNotFoundError("Not found session files")

	tg_clients = [Client(
		name=session_name,
		api_id=settings.API_ID,
		api_hash=settings.API_HASH,
		workdir='sessions/',
		plugins=dict(root='bot/plugins')
	) for session_name in session_names]

	return tg_clients

async def run_bot_with_delay(tg_client, proxy, delay):
	if delay > 0:
		log.info(f"{tg_client.name} | Wait {delay} seconds before start")
		await asyncio.sleep(delay)
	await run_claimer(tg_client=tg_client, proxy=proxy)

async def run_clients(tg_clients: list[Client]):
	proxies = get_proxies()
	proxies_cycle = cycle(proxies) if proxies else cycle([None])
	tasks = []
	delay = 0
	for index, tg_client in enumerate(tg_clients):
		if index > 0:
			delay = random.randint(*settings.SLEEP_BETWEEN_START)
		proxy = next(proxies_cycle)
		task = asyncio.create_task(run_bot_with_delay(tg_client=tg_client, proxy=proxy, delay=delay))
		tasks.append(task)
	await asyncio.gather(*tasks)

async def process() -> None:
	if not settings:
		logger.warning(f"Please fix the above errors in the .env file")
		return
	parser = argparse.ArgumentParser()
	parser.add_argument('-a', '--action', type=int, help='Action to perform')

	logger.info(f"Detected {len(get_session_names())} sessions | {len(get_proxies())} proxies")

	action = parser.parse_args().action

	if not action:
		print(start_text)

		while True:
			action = input("> ")

			if not action.isdigit():
				logger.warning("Action must be number")
			elif action not in ['1', '2']:
				logger.warning("Action must be 1 or 2")
			else:
				action = int(action)
				break

	if action == 1:
		await register_sessions()
	elif action == 2:
		tg_clients = await get_tg_clients()

		await run_clients(tg_clients=tg_clients)