import inspect

import telegram.constants
from telegram import Update
from telegram.ext import ContextTypes

from . import api
from .api import ApiException
from .helper import escape_markdown
from .logger import create_logger


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log = create_logger(inspect.currentframe().f_code.co_name)


async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log = create_logger(inspect.currentframe().f_code.co_name)
    if not any(a for a in context.args):
        log.error("no argument has been passed to `/add`")
        return await update.effective_message.reply_text("...")

    name = " ".join(context.args)
    item_base = api.models.ItemBase.parse_obj({
        "name": name,
        "description": "",
    })
    try:
        item = api.create_item(item_base)
        message = f"Added {str(item)}"
    except ApiException as e:
        message = str(e)

    return await update.effective_message.reply_text(message, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)


async def items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log = create_logger(inspect.currentframe().f_code.co_name)
    try:
        # noinspection PyShadowingNames
        items = api.get_items()
        message = "\n".join([escape_markdown(item.name) for item in items.data])
    except ApiException as e:
        log.exception("failed to retrieve items", exc_info=True)
        message = str(e)

    return await update.effective_message.reply_text(message, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
