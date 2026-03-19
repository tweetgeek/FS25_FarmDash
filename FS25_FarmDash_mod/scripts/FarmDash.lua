-- FarmDash: Live game data exporter for Farming Simulator 25
--
-- Writes two JSON files to modSettings/:
--   farmdash_live.json   – updated every 60 s (money, vehicles, fields, weather)
--   farmdash_static.json – updated on game start and every 5 minutes (map info, fill types)
--
-- Uses addTimer() for non-blocking periodic execution.
-- Requires Helpers.lua to be loaded first (see modDesc.xml).

FarmDash = {}

-- ----------------------------------------------------------------
-- Configuration
-- ----------------------------------------------------------------

local LIVE_FILE    = "farmdash_live.json"
local STATIC_FILE  = "farmdash_static.json"
local LIVE_TICK_MS = 60 * 1000   -- milliseconds between live exports
local STATIC_EVERY = 5           -- export static every N live ticks (= 5 min)

-- ----------------------------------------------------------------
-- Entry point via FSBaseMission hook
-- ----------------------------------------------------------------

local function onStart()
    FarmDash:init()
end

FSBaseMission.onStartMission = Utils.appendedFunction(FSBaseMission.onStartMission, onStart)

function FarmDash:init()
    self.staticCounter = 0

    -- Build WeatherType name lookup after the mission is loaded
    -- (WeatherType global is guaranteed to exist at this point)
    self.weatherNames = {}
    local wt = WeatherType or {}
    local mapping = {
        SUN              = "SUN",
        RAIN             = "RAIN",
        CLOUDY           = "CLOUDY",
        SNOW             = "SNOW",
        TWISTER          = "TWISTER",
        THUNDER          = "THUNDER",
        PARTIALLY_CLOUDY = "PARTIALLY_CLOUDY",
        HAIL             = "HAIL",
    }
    for key, name in pairs(mapping) do
        if wt[key] ~= nil then
            self.weatherNames[wt[key]] = name
        end
    end

    -- Export static data immediately on game load
    self:exportStatic()

    -- Start the live tick loop
    self:tick()

    Logging.info("[FarmDash] Initialised. Writing to modSettings/" .. LIVE_FILE)
end

-- ----------------------------------------------------------------
-- Tick loop (non-blocking, rescheduled via addTimer)
-- ----------------------------------------------------------------

function FarmDash:tick()
    if g_currentMission == nil then
        -- Mission ended – stop the loop
        return
    end

    self:exportLive()

    self.staticCounter = self.staticCounter + 1
    if self.staticCounter >= STATIC_EVERY then
        self.staticCounter = 0
        self:exportStatic()
    end

    addTimer(LIVE_TICK_MS, "tick", self)
end

-- ----------------------------------------------------------------
-- Export: live data
-- ----------------------------------------------------------------

function FarmDash:exportLive()
    if g_currentMission == nil then return end

    local data = {
        updatedAt   = getDate("%Y-%m-%d %H:%M:%S"),
        environment = self:getEnvData(),
        farm        = self:getFarmData(),
        weather     = self:getWeatherData(),
        vehicles    = self:getVehiclesData(),
        fields      = self:getFieldsData(),
    }

    FarmDashHelpers.writeJson(LIVE_FILE, data)
end

-- ----------------------------------------------------------------
-- Export: static / slow-changing data
-- ----------------------------------------------------------------

function FarmDash:exportStatic()
    if g_currentMission == nil then return end

    local data = {
        updatedAt = getDate("%Y-%m-%d %H:%M:%S"),
        mapTitle  = self:getMapTitle(),
        farmName  = self:getFarmName(),
        fillTypes = self:getFillTypesData(),
    }

    FarmDashHelpers.writeJson(STATIC_FILE, data)
end

-- ----------------------------------------------------------------
-- Data collectors
-- ----------------------------------------------------------------

