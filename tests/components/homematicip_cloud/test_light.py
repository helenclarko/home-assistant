"""Tests for HomematicIP Cloud light."""
from homematicip.base.enums import RGBColorState

from homeassistant.components.homematicip_cloud.light import (
    ATTR_ENERGY_COUNTER,
    ATTR_POWER_CONSUMPTION,
)
from homeassistant.components.light import ATTR_BRIGHTNESS, ATTR_COLOR_NAME
from homeassistant.const import STATE_OFF, STATE_ON

from .helper import async_manipulate_test_data, get_and_check_entity_basics


async def test_hmip_light(hass, default_mock_hap):
    """Test HomematicipLight."""
    entity_id = "light.treppe"
    entity_name = "Treppe"
    device_model = "HmIP-BSL"

    ha_state, hmip_device = get_and_check_entity_basics(
        hass, default_mock_hap, entity_id, entity_name, device_model
    )

    assert ha_state.state == STATE_ON

    service_call_counter = len(hmip_device.mock_calls)
    await hass.services.async_call(
        "light", "turn_off", {"entity_id": entity_id}, blocking=True
    )
    assert len(hmip_device.mock_calls) == service_call_counter + 1
    assert hmip_device.mock_calls[-1][0] == "turn_off"
    assert hmip_device.mock_calls[-1][1] == ()

    await async_manipulate_test_data(hass, hmip_device, "on", False)
    ha_state = hass.states.get(entity_id)
    assert ha_state.state == STATE_OFF

    await hass.services.async_call(
        "light", "turn_on", {"entity_id": entity_id}, blocking=True
    )
    assert len(hmip_device.mock_calls) == service_call_counter + 3
    assert hmip_device.mock_calls[-1][0] == "turn_on"
    assert hmip_device.mock_calls[-1][1] == ()

    await async_manipulate_test_data(hass, hmip_device, "on", True)
    ha_state = hass.states.get(entity_id)
    assert ha_state.state == STATE_ON


async def test_hmip_notification_light(hass, default_mock_hap):
    """Test HomematicipNotificationLight."""
    entity_id = "light.treppe_top_notification"
    entity_name = "Treppe Top Notification"
    device_model = "HmIP-BSL"

    ha_state, hmip_device = get_and_check_entity_basics(
        hass, default_mock_hap, entity_id, entity_name, device_model
    )

    assert ha_state.state == STATE_OFF
    service_call_counter = len(hmip_device.mock_calls)

    # Send all color via service call.
    await hass.services.async_call(
        "light", "turn_on", {"entity_id": entity_id}, blocking=True
    )
    assert hmip_device.mock_calls[-1][0] == "set_rgb_dim_level"
    assert hmip_device.mock_calls[-1][1] == (2, RGBColorState.RED, 1.0)

    color_list = {
        RGBColorState.WHITE: [0.0, 0.0],
        RGBColorState.RED: [0.0, 100.0],
        RGBColorState.YELLOW: [60.0, 100.0],
        RGBColorState.GREEN: [120.0, 100.0],
        RGBColorState.TURQUOISE: [180.0, 100.0],
        RGBColorState.BLUE: [240.0, 100.0],
        RGBColorState.PURPLE: [300.0, 100.0],
    }

    for color, hs_color in color_list.items():
        await hass.services.async_call(
            "light",
            "turn_on",
            {"entity_id": entity_id, "hs_color": hs_color},
            blocking=True,
        )
        assert hmip_device.mock_calls[-1][0] == "set_rgb_dim_level"
        assert hmip_device.mock_calls[-1][1] == (2, color, 0.0392156862745098)

    assert len(hmip_device.mock_calls) == service_call_counter + 8

    assert hmip_device.mock_calls[-1][0] == "set_rgb_dim_level"
    assert hmip_device.mock_calls[-1][1] == (
        2,
        RGBColorState.PURPLE,
        0.0392156862745098,
    )
    await async_manipulate_test_data(hass, hmip_device, "dimLevel", 1, 2)
    await async_manipulate_test_data(
        hass, hmip_device, "simpleRGBColorState", RGBColorState.PURPLE, 2
    )
    ha_state = hass.states.get(entity_id)
    assert ha_state.state == STATE_ON
    assert ha_state.attributes[ATTR_COLOR_NAME] == RGBColorState.PURPLE
    assert ha_state.attributes[ATTR_BRIGHTNESS] == 255

    await hass.services.async_call(
        "light", "turn_off", {"entity_id": entity_id}, blocking=True
    )
    assert len(hmip_device.mock_calls) == service_call_counter + 11
    assert hmip_device.mock_calls[-1][0] == "set_rgb_dim_level"
    assert hmip_device.mock_calls[-1][1] == (2, RGBColorState.PURPLE, 0.0)
    await async_manipulate_test_data(hass, hmip_device, "dimLevel", 0, 2)
    ha_state = hass.states.get(entity_id)
    assert ha_state.state == STATE_OFF


