from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup
from master import key as master_key
from master import buttom as master_buttom
from config import Config
import json
import traceback

# Bridge plugin: connects inline button callbacks to compiled .so handlers
#
# master.buttom signatures:
#   show_all_batches_buttom(user_id) -> returns keyboard markup
#   show_all_batches_buttom_delete(user_id) -> returns keyboard markup
#   show_all_batches_buttom_manage(user_id) -> returns keyboard markup
#   delete_batch(bot, user_id, course_id)
#   manage_batch(bot, m, course_id)
#   get_batch_statistics(bot, user_id, course_id)
#
# master.key signatures:
#   handle_app_paid(bot, data, call_msg, a)
#   appx_page_paid(call_msg, letter, page)
#   gen_alpha_paid_kb() -> returns keyboard
#   gen_apps_paid_kb(letter, page, apps_per_page)


@Client.on_callback_query(filters.regex("^appxlist$"))
async def cb_appxlist(bot: Client, query: CallbackQuery):
    """ADD Batch button - shows all batches for selection"""
    try:
        user_id = query.from_user.id
        result = await master_buttom.show_all_batches_buttom(user_id)
        if result:
            if isinstance(result, InlineKeyboardMarkup):
                await query.message.edit_reply_markup(reply_markup=result)
            else:
                await query.message.edit_text(str(result))
        else:
            await query.answer("No batches found.", show_alert=True)
    except Exception as e:
        print(f"Error in appxlist: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^delete_batch$"))
async def cb_delete_batch(bot: Client, query: CallbackQuery):
    """Delete Batch button - shows batches for deletion"""
    try:
        user_id = query.from_user.id
        result = await master_buttom.show_all_batches_buttom_delete(user_id)
        if result:
            if isinstance(result, InlineKeyboardMarkup):
                await query.message.edit_reply_markup(reply_markup=result)
            else:
                await query.message.edit_text(str(result))
        else:
            await query.answer("No batches found.", show_alert=True)
    except Exception as e:
        print(f"Error in delete_batch: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^manage_batch$"))
async def cb_manage_batch(bot: Client, query: CallbackQuery):
    """Manage Batch button - shows batches for management"""
    try:
        user_id = query.from_user.id
        result = await master_buttom.show_all_batches_buttom_manage(user_id)
        if result:
            if isinstance(result, InlineKeyboardMarkup):
                await query.message.edit_reply_markup(reply_markup=result)
            else:
                await query.message.edit_text(str(result))
        else:
            await query.answer("No batches found.", show_alert=True)
    except Exception as e:
        print(f"Error in manage_batch: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^show_batch$"))
async def cb_show_batch(bot: Client, query: CallbackQuery):
    """Show Batch button - shows batch statistics"""
    try:
        user_id = query.from_user.id
        result = await master_buttom.show_all_batches_buttom(user_id)
        if result:
            if isinstance(result, InlineKeyboardMarkup):
                await query.message.edit_reply_markup(reply_markup=result)
            else:
                await query.message.edit_text(str(result))
        else:
            await query.answer("No batches found.", show_alert=True)
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
    """Handle specific batch deletion - del_<course_id>"""
    try:
        user_id = query.from_user.id
        course_id = query.data.replace("del_", "")
        await master_buttom.delete_batch(bot, user_id, course_id)
    except Exception as e:
        print(f"Error in del_: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^manage_(?!batch$)"))
async def cb_manage_specific(bot: Client, query: CallbackQuery):
    """Handle specific batch management - manage_<course_id>"""
    try:
        course_id = query.data.replace("manage_", "")
        await master_buttom.manage_batch(bot, query.message, course_id)
    except Exception as e:
        print(f"Error in manage_specific: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^batch_"))
async def cb_batch_action(bot: Client, query: CallbackQuery):
    """Handle batch-related callbacks - batch_<course_id>"""
    try:
        course_id = query.data.replace("batch_", "")
        await master_buttom.manage_batch(bot, query.message, course_id)
    except Exception as e:
        print(f"Error in batch_: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^stats_"))
async def cb_stats(bot: Client, query: CallbackQuery):
    """Handle stats callbacks - stats_<course_id>"""
    try:
        user_id = query.from_user.id
        course_id = query.data.replace("stats_", "")
        await master_buttom.get_batch_statistics(bot, user_id, course_id)
    except Exception as e:
        print(f"Error in stats_: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^app_paid"))
async def cb_app_paid(bot: Client, query: CallbackQuery):
    """Handle app paid callback - app_paid data contains JSON"""
    try:
        data = query.data
        # Try to parse JSON from callback data
        try:
            parsed = json.loads(data.replace("app_paid", "").strip())
        except:
            parsed = data
        await master_key.handle_app_paid(bot, parsed, query.message, query)
    except Exception as e:
        print(f"Error in app_paid: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^appx_"))
async def cb_appx_action(bot: Client, query: CallbackQuery):
    """Handle appx page callbacks - appx_<letter>_<page>"""
    try:
        parts = query.data.split("_")
        letter = parts[1] if len(parts) > 1 else ""
        page = int(parts[2]) if len(parts) > 2 else 0
        await master_key.appx_page_paid(query.message, letter, page)
    except Exception as e:
        print(f"Error in appx_: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^page_"))
async def cb_page_action(bot: Client, query: CallbackQuery):
    """Handle pagination callbacks - page_<letter>_<page>"""
    try:
        parts = query.data.split("_")
        letter = parts[1] if len(parts) > 1 else ""
        page = int(parts[2]) if len(parts) > 2 else 0
        await master_key.appx_page_paid(query.message, letter, page)
    except Exception as e:
        print(f"Error in page_: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("^alpha_"))
async def cb_alpha_action(bot: Client, query: CallbackQuery):
    """Handle alphabet selection callbacks"""
    try:
        parts = query.data.split("_")
        letter = parts[1] if len(parts) > 1 else ""
        page = int(parts[2]) if len(parts) > 2 else 0
        await master_key.appx_page_paid(query.message, letter, page)
    except Exception as e:
        print(f"Error in alpha_: {e}")
        traceback.print_exc()
        await query.answer(f"⚠️ Error: {e}", show_alert=True)
