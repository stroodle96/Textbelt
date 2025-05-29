"""
Config flow for the Textbelt integration (UI setup support).
"""

from homeassistant import config_entries  # type: ignore
from homeassistant.core import callback  # type: ignore
from .const import DOMAIN
from homeassistant.data_entry_flow import FlowResult  # type: ignore

class TextbeltConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Textbelt."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            api_key = user_input.get("api_key")
            webhook_url = user_input.get("webhook_url")
            if not api_key:
                errors["api_key"] = "required"
            if not webhook_url:
                errors["webhook_url"] = "required"
            if not errors:
                return self.async_create_entry(title="Textbelt", data={"api_key": api_key, "webhook_url": webhook_url})
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_schema(),
            errors=errors,
        )

    @staticmethod
    def _get_schema():
        import voluptuous as vol
        return vol.Schema({
            vol.Required("api_key"): str,
            vol.Required("webhook_url"): str
        })