async def test_hmip_dimmer(hass, default_mock_hap):
    """Test HomematicipDimmer."""
    entity_id = "light.schlafzimmerlicht"
    entity_name = "Schlafzimmerlicht"
    device_model = "HmIP-BDT"

    ha_state, hmip_device = get_and_check_entity_basics(
        hass, default_mock_hap, entity_id, entity_name, device_model
    )

    assert ha_state.state == STATE_OFF
    service_call_counter = len(hmip_device.mock_calls)

    await hass.services.async_call(
        "light", "turn_on", {"entity_id": entity_id}, blocking=True
    )
    assert hmip_device.mock_calls[-1][0] == "set_dim_level"
    assert hmip_device.mock_calls[-1][1] == (1,)

    await hass.services.async_call(
        "light",
        "turn_on",
        {"entity_id": entity_id, "brightness_pct": "100"},
        blocking=True,
    )
    assert len(hmip_device.mock_calls) == service_call_counter + 2
    assert hmip_device.mock_calls[-1][0] == "set_dim_level"
    assert hmip_device.mock_calls[-1][1] == (1.0,)
    await async_manipulate_test_data(hass, hmip_device, "dimLevel", 1)
    ha_state = hass.states.get(entity_id)
    assert ha_state.state == STATE_ON
    assert ha_state.attributes[ATTR_BRIGHTNESS] == 255

    await hass.services.async_call(
        "light", "turn_off", {"entity_id": entity_id}, blocking=True
    )
    assert len(hmip_device.mock_calls) == service_call_counter + 4
    assert hmip_device.mock_calls[-1][0] == "set_dim_level"
    assert hmip_device.mock_calls[-1][1] == (0,)
    await async_manipulate_test_data(hass, hmip_device, "dimLevel", 0)
    ha_state = hass.states.get(entity_id)
    assert ha_state.state == STATE_OFF


async def test_hmip_light_measuring(hass, default_mock_hap):
    """Test HomematicipLightMeasuring."""
    entity_id = "light.flur_oben"
    entity_name = "Flur oben"
    device_model = "HmIP-BSM"

    ha_state, hmip_device = get_and_check_entity_basics(
        hass, default_mock_hap, entity_id, entity_name, device_model
    )

    assert ha_state.state == STATE_OFF
    service_call_counter = len(hmip_device.mock_calls)

    await hass.services.async_call(
        "light", "turn_on", {"entity_id": entity_id}, blocking=True
    )
    assert len(hmip_device.mock_calls) == service_call_counter + 1
    assert hmip_device.mock_calls[-1][0] == "turn_on"
    assert hmip_device.mock_calls[-1][1] == ()
    await async_manipulate_test_data(hass, hmip_device, "on", True)
    await async_manipulate_test_data(hass, hmip_device, "currentPowerConsumption", 50)
    ha_state = hass.states.get(entity_id)
    assert ha_state.state == STATE_ON
    assert ha_state.attributes[ATTR_POWER_CONSUMPTION] == 50
    assert ha_state.attributes[ATTR_ENERGY_COUNTER] == 6.33

    await hass.services.async_call(
        "light", "turn_off", {"entity_id": entity_id}, blocking=True
    )
    assert len(hmip_device.mock_calls) == service_call_counter + 4
    assert hmip_device.mock_calls[-1][0] == "turn_off"
    assert hmip_device.mock_calls[-1][1] == ()
    await async_manipulate_test_data(hass, hmip_device, "on", False)
    ha_state = hass.states.get(entity_id)
    assert ha_state.state == STATE_OFF
