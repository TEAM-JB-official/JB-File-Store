from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    buttons = [
        [InlineKeyboardButton("📁 Store File", callback_data="store_file")],
        [InlineKeyboardButton("🔗 My Links", callback_data="my_links")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton("👤 User Panel", callback_data="user_panel")],
        [InlineKeyboardButton("💰 Premium", callback_data="premium")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ]
    return InlineKeyboardMarkup(buttons)

def admin_panel():
    buttons = [
        [InlineKeyboardButton("📊 Stats", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton("🚫 Ban/Unban", callback_data="admin_ban")],
        [InlineKeyboardButton("⭐ Premium Management", callback_data="admin_premium")],
        [InlineKeyboardButton("🔧 Settings", callback_data="admin_settings")],
        [InlineKeyboardButton("💾 Backup", callback_data="admin_backup")],
        [InlineKeyboardButton("🤖 Clone Management", callback_data="admin_clones")]
    ]
    return InlineKeyboardMarkup(buttons)

def clone_panel(clones_list):
    buttons = []
    for clone in clones_list:
        status = "✅" if clone["is_active"] else "❌"
        buttons.append([InlineKeyboardButton(f"{status} {clone['bot_username']}", callback_data=f"clone_{clone['clone_id']}")])
    buttons.append([InlineKeyboardButton("➕ Create New Clone", callback_data="create_clone")])
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)

def settings_keyboard(clone_id="main"):
    buttons = [
        [InlineKeyboardButton("🔗 Link Shortener", callback_data=f"set_link_shortener_{clone_id}")],
        [InlineKeyboardButton("🎫 Token Verification", callback_data=f"set_token_verification_{clone_id}")],
        [InlineKeyboardButton("📢 Force Subscribe", callback_data=f"set_force_subscribe_{clone_id}")],
        [InlineKeyboardButton("🖼️ Custom Caption", callback_data=f"set_custom_caption_{clone_id}")],
        [InlineKeyboardButton("🔘 Custom Buttons", callback_data=f"set_custom_buttons_{clone_id}")],
        [InlineKeyboardButton("⏰ Auto Delete", callback_data=f"set_auto_delete_{clone_id}")],
        [InlineKeyboardButton("🛡️ Protect Content", callback_data=f"set_protect_content_{clone_id}")],
        [InlineKeyboardButton("🔒 File Forward Lock", callback_data=f"set_file_forward_lock_{clone_id}")],
        [InlineKeyboardButton("🚫 Disable Save Media", callback_data=f"set_disable_save_media_{clone_id}")],
        [InlineKeyboardButton("🔁 Disable Forward Media", callback_data=f"set_disable_forward_media_{clone_id}")],
        [InlineKeyboardButton("💬 Custom Start Message", callback_data=f"set_custom_start_msg_{clone_id}")],
        [InlineKeyboardButton("ℹ️ Custom About Message", callback_data=f"set_custom_about_msg_{clone_id}")],
        [InlineKeyboardButton("🖼️ Custom Thumbnail", callback_data=f"set_thumbnail_{clone_id}")],
        [InlineKeyboardButton("📸 Custom Welcome Photo", callback_data=f"set_welcome_photo_{clone_id}")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_settings")]
    ]
    return InlineKeyboardMarkup(buttons)

def file_buttons(file_id, has_password=False, is_one_time=False):
    buttons = []
    if has_password:
        buttons.append([InlineKeyboardButton("🔐 Unlock with Password", callback_data=f"unlock_{file_id}")])
    else:
        buttons.append([InlineKeyboardButton("📥 Get File", callback_data=f"get_file_{file_id}")])
    if is_one_time:
        buttons.append([InlineKeyboardButton("⚠️ One-Time Link", callback_data="noop")])
    return InlineKeyboardMarkup(buttons)