function FarmDash:getEnvData()
    local env = g_currentMission and g_currentMission.environment
    if env == nil then return nil end

    local dayTime = env.dayTime or 0
    local hours   = math.floor(dayTime / 3600000)
    local minutes = math.floor((dayTime % 3600000) / 60000)

    return {
        dayTime       = string.format("%02d:%02d", hours, minutes),
        currentDay    = env.currentDay    or 0,
        period        = env.currentPeriod or 1,
        dayInPeriod   = env.currentDayInPeriod or 1,
        daysPerPeriod = env.daysPerPeriod  or 3,
    }
end

function FarmDash:getFarmData()
    -- Farm ID 1 is the player farm in singleplayer
    local farm = g_farmManager and g_farmManager:getFarmById(1)
    if farm == nil then return nil end

    return {
        money = farm.money or 0,
        loan  = farm.loan  or 0,
    }
end

function FarmDash:getWeatherData()
    local env = g_currentMission and g_currentMission.environment
    if env == nil or env.weather == nil then return nil end

    local forecast = env.weather.forecast
    if forecast == nil then return nil end

    -- Current weather
    local cur     = forecast:getCurrentWeather()
    local current = nil
    if cur then
        current = {
            type        = self.weatherNames[cur.forecastType] or tostring(cur.forecastType or ""),
            temperature = cur.temperature and math.floor(cur.temperature + 0.5) or 0,
            windSpeed   = cur.windSpeed   or 0,
            windDir     = cur.windDirection or 0,
        }
    end

    -- Hourly forecast (next 12 hours, every other slot = 12 entries of ~2h)
    local hourly = {}
    for i = 0, 11 do
        local h = forecast:getHourlyForecast(i)
        if h then
            local timeMs = h.time or 0
            local timeH  = math.floor(timeMs / 3600000) % 24
            table.insert(hourly, {
                label       = string.format("%02d:00", timeH),
                type        = self.weatherNames[h.forecastType] or tostring(h.forecastType or ""),
                temperature = h.temperature and math.floor(h.temperature + 0.5) or 0,
                windSpeed   = h.windSpeed or 0,
            })
        end
    end

    -- Daily forecast (next 7 days)
    local daily = {}
    for i = 1, 7 do
        local d = forecast:getDailyForecast(i)
        if d then
            local period, dayInPer = 0, 0
            if env.getPeriodFromDay then
                period    = env:getPeriodFromDay(d.day)    or 0
                dayInPer  = env:getDayInPeriodFromDay(d.day) or 0
            end
            table.insert(daily, {
                day         = d.day or 0,
                period      = period,
                dayInPeriod = dayInPer,
                type        = self.weatherNames[d.forecastType] or tostring(d.forecastType or ""),
                tempHigh    = d.highTemperature and math.floor(d.highTemperature + 0.5) or 0,
                tempLow     = d.lowTemperature  and math.floor(d.lowTemperature  + 0.5) or 0,
                windSpeed   = d.windSpeed or 0,
            })
        end
    end

    return {
        current = current,
        hourly  = hourly,
        daily   = daily,
    }
end

