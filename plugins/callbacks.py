from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from master import key as master_key
from master import buttom as master_buttom
from config import Config
import traceback

# Bridge plugin: connects inline button callbacks to compiled .so handlers
# master.buttom has: delete_batch, manage_batch, show_all_batches_buttom,
#   show_all_batches_buttom_delete, show_all_batches_buttom_manage, get_batch_statistics
# master.key has: handle_app_paid, appx_page_paid, gen_apps_paid_kb, gen_alpha_paid_kb


@Client.on_callback_query(filters.regex("^appxlist$"))
async def cb_appxlist(bot: Client, query: CallbackQuery):
    """ADD Batch button - shows batch list for adding"""
    try:
        await master_buttom.show_all_batches_buttom(bot, query)
    except Exception as e:
        print(f"Error in appxlist: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^delete_batch$"))
async def cb_delete_batch(bot: Client, query: CallbackQuery):
    """Delete Batch button"""
    try:
        await master_buttom.show_all_batches_buttom_delete(bot, query)
    except Exception as e:
        print(f"Error in delete_batch: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^manage_batch$"))
async def cb_manage_batch(bot: Client, query: CallbackQuery):
    """Manage Batch button"""
    try:
        await master_buttom.show_all_batches_buttom_manage(bot, query)
    except Exception as e:
        print(f"Error in manage_batch: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^show_batch$"))
async def cb_show_batch(bot: Client, query: CallbackQuery):
    """Show Batch button"""
    try:
        await master_buttom.get_batch_statistics(bot, query)
    except Exception as e:
        print(f"Error in show_batch: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^close$"))
async def cb_close(bot: Client, query: CallbackQuery):
    """Close button - deletes the message"""
    try:
        await query.message.delete()
    except Exception as e:
        await query.answer("⚠️ Could not close.", show_alert=True)


@Client.on_callback_query(filters.regex("^del_"))
async def cb_del_specific(bot: Client, query: CallbackQuery):
    """Handle specific batch deletion"""
    try:
        await master_buttom.delete_batch(bot, query)
    except Exception as e:
        print(f"Error in del_: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^manage_"))
async def cb_manage_specific(bot: Client, query: CallbackQuery):
    """Handle specific batch management"""
    try:
        await master_buttom.manage_batch(bot, query)
    except Exception as e:
        print(f"Error in manage_: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^batch_"))
async def cb_batch_action(bot: Client, query: CallbackQuery):
    """Handle batch-related callbacks"""
    try:
        await master_buttom.manage_batch(bot, query)
    except Exception as e:
        print(f"Error in batch_: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^app_paid"))
async def cb_app_paid(bot: Client, query: CallbackQuery):
    """Handle app paid callback"""
    try:
        await master_key.handle_app_paid(bot, query)
    except Exception as e:
        print(f"Error in app_paid: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^appx_"))
async def cb_appx_action(bot: Client, query: CallbackQuery):
    """Handle appx-related callbacks"""
    try:
        await master_key.appx_page_paid(bot, query)
    except Exception as e:
        print(f"Error in appx_: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^page_"))
async def cb_page_action(bot: Client, query: CallbackQuery):
    """Handle pagination callbacks"""
    try:
        await master_key.appx_page_paid(bot, query)
    except Exception as e:
        print(f"Error in page_: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^stats_"))
async def cb_stats(bot: Client, query: CallbackQuery):
    """Handle stats callbacks"""
    try:
        await master_buttom.get_batch_statistics(bot, query)
    except Exception as e:
        print(f"Error in stats_: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)
