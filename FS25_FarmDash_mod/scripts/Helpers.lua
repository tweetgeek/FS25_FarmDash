-- FarmDash: JSON utilities
-- Loaded before FarmDash.lua (see modDesc.xml order)

FarmDashHelpers = {}

-- ----------------------------------------------------------------
-- JSON encoder (depth-limited to avoid FS25 circular references)
-- ----------------------------------------------------------------

local MAX_DEPTH = 20

local function encodeVal(val, depth)
    depth = depth or 0
    if depth >= MAX_DEPTH then return "null" end

    local t = type(val)

    if val == nil then
        return "null"

    elseif t == "boolean" then
        return val and "true" or "false"

    elseif t == "number" then
        -- Guard against non-finite values
        if val ~= val or val == math.huge or val == -math.huge then
            return "null"
        end
        -- Output integers without decimal point
        if val == math.floor(val) and math.abs(val) < 1e15 then
            return string.format("%d", val)
        end
        return string.format("%.4f", val)

    elseif t == "string" then
        val = val:gsub('\\', '\\\\')
        val = val:gsub('"',  '\\"')
        val = val:gsub('\n', '\\n')
        val = val:gsub('\r', '\\r')
        val = val:gsub('\t', '\\t')
        return '"' .. val .. '"'

    elseif t == "table" then
        -- Detect array: all keys are consecutive integers 1..n
        local maxIdx, count = 0, 0
        local isArray = true
        for k, _ in pairs(val) do
            count = count + 1
            if type(k) ~= "number" or math.floor(k) ~= k or k < 1 then
                isArray = false
                break
            end
            if k > maxIdx then maxIdx = k end
        end
        -- Also reject sparse arrays (holes)
        if isArray and maxIdx ~= count then
            isArray = false
        end

        local parts = {}
        if isArray then
            for i = 1, count do
                parts[i] = encodeVal(val[i], depth + 1)
            end
            return "[" .. table.concat(parts, ",") .. "]"
        else
            for k, v in pairs(val) do
                local ks = tostring(k)
                ks = ks:gsub('\\', '\\\\'):gsub('"', '\\"')
                table.insert(parts, '"' .. ks .. '":' .. encodeVal(v, depth + 1))
            end
            return "{" .. table.concat(parts, ",") .. "}"
        end

    else
        return "null"
    end
end

function FarmDashHelpers.encode(val)
    return encodeVal(val)
end

-- Write JSON data to modSettings/<filename>
function FarmDashHelpers.writeJson(filename, data)
    local path = getUserProfileAppPath() .. "modSettings/" .. filename
    local json = encodeVal(data)
    local file = createFile(path, FileAccess.WRITE)
    if file and file ~= 0 then
        fileWrite(file, json)
        delete(file)
        return true
    end
    Logging.warning("[FarmDash] Cannot write file: " .. tostring(path))
    return false
end

-- Delete modSettings/<filename>; fallback: write {"active":false}
function FarmDashHelpers.deleteJson(filename)
    local path = getUserProfileAppPath() .. "modSettings/" .. filename
    local ok = pcall(fileDelete, path)
    if not ok then
        local f = createFile(path, FileAccess.WRITE)
        if f and f ~= 0 then
            fileWrite(f, '{"active":false}')
            delete(f)
        end
    end
end
