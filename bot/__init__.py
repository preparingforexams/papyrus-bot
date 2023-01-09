import inspect

import telegram.constants
from telegram import Update
from telegram.ext import ContextTypes

from . import api
from .api import ApiException
from .helper import escape_markdown
from .logger import create_logger


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


async def add_batch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log = create_logger(inspect.currentframe().f_code.co_name)
    if not any(a for a in context.args):
        log.error("no argument has been passed to `/addbatch`")
        return await update.effective_message.reply_text("...")

    text = " ".join(context.args)
    batch_items = [name.strip() for name in text.split(";")]

    messages = []
    for name in batch_items:
        item_base = api.models.ItemBase.parse_obj({
            "name": name,
            "description": "",
        })
        try:
            item = api.create_item(item_base)
            messages.append(f"Added {str(item)}")
        except ApiException as e:
            messages.append(str(e))

    message = "\n".join(messages)
    return await update.effective_message.reply_text(message, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)


async def items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log = create_logger(inspect.currentframe().f_code.co_name)
    try:
        # noinspection PyShadowingNames
        items = api.get_items()
        message = "\n".join([escape_markdown(item.name) for item in items.data if not item.done])
    except ApiException as e:
        log.exception("failed to retrieve items", exc_info=True)
        message = str(e)

    return await update.effective_message.reply_text(message, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log = create_logger(inspect.currentframe().f_code.co_name)
    if not any(a for a in context.args):
        log.error("no argument has been passed to `/done`")
        return await update.effective_message.reply_text("...")
    name = " ".join(context.args)

    try:
        item = api.find_item_by_name(name)
        if not item:
            message = f"couldn't find item named `{name}`"
        else:
            api.mark_as_done(item)
            message = f"marked `{name}` as done"
    except ApiException as e:
        log.exception("failed to retrieve items or marking item as done", exc_info=True)
        message = str(e)

    return await update.effective_message.reply_text(message, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)


def add_chat(update: Update) -> Optional[str]:
    log = create_logger(inspect.currentframe().f_code.co_name)
    title = update.effective_message.new_chat_title or update.effective_chat.title or update.effective_chat.first_name

    chat = api.models.ChatBase.parse_obj({
        "id": update.effective_chat.id,
        "name": title,
    })

    try:
        # noinspection PyShadowingNames
        api.create_chat(chat)
    except ApiException as e:
        log.exception("failed to retrieve items", exc_info=True)
        return str(e)
    except requests.exceptions.ConnectionError as e:
        return escape_markdown(str(e))[:4000]


async def chat_created(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if message := add_chat(update):
        return await update.effective_message.reply_text(message, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)


async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if message := add_chat(update):
        return await update.effective_message.reply_text(message, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if message := add_chat(update):
        return await update.effective_message.reply_text(message, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