function FarmDash:getVehiclesData()
    local vs = g_currentMission and g_currentMission.vehicleSystem
    if vs == nil then return {} end

    local result = {}

    for _, vehicle in pairs(vs.vehicles) do
        if not vehicle.isDeleted then
            local name = vehicle:getName()
            if name == nil or name == "" then goto continue end

            local entry = {
                name           = name,
                typeName       = vehicle.typeName or "unknown",
                operatingHours = 0,
                damage         = 0,
                dirt           = 0,
                fuelPct        = nil,
                x              = nil,
                z              = nil,
                rotation       = nil,
            }

            -- Operating time (ms → hours, 1 decimal)
            if vehicle.operatingTime then
                entry.operatingHours = math.floor(vehicle.operatingTime / 360000) / 10
            end

            -- Wear (average across all wearable nodes) and dirt
            if vehicle.spec_wearable then
                local sw = vehicle.spec_wearable
                -- Dirt
                entry.dirt = math.floor((sw.dirtyFactor or 0) * 1000) / 10
                -- Damage: average wear from all wearable nodes
                if sw.wearableNodes then
                    local wearSum, wearCount = 0, 0
                    for _, node in ipairs(sw.wearableNodes) do
                        wearSum   = wearSum   + (node.wearAmount or 0)
                        wearCount = wearCount + 1
                    end
                    if wearCount > 0 then
                        entry.damage = math.floor(wearSum / wearCount * 1000) / 10
                    end
                end
            end

            -- Fuel percentage (via motorized spec + fill unit)
            if vehicle.spec_motorized and vehicle.spec_fillUnit then
                local fuelIdx = vehicle.spec_motorized.fuelFillUnitIndex
                if fuelIdx then
                    local fu = vehicle.spec_fillUnit.fillUnits
                              and vehicle.spec_fillUnit.fillUnits[fuelIdx]
                    if fu and fu.capacity and fu.capacity > 0 then
                        entry.fuelPct = math.floor(fu.fillLevel / fu.capacity * 1000) / 10
                    end
                end
            end

            -- World position and heading
            if vehicle.rootNode and vehicle.rootNode ~= 0 then
                local x, _, z = getWorldTranslation(vehicle.rootNode)
                if x ~= nil then
                    local dx, _, dz = localDirectionToWorld(vehicle.rootNode, 0, 0, 1)
                    entry.x        = math.floor(x * 10) / 10
                    entry.z        = math.floor(z * 10) / 10
                    entry.rotation = math.floor(
                        MathUtil.getYRotationFromDirection(dx, dz) * 1000
                    ) / 1000
                end
            end

            table.insert(result, entry)

            ::continue::
        end
    end

    return result
end

function FarmDash:getFieldsData()
    if g_fieldManager == nil then return {} end

    local result = {}

    for fieldId, field in pairs(g_fieldManager.fields) do
        if field.farmland == nil then goto skip end

        local cx, cz   = field:getCenterOfFieldWorldPosition()
        local fruitType  = "NONE"
        local fruitTitle = ""

        if cx ~= nil then
            local ftIdx = FSDensityMapUtil.getFruitTypeIndexAtWorldPos(cx, cz)
            if ftIdx and ftIdx > 0 then
                local ft = g_fruitTypeManager:getFruitTypeByIndex(ftIdx)
                if ft then
                    fruitType  = ft.name or "UNKNOWN"
                    fruitTitle = (ft.fillType and ft.fillType.title) or ft.name or ""
                end
            end
        end

        table.insert(result, {
            id         = fieldId,
            farmId     = field.farmland.farmId or 0,
            owned      = (field.farmland.farmId == 1),
            area       = field.farmland.areaInHa
                         and math.floor(field.farmland.areaInHa * 100) / 100
                         or 0,
            fruitType  = fruitType,
            fruitTitle = fruitTitle,
            x          = cx and math.floor(cx) or nil,
            z          = cz and math.floor(cz) or nil,
        })

        ::skip::
    end

    return result
end

function FarmDash:getMapTitle()
    if g_currentMission and g_currentMission.missionInfo and g_mapManager then
        local map = g_mapManager:getMapById(g_currentMission.missionInfo.mapId)
        if map then return map.title end
    end
    return "Unknown"
end

function FarmDash:getFarmName()
    local farm = g_farmManager and g_farmManager:getFarmById(1)
    return (farm and farm.name) or "Unknown"
end

function FarmDash:getFillTypesData()
    if g_fillTypeManager == nil then return {} end

    local result = {}
    local fillTypes = g_fillTypeManager:getFillTypes()

    for i = 1, #fillTypes do
        local ft = fillTypes[i]
        if ft and ft.name and ft.name ~= "UNKNOWN"
                and ft.title and ft.title ~= "" then
            table.insert(result, {
                name  = ft.name,
                title = ft.title,
            })
        end
    end

    return result
end
