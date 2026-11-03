import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
)

from .const import (
    DOMAIN,
    CONF_LOGGER_SERIAL,
    CONF_SCAN_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
)

from .protocol import (
    SofarProtocolError,
    read_register_block,
)


class SofarConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):

    VERSION = 1

    async def async_step_user(
        self,
        user_input=None,
    ):

        errors = {}

        if user_input is not None:

            try:

                await read_register_block(
                    user_input[CONF_HOST],
                    user_input[CONF_PORT],
                    user_input[
                        CONF_LOGGER_SERIAL
                    ],
                    0x0400,
                    0x043A,
                )

            except SofarProtocolError:

                errors["base"] = (
                    "cannot_connect"
                )

            except Exception:

                errors["base"] = "unknown"

            else:

                uid = (
                    f"{user_input[CONF_HOST]}:"
                    f"{user_input[CONF_PORT]}:"
                    f"{user_input[CONF_LOGGER_SERIAL]}"
                )

                await self.async_set_unique_id(
                    uid
                )

                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Fotowoltaika",
                    data=user_input,
                )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_HOST,
                ): str,

                vol.Required(
                    CONF_PORT,
                    default=DEFAULT_PORT,
                ): int,

                vol.Required(
                    CONF_LOGGER_SERIAL,
                ): int,

                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=DEFAULT_SCAN_INTERVAL,
                ): vol.All(
                    int,
                    vol.Range(
                        min=2,
                        max=300,
                    ),
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
