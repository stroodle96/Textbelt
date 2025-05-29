"""
Init file for the Textbelt integration.
"""

from homeassistant.config_entries import ConfigEntry  # type: ignore
from homeassistant.core import HomeAssistant  # type: ignore
import aiohttp
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Textbelt from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api_key": entry.data["api_key"],
        "webhook_url": entry.data["webhook_url"]
    }

    async def handle_send_sms(call):
        phone = call.data["number"]
        message = call.data["message"]
        api_key = entry.data["api_key"]
        webhook_url = entry.data["webhook_url"]
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://textbelt.com/text",
                data={
                    "phone": phone,
                    "message": message,
                    "key": api_key,
                    "webhook": webhook_url,
                },
            ) as resp:
                result = await resp.json()
                if result.get("success"):
                    text_id = result.get("textId")
                    quota = result.get("quotaRemaining")
                    _LOGGER.info(
                        "Textbelt SMS sent successfully: textId=%s, quotaRemaining=%s, response=%s",
                        text_id, quota, result
                    )
                else:
                    error = result.get("error", "Unknown error")
                    quota = result.get("quotaRemaining", "?")
                    _LOGGER.error(
                        "Textbelt SMS failed: error=%s, quotaRemaining=%s, response=%s",
                        error, quota, result
                    )
                    hass.components.persistent_notification.create(
                        f"Textbelt SMS failed: {error} (quota remaining: {quota})",
                        title="Textbelt Integration",
                    )

    hass.services.async_register(
        DOMAIN, "send_sms", handle_send_sms
    )
    # Register services, platforms, etc. here
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
